#!/usr/bin/env python3
"""Plot the completed 907 downstream localized-release tail-capture mechanism."""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
TABLE_DIR = PAPER_DIR / "tables"
FIG_DIR = PAPER_DIR / "figures"

TIMESERIES = TABLE_DIR / "explicit_localized_production_timeseries.csv"
SUMMARY = TABLE_DIR / "explicit_localized_production_summary.csv"
SOURCE_OUT = TABLE_DIR / "paper2_figS9_907_tail_capture_source.csv"
FIG_STEM = "paper2_figS9_907_tail_capture_mechanism"
JOB_ID = "907_downstream_source_dt5e9_to_10ms"


def configure_matplotlib() -> None:
    """Configure a compact journal-style Matplotlib theme."""
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


def panel_label(ax: plt.Axes, label: str) -> None:
    """Place a compact panel label in axes coordinates."""
    ax.text(-0.12, 1.05, label, transform=ax.transAxes, weight="bold", fontsize=9, va="top")


def load_907_timeseries() -> tuple[pd.DataFrame, pd.Series]:
    """Load and validate the completed 907 production time series."""
    if not TIMESERIES.exists():
        raise FileNotFoundError(f"Missing production timeseries: {TIMESERIES}")
    if not SUMMARY.exists():
        raise FileNotFoundError(f"Missing production summary: {SUMMARY}")
    ts = pd.read_csv(TIMESERIES)
    summary = pd.read_csv(SUMMARY)
    required = {
        "job_id",
        "step",
        "time_s",
        "source_fraction",
        "downstream_fraction",
        "outlet_fraction",
        "x_mean_over_L",
        "x_q99_over_L",
        "x_max_over_L",
        "max_abs_velocity_m_s",
    }
    missing = sorted(required.difference(ts.columns))
    if missing:
        raise ValueError(f"Timeseries missing columns: {missing}")
    job_ts = ts[ts["job_id"].astype(str) == JOB_ID].sort_values("time_s").copy()
    if job_ts.empty:
        raise ValueError(f"No rows found for {JOB_ID}")
    job_summary = summary[summary["job_id"].astype(str) == JOB_ID]
    if job_summary.empty:
        raise ValueError(f"No summary row found for {JOB_ID}")
    if not bool(job_summary.iloc[-1].get("target_time_reached", False)):
        raise ValueError("907 target time has not been reached in the production summary.")
    return job_ts, job_summary.iloc[-1]


def write_source_table(ts: pd.DataFrame) -> None:
    """Save the exact 907 source data used for Fig. S9."""
    cols = [
        "job_id",
        "step",
        "time_s",
        "source_fraction",
        "downstream_fraction",
        "outlet_fraction",
        "x_mean_over_L",
        "x_q99_over_L",
        "x_max_over_L",
        "max_abs_velocity_m_s",
    ]
    SOURCE_OUT.parent.mkdir(parents=True, exist_ok=True)
    ts[cols].to_csv(SOURCE_OUT, index=False)


