#!/usr/bin/env python3
"""Quantify early tail migration from the explicit localized-release case."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
TABLE_DIR = PAPER_DIR / "tables"
FIG_DIR = PAPER_DIR / "figures"
DATA_DIR = PAPER_DIR / "data"

INPUT_TABLE = TABLE_DIR / "explicit_localized_release_early_timeseries.csv"
OUT_TABLE = TABLE_DIR / "explicit_localized_release_mechanism_metrics.csv"
OUT_JSON = DATA_DIR / "explicit_localized_release_mechanism_metrics.json"
OUT_FIG = FIG_DIR / "paper2_figS7_localized_release_tail_mechanism"

BED_LENGTH_M = 0.045
SOURCE_X_MIN = 0.012
SOURCE_X_MAX = 0.018


def configure_matplotlib() -> None:
    """Configure compact, colorblind-safe Matplotlib defaults."""
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


def linear_fit(x: np.ndarray, y: np.ndarray) -> dict[str, float]:
    """Return slope, intercept and R2 for a least-squares line."""
    if x.size < 2:
        raise ValueError("At least two points are required for a linear fit.")
    coeff = np.polyfit(x, y, 1)
    y_fit = np.polyval(coeff, x)
    ss_res = float(np.sum((y - y_fit) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 if ss_tot == 0.0 else 1.0 - ss_res / ss_tot
    return {"slope": float(coeff[0]), "intercept": float(coeff[1]), "r2": r2}


def fit_column(table: pd.DataFrame, column: str, t_min_s: float | None = None) -> dict[str, float]:
    """Fit one time-dependent column over all or late-time rows."""
    subset = table.copy()
    if t_min_s is not None:
        subset = subset[subset["time_s"] >= t_min_s]
    if subset.empty:
        raise ValueError(f"No rows remain for {column} after applying t_min_s={t_min_s}.")
    return linear_fit(subset["time_s"].to_numpy(float), subset[column].to_numpy(float))


def compute_interval_rates(table: pd.DataFrame) -> pd.DataFrame:
    """Compute interval-wise release and downstream growth rates."""
    sorted_table = table.sort_values("time_s").copy()
    dt = sorted_table["time_s"].diff()
    out = pd.DataFrame(
        {
            "step": sorted_table["step"],
            "time_s": sorted_table["time_s"],
            "interval_dt_s": dt,
            "source_loss_rate_particles_s": -sorted_table["retained_in_source_slab_count"].diff() / dt,
            "downstream_growth_rate_particles_s": sorted_table["downstream_of_source_count"].diff() / dt,
            "q99_speed_m_s": (sorted_table["x_q99_over_L"].diff() * BED_LENGTH_M) / dt,
            "max_tail_speed_m_s": (sorted_table["x_max_over_L"].diff() * BED_LENGTH_M) / dt,
        }
    )
    return out.replace([np.inf, -np.inf], np.nan)


def summarize_mechanism(table: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Summarize source retention and tail migration mechanisms."""
    if table.empty:
        raise ValueError("Localized-release timeseries is empty.")
    final = table.sort_values("time_s").iloc[-1]
    n_debris = float(final["debris_count"])
    interval = compute_interval_rates(table)

    metrics_rows = []
    fits: dict[str, dict[str, float]] = {}
    fit_specs = {
        "source_count_all": ("retained_in_source_slab_count", None),
        "source_count_late_5_10ms": ("retained_in_source_slab_count", 0.005),
        "downstream_count_all": ("downstream_of_source_count", None),
        "downstream_count_late_5_10ms": ("downstream_of_source_count", 0.005),
        "x_mean_all_m_s": ("x_mean_over_L", None),
        "x_q99_all_m_s": ("x_q99_over_L", None),
        "x_max_late_5_10ms_m_s": ("x_max_over_L", 0.005),
    }
    for name, (column, tmin) in fit_specs.items():
        fit = fit_column(table, column, tmin)
        if column.startswith("x_"):
            fit["slope"] *= BED_LENGTH_M
            fit["intercept"] *= BED_LENGTH_M
        fits[name] = fit
        metrics_rows.append(
            {
                "metric": name,
                "slope": fit["slope"],
                "intercept": fit["intercept"],
                "r2": fit["r2"],
                "t_min_s": np.nan if tmin is None else tmin,
            }
        )

    late = interval[interval["time_s"] >= 0.005]
    summary = {
        "final_step": int(final["step"]),
        "final_time_s": float(final["time_s"]),
        "final_retained_fraction": float(final["retained_in_source_slab_count"] / n_debris),
        "final_downstream_fraction": float(final["downstream_of_source_count"] / n_debris),
        "final_outlet_fraction": float(final["btc_approx_x_ge_L"] / n_debris),
        "final_x_mean_over_L": float(final["x_mean_over_L"]),
        "final_x_q99_over_L": float(final["x_q99_over_L"]),
        "final_x_max_over_L": float(final["x_max_over_L"]),
        "source_loss_rate_all_particles_s": float(-fits["source_count_all"]["slope"]),
        "source_loss_rate_late_5_10ms_particles_s": float(-fits["source_count_late_5_10ms"]["slope"]),
        "downstream_growth_rate_all_particles_s": float(fits["downstream_count_all"]["slope"]),
        "downstream_growth_rate_late_5_10ms_particles_s": float(fits["downstream_count_late_5_10ms"]["slope"]),
        "mean_cloud_speed_all_m_s": float(fits["x_mean_all_m_s"]["slope"]),
        "q99_tail_speed_all_m_s": float(fits["x_q99_all_m_s"]["slope"]),
        "max_tail_speed_late_5_10ms_m_s": float(fits["x_max_late_5_10ms_m_s"]["slope"]),
        "median_late_downstream_growth_rate_particles_s": float(late["downstream_growth_rate_particles_s"].median()),
        "median_late_q99_speed_m_s": float(late["q99_speed_m_s"].median()),
        "interpretation": (
            "The localized internal source remains retention dominated: the retained fraction is high, "
            "the downstream fraction grows slowly, and no outlet breakthrough occurs by 10 ms."
        ),
    }
    metrics = pd.DataFrame(metrics_rows)
    return metrics, summary


