#!/usr/bin/env python3
"""Audit Paper 2 manuscript readiness against current evidence files."""

from __future__ import annotations

import json
import re
import struct
import zipfile
from pathlib import Path

import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
OUT_JSON = PAPER_DIR / "data" / "paper2_manuscript_readiness.json"
OUT_MD = PAPER_DIR / "notes" / "paper2_manuscript_readiness.md"
DEPOSIT_ARCHIVE = PAPER_DIR / "deposit" / "archives" / "paper2_lightweight_deposit.zip"
DEPOSIT_ARCHIVE_MEMBERS = {
    "deposit_staging_readme": "paper2_lightweight_deposit/README.md",
    "deposit_staging_manifest": "paper2_lightweight_deposit/MANIFEST.json",
}


REQUIRED_FILES = {
    "latex_main": PAPER_DIR / "latex" / "main.tex",
    "latex_pdf": PAPER_DIR / "latex" / "main.pdf",
    "reference_library": PAPER_DIR / "references" / "paper2_references.bib",
    "citation_support_map": PAPER_DIR / "references" / "citation_support_map.md",
    "evidence_map": PAPER_DIR / "notes" / "evidence_map.md",
    "results_draft": PAPER_DIR / "draft" / "results_draft.md",
    "captions_draft": PAPER_DIR / "draft" / "figure_captions_draft.md",
    "baseline_topology": PAPER_DIR / "data" / "baseline_topology_metrics_effective.json",
    "representative_states": PAPER_DIR / "tables" / "paper2_fig3_representative_state_source.csv",
    "mechanism_summary": PAPER_DIR / "tables" / "paper2_mechanism_summary_source.csv",
    "loading_summary": PAPER_DIR / "tables" / "paper2_fig4_loading_summary_source.csv",
    "loading_btc": PAPER_DIR / "tables" / "paper2_fig4_loading_btc_source.csv",
    "loading_blockage": PAPER_DIR / "tables" / "paper2_fig4_loading_blockage_source.csv",
    "voxel_size_sensitivity": PAPER_DIR / "tables" / "paper2_voxel_size_sensitivity_source.csv",
    "pressure_proxy": PAPER_DIR / "tables" / "paper2_pressure_proxy_source.csv",
    "voxel_pressure_pilot": PAPER_DIR / "tables" / "paper2_voxel_pressure_pilot_source.csv",
    "time_resolved_deposition": PAPER_DIR / "tables" / "paper2_time_resolved_deposition_source.csv",
    "time_resolved_blockage_profile": PAPER_DIR / "tables" / "paper2_time_resolved_blockage_profile_source.csv",
    "front_migration_metrics": PAPER_DIR / "tables" / "paper2_front_migration_metrics_source.csv",
    "front_migration_events": PAPER_DIR / "tables" / "paper2_front_migration_events_source.csv",
    "localized_production_summary": PAPER_DIR / "tables" / "explicit_localized_production_summary.csv",
    "localized_production_timeseries": PAPER_DIR / "tables" / "explicit_localized_production_timeseries.csv",
    "localized_diagnostic_summary": PAPER_DIR / "tables" / "explicit_localized_diagnostic_summary.csv",
    "localized_production_status_md": PAPER_DIR / "notes" / "localized_production_status.md",
    "localized_production_status_json": PAPER_DIR / "data" / "localized_production_status.json",
    "localized_production_status_script": PAPER_DIR / "scripts" / "make_localized_production_status.py",
    "remaining_localized_run_plan_md": PAPER_DIR / "notes" / "remaining_localized_run_plan.md",
    "remaining_localized_run_plan_json": PAPER_DIR / "data" / "remaining_localized_run_plan.json",
    "remaining_localized_run_plan_script": PAPER_DIR / "scripts" / "make_remaining_localized_run_plan.py",
    "remaining_localized_run_shell": PAPER_DIR / "scripts" / "run_remaining_localized_production.sh",
    "latest_localized_remote_bundle": PAPER_DIR / "data" / "latest_localized_remote_bundle.json",
    "supplementary_tables_md": PAPER_DIR / "supplementary" / "supplementary_tables.md",
    "supplementary_figures_md": PAPER_DIR / "supplementary" / "supplementary_figures.md",
    "supplementary_table_s1": PAPER_DIR / "supplementary" / "table_s1_case_matrix.csv",
    "supplementary_table_s2": PAPER_DIR / "supplementary" / "table_s2_structural_metrics.csv",
    "supplementary_table_s3": PAPER_DIR / "supplementary" / "table_s3_resolution_and_status.csv",
    "supplementary_table_s4": PAPER_DIR / "supplementary" / "table_s4_mechanism_evidence_matrix.csv",
    "supplementary_table_s5": PAPER_DIR / "supplementary" / "table_s5_literature_positioning_matrix.csv",
    "supplementary_table_s6": PAPER_DIR / "supplementary" / "table_s6_pressure_proxy_summary.csv",
    "supplementary_table_s7": PAPER_DIR / "supplementary" / "table_s7_voxel_pressure_pilot_summary.csv",
    "supplementary_table_s12": PAPER_DIR / "supplementary" / "table_s12_dimensionless_mechanism_map.csv",
    "supplementary_table_s13": PAPER_DIR / "supplementary" / "table_s13_mechanism_claim_table.csv",
    "supplementary_tables_metadata": PAPER_DIR / "supplementary" / "supplementary_tables_metadata.json",
    "figure_provenance_json": PAPER_DIR / "data" / "figure_provenance_manifest.json",
    "figure_provenance_md": PAPER_DIR / "notes" / "figure_provenance_manifest.md",
    "supplementary_figure_reference_audit_json": PAPER_DIR / "data" / "supplementary_figure_reference_audit.json",
    "supplementary_figure_reference_audit_md": PAPER_DIR / "notes" / "supplementary_figure_reference_audit.md",
    "supplementary_figure_reference_audit_script": PAPER_DIR / "scripts" / "audit_supplementary_figure_references.py",
    "supplementary_table_reference_audit_json": PAPER_DIR / "data" / "supplementary_table_reference_audit.json",
    "supplementary_table_reference_audit_md": PAPER_DIR / "notes" / "supplementary_table_reference_audit.md",
    "supplementary_table_reference_audit_script": PAPER_DIR / "scripts" / "audit_supplementary_table_references.py",
    "reviewer_risk_matrix_json": PAPER_DIR / "data" / "reviewer_risk_matrix.json",
    "reviewer_risk_matrix_md": PAPER_DIR / "notes" / "reviewer_risk_matrix.md",
    "submission_cover_letter_draft": PAPER_DIR / "submission" / "cover_letter_draft.md",
    "submission_checklist": PAPER_DIR / "submission" / "submission_checklist.md",
    "claim_boundary_statement": PAPER_DIR / "submission" / "claim_boundary_statement.md",
    "data_code_deposit_manifest_json": PAPER_DIR / "data" / "data_code_deposit_manifest.json",
    "data_code_deposit_manifest_md": PAPER_DIR / "submission" / "data_code_deposit_manifest.md",
    "submission_metadata_template": PAPER_DIR / "submission" / "submission_metadata_template.md",
    "author_declarations_checklist": PAPER_DIR / "submission" / "author_declarations_checklist.md",
    "author_confirmation_request_md": PAPER_DIR / "submission" / "author_confirmation_request.md",
    "author_confirmation_request_json": PAPER_DIR / "submission" / "author_confirmation_request.json",
    "author_confirmation_request_script": PAPER_DIR / "scripts" / "make_author_confirmation_request.py",
    "reviewer_precheck_md": PAPER_DIR / "submission" / "reviewer_precheck.md",
    "reviewer_precheck_json": PAPER_DIR / "submission" / "reviewer_precheck.json",
    "reviewer_precheck_script": PAPER_DIR / "scripts" / "make_reviewer_precheck.py",
    "deposit_staging_readme": PAPER_DIR / "deposit" / "paper2_lightweight_deposit" / "README.md",
    "deposit_staging_manifest": PAPER_DIR / "deposit" / "paper2_lightweight_deposit" / "MANIFEST.json",
    "deposit_archive_zip": PAPER_DIR / "deposit" / "archives" / "paper2_lightweight_deposit.zip",
    "deposit_archive_sha256": PAPER_DIR / "deposit" / "archives" / "paper2_lightweight_deposit.zip.sha256",
    "deposit_archive_summary": PAPER_DIR / "deposit" / "archives" / "paper2_lightweight_deposit_archive_summary.json",
    "journal_submission_readme": PAPER_DIR / "submission_package" / "journal_submission_files" / "README.md",
    "journal_submission_manifest": PAPER_DIR / "submission_package" / "journal_submission_files" / "MANIFEST.json",
    "final_submission_gate_json": PAPER_DIR / "submission" / "final_submission_gate.json",
    "final_submission_gate_md": PAPER_DIR / "submission" / "final_submission_gate.md",
    "submission_metadata_yaml": PAPER_DIR / "submission" / "submission_metadata.yaml",
    "apply_submission_metadata_script": PAPER_DIR / "scripts" / "apply_submission_metadata.py",
    "journal_submission_archive_zip": PAPER_DIR / "submission_package" / "archives" / "paper2_journal_submission_files.zip",
    "journal_submission_archive_sha256": PAPER_DIR / "submission_package" / "archives" / "paper2_journal_submission_files.zip.sha256",
    "journal_submission_archive_summary": PAPER_DIR / "submission_package" / "archives" / "paper2_journal_submission_files_archive_summary.json",
    "current_project_status": PAPER_DIR / "CURRENT_PROJECT_STATUS.md",
    "highlights": PAPER_DIR / "submission" / "highlights.md",
    "graphical_abstract_png": PAPER_DIR / "figures" / "paper2_graphical_abstract.png",
    "graphical_abstract_pdf": PAPER_DIR / "figures" / "paper2_graphical_abstract.pdf",
    "graphical_abstract_svg": PAPER_DIR / "figures" / "paper2_graphical_abstract.svg",
    "graphical_abstract_script": PAPER_DIR / "scripts" / "make_graphical_abstract.py",
    "repository_metadata": PAPER_DIR / "submission" / "repository_deposit" / "repository_metadata.yaml",
    "repository_citation_cff": PAPER_DIR / "submission" / "repository_deposit" / "CITATION.cff",
    "repository_upload_instructions": PAPER_DIR / "submission" / "repository_deposit" / "UPLOAD_INSTRUCTIONS.md",
    "submission_form_packet_json": PAPER_DIR / "submission" / "submission_form_packet.json",
    "submission_form_packet_md": PAPER_DIR / "submission" / "submission_form_packet.md",
    "submission_form_packet_script": PAPER_DIR / "scripts" / "make_submission_form_packet.py",
    "final_metadata_completion_packet_json": PAPER_DIR / "submission" / "final_metadata_completion_packet.json",
    "final_metadata_completion_packet_md": PAPER_DIR / "submission" / "final_metadata_completion_packet.md",
    "final_metadata_completion_packet_script": PAPER_DIR / "scripts" / "make_final_metadata_completion_packet.py",
    "submission_decision_ledger_json": PAPER_DIR / "submission" / "submission_decision_ledger.json",
    "submission_decision_ledger_md": PAPER_DIR / "submission" / "submission_decision_ledger.md",
    "submission_decision_ledger_csv": PAPER_DIR / "submission" / "submission_decision_ledger.csv",
    "submission_decision_ledger_script": PAPER_DIR / "scripts" / "make_submission_decision_ledger.py",
}

