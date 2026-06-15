#!/usr/bin/env python3
"""Analyze voxel-size sensitivity for Paper 2 baseline topology metrics."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.postprocess.read_liggghts_dump import read_liggghts_dump
from src.voxel.fractal import box_counting_dimension
from src.voxel.topology import (
    compute_connected_components,
    compute_euler_number,
    compute_largest_connected_void_fraction,
    compute_outlet_connected_fraction,
    compute_topological_charge,
)
from src.voxel.voxelize import voxelize_spheres


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
FIG_DIR = PAPER_DIR / "figures"
TABLE_DIR = PAPER_DIR / "tables"
NOTE_DIR = PAPER_DIR / "notes"

BASELINE_VOXEL = PROJECT_ROOT / "data" / "processed" / "ct_pipeline_li4sio4_1mm_10k_axial_cuboid_piston_compacted" / "bed_voxel_effective.npz"
BASELINE_DUMP = (
    PROJECT_ROOT
    / "cases"
    / "bed_piston_compaction_li4sio4_1mm_10k_axial_cuboid"
    / "li4sio4_1mm_10k_axial_cuboid_piston_compacted_12000000.dump"
)
OUT_TABLE = TABLE_DIR / "paper2_voxel_size_sensitivity_source.csv"
OUT_FIG = FIG_DIR / "paper2_figS1_voxel_size_sensitivity"
OUT_STRESS_FIG = FIG_DIR / "paper2_figS2_voxel_coarsening_stress_test"
OUT_NOTE = NOTE_DIR / "stage_report_voxel_size_sensitivity_2026-06-09.md"
REVOXELIZED_SIZES_M = (0.00020, 0.00025, 0.00030, 0.00040, 0.00050)


def configure_matplotlib() -> None:
    """Configure a clean style for sensitivity plots."""
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 8,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.8,
            "axes.labelsize": 8,
            "axes.titlesize": 8,
            "xtick.labelsize": 7.2,
            "ytick.labelsize": 7.2,
            "legend.fontsize": 7,
            "legend.frameon": False,
        }
    )


def load_baseline_voxel() -> tuple[np.ndarray, dict]:
    """Load the baseline voxel and metadata."""
    if not BASELINE_VOXEL.exists():
        raise FileNotFoundError(BASELINE_VOXEL)
    data = np.load(BASELINE_VOXEL, allow_pickle=True)
    voxel = data["voxel"]
    metadata = json.loads(str(data["metadata"]))
    if voxel.ndim != 3:
        raise ValueError(f"Expected 3D voxel, got {voxel.shape}")
    return voxel, metadata


def crop_to_factor(voxel: np.ndarray, factor: int) -> np.ndarray:
    """Crop a voxel array so each dimension is divisible by the coarsening factor."""
    if factor <= 0:
        raise ValueError("factor must be positive.")
    shape = tuple((dim // factor) * factor for dim in voxel.shape)
    if any(dim <= 0 for dim in shape):
        raise ValueError(f"Coarsening factor {factor} is too large for shape {voxel.shape}")
    return voxel[: shape[0], : shape[1], : shape[2]]


def coarsen_void_mask(void_mask: np.ndarray, factor: int, rule: str) -> np.ndarray:
    """Coarsen a void mask by block aggregation.

    ``majority`` marks a coarse cell as void if at least half of its fine voxels
    are void. ``conservative_void`` marks a coarse cell as void only if all fine
    voxels in the block are void.
    """
    if rule not in {"majority", "conservative_void"}:
        raise ValueError("rule must be 'majority' or 'conservative_void'.")
    cropped = crop_to_factor(void_mask.astype(bool), factor)
    sx, sy, sz = cropped.shape
    blocks = cropped.reshape(sx // factor, factor, sy // factor, factor, sz // factor, factor)
    void_fraction = blocks.mean(axis=(1, 3, 5))
    if rule == "majority":
        return void_fraction >= 0.5
    return void_fraction >= 1.0


def compute_metrics(void_mask: np.ndarray, voxel_size: float, factor: int, rule: str, analysis_type: str) -> dict[str, object]:
    """Compute topology and fractal metrics for one coarsened void mask."""
    pore_count = int(void_mask.sum())
    porosity = float(pore_count / void_mask.size)
    _, component_count = compute_connected_components(void_mask)
    largest = compute_largest_connected_void_fraction(void_mask)
    outlet_x = compute_outlet_connected_fraction(void_mask, inlet_axis="x")
    euler = compute_euler_number(void_mask)
    topological_charge = compute_topological_charge(euler, reference=float(void_mask.size))
    fractal = box_counting_dimension(void_mask)
    return {
        "analysis_type": analysis_type,
        "factor": factor,
        "rule": rule,
        "effective_voxel_size_m": voxel_size * factor,
        "shape_x": int(void_mask.shape[0]),
        "shape_y": int(void_mask.shape[1]),
        "shape_z": int(void_mask.shape[2]),
        "porosity": porosity,
        "connected_void_components": int(component_count),
        "largest_connected_void_fraction": float(largest),
        "outlet_connected_fraction_x": float(outlet_x),
        "euler_number": int(euler),
        "topological_charge": float(topological_charge),
        "fractal_dimension": float(fractal["Df"]),
        "fractal_fit_r2": float(fractal["fit_r2"]),
        "pore_voxel_count": pore_count,
        "total_voxel_count": int(void_mask.size),
    }


def build_sensitivity_table() -> pd.DataFrame:
    """Build the voxel-size sensitivity table."""
    voxel, metadata = load_baseline_voxel()
    voxel_size = float(metadata["voxel_size"])
    base_void = voxel == 0
    rows = [compute_metrics(base_void, voxel_size, 1, "native_existing_voxel", "native")]
    for factor in (2, 3, 4, 5):
        for rule in ("majority", "conservative_void"):
            rows.append(compute_metrics(coarsen_void_mask(base_void, factor, rule), voxel_size, factor, rule, "coarsened"))
    rows.extend(build_revoxelized_rows(metadata))
    return pd.DataFrame(rows)


def build_revoxelized_rows(metadata: dict) -> list[dict[str, object]]:
    """Re-voxelize the bed skeleton from DEM coordinates at independent voxel sizes."""
    if not BASELINE_DUMP.exists():
        raise FileNotFoundError(BASELINE_DUMP)
    domain = metadata["domain"]
    df = read_liggghts_dump(BASELINE_DUMP)
    bed = df[df["type"] == 1].copy()
    if bed.empty:
        raise ValueError(f"No type-1 bed particles found in {BASELINE_DUMP}")
    centers = bed[["x", "y", "z"]].to_numpy(dtype=float)
    radii = bed["radius"].to_numpy(dtype=float)
    rows: list[dict[str, object]] = []
    for voxel_size in REVOXELIZED_SIZES_M:
        voxel = voxelize_spheres(centers, radii, domain, voxel_size, solid_value=1, progress_interval=0)
        rows.append(compute_metrics(voxel == 0, float(voxel_size), 1, "revoxelized_from_dem", "revoxelized"))
    return rows


def panel_label(ax: plt.Axes, label: str) -> None:
    """Place a panel label inside the axes."""
    ax.text(
        0.03,
        0.92,
        label,
        transform=ax.transAxes,
        va="top",
        ha="left",
        weight="bold",
        fontsize=9,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85, "pad": 0.8},
    )


def plot_revoxelized_sensitivity(table: pd.DataFrame) -> None:
    """Plot independent re-voxelization sensitivity as a supplementary figure."""
    configure_matplotlib()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    revox = table[table["analysis_type"] == "revoxelized"].sort_values("effective_voxel_size_m")
    if revox.empty:
        raise ValueError("No revoxelized rows available for plotting.")
    fig = plt.figure(figsize=(7.2, 4.8), constrained_layout=True)
    grid = fig.add_gridspec(2, 2)
    axes = [fig.add_subplot(grid[i, j]) for i in range(2) for j in range(2)]
    metrics = [
        ("porosity", "porosity"),
        ("outlet_connected_fraction_x", "outlet-connected void"),
        ("fractal_dimension", "fractal dimension"),
        ("topological_charge", "topological charge"),
    ]
    for ax, (metric, ylabel), label in zip(axes, metrics, ["a", "b", "c", "d"]):
        ax.scatter(
            revox["effective_voxel_size_m"] * 1e3,
            revox[metric],
            color="#2166ac",
            s=44,
            edgecolor="#222222",
            linewidth=0.35,
        )
        ax.axvline(0.25, color="#7f7f7f", linewidth=0.8, linestyle=":", zorder=0)
        ax.set_xlabel("effective voxel size (mm)")
        ax.set_ylabel(ylabel)
        ax.grid(True, linewidth=0.35, alpha=0.35)
        panel_label(ax, label)
    for suffix, kwargs in {".png": {"dpi": 600}, ".pdf": {}, ".svg": {}}.items():
        fig.savefig(f"{OUT_FIG}{suffix}", bbox_inches="tight", **kwargs)
    plt.close(fig)


def plot_coarsening_stress_test(table: pd.DataFrame) -> None:
    """Plot coarse-graining sensitivity as a stress-test supplementary figure."""
    configure_matplotlib()
    stress = table[table["analysis_type"].isin(["native", "coarsened"])].copy()
    fig = plt.figure(figsize=(7.2, 4.8), constrained_layout=True)
    grid = fig.add_gridspec(2, 2)
    axes = [fig.add_subplot(grid[i, j]) for i in range(2) for j in range(2)]
    metrics = [
        ("porosity", "porosity"),
        ("outlet_connected_fraction_x", "outlet-connected void"),
        ("fractal_dimension", "fractal dimension"),
        ("topological_charge", "topological charge"),
    ]
    colors = {"native_existing_voxel": "#4d4d4d", "majority": "#2166ac", "conservative_void": "#b2182b"}
    markers = {"native_existing_voxel": "o", "majority": "o", "conservative_void": "s"}
    for ax, (metric, ylabel), label in zip(axes, metrics, ["a", "b", "c", "d"]):
        for rule, group in stress.groupby("rule"):
            group = group.sort_values("effective_voxel_size_m")
            label_text = rule.replace("_", " ")
            ax.scatter(
                group["effective_voxel_size_m"] * 1e3,
                group[metric],
                s=42,
                marker=markers.get(rule, "o"),
                color=colors.get(rule, "#4d4d4d"),
                edgecolor="#222222",
                linewidth=0.35,
                label=label_text,
            )
            if rule != "native_existing_voxel" and len(group) > 1:
                ax.plot(
                    group["effective_voxel_size_m"] * 1e3,
                    group[metric],
                    color=colors[rule],
                    linewidth=0.8,
                    alpha=0.35,
                    zorder=0,
                )
        ax.set_xlabel("effective voxel size (mm)")
        ax.set_ylabel(ylabel)
        ax.grid(True, linewidth=0.35, alpha=0.35)
        panel_label(ax, label)
    axes[0].legend(loc="best")
    for suffix, kwargs in {".png": {"dpi": 600}, ".pdf": {}, ".svg": {}}.items():
        fig.savefig(f"{OUT_STRESS_FIG}{suffix}", bbox_inches="tight", **kwargs)
    plt.close(fig)


def write_stage_report(table: pd.DataFrame) -> None:
    """Write a short stage report for the sensitivity analysis."""
    NOTE_DIR.mkdir(parents=True, exist_ok=True)
    native = table[table["rule"] == "native_existing_voxel"].iloc[0]
    revox = table[table["analysis_type"] == "revoxelized"]
    majority = table[table["rule"] == "majority"]
    conservative = table[table["rule"] == "conservative_void"]
    lines = [
        "# Stage Report: Voxel-Size Sensitivity",
        "",
        "Date: 2026-06-09",
        "",
        "## Scope",
        "",
        "This stage tests whether baseline pore-topology metrics are robust to voxel-size choices.",
        "",
        "## Method",
        "",
        "Two sensitivity checks are reported:",
        "",
        "- independent re-voxelization from DEM particle coordinates at voxel sizes of 0.20, 0.25, 0.30, 0.40 and 0.50 mm;",
        "- coarse-graining of the native voxel field by block factors 2, 3, 4 and 5 using majority and conservative-void rules.",
        "",
        "The independent re-voxelization rows are the primary sensitivity evidence. The coarse-graining rows are treated as a numerical stress test.",
        "",
        "## Outputs",
        "",
        f"- `{OUT_TABLE.relative_to(PROJECT_ROOT)}`",
        f"- `{OUT_FIG.relative_to(PROJECT_ROOT)}.png`",
        f"- `{OUT_FIG.relative_to(PROJECT_ROOT)}.pdf`",
        f"- `{OUT_FIG.relative_to(PROJECT_ROOT)}.svg`",
        f"- `{OUT_STRESS_FIG.relative_to(PROJECT_ROOT)}.png`",
        f"- `{OUT_STRESS_FIG.relative_to(PROJECT_ROOT)}.pdf`",
        f"- `{OUT_STRESS_FIG.relative_to(PROJECT_ROOT)}.svg`",
        "",
        "## Native Baseline",
        "",
        f"- porosity: {native['porosity']:.6f}",
        f"- outlet-connected void fraction along x: {native['outlet_connected_fraction_x']:.6f}",
        f"- fractal dimension: {native['fractal_dimension']:.6f}",
        f"- topological charge: {native['topological_charge']:.6f}",
        "",
        "## Independent Re-Voxelization Ranges",
        "",
        f"- porosity range: {revox['porosity'].min():.6f} to {revox['porosity'].max():.6f}",
        f"- outlet-connected range: {revox['outlet_connected_fraction_x'].min():.6f} to {revox['outlet_connected_fraction_x'].max():.6f}",
        f"- fractal-dimension range: {revox['fractal_dimension'].min():.6f} to {revox['fractal_dimension'].max():.6f}",
        f"- topological-charge range: {revox['topological_charge'].min():.6f} to {revox['topological_charge'].max():.6f}",
        "",
        "## Coarsened Ranges",
        "",
        f"- majority porosity range: {majority['porosity'].min():.6f} to {majority['porosity'].max():.6f}",
        f"- conservative-void porosity range: {conservative['porosity'].min():.6f} to {conservative['porosity'].max():.6f}",
        f"- majority outlet-connected range: {majority['outlet_connected_fraction_x'].min():.6f} to {majority['outlet_connected_fraction_x'].max():.6f}",
        f"- conservative-void outlet-connected range: {conservative['outlet_connected_fraction_x'].min():.6f} to {conservative['outlet_connected_fraction_x'].max():.6f}",
        "",
        "## Interpretation Boundary",
        "",
        "The independent re-voxelization check is suitable for manuscript support because it recomputes the solid/pore field directly from DEM coordinates. The coarse-graining check is more conservative and mainly shows that topology metrics can be sensitive to thresholding rules when the voxel field is aggressively down-sampled.",
    ]
    OUT_NOTE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    """Run voxel-size sensitivity analysis."""
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    table = build_sensitivity_table()
    table.to_csv(OUT_TABLE, index=False)
    plot_revoxelized_sensitivity(table)
    plot_coarsening_stress_test(table)
    write_stage_report(table)
    print(f"Wrote: {OUT_TABLE}")
    print(f"Wrote: {OUT_FIG}.png/.pdf/.svg")
    print(f"Wrote: {OUT_STRESS_FIG}.png/.pdf/.svg")
    print(f"Wrote: {OUT_NOTE}")
    print(table[["analysis_type", "factor", "rule", "effective_voxel_size_m", "porosity", "outlet_connected_fraction_x", "fractal_dimension", "topological_charge"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
