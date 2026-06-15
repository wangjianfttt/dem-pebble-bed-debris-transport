#!/usr/bin/env python3
"""Generate a formal supplementary-material LaTeX document for Paper 2."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path


PAPER_DIR = Path(__file__).resolve().parents[1]
SUPP_DIR = PAPER_DIR / "supplementary"
FIGURE_CATALOG = SUPP_DIR / "supplementary_figures.md"
TABLE_CATALOG = SUPP_DIR / "supplementary_tables.md"
OUT_TEX = SUPP_DIR / "supplementary_material.tex"


@dataclass(frozen=True)
class SupplementaryFigure:
    """Metadata for one supplementary figure."""

    label: str
    role: str
    pdf_path: str
    boundary: str


@dataclass(frozen=True)
class SupplementaryTable:
    """Metadata for one supplementary table file."""

    label: str
    title: str
    file_name: str
    columns: list[str]


def latex_escape(text: str) -> str:
    """Escape text for conservative LaTeX use."""
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def parse_markdown_table_row(line: str) -> list[str]:
    """Split a simple pipe-delimited markdown table row."""
    return [part.strip() for part in line.strip().strip("|").split("|")]


def parse_figures() -> list[SupplementaryFigure]:
    """Parse the supplementary-figure catalogue."""
    figures: list[SupplementaryFigure] = []
    for line in FIGURE_CATALOG.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| Fig. S"):
            continue
        cells = parse_markdown_table_row(line)
        if len(cells) < 6:
            continue
        label, role, _png, pdf_cell, _svg, boundary = cells[:6]
        match = re.search(r"`([^`]+\.pdf)`", pdf_cell)
        if not match:
            continue
        pdf_path = Path(match.group(1)).name
        figures.append(SupplementaryFigure(label=label, role=role, pdf_path=pdf_path, boundary=boundary))
    return figures


def parse_table_title(lines: list[str], index: int) -> str:
    """Extract a short table title near a file declaration."""
    for previous in reversed(lines[max(0, index - 5) : index]):
        previous = previous.strip()
        if previous.startswith("## "):
            return previous.removeprefix("## ").strip()
        if previous.startswith("### "):
            return previous.removeprefix("### ").strip()
    return "Supplementary table"


def parse_tables() -> list[SupplementaryTable]:
    """Parse supplementary table files and extract their column headers."""
    lines = TABLE_CATALOG.read_text(encoding="utf-8").splitlines()
    tables: list[SupplementaryTable] = []
    for index, line in enumerate(lines):
        match = re.search(r"`papers/paper2_voxel_topology_clogging/supplementary/(table_s(\d+)[^`]+\.csv)`", line)
        if not match:
            continue
        file_name = match.group(1)
        number = match.group(2)
        csv_path = SUPP_DIR / file_name
        columns: list[str] = []
        if csv_path.exists():
            with csv_path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.reader(handle)
                columns = next(reader, [])
        tables.append(
            SupplementaryTable(
                label=f"Table S{number}",
                title=parse_table_title(lines, index),
                file_name=file_name,
                columns=columns,
            )
        )
    return sorted(tables, key=lambda row: int(re.search(r"S(\d+)", row.label).group(1)))


def figure_include_path(figure: SupplementaryFigure) -> str:
    """Return the LaTeX include path for a supplementary figure."""
    return f"../figures/{figure.pdf_path}"


def build_tex(figures: list[SupplementaryFigure], tables: list[SupplementaryTable]) -> str:
    """Build the supplementary-material LaTeX source."""
    lines: list[str] = [
        r"\documentclass[11pt]{article}",
        r"\usepackage[a4paper,margin=22mm]{geometry}",
        r"\usepackage{graphicx}",
        r"\usepackage{booktabs}",
        r"\usepackage{longtable}",
        r"\usepackage{array}",
        r"\usepackage{ragged2e}",
        r"\usepackage[hidelinks]{hyperref}",
        r"\usepackage{caption}",
        r"\captionsetup{font=small,labelfont=bf}",
        r"\newcolumntype{P}[1]{>{\RaggedRight\arraybackslash}p{#1}}",
        r"\setlength{\parskip}{0.45em}",
        r"\setlength{\parindent}{0pt}",
        r"\begin{document}",
        r"\begin{center}",
        r"{\Large Supplementary Material}\\[0.5em]",
        r"{\large DEM-derived pore reconstruction and debris-transport assessment in a Li$_4$SiO$_4$ pebble bed}\\[0.75em]",
        r"Jian Wang, Mingzhun Lei, Haoxi Wang, Zhiyuan Liu, Haishun Deng, Wei Wen, and Gang Shen",
        r"\end{center}",
        r"\section*{Scope of the Supplementary Material}",
        (
            "This document collects the supplementary figures and table descriptors that support the "
            "bounded mechanism interpretation in the main manuscript. The supplementary material is used "
            "for traceability, sensitivity checks and evidence-boundary documentation. It does not introduce "
            "a universal clogging-transition law, a pressure-calibrated safety criterion or experimental "
            "validation of the DEM workflow."
        ),
        r"\section*{Supplementary Figure Roadmap}",
        r"\begin{longtable}{P{0.12\linewidth}P{0.40\linewidth}P{0.40\linewidth}}",
        r"\toprule",
        r"Figure & Role & Evidence boundary \\",
        r"\midrule",
        r"\endhead",
    ]
    for figure in figures:
        lines.append(
            f"{latex_escape(figure.label)} & {latex_escape(figure.role)} & {latex_escape(figure.boundary)} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{longtable}",
            r"\clearpage",
            r"\section*{Supplementary Figures}",
        ]
    )
    for figure in figures:
        lines.extend(
            [
                r"\begin{figure}[p]",
                r"\centering",
                rf"\includegraphics[width=0.96\linewidth,height=0.78\textheight,keepaspectratio]{{{figure_include_path(figure)}}}",
                (
                    rf"\caption*{{\textbf{{{latex_escape(figure.label)}.}} "
                    rf"{latex_escape(figure.role)}. \textit{{Boundary:}} {latex_escape(figure.boundary)}}}"
                ),
                r"\end{figure}",
                r"\clearpage",
            ]
        )
    lines.extend(
        [
            r"\section*{Supplementary Table Roadmap}",
            (
                "The numerical source tables are provided as comma-separated files to keep the quantitative "
                "evidence machine-readable. The table below records their role and column structure."
            ),
            r"\footnotesize",
            r"\begin{longtable}{P{0.12\linewidth}P{0.34\linewidth}P{0.26\linewidth}P{0.20\linewidth}}",
            r"\toprule",
            r"Table & Role & File & Columns \\",
            r"\midrule",
            r"\endhead",
        ]
    )
    for table in tables:
        columns = ", ".join(table.columns[:5])
        if len(table.columns) > 5:
            columns += ", ..."
        lines.append(
            f"{latex_escape(table.label)} & {latex_escape(table.title)} & "
            f"{latex_escape(table.file_name)} & {latex_escape(columns)} \\\\"
        )
    lines.extend(
        [
            r"\bottomrule",
            r"\end{longtable}",
            r"\section*{Boundary Statement}",
            (
                "All supplementary plots and tables should be interpreted within the studied parameter "
                "space, the present one-way DEM drag assumptions, finite voxel resolution and the absence "
                "of resolved hydraulic feedback in the transport calculation. Breakthrough curves, local "
                "blockage, connected-pore descriptors and pressure-drop checks are deliberately separated "
                "rather than collapsed into a single predictive clogging criterion."
            ),
            r"\end{document}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    """Generate the supplementary-material TeX file."""
    figures = parse_figures()
    tables = parse_tables()
    OUT_TEX.write_text(build_tex(figures, tables), encoding="utf-8")
    print(f"Wrote {OUT_TEX} with {len(figures)} figures and {len(tables)} tables.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
