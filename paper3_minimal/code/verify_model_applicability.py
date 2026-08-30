#!/usr/bin/env python3
"""Verify the processed pore-flow and occupied-position diagnostics."""

from __future__ import annotations

import csv
import json
import math
import statistics
from pathlib import Path


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"empty CSV: {path}")
    return rows


def close(actual: float, expected: float, tolerance: float = 2.0e-7) -> None:
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=tolerance):
        raise ValueError(f"expected {expected}, obtained {actual}")


def relative_l2(rows, candidate: str, reference: str) -> float:
    numerator = 0.0
    denominator = 0.0
    for row in rows:
        a = float(row[candidate])
        b = float(row[reference])
        numerator += (a - b) ** 2
        denominator += b**2
    return math.sqrt(numerator / denominator)


def vector(row, prefix: str) -> tuple[float, float, float]:
    return tuple(float(row[f"{prefix}_{axis}"]) for axis in ("x", "y", "z"))


def norm(values) -> float:
    return math.sqrt(sum(value * value for value in values))


def verify_carrier_zone(path: Path, cpd: int, expected_ux: float, expected_qx: float):
    rows = read_csv(path / f"carrier_field_bins_c{cpd}.csv")
    summary = json.loads(
        (path / f"carrier_field_comparison_c{cpd}.json").read_text(encoding="utf-8")
    )
    ux = relative_l2(rows, "resolved_ux_m_per_s", "unresolved_ux_m_per_s")
    qx = relative_l2(rows, "resolved_qx_m_per_s", "unresolved_qx_m_per_s")
    close(ux, expected_ux)
    close(qx, expected_qx)
    close(ux, summary["metrics_resolved_minus_unresolved"]["fluid_phase_ux_m_per_s"]["relative_l2"])
    close(qx, summary["metrics_resolved_minus_unresolved"]["superficial_qx_m_per_s"]["relative_l2"])
    return {
        "cells_per_pebble_diameter": cpd,
        "bin_count": len(rows),
        "porosity": summary["resolved_window_porosity"],
        "pressure_gradient_ratio": summary["cross_sectional_pressure"]["absolute_gradient_ratio_resolved_over_unresolved"],
        "ux_relative_l2": ux,
        "qx_relative_l2": qx,
        "resolved_speed_p99_m_per_s": summary["void_space_speed_distribution"]["speed_quantiles_m_per_s"]["p99"],
        "unresolved_speed_p99_m_per_s": summary["unresolved_cell_speed_distribution"]["speed_quantiles_m_per_s"]["p99"],
    }


def verify_occupied_positions(path: Path):
    rows = read_csv(path / "fine_particle_point_forcing_samples.csv")
    summary = json.loads(
        (path / "fine_particle_point_forcing_summary.json").read_text(encoding="utf-8")
    )
    ratios = []
    cosines = []
    for row in rows:
        logged = vector(row, "logged_drag")
        replacement = vector(row, "replacement_drag")
        logged_norm = norm(logged)
        replacement_norm = norm(replacement)
        if logged_norm <= 0.0 or replacement_norm <= 0.0:
            raise ValueError("zero drag vector in occupied-position package")
        ratios.append(replacement_norm / logged_norm)
        cosines.append(
            sum(a * b for a, b in zip(logged, replacement))
            / (logged_norm * replacement_norm)
        )
    median_ratio = statistics.median(ratios)
    opposite_fraction = sum(value < 0.0 for value in cosines) / len(cosines)
    expected = summary["groups"]["all"]["fixed_coefficient_drag"]
    close(median_ratio, 8.29562743433221, 1.0e-10)
    close(opposite_fraction, 0.41241890639481, 1.0e-12)
    close(median_ratio, expected["magnitude_ratio_p10_p50_p90"][1], 1.0e-10)
    close(opposite_fraction, expected["opposite_direction_fraction"], 1.0e-12)
    if len(rows) != 1079 or summary["field_sampling_validity"]["selected_rows"] != 1229:
        raise ValueError("occupied-position sample counts do not match")
    return {
        "selected_count": 1229,
        "valid_count": len(rows),
        "median_fixed_coefficient_force_ratio": median_ratio,
        "opposite_force_direction_fraction": opposite_fraction,
    }


def verify(root: Path) -> dict[str, object]:
    release = root / "release_zone"
    interior = root / "interior_zone"
    grid = read_csv(release / "grid_convergence.csv")
    if [int(row["cells_per_dp"]) for row in grid] != [10, 15, 20]:
        raise ValueError("release-zone grid sequence is incomplete")
    close(float(grid[-1]["resolved_window_porosity"]), 0.41446935529671225)
    close(float(grid[-1]["absolute_gradient_ratio_resolved_over_unresolved"]), 1.3870490491106866)

    release_c20 = verify_carrier_zone(
        release, 20, 0.34228627819085317, 0.3324289627826118
    )
    interior_c15 = verify_carrier_zone(
        interior, 15, 0.2424811089746282, 0.24325864258755642
    )
    interior_c20 = verify_carrier_zone(
        interior, 20, 0.247207376767142, 0.24949720424852892
    )
    close(interior_c20["porosity"], 0.3969794208291384)
    close(interior_c20["pressure_gradient_ratio"], 1.3426020961941925)

    return {
        "release_zone_grid_points": 3,
        "release_zone_c20": release_c20,
        "interior_zone_c15": interior_c15,
        "interior_zone_c20": interior_c20,
        "occupied_positions": verify_occupied_positions(root / "occupied_positions"),
        "interpretation": (
            "Geometry and pressure improve with refinement, while filtered local "
            "carrier-velocity differences persist. Occupied-position force changes "
            "are a carrier-field sensitivity diagnostic, not a corrected drag law."
        ),
    }


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    print(json.dumps(verify(here.parent / "data/model_applicability"), indent=2))
