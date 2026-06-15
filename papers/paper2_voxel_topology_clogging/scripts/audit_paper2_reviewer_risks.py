#!/usr/bin/env python3
"""Build a reviewer-risk matrix for the Paper 2 manuscript.

The audit is intentionally conservative: it records what a reviewer could
reasonably challenge, whether the current manuscript bounds the claim, and what
evidence would be needed to upgrade the paper beyond the present pre-clogging
scope.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
LATEX_MAIN = PAPER_DIR / "latex" / "main.tex"
READINESS_JSON = PAPER_DIR / "data" / "paper2_manuscript_readiness.json"
LOCALIZED_PRODUCTION = PAPER_DIR / "tables" / "explicit_localized_production_summary.csv"
FIGURE_PROVENANCE = PAPER_DIR / "data" / "figure_provenance_manifest.json"
RESISTANCE_SENSITIVITY = PAPER_DIR / "tables" / "paper2_3d_resistance_amplification_sensitivity_source.csv"
DRAG_SCALING_SUMMARY = PAPER_DIR / "data" / "paper2_drag_scaling_summary.json"
DRAG_SCALING_TABLE = PAPER_DIR / "supplementary" / "table_s18_drag_scaling_summary.csv"
OUT_JSON = PAPER_DIR / "data" / "reviewer_risk_matrix.json"
OUT_MD = PAPER_DIR / "notes" / "reviewer_risk_matrix.md"


REQUIRED_COLUMNS = [
    "risk_id",
    "risk",
    "severity",
    "status",
    "reviewer_concern",
    "current_boundary",
    "evidence_path",
    "mitigation_action",
    "submission_decision",
]


def rel(path: Path) -> str:
    """Return a project-relative path for reports."""
    return str(path.relative_to(PROJECT_ROOT))


def read_text(path: Path) -> str:
    """Read a UTF-8 file and raise a clear error if it is absent."""
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def readable_title(title_line: str) -> str:
    """Extract a reviewer-readable title from the LaTeX title line."""
    match = re.search(r"\\texorpdfstring\{.*?\}\{(?P<title>.*?)\}", title_line)
    if match:
        return match.group("title")
    cleaned = title_line.replace("\\title", "").strip()
    if cleaned.startswith("{") and cleaned.endswith("}"):
        cleaned = cleaned[1:-1]
    return cleaned.replace("\\LiSi", "Li4SiO4")


def load_readiness_summary() -> dict[str, int]:
    """Load readiness status counts if the readiness audit has been run."""
    if not READINESS_JSON.exists():
        return {}
    data = json.loads(read_text(READINESS_JSON))
    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict):
        rows = data.get("rows", [])
    else:
        rows = []
    if not isinstance(rows, list):
        return {}
    return dict(Counter(str(row.get("status", "unknown")) for row in rows))


def count_localized_production_jobs() -> tuple[int, int]:
    """Return completed and expected localized-production job counts."""
    expected = 3
    if not LOCALIZED_PRODUCTION.exists():
        return 0, expected
    df = pd.read_csv(LOCALIZED_PRODUCTION)
    if "target_time_reached" in df.columns:
        completed = int(df["target_time_reached"].astype(bool).sum())
    else:
        completed = int(len(df))
    return completed, expected


def figure_boundary_complete() -> bool:
    """Return whether the provenance manifest includes explicit claim boundaries."""
    if not FIGURE_PROVENANCE.exists():
        return False
    data = json.loads(read_text(FIGURE_PROVENANCE))
    if isinstance(data, list):
        figures = data
    elif isinstance(data, dict):
        figures = data.get("figures", [])
    else:
        figures = []
    if not isinstance(figures, list) or not figures:
        return False
    return all(str(fig.get("claim_boundary", "")).strip() for fig in figures)


def build_risk_rows() -> list[dict[str, Any]]:
    """Build reviewer-risk rows from the current manuscript and evidence state."""
    text = read_text(LATEX_MAIN)
    text_lower = text.lower()
    title_line = next((line for line in text.splitlines() if line.startswith("\\title")), "")
    title_text = readable_title(title_line)
    completed_localized, expected_localized = count_localized_production_jobs()
    readiness_summary = load_readiness_summary()

    has_pressure_boundary = (
        "pressure-free structural pre-screening index" in text_lower
        and "not a pressure-calibrated safety criterion" in text_lower
        and "not used to calibrate" in text_lower
    )
    has_transition_boundary = (
        "pre-clogging migration/filtering regime" in text_lower
        and (
            "identifying a bed-scale clogging threshold will require" in text_lower
            or "a pressure-calibrated critical threshold will require" in text_lower
        )
        and (
            "rather than evidence of bed-scale pore-network degradation" in text_lower
            or "rather than a critical" in text_lower
            or "not a critical clogging transition" in text_lower
        )
    )
    has_single_seed_boundary = (
        "single-seed loading states" in text_lower
        and (
            "discrete terminal responses rather than a fitted loading law" in text_lower
            or "not a monotonic universal loading law" in text_lower
        )
    )
    avoids_experiment_title = "experiment" not in title_line.lower()
    title_lower = title_line.lower()
    avoids_ct_title = "computed tomography" not in title_lower and not re.search(r"(?<![a-z])ct(?![a-z])", title_lower)
    has_dem_reconstruction_boundary = (
        ("dem-derived pore reconstruction" in text_lower or "dem-derived pore reconstructions" in text_lower)
        and (
            "not experimental imaging data" in text_lower
            or "not be interpreted as experimental imaging measurements" in text_lower
            or "not be interpreted as experimental computed-tomography measurements" in text_lower
        )
    )
    has_drag_boundary = all(
        phrase in text_lower
        for phrase in [
            "one-way stokes drag",
            "does not resolve pore-scale gas redistribution",
        ]
    )
    has_drag_scaling_audit = (
        DRAG_SCALING_SUMMARY.exists()
        and DRAG_SCALING_TABLE.exists()
        and "supplementary table~s18" in text_lower
        and "does not replace resolved pore-scale gas-flow calculation" in text_lower
    )
    has_fixed_bed_boundary = "fixed bed" in text_lower and "rearrangement of the large pebbles" in text_lower
    has_fig_boundaries = figure_boundary_complete()
    has_reduced_resistance_boundary = (
        (
            "three-dimensional resistance-amplification test" in text_lower
            or "reduced three-dimensional resistance sensitivity" in text_lower
        )
        and "pressure-calibrated" in text_lower
        and "not openfoam cfd" in read_text(FIGURE_PROVENANCE).lower()
        and RESISTANCE_SENSITIVITY.exists()
    )
    has_localized_boundary = (
        "not a source-position scaling law" in text_lower
        or "not establish a universal clogging transition or source-position law" in text_lower
    )
    admin_open = readiness_summary.get("needs_confirmation", 0)

    rows: list[dict[str, Any]] = [
        {
            "risk_id": "R01",
            "risk": "Pressure-free clogging index could be misread as a pressure-calibrated safety criterion.",
            "severity": "major",
            "status": "bounded" if has_pressure_boundary else "unresolved",
            "reviewer_concern": "Chemical Engineering Science reviewers may ask whether Ib is supported by pressure-drop or CFD data.",
            "current_boundary": "The manuscript states that Ib is a pressure-free structural pre-screening index and that the Ergun result is only a proxy.",
            "evidence_path": rel(LATEX_MAIN),
            "mitigation_action": "Keep the current boundary language; upgrade only after CFD/OpenLB/OpenFOAM or measured pressure-gradient data are added.",
            "submission_decision": "acceptable_for_preclogging_scope" if has_pressure_boundary else "revise_before_submission",
        },
        {
            "risk_id": "R02",
            "risk": "Critical clogging transition is not demonstrated by the current data.",
            "severity": "major",
            "status": "bounded" if has_transition_boundary else "unresolved",
            "reviewer_concern": "A reviewer could reject any claim of a universal transition because connectivity loss is not measurable in the current cases.",
            "current_boundary": "The manuscript frames the result as pre-clogging migration/filtering and states that identifying a bed-scale clogging threshold requires higher loading, localized release, or coupled flow.",
            "evidence_path": rel(LATEX_MAIN),
            "mitigation_action": "Do not claim critical transition in title, abstract, or conclusions unless new localized/high-loading production runs generate connectivity loss or pressure increase.",
            "submission_decision": "acceptable_for_preclogging_scope" if has_transition_boundary else "revise_before_submission",
        },
        {
            "risk_id": "R03",
            "risk": "Loading scan has three single-seed states and cannot support a monotonic law.",
            "severity": "major",
            "status": "bounded" if has_single_seed_boundary else "unresolved",
            "reviewer_concern": "The final BTC values are not monotonic with injected debris count, so reviewers may challenge trend claims.",
            "current_boundary": "The manuscript says the loading data are bounded loading responses rather than a monotonic breakthrough law.",
            "evidence_path": rel(PAPER_DIR / "tables" / "paper2_fig4_loading_summary_source.csv"),
            "mitigation_action": "For a stronger paper, add repeat seeds or reframe the loading scan as a bounded response only.",
            "submission_decision": "acceptable_if_claims_remain_bounded" if has_single_seed_boundary else "revise_before_submission",
        },
        {
            "risk_id": "R04",
            "risk": "Localized internal-release cases may be overread as a source-position or source-strength law.",
            "severity": "major",
            "status": "resolved" if completed_localized >= expected_localized else ("bounded" if has_localized_boundary else "unresolved"),
            "reviewer_concern": "The localized-release evidence now covers the planned target-time rows, but the case family is still too sparse to fit a general source-position or source-strength law.",
            "current_boundary": f"{completed_localized}/{expected_localized} localized-release production jobs reached target physical time; the manuscript treats them as mechanism evidence rather than a fitted source-location law.",
            "evidence_path": rel(LOCALIZED_PRODUCTION),
            "mitigation_action": "Keep localized-release interpretation bounded to retention, downstream leakage and sparse-front decoupling; add more source positions/seeds only if a scaling law is claimed.",
            "submission_decision": "acceptable_with_boundary" if completed_localized < expected_localized and has_localized_boundary else ("strengthen_before_high_level_submission" if completed_localized < expected_localized else "acceptable"),
        },
        {
            "risk_id": "R05",
            "risk": "DEM-derived pore fields could be mistaken for experimental CT validation.",
            "severity": "major",
            "status": "bounded" if has_dem_reconstruction_boundary and avoids_ct_title else "unresolved",
            "reviewer_concern": "The study has no physical CT/PIV experiment, so imaging terminology must be precise.",
            "current_boundary": "The manuscript uses DEM-derived pore reconstruction and explicitly rejects experimental computed-tomography interpretation.",
            "evidence_path": rel(LATEX_MAIN),
            "mitigation_action": "Keep CT out of the title and figure labels; use 'DEM-derived pore reconstruction' or 'voxelized pore field'.",
            "submission_decision": "acceptable_for_numerical_study" if has_dem_reconstruction_boundary and avoids_ct_title else "revise_before_submission",
        },
        {
            "risk_id": "R06",
            "risk": "One-way Stokes drag omits pore-scale gas redistribution and two-way coupling.",
            "severity": "major",
            "status": "bounded" if has_drag_boundary and has_drag_scaling_audit else "unresolved",
            "reviewer_concern": "Reviewers may ask whether drag forcing is physically realistic inside a tortuous packed bed.",
            "current_boundary": "The manuscript states that the forcing is one-way Stokes drag, reports a dimensional drag-scaling audit, and does not solve the local gas field.",
            "evidence_path": f"{rel(LATEX_MAIN)}; {rel(DRAG_SCALING_TABLE)}; {rel(DRAG_SCALING_SUMMARY)}",
            "mitigation_action": "Do not amplify drag nonphysically; use the S18 Reynolds/drag-to-weight audit for scope, and add CFD/OpenLB/OpenFOAM or calibrated pore-flow closure only for resolved gas-flow claims.",
            "submission_decision": "acceptable_as_first_mechanistic_model" if has_drag_boundary and has_drag_scaling_audit else "revise_before_submission",
        },
        {
            "risk_id": "R07",
            "risk": "Large-pebble motion during debris transport would confound deposition interpretation.",
            "severity": "minor",
            "status": "bounded" if has_fixed_bed_boundary else "unresolved",
            "reviewer_concern": "If the skeleton moves, transport differences could reflect bed rearrangement rather than debris migration.",
            "current_boundary": "Formal transport cases use a fixed compacted skeleton so the response is attributed to debris parameters.",
            "evidence_path": rel(LATEX_MAIN),
            "mitigation_action": "Keep this statement in Methods and verify future LIGGGHTS cases freeze type-1 pebbles.",
            "submission_decision": "acceptable" if has_fixed_bed_boundary else "revise_before_submission",
        },
        {
            "risk_id": "R08",
            "risk": "Figure panels could overstate evidence or look like schematic claims rather than data.",
            "severity": "minor",
            "status": "bounded" if has_fig_boundaries else "unresolved",
            "reviewer_concern": "Figures with text-heavy panels, black slices, or unclear provenance weaken a mechanism-first journal submission.",
            "current_boundary": "A figure provenance manifest records source scripts, exports, and claim boundaries for each figure.",
            "evidence_path": rel(FIGURE_PROVENANCE),
            "mitigation_action": "Use the provenance manifest before final figure edits and avoid large in-figure text blocks.",
            "submission_decision": "acceptable_with_final_visual_QA" if has_fig_boundaries else "revise_before_submission",
        },
        {
            "risk_id": "R09",
            "risk": "Title and framing could sound like an experiment or a critical-clogging paper.",
            "severity": "minor",
            "status": "resolved" if avoids_experiment_title and avoids_ct_title and has_transition_boundary else "unresolved",
            "reviewer_concern": "The target journal title should be concise and should not promise unavailable validation or critical transition evidence.",
            "current_boundary": f"The current title is Chemical Engineering Science-oriented and DEM-bounded: {title_text}.",
            "evidence_path": rel(LATEX_MAIN),
            "mitigation_action": "Do not reintroduce experiment, CT, or critical transition wording unless the evidence changes.",
            "submission_decision": "acceptable" if avoids_experiment_title and avoids_ct_title else "revise_before_submission",
        },
        {
            "risk_id": "R10",
            "risk": "Reduced hydraulic sensitivity could be mistaken for resolved CFD pressure evidence.",
            "severity": "major",
            "status": "bounded" if has_reduced_resistance_boundary else "unresolved",
            "reviewer_concern": "Reviewers may ask whether the 3D resistance-amplification result is a calibrated pore-flow or pressure-drop calculation.",
            "current_boundary": "The manuscript and figure provenance identify Fig. S22/Table S15 as a scalar voxel-network sensitivity test, not OpenFOAM CFD, LBM, measured pressure or pressure-calibrated Ib.",
            "evidence_path": rel(RESISTANCE_SENSITIVITY),
            "mitigation_action": "Keep Fig. S22 in the supplement and do not promote it to validation-grade pressure evidence until a coupled flow solver consumes the resistance field.",
            "submission_decision": "acceptable_for_preclogging_scope" if has_reduced_resistance_boundary else "revise_before_submission",
        },
        {
            "risk_id": "R11",
            "risk": "Administrative submission items remain unconfirmed.",
            "severity": "blocker",
            "status": "needs_confirmation" if admin_open else "resolved",
            "reviewer_concern": "Journal submission requires confirmed repository, competing-interest, acknowledgement and corresponding-author metadata.",
            "current_boundary": f"Readiness audit reports {admin_open} needs-confirmation items.",
            "evidence_path": rel(READINESS_JSON),
            "mitigation_action": "Confirm repository DOI/accession, competing interests, acknowledgements and corresponding-author email before submission.",
            "submission_decision": "must_resolve_before_submission" if admin_open else "acceptable",
        },
    ]
    return rows


def write_outputs(rows: list[dict[str, Any]]) -> None:
    """Write the reviewer-risk matrix as JSON and Markdown."""
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    summary = dict(Counter(str(row["status"]) for row in rows))
    payload = {"summary": summary, "rows": rows}
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# Paper 2 Reviewer Risk Matrix",
        "",
        "This matrix records plausible reviewer objections, the current manuscript boundary language, and the required mitigation. It is a submission-risk guide, not a claim that the paper is already accepted or complete.",
        "",
        f"Summary: `{json.dumps(summary, sort_keys=True)}`",
        "",
        "| ID | Severity | Status | Risk | Current Boundary | Mitigation | Submission Decision |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {risk_id} | {severity} | {status} | {risk} | {current_boundary} | {mitigation_action} | {submission_decision} |".format(
                **{key: str(value).replace("\n", " ") for key, value in row.items()}
            )
        )
    lines.extend(
        [
            "",
            "## Immediate Interpretation",
            "",
            "- The manuscript is defensible as a bounded pre-clogging migration/retention paper if the current limitation language is retained.",
            "- It is not yet defensible as a pressure-calibrated critical-clogging-transition paper.",
            "- The localized internal-release target-time rows are complete; the strongest remaining upgrades are mechanism-map polish, broader parameter/seeding evidence and pressure-gradient calibration.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """Run the reviewer-risk audit."""
    rows = build_risk_rows()
    missing = [col for row in rows for col in REQUIRED_COLUMNS if col not in row]
    if missing:
        raise ValueError(f"Risk rows are missing required columns: {sorted(set(missing))}")
    write_outputs(rows)
    print(f"Wrote {rel(OUT_JSON)}")
    print(f"Wrote {rel(OUT_MD)}")
    print(json.dumps(dict(Counter(str(row['status']) for row in rows)), sort_keys=True))


if __name__ == "__main__":
    main()