REQUIRED_FIGURE_STEMS = [
    "paper2_fig1_voxel_topology_framework",
    "paper2_fig2_baseline_voxel_topology",
    "paper2_fig3_representative_debris_blockage",
    "paper2_fig4_loading_clogging_response",
    "paper2_figS1_voxel_size_sensitivity",
    "paper2_figS2_voxel_coarsening_stress_test",
    "paper2_figS3_ergun_pressure_proxy",
    "paper2_figS4_time_resolved_deposition",
    "paper2_figS5_front_migration_metrics",
    "paper2_figS8_explicit_localized_production_summary",
    "paper2_figS11_mechanism_evidence_map",
    "paper2_graphical_abstract",
]


def read_text(path: Path) -> str:
    """Read a UTF-8 text file with a clear missing-file error."""
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def rel(path: Path) -> str:
    """Return a project-relative path string."""
    return str(path.relative_to(PROJECT_ROOT))


def figure_exports_complete(stem: str) -> bool:
    """Return whether PNG, PDF, and SVG exports exist for a figure stem."""
    return all((PAPER_DIR / "figures" / f"{stem}.{suffix}").exists() for suffix in ("png", "pdf", "svg"))


def archive_member_exists(archive_path: Path, member: str) -> bool:
    """Return whether a zip archive contains a non-directory member."""
    if not archive_path.exists() or archive_path.stat().st_size == 0:
        return False
    try:
        with zipfile.ZipFile(archive_path) as archive:
            info = archive.getinfo(member)
    except (KeyError, zipfile.BadZipFile):
        return False
    return not info.is_dir() and info.file_size > 0


