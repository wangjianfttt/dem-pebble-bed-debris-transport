#!/usr/bin/env python3
"""Test reduced pressure sensitivity to 3D hydraulic-resistance amplification."""

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
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.voxel.io import load_voxel_npz  # noqa: E402
from src.voxel.permeability import conductance_from_resistance_multiplier, solve_voxel_pressure  # noqa: E402


PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
DEFAULT_CROP_MANIFEST = PAPER_DIR / "tables/paper2_cropped_flow_domain_manifest.csv"
OUT_TABLE = PAPER_DIR / "tables/paper2_3d_resistance_amplification_sensitivity_source.csv"
OUT_JSON = PAPER_DIR / "data/paper2_3d_resistance_amplification_sensitivity_summary.json"
OUT_FIG = PAPER_DIR / "figures/paper2_figS22_3d_resistance_amplification_sensitivity"
OUT_REPORT = PAPER_DIR / "notes/stage_report_3d_resistance_amplification_sensitivity_2026-06-10.md"


def configure_matplotlib() -> None:
    """Configure compact publication-style plotting."""
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
    parser.add_argument(
        "--amplification-factors",
        type=float,
        nargs="+",
        default=[1.0, 3.0, 10.0, 30.0, 100.0, 300.0],
        help="Factors applied to the excess resistance, R_eff = 1 + factor * (R - 1).",
    )
    return parser.parse_args()


def validate_amplification_factors(values: list[float]) -> list[float]:
    """Validate and return sorted unique positive amplification factors."""
    if not values:
        raise ValueError("At least one amplification factor is required.")
    factors = sorted({float(value) for value in values})
    if any(value <= 0.0 for value in factors):
        raise ValueError("Amplification factors must be positive.")
    return factors


def amplify_resistance_multiplier(resistance: np.ndarray, factor: float, void_mask: np.ndarray | None = None) -> np.ndarray:
    """Amplify only the debris-induced excess resistance above the baseline.

    The mapping preserves a clean baseline: a voxel with `R=1` remains `R=1`
    for every factor, while local debris-induced excess resistance is scaled as
    `R_eff = 1 + factor * (R - 1)`.
    """
    if factor <= 0.0:
        raise ValueError("factor must be positive.")
    if not isinstance(resistance, np.ndarray):
        raise TypeError("resistance must be a numpy array.")
    if resistance.ndim != 3:
        raise ValueError("resistance must be 3D.")
    mask = np.ones(resistance.shape, dtype=bool) if void_mask is None else np.asarray(void_mask, dtype=bool)
    if mask.shape != resistance.shape:
        raise ValueError("void_mask must have the same shape as resistance.")
    if np.any(~np.isfinite(resistance[mask])):
        raise ValueError("resistance contains non-finite pore values.")
    if np.any(resistance[mask] <= 0.0):
        raise ValueError("resistance must be positive on pore voxels.")
    amplified = 1.0 + factor * (resistance.astype(float, copy=False) - 1.0)
    amplified[~mask] = 1.0
    return np.clip(amplified, 1.0e-9, None)


