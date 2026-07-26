#!/usr/bin/env python3
"""Combine the four completed 20 s benchmark cases with Xie et al. data."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np


EXPECTED_RATIOS = (0.10, 0.15, 0.20, 0.25)
EXPECTED_FINE_COUNT = 4104
EXPECTED_TIME_S = 20.0
EXPECTED_INPUT_DATA_SHA256 = {
    "r010": "4dfe738b7ca4960f8c06781a511b08a1deebb3c768e3812010124ae9b055f5f9",
    "r015": "0a9795be619402c197e4120dc1e2fe206dfc5c00460588f43ab42c733732cab3",
    "r020": "2c727ff2950543dd46db628154cd97a8c2278d4e0a7d2e6ed1da308f25f8d91a",
    "r025": "2d3fe469108514839f29101cf3f7d688ed2f5150cd0db7fa64d83504f0590b45",
}
EXPECTED_SHARED_METADATA = {
    "coarse_particle_count": 2000,
    "fine_particle_count": 4104,
    "domain_m": [0.012, 0.012, 0.03],
    "coarse_diameter_m": 1.0e-3,
    "particle_density_kg_m3": 2500.0,
    "youngs_modulus_Pa": 1.0e7,
    "poissons_ratio": 0.3,
    "restitution": 0.6,
    "sliding_friction": 0.2,
    "rolling_friction": 0.002,
    "fluid_density_kg_m3": 1000.0,
    "fluid_dynamic_viscosity_Pa_s": 1.0e-3,
    "inlet_velocity_m_s": [0.0, 0.0, -0.02],
    "mesh_divisions": [24, 24, 60],
    "mesh_size_m": 5.0e-4,
    "cfd_timestep_s": 1.0e-5,
    "dem_timestep_s": 1.0e-6,
    "simulation_time_s": 20.0,
    "drag_model": "DiFeliceDrag",
    "pressure_gradient_force": True,
    "viscous_stress_force": True,
    "added_mass_coefficient": 2.0,
    "added_mass_to_particle_mass_ratio": 0.8,
    "added_mass_translational_integrator": True,
    "independent_virtual_mass_force_enabled": False,
    "hydrodynamic_stress_terms_dem_side_only": True,
    "fluid_particle_momentum_exchange": "drag_only",
    "cfd_solver": "cfdemSolverPisoImEx",
    "void_fraction_model": "divided",
    "smoothing_model": "constDiffSmoothing",
    "smoothing_length_m": 1.5e-3,
    "literature_smoothing_support_m": 1.5e-3,
    "coarse_bed_frozen": True,
}
REQUIRED_HEALTH_CHECKS = {
    "metadata_complete_passed",
    "return_code_passed",
    "initial_dump_at_zero_passed",
    "initial_fine_count_passed",
    "particle_ids_monotonic_passed",
    "final_dump_time_passed",
    "solver_end_time_passed",
    "normal_solver_end_passed",
    "courant_number_passed",
    "added_mass_coefficient_passed",
    "added_mass_ratio_passed",
    "added_mass_integrator_passed",
    "independent_virtual_mass_disabled_passed",
    "stress_terms_dem_side_only_passed",
    "drag_only_momentum_exchange_passed",
}


def metadata_values_match(actual: object, expected: object) -> bool:
    """Compare scalar or list metadata with strict numerical tolerances."""
    if isinstance(expected, list):
        return (
            isinstance(actual, list)
            and len(actual) == len(expected)
            and all(
                metadata_values_match(actual_value, expected_value)
                for actual_value, expected_value in zip(actual, expected)
            )
        )
    if isinstance(expected, float):
        try:
            return math.isclose(
                float(actual), expected, rel_tol=0.0, abs_tol=1.0e-12
            )
        except (TypeError, ValueError):
            return False
    return actual == expected


def validate_case_metadata(
    metadata: dict[str, object], ratio: float, label: str
) -> None:
    """Require every case to use the frozen four-point benchmark settings."""
    mismatches = [
        name
        for name, expected in EXPECTED_SHARED_METADATA.items()
        if not metadata_values_match(metadata.get(name), expected)
    ]
    if mismatches:
        raise ValueError(
            f"Xie shared metadata mismatch for {label}: {', '.join(mismatches)}"
        )
    if not metadata_values_match(metadata.get("df_over_dp"), ratio):
        raise ValueError(f"Xie metadata size-ratio mismatch for {label}")
    expected_fine_diameter = ratio * float(
        EXPECTED_SHARED_METADATA["coarse_diameter_m"]
    )
    if not metadata_values_match(
        metadata.get("fine_diameter_m"), expected_fine_diameter
    ):
        raise ValueError(f"Xie fine-particle diameter mismatch for {label}")
    if metadata.get("status") != "complete" or metadata.get("return_code") != 0:
        raise ValueError(f"Xie solver metadata is incomplete for {label}")
    if metadata.get("input_data_sha256") != EXPECTED_INPUT_DATA_SHA256[label]:
        raise ValueError(f"Xie formal input data SHA mismatch for {label}")


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a CSV table."""
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    """Write a nonempty flat table."""
    if not rows:
        raise ValueError(f"No rows available for {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def collect(
    reference_path: Path,
    results_root: Path,
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    """Return paired final values, time histories and comparison statistics."""
    reference_rows = read_csv(reference_path)
    reference_metadata = json.loads(reference_path.with_suffix(".json").read_text())
    if (
        reference_metadata.get("source_doi") != "10.1016/j.ces.2020.116261"
        or reference_metadata.get("source_figure") != "Fig. 21"
        or reference_metadata.get("render_resolution_dpi") != 300
        or reference_metadata.get("method")
        != "cyan-bar pixel height normalized by the r/R=0.25 full-scale bar"
    ):
        raise ValueError("Xie reference digitization metadata is incomplete")
    reference_ratios = tuple(
        sorted(float(row["size_ratio_r_over_R"]) for row in reference_rows)
    )
    if reference_ratios != EXPECTED_RATIOS:
        raise ValueError(
            "Xie reference ratios must be exactly "
            f"{EXPECTED_RATIOS}; received {reference_ratios}"
        )
    metadata_rows = reference_metadata.get("rows")
    numeric_fields = (
        "size_ratio_r_over_R",
        "retained_fraction_digitized",
        "bar_x0_px",
        "bar_x1_px",
        "bar_top_y_px",
        "bar_bottom_y_px",
        "cyan_pixel_count",
    )
    if not isinstance(metadata_rows, list) or len(metadata_rows) != len(reference_rows):
        raise ValueError("Xie reference CSV and digitization metadata disagree")
    for csv_row, metadata_row in zip(
        sorted(reference_rows, key=lambda row: float(row["size_ratio_r_over_R"])),
        sorted(metadata_rows, key=lambda row: float(row["size_ratio_r_over_R"])),
    ):
        if any(
            not math.isclose(
                float(csv_row[field]),
                float(metadata_row[field]),
                rel_tol=0.0,
                abs_tol=1.0e-12,
            )
            for field in numeric_fields
        ):
            raise ValueError("Xie reference CSV and digitization metadata disagree")
    bottom_pixels = {int(row["bar_bottom_y_px"]) for row in reference_rows}
    if len(bottom_pixels) != 1:
        raise ValueError("Xie digitized bars do not share a common baseline")
    full_scale_pixels = (
        next(iter(bottom_pixels))
        - min(int(row["bar_top_y_px"]) for row in reference_rows)
        + 1
    )
    if full_scale_pixels <= 1:
        raise ValueError("Xie digitization full-scale pixel height is invalid")
    digitization_uncertainty = 1.0 / full_scale_pixels
    paired: list[dict[str, object]] = []
    histories: list[dict[str, object]] = []
    for reference in sorted(
        reference_rows, key=lambda row: float(row["size_ratio_r_over_R"])
    ):
        ratio = float(reference["size_ratio_r_over_R"])
        label = f"r{round(100 * ratio):03d}"
        result_dir = results_root / label
        metadata_path = result_dir / "metadata.json"
        metrics_path = result_dir / "xie2021_full_benchmark_metrics.json"
        history_path = result_dir / "retention_breakthrough_history.csv"
        if (
            not metadata_path.is_file()
            or not metrics_path.is_file()
            or not history_path.is_file()
        ):
            raise FileNotFoundError(f"Completed benchmark output is missing for {label}")
        metadata = json.loads(metadata_path.read_text())
        validate_case_metadata(metadata, ratio, label)
        metrics = json.loads(metrics_path.read_text())
        health = metrics.get("health_checks")
        if not isinstance(health, dict) or not REQUIRED_HEALTH_CHECKS.issubset(health):
            raise ValueError(f"Benchmark health checks are incomplete: {label}")
        if metrics.get("status") != "complete" or not all(
            bool(health[name]) for name in REQUIRED_HEALTH_CHECKS
        ):
            raise ValueError(f"Benchmark result has not passed completion checks: {label}")
        if abs(float(metrics["df_over_dp"]) - ratio) > 1.0e-12:
            raise ValueError(f"Size-ratio mismatch for {label}")
        initial_count = int(metrics["initial_fine_count"])
        retained_count = int(metrics["final_retained_count"])
        outlet_count = int(metrics["final_outlet_count"])
        simulated_fraction = float(metrics["final_retained_fraction"])
        final_time_s = float(metrics["final_dump_time_s"])
        if initial_count != EXPECTED_FINE_COUNT:
            raise ValueError(f"Initial fine count is not 4104 for {label}")
        if not 0 <= retained_count <= initial_count:
            raise ValueError(f"Final retained count is outside physical bounds for {label}")
        if outlet_count != initial_count - retained_count:
            raise ValueError(f"Final fine-particle balance is inconsistent for {label}")
        if not math.isclose(
            simulated_fraction,
            retained_count / initial_count,
            rel_tol=0.0,
            abs_tol=1.0e-12,
        ):
            raise ValueError(f"Final retained count and fraction disagree for {label}")
        if not math.isclose(
            final_time_s, EXPECTED_TIME_S, rel_tol=0.0, abs_tol=5.0e-7
        ):
            raise ValueError(f"Final Xie result is not at 20 s for {label}")
        tail_change = metrics.get("tail_change")
        if not isinstance(tail_change, dict):
            raise ValueError(f"Late-time Xie changes are missing for {label}")
        for key, expected_window, expected_start in (
            ("last_1s", 1.0, 19.0),
            ("last_2s", 2.0, 18.0),
        ):
            window = tail_change.get(key)
            if not isinstance(window, dict) or any(
                not math.isclose(
                    float(window[field]),
                    expected,
                    rel_tol=0.0,
                    abs_tol=5.0e-7,
                )
                for field, expected in (
                    ("window_s", expected_window),
                    ("start_time_s", expected_start),
                    ("end_time_s", 20.0),
                )
            ):
                raise ValueError(
                    f"Late-time Xie window is not exactly {expected_start:g}--20 s "
                    f"for {label}"
                )
        case_history = read_csv(history_path)
        if len(case_history) < 2:
            raise ValueError(f"Retention history is incomplete for {label}")
        history_times = [float(row["time_s"]) for row in case_history]
        retained_fractions = [
            float(row["retained_fraction"]) for row in case_history
        ]
        breakthrough_fractions = [
            float(row["cumulative_breakthrough_fraction"])
            for row in case_history
        ]
        if (
            not math.isclose(history_times[0], 0.0, abs_tol=5.0e-7)
            or not math.isclose(history_times[-1], EXPECTED_TIME_S, abs_tol=5.0e-7)
            or any(right <= left for left, right in zip(history_times, history_times[1:]))
        ):
            raise ValueError(f"Retention history does not span 0--20 s for {label}")
        if any(
            right > left + 1.0e-12
            for left, right in zip(retained_fractions, retained_fractions[1:])
        ) or any(
            right + 1.0e-12 < left
            for left, right in zip(
                breakthrough_fractions, breakthrough_fractions[1:]
            )
        ):
            raise ValueError(f"Retention history is not monotonic for {label}")
        if any(
            not math.isclose(retained + breakthrough, 1.0, abs_tol=1.0e-12)
            for retained, breakthrough in zip(
                retained_fractions, breakthrough_fractions
            )
        ):
            raise ValueError(
                f"Retention and breakthrough fractions do not sum to one for {label}"
            )
        if not math.isclose(
            retained_fractions[-1], simulated_fraction, abs_tol=1.0e-12
        ):
            raise ValueError(
                f"History endpoint and final retained fraction disagree for {label}"
            )
        reference_fraction = float(reference["retained_fraction_digitized"])
        absolute_difference = abs(simulated_fraction - reference_fraction)
        digitization_interval_excess = max(
            absolute_difference - digitization_uncertainty,
            0.0,
        )
        paired.append(
            {
                "df_over_dp": ratio,
                "xie2021_retained_fraction": reference_fraction,
                "xie2021_digitization_uncertainty": digitization_uncertainty,
                "cfdem_retained_fraction": simulated_fraction,
                "cfdem_minus_xie2021": simulated_fraction - reference_fraction,
                "absolute_difference": absolute_difference,
                "within_xie2021_digitization_interval": (
                    absolute_difference <= digitization_uncertainty
                ),
                "digitization_interval_excess": digitization_interval_excess,
                "initial_fine_count": initial_count,
                "final_retained_count": retained_count,
                "simulation_time_s": final_time_s,
                "tail_last_1s_start_time_s": float(
                    tail_change["last_1s"]["start_time_s"]
                ),
                "tail_last_2s_start_time_s": float(
                    tail_change["last_2s"]["start_time_s"]
                ),
                "tail_window_end_time_s": float(
                    tail_change["last_1s"]["end_time_s"]
                ),
                "breakthrough_fraction_increment_last_1s": float(
                    tail_change["last_1s"][
                        "breakthrough_fraction_increment"
                    ]
                ),
                "breakthrough_fraction_increment_last_2s": float(
                    tail_change["last_2s"][
                        "breakthrough_fraction_increment"
                    ]
                ),
                "source_case": str(metrics["case"]),
                "reference": "Xie et al., Chemical Engineering Science 231 (2021) 116261, Fig. 21",
            }
        )
        for row in case_history:
            histories.append(
                {
                    "df_over_dp": ratio,
                    "time_s": float(row["time_s"]),
                    "retained_fraction": float(row["retained_fraction"]),
                    "cumulative_breakthrough_fraction": float(
                        row["cumulative_breakthrough_fraction"]
                    ),
                }
            )
    differences = np.array([float(row["cfdem_minus_xie2021"]) for row in paired])
    reference_values = np.array(
        [float(row["xie2021_retained_fraction"]) for row in paired]
    )
    simulated_values = np.array(
        [float(row["cfdem_retained_fraction"]) for row in paired]
    )
    digitization_interval_excesses = np.array(
        [float(row["digitization_interval_excess"]) for row in paired]
    )
    simulated_increments = np.diff(simulated_values)
    monotonic_violation_count = int(np.sum(simulated_increments < 0.0))
    simulated_endpoint_change = float(simulated_values[-1] - simulated_values[0])
    monotonic_trend_reproduced = bool(
        monotonic_violation_count == 0 and simulated_endpoint_change > 0.0
    )
    summary: dict[str, object] = {
        "status": "complete",
        "comparison_point_count": len(paired),
        "rmse_retained_fraction": float(np.sqrt(np.mean(differences**2))),
        "mae_retained_fraction": float(np.mean(np.abs(differences))),
        "maximum_absolute_difference": float(np.max(np.abs(differences))),
        "within_digitization_interval_count": sum(
            bool(row["within_xie2021_digitization_interval"]) for row in paired
        ),
        "digitization_interval_excess_rmse": float(
            np.sqrt(np.mean(digitization_interval_excesses**2))
        ),
        "maximum_digitization_interval_excess": float(
            np.max(digitization_interval_excesses)
        ),
        "pearson_correlation": float(np.corrcoef(reference_values, simulated_values)[0, 1]),
        "monotonic_trend_reproduced": monotonic_trend_reproduced,
        "monotonic_violation_count": monotonic_violation_count,
        "simulated_endpoint_retention_change": simulated_endpoint_change,
        "reference": "Xie et al., Chemical Engineering Science 231 (2021) 116261, Fig. 21",
        "reference_doi": "10.1016/j.ces.2020.116261",
        "shared_case_configuration_verified": True,
        "formal_input_data_sha256_verified": True,
        "formal_input_data_sha256": EXPECTED_INPUT_DATA_SHA256,
        "shared_case_configuration": EXPECTED_SHARED_METADATA,
        "reference_digitization": {
            "render_resolution_dpi": 300,
            "method": reference_metadata["method"],
            "vertical_full_scale_pixels": full_scale_pixels,
            "one_pixel_retained_fraction_uncertainty": digitization_uncertainty,
        },
        "rows": paired,
    }
    return paired, histories, summary


def main() -> int:
    """Build the final full-duration literature comparison tables."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--results-root", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    paired, histories, summary = collect(args.reference, args.results_root)
    args.out.mkdir(parents=True, exist_ok=True)
    write_csv(args.out / "xie2021_full_validation.csv", paired)
    write_csv(args.out / "xie2021_full_retention_histories.csv", histories)
    (args.out / "xie2021_full_validation.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
