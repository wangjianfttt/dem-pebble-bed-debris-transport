#!/usr/bin/env python3
"""Compute an Ergun pressure-gradient proxy for Paper 2 loading cases."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models.ergun import ergun_pressure_gradient


PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
DATA_DIR = PAPER_DIR / "data"
TABLE_DIR = PAPER_DIR / "tables"
FIG_DIR = PAPER_DIR / "figures"
NOTE_DIR = PAPER_DIR / "notes"

BASE_CONFIG = PROJECT_ROOT / "configs" / "base_li4sio4_1mm_10k_axial_cuboid.yaml"
BASELINE_TOPOLOGY = DATA_DIR / "baseline_topology_metrics_effective.json"
LOADING_SUMMARY = TABLE_DIR / "paper2_fig4_loading_summary_source.csv"
LOADING_BLOCKAGE = TABLE_DIR / "paper2_fig4_loading_blockage_source.csv"
OUT_TABLE = TABLE_DIR / "paper2_pressure_proxy_source.csv"
OUT_FIG = FIG_DIR / "paper2_figS3_ergun_pressure_proxy"
OUT_NOTE = NOTE_DIR / "stage_report_pressure_proxy_2026-06-09.md"


def configure_matplotlib() -> None:
    """Configure a compact journal-style plot."""
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


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML mapping."""
    if not path.exists():
        raise FileNotFoundError(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return data


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON mapping."""
    if not path.exists():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON mapping in {path}")
    return data


def effective_porosity_after_blockage(epsilon0: float, blockage_ratio) -> pd.Series:
    """Convert debris-volume/pore-volume blockage ratio to remaining porosity."""
    eps = float(epsilon0) * (1.0 - pd.Series(blockage_ratio, dtype=float))
    return eps.clip(lower=1.0e-6, upper=0.999999)


def pressure_proxy_table() -> pd.DataFrame:
    """Compute Ergun pressure-gradient proxies for the loading cases."""
    config = load_yaml(BASE_CONFIG)
    baseline = load_json(BASELINE_TOPOLOGY)
    loading = pd.read_csv(LOADING_SUMMARY)
    blockage = pd.read_csv(LOADING_BLOCKAGE)

    epsilon0 = float(baseline["porosity"])
    dp = float(config["dp"])
    mu = float(config["mu_g"])
    rho = float(config["rho_g"])
    length = float(baseline["metadata"]["domain"]["Lx"])

    rows: list[dict[str, Any]] = []
    for item in loading.sort_values("debris_total_number").to_dict(orient="records"):
        n_debris = int(item["debris_total_number"])
        case_profile = blockage[blockage["debris_total_number"].astype(int) == n_debris].copy()
        if case_profile.empty:
            raise ValueError(f"No blockage profile found for debris_total_number={n_debris}")
        u = float(item["gas_velocity"])
        baseline_gradient = float(ergun_pressure_gradient(epsilon0, dp, mu, rho, u))
        eps_profile = effective_porosity_after_blockage(epsilon0, case_profile["blockage_ratio"])
        profile_gradient = ergun_pressure_gradient(eps_profile.to_numpy(dtype=float), dp, mu, rho, u)
        mean_gradient = float(profile_gradient.mean())
        peak_blockage = float(case_profile["blockage_ratio"].max())
        peak_epsilon = float(effective_porosity_after_blockage(epsilon0, [peak_blockage]).iloc[0])
        peak_gradient = float(ergun_pressure_gradient(peak_epsilon, dp, mu, rho, u))
        rows.append(
            {
                "debris_total_number": n_debris,
                "gas_velocity_m_s": u,
                "baseline_porosity": epsilon0,
                "baseline_pressure_gradient_pa_m": baseline_gradient,
                "profile_mean_pressure_gradient_pa_m": mean_gradient,
                "peak_local_pressure_gradient_pa_m": peak_gradient,
                "baseline_pressure_drop_pa": baseline_gradient * length,
                "profile_mean_pressure_drop_pa": mean_gradient * length,
                "peak_local_equivalent_pressure_drop_pa": peak_gradient * length,
                "profile_pressure_increase_ratio": max(0.0, (mean_gradient - baseline_gradient) / baseline_gradient),
                "peak_local_pressure_increase_ratio": max(0.0, (peak_gradient - baseline_gradient) / baseline_gradient),
                "subvoxel_mean_blockage_ratio": float(case_profile["blockage_ratio"].mean()),
                "subvoxel_max_blockage_ratio": peak_blockage,
                "pressure_proxy_type": "Ergun with epsilon_t = epsilon0 * (1 - B)",
                "pressure_proxy_not_cfd": True,
            }
        )
    return pd.DataFrame(rows)


def save_pressure_proxy_figure(table: pd.DataFrame) -> None:
    """Save a compact pressure-proxy figure."""
    configure_matplotlib()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), constrained_layout=True)
    x = table["debris_total_number"].to_numpy(dtype=float)
    axes[0].scatter(
        x,
        table["profile_pressure_increase_ratio"],
        s=48,
        color="#2166ac",
        edgecolor="#222222",
        linewidth=0.4,
        label="profile mean",
    )
    axes[0].scatter(
        x,
        table["peak_local_pressure_increase_ratio"],
        s=46,
        marker="s",
        facecolor="white",
        edgecolor="#b2182b",
        linewidth=1.0,
        label="peak local",
    )
    axes[0].set_xlabel("injected debris count")
    axes[0].set_ylabel("pressure-increase ratio")
    axes[0].set_yscale("log")
    axes[0].grid(True, linewidth=0.35, alpha=0.35)
    axes[0].legend(loc="best")
    axes[0].text(0.02, 0.95, "a", transform=axes[0].transAxes, va="top", ha="left", weight="bold")

    axes[1].scatter(
        table["subvoxel_max_blockage_ratio"],
        table["peak_local_pressure_increase_ratio"],
        s=48,
        color="#4d4d4d",
        edgecolor="#222222",
        linewidth=0.4,
    )
    axes[1].set_xlabel("max local blockage ratio")
    axes[1].set_ylabel("peak pressure-increase ratio")
    axes[1].ticklabel_format(axis="x", style="sci", scilimits=(0, 0))
    axes[1].set_yscale("log")
    axes[1].grid(True, linewidth=0.35, alpha=0.35)
    axes[1].text(0.02, 0.95, "b", transform=axes[1].transAxes, va="top", ha="left", weight="bold")

    for suffix, kwargs in {".png": {"dpi": 600}, ".pdf": {}, ".svg": {}}.items():
        fig.savefig(f"{OUT_FIG}{suffix}", bbox_inches="tight", **kwargs)
    plt.close(fig)


def write_stage_report(table: pd.DataFrame) -> None:
    """Write a stage report for the pressure proxy."""
    NOTE_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Stage Report: Ergun Pressure-Gradient Proxy",
        "",
        "Date: 2026-06-09",
        "",
        "## Scope",
        "",
        "This stage estimates a pressure-gradient proxy from the Paper 2 loading blockage profiles using the traditional Ergun relation. The calculation is not CFD and is not experimental pressure validation.",
        "",
        "## Outputs",
        "",
        f"- `{OUT_TABLE.relative_to(PROJECT_ROOT)}`",
        f"- `{OUT_FIG.relative_to(PROJECT_ROOT)}.png`",
        f"- `{OUT_FIG.relative_to(PROJECT_ROOT)}.pdf`",
        f"- `{OUT_FIG.relative_to(PROJECT_ROOT)}.svg`",
        "",
        "## Key Results",
        "",
        f"- baseline pressure gradient: {table['baseline_pressure_gradient_pa_m'].iloc[0]:.6g} Pa/m",
        f"- profile-mean pressure-increase ratio range: {table['profile_pressure_increase_ratio'].min():.6e} to {table['profile_pressure_increase_ratio'].max():.6e}",
        f"- peak-local pressure-increase ratio range: {table['peak_local_pressure_increase_ratio'].min():.6e} to {table['peak_local_pressure_increase_ratio'].max():.6e}",
        "",
        "## Interpretation",
        "",
        "The Ergun proxy shows that the present sub-voxel debris loading produces only a small pressure-response estimate, consistent with the pre-clogging interpretation. The result should be used as a hydraulic-consequence proxy, not as a pressure-calibrated clogging criterion.",
    ]
    OUT_NOTE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    """Run the pressure-proxy workflow."""
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    table = pressure_proxy_table()
    table.to_csv(OUT_TABLE, index=False)
    save_pressure_proxy_figure(table)
    write_stage_report(table)
    print(f"Wrote: {OUT_TABLE}")
    print(f"Wrote: {OUT_FIG}.png/.pdf/.svg")
    print(f"Wrote: {OUT_NOTE}")
    print(table.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
