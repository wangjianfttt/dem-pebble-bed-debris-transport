#!/usr/bin/env python3
"""Recompute Paper 3 held-out mobile--immobile model rankings from predictions."""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path


MODELS = {
    "classical_ade",
    "homogeneous_exponential_mobile_immobile",
    "heterogeneous_advection_dispersion",
    "heterogeneous_exponential_mobile_immobile",
    "heterogeneous_fitted_residence_mobile_immobile",
    "heterogeneous_correlated_fitted_residence_ctrw",
}
DESIGN_CELLS = {
    (0.10, 0.05),
    (0.10, 0.10),
    (0.20, 0.05),
    (0.20, 0.10),
}
RELEASE_SEEDS = {20260713, 20260714, 20260715}


def finite(value: object, label: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"Non-finite {label}: {value}")
    return result


def verify(predictions_path: Path, summary_path: Path) -> dict[str, object]:
    with predictions_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if len(rows) != 72:
        raise ValueError(f"Expected 72 held-out model rows, found {len(rows)}")
    if (
        summary.get("status") != "complete"
        or int(summary.get("held_out_prediction_count", -1)) != 12
    ):
        raise ValueError("The held-out mobile--immobile summary is incomplete")

    predictions: dict[tuple[float, float, int], list[dict[str, str]]] = defaultdict(list)
    model_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (
            round(finite(row["gas_velocity_m_s"], "gas velocity"), 8),
            round(finite(row["df_over_dp"], "size ratio"), 8),
            int(row["prediction_release_seed"]),
        )
        model = row["model"]
        if model not in MODELS:
            raise ValueError(f"Unexpected mobile--immobile model: {model}")
        for field in ("cdf_rmse", "cdf_mae"):
            if finite(row[field], field) < 0.0:
                raise ValueError(f"Negative {field} for {key}, {model}")
        for field in ("observed_passage_fraction", "predicted_passage_fraction"):
            value = finite(row[field], field)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field} outside [0,1] for {key}, {model}")
        predictions[key].append(row)
        model_rows[model].append(row)

    if len(predictions) != 12:
        raise ValueError(f"Expected 12 held-out releases, found {len(predictions)}")
    for key, values in predictions.items():
        models = [row["model"] for row in values]
        if len(values) != 6 or set(models) != MODELS or len(set(models)) != 6:
            raise ValueError(f"Held-out release {key} does not contain six unique models")

    wins = {model: 0 for model in MODELS}
    for values in predictions.values():
        winner = min(values, key=lambda row: finite(row["cdf_rmse"], "CDF RMSE"))
        wins[winner["model"]] += 1

    recomputed = []
    for model in MODELS:
        values = model_rows[model]
        if len(values) != 12:
            raise ValueError(f"Model {model} has {len(values)} predictions")
        errors = [finite(row["cdf_rmse"], "CDF RMSE") for row in values]
        recomputed.append(
            {
                "model": model,
                "prediction_count": 12,
                "mean_cdf_rmse": sum(errors) / 12.0,
                "median_cdf_rmse": statistics.median(errors),
                "minimum_cdf_rmse": min(errors),
                "maximum_cdf_rmse": max(errors),
                "win_count": wins[model],
            }
        )
    recomputed.sort(key=lambda item: float(item["mean_cdf_rmse"]))

    recorded = summary.get("models")
    if not isinstance(recorded, list) or len(recorded) != 6:
        raise ValueError("The summary does not contain six model records")
    if [item.get("model") for item in recorded] != [
        item["model"] for item in recomputed
    ]:
        raise ValueError("The recorded model ranking does not match the prediction table")
    for expected, actual in zip(recomputed, recorded):
        if int(actual.get("prediction_count", -1)) != 12:
            raise ValueError(f"Model {expected['model']} has an invalid prediction count")
        if int(actual.get("win_count", -1)) != expected["win_count"]:
            raise ValueError(f"Model {expected['model']} has an inconsistent win count")
        for field in (
            "mean_cdf_rmse",
            "median_cdf_rmse",
            "minimum_cdf_rmse",
            "maximum_cdf_rmse",
        ):
            recorded_value = finite(actual.get(field), f"recorded {field}")
            if not math.isclose(
                recorded_value,
                float(expected[field]),
                rel_tol=0.0,
                abs_tol=1.0e-12,
            ):
                raise ValueError(f"Model {expected['model']} has an inconsistent {field}")

    return {
        "status": "complete",
        "held_out_prediction_count": 12,
        "model_count": 6,
        "ranking_metric": "mean_cdf_rmse",
        "models": recomputed,
    }


