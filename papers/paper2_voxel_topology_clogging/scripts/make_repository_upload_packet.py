#!/usr/bin/env python3
"""Create a repository-upload packet for the Paper 2 data/code archive."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
REPOSITORY_METADATA = PAPER_DIR / "submission" / "repository_deposit" / "repository_metadata.yaml"
CITATION = PAPER_DIR / "submission" / "repository_deposit" / "CITATION.cff"
UPLOAD_INSTRUCTIONS = PAPER_DIR / "submission" / "repository_deposit" / "UPLOAD_INSTRUCTIONS.md"
ZENODO_DRAFT = PAPER_DIR / "submission" / "repository_deposit" / "zenodo_metadata_draft.json"
DEPOSIT_ARCHIVE_SUMMARY = PAPER_DIR / "deposit" / "archives" / "paper2_lightweight_deposit_archive_summary.json"
FINAL_ACTION_LIST = PAPER_DIR / "submission" / "final_submission_action_list.json"
OUT_JSON = PAPER_DIR / "submission" / "repository_upload_packet.json"
OUT_MD = PAPER_DIR / "submission" / "repository_upload_packet.md"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-json", type=Path, default=OUT_JSON, help="Output JSON upload packet.")
    parser.add_argument("--out-md", type=Path, default=OUT_MD, help="Output Markdown upload packet.")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object."""
    if not path.exists():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML mapping."""
    if not path.exists():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping: {path}")
    return data


def rel(path: Path | str) -> str:
    """Return a project-relative path string when possible."""
    path_obj = Path(path)
    try:
        return path_obj.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path_obj.as_posix()


def build_packet() -> dict[str, Any]:
    """Build the repository upload packet."""
    metadata = load_yaml(REPOSITORY_METADATA)
    archive = load_json(DEPOSIT_ARCHIVE_SUMMARY)
    action_list = load_json(FINAL_ACTION_LIST)
    upload_files = [
        {
            "role": "data_code_archive",
            "path": rel(archive["archive_path"]),
            "sha256": archive["sha256"],
            "size_bytes": archive["archive_size_bytes"],
        },
        {
            "role": "data_code_archive_sha256",
            "path": rel(archive["sha256_path"]),
            "sha256": None,
            "size_bytes": Path(archive["sha256_path"]).stat().st_size if Path(archive["sha256_path"]).exists() else 0,
        },
    ]
    zenodo_metadata = {
        "title": metadata["title"],
        "upload_type": metadata.get("upload_type", "dataset"),
        "publication_type": metadata.get("publication_type", "article"),
        "creators": metadata.get("creators", []),
        "description": metadata.get("description", ""),
        "keywords": metadata.get("keywords", []),
        "license": metadata.get("license", "TBC"),
        "related_identifiers": metadata.get("related_identifiers", {}),
        "notes": metadata.get("notes", {}),
        "access_right": "open",
    }
    repository_doi = str(metadata.get("related_identifiers", {}).get("repository_doi", "")).strip()
    repository_doi_assigned = bool(repository_doi and repository_doi.upper() not in {"TBC", "TBD", "NA", "N/A"})
    boundary = (
        "Repository DOI/accession has been assigned and inserted into the repository metadata."
        if repository_doi_assigned
        else "Upload packet only; DOI/accession is not assigned until the repository record is actually created."
    )
    return {
        "decision": "ready_for_repository_upload_packet",
        "repository_doi_assigned": repository_doi_assigned,
        "upload_files": upload_files,
        "metadata_source": rel(REPOSITORY_METADATA),
        "citation_source": rel(CITATION),
        "upload_instructions": rel(UPLOAD_INSTRUCTIONS),
        "zenodo_metadata_draft_path": rel(ZENODO_DRAFT),
        "zenodo_metadata_draft": zenodo_metadata,
        "license_options_to_confirm": [
            "CC-BY-4.0 for data/figures if authors want a permissive attribution data license",
            "MIT or BSD-3-Clause for reusable code if a separate software license is desired",
            "A single repository-level license chosen by the corresponding author or institution",
        ],
        "fields_to_confirm_after_upload": [
            "repository.name",
            "repository.identifier",
            "repository.url",
            "repository.license",
            "repository.confirmed",
        ],
        "remaining_required_actions": action_list.get("required_open_actions", []),
        "post_upload_commands": [
            "python3 papers/paper2_voxel_topology_clogging/scripts/audit_submission_metadata_gaps.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/apply_submission_metadata.py --apply",
            "cd papers/paper2_voxel_topology_clogging/latex && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex",
            "PYTHONPATH=. python3 papers/paper2_voxel_topology_clogging/scripts/audit_paper2_manuscript_readiness.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/audit_latex_citations.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/audit_final_submission_gate.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/stage_data_code_deposit.py --force",
            "python3 papers/paper2_voxel_topology_clogging/scripts/archive_data_code_deposit.py --force",
            "python3 papers/paper2_voxel_topology_clogging/scripts/stage_journal_submission_files.py --force",
            "python3 papers/paper2_voxel_topology_clogging/scripts/archive_journal_submission_files.py --force",
            "python3 papers/paper2_voxel_topology_clogging/scripts/stage_elsevier_portal_upload_files.py --force",
            "python3 papers/paper2_voxel_topology_clogging/scripts/archive_elsevier_portal_upload_files.py --force",
            "python3 papers/paper2_voxel_topology_clogging/scripts/audit_release_archive_consistency.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/make_current_project_status.py",
        ],
        "boundary": boundary,
    }


def write_markdown(packet: dict[str, Any], out_md: Path) -> None:
    """Write a human-readable repository upload packet."""
    lines = [
        "# Paper 2 Repository Upload Packet",
        "",
        f"- Decision: `{packet['decision']}`",
        f"- Repository DOI assigned: `{packet['repository_doi_assigned']}`",
            f"- Metadata source: `{packet['metadata_source']}`",
            f"- Citation source: `{packet['citation_source']}`",
            f"- Upload instructions: `{packet['upload_instructions']}`",
            f"- Zenodo metadata draft: `{packet['zenodo_metadata_draft_path']}`",
            "",
        "## Upload Files",
        "",
        "| Role | Path | Size bytes | SHA256 |",
        "|---|---|---:|---|",
    ]
    for item in packet["upload_files"]:
        sha = item["sha256"] or "see file"
        lines.append(f"| {item['role']} | `{item['path']}` | {item['size_bytes']} | `{sha}` |")

    metadata = packet["zenodo_metadata_draft"]
    lines.extend(
        [
            "",
            "## Repository Metadata Draft",
            "",
            f"- Title: {metadata['title']}",
            f"- Upload type: `{metadata['upload_type']}`",
            f"- Access right: `{metadata['access_right']}`",
            f"- License: `{metadata['license']}`",
            f"- Keywords: {', '.join(metadata['keywords'])}",
            f"- Repository DOI: `{metadata.get('related_identifiers', {}).get('repository_doi', 'TBC')}`",
            f"- Manuscript DOI: `{metadata.get('related_identifiers', {}).get('manuscript_doi', 'TBC')}`",
            "",
            "### Creators",
            "",
        ]
    )
    for creator in metadata["creators"]:
        affiliation = creator.get("affiliation", "")
        lines.append(f"- {creator['name']} ({affiliation})")
    lines.extend(
        [
            "",
            "### Description",
            "",
            str(metadata["description"]).strip(),
            "",
            "### License Options To Confirm",
            "",
        ]
    )
    for option in packet["license_options_to_confirm"]:
        lines.append(f"- {option}")
    lines.extend(
        [
            "",
            "## Fields To Confirm After Upload",
            "",
        ]
    )
    for field in packet["fields_to_confirm_after_upload"]:
        lines.append(f"- `{field}`")
    lines.extend(["", "## Post-Upload Commands", "", "```bash"])
    lines.extend(packet["post_upload_commands"])
    lines.extend(
        [
            "```",
            "",
            "## Boundary",
            "",
            str(packet["boundary"]),
            "",
            (
                "Repository DOI/accession has been inserted; remaining checks concern manuscript/admin metadata."
                if packet["repository_doi_assigned"]
                else "Do not claim the repository is public until the DOI/accession and URL are assigned and inserted into `submission_metadata.yaml`."
            ),
        ]
    )
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_text_if_changed(path: Path, text: str) -> None:
    """Write text only when content changes so quick freshness checks remain stable."""
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_outputs(out_json: Path = OUT_JSON, out_md: Path = OUT_MD) -> dict[str, Any]:
    """Write JSON and Markdown repository upload packets."""
    packet = build_packet()
    out_json.parent.mkdir(parents=True, exist_ok=True)
    ZENODO_DRAFT.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    write_text_if_changed(ZENODO_DRAFT, json.dumps(packet["zenodo_metadata_draft"], indent=2, ensure_ascii=False))
    write_markdown(packet, out_md)
    return packet


def main() -> int:
    """Run upload-packet generation."""
    args = parse_args()
    packet = write_outputs(args.out_json, args.out_md)
    print(
        json.dumps(
            {
                "decision": packet["decision"],
                "repository_doi_assigned": packet["repository_doi_assigned"],
                "upload_files": len(packet["upload_files"]),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
