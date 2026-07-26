#!/usr/bin/env python3
"""Recompute four Paper 3 CTRW design summaries from release-level metrics."""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


EXPECTED_CELLS = {
    (0.10, 0.05),
    (0.10, 0.10),
    (0.20, 0.05),
    (0.20, 0.10),
}
ABS_TOL = 1.0e-12


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"Empty CTRW table: {path}")
    return rows


def number(value: object, label: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"Non-finite {label}: {value}")
    return result


def cell(row: dict[str, str]) -> tuple[float, float]:
    return (
        round(number(row["gas_velocity_m_s"], "gas velocity"), 8),
        round(number(row["df_over_dp"], "size ratio"), 8),
    )


def verify(
    case_path: Path, waiting_path: Path, design_path: Path
) -> dict[str, object]:
    case_rows = read(case_path)
    waiting_rows = read(waiting_path)
    design_rows = read(design_path)
    cases: dict[tuple[float, float], list[dict[str, str]]] = defaultdict(list)
    waiting: dict[tuple[float, float], dict[str, list[dict[str, str]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    designs = {cell(row): row for row in design_rows}
    for row in case_rows:
        cases[cell(row)].append(row)
    for row in waiting_rows:
        state = row["state"]
        if state not in {"low_mobility", "reverse"}:
            raise ValueError(f"Unexpected waiting-time state: {state}")
        waiting[cell(row)][state].append(row)
    if (
        len(case_rows) != 12
        or len(waiting_rows) != 24
        or len(design_rows) != 4
        or set(cases) != EXPECTED_CELLS
        or set(waiting) != EXPECTED_CELLS
        or set(designs) != EXPECTED_CELLS
    ):
        raise ValueError("The 12-case/four-cell CTRW design is incomplete")

    reports = []
    for design_cell in sorted(EXPECTED_CELLS):
        release_rows = cases[design_cell]
        low = waiting[design_cell]["low_mobility"]
        reverse = waiting[design_cell]["reverse"]
        if len(release_rows) != 3 or len(low) != 3 or len(reverse) != 3:
            raise ValueError(f"Design cell {design_cell} does not contain three releases")
        available_low_alphas = [
            float(row["alpha_median"])
            for row in low
            if math.isfinite(float(row["alpha_median"]))
        ]
        if not available_low_alphas:
            raise ValueError(
                f"Design cell {design_cell} has no available low-mobility alpha"
            )
        expected = {
            "release_count": 3,
            "p50_distance_exponent_mean": sum(
                number(row["p50_distance_exponent"], "P50 distance exponent")
                for row in release_rows
            )
            / 3.0,
            "p50_distance_exponent_min": min(
                number(row["p50_distance_exponent"], "P50 distance exponent")
                for row in release_rows
            ),
            "p50_distance_exponent_max": max(
                number(row["p50_distance_exponent"], "P50 distance exponent")
                for row in release_rows
            ),
            "median_p90_over_p50_mean": sum(
                number(row["median_p90_over_p50"], "P90/P50")
                for row in release_rows
            )
            / 3.0,
            "median_p99_over_p50_mean": sum(
                number(row["median_p99_over_p50"], "P99/P50")
                for row in release_rows
            )
            / 3.0,
            "transition_model_winner_share_mean": sum(
                number(row["winning_transition_model_share"], "transition winner share")
                for row in release_rows
            )
            / 3.0,
            "minimum_delta_aic_exponential": min(
                number(row["minimum_delta_aic_exponential"], "minimum delta AIC")
                for row in release_rows
            ),
            "low_mobility_alpha_available_release_count": len(
                available_low_alphas
            ),
            "low_mobility_alpha_median_across_releases": statistics.median(
                available_low_alphas
            ),
            "low_mobility_power_law_winner_share_mean": sum(
                number(row["power_law_family_winner_share"], "power-law winner share")
                for row in low
            )
            / 3.0,
            "low_mobility_tail_span_sufficient_share_mean": sum(
                number(row["tail_span_sufficient_share"], "tail-span share")
                for row in low
            )
            / 3.0,
            "low_mobility_power_law_supported_share_mean": sum(
                number(row["power_law_tail_supported_share"], "supported tail share")
                for row in low
            )
            / 3.0,
            "reverse_lognormal_winner_share_mean": sum(
                row["winning_model"] == "lognormal" for row in reverse
            )
            / 3.0,
        }
        recorded = designs[design_cell]
        if int(recorded["release_count"]) != 3:
            raise ValueError(f"Design cell {design_cell} has an invalid release count")
        for field, expected_value in expected.items():
            if field in {
                "release_count",
                "low_mobility_alpha_available_release_count",
            }:
                if int(recorded[field]) != int(expected_value):
                    raise ValueError(
                        f"Design cell {design_cell} has an inconsistent {field}"
                    )
                continue
            actual = number(recorded[field], field)
            if not math.isclose(
                actual, float(expected_value), rel_tol=0.0, abs_tol=ABS_TOL
            ):
                raise ValueError(
                    f"Design cell {design_cell} has an inconsistent {field}"
                )
        reports.append(
            {
                "gas_velocity_m_s": design_cell[0],
                "df_over_dp": design_cell[1],
                **expected,
            }
        )
    return {
        "status": "complete",
        "case_count": 12,
        "design_cell_count": 4,
        "waiting_state_row_count": 24,
        "cells": reports,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-metrics", type=Path, required=True)
    parser.add_argument("--waiting-metrics", type=Path, required=True)
    parser.add_argument("--design-metrics", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = verify(args.case_metrics, args.waiting_metrics, args.design_metrics)
    text = json.dumps(report, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
