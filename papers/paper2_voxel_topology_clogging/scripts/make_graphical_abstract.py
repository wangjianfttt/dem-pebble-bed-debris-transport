#!/usr/bin/env python3
"""Create a non-distorted graphical abstract for journal submission."""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
OUT_BASE = PAPER_DIR / "figures" / "paper2_graphical_abstract"


def configure_matplotlib() -> None:
    """Configure typography and export settings for a journal graphical abstract."""
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 9,
        }
    )


def arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], color: str = "#4a4a4a") -> None:
    """Draw a clean process arrow between graphical-abstract panels."""
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=18,
            linewidth=1.8,
            color=color,
            shrinkA=0,
            shrinkB=0,
        )
    )


def panel_label(ax: plt.Axes, x: float, y: float, text: str) -> None:
    """Draw a compact panel label."""
    ax.text(x, y, text, ha="center", va="center", fontsize=10.5, weight="bold", color="#222222")


def draw_dem_panel(ax: plt.Axes) -> None:
    """Draw a stylized DEM pebble bed with gas-driven fine-particle transport."""
    rng = np.random.default_rng(42)
    x0, y0, w, h = 0.45, 0.85, 2.55, 1.95
    ax.add_patch(Rectangle((x0, y0), w, h, facecolor="#fbfaf6", edgecolor="#333333", linewidth=1.3))

    for _ in range(72):
        r = rng.uniform(0.055, 0.085)
        x = rng.uniform(x0 + r + 0.04, x0 + w - r - 0.04)
        y = rng.uniform(y0 + r + 0.04, y0 + h - r - 0.04)
        ax.add_patch(Circle((x, y), r, facecolor="#d6d3c8", edgecolor="white", linewidth=0.45))

    path = np.array(
        [
            [0.72, 1.20],
            [1.05, 1.42],
            [1.36, 1.36],
            [1.70, 1.72],
            [2.05, 1.84],
            [2.38, 2.05],
            [2.72, 2.26],
        ]
    )
    ax.plot(path[:, 0], path[:, 1], color="#b33b35", linewidth=2.2, solid_capstyle="round")
    for x, y in path:
        ax.add_patch(Circle((x, y), 0.035, facecolor="#b33b35", edgecolor="white", linewidth=0.35, zorder=4))

    arrow(ax, (0.18, 1.78), (0.45, 1.78), "#2d6fb8")
    arrow(ax, (3.00, 1.78), (3.28, 1.78), "#2d6fb8")
    ax.text(0.18, 1.52, "gas", ha="center", va="center", fontsize=9.5, color="#2d6fb8")
    ax.text(1.73, 0.55, "fines migrate through a stiff pebble bed", ha="center", va="center", fontsize=9.0, color="#333333")
    panel_label(ax, 1.73, 3.12, "DEM transport")


def draw_pore_panel(ax: plt.Axes) -> None:
    """Draw a compact DEM-derived pore reconstruction and topology diagnostic panel."""
    panel_label(ax, 5.0, 3.12, "Pore-structure observables")
    x0, y0, cell = 4.00, 1.36, 0.145
    pattern = np.array(
        [
            [1, 0, 0, 1, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 2, 0, 0, 1],
            [1, 0, 0, 1, 0, 0, 1, 0],
            [0, 0, 2, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 1, 0, 0, 1],
        ]
    )
    colors = {0: "#ffffff", 1: "#899596", 2: "#b33b35"}
    for row in range(pattern.shape[0]):
        for col in range(pattern.shape[1]):
            ax.add_patch(
                Rectangle(
                    (x0 + col * cell, y0 + (pattern.shape[0] - 1 - row) * cell),
                    cell,
                    cell,
                    facecolor=colors[int(pattern[row, col])],
                    edgecolor="#dadada",
                    linewidth=0.65,
                )
            )
    ax.add_patch(
        Rectangle((x0, y0), pattern.shape[1] * cell, pattern.shape[0] * cell, fill=False, edgecolor="#333333", linewidth=1.1)
    )
    ax.text(4.58, 0.98, "local void/\nsolid map", ha="center", va="center", fontsize=8.0, color="#333333", linespacing=1.05)

    nodes = np.array([[5.70, 1.68], [6.02, 2.10], [6.36, 1.70], [5.92, 1.28], [6.50, 2.18]])
    edges = [(0, 1), (1, 2), (1, 4), (0, 3), (2, 3)]
    for i, j in edges:
        ax.plot(nodes[[i, j], 0], nodes[[i, j], 1], color="#2c748a", linewidth=1.8)
    ax.scatter(nodes[:, 0], nodes[:, 1], s=140, color="#8ec6d9", edgecolor="#333333", linewidth=0.7, zorder=4)
    ax.text(6.12, 0.98, "connected-pore\nskeleton", ha="center", va="center", fontsize=8.0, color="#333333", linespacing=1.05)


def draw_assessment_panel(ax: plt.Axes) -> None:
    """Draw staged clogging-assessment logic without claiming a universal criterion."""
    panel_label(ax, 8.42, 3.12, "Staged assessment")
    rows = [
        ("BTC", "transport / contamination"),
        ("B(z,t)", "deposition localization"),
        ("C loss", "structural degradation"),
        ("\u0394P", "hydraulic confirmation"),
    ]
    y_start = 2.46
    fills = ["#edf4fb", "#fff3e8", "#eef7ef", "#f7eeee"]
    marks = ["#2d6fb8", "#c7772e", "#1d7f43", "#9a2d2d"]
    for idx, ((symbol, text), fill, mark) in enumerate(zip(rows, fills, marks)):
        y = y_start - idx * 0.39
        ax.add_patch(Rectangle((7.28, y - 0.16), 2.28, 0.32, facecolor=fill, edgecolor="#b7b7b7", linewidth=0.8))
        ax.add_patch(Circle((7.48, y), 0.055, facecolor=mark, edgecolor="white", linewidth=0.35))
        ax.text(7.68, y, symbol, ha="left", va="center", fontsize=9.4, weight="bold", color="#222222")
        ax.text(8.34, y, text, ha="left", va="center", fontsize=7.8, color="#333333")

    ax.text(
        8.42,
        0.70,
        "breakthrough alone is not a\npressure-calibrated clogging criterion",
        ha="center",
        va="center",
        fontsize=8.6,
        color="#333333",
        linespacing=1.12,
    )


def make_graphical_abstract() -> list[Path]:
    """Generate PNG, PDF and SVG files with equal-aspect geometry."""
    configure_matplotlib()
    fig, ax = plt.subplots(figsize=(10, 4), dpi=240)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(
        5.0,
        3.65,
        "Separating fines breakthrough from pore-network clogging indicators",
        ha="center",
        va="center",
        fontsize=13.2,
        weight="bold",
        color="#111111",
    )
    draw_dem_panel(ax)
    arrow(ax, (3.34, 1.80), (3.75, 1.80))
    draw_pore_panel(ax)
    arrow(ax, (6.75, 1.80), (7.17, 1.80))
    draw_assessment_panel(ax)
    ax.text(
        5.0,
        0.22,
        "DEM trajectories, pore reconstruction and bounded pressure checks provide complementary indicators in the sampled cases.",
        ha="center",
        va="center",
        fontsize=8.8,
        color="#333333",
    )

    outputs = []
    for suffix in (".png", ".pdf", ".svg"):
        path = OUT_BASE.with_suffix(suffix)
        fig.savefig(path, bbox_inches="tight", pad_inches=0.08)
        outputs.append(path)
    plt.close(fig)
    return outputs


def main() -> int:
    """Run graphical abstract generation."""
    for path in make_graphical_abstract():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
