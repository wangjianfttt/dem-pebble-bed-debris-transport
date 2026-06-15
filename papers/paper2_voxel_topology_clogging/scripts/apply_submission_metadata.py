#!/usr/bin/env python3
"""Apply confirmed submission metadata to the Paper 2 LaTeX manuscript."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
DEFAULT_METADATA = PAPER_DIR / "submission" / "submission_metadata.yaml"
DEFAULT_LATEX = PAPER_DIR / "latex" / "main.tex"
DEFAULT_REPORT = PAPER_DIR / "submission" / "submission_metadata_application_report.json"

PLACEHOLDER_PATTERNS = [
    "TBC",
    "TBD",
    "TO_BE_ASSIGNED",
    "not yet assigned",
    "[TBC]",
    "[repository name]",
    "[grant number]",
]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA, help="YAML metadata file.")
    parser.add_argument("--latex", type=Path, default=DEFAULT_LATEX, help="LaTeX manuscript to update.")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT, help="JSON report path.")
    parser.add_argument("--apply", action="store_true", help="Write changes to the LaTeX manuscript.")
    return parser.parse_args()


def load_metadata(path: Path) -> dict[str, Any]:
    """Load submission metadata from YAML."""
    if not path.exists():
        raise FileNotFoundError(f"Missing metadata file: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Metadata YAML must contain a mapping: {path}")
    return data


def contains_placeholder(value: str) -> bool:
    """Return whether a string still contains placeholder wording."""
    normalized = value.strip()
    if not normalized:
        return True
    lower = normalized.lower()
    return any(pattern.lower() in lower for pattern in PLACEHOLDER_PATTERNS)


def require_confirmed_text(metadata: dict[str, Any], section: str, field: str) -> str:
    """Return a confirmed metadata string or raise a clear error."""
    block = metadata.get(section)
    if not isinstance(block, dict):
        raise ValueError(f"Missing metadata section: {section}")
    if not bool(block.get("confirmed", False)):
        raise ValueError(f"Metadata section is not confirmed: {section}")
    value = str(block.get(field, "")).strip()
    if contains_placeholder(value):
        raise ValueError(f"Metadata value is missing or still a placeholder: {section}.{field}")
    return value


def validate_metadata(metadata: dict[str, Any]) -> dict[str, str]:
    """Validate confirmed metadata and return normalized fields."""
    repository = metadata.get("repository")
    if not isinstance(repository, dict) or not bool(repository.get("confirmed", False)):
        raise ValueError("Metadata section is not confirmed: repository")
    repo_fields = {}
    for field in ("name", "identifier", "url", "license"):
        value = str(repository.get(field, "")).strip()
        if contains_placeholder(value):
            raise ValueError(f"Metadata value is missing or still a placeholder: repository.{field}")
        repo_fields[field] = value
    return {
        **{f"repository_{key}": value for key, value in repo_fields.items()},
        "competing_interests_statement": require_confirmed_text(metadata, "competing_interests", "statement"),
        "acknowledgements_statement": require_confirmed_text(metadata, "acknowledgements", "statement"),
        "corresponding_author_name": require_confirmed_text(metadata, "corresponding_author", "name"),
        "corresponding_author_email": require_confirmed_text(metadata, "corresponding_author", "email"),
    }


def build_data_availability(fields: dict[str, str]) -> str:
    """Build the LaTeX Data availability statement."""
    return (
        "The processed data, source tables, figure-generation scripts and analysis code supporting this study "
        f"are available from {fields['repository_name']} under DOI/accession "
        f"\\href{{{fields['repository_url']}}}{{{fields['repository_identifier']}}}. "
        "Large DEM dump/restart files are documented as optional raw-archive material and can be archived separately "
        f"where repository size limits require it. The lightweight deposit is released under {fields['repository_license']}."
    )


def build_code_availability(fields: dict[str, str]) -> str:
    """Build the LaTeX Code availability statement."""
    return (
        "The analysis and plotting scripts used to generate the figures and quantitative source tables are available "
        f"from {fields['repository_name']} under DOI/accession "
        f"\\href{{{fields['repository_url']}}}{{{fields['repository_identifier']}}}. "
        "The deposit includes paper-specific scripts, shared DEM post-processing utilities, voxel-topology analysis code, "
        "transport-analysis routines and regression tests."
    )


def replace_section_body(text: str, section: str, next_section: str, replacement: str) -> str:
    """Replace the body between two LaTeX unnumbered section headings."""
    start = f"\\section*{{{section}}}"
    end = next_section if next_section.startswith("\\") else f"\\section*{{{next_section}}}"
    start_index = text.find(start)
    end_index = text.find(end)
    if start_index < 0 or end_index < 0 or end_index <= start_index:
        raise ValueError(f"Could not locate LaTeX section boundary: {section} -> {next_section}")
    body_start = start_index + len(start)
    return text[:body_start] + "\n\n" + replacement.strip() + "\n\n" + text[end_index:]


def apply_metadata_to_text(text: str, fields: dict[str, str]) -> str:
    """Apply confirmed metadata fields to the LaTeX text."""
    updated = replace_section_body(text, "Data availability", "Code availability", build_data_availability(fields))
    updated = replace_section_body(updated, "Code availability", "CRediT authorship contribution statement", build_code_availability(fields))
    updated = replace_section_body(updated, "Declaration of competing interest", "Acknowledgements", fields["competing_interests_statement"])
    updated = replace_section_body(updated, "Acknowledgements", "\\bibliographystyle", fields["acknowledgements_statement"])
    return updated


def placeholder_warnings(text: str) -> list[str]:
    """Return known unresolved placeholder phrases still present in declaration sections."""
    warnings = []
    for phrase in (
        "A public repository DOI/accession has not yet been assigned",
        "Funding information should be confirmed",
        "This statement should be confirmed by all authors",
        "acknowledgements should be confirmed before submission",
    ):
        if phrase in text:
            warnings.append(phrase)
    return warnings


def apply_submission_metadata(metadata_path: Path, latex_path: Path, report_path: Path, write: bool) -> dict[str, Any]:
    """Validate metadata and optionally write updated LaTeX text."""
    metadata = load_metadata(metadata_path)
    fields = validate_metadata(metadata)
    original = latex_path.read_text(encoding="utf-8")
    updated = apply_metadata_to_text(original, fields)
    warnings = placeholder_warnings(updated)
    result = {
        "mode": "applied" if write else "dry_run",
        "metadata": str(metadata_path),
        "latex": str(latex_path),
        "report": str(report_path),
        "repository_identifier": fields["repository_identifier"],
        "corresponding_author_name": fields["corresponding_author_name"],
        "corresponding_author_email": fields["corresponding_author_email"],
        "remaining_placeholder_warnings": warnings,
        "post_apply_commands": [
            "python3 papers/paper2_voxel_topology_clogging/scripts/audit_submission_metadata_gaps.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/make_submission_form_packet.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/audit_final_submission_gate.py",
            "python3 papers/paper2_voxel_topology_clogging/scripts/make_current_project_status.py",
        ],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    if write:
        latex_path.write_text(updated, encoding="utf-8")
    return result


def main() -> int:
    """Run the metadata application workflow."""
    args = parse_args()
    result = apply_submission_metadata(args.metadata, args.latex, args.report, write=args.apply)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
