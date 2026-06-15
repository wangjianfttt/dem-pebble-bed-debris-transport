#!/usr/bin/env python3
"""Create an Elsevier Editorial Manager entry checklist for Paper 2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
DEFAULT_FORM = PAPER_DIR / "submission" / "submission_form_packet.json"
DEFAULT_ACTIONS = PAPER_DIR / "submission" / "final_submission_action_list.json"
DEFAULT_GATE = PAPER_DIR / "submission" / "final_submission_gate.json"
DEFAULT_MANIFEST = PAPER_DIR / "submission_package" / "journal_submission_files" / "MANIFEST.json"
DEFAULT_JSON = PAPER_DIR / "submission" / "elsevier_portal_checklist.json"
DEFAULT_MD = PAPER_DIR / "submission" / "elsevier_portal_checklist.md"


REQUIRED_UPLOADS = [
    "manuscript/main.pdf",
    "manuscript/main.tex",
    "manuscript/paper2_references.bib",
    "manuscript/highlights.md",
    "main_figures/paper2_fig1_voxel_topology_framework.pdf",
    "main_figures/paper2_fig2_baseline_voxel_topology.pdf",
    "main_figures/paper2_fig3_representative_debris_blockage.pdf",
    "main_figures/paper2_908_spatial_distribution_evidence.pdf",
    "main_figures/paper2_fig4_loading_clogging_response.pdf",
    "main_figures/paper2_graphical_abstract.png",
    "main_figures/paper2_graphical_abstract.pdf",
    "main_figures/paper2_graphical_abstract.svg",
    "supplementary_material/supplementary/supplementary_tables.md",
    "supplementary_material/supplementary/supplementary_figures.md",
    "cover_and_declarations/cover_letter_draft.md",
    "cover_and_declarations/claim_boundary_statement.md",
    "cover_and_declarations/reviewer_precheck.md",
    "cover_and_declarations/editor_response_map.md",
    "cover_and_declarations/final_submission_action_list.md",
    "cover_and_declarations/repository_upload_packet.md",
    "cover_and_declarations/submission_form_packet.md",
    "cover_and_declarations/repository_deposit/repository_metadata.yaml",
    "cover_and_declarations/repository_deposit/CITATION.cff",
]


PORTAL_BOUNDARIES = [
    "Do not claim experimental CT; use DEM-derived voxel or pore reconstruction wording.",
    "Do not claim pressure-calibrated safety limits unless returned flow-solver or experimental pressure evidence is inserted.",
    "Do not claim a public repository DOI/accession until the repository record exists.",
]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--form", type=Path, default=DEFAULT_FORM, help="Submission form packet JSON.")
    parser.add_argument("--actions", type=Path, default=DEFAULT_ACTIONS, help="Final action list JSON.")
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE, help="Final submission gate JSON.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Staged journal submission MANIFEST.json.")
    parser.add_argument("--out-json", type=Path, default=DEFAULT_JSON, help="Output checklist JSON.")
    parser.add_argument("--out-md", type=Path, default=DEFAULT_MD, help="Output checklist Markdown.")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    """Load a required JSON object."""
    if not path.exists():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def word_count(text: str) -> int:
    """Return a simple whitespace-based word count."""
    return len([token for token in text.split() if token.strip()])


def manifest_paths(manifest: dict[str, Any]) -> set[str]:
    """Return the set of staged file paths from a journal-submission manifest."""
    files = manifest.get("files", [])
    if not isinstance(files, list):
        raise ValueError("Manifest field 'files' must be a list")
    return {str(row["path"]) for row in files if isinstance(row, dict) and "path" in row}


def upload_item(path: str, staged: set[str]) -> dict[str, Any]:
    """Build one upload item from a staged path."""
    return {"path": path, "present": path in staged}


def classify_decision(required_open: int, missing_uploads: list[str], gate_status: str) -> str:
    """Classify current portal readiness from administrative and upload checks."""
    if missing_uploads:
        return "portal_blocked_missing_uploads"
    if required_open:
        return "portal_ready_after_admin_metadata"
    if gate_status in {"ready_for_submission", "ready_for_bounded_submission"}:
        return "portal_ready_to_submit"
    return "portal_needs_final_gate_refresh"


def build_checklist(form_path: Path, actions_path: Path, gate_path: Path, manifest_path: Path) -> dict[str, Any]:
    """Build the Elsevier portal checklist from existing submission packets."""
    form = load_json(form_path)
    actions = load_json(actions_path)
    gate = load_json(gate_path)
    manifest = load_json(manifest_path)
    staged = manifest_paths(manifest)
    upload_items = [upload_item(path, staged) for path in REQUIRED_UPLOADS]
    missing_uploads = [item["path"] for item in upload_items if not item["present"]]
    required_open_count = int(actions.get("required_open_count", 0))
    optional_open_count = int(actions.get("optional_open_count", 0))
    decision = classify_decision(required_open_count, missing_uploads, str(gate.get("gate_status", "")))

    portal_sections = [
        {
            "section": "Manuscript metadata",
            "status": "copy_ready",
            "items": {
                "journal": form["journal"],
                "article_type": "Research article",
                "title": form["title"],
                "abstract_word_count": word_count(form["abstract"]),
                "keyword_count": len(form["keywords"]),
                "highlight_count": len(form["highlights"]),
                "author_count": len(form["authors"]),
                "affiliation_count": len(form["affiliations"]),
            },
        },
        {
            "section": "Copy-ready text fields",
            "status": "copy_ready_with_admin_placeholders",
            "items": {
                "abstract": form["abstract"],
                "keywords": form["keywords"],
                "highlights": form["highlights"],
                "data_availability": form["data_availability"],
                "code_availability": form["code_availability"],
                "credit_author_statement": form["credit_author_statement"],
                "declaration_of_competing_interest": form["declaration_of_competing_interest"],
                "acknowledgements": form["acknowledgements"],
            },
        },
        {
            "section": "Upload files",
            "status": "ready" if not missing_uploads else "missing_files",
            "items": upload_items,
        },
        {
            "section": "Administrative blockers",
            "status": "open" if required_open_count else "cleared",
            "items": actions.get("actions", []),
        },
    ]

    return {
        "decision": decision,
        "journal": form["journal"],
        "title": form["title"],
        "gate_status": gate.get("gate_status"),
        "required_open_count": required_open_count,
        "optional_open_count": optional_open_count,
        "required_open_actions": actions.get("required_open_actions", []),
        "optional_open_actions": actions.get("optional_open_actions", []),
        "missing_upload_files": sorted(set(missing_uploads + list(actions.get("missing_upload_files", [])))),
        "manifest_file_count": manifest.get("file_count"),
        "portal_sections": portal_sections,
        "upload_items": upload_items,
        "copy_ready_fields": portal_sections[1]["items"],
        "boundaries": PORTAL_BOUNDARIES,
        "next_action": (
            "Confirm repository DOI/accession, competing-interest, acknowledgement and corresponding-author metadata, "
            "then rerun the submission gate before pressing submit."
        ),
    }


def checkbox(done: bool) -> str:
    """Return a Markdown checkbox marker."""
    return "[x]" if done else "[ ]"


def write_markdown(checklist: dict[str, Any], out_path: Path) -> None:
    """Write a human-readable portal checklist."""
    metadata = checklist["portal_sections"][0]["items"]
    fields = checklist["copy_ready_fields"]
    lines = [
        "# Elsevier Portal Checklist",
        "",
        "This checklist converts the current Paper 2 package into journal-portal actions. It is not an author approval record.",
        "",
        "## Readiness",
        "",
        f"- Decision: `{checklist['decision']}`",
        f"- Gate status: `{checklist['gate_status']}`",
        f"- Required open actions: {checklist['required_open_count']}",
        f"- Optional open actions: {checklist['optional_open_count']}",
        f"- Missing upload files: `{checklist['missing_upload_files']}`",
        "",
        "## Manuscript Metadata",
        "",
        f"- Journal: {metadata['journal']}",
        f"- Article type: {metadata['article_type']}",
        f"- Title: {metadata['title']}",
        f"- Authors: {metadata['author_count']}",
        f"- Affiliations: {metadata['affiliation_count']}",
        f"- Abstract words: {metadata['abstract_word_count']}",
        f"- Keywords: {metadata['keyword_count']}",
        f"- Highlights: {metadata['highlight_count']}",
        "",
        "## Copy-Ready Text",
        "",
        "### Abstract",
        "",
        fields["abstract"],
        "",
        "### Keywords",
        "",
    ]
    for keyword in fields["keywords"]:
        lines.append(f"- {keyword}")
    lines.extend(["", "### Highlights", ""])
    for highlight in fields["highlights"]:
        lines.append(f"- {highlight}")
    for key, heading in [
        ("data_availability", "Data Availability"),
        ("code_availability", "Code Availability"),
        ("credit_author_statement", "CRediT Author Statement"),
        ("declaration_of_competing_interest", "Declaration Of Competing Interest"),
        ("acknowledgements", "Acknowledgements"),
    ]:
        lines.extend(["", f"### {heading}", "", fields[key]])

    lines.extend(["", "## Upload Checklist", ""])
    for item in checklist["upload_items"]:
        lines.append(f"- {checkbox(bool(item['present']))} `{item['path']}`")

    lines.extend(["", "## Required Administrative Actions", ""])
    for action in checklist["portal_sections"][3]["items"]:
        if action.get("required"):
            lines.append(f"- [ ] `{action['action_id']}`: {action['action']}")
    lines.extend(["", "## Optional Administrative Actions", ""])
    for action in checklist["portal_sections"][3]["items"]:
        if not action.get("required"):
            lines.append(f"- [ ] `{action['action_id']}`: {action['action']}")

    lines.extend(["", "## Boundary Phrases", ""])
    for boundary in checklist["boundaries"]:
        lines.append(f"- {boundary}")
    lines.extend(["", "## Next Action", "", checklist["next_action"]])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(out_json: Path = DEFAULT_JSON, out_md: Path = DEFAULT_MD) -> dict[str, Any]:
    """Write JSON and Markdown checklist outputs."""
    checklist = build_checklist(DEFAULT_FORM, DEFAULT_ACTIONS, DEFAULT_GATE, DEFAULT_MANIFEST)
    out_json.write_text(json.dumps(checklist, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(checklist, out_md)
    return checklist


def main() -> int:
    """Run the checklist generator."""
    args = parse_args()
    checklist = build_checklist(args.form, args.actions, args.gate, args.manifest)
    args.out_json.write_text(json.dumps(checklist, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(checklist, args.out_md)
    print(json.dumps({"decision": checklist["decision"], "required_open_count": checklist["required_open_count"], "missing_upload_files": checklist["missing_upload_files"]}, indent=2))
    print(args.out_json)
    print(args.out_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
