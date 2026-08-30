#!/usr/bin/env python3
"""Summarize the formal 12780 pore-flow grid comparison."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
from pathlib import Path


def last_number(text: str, pattern: str, cast=float):
    values = re.findall(pattern, text, flags=re.MULTILINE)
    if not values:
        return None
    return cast(values[-1])


def last_log_value(text: str, pattern: str):
    return last_number(text, pattern, float)


def read_case(case: Path, comparison_dir: Path, cells_per_dp: int):
    check = (case / "log.checkMesh.final").read_text(encoding="utf-8", errors="replace")
    solver = (case / "log.simpleFoam").read_text(encoding="utf-8", errors="replace")
    correction = json.loads(
        (case / "superficial_velocity_correction.json").read_text(encoding="utf-8")
    )
    comparison = json.loads(
        (comparison_dir / f"carrier_field_comparison_c{cells_per_dp}.json").read_text(
            encoding="utf-8"
        )
    )
    cells = last_number(check, r"^\s*cells:\s+(\d+)", int)
    under = last_number(
        check, r"Cells with small determinant \(< 0\.001\) found, number of cells:\s+(\d+)", int
    )
    inlet_p = last_log_value(solver, r"areaAverage\(inlet\) of p =\s*([-+0-9.eE]+)")
    outlet_p = last_log_value(solver, r"areaAverage\(outlet\) of p =\s*([-+0-9.eE]+)")
    inlet_phi = last_log_value(solver, r"sum\(inlet\) of phi =\s*([-+0-9.eE]+)")
    outlet_phi = last_log_value(solver, r"sum\(outlet\) of phi =\s*([-+0-9.eE]+)")
    speed = comparison["void_space_speed_distribution"]["speed_quantiles_m_per_s"]
    m = comparison["metrics_resolved_minus_unresolved"]
    pressure = comparison["cross_sectional_pressure"]
    ergun = comparison.get("ergun_reference", {})
    return {
        "cells_per_dp": cells_per_dp,
        "fluid_cells": cells,
        "small_determinant_cells": under,
        "small_determinant_fraction": under / cells if under is not None else None,
        "open_inlet_area_m2": correction["open_inlet_area_m2"],
        "open_area_fraction": correction["open_area_fraction"],
        "imposed_open_patch_velocity_m_per_s": correction[
            "imposed_open_patch_velocity_m_per_s"
        ],
        "final_inlet_phi_m3_per_s": inlet_phi,
        "final_outlet_phi_m3_per_s": outlet_phi,
        "absolute_outlet_to_inlet_flow_ratio": abs(outlet_phi / inlet_phi),
        "inlet_kinematic_pressure_m2_per_s2": inlet_p,
        "outlet_kinematic_pressure_m2_per_s2": outlet_p,
        "full_window_kinematic_pressure_drop_m2_per_s2": inlet_p - outlet_p,
        "resolved_window_porosity": comparison["resolved_window_porosity"],
        "nominal_window_porosity": comparison.get(
            "nominal_window_porosity_from_sphere_box_integration"
        ),
        "resolved_window_porosity_error": comparison.get("resolved_window_porosity_error"),
        "resolved_dpdx_m_per_s2_per_m": pressure["resolved_dpdx_m_per_s2_per_m"],
        "unresolved_dpdx_m_per_s2_per_m": pressure["unresolved_dpdx_m_per_s2_per_m"],
        "absolute_gradient_ratio_resolved_over_unresolved": pressure[
            "absolute_gradient_ratio_resolved_over_unresolved"
        ],
        "ergun_kinematic_pressure_gradient_m2_per_s2_per_m": ergun.get(
            "kinematic_pressure_gradient_m_per_s2_per_m"
        ),
        "resolved_to_ergun_gradient_ratio": ergun.get(
            "resolved_to_ergun_gradient_ratio"
        ),
        "unresolved_to_ergun_gradient_ratio": ergun.get(
            "unresolved_to_ergun_gradient_ratio"
        ),
        "fluid_phase_ux_pearson_r": m["fluid_phase_ux_m_per_s"]["pearson_r"],
        "fluid_phase_ux_relative_l2": m["fluid_phase_ux_m_per_s"]["relative_l2"],
        "superficial_qx_pearson_r": m["superficial_qx_m_per_s"]["pearson_r"],
        "superficial_qx_relative_l2": m["superficial_qx_m_per_s"]["relative_l2"],
        "void_speed_p10_m_per_s": speed["p10"],
        "void_speed_p50_m_per_s": speed["p50"],
        "void_speed_p90_m_per_s": speed["p90"],
        "void_speed_p95_m_per_s": speed["p95"],
        "void_speed_p99_m_per_s": speed["p99"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case-root", type=Path, required=True)
    parser.add_argument("--comparison-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for cpd in (10, 15, 20):
        case = args.case_root / f"paper3_poreflow_formal12780_upstream12dp_ug010_c{cpd}_stair_v1"
        rows.append(read_case(case, args.comparison_dir, cpd))

    summary = {
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "interpretation": (
            "Grid convergence is assessed jointly from geometry, pressure, velocity "
            "distribution, filtered-field error, flow balance and mesh topology."
        ),
        "rows": rows,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "formal12780_poreflow_grid_convergence.json"
    csv_path = args.output_dir / "formal12780_poreflow_grid_convergence.csv"
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