def run_sensitivity(crop_manifest: Path, amplification_factors: list[float]) -> pd.DataFrame:
    """Run cropped-domain pressure solves over 3D resistance amplification factors."""
    factors = validate_amplification_factors(amplification_factors)
    manifest = pd.read_csv(crop_manifest)
    required = {"debris_total_number", "voxel_npz", "hydraulic_resistance_multiplier_field_npy"}
    missing = sorted(required.difference(manifest.columns))
    if missing:
        raise ValueError(f"crop manifest missing columns: {missing}")

    rows: list[dict[str, object]] = []
    for _, crop_row in manifest.iterrows():
        n_debris = int(crop_row["debris_total_number"])
        voxel, _metadata = load_voxel_npz(PROJECT_ROOT / str(crop_row["voxel_npz"]))
        void = voxel == 0
        resistance_path = PROJECT_ROOT / str(crop_row["hydraulic_resistance_multiplier_field_npy"])
        if not resistance_path.exists():
            raise FileNotFoundError(resistance_path)
        resistance = np.load(resistance_path)
        if resistance.shape != void.shape:
            raise ValueError(f"Resistance shape {resistance.shape} does not match voxel shape {void.shape}.")

        baseline = solve_voxel_pressure(void, axis="x")
        if baseline.status != "solved":
            raise RuntimeError(f"Baseline local solve failed for N={n_debris}: {baseline.status}")
        pore_excess = resistance[void] - 1.0
        for factor in factors:
            amplified = amplify_resistance_multiplier(resistance, factor, void_mask=void)
            conductance = conductance_from_resistance_multiplier(amplified, void_mask=void)
            loaded = solve_voxel_pressure(void, axis="x", conductance=conductance)
            relative_conductance = loaded.conductance / baseline.conductance if baseline.conductance > 0.0 else np.nan
            local_loss = 1.0 - relative_conductance
            rows.append(
                {
                    "case_label": f"N={n_debris}",
                    "debris_total_number": n_debris,
                    "resistance_mapping": "R_eff=1+factor*(R-1); g=1/R_eff",
                    "amplification_factor": float(factor),
                    "baseline_conductance": float(baseline.conductance),
                    "loaded_conductance": float(loaded.conductance),
                    "relative_conductance": float(relative_conductance),
                    "relative_resistance": float(1.0 / relative_conductance) if relative_conductance > 0.0 else np.inf,
                    "local_conductance_loss": float(local_loss),
                    "mean_excess_resistance": float(np.mean(pore_excess)),
                    "max_excess_resistance": float(np.max(pore_excess)),
                    "mean_amplified_resistance": float(np.mean(amplified[void])),
                    "max_amplified_resistance": float(np.max(amplified[void])),
                    "min_conductance": float(np.min(conductance[void])),
                    "mean_conductance": float(np.mean(conductance[void])),
                    "hydraulic_resistance_field": str(Path(crop_row["hydraulic_resistance_multiplier_field_npy"])),
                    "not_cfd": True,
                    "not_lbm": True,
                    "evidence_boundary": "3D hydraulic-resistance amplification sensitivity in a scalar voxel-network Darcy-Laplace model; not CFD/LBM and not a calibrated pressure-drop measurement",
                }
            )
    table = pd.DataFrame(rows)
    OUT_TABLE.parent.mkdir(parents=True, exist_ok=True)
    OUT_TABLE.write_text(table.to_csv(index=False), encoding="utf-8")
    summary = summarize(table, crop_manifest, factors)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    save_figure(table)
    write_stage_report(table, factors)
    return table


def summarize(table: pd.DataFrame, crop_manifest: Path, factors: list[float]) -> dict[str, object]:
    """Summarize sensitivity outputs in JSON-friendly form."""
    grouped = table.groupby("debris_total_number")["local_conductance_loss"]
    return {
        "crop_manifest": str(crop_manifest.relative_to(PROJECT_ROOT)),
        "resistance_mapping": "R_eff=1+factor*(R-1); g=1/R_eff",
        "amplification_factors": factors,
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
        "evidence_boundary": "Reduced 3D resistance sensitivity only; no CFD/LBM solver was run.",
    }


