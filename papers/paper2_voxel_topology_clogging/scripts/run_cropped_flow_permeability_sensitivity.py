#!/usr/bin/env python3
"""Test cropped-domain conductance sensitivity to blockage-conductance mapping."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from run_cropped_flow_domain_permeability import local_conductance_scale  # noqa: E402
from src.voxel.io import load_voxel_npz  # noqa: E402
from src.voxel.permeability import solve_voxel_pressure  # noqa: E402


PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
DEFAULT_CROP_MANIFEST = PAPER_DIR / "tables/paper2_cropped_flow_domain_manifest.csv"
DEFAULT_BLOCKAGE = PAPER_DIR / "tables/paper2_fig4_loading_blockage_source.csv"
OUT_TABLE = PAPER_DIR / "tables/paper2_cropped_flow_permeability_sensitivity_source.csv"
OUT_JSON = PAPER_DIR / "data/paper2_cropped_flow_permeability_sensitivity_summary.json"
OUT_FIG = PAPER_DIR / "figures/paper2_figS15_cropped_flow_permeability_sensitivity"
OUT_REPORT = PAPER_DIR / "notes/stage_report_cropped_flow_permeability_sensitivity_2026-06-10.md"


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


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crop-manifest", type=Path, default=DEFAULT_CROP_MANIFEST, help="Cropped flow-domain manifest.")
    parser.add_argument("--blockage", type=Path, default=DEFAULT_BLOCKAGE, help="Axial blockage profile CSV.")
    parser.add_argument(
        "--exponents",
        type=float,
        nargs="+",
        default=[1.0, 2.0, 3.0, 5.0, 8.0],
        help="Conductance exponents for g=(1-B)^n.",
    )
    return parser.parse_args()


def validate_exponents(exponents: list[float]) -> list[float]:
    """Validate conductance exponents and return a sorted unique list."""
    if not exponents:
        raise ValueError("At least one exponent is required.")
    values = sorted({float(value) for value in exponents})
    if any(value <= 0.0 for value in values):
        raise ValueError("All exponents must be positive.")
    return values


def run_sensitivity(
    crop_manifest: Path,
    blockage_path: Path,
    exponents: list[float],
) -> pd.DataFrame:
    """Run cropped-domain conductance solves over a set of blockage exponents."""
    exponents = validate_exponents(exponents)
    manifest = pd.read_csv(crop_manifest)
    blockage = pd.read_csv(blockage_path)
    rows = []
    for _, crop_row in manifest.iterrows():
        n_debris = int(crop_row["debris_total_number"])
        voxel, metadata = load_voxel_npz(PROJECT_ROOT / str(crop_row["voxel_npz"]))
        void = voxel == 0
        baseline = solve_voxel_pressure(void, axis="x")
        if baseline.status != "solved":
            raise RuntimeError(f"Baseline local solve failed for N={n_debris}: {baseline.status}")
        group = blockage[blockage["debris_total_number"].astype(int) == n_debris]
        if group.empty:
            raise ValueError(f"No blockage profile rows found for debris_total_number={n_debris}.")
        max_blockage = float(group["blockage_ratio"].max())
        for exponent in exponents:
            scale = local_conductance_scale(
                void.shape,
                crop_x_min=float(crop_row["x_applied_lower_m"]),
                voxel_size=float(metadata["voxel_size"]),
                blockage_profile=group,
                exponent=exponent,
            )
            loaded = solve_voxel_pressure(void, axis="x", conductance=scale)
            relative_conductance = loaded.conductance / baseline.conductance if baseline.conductance > 0.0 else np.nan
            rows.append(
                {
                    "case_label": f"N={n_debris}",
                    "debris_total_number": n_debris,
                    "conductance_mapping": "g=(1-B)^n",
                    "conductance_exponent": float(exponent),
                    "baseline_conductance": float(baseline.conductance),
                    "loaded_conductance": float(loaded.conductance),
                    "relative_conductance": float(relative_conductance),
                    "relative_resistance": float(1.0 / relative_conductance) if relative_conductance > 0.0 else np.inf,
                    "local_conductance_loss": float(1.0 - relative_conductance),
                    "max_blockage_ratio_in_profile": max_blockage,
                    "mean_scale_in_crop": float(scale.mean()),
                    "min_scale_in_crop": float(scale.min()),
                    "not_cfd": True,
                    "not_lbm": True,
                    "evidence_boundary": "exponent sensitivity of a cropped scalar voxel-network conductance proxy; not CFD/LBM and not a calibrated pressure-drop measurement",
                }
            )
    table = pd.DataFrame(rows)
    OUT_TABLE.parent.mkdir(parents=True, exist_ok=True)
    OUT_TABLE.write_text(table.to_csv(index=False), encoding="utf-8")
    summary = summarize_sensitivity(table, crop_manifest, blockage_path, exponents)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    save_figure(table)
    write_stage_report(table, exponents)
    return table


def summarize_sensitivity(
    table: pd.DataFrame,
    crop_manifest: Path,
    blockage_path: Path,
    exponents: list[float],
) -> dict[str, object]:
    """Summarize sensitivity results in JSON-friendly form."""
    grouped = table.groupby("debris_total_number")["local_conductance_loss"]
    return {
        "crop_manifest": str(crop_manifest.relative_to(PROJECT_ROOT)),
        "blockage_profile": str(blockage_path.relative_to(PROJECT_ROOT)),
        "conductance_mapping": "g=(1-B)^n",
        "conductance_exponents": exponents,
        "cases": int(table["debris_total_number"].nunique()),
        "rows": int(len(table)),
        "min_local_conductance_loss": float(table["local_conductance_loss"].min()),
        "max_local_conductance_loss": float(table["local_conductance_loss"].max()),
        "case_loss_ranges": {
            str(int(n_debris)): {
                "min": float(values.min()),
                "max": float(values.max()),
            }
            for n_debris, values in grouped
        },
        "evidence_boundary": "Cropped voxel-network conductance exponent sensitivity only; no CFD/LBM solver was run.",
    }


def save_figure(table: pd.DataFrame) -> None:
    """Save the conductance-exponent sensitivity figure."""
    configure_matplotlib()
    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), constrained_layout=True)

    pivot = table.pivot(index="debris_total_number", columns="conductance_exponent", values="local_conductance_loss")
    image_values = np.log10(np.clip(pivot.to_numpy(dtype=float), 1.0e-12, None))
    im = axes[0].imshow(image_values, aspect="auto", cmap="viridis")
    axes[0].set_xticks(np.arange(len(pivot.columns)), [f"{value:g}" for value in pivot.columns])
    axes[0].set_yticks(np.arange(len(pivot.index)), [str(int(value)) for value in pivot.index])
    axes[0].set_xlabel("conductance exponent n")
    axes[0].set_ylabel("injected debris count")
    cbar = fig.colorbar(im, ax=axes[0], fraction=0.05, pad=0.03)
    cbar.set_label(r"$\log_{10}$ conductance loss")
    axes[0].text(0.02, 0.95, "a", transform=axes[0].transAxes, va="top", ha="left", weight="bold", color="white")

    summary = (
        table.groupby("debris_total_number")["local_conductance_loss"]
        .agg(["min", "max"])
        .reset_index()
        .sort_values("debris_total_number")
    )
    y = np.arange(len(summary))
    x_mid = np.sqrt(summary["min"].to_numpy(dtype=float) * summary["max"].to_numpy(dtype=float))
    xerr = np.vstack([x_mid - summary["min"].to_numpy(dtype=float), summary["max"].to_numpy(dtype=float) - x_mid])
    axes[1].errorbar(x_mid, y, xerr=xerr, fmt="o", color="#2166ac", ecolor="#67a9cf", capsize=3, markersize=4)
    axes[1].set_xscale("log")
    axes[1].set_yticks(y, [str(int(value)) for value in summary["debris_total_number"]])
    axes[1].set_xlabel("loss range over exponent sweep")
    axes[1].set_ylabel("injected debris count")
    axes[1].grid(True, axis="x", linewidth=0.35, alpha=0.35)
    axes[1].text(0.02, 0.95, "b", transform=axes[1].transAxes, va="top", ha="left", weight="bold")

    for suffix, kwargs in {".png": {"dpi": 600}, ".pdf": {}, ".svg": {}}.items():
        fig.savefig(f"{OUT_FIG}{suffix}", bbox_inches="tight", **kwargs)
    plt.close(fig)


def write_stage_report(table: pd.DataFrame, exponents: list[float]) -> None:
    """Write a concise stage report for the exponent sensitivity check."""
    lines = [
        "# Stage report: cropped flow-domain conductance-exponent sensitivity",
        "",
        "Date: 2026-06-10",
        "",
        "## Scope",
        "",
        "This stage tests whether the cropped voxel-network conductance conclusion depends strongly on the exponent in `g=(1-B)^n`. It is a proxy robustness check only; it is not CFD, not LBM and not pressure calibration.",
        "",
        "## Files Added or Updated",
        "",
        f"- `{Path(__file__).relative_to(PROJECT_ROOT)}`",
        f"- `{OUT_TABLE.relative_to(PROJECT_ROOT)}`",
        f"- `{OUT_JSON.relative_to(PROJECT_ROOT)}`",
        f"- `{OUT_FIG.relative_to(PROJECT_ROOT)}.png/.pdf/.svg`",
        "",
        "## Key Results",
        "",
        f"- Exponents tested: {', '.join(f'{value:g}' for value in exponents)}.",
        f"- Minimum local conductance loss: {float(table['local_conductance_loss'].min()):.6e}.",
        f"- Maximum local conductance loss: {float(table['local_conductance_loss'].max()):.6e}.",
        "",
        "## How To Run",
        "",
        "```bash",
        "python3 papers/paper2_voxel_topology_clogging/scripts/run_cropped_flow_permeability_sensitivity.py",
        "```",
        "",
        "## Boundary",
        "",
        "Use this result only to support robustness of the pre-clogging structural interpretation. Do not cite it as Navier-Stokes CFD, LBM, measured pressure or pressure-calibrated Ib.",
    ]
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    """Run the cropped-domain conductance-exponent sensitivity check."""
    args = parse_args()
    table = run_sensitivity(args.crop_manifest, args.blockage, args.exponents)
    print(OUT_TABLE)
    print(
        json.dumps(
            {
                "rows": int(len(table)),
                "max_local_loss": float(table["local_conductance_loss"].max()),
                "exponents": sorted(float(value) for value in table["conductance_exponent"].unique()),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