def save_figure(fig: plt.Figure, stem: str) -> None:
    """Save the figure in manuscript-friendly raster and vector formats."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for suffix, kwargs in {".png": {"dpi": 600}, ".pdf": {}, ".svg": {}}.items():
        fig.savefig(FIG_DIR / f"{stem}{suffix}", bbox_inches="tight", **kwargs)


def save_gray_preview(png_path: Path) -> None:
    """Save a grayscale preview for quick color-independence checks."""
    image = plt.imread(png_path)
    rgb = image[..., :3]
    gray = np.dot(rgb, np.array([0.299, 0.587, 0.114]))
    preview = np.dstack([gray, gray, gray])
    plt.imsave(FIG_DIR / f"{FIG_STEM}_gray_preview.png", preview)


def draw_release_partition(ax: plt.Axes, ts: pd.DataFrame) -> None:
    """Draw source, downstream and outlet fractions over time."""
    time_ms = ts["time_s"].to_numpy(dtype=float) * 1e3
    ax.plot(time_ms, ts["source_fraction"], color="#4d4d4d", linewidth=1.3, label="source")
    ax.plot(time_ms, ts["downstream_fraction"], color="#2166ac", linewidth=1.3, linestyle="--", label="downstream")
    ax.plot(time_ms, ts["outlet_fraction"], color="#b2182b", linewidth=1.1, marker="o", markersize=2.1, markevery=8, label="outlet")
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("debris fraction")
    ax.set_ylim(-0.03, 1.03)
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.legend(loc="center right")
    panel_label(ax, "a")


def draw_front_motion(ax: plt.Axes, ts: pd.DataFrame) -> None:
    """Draw mean, q99 and leading-front positions."""
    time_ms = ts["time_s"].to_numpy(dtype=float) * 1e3
    ax.plot(time_ms, ts["x_mean_over_L"], color="#4d4d4d", linewidth=1.1, label="mean")
    ax.plot(time_ms, ts["x_q99_over_L"], color="#2166ac", linewidth=1.1, linestyle="--", label="q99")
    ax.plot(time_ms, ts["x_max_over_L"], color="#b2182b", linewidth=1.1, label="max")
    ax.axhline(1.0, color="#777777", linewidth=0.9, linestyle=":")
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("x / L")
    ax.set_ylim(0.45, 1.03)
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.legend(loc="lower right")
    panel_label(ax, "b")


def draw_phase_path(ax: plt.Axes, ts: pd.DataFrame) -> None:
    """Draw front-position path against downstream fraction."""
    time_ms = ts["time_s"].to_numpy(dtype=float) * 1e3
    scatter = ax.scatter(
        ts["downstream_fraction"],
        ts["x_max_over_L"],
        c=time_ms,
        cmap="viridis",
        s=14,
        edgecolor="#222222",
        linewidth=0.25,
    )
    ax.axhline(1.0, color="#777777", linewidth=0.9, linestyle=":")
    ax.set_xlabel("downstream fraction")
    ax.set_ylabel("leading x / L")
    ax.set_ylim(0.80, 1.03)
    ax.grid(True, linewidth=0.35, alpha=0.35)
    cb = plt.colorbar(scatter, ax=ax, pad=0.02)
    cb.set_label("time (ms)")
    panel_label(ax, "c")


def draw_final_partition(ax: plt.Axes, summary: pd.Series) -> None:
    """Draw the final 907 debris partition as discrete bars."""
    labels = ["source", "downstream", "outlet"]
    values = [
        float(summary["final_source_fraction"]),
        float(summary["final_downstream_fraction"]),
        float(summary["final_outlet_fraction"]),
    ]
    colors = ["#4d4d4d", "#2166ac", "#b2182b"]
    ax.bar(labels, values, color=colors, edgecolor="#222222", linewidth=0.45)
    ax.set_ylabel("final fraction")
    ax.set_ylim(0, 1.0)
    ax.grid(True, axis="y", linewidth=0.35, alpha=0.35)
    panel_label(ax, "d")


def make_figure(ts: pd.DataFrame, summary: pd.Series) -> Path:
    """Create Fig. S9 and return the PNG path."""
    configure_matplotlib()
    fig = plt.figure(figsize=(7.2, 4.8), constrained_layout=True)
    grid = fig.add_gridspec(2, 2)
    draw_release_partition(fig.add_subplot(grid[0, 0]), ts)
    draw_front_motion(fig.add_subplot(grid[0, 1]), ts)
    draw_phase_path(fig.add_subplot(grid[1, 0]), ts)
    draw_final_partition(fig.add_subplot(grid[1, 1]), summary)
    save_figure(fig, FIG_STEM)
    plt.close(fig)
    png_path = FIG_DIR / f"{FIG_STEM}.png"
    save_gray_preview(png_path)
    return png_path


def main() -> int:
    """Run the 907 tail-capture plotting workflow."""
    ts, summary = load_907_timeseries()
    write_source_table(ts)
    path = make_figure(ts, summary)
    print(path)
    print(SOURCE_OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