def save_figure(table: pd.DataFrame) -> None:
    """Save a compact sensitivity figure."""
    configure_matplotlib()
    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), constrained_layout=True)

    pivot = table.pivot(index="debris_total_number", columns="amplification_factor", values="local_conductance_loss")
    values = np.log10(np.clip(pivot.to_numpy(dtype=float), 1.0e-12, None))
    im = axes[0].imshow(values, aspect="auto", cmap="cividis")
    axes[0].set_xticks(np.arange(len(pivot.columns)), [f"{value:g}" for value in pivot.columns], rotation=35, ha="right")
    axes[0].set_yticks(np.arange(len(pivot.index)), [str(int(value)) for value in pivot.index])
    axes[0].set_xlabel("resistance amplification factor")
    axes[0].set_ylabel("injected debris count")
    cbar = fig.colorbar(im, ax=axes[0], fraction=0.05, pad=0.03)
    cbar.set_label(r"$\log_{10}$ local conductance loss")
    axes[0].text(0.02, 0.95, "a", transform=axes[0].transAxes, va="top", ha="left", weight="bold", color="white")

    summary = (
        table.groupby("debris_total_number")["local_conductance_loss"]
        .agg(["min", "max"])
        .reset_index()
        .sort_values("debris_total_number")
    )
    y = np.arange(len(summary))
    xmin = np.clip(summary["min"].to_numpy(dtype=float), 1.0e-12, None)
    xmax = np.clip(summary["max"].to_numpy(dtype=float), 1.0e-12, None)
    xmid = np.sqrt(xmin * xmax)
    xerr = np.vstack([xmid - xmin, xmax - xmid])
    axes[1].errorbar(xmid, y, xerr=xerr, fmt="o", color="#0072b2", ecolor="#56b4e9", capsize=3, markersize=4)
    axes[1].set_xscale("log")
    axes[1].set_yticks(y, [str(int(value)) for value in summary["debris_total_number"]])
    axes[1].set_xlabel("loss range over factor sweep")
    axes[1].set_ylabel("injected debris count")
    axes[1].grid(True, axis="x", linewidth=0.35, alpha=0.35)
    axes[1].text(0.02, 0.95, "b", transform=axes[1].transAxes, va="top", ha="left", weight="bold")

    for suffix, kwargs in {".png": {"dpi": 600}, ".pdf": {}, ".svg": {}}.items():
        fig.savefig(f"{OUT_FIG}{suffix}", bbox_inches="tight", **kwargs)
    plt.close(fig)


def write_stage_report(table: pd.DataFrame, factors: list[float]) -> None:
    """Write a stage report for the 3D resistance amplification sensitivity."""
    lines = [
        "# Stage report: 3D hydraulic-resistance amplification sensitivity",
        "",
        "Date: 2026-06-10",
        "",
        "## Scope",
        "",
        "This stage tests whether the reduced pressure-response conclusion depends on the amplitude assigned to the debris-induced hydraulic-resistance field. The model consumes the full 3D resistance field and applies `R_eff=1+factor*(R-1)`, followed by `g=1/R_eff` in the voxel-network Darcy-Laplace solve.",
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
        f"- Amplification factors tested: {', '.join(f'{value:g}' for value in factors)}.",
        f"- Minimum local conductance loss: {float(table['local_conductance_loss'].min()):.6e}.",
        f"- Maximum local conductance loss: {float(table['local_conductance_loss'].max()):.6e}.",
        "",
        "## Case Ranges",
        "",
    ]
    grouped = table.groupby("debris_total_number")["local_conductance_loss"].agg(["min", "max"]).reset_index()
    for _, row in grouped.iterrows():
        lines.append(
            f"- N={int(row['debris_total_number'])}: {float(row['min']):.6e} to {float(row['max']):.6e}"
        )
    lines.extend(
        [
            "",
            "## How To Run",
            "",
            "```bash",
            "python papers/paper2_voxel_topology_clogging/scripts/run_3d_resistance_amplification_sensitivity.py",
            "```",
            "",
            "## Boundary",
            "",
            "This is a reduced scalar pressure-response sensitivity test. It can support mechanism discussion about robustness of local resistance amplification, but it is not Navier-Stokes CFD, not LBM, not measured pressure and not pressure-calibrated `Ib`.",
        ]
    )
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    """Run the 3D resistance amplification sensitivity workflow."""
    args = parse_args()
    table = run_sensitivity(args.crop_manifest, args.amplification_factors)
    print(OUT_TABLE)
    print(
        json.dumps(
            {
                "rows": int(len(table)),
                "cases": int(table["debris_total_number"].nunique()),
                "max_local_loss": float(table["local_conductance_loss"].max()),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