def save_figure(table: pd.DataFrame, interval: pd.DataFrame) -> None:
    """Save a compact multi-panel mechanism figure."""
    configure_matplotlib()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    time_ms = table["time_s"] * 1000.0
    n_debris = table["debris_count"].iloc[-1]

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 4.4), constrained_layout=True)
    ax = axes[0, 0]
    ax.plot(time_ms, table["retained_in_source_slab_count"] / n_debris, color="#00876c", marker="o", ms=3, lw=1.25)
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("source-retained fraction")
    ax.set_ylim(0.86, 1.01)

    ax = axes[0, 1]
    ax.plot(time_ms, table["downstream_of_source_count"] / n_debris, color="#d95f02", marker="s", ms=3, lw=1.25, label="downstream")
    ax.plot(time_ms, table["btc_approx_x_ge_L"] / n_debris, color="0.2", marker="^", ms=3, lw=1.25, label="outlet")
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("released fraction")
    ax.set_ylim(-0.005, 0.12)
    ax.legend(loc="upper left")

    ax = axes[1, 0]
    ax.plot(time_ms, table["x_mean_over_L"], color="#2f5d8c", marker="o", ms=3, lw=1.25, label="mean")
    ax.plot(time_ms, table["x_q99_over_L"], color="#ef5675", marker="^", ms=3, lw=1.25, label="q99")
    ax.plot(time_ms, table["x_max_over_L"], color="#7a5195", marker="D", ms=2.8, lw=1.0, label="max")
    ax.axhspan(SOURCE_X_MIN / BED_LENGTH_M, SOURCE_X_MAX / BED_LENGTH_M, color="0.9", zorder=-1)
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("axial position, x/L")
    ax.set_ylim(0.25, 0.9)
    ax.legend(loc="upper left")

    ax = axes[1, 1]
    plot_interval = interval.dropna(subset=["downstream_growth_rate_particles_s"])
    ax.scatter(
        plot_interval["time_s"] * 1000.0,
        plot_interval["downstream_growth_rate_particles_s"] / 1000.0,
        s=18,
        color="#d95f02",
        edgecolor="white",
        linewidth=0.3,
    )
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("downstream growth\n(10$^3$ particles s$^{-1}$)")
    ax.set_ylim(bottom=0)

    for label, ax in zip(("a", "b", "c", "d"), axes.ravel()):
        ax.text(0.02, 0.96, label, transform=ax.transAxes, ha="left", va="top", fontweight="bold")

    for suffix in ("png", "pdf", "svg"):
        fig.savefig(f"{OUT_FIG}.{suffix}", dpi=300)
    plt.close(fig)


def main() -> int:
    """Run the localized-release mechanism analysis."""
    if not INPUT_TABLE.exists():
        raise FileNotFoundError(f"Missing input timeseries: {INPUT_TABLE}")
    table = pd.read_csv(INPUT_TABLE).sort_values("time_s")
    interval = compute_interval_rates(table)
    metrics, summary = summarize_mechanism(table)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(OUT_TABLE, index=False)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    save_figure(table, interval)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