def png_size(path: Path) -> tuple[int, int]:
    """Read PNG width and height using the PNG header."""
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Not a PNG file: {path}")
    width, height = struct.unpack(">II", data[16:24])
    return int(width), int(height)


def audit_required_files() -> list[dict[str, object]]:
    """Audit required manuscript files and source tables."""
    rows: list[dict[str, object]] = []
    for name, path in REQUIRED_FILES.items():
        archive_member = DEPOSIT_ARCHIVE_MEMBERS.get(name)
        if archive_member and not (path.exists() and path.stat().st_size > 0):
            member_ok = archive_member_exists(DEPOSIT_ARCHIVE, archive_member)
            rows.append(
                {
                    "item": name,
                    "category": "file",
                    "status": "supported" if member_ok else "missing",
                    "evidence": f"{rel(DEPOSIT_ARCHIVE)}::{archive_member}",
                    "details": {"checked_archive_member": archive_member, "live_staging_exists": False},
                }
            )
            continue
        rows.append(
            {
                "item": name,
                "category": "file",
                "status": "supported" if path.exists() and path.stat().st_size > 0 else "missing",
                "evidence": rel(path),
            }
        )
    for stem in REQUIRED_FIGURE_STEMS:
        rows.append(
            {
                "item": stem,
                "category": "figure_exports",
                "status": "supported" if figure_exports_complete(stem) else "missing",
                "evidence": f"papers/paper2_voxel_topology_clogging/figures/{stem}.[png,pdf,svg]",
            }
        )
    return rows


def audit_latex_structure() -> list[dict[str, object]]:
    """Audit the LaTeX manuscript structure and wording boundaries."""
    path = REQUIRED_FILES["latex_main"]
    text = read_text(path)
    required_markers = [
        "\\begin{abstract}",
        "\\section{Introduction}",
        "\\section{Methods}",
        "\\section{Results}",
        "\\section{Discussion}",
        "\\section{Conclusions}",
        "\\section*{Data availability}",
        "\\section*{Code availability}",
        "\\section*{Declaration of competing interest}",
    ]
    missing = [marker for marker in required_markers if marker not in text]
    rows = [
        {
            "item": "latex_core_sections",
            "category": "manuscript",
            "status": "supported" if not missing else "partial",
            "evidence": rel(path),
            "details": {"missing": missing},
        }
    ]
    experimental_imaging_boundary = (
        "DEM-derived voxel reconstructions" in text
        and (
            "not experimental computed-tomography data" in text
            or "not be described as experimental computed tomography" in text
            or "not be interpreted as experimental computed-tomography measurements" in text
        )
    )
    required_boundaries = [
        "default software screening reference",
        "not safety limits",
        "rather than as evidence of bed-scale pore-network clogging",
        "single-seed loading states",
    ]
    missing_boundaries = [snippet for snippet in required_boundaries if snippet not in text]
    if not experimental_imaging_boundary:
        missing_boundaries.append("experimental imaging boundary")
    forbidden_overclaims = [
        "universal critical clogging threshold",
        "pressure-calibrated safety criterion is established",
        "experimental CT validation",
        "validated by CT",
        "validated by PIV",
    ]
    present_forbidden = [snippet for snippet in forbidden_overclaims if snippet in text]
    rows.append(
        {
            "item": "claim_boundary_language",
            "category": "manuscript",
            "status": "supported" if not missing_boundaries and not present_forbidden else "partial",
            "evidence": rel(path),
            "details": {"missing_required": missing_boundaries, "present_forbidden": present_forbidden},
        }
    )
    return rows


