#!/usr/bin/env python3
"""Run a lightweight voxel-network pressure pilot for Paper 2."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.voxel.io import load_voxel_npz  # noqa: E402
from src.voxel.permeability import pressure_profile, solve_voxel_pressure  # noqa: E402


PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
VOXEL_PATH = PROJECT_ROOT / "data/processed/ct_pipeline_li4sio4_1mm_10k_axial_cuboid_piston_compacted/bed_voxel_effective.npz"
BLOCKAGE_PROFILE = PAPER_DIR / "tables/paper2_fig4_loading_blockage_source.csv"
OUT_TABLE = PAPER_DIR / "tables/paper2_voxel_pressure_pilot_source.csv"
OUT_PROFILE = PAPER_DIR / "tables/paper2_voxel_pressure_pilot_profiles.csv"
OUT_JSON = PAPER_DIR / "data/paper2_voxel_pressure_pilot_summary.json"
OUT_FIG = PAPER_DIR / "figures/paper2_figS12_voxel_pressure_pilot"
OUT_REPORT = PAPER_DIR / "notes/stage_report_voxel_pressure_pilot_2026-06-09.md"


def configure_matplotlib() -> None:
    """Configure compact journal-style plotting."""
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


def axial_conductance_from_blockage(shape: tuple[int, int, int], x_centers: np.ndarray, blockage: np.ndarray, exponent: float) -> np.ndarray:
    """Map an axial blockage profile to a 3D conductance scaling field."""
    nx = shape[0]
    normalized_x = (np.arange(nx, dtype=float) + 0.5) / nx
    profile_x = x_centers / float(np.max(x_centers) + (x_centers[1] - x_centers[0]) / 2.0)
    blockage_interp = np.interp(normalized_x, profile_x, blockage, left=float(blockage[0]), right=float(blockage[-1]))
    scale = np.clip((1.0 - blockage_interp) ** exponent, 1.0e-9, 1.0)
    return np.broadcast_to(scale[:, None, None], shape).copy()


def run_pressure_pilot(exponent: float = 3.0) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run baseline and loading-state voxel pressure solves."""
    voxel, metadata = load_voxel_npz(VOXEL_PATH)
    void_mask = voxel == 0
    blockage = pd.read_csv(BLOCKAGE_PROFILE)
    baseline = solve_voxel_pressure(void_mask, axis="x")
    if baseline.status != "solved":
        raise RuntimeError(f"Baseline pressure solve failed with status={baseline.status}")

    rows = [
        {
            "case_label": "baseline",
            "debris_total_number": 0,
            "pressure_model": "voxel-network Darcy-Laplace",
            "conductance_exponent": exponent,
            "status": baseline.status,
            "through_pore_voxels": baseline.through_pore_voxels,
            "unknown_count": baseline.unknown_count,
            "conductance": baseline.conductance,
            "relative_conductance": 1.0,
            "relative_resistance": 1.0,
            "conductance_loss": 0.0,
            "max_blockage_ratio": 0.0,
            "mean_blockage_ratio": 0.0,
            "not_cfd": True,
            "not_lbm": True,
            "evidence_boundary": "voxel-network pressure pilot; not CFD/LBM and not pressure-calibrated Ib",
        }
    ]
    profiles = [
        pd.DataFrame(
            {
                "case_label": "baseline",
                "debris_total_number": 0,
                "x_index": np.arange(voxel.shape[0], dtype=int),
                "x_over_L": (np.arange(voxel.shape[0], dtype=float) + 0.5) / voxel.shape[0],
                "mean_pressure": pressure_profile(baseline, axis="x"),
            }
        )
    ]
    for n_debris, group in blockage.groupby("debris_total_number"):
        group = group.sort_values("x_center")
        conductance = axial_conductance_from_blockage(
            void_mask.shape,
            group["x_center"].to_numpy(dtype=float),
            group["blockage_ratio"].to_numpy(dtype=float),
            exponent=exponent,
        )
        result = solve_voxel_pressure(void_mask, axis="x", conductance=conductance)
        rel_g = result.conductance / baseline.conductance if baseline.conductance > 0.0 else np.nan
        rows.append(
            {
                "case_label": f"N={int(n_debris)}",
                "debris_total_number": int(n_debris),
                "pressure_model": "voxel-network Darcy-Laplace",
                "conductance_exponent": exponent,
                "status": result.status,
                "through_pore_voxels": result.through_pore_voxels,
                "unknown_count": result.unknown_count,
                "conductance": result.conductance,
                "relative_conductance": rel_g,
                "relative_resistance": 1.0 / rel_g if rel_g > 0.0 else np.inf,
                "conductance_loss": 1.0 - rel_g,
                "max_blockage_ratio": float(group["blockage_ratio"].max()),
                "mean_blockage_ratio": float(group["blockage_ratio"].mean()),
                "not_cfd": True,
                "not_lbm": True,
                "evidence_boundary": "voxel-network pressure pilot; not CFD/LBM and not pressure-calibrated Ib",
            }
        )
        profiles.append(
            pd.DataFrame(
                {
                    "case_label": f"N={int(n_debris)}",
                    "debris_total_number": int(n_debris),
                    "x_index": np.arange(voxel.shape[0], dtype=int),
                    "x_over_L": (np.arange(voxel.shape[0], dtype=float) + 0.5) / voxel.shape[0],
                    "mean_pressure": pressure_profile(result, axis="x"),
                }
            )
        )
    table = pd.DataFrame(rows)
    profile_table = pd.concat(profiles, ignore_index=True)
    summary = {
        "voxel_path": str(VOXEL_PATH.relative_to(PROJECT_ROOT)),
        "voxel_shape": list(voxel.shape),
        "voxel_size": metadata.get("voxel_size"),
        "pressure_model": "voxel-network Darcy-Laplace",
        "conductance_exponent": exponent,
        "not_cfd": True,
        "not_lbm": True,
        "not_pressure_calibrated_Ib": True,
        "baseline_conductance": float(baseline.conductance),
        "loading_conductance_loss_min": float(table.loc[table["debris_total_number"] > 0, "conductance_loss"].min()),
        "loading_conductance_loss_max": float(table.loc[table["debris_total_number"] > 0, "conductance_loss"].max()),
    }
    OUT_TABLE.parent.mkdir(parents=True, exist_ok=True)
    OUT_TABLE.write_text(table.to_csv(index=False), encoding="utf-8")
    OUT_PROFILE.write_text(profile_table.to_csv(index=False), encoding="utf-8")
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    save_figure(table, profile_table)
    write_report(table, summary)
    return table, profile_table


