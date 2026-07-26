#!/usr/bin/env python3
"""Recompute Paper 3 mechanism means from the 100 particle-paired differences."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


COMPARISONS = {
    "local_cfd_initial_velocity_minus_zero",
    "zero_gravity_minus_normal_gravity",
}
METRICS = {
    "final_dx_dp",
    "final_dz_dp",
    "reached_5dp",
    "ever_contacted",
    "sampled_contact_fraction",
    "maximum_contact_force_N",
    "bottom_wall_contact_sample_fraction",
    "time_averaged_total_fluid_force_x_N",
    "time_averaged_mechanical_contact_force_x_N",
    "time_averaged_total_fluid_force_z_N",
    "time_averaged_gravity_force_z_N",
    "time_averaged_mechanical_contact_force_z_N",
}
CHANGE_FIELDS = {
    "mean_dx_dp_difference": "final_dx_dp",
    "mean_dz_dp_difference": "final_dz_dp",
    "fpt_5dp_reached_fraction_difference": "reached_5dp",
    "ever_contacted_fraction_difference": "ever_contacted",
    "mean_sampled_contact_fraction_difference": "sampled_contact_fraction",
    "mean_bottom_wall_contact_sample_fraction_difference": (
        "bottom_wall_contact_sample_fraction"
    ),
    "mean_time_averaged_mechanical_contact_force_z_N_difference": (
        "time_averaged_mechanical_contact_force_z_N"
    ),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"Empty mechanism table: {path}")
    return rows


def number(value: object, label: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"Non-finite {label}: {value}")
    return result


def same(actual: float, expected: float, label: str) -> None:
    if not math.isclose(actual, expected, rel_tol=1.0e-10, abs_tol=1.0e-15):
        raise ValueError(f"{label}: recorded={actual}, recomputed={expected}")


def verify(
    particles_path: Path, bootstrap_path: Path, changes_path: Path
) -> dict[str, object]:
    particle_rows = read(particles_path)
    bootstrap_rows = read(bootstrap_path)
    changes = read(changes_path)
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in particle_rows:
        grouped[(row["comparison"], row["metric"])].append(row)
    expected = {
        (comparison, metric)
        for comparison in COMPARISONS
        for metric in METRICS
    }
    if len(particle_rows) != 2400 or set(grouped) != expected:
        raise ValueError("The particle-paired mechanism table is incomplete")

    means = {}
    for key, rows in grouped.items():
        particle_ids = {int(row["particle_id"]) for row in rows}
        if len(rows) != 100 or len(particle_ids) != 100:
            raise ValueError(f"{key} does not contain 100 unique particles")
        differences = []
        for row in rows:
            reference = number(row["reference_value"], "reference value")
            modified = number(row["modified_value"], "modified value")
            difference = number(row["paired_difference"], "paired difference")
            same(difference, modified - reference, f"{key} particle difference")
            differences.append(difference)
        means[key] = sum(differences) / 100.0

    bootstrap = {(row["comparison"], row["metric"]): row for row in bootstrap_rows}
    if len(bootstrap_rows) != 24 or set(bootstrap) != expected:
        raise ValueError("The paired bootstrap table is incomplete")
    reports = []
    for key in sorted(expected):
        row = bootstrap[key]
        mean = number(row["paired_mean_difference"], "paired bootstrap mean")
        same(mean, means[key], f"{key} paired mean")
        low = number(row["bootstrap_ci95_low"], "bootstrap CI low")
        high = number(row["bootstrap_ci95_high"], "bootstrap CI high")
        if (
            int(row["particle_count"]) != 100
            or int(row["bootstrap_sample_count"]) != 10000
            or not low <= mean <= high
        ):
            raise ValueError(f"{key} has an invalid bootstrap interval")
        reports.append(
            {
                "comparison": key[0],
                "metric": key[1],
                "particle_count": 100,
                "paired_mean_difference": mean,
                "bootstrap_ci95_low": low,
                "bootstrap_ci95_high": high,
            }
        )

    change_lookup = {row["comparison"]: row for row in changes}
    if len(changes) != 2 or set(change_lookup) != COMPARISONS:
        raise ValueError("The two aggregate mechanism comparisons are incomplete")
    for comparison, row in change_lookup.items():
        for field, metric in CHANGE_FIELDS.items():
            same(
                number(row[field], field),
                means[(comparison, metric)],
                f"{comparison}/{field}",
            )
    return {
        "status": "complete",
        "comparison_count": 2,
        "metric_count_per_comparison": 12,
        "paired_particle_row_count": 2400,
        "bootstrap_sample_count": 10000,
        "metrics": reports,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paired-particles", type=Path, required=True)
    parser.add_argument("--paired-bootstrap", type=Path, required=True)
    parser.add_argument("--changes", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = verify(args.paired_particles, args.paired_bootstrap, args.changes)
    text = json.dumps(report, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
