#!/usr/bin/env python3
"""Create the final action list for submitting Paper 2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
FINAL_GATE = PAPER_DIR / "submission" / "final_submission_gate.json"
METADATA_GAPS = PAPER_DIR / "submission" / "submission_metadata_gaps.json"
OUT_JSON = PAPER_DIR / "submission" / "final_submission_action_list.json"
OUT_MD = PAPER_DIR / "submission" / "final_submission_action_list.md"

SECTION_TO_BLOCKER = {
    "repository": "public_repository_doi",
    "competing_interests": "competing_interest_confirmation",
    "acknowledgements": "acknowledgement_confirmation",
    "corresponding_author": "corresponding_author_confirmation",
}

OWNERS = {
    "repository": "corresponding author or data manager",
    "competing_interests": "all authors",
    "acknowledgements": "corresponding author",
    "corresponding_author": "corresponding author",
}

OUTPUT_FIELDS = {
    "repository": "repository name, DOI/accession, URL and license in submission_metadata.yaml",
    "competing_interests": "author-confirmed competing-interest statement",
    "acknowledgements": "approved acknowledgement and computing-resource wording",
    "corresponding_author": "name and email for the journal submission system",
}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-json", type=Path, default=OUT_JSON, help="Output JSON action list.")
    parser.add_argument("--out-md", type=Path, default=OUT_MD, help="Output Markdown action list.")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, object]:
    """Load a JSON object from disk."""
    if not path.exists():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def rel(path: Path) -> str:
    """Return a project-relative path."""
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def build_actions(gate: dict[str, object], gaps: dict[str, object]) -> list[dict[str, object]]:
    """Build required and optional final submission actions."""
    admin_by_item = {str(item["item"]): item for item in gate.get("admin_blockers", [])}
    actions: list[dict[str, object]] = []

    for section in gaps.get("sections", []):
        section_name = str(section["section"])
        required = bool(section["required"])
        blocker_item = SECTION_TO_BLOCKER.get(section_name, "policy_dependent")
        admin = admin_by_item.get(blocker_item)
        action_text = str(admin["action"]) if admin else str(section["why"])
        commands = [
            "python3 papers/paper2_voxel_topology_clogging/scripts/audit_submission_metadata_gaps.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/apply_submission_metadata.py --apply",
            "cd papers/paper2_voxel_topology_clogging/latex && pdflatex -interaction=nonstopmode main.tex && bibtex main && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex",
            "python3 papers/paper2_voxel_topology_clogging/scripts/audit_final_submission_gate.py",
        ]
        actions.append(
            {
                "action_id": f"A{len(actions) + 1:02d}_{section_name}",
                "section": section_name,
                "required": required,
                "status": section["status"],
                "owner": OWNERS.get(section_name, "corresponding author"),
                "blocker_item": blocker_item if required else None,
                "missing_fields": section["missing_fields"],
                "why": section["why"],
                "action": action_text,
                "required_output": OUTPUT_FIELDS.get(section_name, "confirmed metadata"),
                "write_to": rel(PAPER_DIR / "submission" / "submission_metadata.yaml"),
                "verification_commands": commands if required else commands[:1],
            }
        )
    return actions


def build_report() -> dict[str, object]:
    """Build the final submission action-list report."""
    gate = load_json(FINAL_GATE)
    gaps = load_json(METADATA_GAPS)
    actions = build_actions(gate, gaps)
    high_impact_actions = gate.get("high_impact_pending_scientific_actions", [])
    if not isinstance(high_impact_actions, list):
        high_impact_actions = []
    required_open = [item["action_id"] for item in actions if item["required"] and item["status"] != "complete"]
    optional_open = [item["action_id"] for item in actions if not item["required"] and item["status"] != "complete"]
    return {
        "decision": "ready_to_submit" if not required_open and gate["gate_status"] != "not_ready_for_submission" else "admin_actions_required",
        "gate_status": gate["gate_status"],
        "required_open_count": len(required_open),
        "optional_open_count": len(optional_open),
        "high_impact_pending_count": len(high_impact_actions),
        "required_open_actions": required_open,
        "optional_open_actions": optional_open,
        "high_impact_pending_scientific_actions": high_impact_actions,
        "missing_upload_files": gate["missing_upload_files"],
        "journal_submission_archive": gate["upload_files"]["journal_submission_archive"]["path"],
        "data_code_archive": gate["upload_files"]["data_code_archive"]["path"],
        "actions": actions,
        "final_verification_commands": [
            "python3 papers/paper2_voxel_topology_clogging/scripts/audit_submission_metadata_gaps.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/apply_submission_metadata.py --apply",
            "cd papers/paper2_voxel_topology_clogging/latex && pdflatex -interaction=nonstopmode main.tex && bibtex main && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex",
            "PYTHONPATH=. python3 papers/paper2_voxel_topology_clogging/scripts/audit_paper2_manuscript_readiness.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/audit_final_submission_gate.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/stage_journal_submission_files.py --force",
            "python3 papers/paper2_voxel_topology_clogging/scripts/archive_journal_submission_files.py --force",
        ],
        "boundary": "Administrative action list only; it does not change scientific evidence or manuscript scope.",
    }


def write_markdown(report: dict[str, object], out_md: Path) -> None:
    """Write the action list as Markdown."""
    lines = [
        "# Paper 2 Final Submission Action List",
        "",
        f"- Decision: `{report['decision']}`",
        f"- Gate status: `{report['gate_status']}`",
        f"- Required open actions: {report['required_open_count']}",
        f"- Optional open actions: {report['optional_open_count']}",
        f"- High-impact scientific actions pending: {report['high_impact_pending_count']}",
        f"- Missing upload files: `{report['missing_upload_files']}`",
        f"- Journal submission archive: `{report['journal_submission_archive']}`",
        f"- Data/code archive: `{report['data_code_archive']}`",
        "",
        "## Required Actions",
        "",
        "| ID | Section | Owner | Missing fields | Required output |",
        "|---|---|---|---|---|",
    ]
    for item in report["actions"]:
        if not item["required"]:
            continue
        missing = ", ".join(item["missing_fields"]) if item["missing_fields"] else "confirmation"
        lines.append(f"| {item['action_id']} | {item['section']} | {item['owner']} | {missing} | {item['required_output']} |")

    lines.extend(["", "## Optional Or Policy-Dependent Actions", "", "| ID | Section | Owner | Missing fields | Required output |", "|---|---|---|---|---|"])
    for item in report["actions"]:
        if item["required"]:
            continue
        missing = ", ".join(item["missing_fields"]) if item["missing_fields"] else "confirmation"
        lines.append(f"| {item['action_id']} | {item['section']} | {item['owner']} | {missing} | {item['required_output']} |")

    lines.extend(
        [
            "",
            "## High-Impact Scientific Actions",
            "",
            "| Item | Status | Progress | Action |",
            "|---|---|---:|---|",
        ]
    )
    for item in report["high_impact_pending_scientific_actions"]:
        progress = item.get("progress_fraction")
        progress_text = f"{float(progress):.3f}" if isinstance(progress, (int, float)) else "unknown"
        lines.append(f"| {item['item']} | {item['status']} | {progress_text} | {item['action']} |")
    if not report["high_impact_pending_scientific_actions"]:
        lines.append("| none | none | n/a | none |")

    lines.extend(["", "## Exact Final Verification Commands", "", "```bash"])
    lines.extend(report["final_verification_commands"])
    lines.extend(
        [
            "```",
            "",
            "## Submission Boundary",
            "",
            "- Submit only after all required actions are complete and the final gate changes from `not_ready_for_submission`.",
            "- Keep the manuscript bounded to DEM-based pre-clogging migration/filtering.",
            "- Do not add pressure-calibrated safety-limit language unless new pressure evidence is actually available.",
            "- Do not describe DEM-derived pore reconstructions as experimental CT.",
            "",
            f"Boundary: {report['boundary']}",
        ]
    )
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(out_json: Path = OUT_JSON, out_md: Path = OUT_MD) -> dict[str, object]:
    """Write JSON and Markdown action-list outputs."""
    report = build_report()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(report, out_md)
    return report


def main() -> int:
    """Run final submission action-list generation."""
    args = parse_args()
    report = write_outputs(args.out_json, args.out_md)
    print(
        json.dumps(
            {
                "decision": report["decision"],
                "gate_status": report["gate_status"],
            "required_open_count": report["required_open_count"],
            "optional_open_count": report["optional_open_count"],
            "high_impact_pending_count": report["high_impact_pending_count"],
        },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