def audit_quantitative_claims() -> list[dict[str, object]]:
    """Audit key quantitative Paper 2 claims against source tables."""
    text = read_text(REQUIRED_FILES["latex_main"])
    baseline = json.loads(read_text(REQUIRED_FILES["baseline_topology"]))
    representative = pd.read_csv(REQUIRED_FILES["representative_states"])
    mechanism = pd.read_csv(REQUIRED_FILES["mechanism_summary"])
    loading = pd.read_csv(REQUIRED_FILES["loading_summary"])
    voxel_sensitivity = pd.read_csv(REQUIRED_FILES["voxel_size_sensitivity"])
    pressure_proxy = pd.read_csv(REQUIRED_FILES["pressure_proxy"])
    voxel_pressure_pilot = pd.read_csv(REQUIRED_FILES["voxel_pressure_pilot"])
    time_deposition = pd.read_csv(REQUIRED_FILES["time_resolved_deposition"])
    front_metrics = pd.read_csv(REQUIRED_FILES["front_migration_metrics"])
    localized_summary = pd.read_csv(REQUIRED_FILES["localized_production_summary"])
    table_s1 = pd.read_csv(REQUIRED_FILES["supplementary_table_s1"])
    table_s3 = pd.read_csv(REQUIRED_FILES["supplementary_table_s3"])
    table_s4 = pd.read_csv(REQUIRED_FILES["supplementary_table_s4"])
    table_s5 = pd.read_csv(REQUIRED_FILES["supplementary_table_s5"])
    table_s6 = pd.read_csv(REQUIRED_FILES["supplementary_table_s6"])
    table_s7 = pd.read_csv(REQUIRED_FILES["supplementary_table_s7"])
    table_s12 = pd.read_csv(REQUIRED_FILES["supplementary_table_s12"])
    table_s13 = pd.read_csv(REQUIRED_FILES["supplementary_table_s13"])
    figure_provenance = json.loads(read_text(REQUIRED_FILES["figure_provenance_json"]))
    supplementary_figure_reference_audit = json.loads(read_text(REQUIRED_FILES["supplementary_figure_reference_audit_json"]))
    supplementary_table_reference_audit = json.loads(read_text(REQUIRED_FILES["supplementary_table_reference_audit_json"]))
    rows: list[dict[str, object]] = []

    baseline_ok = (
        abs(float(baseline["porosity"]) - 0.4114) < 5e-4
        and abs(float(baseline["largest_connected_void_fraction"]) - 0.9921) < 5e-4
        and abs(float(baseline["fractal_dimension"]) - 2.694) < 5e-4
        and int(baseline["euler_number"]) == -18225
    )
    baseline_text_ok = all(snippet in text for snippet in ["0.4114", "0.9921", "2.694", "-18225"])
    rows.append(
        {
            "item": "baseline_topology_claims",
            "category": "quantitative_claim",
            "status": "supported" if baseline_ok and baseline_text_ok else "partial",
            "evidence": rel(REQUIRED_FILES["baseline_topology"]),
        }
    )

    fdw_text_ok = all(f"{value:.2f}" in text for value in representative["drag_to_weight_ratio"].astype(float))
    btc_text_ok = all((f"{value:.4f}" in text or abs(float(value)) < 1e-12) for value in representative["final_BTC"].astype(float))
    rows.append(
        {
            "item": "representative_state_claims",
            "category": "quantitative_claim",
            "status": "supported" if len(representative) == 3 and fdw_text_ok and btc_text_ok else "partial",
            "evidence": rel(REQUIRED_FILES["representative_states"]),
            "details": {"representative_rows": int(len(representative))},
        }
    )
    mechanism_ok = (
        len(mechanism) == 3
        and float(mechanism["peak_blockage_x_over_L"].min()) < 0.20
        and float(mechanism["peak_blockage_x_over_L"].max()) > 0.99
        and set(mechanism["mechanism_label"]) == {
            "internal filtering without outlet breakthrough",
            "downstream migration with outlet-side enrichment",
        }
    )
    mechanism_text_ok = all(snippet in text for snippet in ["8.35", "44.95", "internal filtering", "outlet-side enrichment"])
    rows.append(
        {
            "item": "mechanism_summary_claims",
            "category": "quantitative_claim",
            "status": "supported" if mechanism_ok and mechanism_text_ok else "partial",
            "evidence": rel(REQUIRED_FILES["mechanism_summary"]),
            "details": {
                "peak_x_over_L_min": float(mechanism["peak_blockage_x_over_L"].min()),
                "peak_x_over_L_max": float(mechanism["peak_blockage_x_over_L"].max()),
            },
        }
    )

    loading_ok = (
        set(loading["debris_total_number"].astype(int)) == {3000, 6000, 10000}
        and set(loading["final_Nout"].astype(int)) == {55, 85, 156}
        and float(loading["Ib_no_pressure"].max()) < 2e-5
        and not bool(loading["pressure_used"].astype(bool).any())
    )
    loading_text_ok = all(snippet in text for snippet in ["3000", "6000", "10000", "55", "85", "156", "1.77\\times10^{-5}"])
    rows.append(
        {
            "item": "loading_and_Ib_claims",
            "category": "quantitative_claim",
            "status": "supported" if loading_ok and loading_text_ok else "partial",
            "evidence": rel(REQUIRED_FILES["loading_summary"]),
            "details": {"Ib_max": float(loading["Ib_no_pressure"].max())},
        }
    )
    revox = voxel_sensitivity[voxel_sensitivity["analysis_type"] == "revoxelized"].copy()
    revox_025 = revox[abs(revox["effective_voxel_size_m"].astype(float) - 0.00025) < 1e-12]
    revox_020_040 = revox[
        (revox["effective_voxel_size_m"].astype(float) >= 0.00020)
        & (revox["effective_voxel_size_m"].astype(float) <= 0.00040)
    ]
    sensitivity_ok = (
        len(revox) == 5
        and len(revox_025) == 1
        and abs(float(revox_025.iloc[0]["porosity"]) - float(baseline["porosity"])) < 1e-12
        and abs(float(revox_025.iloc[0]["outlet_connected_fraction_x"]) - float(baseline["outlet_connected_fraction"])) < 1e-12
        and float(revox_020_040["outlet_connected_fraction_x"].min()) > 0.95
        and float(revox[revox["effective_voxel_size_m"] == 0.00050]["outlet_connected_fraction_x"].iloc[0]) < 0.80
    )
    sensitivity_text_ok = all(snippet in text for snippet in ["0.20", "0.50", "0.743", "0.95"])
    rows.append(
        {
            "item": "voxel_size_sensitivity_claims",
            "category": "quantitative_claim",
            "status": "supported" if sensitivity_ok and sensitivity_text_ok else "partial",
            "evidence": rel(REQUIRED_FILES["voxel_size_sensitivity"]),
            "details": {
                "revoxelized_rows": int(len(revox)),
                "outlet_connected_020_040_min": float(revox_020_040["outlet_connected_fraction_x"].min()),
            },
        }
    )
    pressure_ok = (
        set(pressure_proxy["debris_total_number"].astype(int)) == {3000, 6000, 10000}
        and float(pressure_proxy["baseline_pressure_gradient_pa_m"].iloc[0]) > 3.8e4
        and float(pressure_proxy["profile_pressure_increase_ratio"].max()) < 2.0e-5
        and float(pressure_proxy["peak_local_pressure_increase_ratio"].max()) < 1.0e-4
        and bool(pressure_proxy["pressure_proxy_not_cfd"].astype(bool).all())
    )
    pressure_text_ok = all(snippet in text for snippet in ["3.90\\times10^{4}", "3.77\\times10^{-6}", "8.25\\times10^{-5}", "not CFD"])
    rows.append(
        {
            "item": "ergun_pressure_proxy_claims",
            "category": "quantitative_claim",
            "status": "supported" if pressure_ok and pressure_text_ok else "partial",
            "evidence": rel(REQUIRED_FILES["pressure_proxy"]),
            "details": {
                "profile_pressure_increase_ratio_max": float(pressure_proxy["profile_pressure_increase_ratio"].max()),
                "peak_local_pressure_increase_ratio_max": float(pressure_proxy["peak_local_pressure_increase_ratio"].max()),
            },
        }
    )
    loading_pressure = voxel_pressure_pilot[voxel_pressure_pilot["debris_total_number"].astype(int) > 0]
    voxel_pressure_ok = (
        len(voxel_pressure_pilot) == 4
        and set(loading_pressure["debris_total_number"].astype(int)) == {3000, 6000, 10000}
        and bool(voxel_pressure_pilot["not_cfd"].astype(bool).all())
        and bool(voxel_pressure_pilot["not_lbm"].astype(bool).all())
        and float(loading_pressure["conductance_loss"].max()) < 1.0e-5
        and float(loading_pressure["relative_resistance"].min()) >= 1.0
        and int(voxel_pressure_pilot["through_pore_voxels"].iloc[0]) > 200000
    )
    voxel_pressure_text_ok = all(snippet in text for snippet in ["2.8\\times10^{-6}", "9.3\\times10^{-6}", "Darcy--Laplace", "not Navier--Stokes CFD or LBM"])
    rows.append(
        {
            "item": "voxel_pressure_pilot_claims",
            "category": "quantitative_claim",
            "status": "supported" if voxel_pressure_ok and voxel_pressure_text_ok else "partial",
            "evidence": rel(REQUIRED_FILES["voxel_pressure_pilot"]),
            "details": {
                "conductance_loss_min": float(loading_pressure["conductance_loss"].min()),
                "conductance_loss_max": float(loading_pressure["conductance_loss"].max()),
                "through_pore_voxels": int(voxel_pressure_pilot["through_pore_voxels"].iloc[0]),
            },
        }
    )
    first_nonzero = time_deposition[time_deposition["BTC"].astype(float) > 0.0].iloc[0]
    final_time = time_deposition.iloc[-1]
    max_peak = time_deposition.loc[time_deposition["peak_blockage_ratio"].astype(float).idxmax()]
    time_ok = (
        len(time_deposition) == 50
        and abs(float(first_nonzero["elapsed_time"]) - 0.03159) < 5e-6
        and abs(float(final_time["BTC"]) - 0.0183333333333333) < 1e-9
        and float(final_time["x_q99_over_L"]) > 0.99
        and float(max_peak["peak_blockage_x_over_L"]) < 0.10
        and float(final_time["x_mean_over_L"]) > 0.63
    )
    time_text_ok = all(snippet in text for snippet in ["0.0316", "0.640", "0.997", "early inlet-side"])
    rows.append(
        {
            "item": "time_resolved_deposition_claims",
            "category": "quantitative_claim",
            "status": "supported" if time_ok and time_text_ok else "partial",
            "evidence": rel(REQUIRED_FILES["time_resolved_deposition"]),
            "details": {
                "frames": int(len(time_deposition)),
                "first_nonzero_elapsed_time": float(first_nonzero["elapsed_time"]),
                "final_x_q99_over_L": float(final_time["x_q99_over_L"]),
            },
        }
    )
    front_row = front_metrics.iloc[0]
    front_ok = (
        len(front_metrics) == 1
        and abs(float(front_row["x_mean_speed_m_per_s"]) - 0.7815) < 5e-4
        and abs(float(front_row["x_q99_speed_m_per_s"]) - 1.1255) < 5e-4
        and float(front_row["x_q99_fit_r2"]) > 0.998
        and float(front_row["q99_09_minus_first_BTC_s"]) > 0.0040 - 1e-9
    )
    front_text_ok = all(snippet in text for snippet in ["0.78", "1.13", "0.998", "0.0041"])
    rows.append(
        {
            "item": "front_migration_metrics_claims",
            "category": "quantitative_claim",
            "status": "supported" if front_ok and front_text_ok else "partial",
            "evidence": rel(REQUIRED_FILES["front_migration_metrics"]),
            "details": {
                "x_mean_speed_m_per_s": float(front_row["x_mean_speed_m_per_s"]),
                "x_q99_speed_m_per_s": float(front_row["x_q99_speed_m_per_s"]),
                "q99_09_minus_first_BTC_s": float(front_row["q99_09_minus_first_BTC_s"]),
            },
        }
    )
    localized_906 = localized_summary[localized_summary["job_id"].astype(str).str.startswith("906")]
    localized_907 = localized_summary[localized_summary["job_id"].astype(str).str.startswith("907")]
    localized_908 = localized_summary[localized_summary["job_id"].astype(str).str.startswith("908")]
    target_rows_ok = (
        len(localized_summary) == 3
        and localized_summary["target_time_reached"].astype(bool).all()
        and localized_summary["debris_count_ok"].astype(bool).all()
        and (localized_summary["final_outlet_fraction"].astype(float).abs() < 1e-12).all()
    )
    localized_ok = (
        target_rows_ok
        and
        len(localized_906) == 1
        and abs(float(localized_906.iloc[0]["final_time_s"]) - 0.04) < 1e-12
        and abs(float(localized_906.iloc[0]["final_source_fraction"]) - 0.5793333333333334) < 1e-9
        and abs(float(localized_906.iloc[0]["final_downstream_fraction"]) - 0.42033333333333334) < 1e-9
        and len(localized_907) == 1
        and abs(float(localized_907.iloc[0]["final_time_s"]) - 0.01005) < 1e-12
        and abs(float(localized_907.iloc[0]["final_source_fraction"]) - 0.8961333333333333) < 1e-9
        and abs(float(localized_907.iloc[0]["final_downstream_fraction"]) - 0.10093333333333333) < 1e-9
        and len(localized_908) == 1
        and abs(float(localized_908.iloc[0]["final_time_s"]) - 0.01) < 1e-12
        and abs(float(localized_908.iloc[0]["final_source_fraction"]) - 0.8945) < 1e-9
        and abs(float(localized_908.iloc[0]["final_downstream_fraction"]) - 0.10123333333333333) < 1e-9
    )
    localized_text_ok = all(
        snippet in text
        for snippet in ["57.93\\%", "42.03\\%", "89.61\\%", "10.09\\%", "89.45\\%", "no outlet release"]
    )
    rows.append(
        {
            "item": "localized_production_claims",
            "category": "quantitative_claim",
            "status": "supported" if localized_ok and localized_text_ok else "partial",
            "evidence": rel(REQUIRED_FILES["localized_production_summary"]),
            "details": {
                "production_jobs_available": int(len(localized_summary)),
                "final_time_s": float(localized_906.iloc[0]["final_time_s"]) if len(localized_906) else None,
                "localized_907_time_s": float(localized_907.iloc[0]["final_time_s"]) if len(localized_907) else None,
                "localized_908_time_s": float(localized_908.iloc[0]["final_time_s"]) if len(localized_908) else None,
            },
        }
    )
    supplementary_ok = (
        len(table_s1) == 9
        and len(table_s3) == 8
        and len(table_s4) >= 8
        and len(table_s5) >= 8
        and len(table_s6) == 3
        and len(table_s7) == 4
        and len(table_s12) == 9
        and len(table_s13) == 3
        and int(table_s1["evidence_level"].isin(["production_partial", "production_target_reached"]).sum()) >= 3
        and int(table_s3["status"].isin(["production_partial", "production_target_reached"]).sum()) >= 3
        and {"source-zone retention", "pre-clogging loading response"}.issubset(set(table_s4["mechanism"]))
        and "ThisWork" in set(table_s5["reference_key"])
        and bool(table_s6["pressure_proxy_not_cfd"].astype(bool).all())
        and bool(table_s7["not_cfd"].astype(bool).all())
        and {"drive_state", "loading_state", "localized_source_state"} == set(table_s12["evidence_family"])
        and "source-retained sparse front" in set(table_s12["mechanism_regime"])
        and float(table_s12["front_bulk_gap_over_L"].max()) > 0.5
        and "M03_breakthrough_decouples_from_topology_loss" in set(table_s13["claim_id"])
        and "no universal critical clogging transition" in " ".join(table_s13["boundary"].astype(str)).lower()
        and {"Natsui2012FinesClogging", "Boccardo2019PackedBedDeposition", "Parvan2020Clogging"}.issubset(
            set(table_s5["reference_key"])
        )
        and int(table_s3["status"].isin(["production_partial", "production_target_reached"]).sum()) >= 1
    )
    rows.append(
        {
            "item": "supplementary_case_tables",
            "category": "supplementary",
            "status": "supported" if supplementary_ok else "partial",
            "evidence": rel(REQUIRED_FILES["supplementary_tables_md"]),
            "details": {
                "table_s1_rows": int(len(table_s1)),
                "table_s3_rows": int(len(table_s3)),
                "table_s4_rows": int(len(table_s4)),
                "table_s5_rows": int(len(table_s5)),
                "table_s12_rows": int(len(table_s12)),
                "table_s13_rows": int(len(table_s13)),
                "localized_production_available": int(
                    table_s3["status"].isin(["production_partial", "production_target_reached"]).sum()
                ),
                "localized_production_target_reached": int((table_s3["status"] == "production_target_reached").sum()),
            },
        }
    )
    required_figure_stems = {
        "paper2_fig1_voxel_topology_framework",
        "paper2_fig2_baseline_voxel_topology",
        "paper2_fig3_representative_debris_blockage",
        "paper2_fig4_loading_clogging_response",
        "paper2_figS8_explicit_localized_production_summary",
        "paper2_figS9_907_tail_capture_mechanism",
        "paper2_figS10_source_position_comparison",
        "paper2_figS11_mechanism_evidence_map",
        "paper2_figS12_voxel_pressure_pilot",
        "paper2_figS13_cropped_flow_domains",
        "paper2_figS14_cropped_flow_permeability",
        "paper2_figS15_cropped_flow_permeability_sensitivity",
        "paper2_figS16_dimensionless_mechanism_map",
        "paper2_figS23_openfoam_pressure_evidence",
    }
    available_figure_stems = {str(row.get("stem")) for row in figure_provenance}
    provenance_ok = (
        len(figure_provenance) >= len(required_figure_stems)
        and required_figure_stems.issubset(available_figure_stems)
        and all(bool(row.get("exports_complete")) for row in figure_provenance)
        and all(bool(row.get("all_sources_available")) for row in figure_provenance)
        and all(bool(row.get("script_exists")) for row in figure_provenance)
    )
    rows.append(
        {
            "item": "figure_provenance_manifest",
            "category": "provenance",
            "status": "supported" if provenance_ok else "partial",
            "evidence": rel(REQUIRED_FILES["figure_provenance_json"]),
            "details": {
                "figure_count": int(len(figure_provenance)),
                "required_stems_present": sorted(required_figure_stems.intersection(available_figure_stems)),
                "missing_required_stems": sorted(required_figure_stems.difference(available_figure_stems)),
            },
        }
    )
    rows.append(
        {
            "item": "supplementary_figure_reference_audit",
            "category": "provenance",
            "status": "supported" if supplementary_figure_reference_audit.get("decision") == "pass" else "partial",
            "evidence": rel(REQUIRED_FILES["supplementary_figure_reference_audit_json"]),
            "details": {
                "failure_count": int(supplementary_figure_reference_audit.get("failure_count", -1)),
                "manuscript_refs": supplementary_figure_reference_audit.get("manuscript_refs", []),
                "missing_from_catalogue": supplementary_figure_reference_audit.get("missing_from_catalogue", []),
                "missing_from_provenance": supplementary_figure_reference_audit.get("missing_from_provenance", []),
            },
        }
    )
    rows.append(
        {
            "item": "supplementary_table_reference_audit",
            "category": "provenance",
            "status": "supported" if supplementary_table_reference_audit.get("decision") == "pass" else "partial",
            "evidence": rel(REQUIRED_FILES["supplementary_table_reference_audit_json"]),
            "details": {
                "failure_count": int(supplementary_table_reference_audit.get("failure_count", -1)),
                "manuscript_refs": supplementary_table_reference_audit.get("manuscript_refs", []),
                "missing_from_catalogue": supplementary_table_reference_audit.get("missing_from_catalogue", []),
                "missing_from_metadata": supplementary_table_reference_audit.get("missing_from_metadata", []),
                "missing_csv": supplementary_table_reference_audit.get("missing_csv", []),
            },
        }
    )
    return rows


