#!/usr/bin/env python3
"""Assemble a main-text-style OpenFOAM model and mesh figure.

The ParaView rendering script writes high-resolution standalone images for the
cropped OpenFOAM domain and a central mesh slice. This assembler keeps those
renders unchanged as provenance, then builds a compact three-panel figure:
domain render, full central mesh slice and a local mesh-detail crop.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.patches as patches
import matplotlib.pyplot as plt
from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
DEFAULT_RENDER_DIR = PAPER_DIR / "figures" / "openfoam_paraview"
DEFAULT_OUT = PAPER_DIR / "figures" / "paper2_openfoam_model_mesh_main"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--render-dir",
        type=Path,
        default=DEFAULT_RENDER_DIR,
        help="Directory containing ParaView PNG renders.",
    )
    parser.add_argument(
        "--case-label",
        default="N10000_peak_blockage",
        help="Case label used in render filenames.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output path without extension.",
    )
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
    """Load and crop a rendered ParaView panel."""
    if not path.exists():
        raise FileNotFoundError(path)
    return crop_white_margin(Image.open(path))


def mesh_detail_box(mesh: Image.Image) -> tuple[int, int, int, int]:
    """Return a deterministic central box for local mesh-detail inspection."""
    width, height = mesh.size
    box_w = int(width * 0.42)
    box_h = int(height * 0.42)
    left = int(width * 0.43)
    top = int(height * 0.34)
    right = min(left + box_w, width)
    bottom = min(top + box_h, height)
    return left, top, right, bottom


def add_panel_label(ax: plt.Axes, label: str) -> None:
    """Add a compact journal-style panel label."""
    ax.text(
        0.015,
        0.985,
        label,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=8,
        fontweight="bold",
        color="black",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.78, "pad": 1.0},
    )


def assemble_main_figure(model: Image.Image, mesh: Image.Image, out_base: Path) -> None:
    """Save the three-panel main-text-style OpenFOAM model/mesh figure."""
    detail_box = mesh_detail_box(mesh)
    detail = mesh.crop(detail_box)

    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.35), dpi=600)
    panels = (
        ("a", model, "Cropped domain"),
        ("b", mesh, "Central mesh slice"),
        ("c", detail, "Mesh detail"),
    )
    for ax, (label, image, title) in zip(axes, panels):
        ax.imshow(image)
        ax.set_title(title, fontsize=8, pad=2)
        ax.axis("off")
        add_panel_label(ax, label)

    left, top, right, bottom = detail_box
    rect = patches.Rectangle(
        (left, top),
        right - left,
        bottom - top,
        fill=False,
        linewidth=1.0,
        edgecolor="#B23A48",
    )
    axes[1].add_patch(rect)

    fig.patch.set_facecolor("white")
    fig.subplots_adjust(left=0.004, right=0.996, bottom=0.004, top=0.91, wspace=0.025)
    out_base.parent.mkdir(parents=True, exist_ok=True)
    for suffix in (".png", ".pdf", ".svg"):
        fig.savefig(out_base.with_suffix(suffix), dpi=600, facecolor="white")
    plt.close(fig)


def main() -> None:
    """CLI entry point."""
    args = parse_args()
    render_dir = args.render_dir.resolve()
    model = load_panel(render_dir / f"{args.case_label}_model_domain_paraview.png")
    mesh = load_panel(render_dir / f"{args.case_label}_mesh_slice_paraview.png")
    assemble_main_figure(model, mesh, args.out.resolve())
    print(args.out.with_suffix(".png").resolve())
    print(args.out.with_suffix(".pdf").resolve())
    print(args.out.with_suffix(".svg").resolve())


if __name__ == "__main__":
    main()
