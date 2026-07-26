#!/usr/bin/env python3
"""Verify that pooled and held-out Paper 3 first-passage results agree exactly."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


EXPECTED_CELLS = {
    (0.10, 0.05),
    (0.10, 0.10),
    (0.20, 0.05),
    (0.20, 0.10),
}
ABS_TOL = 1.0e-12


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        result = list(csv.DictReader(handle))
    if not result:
        raise ValueError(f"Empty first-passage table: {path}")
    return result


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


def close(actual: float, expected: float, label: str) -> None:
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=ABS_TOL):
        raise ValueError(f"{label}: recorded={actual}, recomputed={expected}")


def verify(summary_path: Path, folds_path: Path) -> dict[str, object]:
    summary_rows = rows(summary_path)
    fold_rows = rows(folds_path)
    summaries = {cell(row): row for row in summary_rows}
    if len(summary_rows) != 4 or set(summaries) != EXPECTED_CELLS:
        raise ValueError("The pooled first-passage summary must contain four design cells")

    by_cell: dict[tuple[float, float], list[dict[str, str]]] = defaultdict(list)
    for row in fold_rows:
        by_cell[cell(row)].append(row)
    if set(by_cell) != EXPECTED_CELLS:
        raise ValueError("The held-out table does not cover all four design cells")

    reports = []
    for design_cell in sorted(EXPECTED_CELLS):
        folds = by_cell[design_cell]
        if len(folds) != 3:
            raise ValueError(f"Design cell {design_cell} has {len(folds)} held-out folds")
        held_out = {
            (row.get("held_out_case", ""), row.get("held_out_release_seed", ""))
            for row in folds
        }
        if len(held_out) != 3 or any(not case or not seed for case, seed in held_out):
            raise ValueError(f"Design cell {design_cell} has duplicate or missing held-out releases")

        classical = []
        fractional = []
        for row in folds:
            classical_value = number(row["classical_cdf_rmse"], "classical RMSE")
            fractional_value = number(row["fractional_cdf_rmse"], "fractional RMSE")
            if classical_value < 0.0 or fractional_value < 0.0:
                raise ValueError(f"Design cell {design_cell} contains a negative RMSE")
            improvement = number(
                row["fractional_rmse_improvement"], "fold RMSE improvement"
            )
            close(
                improvement,
                classical_value - fractional_value,
                f"Design cell {design_cell} fold improvement",
            )
            classical.append(classical_value)
            fractional.append(fractional_value)

        classical_mean = sum(classical) / 3.0
        fractional_mean = sum(fractional) / 3.0
        improvement_mean = sum(
            old - new for old, new in zip(classical, fractional)
        ) / 3.0
        win_count = sum(new < old for old, new in zip(classical, fractional))
        summary = summaries[design_cell]
        if int(summary["cross_validation_fold_count"]) != 3:
            raise ValueError(f"Design cell {design_cell} summary does not report three folds")
        if int(summary["cross_validation_fractional_win_count"]) != win_count:
            raise ValueError(f"Design cell {design_cell} has an inconsistent win count")
        close(
            number(
                summary["cross_validation_classical_rmse_mean"],
                "summary classical RMSE",
            ),
            classical_mean,
            f"Design cell {design_cell} classical mean",
        )
        close(
            number(
                summary["cross_validation_fractional_rmse_mean"],
                "summary fractional RMSE",
            ),
            fractional_mean,
            f"Design cell {design_cell} fractional mean",
        )
        close(
            number(
                summary["cross_validation_fractional_rmse_improvement"],
                "summary RMSE improvement",
            ),
            improvement_mean,
            f"Design cell {design_cell} improvement mean",
        )
        reports.append(
            {
                "gas_velocity_m_s": design_cell[0],
                "df_over_dp": design_cell[1],
                "fold_count": 3,
                "fractional_win_count": win_count,
                "classical_rmse_mean": classical_mean,
                "fractional_rmse_mean": fractional_mean,
                "fractional_rmse_improvement_mean": improvement_mean,
            }
        )
    return {
        "status": "complete",
        "design_cell_count": 4,
        "held_out_fold_count": 12,
        "cells": reports,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--leave-one-out", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = verify(args.summary, args.leave_one_out)
    text = json.dumps(report, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
