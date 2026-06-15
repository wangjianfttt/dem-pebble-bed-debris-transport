#!/usr/bin/env python3
"""Create manuscript-ready evidence assets from returned OpenFOAM results.

The script is intentionally conservative. If no returned pressure-drop results
are available, it writes status files only and does not create a placeholder
figure. This prevents empty or inferred CFD evidence from entering the paper.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from pandas.errors import EmptyDataError


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
DEFAULT_RESULTS = PAPER_DIR / "tables" / "paper2_openfoam_handoff_results_summary.csv"
DEFAULT_HANDOFF = PAPER_DIR / "tables" / "paper2_flow_solver_handoff_manifest.csv"
OUT_TABLE = PAPER_DIR / "tables" / "paper2_openfoam_pressure_evidence_source.csv"
OUT_SCREENING_TABLE = PAPER_DIR / "tables" / "paper2_openfoam_pressure_screening_source.csv"
OUT_GEOMETRY_AUDIT = PAPER_DIR / "tables" / "paper2_openfoam_geometry_audit.csv"
OUT_JSON = PAPER_DIR / "data" / "paper2_openfoam_pressure_evidence_summary.json"
OUT_MD = PAPER_DIR / "notes" / "openfoam_pressure_evidence_status.md"
OUT_FIG = PAPER_DIR / "figures" / "paper2_figS23_openfoam_pressure_evidence"
EVIDENCE_COLUMNS = [
    "case_name",
    "debris_total_number",
    "checkMesh_ok",
    "simpleFoam_completed",
    "pressure_drop_available",
    "pressure_time_aligned",
    "current_handoff_fields_present",
    "checkMesh_skew6_ok",
    "max_skewness",
    "p_inlet_area_average",
    "p_outlet_area_average",
    "delta_p_inlet_minus_outlet",
    "relative_delta_p_to_first_valid_case",
    "evidence_boundary",
]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS, help="Parsed OpenFOAM result CSV.")
    parser.add_argument("--handoff", type=Path, default=DEFAULT_HANDOFF, help="Flow-solver handoff manifest CSV.")
    parser.add_argument("--out-table", type=Path, default=OUT_TABLE, help="Output source-data CSV.")
    parser.add_argument("--out-screening-table", type=Path, default=OUT_SCREENING_TABLE, help="Output strict-vs-screening source-data CSV.")
    parser.add_argument("--out-geometry-audit", type=Path, default=OUT_GEOMETRY_AUDIT, help="Output geometry audit CSV.")
    parser.add_argument("--out-json", type=Path, default=OUT_JSON, help="Output status JSON.")
    parser.add_argument("--out-md", type=Path, default=OUT_MD, help="Output status Markdown.")
    parser.add_argument("--out-fig", type=Path, default=OUT_FIG, help="Output figure path without extension.")
    return parser.parse_args()


def load_optional_csv(path: Path) -> pd.DataFrame:
    """Read a CSV file if it exists and is non-empty; otherwise return an empty frame."""
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except EmptyDataError:
        return pd.DataFrame()


def parse_bool_series(series: pd.Series) -> pd.Series:
    """Parse bool-like CSV values without treating non-empty strings as truthy."""
    if series.dtype == bool:
        return series
    normalized = series.astype(str).str.strip().str.lower()
    true_values = {"true", "1", "yes", "y"}
    false_values = {"false", "0", "no", "n", "", "nan", "none", "<na>"}
    unknown = set(normalized.unique()).difference(true_values | false_values)
    if unknown:
        raise ValueError(f"Unexpected boolean values: {sorted(unknown)}")
    return normalized.isin(true_values)


def sha256_bytes(data: bytes) -> str:
    """Return the SHA256 digest for a bytes object."""
    return hashlib.sha256(data).hexdigest()


def project_path(path_value: object) -> Path | None:
    """Return an absolute project path for a CSV path value if available."""
    if pd.isna(path_value):
        return None
    path = Path(str(path_value))
    return path if path.is_absolute() else PROJECT_ROOT / path


def build_geometry_audit(handoff: pd.DataFrame) -> pd.DataFrame:
    """Audit whether OpenFOAM handoff cases actually contain distinct geometries.

    The OpenFOAM pressure comparison is only meaningful as a loading trend if
    the handoff geometry changes across the loading cases or an explicitly
    separate porous-resistance field is supplied. A repeated hard-wall pore
    geometry can still be useful as a solver smoke test, but it must not be
    promoted to manuscript-ready loading-dependent pressure evidence.
    """

    columns = [
        "case_name",
        "debris_total_number",
        "source_domain",
        "pore_mask_found",
        "voxel_crop_found",
        "pore_mask_sha256",
        "voxel_array_sha256",
        "hydraulic_resistance_field_found",
        "hydraulic_resistance_field_sha256",
        "pore_nodes",
        "solid_nodes",
        "geometry_signature",
        "flow_input_signature",
    ]
    if handoff.empty or "case_name" not in handoff.columns:
        return pd.DataFrame(columns=columns)

    rows: list[dict[str, object]] = []
    for _, row in handoff.iterrows():
        source_dir = project_path(row.get("source_domain", pd.NA))
        pore_path = source_dir / "pore_mask.npy" if source_dir is not None else None
        voxel_path = source_dir / "voxel_crop.npz" if source_dir is not None else None
        resistance_path = source_dir / "hydraulic_resistance_multiplier_field.npy" if source_dir is not None else None
        pore_hash = pd.NA
        voxel_hash = pd.NA
        resistance_hash = pd.NA
        pore_nodes = pd.NA
        solid_nodes = pd.NA
        if pore_path is not None and pore_path.exists():
            pore = np.load(pore_path).astype(bool)
            pore_hash = sha256_bytes(np.ascontiguousarray(pore).tobytes())
            pore_nodes = int(pore.sum())
        if voxel_path is not None and voxel_path.exists():
            voxel = np.load(voxel_path)["voxel"]
            voxel_hash = sha256_bytes(np.ascontiguousarray(voxel).tobytes())
            solid_nodes = int(np.count_nonzero(voxel))
            if pd.isna(pore_nodes):
                pore_nodes = int(np.count_nonzero(voxel == 0))
        if resistance_path is not None and resistance_path.exists():
            resistance = np.load(resistance_path).astype(np.float32)
            resistance_hash = sha256_bytes(np.ascontiguousarray(resistance).tobytes())
        signature = f"{pore_hash}|{voxel_hash}" if not pd.isna(pore_hash) and not pd.isna(voxel_hash) else pd.NA
        flow_signature = (
            f"{signature}|{resistance_hash}"
            if not pd.isna(signature) and not pd.isna(resistance_hash)
            else signature
        )
        rows.append(
            {
                "case_name": row["case_name"],
                "debris_total_number": row.get("debris_total_number", pd.NA),
                "source_domain": row.get("source_domain", pd.NA),
                "pore_mask_found": bool(pore_path is not None and pore_path.exists()),
                "voxel_crop_found": bool(voxel_path is not None and voxel_path.exists()),
                "pore_mask_sha256": pore_hash,
                "voxel_array_sha256": voxel_hash,
                "hydraulic_resistance_field_found": bool(resistance_path is not None and resistance_path.exists()),
                "hydraulic_resistance_field_sha256": resistance_hash,
                "pore_nodes": pore_nodes,
                "solid_nodes": solid_nodes,
                "geometry_signature": signature,
                "flow_input_signature": flow_signature,
            }
        )
    return pd.DataFrame(rows, columns=columns)


def geometry_gate_status(geometry_audit: pd.DataFrame, expected_cases: int) -> dict[str, object]:
    """Return conservative manuscript-gate fields for OpenFOAM geometry diversity."""
    if geometry_audit.empty:
        return {
            "geometry_audit_available": False,
            "unique_flow_geometries": 0,
            "geometry_distinguishable": expected_cases <= 1,
            "geometry_gate_boundary": "No geometry audit rows were available; pressure evidence remains controlled by mesh/log gates only.",
        }
    signature_column = "flow_input_signature" if "flow_input_signature" in geometry_audit.columns else "geometry_signature"
    valid = geometry_audit.dropna(subset=[signature_column]).copy()
    if valid.empty:
        return {
            "geometry_audit_available": False,
            "unique_flow_geometries": 0,
            "geometry_distinguishable": True,
            "geometry_gate_boundary": "No readable pore/voxel geometry files were available for audit; pressure evidence remains controlled by mesh/log gates only.",
        }
    unique = int(valid[signature_column].nunique())
    distinguishable = bool(expected_cases <= 1 or (len(valid) >= expected_cases and unique >= expected_cases))
    boundary = (
        "Flow inputs differ across all expected loading cases."
        if distinguishable
        else "Repeated hard-wall pore geometry and no distinguishable porous-resistance/debris field across loading cases; do not interpret returned OpenFOAM pressure drops as loading-dependent pressure evidence unless a separate porous-resistance/debris field is supplied."
    )
    return {
        "geometry_audit_available": True,
        "unique_flow_geometries": unique,
        "geometry_distinguishable": distinguishable,
        "geometry_gate_boundary": boundary,
    }


def build_pressure_evidence(results: pd.DataFrame, handoff: pd.DataFrame) -> pd.DataFrame:
    """Return pressure-drop rows that pass basic OpenFOAM evidence checks."""
    if results.empty:
        return pd.DataFrame(columns=EVIDENCE_COLUMNS)
    required = {
        "case_name",
        "checkMesh_ok",
        "simpleFoam_completed",
        "pressure_drop_available",
        "delta_p_inlet_minus_outlet",
    }
    missing = required.difference(results.columns)
    if missing:
        raise ValueError(f"OpenFOAM result table is missing required columns: {sorted(missing)}")
    table = results.copy()
    for column in ["checkMesh_ok", "simpleFoam_completed", "pressure_drop_available"]:
        table[column] = parse_bool_series(table[column])
    if "checkMesh_skew6_ok" in table.columns:
        table["checkMesh_skew6_ok"] = parse_bool_series(table["checkMesh_skew6_ok"])
    else:
        table["checkMesh_skew6_ok"] = False
    if "pressure_time_aligned" not in table.columns:
        table["pressure_time_aligned"] = True
    table["pressure_time_aligned"] = parse_bool_series(table["pressure_time_aligned"])
    table = add_handoff_field_freshness(table, handoff)
    valid = table[
        table["checkMesh_ok"]
        & table["simpleFoam_completed"]
        & table["pressure_drop_available"]
        & table["pressure_time_aligned"]
        & table["current_handoff_fields_present"]
    ].copy()
    if valid.empty:
        return pd.DataFrame(columns=EVIDENCE_COLUMNS)
    if not handoff.empty and {"case_name", "debris_total_number"}.issubset(handoff.columns):
        handoff_columns = [
            column
            for column in ["case_name", "debris_total_number", "porosity", "stl_triangles"]
            if column in handoff.columns and (column == "case_name" or column not in valid.columns)
        ]
        if len(handoff_columns) > 1:
            valid = valid.merge(handoff[handoff_columns], on="case_name", how="left")
    valid["delta_p_inlet_minus_outlet"] = valid["delta_p_inlet_minus_outlet"].astype(float)
    if "debris_total_number" in valid.columns:
        valid = valid.sort_values(["debris_total_number", "case_name"], na_position="last")
    else:
        valid = valid.sort_values("case_name")
    if len(valid) >= 2:
        first = float(valid["delta_p_inlet_minus_outlet"].iloc[0])
        valid["relative_delta_p_to_first_valid_case"] = valid["delta_p_inlet_minus_outlet"] / first if first != 0 else pd.NA
    else:
        valid["relative_delta_p_to_first_valid_case"] = pd.NA
    valid["evidence_boundary"] = "returned OpenFOAM pressure drop with passing checkMesh/simpleFoam logs and aligned inlet/outlet pressure sampling times"
    for column in EVIDENCE_COLUMNS:
        if column not in valid.columns:
            valid[column] = pd.NA
    return valid[EVIDENCE_COLUMNS + [column for column in valid.columns if column not in EVIDENCE_COLUMNS]]


def build_pressure_screening_table(results: pd.DataFrame, handoff: pd.DataFrame) -> pd.DataFrame:
    """Return all returned pressure rows with strict and engineering screening gates.

    The strict gate requires the default `checkMesh` pass. The engineering
    screening gate additionally reports cases with completed solver output,
    aligned pressure sampling and `checkMesh -skewThreshold 6` pass. These
    rows are useful for reviewer triage but should not be called strict
    manuscript-ready pressure evidence.
    """

    columns = [
        "case_name",
        "debris_total_number",
        "checkMesh_ok",
        "checkMesh_skew6_ok",
        "max_skewness",
        "simpleFoam_completed",
        "pressure_drop_available",
        "pressure_time_aligned",
        "current_handoff_hydraulic_field_expected",
        "result_hydraulic_field_found",
        "solver_hydraulic_field_coupled",
        "current_handoff_darcy_coefficient",
        "result_darcy_coefficient",
        "current_handoff_darcy_matches",
        "current_handoff_fields_present",
        "delta_p_inlet_minus_outlet",
        "strict_pressure_evidence",
        "engineering_screening_evidence",
        "gate_boundary",
    ]
    if results.empty:
        return pd.DataFrame(columns=columns)
    table = results.copy()
    for column in ["checkMesh_ok", "simpleFoam_completed", "pressure_drop_available"]:
        if column in table.columns:
            table[column] = parse_bool_series(table[column])
        else:
            table[column] = False
    if "checkMesh_skew6_ok" in table.columns:
        table["checkMesh_skew6_ok"] = parse_bool_series(table["checkMesh_skew6_ok"])
    else:
        table["checkMesh_skew6_ok"] = False
    if "pressure_time_aligned" in table.columns:
        table["pressure_time_aligned"] = parse_bool_series(table["pressure_time_aligned"])
    else:
        table["pressure_time_aligned"] = True
    table = add_handoff_field_freshness(table, handoff)
    table["strict_pressure_evidence"] = (
        table["checkMesh_ok"]
        & table["simpleFoam_completed"]
        & table["pressure_drop_available"]
        & table["pressure_time_aligned"]
        & table["current_handoff_fields_present"]
    )
    table["engineering_screening_evidence"] = (
        table["checkMesh_skew6_ok"]
        & table["simpleFoam_completed"]
        & table["pressure_drop_available"]
        & table["pressure_time_aligned"]
        & table["current_handoff_fields_present"]
    )
    table["gate_boundary"] = table["strict_pressure_evidence"].map(
        {
            True: "strict manuscript-ready pressure evidence after default checkMesh pass",
            False: "screening only unless default checkMesh also passes",
        }
    )
    if "debris_total_number" in table.columns:
        table = table.sort_values(["debris_total_number", "case_name"], na_position="last")
    else:
        table = table.sort_values("case_name")
    for column in columns:
        if column not in table.columns:
            table[column] = pd.NA
    return table[columns]


def result_hydraulic_field_found(case_dir_value: object) -> bool:
    """Return whether a returned OpenFOAM result contains the current hydraulic field."""
    path = project_path(case_dir_value)
    if path is None:
        return False
    return (path / "constant" / "hydraulic_resistance_multiplier_field.npy").exists()


def solver_hydraulic_field_coupled(case_dir_value: object) -> bool:
    """Return whether case dictionaries reference the hydraulic-resistance field."""
    path = project_path(case_dir_value)
    if path is None or not path.exists():
        return False
    candidates = list((path / "system").glob("*")) + list((path / "constant").glob("*Properties"))
    for extra in ["fvModels", "fvOptions", "coordinateSystems", "porosityProperties"]:
        candidate = path / "constant" / extra
        if candidate.exists():
            candidates.append(candidate)
    patterns = [
        "hydraulic_resistance_multiplier_field",
        "hydraulicResistance",
        "explicitPorositySource",
        "fvOptions",
        "porosityForce",
        "DarcyForchheimer",
        "debrisResistanceZone",
    ]
    for file_path in candidates:
        if not file_path.is_file():
            continue
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        if any(pattern in text for pattern in patterns):
            return True
    return False


def result_darcy_coefficient(case_dir_value: object) -> float | pd.NA:
    """Parse the Darcy coefficient from a returned OpenFOAM `constant/fvModels` file."""
    path = project_path(case_dir_value)
    if path is None:
        return pd.NA
    fv_models = path / "constant" / "fvModels"
    if not fv_models.exists():
        return pd.NA
    text = fv_models.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"^\s*D\s+([0-9.+\-Ee]+)\s*;", text, flags=re.MULTILINE)
    if not match:
        return pd.NA
    try:
        return float(match.group(1))
    except ValueError:
        return pd.NA


def add_handoff_field_freshness(results: pd.DataFrame, handoff: pd.DataFrame) -> pd.DataFrame:
    """Add fields that indicate whether returned results match current handoff inputs."""
    table = results.copy()
    if not handoff.empty and "case_name" in handoff.columns:
        extra = [
            col
            for col in [
                "case_name",
                "debris_total_number",
                "openfoam_hydraulic_resistance_field",
                "hydraulic_resistance_field_available",
                "openfoam_darcy_screening_coefficient",
            ]
            if col in handoff.columns
        ]
        table = table.merge(handoff[extra], on="case_name", how="left")
    expected = (
        parse_bool_series(table["hydraulic_resistance_field_available"])
        if "hydraulic_resistance_field_available" in table.columns
        else pd.Series(False, index=table.index)
    )
    found = table["case_dir"].map(result_hydraulic_field_found) if "case_dir" in table.columns else pd.Series(False, index=table.index)
    coupled = table["case_dir"].map(solver_hydraulic_field_coupled) if "case_dir" in table.columns else pd.Series(False, index=table.index)
    result_darcy = table["case_dir"].map(result_darcy_coefficient) if "case_dir" in table.columns else pd.Series(pd.NA, index=table.index)
    current_darcy = (
        pd.to_numeric(table["openfoam_darcy_screening_coefficient"], errors="coerce")
        if "openfoam_darcy_screening_coefficient" in table.columns
        else pd.Series(np.nan, index=table.index)
    )
    darcy_matches = []
    for expected_d, returned_d in zip(current_darcy, result_darcy):
        if pd.isna(expected_d):
            darcy_matches.append(True)
        elif pd.isna(returned_d):
            darcy_matches.append(False)
        else:
            darcy_matches.append(bool(np.isclose(float(expected_d), float(returned_d), rtol=1e-6, atol=1e-9)))
    table["current_handoff_hydraulic_field_expected"] = expected
    table["result_hydraulic_field_found"] = found
    table["solver_hydraulic_field_coupled"] = coupled
    table["current_handoff_darcy_coefficient"] = current_darcy
    table["result_darcy_coefficient"] = result_darcy
    table["current_handoff_darcy_matches"] = pd.Series(darcy_matches, index=table.index)
    table["current_handoff_fields_present"] = (~expected) | (found & coupled & table["current_handoff_darcy_matches"])
    return table


def classify_evidence(valid: pd.DataFrame, expected_cases: int) -> str:
    """Classify the OpenFOAM evidence status for manuscript use."""
    if valid.empty:
        return "awaiting_results"
    if len(valid) < expected_cases:
        return "partial_pressure_evidence"
    return "complete_pressure_evidence"


def write_markdown(valid: pd.DataFrame, screening: pd.DataFrame, status: dict[str, object], out_md: Path) -> None:
    """Write a compact Markdown status note."""
    lines = [
        "# OpenFOAM Pressure Evidence Status",
        "",
        f"Status: `{status['status']}`",
        "",
        "This file is generated from returned OpenFOAM handoff outputs. It does not infer pressure-drop values when solver results are absent.",
        "",
    ]
    if valid.empty:
        lines.append("No manuscript-ready OpenFOAM pressure-drop cases are available yet.")
    else:
        lines.extend(["| Case | Debris count | delta p | relative delta p |", "|---|---:|---:|---:|"])
        for _, row in valid.iterrows():
            debris = "" if pd.isna(row.get("debris_total_number", pd.NA)) else f"{int(row['debris_total_number'])}"
            rel = row.get("relative_delta_p_to_first_valid_case", pd.NA)
            rel_text = "" if pd.isna(rel) else f"{float(rel):.6g}"
            lines.append(f"| {row['case_name']} | {debris} | {float(row['delta_p_inlet_minus_outlet']):.6g} | {rel_text} |")
        lines.extend(["", f"Figure created: `{status['figure_base']}`"])
    if not screening.empty:
        lines.extend(
            [
                "",
                "## Strict vs screening gates",
                "",
                "| Case | Debris count | default checkMesh | skew6 checkMesh | max skewness | delta p | Gate |",
                "|---|---:|---:|---:|---:|---:|---|",
            ]
        )
        for _, row in screening.iterrows():
            debris = "" if pd.isna(row.get("debris_total_number", pd.NA)) else f"{int(row['debris_total_number'])}"
            delta = "" if pd.isna(row.get("delta_p_inlet_minus_outlet", pd.NA)) else f"{float(row['delta_p_inlet_minus_outlet']):.6g}"
            skew = "" if pd.isna(row.get("max_skewness", pd.NA)) else f"{float(row['max_skewness']):.4g}"
            gate = "strict" if bool(row["strict_pressure_evidence"]) else ("screening" if bool(row["engineering_screening_evidence"]) else "not usable")
            lines.append(
                f"| {row['case_name']} | {debris} | {str(bool(row['checkMesh_ok'])).lower()} | {str(bool(row['checkMesh_skew6_ok'])).lower()} | {skew} | {delta} | {gate} |"
            )
    lines.extend(
        [
            "",
            "## Geometry gate",
            "",
            f"- Geometry audit available: `{str(bool(status.get('geometry_audit_available', False))).lower()}`",
            f"- Unique flow geometries: `{int(status.get('unique_flow_geometries', 0))}`",
            f"- Geometry distinguishable: `{str(bool(status.get('geometry_distinguishable', True))).lower()}`",
            f"- Boundary: {status.get('geometry_gate_boundary', '')}",
        ]
    )
    lines.extend(
        [
            "",
            "Manuscript boundary: these values can be used only as returned solver evidence after mesh/log checks pass. They should not be described as experimental pressure measurements.",
        ]
    )
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_pressure_evidence(valid: pd.DataFrame, out_fig: Path) -> list[str]:
    """Plot pressure-drop evidence when at least one valid returned case exists."""
    if valid.empty:
        for ext in [".png", ".pdf", ".svg"]:
            path = out_fig.with_suffix(ext)
            if path.exists():
                path.unlink()
        return []
    import matplotlib.pyplot as plt

    x = valid["debris_total_number"] if "debris_total_number" in valid.columns else valid["case_name"]
    fig, ax = plt.subplots(figsize=(4.8, 3.2))
    ax.scatter(x, valid["delta_p_inlet_minus_outlet"], s=48, color="#2b6cb0", edgecolor="black", linewidth=0.5)
    if len(valid) > 1 and "debris_total_number" in valid.columns:
        ax.plot(x, valid["delta_p_inlet_minus_outlet"], color="#2b6cb0", linewidth=1.2)
    ax.set_xlabel("Injected debris count")
    ax.set_ylabel(r"$\Delta p_{\mathrm{inlet-outlet}}$ (OpenFOAM units)")
    ax.set_title("Returned pore-flow pressure evidence")
    ax.grid(True, color="#d9d9d9", linewidth=0.6, alpha=0.8)
    fig.tight_layout()
    out_fig.parent.mkdir(parents=True, exist_ok=True)
    outputs = []
    for ext in [".png", ".pdf", ".svg"]:
        path = out_fig.with_suffix(ext)
        fig.savefig(path, dpi=300)
        outputs.append(str(path))
    plt.close(fig)
    return outputs


def make_assets(
    results_csv: Path = DEFAULT_RESULTS,
    handoff_csv: Path = DEFAULT_HANDOFF,
    out_table: Path = OUT_TABLE,
    out_screening_table: Path = OUT_SCREENING_TABLE,
    out_geometry_audit: Path = OUT_GEOMETRY_AUDIT,
    out_json: Path = OUT_JSON,
    out_md: Path = OUT_MD,
    out_fig: Path = OUT_FIG,
) -> dict[str, object]:
    """Create OpenFOAM pressure-evidence source data, status files and optional figure."""
    results = load_optional_csv(results_csv)
    handoff = load_optional_csv(handoff_csv)
    valid = build_pressure_evidence(results, handoff)
    screening = build_pressure_screening_table(results, handoff)
    geometry_audit = build_geometry_audit(handoff)
    expected_cases = int(len(handoff)) if not handoff.empty else 0
    status_name = classify_evidence(valid, expected_cases)
    geometry_status = geometry_gate_status(geometry_audit, expected_cases)
    manuscript_ready = bool(status_name == "complete_pressure_evidence" and geometry_status["geometry_distinguishable"])
    engineering_screening_cases = int(screening["engineering_screening_evidence"].sum()) if not screening.empty else 0
    strict_pressure_cases = int(screening["strict_pressure_evidence"].sum()) if not screening.empty else 0
    stale_result_cases = (
        int(
            (
                screening["current_handoff_hydraulic_field_expected"]
                & (
                    ~screening["result_hydraulic_field_found"]
                    | (screening["solver_hydraulic_field_coupled"] & ~screening["current_handoff_darcy_matches"])
                )
            ).sum()
        )
        if not screening.empty
        and {
            "current_handoff_hydraulic_field_expected",
            "result_hydraulic_field_found",
            "solver_hydraulic_field_coupled",
            "current_handoff_darcy_matches",
        }.issubset(screening.columns)
        else 0
    )
    uncoupled_field_cases = (
        int((screening["current_handoff_hydraulic_field_expected"] & screening["result_hydraulic_field_found"] & ~screening["solver_hydraulic_field_coupled"]).sum())
        if not screening.empty and {"current_handoff_hydraulic_field_expected", "result_hydraulic_field_found", "solver_hydraulic_field_coupled"}.issubset(screening.columns)
        else 0
    )
    if stale_result_cases > 0:
        status_name = "stale_pressure_evidence_after_handoff_update"
        manuscript_ready = False
    elif uncoupled_field_cases > 0:
        status_name = "uncoupled_hydraulic_field_screening_evidence"
        manuscript_ready = False
    elif valid.empty and engineering_screening_cases > 0:
        status_name = "screening_only_pressure_evidence"
        manuscript_ready = False
    if status_name == "complete_pressure_evidence" and not geometry_status["geometry_distinguishable"]:
        status_name = "geometry_degenerate_pressure_evidence"
    out_table.parent.mkdir(parents=True, exist_ok=True)
    out_screening_table.parent.mkdir(parents=True, exist_ok=True)
    out_geometry_audit.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    valid.to_csv(out_table, index=False)
    screening.to_csv(out_screening_table, index=False)
    geometry_audit.to_csv(out_geometry_audit, index=False)
    figures = plot_pressure_evidence(valid, out_fig)
    status = {
        "status": status_name,
        "valid_pressure_cases": int(len(valid)),
        "expected_handoff_cases": expected_cases,
        "source_results_csv": str(results_csv),
        "source_handoff_csv": str(handoff_csv),
        "out_table": str(out_table),
        "out_screening_table": str(out_screening_table),
        "out_geometry_audit": str(out_geometry_audit),
        "figure_outputs": figures,
        "figure_base": str(out_fig),
        "manuscript_ready_pressure_evidence": manuscript_ready,
        "engineering_screening_cases": engineering_screening_cases,
        "strict_pressure_cases": strict_pressure_cases,
        "stale_result_cases_after_handoff_update": stale_result_cases,
        "uncoupled_hydraulic_field_cases": uncoupled_field_cases,
        **geometry_status,
        "evidence_boundary": "No pressure values are inferred; valid cases require pressure output, aligned inlet/outlet sampling times and passing checkMesh/simpleFoam logs.",
    }
    out_json.write_text(json.dumps(status, indent=2), encoding="utf-8")
    write_markdown(valid, screening, status, out_md)
    return status


def main() -> int:
    """Run the OpenFOAM pressure-evidence asset generator."""
    args = parse_args()
    status = make_assets(
        results_csv=args.results,
        handoff_csv=args.handoff,
        out_table=args.out_table,
        out_screening_table=args.out_screening_table,
        out_geometry_audit=args.out_geometry_audit,
        out_json=args.out_json,
        out_md=args.out_md,
        out_fig=args.out_fig,
    )
    print(json.dumps(status, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
