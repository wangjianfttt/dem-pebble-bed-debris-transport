#!/usr/bin/env python3
"""Audit unresolved Paper 2 submission metadata and author confirmations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
DEFAULT_METADATA = PAPER_DIR / "submission" / "submission_metadata.yaml"
DEFAULT_JSON = PAPER_DIR / "submission" / "submission_metadata_gaps.json"
DEFAULT_MD = PAPER_DIR / "submission" / "author_confirmation_sheet.md"

REQUIRED_FIELDS = {
    "repository": {
        "fields": ("name", "identifier", "url", "license"),
        "why": "Required for Data availability and Code availability.",
    },
    "competing_interests": {
        "fields": ("statement",),
        "why": "Required by the journal and must be confirmed by all authors.",
    },
    "acknowledgements": {
        "fields": ("statement",),
        "why": "Required to avoid unapproved computing-resource or collaborator wording.",
    },
    "corresponding_author": {
        "fields": ("name", "email"),
        "why": "Required for the journal submission system and cover-letter metadata.",
    },
}

PLACEHOLDERS = ("TBC", "TBD", "TO_BE_ASSIGNED", "[TBC]", "[repository name]", "[grant number]")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA, help="Submission metadata YAML.")
    parser.add_argument("--out-json", type=Path, default=DEFAULT_JSON, help="Output JSON report.")
    parser.add_argument("--out-md", type=Path, default=DEFAULT_MD, help="Output author confirmation sheet.")
    return parser.parse_args()


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML mapping from disk."""
    if not path.exists():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in YAML file: {path}")
    return data


def is_placeholder(value: Any) -> bool:
    """Return True when a metadata value is blank or still a placeholder."""
    text = str(value or "").strip()
    if not text:
        return True
    lower = text.lower()
    return any(token.lower() in lower for token in PLACEHOLDERS)


def audit_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """Build a structured audit report for required submission metadata."""
    sections: list[dict[str, Any]] = []
    required_open = 0
    optional_open = 0

    for section, spec in REQUIRED_FIELDS.items():
        block = metadata.get(section)
        optional = bool(spec.get("optional", False))
        if not isinstance(block, dict):
            missing = list(spec["fields"])
            confirmed = False
        else:
            confirmed = bool(block.get("confirmed", False))
            missing = [field for field in spec["fields"] if is_placeholder(block.get(field))]

        status = "complete" if confirmed and not missing else ("optional_open" if optional else "open")
        if status == "open":
            required_open += 1
        elif status == "optional_open":
            optional_open += 1

        sections.append(
            {
                "section": section,
                "status": status,
                "confirmed": confirmed,
                "missing_fields": missing,
                "required": not optional,
                "why": spec["why"],
            }
        )

    return {
        "metadata": str(DEFAULT_METADATA),
        "required_open": required_open,
        "optional_open": optional_open,
        "ready_to_apply_metadata": required_open == 0,
        "sections": sections,
    }


def write_confirmation_sheet(report: dict[str, Any], out_path: Path) -> None:
    """Write a human-readable author confirmation sheet."""
    lines = [
        "# Paper 2 Author Confirmation Sheet",
        "",
        "Use this sheet before journal submission. It is a control document: do not mark an item complete unless the corresponding author has author-approved wording or metadata.",
        "",
        "## Submission Metadata To Confirm",
        "",
        "| Section | Status | Missing fields | Why it matters |",
        "|---|---|---|---|",
    ]
    for row in report["sections"]:
        missing = ", ".join(row["missing_fields"]) if row["missing_fields"] else "none"
        lines.append(f"| {row['section']} | {row['status']} | {missing} | {row['why']} |")

    lines.extend(
        [
            "",
            "## Author Approval Checks",
            "",
            "| Item | Confirmation owner | Confirmed? | Notes |",
            "|---|---|---|---|",
            "| Final title | All authors | no | Separating breakthrough from pore-network clogging indicators in gas-driven fine-debris transport through Li4SiO4 pebble beds |",
            "| Author order | All authors | yes | Jian Wang; Mingzhun Lei; Haoxi Wang; Zhiyuan Liu; Haishun Deng; Wei Wen; Gang Shen |",
            "| Affiliations | Each author | no | Check spelling and institution names in LaTeX front matter. |",
            "| Corresponding author | Corresponding author | no | Fill name and email in submission_metadata.yaml. |",
            "| Scientific scope | Corresponding author | no | Confirm bounded DEM-based pre-clogging migration/retention framing. |",
            "| Voxel wording | Corresponding author | no | Confirm wording stays as DEM-derived voxel reconstruction, not experimental CT. |",
            "| Data/code deposit | Corresponding author | no | Upload archive, obtain DOI/accession, confirm license. |",
            "| Competing interests | All authors | no | Each author confirms the statement. |",
            "| Acknowledgements | Corresponding author | yes | Support wording supplied by the corresponding author. |",
            "",
            "## Exact Workflow After Confirmation",
            "",
            "1. Edit `papers/paper2_voxel_topology_clogging/submission/submission_metadata.yaml`.",
            "2. Set each confirmed required section to `confirmed: true` and replace all `TBC` values.",
            "3. Run `python3 papers/paper2_voxel_topology_clogging/scripts/audit_submission_metadata_gaps.py`.",
            "4. Run `python3 papers/paper2_voxel_topology_clogging/scripts/apply_submission_metadata.py --apply`.",
            "5. Recompile the LaTeX manuscript and rerun the final submission gate.",
            "",
            "## Current Decision",
            "",
            f"- Required metadata sections still open: `{report['required_open']}`",
            f"- Optional metadata sections still open: `{report['optional_open']}`",
            f"- Ready to apply metadata: `{report['ready_to_apply_metadata']}`",
        ]
    )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    """Run the metadata-gap audit and write reports."""
    args = parse_args()
    metadata = load_yaml(args.metadata)
    report = audit_metadata(metadata)
    report["metadata"] = str(args.metadata)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_confirmation_sheet(report, args.out_md)
    print(json.dumps({"required_open": report["required_open"], "optional_open": report["optional_open"], "ready_to_apply_metadata": report["ready_to_apply_metadata"]}, indent=2))
    print(args.out_json)
    print(args.out_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
