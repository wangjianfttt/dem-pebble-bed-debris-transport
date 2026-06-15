#!/usr/bin/env python3
"""Create a copy-ready final metadata completion packet for Paper 2."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
SUBMISSION_DIR = PAPER_DIR / "submission"

FORM_PACKET = SUBMISSION_DIR / "submission_form_packet.json"
METADATA_YAML = SUBMISSION_DIR / "submission_metadata.yaml"
METADATA_GAPS = SUBMISSION_DIR / "submission_metadata_gaps.json"
REPOSITORY_PACKET = SUBMISSION_DIR / "repository_upload_packet.json"
JOURNAL_ARCHIVE = PAPER_DIR / "submission_package" / "archives" / "paper2_journal_submission_files_archive_summary.json"
JOURNAL_ARCHIVE_ZIP = PAPER_DIR / "submission_package" / "archives" / "paper2_journal_submission_files.zip"
DEPOSIT_ARCHIVE = PAPER_DIR / "deposit" / "archives" / "paper2_lightweight_deposit_archive_summary.json"
OUT_JSON = SUBMISSION_DIR / "final_metadata_completion_packet.json"
OUT_MD = SUBMISSION_DIR / "final_metadata_completion_packet.md"


def read_json(path: Path) -> dict[str, Any]:
    """Read a JSON object from disk."""
    if not path.exists():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def read_yaml(path: Path) -> dict[str, Any]:
    """Read a YAML mapping from disk."""
    if not path.exists():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping: {path}")
    return data


def rel(path: Path | str) -> str:
    """Return a path relative to the project root when possible."""
    path_obj = Path(path)
    try:
        return path_obj.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path_obj.as_posix()


def confirmation_row(section: str, metadata: dict[str, Any], gaps: dict[str, Any]) -> dict[str, Any]:
    """Build one section-level confirmation row."""
    section_data = metadata.get(section, {})
    gap_rows = {row.get("section"): row for row in gaps.get("sections", []) if isinstance(row, dict)}
    gap = gap_rows.get(section, {})
    return {
        "section": section,
        "confirmed": bool(section_data.get("confirmed", False)) if isinstance(section_data, dict) else False,
        "current_value": section_data if isinstance(section_data, dict) else {},
        "missing_fields": gap.get("missing_fields", []),
        "required": bool(gap.get("required", False)),
        "why": gap.get("why", ""),
    }


def build_packet() -> dict[str, Any]:
    """Build the final metadata completion packet."""
    form = read_json(FORM_PACKET)
    metadata = read_yaml(METADATA_YAML)
    gaps = read_json(METADATA_GAPS)
    repository = read_json(REPOSITORY_PACKET)
    deposit_archive = read_json(DEPOSIT_ARCHIVE)
    sections = [
        "repository",
        "competing_interests",
        "acknowledgements",
        "corresponding_author",
    ]
    confirmation_rows = [confirmation_row(section, metadata, gaps) for section in sections]
    required_open = [row for row in confirmation_rows if row["required"] and not row["confirmed"]]
    optional_open = [row for row in confirmation_rows if not row["required"] and not row["confirmed"]]
    return {
        "decision": "metadata_completion_required_before_submission",
        "journal": form["journal"],
        "title": form["title"],
        "authors": form["authors"],
        "affiliations": form["affiliations"],
        "required_open_count": len(required_open),
        "optional_open_count": len(optional_open),
        "confirmation_rows": confirmation_rows,
        "copy_ready_fields": {
            "abstract": form["abstract"],
            "keywords": form["keywords"],
            "highlights": form["highlights"],
            "credit_author_statement": form["credit_author_statement"],
            "current_data_availability": form["data_availability"],
            "current_code_availability": form["code_availability"],
            "current_competing_interest_statement": form["declaration_of_competing_interest"],
        },
        "archives": {
            "data_code_deposit": {
                "path": rel(deposit_archive["archive_path"]),
                "size_bytes": deposit_archive["archive_size_bytes"],
                "sha256": deposit_archive["sha256"],
            },
        },
        "journal_submission_archive_tracking": {
            "path": rel(JOURNAL_ARCHIVE_ZIP),
            "summary_path": rel(JOURNAL_ARCHIVE),
            "sha256_source": rel(PAPER_DIR / "submission" / "release_archive_consistency.md"),
            "self_reference_boundary": (
                "The journal-submission archive SHA is intentionally not embedded in this packet, "
                "because the packet itself is staged inside that archive. Use CURRENT_PROJECT_STATUS.md "
                "or release_archive_consistency.md after final archiving for the current journal-package SHA."
            ),
        },
        "repository_upload": {
            "packet": rel(SUBMISSION_DIR / "repository_upload_packet.md"),
            "zenodo_metadata_draft": repository.get("zenodo_metadata_draft_path"),
            "license_options": repository.get("license_options_to_confirm", []),
        },
        "fillable_yaml_patch": {
            "repository": {
                "confirmed": True,
                "name": "<repository record name>",
                "identifier": "<repository DOI/accession>",
                "url": "<repository landing-page URL>",
                "license": "<confirmed license>",
            },
            "competing_interests": {
                "confirmed": True,
                "statement": metadata["competing_interests"]["statement"],
            },
            "acknowledgements": {
                "confirmed": True,
                "statement": "<author-approved acknowledgements and computing-resource wording>",
            },
            "corresponding_author": {
                "confirmed": True,
                "name": "<corresponding author name>",
                "email": "<corresponding author email>",
            },
        },
        "post_confirmation_commands": [
            "python3 papers/paper2_voxel_topology_clogging/scripts/audit_submission_metadata_gaps.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/apply_submission_metadata.py --apply",
            "cd papers/paper2_voxel_topology_clogging/latex && latexmk -pdf -interaction=nonstopmode main.tex",
            "PYTHONPATH=. python3 papers/paper2_voxel_topology_clogging/scripts/audit_paper2_manuscript_readiness.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/audit_final_submission_gate.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/stage_journal_submission_files.py --force",
            "python3 papers/paper2_voxel_topology_clogging/scripts/archive_journal_submission_files.py --force",
        ],
        "boundaries": [
            "Do not claim a public repository DOI/accession until it exists.",
            "Do not call DEM-derived voxel fields experimental CT.",
            "Do not claim pressure-calibrated Ib or a universal critical-clogging transition.",
        ],
    }


def render_markdown(packet: dict[str, Any]) -> str:
    """Render a human-fillable Markdown metadata packet."""
    lines = [
        "# Paper 2 Final Metadata Completion Packet",
        "",
        f"- Decision: `{packet['decision']}`",
        f"- Journal: {packet['journal']}",
        f"- Title: {packet['title']}",
        f"- Required open sections: {packet['required_open_count']}",
        f"- Optional/policy-dependent open sections: {packet['optional_open_count']}",
        "",
        "## Ready Archives",
        "",
        "| Archive | Path | Size bytes | SHA256 |",
        "|---|---|---:|---|",
    ]
    for key, archive in packet["archives"].items():
        lines.append(f"| {key} | `{archive['path']}` | {archive['size_bytes']} | `{archive['sha256']}` |")

    tracking = packet["journal_submission_archive_tracking"]
    lines.extend(
        [
            "",
            "## Journal Submission Archive Tracking",
            "",
            f"- Archive path: `{tracking['path']}`",
            f"- Current SHA source after final archiving: `{tracking['sha256_source']}`",
            f"- Summary JSON: `{tracking['summary_path']}`",
            f"- Boundary: {tracking['self_reference_boundary']}",
        ]
    )

    lines.extend(["", "## Confirmation Checklist", "", "| Section | Required | Confirmed | Missing fields | Why |", "|---|---|---|---|---|"])
    for row in packet["confirmation_rows"]:
        missing = ", ".join(row["missing_fields"]) if row["missing_fields"] else "none"
        lines.append(f"| {row['section']} | `{row['required']}` | `{row['confirmed']}` | {missing} | {row['why']} |")

    lines.extend(["", "## Fill This YAML Into submission_metadata.yaml", "", "```yaml"])
    lines.append(yaml.safe_dump(packet["fillable_yaml_patch"], sort_keys=False, allow_unicode=True).strip())
    lines.extend(["```", "", "## Repository Upload", ""])
    lines.append(f"- Upload packet: `{packet['repository_upload']['packet']}`")
    lines.append(f"- Zenodo metadata draft: `{packet['repository_upload']['zenodo_metadata_draft']}`")
    lines.append("")
    lines.append("License options to confirm:")
    for option in packet["repository_upload"]["license_options"]:
        lines.append(f"- {option}")

    lines.extend(["", "## Copy-Ready Journal Fields", ""])
    lines.append("### Keywords")
    lines.extend(f"- {keyword}" for keyword in packet["copy_ready_fields"]["keywords"])
    lines.extend(["", "### Highlights"])
    lines.extend(f"- {highlight}" for highlight in packet["copy_ready_fields"]["highlights"])
    lines.extend(["", "### CRediT Statement", "", packet["copy_ready_fields"]["credit_author_statement"]])
    lines.extend(["", "### Current Data Availability Wording", "", packet["copy_ready_fields"]["current_data_availability"]])
    lines.extend(["", "### Current Code Availability Wording", "", packet["copy_ready_fields"]["current_code_availability"]])
    lines.extend(["", "### Current Competing-Interest Wording", "", packet["copy_ready_fields"]["current_competing_interest_statement"]])

    lines.extend(["", "## Post-Confirmation Commands", "", "```bash"])
    lines.extend(packet["post_confirmation_commands"])
    lines.extend(["```", "", "## Boundaries", ""])
    for boundary in packet["boundaries"]:
        lines.append(f"- {boundary}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(out_json: Path = OUT_JSON, out_md: Path = OUT_MD) -> dict[str, Any]:
    """Write JSON and Markdown metadata completion packets."""
    packet = build_packet()
    out_json.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    out_md.write_text(render_markdown(packet), encoding="utf-8")
    return packet


def main() -> int:
    """CLI entry point."""
    packet = write_outputs()
    print(json.dumps({"decision": packet["decision"], "required_open_count": packet["required_open_count"]}, indent=2))
    print(OUT_JSON)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
