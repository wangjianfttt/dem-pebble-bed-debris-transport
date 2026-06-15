#!/usr/bin/env python3
"""Create copy-ready journal submission form fields for Paper 2."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
DEFAULT_LATEX = PAPER_DIR / "latex" / "main.tex"
DEFAULT_METADATA = PAPER_DIR / "submission" / "submission_metadata.yaml"
DEFAULT_JSON = PAPER_DIR / "submission" / "submission_form_packet.json"
DEFAULT_MD = PAPER_DIR / "submission" / "submission_form_packet.md"
TARGET_JOURNAL = "Chemical Engineering Science"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--latex", type=Path, default=DEFAULT_LATEX, help="LaTeX manuscript.")
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA, help="Submission metadata YAML.")
    parser.add_argument("--out-json", type=Path, default=DEFAULT_JSON, help="Output JSON packet.")
    parser.add_argument("--out-md", type=Path, default=DEFAULT_MD, help="Output Markdown packet.")
    return parser.parse_args()


def read_text(path: Path) -> str:
    """Read UTF-8 text from a required file."""
    if not path.exists():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8")


def clean_latex(text: str) -> str:
    """Convert a small subset of LaTeX markup to copy-ready plain text."""
    replacements = {
        r"\LiSi": "Li4SiO4",
        r"\BTC": "BTC",
        r"\Ib": "Ib",
        r"\FdW": "Fd/W",
        r"\ug": "ug",
        r"\dfdp": "df/dp",
        r"\%": "%",
        "--": "-",
    }
    cleaned = text
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    cleaned = re.sub(r"\\texorpdfstring\{([^{}]+)\}\{([^{}]+)\}", r"\2", cleaned)
    cleaned = re.sub(r"\\SI\{([^{}]+)\}\{([^{}]+)\}", r"\1 \2", cleaned)
    cleaned = re.sub(r"\\si\{([^{}]+)\}", r"\1", cleaned)
    cleaned = re.sub(r"\\times\s*10\^\{([^{}]+)\}", r"x10^\1", cleaned)
    cleaned = re.sub(r"\$([^$]+)\$", r"\1", cleaned)
    cleaned = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?\{([^{}]*)\}", r"\1", cleaned)
    cleaned = cleaned.replace("{", "").replace("}", "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def extract_between(text: str, start: str, end: str) -> str:
    """Extract text between two markers."""
    start_index = text.find(start)
    end_index = text.find(end, start_index + len(start))
    if start_index < 0 or end_index < 0:
        raise ValueError(f"Could not extract section between {start!r} and {end!r}")
    return text[start_index + len(start) : end_index].strip()


def extract_title(text: str) -> str:
    """Extract the PDF-safe manuscript title."""
    match = re.search(r"\\title\{\\texorpdfstring\{.*?\}\{(.*?)\}\}", text, flags=re.DOTALL)
    if not match:
        match = re.search(r"\\title\{(.*?)\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("Could not find manuscript title")
    return clean_latex(match.group(1))


def extract_authors(text: str) -> list[dict[str, str]]:
    """Extract authors and affiliation labels from elsarticle front matter."""
    rows = []
    author_text = re.sub(r"\\corref\{[^{}]+\}", "", text)
    for labels, name in re.findall(r"\\author\[([^\]]+)\]\{([^{}]+)\}", author_text):
        rows.append({"name": clean_latex(name), "affiliation_labels": labels})
    return rows


def extract_affiliations(text: str) -> dict[str, str]:
    """Extract affiliation labels and addresses."""
    return {label: clean_latex(address) for label, address in re.findall(r"\\address\[([^\]]+)\]\{([^{}]+)\}", text)}


def extract_keywords(text: str) -> list[str]:
    """Extract keyword entries from the LaTeX keyword block."""
    block = extract_between(text, "\\begin{keyword}", "\\end{keyword}")
    return [clean_latex(part) for part in block.split("\\sep") if clean_latex(part)]


def extract_section(text: str, section_name: str, next_marker: str) -> str:
    """Extract an unnumbered LaTeX section body."""
    return clean_latex(extract_between(text, f"\\section*{{{section_name}}}", next_marker))


def load_metadata(path: Path) -> dict[str, Any]:
    """Load submission metadata YAML."""
    data = yaml.safe_load(read_text(path))
    if not isinstance(data, dict):
        raise ValueError(f"Expected metadata mapping: {path}")
    return data


def load_highlights() -> list[str]:
    """Load highlights from the submission highlights file."""
    text = read_text(PAPER_DIR / "submission" / "highlights.md")
    return [line.strip()[2:].strip() for line in text.splitlines() if line.strip().startswith("- ")]


def metadata_status(metadata: dict[str, Any]) -> dict[str, bool]:
    """Return confirmation status flags from submission metadata."""
    keys = ["repository", "competing_interests", "acknowledgements", "corresponding_author"]
    return {key: bool(metadata.get(key, {}).get("confirmed", False)) for key in keys}


def build_packet(latex_path: Path, metadata_path: Path) -> dict[str, Any]:
    """Build the submission form packet."""
    text = read_text(latex_path)
    metadata = load_metadata(metadata_path)
    status = metadata_status(metadata)
    open_items = [key for key, confirmed in status.items() if not confirmed]
    remaining_note = (
        "All tracked administrative metadata are marked confirmed in submission_metadata.yaml."
        if not open_items
        else "Unconfirmed administrative metadata: " + ", ".join(open_items) + "."
    )
    packet = {
        "journal": TARGET_JOURNAL,
        "title": extract_title(text),
        "authors": extract_authors(text),
        "affiliations": extract_affiliations(text),
        "abstract": clean_latex(extract_between(text, "\\begin{abstract}", "\\end{abstract}")),
        "keywords": extract_keywords(text),
        "highlights": load_highlights(),
        "graphical_abstract_files": {
            "png": str(PAPER_DIR / "figures" / "paper2_graphical_abstract.png"),
            "pdf": str(PAPER_DIR / "figures" / "paper2_graphical_abstract.pdf"),
            "svg": str(PAPER_DIR / "figures" / "paper2_graphical_abstract.svg"),
        },
        "data_availability": extract_section(text, "Data availability", "\\section*{Code availability}"),
        "code_availability": extract_section(text, "Code availability", "\\section*{CRediT authorship contribution statement}"),
        "credit_author_statement": extract_section(text, "CRediT authorship contribution statement", "\\section*{Declaration of competing interest}"),
        "declaration_of_competing_interest": extract_section(text, "Declaration of competing interest", "\\section*{Acknowledgements}"),
        "acknowledgements": extract_section(text, "Acknowledgements", "\\bibliographystyle"),
        "metadata_confirmed": status,
        "submission_scope_note": (
            "Chemical Engineering Science submission framed as a mechanistic packed-bed transport study; "
            "the manuscript is bounded to DEM-derived pre-clogging migration, retention and pore-structure diagnostics."
        ),
        "remaining_admin_note": remaining_note,
    }
    return packet


def write_markdown(packet: dict[str, Any], out_path: Path) -> None:
    """Write a copy-ready Markdown version of the submission form packet."""
    lines = [
        "# Paper 2 Submission Form Packet",
        "",
        "This file collects copy-ready fields for the journal submission system. Do not treat placeholder or unconfirmed declaration text as final author-approved metadata.",
        "",
        f"## Journal\n\n{packet['journal']}",
        "",
        f"## Title\n\n{packet['title']}",
        "",
        "## Authors",
        "",
    ]
    for author in packet["authors"]:
        lines.append(f"- {author['name']} ({author['affiliation_labels']})")
    lines.extend(["", "## Affiliations", ""])
    for label, affiliation in packet["affiliations"].items():
        lines.append(f"- {label}: {affiliation}")
    lines.extend(["", "## Abstract", "", packet["abstract"], "", "## Keywords", ""])
    for keyword in packet["keywords"]:
        lines.append(f"- {keyword}")
    lines.extend(["", "## Highlights", ""])
    for highlight in packet["highlights"]:
        lines.append(f"- {highlight}")
    lines.extend(["", "## Graphical Abstract Files", ""])
    for label, path in packet["graphical_abstract_files"].items():
        lines.append(f"- {label}: `{path}`")
    lines.extend(["", "## Submission Scope Note", "", packet["submission_scope_note"]])
    for key, heading in [
        ("data_availability", "Data Availability"),
        ("code_availability", "Code Availability"),
        ("credit_author_statement", "CRediT Author Statement"),
        ("declaration_of_competing_interest", "Declaration Of Competing Interest"),
        ("acknowledgements", "Acknowledgements"),
    ]:
        lines.extend(["", f"## {heading}", "", packet[key]])
    lines.extend(["", "## Metadata Confirmation Status", ""])
    for key, value in packet["metadata_confirmed"].items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Remaining Administrative Note", "", packet["remaining_admin_note"]])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    """Write JSON and Markdown submission form packets."""
    args = parse_args()
    packet = build_packet(args.latex, args.metadata)
    args.out_json.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(packet, args.out_md)
    print(json.dumps({"title": packet["title"], "authors": len(packet["authors"]), "keywords": len(packet["keywords"]), "highlights": len(packet["highlights"])}, indent=2))
    print(args.out_json)
    print(args.out_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
