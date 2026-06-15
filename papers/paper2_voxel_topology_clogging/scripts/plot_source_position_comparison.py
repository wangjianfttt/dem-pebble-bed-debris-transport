#!/usr/bin/env python3
"""Plot source-position effects for the available 906 and 907 localized-release cases."""

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
SOURCE_OUT = TABLE_DIR / "paper2_figS10_source_position_comparison_source.csv"
FIG_STEM = "paper2_figS10_source_position_comparison"
JOB_ORDER = [
    "906_upstream_source_continue_1M_to_4M",
    "907_downstream_source_dt5e9_to_10ms",
]
JOB_LABELS = {
    "906_upstream_source_continue_1M_to_4M": "906 upstream",
    "907_downstream_source_dt5e9_to_10ms": "907 downstream",
}


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


def load_source_position_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load and validate production data for 906 and 907."""
    if not TIMESERIES.exists():
        raise FileNotFoundError(f"Missing production timeseries: {TIMESERIES}")
    if not SUMMARY.exists():
        raise FileNotFoundError(f"Missing production summary: {SUMMARY}")
    ts = pd.read_csv(TIMESERIES)
    summary = pd.read_csv(SUMMARY)
    required_ts = {
        "job_id",
        "step",
        "time_s",
        "source_fraction",
        "downstream_fraction",
        "outlet_fraction",
        "x_mean_over_L",
        "x_q99_over_L",
        "x_max_over_L",
    }
    missing = sorted(required_ts.difference(ts.columns))
    if missing:
        raise ValueError(f"Timeseries missing columns: {missing}")
    subset = ts[ts["job_id"].astype(str).isin(JOB_ORDER)].copy()
    if subset["job_id"].nunique() != len(JOB_ORDER):
        raise ValueError("Both 906 and 907 production series are required.")
    subset = subset[subset["time_s"] <= 0.01005].sort_values(["job_id", "time_s"])
    summary_subset = summary[summary["job_id"].astype(str).isin(JOB_ORDER)].copy()
    if summary_subset["job_id"].nunique() != len(JOB_ORDER):
        raise ValueError("Both 906 and 907 summary rows are required.")
    return subset, summary_subset


def write_source_table(ts: pd.DataFrame) -> None:
    """Save the exact source-position comparison rows used for Fig. S10."""
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
    ]
    SOURCE_OUT.parent.mkdir(parents=True, exist_ok=True)
    ts[cols].to_csv(SOURCE_OUT, index=False)


def save_figure(fig: plt.Figure, stem: str) -> None:
    """Save the figure in PNG, PDF and SVG formats."""
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


def colors() -> dict[str, str]:
    """Return stable colors for 906 and 907."""
    return {
        "906_upstream_source_continue_1M_to_4M": "#4d4d4d",
        "907_downstream_source_dt5e9_to_10ms": "#2166ac",
    }


def draw_downstream_growth(ax: plt.Axes, ts: pd.DataFrame) -> None:
    """Draw downstream debris fraction for the two source positions."""
    c = colors()
    for job_id in JOB_ORDER:
        group = ts[ts["job_id"].astype(str) == job_id].sort_values("time_s")
        ax.plot(
            group["time_s"].to_numpy(dtype=float) * 1e3,
            group["downstream_fraction"],
            color=c[job_id],
            linewidth=1.25,
            label=JOB_LABELS[job_id],
        )
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("downstream fraction")
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.legend(loc="upper left")
    panel_label(ax, "a")


def draw_front_position(ax: plt.Axes, ts: pd.DataFrame) -> None:
    """Draw leading-front position for the two source positions."""
    c = colors()
    for job_id in JOB_ORDER:
        group = ts[ts["job_id"].astype(str) == job_id].sort_values("time_s")
        ax.plot(
            group["time_s"].to_numpy(dtype=float) * 1e3,
            group["x_max_over_L"],
            color=c[job_id],
            linewidth=1.25,
            label=JOB_LABELS[job_id],
        )
    ax.axhline(1.0, color="#777777", linewidth=0.9, linestyle=":")
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("leading x / L")
    ax.set_ylim(0.2, 1.04)
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.legend(loc="lower right")
    panel_label(ax, "b")


def draw_final_comparison(ax: plt.Axes, summary: pd.DataFrame) -> None:
    """Draw final downstream and outlet fractions for 906 and 907."""
    ordered = summary.set_index("job_id").loc[JOB_ORDER].reset_index()
    x = np.arange(len(ordered))
    width = 0.34
    ax.bar(
        x - width / 2,
        ordered["final_downstream_fraction"],
        width,
        color="#2166ac",
        edgecolor="#222222",
        linewidth=0.4,
        label="downstream",
    )
    ax.bar(
        x + width / 2,
        ordered["final_outlet_fraction"],
        width,
        color="#b2182b",
        edgecolor="#222222",
        linewidth=0.4,
        label="outlet",
    )
    ax.set_xticks(x, [JOB_LABELS[job_id] for job_id in ordered["job_id"]])
    ax.set_ylabel("final fraction")
    ax.set_ylim(0, 0.14)
    ax.grid(True, axis="y", linewidth=0.35, alpha=0.35)
    ax.legend(loc="upper left")
    panel_label(ax, "c")


def draw_front_gap(ax: plt.Axes, summary: pd.DataFrame) -> None:
    """Draw final upstream distance from the outlet for 906 and 907."""
    ordered = summary.set_index("job_id").loc[JOB_ORDER].reset_index()
    gap = 1.0 - ordered["final_x_max_over_L"].to_numpy(dtype=float)
    ax.bar(
        [JOB_LABELS[job_id] for job_id in ordered["job_id"]],
        gap,
        color=["#4d4d4d", "#2166ac"],
        edgecolor="#222222",
        linewidth=0.4,
    )
    ax.set_ylabel("1 - leading x/L")
    ax.set_ylim(0, max(0.18, float(gap.max()) * 1.2))
    ax.grid(True, axis="y", linewidth=0.35, alpha=0.35)
    panel_label(ax, "d")


def make_figure(ts: pd.DataFrame, summary: pd.DataFrame) -> Path:
    """Create Fig. S10 and return the PNG path."""
    configure_matplotlib()
    fig = plt.figure(figsize=(7.2, 4.8), constrained_layout=True)
    grid = fig.add_gridspec(2, 2)
    draw_downstream_growth(fig.add_subplot(grid[0, 0]), ts)
    draw_front_position(fig.add_subplot(grid[0, 1]), ts)
    draw_final_comparison(fig.add_subplot(grid[1, 0]), summary)
    draw_front_gap(fig.add_subplot(grid[1, 1]), summary)
    save_figure(fig, FIG_STEM)
    plt.close(fig)
    png_path = FIG_DIR / f"{FIG_STEM}.png"
    save_gray_preview(png_path)
    return png_path


def main() -> int:
    """Run the source-position comparison plotting workflow."""
    ts, summary = load_source_position_data()
    write_source_table(ts)
    path = make_figure(ts, summary)
    print(path)
    print(SOURCE_OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
