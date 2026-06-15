#!/usr/bin/env python3
"""Build the final pre-submission gate report for Paper 2."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
READINESS_JSON = PAPER_DIR / "data" / "paper2_manuscript_readiness.json"
RISK_JSON = PAPER_DIR / "data" / "reviewer_risk_matrix.json"
REPEAT_STATUS_JSON = PAPER_DIR / "data" / "paper2_near_threshold_repeat_run_status.json"
METADATA_GAPS_JSON = PAPER_DIR / "submission" / "submission_metadata_gaps.json"
OUT_JSON = PAPER_DIR / "submission" / "final_submission_gate.json"
OUT_MD = PAPER_DIR / "submission" / "final_submission_gate.md"

REQUIRED_UPLOAD_FILES = {
    "journal_submission_archive": PAPER_DIR / "submission_package" / "archives" / "paper2_journal_submission_files.zip",
    "journal_submission_archive_sha256": PAPER_DIR / "submission_package" / "archives" / "paper2_journal_submission_files.zip.sha256",
    "journal_submission_archive_summary": PAPER_DIR / "submission_package" / "archives" / "paper2_journal_submission_files_archive_summary.json",
    "journal_submission_manifest": PAPER_DIR / "submission_package" / "journal_submission_files" / "MANIFEST.json",
    "journal_submission_readme": PAPER_DIR / "submission_package" / "journal_submission_files" / "README.md",
    "data_code_archive": PAPER_DIR / "deposit" / "archives" / "paper2_lightweight_deposit.zip",
    "data_code_archive_sha256": PAPER_DIR / "deposit" / "archives" / "paper2_lightweight_deposit.zip.sha256",
    "data_code_archive_summary": PAPER_DIR / "deposit" / "archives" / "paper2_lightweight_deposit_archive_summary.json",
}

ADMIN_ITEMS = {
    "public_repository_doi": "Upload the data/code archive and insert DOI/accession into Data and Code availability.",
    "competing_interest_confirmation": "Confirm competing-interest statement with all authors.",
    "acknowledgement_confirmation": "Confirm computing-resource, collaborator and institutional acknowledgement wording.",
    "corresponding_author_confirmation": "Confirm corresponding-author name and email for the journal submission system.",
}

METADATA_SECTION_ACTIONS = {
    "repository": "Upload the data/code archive or confirm repository name, DOI/accession, URL and license.",
    "competing_interests": "Confirm the competing-interest statement with all authors.",
    "acknowledgements": "Confirm acknowledgements, computing-resource and collaborator wording.",
    "corresponding_author": "Confirm corresponding-author name and email for the journal submission system.",
}


def load_json(path: Path) -> object:
    """Load a JSON file with a clear error when missing."""
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path) -> str:
    """Return a project-relative path string."""
    return str(path.relative_to(PROJECT_ROOT))


def count_status(rows: list[dict[str, object]]) -> dict[str, int]:
    """Count status values in a list of audit rows."""
    return dict(Counter(str(row["status"]) for row in rows))


def build_gate() -> dict[str, object]:
    """Build the final pre-submission gate object."""
    readiness = load_json(READINESS_JSON)
    risk_data = load_json(RISK_JSON)
    repeat_status = load_json(REPEAT_STATUS_JSON) if REPEAT_STATUS_JSON.exists() else {}
    metadata_gaps = load_json(METADATA_GAPS_JSON) if METADATA_GAPS_JSON.exists() else {}
    risks = risk_data.get("rows", risk_data) if isinstance(risk_data, dict) else risk_data
    readiness_counts = count_status(readiness)
    risk_counts = count_status(risks)
    repeat_summary = repeat_status.get("summary", {}) if isinstance(repeat_status, dict) else {}

    upload_files = {
        name: {"path": rel(path), "exists": path.exists(), "size_bytes": path.stat().st_size if path.exists() else 0}
        for name, path in REQUIRED_UPLOAD_FILES.items()
    }
    needs_confirmation = [row for row in readiness if row["status"] == "needs_confirmation"]
    not_supported = [row for row in readiness if row["status"] == "not_supported_current_scope"]
    unresolved_risks = [row for row in risks if row["status"] == "unresolved"]
    blocker_risks = [row for row in risks if row["severity"] == "blocker" and row["status"] != "resolved"]

    readiness_admin_blockers = [
        {
            "item": row["item"],
            "action": ADMIN_ITEMS.get(str(row["item"]), "Confirm this item before submission."),
            "evidence": row["evidence"],
        }
        for row in needs_confirmation
    ]
    metadata_admin_blockers = []
    if isinstance(metadata_gaps, dict):
        for row in metadata_gaps.get("sections", []):
            if row.get("status") != "open":
                continue
            missing = ", ".join(row.get("missing_fields", [])) or "confirmation"
            section = str(row.get("section"))
            metadata_admin_blockers.append(
                {
                    "item": f"metadata_{section}",
                    "action": f"{METADATA_SECTION_ACTIONS.get(section, 'Confirm required submission metadata.')} Missing: {missing}.",
                    "evidence": rel(METADATA_GAPS_JSON),
                }
            )
    admin_blockers = metadata_admin_blockers or readiness_admin_blockers
    scientific_scope_warnings = [
        {
            "item": row["item"],
            "status": row["status"],
            "evidence": row["evidence"],
            "gate_interpretation": "acceptable only if manuscript remains bounded to pre-clogging migration/retention scope",
        }
        for row in not_supported
    ]

    missing_upload_files = [name for name, info in upload_files.items() if not info["exists"]]
    high_impact_pending_scientific_actions = []
    if repeat_summary and repeat_summary.get("decision") != "production_repeat_runs_completed":
        high_impact_pending_scientific_actions.append(
            {
                "item": "repeat_seed_completion",
                "status": repeat_summary.get("decision", "unknown"),
                "evidence": rel(REPEAT_STATUS_JSON),
                "progress_fraction": repeat_summary.get("mean_progress_fraction"),
                "completed_count": repeat_summary.get("completed_count"),
                "case_count": repeat_summary.get("case_count"),
                "action": "Wait for both repeat production runs to complete, then rerun the protected repeat-completion pipeline without --force.",
                "gate_interpretation": "not an administrative submission blocker for the bounded manuscript, but a high-impact evidence upgrade before targeting a stronger journal route",
            }
        )
    gate_status = "not_ready_for_submission"
    if not admin_blockers and not missing_upload_files and not blocker_risks:
        gate_status = "ready_for_bounded_submission"

    if gate_status == "not_ready_for_submission":
        if high_impact_pending_scientific_actions:
            decision = (
                "Files are staged and evidence is internally consistent, but author/repository confirmations remain before journal submission. "
                "Repeat-seed production is still tracked as a high-impact evidence upgrade until completed."
            )
        else:
            decision = (
                "Files are staged and repeat-seed production has completed, but author/repository confirmations remain before journal submission."
            )
    else:
        decision = "Ready for bounded pre-clogging migration/retention submission."

    return {
        "gate_status": gate_status,
        "decision": decision,
        "readiness_counts": readiness_counts,
        "reviewer_risk_counts": risk_counts,
        "metadata_gap_counts": {
            "required_open": metadata_gaps.get("required_open", 0) if isinstance(metadata_gaps, dict) else 0,
            "optional_open": metadata_gaps.get("optional_open", 0) if isinstance(metadata_gaps, dict) else 0,
        },
        "upload_files": upload_files,
        "missing_upload_files": missing_upload_files,
        "admin_blockers": admin_blockers,
        "scientific_scope_warnings": scientific_scope_warnings,
        "high_impact_pending_scientific_actions": high_impact_pending_scientific_actions,
        "unresolved_reviewer_risks": [
            {"risk_id": row["risk_id"], "risk": row["risk"], "mitigation_action": row["mitigation_action"]}
            for row in unresolved_risks
        ],
        "blocker_reviewer_risks": [
            {"risk_id": row["risk_id"], "risk": row["risk"], "mitigation_action": row["mitigation_action"]}
            for row in blocker_risks
        ],
    }


def write_markdown(gate: dict[str, object]) -> None:
    """Write a human-readable pre-submission gate report."""
    lines = [
        "# Paper 2 Final Submission Gate",
        "",
        f"Gate status: `{gate['gate_status']}`",
        "",
        str(gate["decision"]),
        "",
        "## Audit Summary",
        "",
        f"- Manuscript readiness: `{json.dumps(gate['readiness_counts'], sort_keys=True)}`",
        f"- Reviewer risks: `{json.dumps(gate['reviewer_risk_counts'], sort_keys=True)}`",
        f"- Submission metadata gaps: `{json.dumps(gate['metadata_gap_counts'], sort_keys=True)}`",
        "",
        "## Upload-Ready Files",
        "",
        "| Item | Exists | Size | Path |",
        "|---|---:|---:|---|",
    ]
    for name, info in gate["upload_files"].items():
        lines.append(f"| {name} | {info['exists']} | {info['size_bytes']} | `{info['path']}` |")

    lines.extend(["", "## Required Before Submission", "", "| Item | Action | Evidence |", "|---|---|---|"])
    for blocker in gate["admin_blockers"]:
        lines.append(f"| {blocker['item']} | {blocker['action']} | `{blocker['evidence']}` |")
    if not gate["admin_blockers"]:
        lines.append("| none | none | none |")

    lines.extend(["", "## Scientific Scope Warnings", "", "| Item | Status | Interpretation | Evidence |", "|---|---|---|---|"])
    for warning in gate["scientific_scope_warnings"]:
        lines.append(
            f"| {warning['item']} | {warning['status']} | {warning['gate_interpretation']} | `{warning['evidence']}` |"
        )
    if not gate["scientific_scope_warnings"]:
        lines.append("| none | none | none | none |")

    lines.extend(
        [
            "",
            "## High-Impact Scientific Actions",
            "",
            "| Item | Status | Progress | Action | Interpretation |",
            "|---|---|---:|---|---|",
        ]
    )
    for item in gate["high_impact_pending_scientific_actions"]:
        progress = item.get("progress_fraction")
        progress_text = f"{float(progress):.3f}" if isinstance(progress, (int, float)) else "unknown"
        lines.append(
            f"| {item['item']} | {item['status']} | {progress_text} | {item['action']} | {item['gate_interpretation']} |"
        )
    if not gate["high_impact_pending_scientific_actions"]:
        lines.append("| none | none | n/a | none | none |")

    lines.extend(["", "## Unresolved Reviewer Risks", "", "| Risk | Mitigation |", "|---|---|"])
    for risk in gate["unresolved_reviewer_risks"]:
        lines.append(f"| {risk['risk_id']}: {risk['risk']} | {risk['mitigation_action']} |")
    if not gate["unresolved_reviewer_risks"]:
        lines.append("| none | none |")

    lines.extend(
        [
            "",
            "## Practical Decision",
            "",
            "- The manuscript files and public data/code archive are prepared.",
            "- The paper should be submitted only as a bounded DEM-based pre-clogging migration/retention study.",
            "- Do not submit as a pressure-calibrated critical-clogging or safety-limit paper.",
            "- Final submission still requires author/repository confirmations listed above.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    """Run the final submission gate audit."""
    gate = build_gate()
    OUT_JSON.write_text(json.dumps(gate, indent=2), encoding="utf-8")
    write_markdown(gate)
    print(json.dumps({"gate_status": gate["gate_status"], "admin_blockers": len(gate["admin_blockers"]), "missing_upload_files": gate["missing_upload_files"]}, indent=2))
    print(OUT_JSON)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
