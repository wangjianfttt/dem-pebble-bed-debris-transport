#!/usr/bin/env python3
"""Assemble multi-case ParaView OpenFOAM model and mesh renders."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
DEFAULT_RENDER_DIR = PAPER_DIR / "figures" / "openfoam_paraview"
DEFAULT_OUT = PAPER_DIR / "figures" / "paper2_figS26_openfoam_case_matrix"
DEFAULT_CASES = ("N3000_peak_blockage", "N6000_peak_blockage", "N10000_peak_blockage")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render-dir", type=Path, default=DEFAULT_RENDER_DIR, help="Directory containing ParaView PNG renders.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output path without extension.")
    parser.add_argument("--cases", nargs="+", default=list(DEFAULT_CASES), help="Case labels used in render filenames.")
    return parser.parse_args()


def crop_white_margin(image: Image.Image, threshold: int = 248, padding: int = 28) -> Image.Image:
    """Return a copy with excessive white margins removed."""
    rgb = image.convert("RGB")
    pixels = rgb.load()
    width, height = rgb.size
    xs: list[int] = []
    ys: list[int] = []
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            if min(r, g, b) < threshold:
                xs.append(x)
                ys.append(y)
    if not xs or not ys:
        return rgb
    left = max(min(xs) - padding, 0)
    right = min(max(xs) + padding, width)
    top = max(min(ys) - padding, 0)
    bottom = min(max(ys) + padding, height)
    return rgb.crop((left, top, right, bottom))


def load_panel(path: Path) -> Image.Image:
    """Load and crop one ParaView render."""
    if not path.exists():
        raise FileNotFoundError(path)
    return crop_white_margin(Image.open(path))


def debris_count_label(case_label: str) -> str:
    """Return a compact debris-count label from a case name."""
    token = case_label.split("_", 1)[0]
    if not token.startswith("N"):
        return case_label
    return f"N={token[1:]}"


def assemble_case_matrix(render_dir: Path, case_labels: list[str], out_base: Path) -> None:
    """Save a multi-case domain/mesh ParaView comparison figure."""
    if not case_labels:
        raise ValueError("At least one case label is required.")

    fig, axes = plt.subplots(len(case_labels), 2, figsize=(7.2, 2.35 * len(case_labels)), dpi=600)
    if len(case_labels) == 1:
        axes = axes.reshape(1, 2)

    column_titles = ("Cropped OpenFOAM domain", "Central mesh slice")
    for col, title in enumerate(column_titles):
        axes[0, col].set_title(title, fontsize=8, pad=3)

    panel_index = 0
    for row, case_label in enumerate(case_labels):
        model = load_panel(render_dir / f"{case_label}_model_domain_paraview.png")
        mesh = load_panel(render_dir / f"{case_label}_mesh_slice_paraview.png")
        for col, image in enumerate((model, mesh)):
            ax = axes[row, col]
            ax.imshow(image)
            ax.axis("off")
            ax.text(
                0.015,
                0.985,
                chr(ord("a") + panel_index),
                transform=ax.transAxes,
                ha="left",
                va="top",
                fontsize=8,
                fontweight="bold",
                color="black",
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.72, "pad": 1.0},
            )
            panel_index += 1
        axes[row, 0].text(
            -0.015,
            0.5,
            debris_count_label(case_label),
            transform=axes[row, 0].transAxes,
            ha="right",
            va="center",
            rotation=90,
            fontsize=8,
            color="black",
        )

    fig.patch.set_facecolor("white")
    fig.subplots_adjust(left=0.035, right=0.995, bottom=0.01, top=0.965, wspace=0.015, hspace=0.04)
    out_base.parent.mkdir(parents=True, exist_ok=True)
    for suffix in (".png", ".pdf", ".svg"):
        fig.savefig(out_base.with_suffix(suffix), dpi=600, facecolor="white")
    plt.close(fig)


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    assemble_case_matrix(args.render_dir.resolve(), list(args.cases), args.out.resolve())
    print(args.out.with_suffix(".png").resolve())
    print(args.out.with_suffix(".pdf").resolve())
    print(args.out.with_suffix(".svg").resolve())


if __name__ == "__main__":
    main()