def verify_pairwise(
    predictions_path: Path, summary_path: Path
) -> dict[str, object]:
    """Recompute all 24 ordered single-release predictions from their table."""
    with predictions_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if len(rows) != 144:
        raise ValueError(f"Expected 144 pairwise model rows, found {len(rows)}")
    if (
        summary.get("status") != "complete"
        or int(summary.get("model_version", -1)) != 3
        or int(summary.get("eligible_group_count", -1)) != 4
        or int(summary.get("eligible_case_count", -1)) != 12
        or int(summary.get("pair_count", -1)) != 24
    ):
        raise ValueError("The pairwise mobile--immobile summary is incomplete")

    predictions: dict[
        tuple[float, float, int, int], list[dict[str, str]]
    ] = defaultdict(list)
    model_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        cell = (
            round(finite(row["gas_velocity_m_s"], "gas velocity"), 8),
            round(finite(row["df_over_dp"], "size ratio"), 8),
        )
        training_seed = int(row["training_release_seed"])
        prediction_seed = int(row["prediction_release_seed"])
        key = (*cell, training_seed, prediction_seed)
        if (
            cell not in DESIGN_CELLS
            or training_seed not in RELEASE_SEEDS
            or prediction_seed not in RELEASE_SEEDS
            or training_seed == prediction_seed
        ):
            raise ValueError(f"Invalid pairwise prediction coordinates: {key}")
        model = row["model"]
        if model not in MODELS:
            raise ValueError(f"Unexpected mobile--immobile model: {model}")
        for field in ("cdf_rmse", "cdf_mae"):
            if finite(row[field], field) < 0.0:
                raise ValueError(f"Negative {field} for {key}, {model}")
        for field in ("observed_passage_fraction", "predicted_passage_fraction"):
            value = finite(row[field], field)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{field} outside [0,1] for {key}, {model}")
        predictions[key].append(row)
        model_rows[model].append(row)

    if len(predictions) != 24:
        raise ValueError(f"Expected 24 ordered release pairs, found {len(predictions)}")
    for key, values in predictions.items():
        models = [row["model"] for row in values]
        if len(values) != 6 or set(models) != MODELS or len(set(models)) != 6:
            raise ValueError(f"Release pair {key} does not contain six unique models")

    wins = {model: 0 for model in MODELS}
    for values in predictions.values():
        winner = min(values, key=lambda row: finite(row["cdf_rmse"], "CDF RMSE"))
        wins[winner["model"]] += 1

    recomputed = []
    for model in MODELS:
        values = model_rows[model]
        if len(values) != 24:
            raise ValueError(f"Model {model} has {len(values)} pairwise predictions")
        errors = [finite(row["cdf_rmse"], "CDF RMSE") for row in values]
        recomputed.append(
            {
                "model": model,
                "prediction_count": 24,
                "mean_cdf_rmse": sum(errors) / 24.0,
                "median_cdf_rmse": statistics.median(errors),
                "minimum_cdf_rmse": min(errors),
                "maximum_cdf_rmse": max(errors),
                "win_count": wins[model],
            }
        )
    recomputed.sort(key=lambda item: float(item["mean_cdf_rmse"]))

    recorded = summary.get("models")
    if not isinstance(recorded, list) or len(recorded) != 6:
        raise ValueError("The pairwise summary does not contain six model records")
    if [item.get("model") for item in recorded] != [
        item["model"] for item in recomputed
    ]:
        raise ValueError(
            "The recorded pairwise model ranking does not match the prediction table"
        )
    for expected, actual in zip(recomputed, recorded):
        if int(actual.get("prediction_count", -1)) != 24:
            raise ValueError(
                f"Model {expected['model']} has an invalid pairwise prediction count"
            )
        if int(actual.get("win_count", -1)) != expected["win_count"]:
            raise ValueError(
                f"Model {expected['model']} has an inconsistent pairwise win count"
            )
        for field in (
            "mean_cdf_rmse",
            "median_cdf_rmse",
            "minimum_cdf_rmse",
            "maximum_cdf_rmse",
        ):
            if not math.isclose(
                finite(actual.get(field), f"recorded pairwise {field}"),
                float(expected[field]),
                rel_tol=0.0,
                abs_tol=1.0e-12,
            ):
                raise ValueError(
                    f"Model {expected['model']} has an inconsistent pairwise {field}"
                )

    return {
        "status": "complete",
        "ordered_pair_count": 24,
        "model_count": 6,
        "ranking_metric": "mean_cdf_rmse",
        "models": recomputed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--pairwise-predictions", type=Path)
    parser.add_argument("--pairwise-summary", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = verify(args.predictions, args.summary)
    if (args.pairwise_predictions is None) != (args.pairwise_summary is None):
        parser.error(
            "--pairwise-predictions and --pairwise-summary must be supplied together"
        )
    if args.pairwise_predictions is not None:
        report["pairwise_validation"] = verify_pairwise(
            args.pairwise_predictions, args.pairwise_summary
        )
    text = json.dumps(report, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