def save_figure(table: pd.DataFrame, profile_table: pd.DataFrame) -> None:
    """Save the voxel pressure-pilot figure."""
    configure_matplotlib()
    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), constrained_layout=True)
    load = table[table["debris_total_number"] > 0]
    axes[0].scatter(
        load["debris_total_number"],
        load["conductance_loss"],
        s=48,
        color="#2166ac",
        edgecolor="#222222",
        linewidth=0.4,
    )
    axes[0].set_xlabel("injected debris count")
    axes[0].set_ylabel("voxel-network conductance loss")
    axes[0].ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    axes[0].grid(True, linewidth=0.35, alpha=0.35)
    axes[0].text(0.02, 0.95, "a", transform=axes[0].transAxes, va="top", ha="left", weight="bold")

    for label, group in profile_table.groupby("case_label", sort=False):
        if label == "baseline":
            axes[1].plot(group["x_over_L"], group["mean_pressure"], color="#4d4d4d", linewidth=1.4, label=label)
        else:
            axes[1].plot(group["x_over_L"], group["mean_pressure"], linewidth=1.1, label=label)
    axes[1].set_xlabel("x/L")
    axes[1].set_ylabel("mean pressure")
    axes[1].grid(True, linewidth=0.35, alpha=0.35)
    axes[1].legend(loc="best")
    axes[1].text(0.02, 0.95, "b", transform=axes[1].transAxes, va="top", ha="left", weight="bold")
    for suffix, kwargs in {".png": {"dpi": 600}, ".pdf": {}, ".svg": {}}.items():
        fig.savefig(f"{OUT_FIG}{suffix}", bbox_inches="tight", **kwargs)
    plt.close(fig)


def write_report(table: pd.DataFrame, summary: dict[str, object]) -> None:
    """Write a short stage report for the pressure pilot."""
    load = table[table["debris_total_number"] > 0]
    lines = [
        "# Stage report: voxel-network pressure pilot",
        "",
        "Date: 2026-06-09",
        "",
        "## Scope",
        "",
        "This stage solves a scalar Darcy-Laplace pressure field on the DEM-derived pore voxel network. It is a pressure-informed pilot, not CFD, not LBM, and not a pressure-calibrated clogging criterion.",
        "",
        "## Outputs",
        "",
        f"- `{OUT_TABLE.relative_to(PROJECT_ROOT)}`",
        f"- `{OUT_PROFILE.relative_to(PROJECT_ROOT)}`",
        f"- `{OUT_JSON.relative_to(PROJECT_ROOT)}`",
        f"- `{OUT_FIG.relative_to(PROJECT_ROOT)}.png/.pdf/.svg`",
        "",
        "## Key Results",
        "",
        f"- baseline conductance: {summary['baseline_conductance']:.6g}",
        f"- loading conductance-loss range: {load['conductance_loss'].min():.6e} to {load['conductance_loss'].max():.6e}",
        "",
        "## Boundary",
        "",
        "The result can support relative pressure-response reasoning for the connected pore skeleton, but it must not be described as Navier-Stokes CFD, LBM, measured pressure or pressure-calibrated Ib.",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    """Run the voxel pressure pilot."""
    table, _ = run_pressure_pilot()
    print(f"Wrote: {OUT_TABLE}")
    print(f"Wrote: {OUT_PROFILE}")
    print(f"Wrote: {OUT_JSON}")
    print(f"Wrote: {OUT_FIG}.png/.pdf/.svg")
    print(table.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