def audit_citations() -> list[dict[str, object]]:
    """Audit citation keys and support-map coverage."""
    tex = read_text(REQUIRED_FILES["latex_main"])
    bib = read_text(REQUIRED_FILES["reference_library"])
    support = read_text(REQUIRED_FILES["citation_support_map"])
    cited_keys = sorted(set(re.findall(r"\\citep\{([^{}]+)\}", tex)))
    flat_keys = sorted({key.strip() for group in cited_keys for key in group.split(",")})
    missing_bib = [key for key in flat_keys if f"{{{key}," not in bib]
    missing_support = [key for key in flat_keys if key not in support]
    return [
        {
            "item": "citation_bib_coverage",
            "category": "citation",
            "status": "supported" if not missing_bib else "partial",
            "evidence": rel(REQUIRED_FILES["reference_library"]),
            "details": {"missing_bib": missing_bib, "citation_count": len(flat_keys)},
        },
        {
            "item": "citation_support_map_coverage",
            "category": "citation",
            "status": "supported" if not missing_support else "partial",
            "evidence": rel(REQUIRED_FILES["citation_support_map"]),
            "details": {"missing_support_map": missing_support},
        },
    ]


def audit_submission_artifacts() -> list[dict[str, object]]:
    """Audit journal-facing submission artifacts beyond the manuscript PDF."""
    rows: list[dict[str, object]] = []

    highlights_text = read_text(REQUIRED_FILES["highlights"])
    highlights = [line.strip()[2:].strip() for line in highlights_text.splitlines() if line.strip().startswith("- ")]
    highlight_lengths = [len(line) for line in highlights]
    highlights_ok = 3 <= len(highlights) <= 5 and all(length <= 85 for length in highlight_lengths)
    rows.append(
        {
            "item": "elsevier_highlights",
            "category": "submission_artifact",
            "status": "supported" if highlights_ok else "partial",
            "evidence": rel(REQUIRED_FILES["highlights"]),
            "details": {"count": len(highlights), "lengths": highlight_lengths},
        }
    )

    ga_paths = [
        REQUIRED_FILES["graphical_abstract_png"],
        REQUIRED_FILES["graphical_abstract_pdf"],
        REQUIRED_FILES["graphical_abstract_svg"],
    ]
    width, height = png_size(REQUIRED_FILES["graphical_abstract_png"])
    graphical_abstract_ok = all(path.exists() and path.stat().st_size > 0 for path in ga_paths) and width >= 1328 and height >= 531
    rows.append(
        {
            "item": "graphical_abstract_exports",
            "category": "submission_artifact",
            "status": "supported" if graphical_abstract_ok else "partial",
            "evidence": "papers/paper2_voxel_topology_clogging/figures/paper2_graphical_abstract.[png,pdf,svg]",
            "details": {"png_width": width, "png_height": height},
        }
    )

    repository_files = [
        REQUIRED_FILES["repository_metadata"],
        REQUIRED_FILES["repository_citation_cff"],
        REQUIRED_FILES["repository_upload_instructions"],
    ]
    repository_text = "\n".join(read_text(path) for path in repository_files)
    repository_ok = all(path.exists() and path.stat().st_size > 0 for path in repository_files) and "TBC" in repository_text
    rows.append(
        {
            "item": "repository_deposit_metadata_bundle",
            "category": "submission_artifact",
            "status": "supported" if repository_ok else "partial",
            "evidence": "papers/paper2_voxel_topology_clogging/submission/repository_deposit/",
            "details": {"placeholder_doi_retained": "TBC" in repository_text},
        }
    )
    packet = json.loads(read_text(REQUIRED_FILES["submission_form_packet_json"]))
    packet_md = read_text(REQUIRED_FILES["submission_form_packet_md"])
    packet_ok = (
        packet.get("journal") == "Chemical Engineering Science"
        and str(packet.get("title", "")).startswith("Separating breakthrough from pore-network clogging indicators")
        and len(packet.get("authors", [])) == 6
        and len(packet.get("keywords", [])) == 7
        and len(packet.get("highlights", [])) == 5
        and "Remaining Administrative Note" in packet_md
    )
    rows.append(
        {
            "item": "submission_form_packet",
            "category": "submission_artifact",
            "status": "supported" if packet_ok else "partial",
            "evidence": rel(REQUIRED_FILES["submission_form_packet_md"]),
            "details": {
                "authors": len(packet.get("authors", [])),
                "keywords": len(packet.get("keywords", [])),
                "highlights": len(packet.get("highlights", [])),
            },
        }
    )
    decision_ledger = json.loads(read_text(REQUIRED_FILES["submission_decision_ledger_json"]))
    route_decisions = decision_ledger.get("summary", {}).get("route_decisions", {})
    ledger_ok = (
        route_decisions.get("R01_submit_bounded_ces_after_admin") == "not_ready_admin_only"
        and route_decisions.get("R02_wait_for_repeat_then_ces") == "not_ready_admin_only_repeat_evidence_available"
        and route_decisions.get("R03_cej_stretch") == "do_not_submit_current_version"
    )
    rows.append(
        {
            "item": "submission_decision_ledger",
            "category": "submission_artifact",
            "status": "supported" if ledger_ok else "partial",
            "evidence": rel(REQUIRED_FILES["submission_decision_ledger_md"]),
            "details": {"route_decisions": route_decisions},
        }
    )
    return rows


def audit_submission_gaps() -> list[dict[str, object]]:
    """Record known submission-blocking gaps that need author input or more data."""
    text = read_text(REQUIRED_FILES["latex_main"])
    metadata = yaml.safe_load(read_text(REQUIRED_FILES["submission_metadata_yaml"]))
    if not isinstance(metadata, dict):
        metadata = {}
    checks = [
        ("public_repository_doi", "A public repository DOI/accession has not yet been assigned"),
        ("competing_interest_confirmation", "This statement should be confirmed by all authors"),
        ("acknowledgement_confirmation", "acknowledgements should be confirmed before submission"),
    ]
    rows = []
    for item, snippet in checks:
        rows.append(
            {
                "item": item,
                "category": "submission_gap",
                "status": "needs_confirmation" if snippet in text else "supported",
                "evidence": rel(REQUIRED_FILES["latex_main"]),
            }
        )
    corresponding_author = metadata.get("corresponding_author", {})
    corresponding_ok = (
        isinstance(corresponding_author, dict)
        and bool(corresponding_author.get("confirmed", False))
        and str(corresponding_author.get("name", "")).strip().upper() not in {"", "TBC", "TBD"}
        and str(corresponding_author.get("email", "")).strip().upper() not in {"", "TBC", "TBD"}
    )
    rows.append(
        {
            "item": "corresponding_author_confirmation",
            "category": "submission_gap",
            "status": "supported" if corresponding_ok else "needs_confirmation",
            "evidence": rel(REQUIRED_FILES["submission_metadata_yaml"]),
        }
    )
    rows.append(
        {
            "item": "pressure_calibrated_Ib",
            "category": "evidence_gap",
            "status": "not_required_for_preclogging_scope",
            "evidence": "Manuscript explicitly frames Ib as pressure-free structural pre-screening.",
        }
    )
    rows.append(
        {
            "item": "critical_clogging_transition",
            "category": "evidence_gap",
            "status": "not_supported_current_scope",
            "evidence": "Current loading scan has three single-seed states and no measurable connectivity loss.",
        }
    )
    production_summary = pd.read_csv(REQUIRED_FILES["localized_production_summary"])
    if not production_summary.empty and "target_time_reached" in production_summary.columns:
        production_job_count = int(production_summary["target_time_reached"].astype(bool).sum())
    else:
        production_job_count = int(production_summary["job_id"].nunique()) if not production_summary.empty else 0
    rows.append(
        {
            "item": "localized_907_908_production_completion",
            "category": "evidence_gap",
            "status": "not_supported_current_scope" if production_job_count < 3 else "supported",
            "evidence": f"{production_job_count}/3 localized-release production jobs reached target physical time.",
        }
    )
    return rows


def build_rows() -> list[dict[str, object]]:
    """Build all readiness rows."""
    rows: list[dict[str, object]] = []
    rows.extend(audit_required_files())
    rows.extend(audit_latex_structure())
    rows.extend(audit_quantitative_claims())
    rows.extend(audit_citations())
    rows.extend(audit_submission_artifacts())
    rows.extend(audit_submission_gaps())
    return rows


def write_reports(rows: list[dict[str, object]]) -> None:
    """Write JSON and Markdown readiness reports."""
    OUT_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Paper 2 Manuscript Readiness Audit",
        "",
        "| Item | Category | Status | Evidence |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(f"| {row['item']} | {row['category']} | {row['status']} | {row.get('evidence', '')} |")
    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row["status"])] = counts.get(str(row["status"]), 0) + 1
    lines.extend(["", f"Summary: `{json.dumps(counts, sort_keys=True)}`"])
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    """Run the Paper 2 manuscript-readiness audit."""
    rows = build_rows()
    write_reports(rows)
    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row["status"])] = counts.get(str(row["status"]), 0) + 1
    print(json.dumps(counts, sort_keys=True))
    print(f"Wrote: {OUT_JSON}")
    print(f"Wrote: {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
