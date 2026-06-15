#!/usr/bin/env python3
"""Analyze localized-release mechanism axes across 906, 907 and 908."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
TABLE_DIR = PAPER_DIR / "tables"
DATA_DIR = PAPER_DIR / "data"
FIG_DIR = PAPER_DIR / "figures"
NOTE_DIR = PAPER_DIR / "notes"

DEFAULT_TIMESERIES = TABLE_DIR / "explicit_localized_production_timeseries.csv"
DEFAULT_SUMMARY = TABLE_DIR / "explicit_localized_production_summary.csv"
OUT_TABLE = TABLE_DIR / "paper2_localized_mechanism_axes.csv"
OUT_JSON = DATA_DIR / "paper2_localized_mechanism_axes.json"
OUT_MD = NOTE_DIR / "paper2_localized_mechanism_axes.md"
FIG_STEM = "paper2_figS19_localized_mechanism_axes"

JOB_LABELS = {
    "906_upstream_source_continue_1M_to_4M": "906 upstream",
    "907_downstream_source_dt5e9_to_10ms": "907 downstream",
    "908_high_inventory_dt5e9_to_10ms": "908 high inventory",
}
JOB_ORDER = list(JOB_LABELS)


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
    """Place a compact panel label."""
    ax.text(-0.12, 1.05, label, transform=ax.transAxes, weight="bold", fontsize=9, va="top")


def load_tables(timeseries_path: Path, summary_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load and validate localized-release time-series and summary tables."""
    if not timeseries_path.exists():
        raise FileNotFoundError(timeseries_path)
    if not summary_path.exists():
        raise FileNotFoundError(summary_path)
    ts = pd.read_csv(timeseries_path)
    summary = pd.read_csv(summary_path)
    required_ts = {
        "job_id",
        "time_s",
        "source_fraction",
        "downstream_fraction",
        "outlet_fraction",
        "x_mean_over_L",
        "x_q99_over_L",
        "x_max_over_L",
        "debris_count",
        "debris_count_ok",
    }
    required_summary = {
        "job_id",
        "final_time_s",
        "target_time_reached",
        "final_debris_count",
        "final_source_fraction",
        "final_downstream_fraction",
        "final_outlet_fraction",
        "final_x_mean_over_L",
        "final_x_q99_over_L",
        "final_x_max_over_L",
        "debris_count_ok",
    }
    missing_ts = sorted(required_ts.difference(ts.columns))
    missing_summary = sorted(required_summary.difference(summary.columns))
    if missing_ts:
        raise ValueError(f"Timeseries missing columns: {missing_ts}")
    if missing_summary:
        raise ValueError(f"Summary missing columns: {missing_summary}")
    ts = ts[ts["job_id"].astype(str).isin(JOB_ORDER)].copy()
    summary = summary[summary["job_id"].astype(str).isin(JOB_ORDER)].copy()
    if ts["job_id"].nunique() != len(JOB_ORDER):
        raise ValueError("Localized mechanism axes require 906, 907 and 908 time series.")
    if summary["job_id"].nunique() != len(JOB_ORDER):
        raise ValueError("Localized mechanism axes require 906, 907 and 908 summary rows.")
    if not bool(ts["debris_count_ok"].all()) or not bool(summary["debris_count_ok"].all()):
        raise ValueError("At least one localized-release row has an unexpected debris count.")
    return ts.sort_values(["job_id", "time_s"]), summary


def linear_slope(x: np.ndarray, y: np.ndarray) -> float:
    """Return a least-squares linear slope, or NaN for insufficient data."""
    finite = np.isfinite(x) & np.isfinite(y)
    if finite.sum() < 2:
        return float("nan")
    return float(np.polyfit(x[finite], y[finite], 1)[0])


def front_intermittency(values: np.ndarray) -> float:
    """Return a dimensionless frame-to-frame front intermittency index."""
    if values.size < 3:
        return float("nan")
    delta = np.diff(values)
    denom = np.mean(np.abs(delta))
    if denom <= 0:
        return 0.0
    return float(np.std(delta) / denom)


def nearest_at_or_before(group: pd.DataFrame, time_s: float) -> pd.Series:
    """Return the row nearest to but not later than the requested time."""
    subset = group[group["time_s"] <= time_s]
    if subset.empty:
        return group.sort_values("time_s").iloc[0]
    return subset.sort_values("time_s").iloc[-1]


def summarize_axes(ts: pd.DataFrame, summary: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Compute localized-release mechanism metrics for all available jobs."""
    common_time = float(ts.groupby("job_id")["time_s"].max().min())
    rows: list[dict[str, Any]] = []
    for job_id in JOB_ORDER:
        group = ts[ts["job_id"].astype(str) == job_id].sort_values("time_s")
        final = summary[summary["job_id"].astype(str) == job_id].iloc[-1]
        common = nearest_at_or_before(group, common_time)
        time = group["time_s"].to_numpy(dtype=float)
        source = group["source_fraction"].to_numpy(dtype=float)
        downstream = group["downstream_fraction"].to_numpy(dtype=float)
        x99 = group["x_q99_over_L"].to_numpy(dtype=float)
        xmax = group["x_max_over_L"].to_numpy(dtype=float)
        xmean = group["x_mean_over_L"].to_numpy(dtype=float)
        x99_slope = linear_slope(time, x99)
        xmax_slope = linear_slope(time, xmax)
        rows.append(
            {
                "job_id": job_id,
                "label": JOB_LABELS[job_id],
                "final_time_s": float(final["final_time_s"]),
                "target_time_reached": bool(final["target_time_reached"]),
                "particle_count": int(final["final_debris_count"]),
                "final_source_fraction": float(final["final_source_fraction"]),
                "final_released_fraction": 1.0 - float(final["final_source_fraction"]),
                "final_downstream_fraction": float(final["final_downstream_fraction"]),
                "final_outlet_fraction": float(final["final_outlet_fraction"]),
                "final_x_mean_over_L": float(final["final_x_mean_over_L"]),
                "final_x99_over_L": float(final["final_x_q99_over_L"]),
                "final_xmax_over_L": float(final["final_x_max_over_L"]),
                "final_front_bulk_gap_over_L": float(final["final_x_max_over_L"] - final["final_x_q99_over_L"]),
                "final_gap_to_outlet_over_L": float(1.0 - final["final_x_max_over_L"]),
                "common_time_s": common_time,
                "common_source_fraction": float(common["source_fraction"]),
                "common_downstream_fraction": float(common["downstream_fraction"]),
                "common_outlet_fraction": float(common["outlet_fraction"]),
                "common_x99_over_L": float(common["x_q99_over_L"]),
                "common_xmax_over_L": float(common["x_max_over_L"]),
                "common_front_bulk_gap_over_L": float(common["x_max_over_L"] - common["x_q99_over_L"]),
                "source_release_rate_fraction_per_s": -linear_slope(time, source),
                "downstream_growth_rate_fraction_per_s": linear_slope(time, downstream),
                "x99_speed_L_per_s": x99_slope,
                "xmax_speed_L_per_s": xmax_slope,
                "front_to_bulk_speed_ratio": float(xmax_slope / x99_slope) if x99_slope > 0 else float("nan"),
                "front_intermittency_index": front_intermittency(xmax),
            }
        )
    metrics = pd.DataFrame(rows)
    overview = {
        "job_count": int(len(metrics)),
        "common_time_s": common_time,
        "all_outlet_fractions_zero": bool((metrics["final_outlet_fraction"] == 0.0).all()),
        "max_final_released_fraction": float(metrics["final_released_fraction"].max()),
        "min_final_source_fraction": float(metrics["final_source_fraction"].min()),
        "max_front_bulk_gap_over_L": float(metrics["final_front_bulk_gap_over_L"].max()),
        "max_front_to_bulk_speed_ratio": float(metrics["front_to_bulk_speed_ratio"].max()),
        "claim_boundary": (
            "These metrics compare localized-release mechanism axes across three production cases. "
            "They support retained-bulk/sparse-front decoupling, not a source-position scaling law, "
            "completed BTC, outlet breakthrough or critical clogging transition."
        ),
    }
    return metrics, overview


def color_map() -> dict[str, str]:
    """Return stable colorblind-safe colors for the three jobs."""
    return {
        "906_upstream_source_continue_1M_to_4M": "#4d4d4d",
        "907_downstream_source_dt5e9_to_10ms": "#2166ac",
        "908_high_inventory_dt5e9_to_10ms": "#b2182b",
    }


def draw_retention(ax: plt.Axes, ts: pd.DataFrame) -> None:
    """Draw source-retention fraction over time."""
    colors = color_map()
    for job_id in JOB_ORDER:
        group = ts[ts["job_id"].astype(str) == job_id]
        ax.plot(group["time_s"] * 1e3, group["source_fraction"], color=colors[job_id], linewidth=1.25, label=JOB_LABELS[job_id])
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("source fraction")
    ax.set_ylim(0.86, 1.01)
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.legend(loc="lower left")
    panel_label(ax, "a")


def draw_release(ax: plt.Axes, ts: pd.DataFrame) -> None:
    """Draw downstream release fraction over time."""
    colors = color_map()
    for job_id in JOB_ORDER:
        group = ts[ts["job_id"].astype(str) == job_id]
        ax.plot(group["time_s"] * 1e3, group["downstream_fraction"], color=colors[job_id], linewidth=1.25, label=JOB_LABELS[job_id])
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("downstream fraction")
    ax.set_ylim(0, 0.12)
    ax.grid(True, linewidth=0.35, alpha=0.35)
    panel_label(ax, "b")


def draw_front_split(ax: plt.Axes, metrics: pd.DataFrame) -> None:
    """Draw final mean, 99th percentile and leading-front positions."""
    colors = color_map()
    x = np.arange(len(JOB_ORDER))
    for idx, job_id in enumerate(JOB_ORDER):
        row = metrics[metrics["job_id"] == job_id].iloc[0]
        ax.plot(
            [idx, idx],
            [row["final_x99_over_L"], row["final_xmax_over_L"]],
            color=colors[job_id],
            linewidth=1.0,
            alpha=0.8,
        )
        ax.scatter(idx - 0.08, row["final_x_mean_over_L"], marker="o", s=22, color=colors[job_id], edgecolor="#222222", linewidth=0.3)
        ax.scatter(idx, row["final_x99_over_L"], marker="s", s=22, color=colors[job_id], edgecolor="#222222", linewidth=0.3)
        ax.scatter(idx + 0.08, row["final_xmax_over_L"], marker="^", s=28, color=colors[job_id], edgecolor="#222222", linewidth=0.3)
    ax.axhline(1.0, color="#777777", linewidth=0.9, linestyle=":")
    ax.set_xticks(x, [JOB_LABELS[job_id] for job_id in JOB_ORDER], rotation=15, ha="right")
    ax.set_ylabel("final x / L")
    ax.set_ylim(0.25, 1.04)
    ax.grid(True, axis="y", linewidth=0.35, alpha=0.35)
    ax.scatter([], [], marker="o", color="#777777", label="mean")
    ax.scatter([], [], marker="s", color="#777777", label="x99")
    ax.scatter([], [], marker="^", color="#777777", label="max")
    ax.legend(loc="lower right", ncol=3, handletextpad=0.2, columnspacing=0.8)
    panel_label(ax, "c")


def draw_mechanism_plane(ax: plt.Axes, metrics: pd.DataFrame) -> None:
    """Draw release fraction against sparse-front separation."""
    colors = color_map()
    for job_id in JOB_ORDER:
        row = metrics[metrics["job_id"] == job_id].iloc[0]
        ax.scatter(
            row["final_released_fraction"],
            row["final_front_bulk_gap_over_L"],
            s=34 + row["particle_count"] / 600,
            color=colors[job_id],
            edgecolor="#222222",
            linewidth=0.35,
            label=JOB_LABELS[job_id],
        )
    ax.set_xlabel("released fraction")
    ax.set_ylabel("front-bulk gap, xmax - x99")
    ax.set_xlim(0, max(0.12, float(metrics["final_released_fraction"].max()) * 1.2))
    ax.set_ylim(0, max(0.7, float(metrics["final_front_bulk_gap_over_L"].max()) * 1.12))
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.legend(loc="lower left")
    panel_label(ax, "d")


def save_figure(fig: plt.Figure) -> None:
    """Save the mechanism-axis figure in PNG, PDF and SVG formats."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for suffix, kwargs in {".png": {"dpi": 600}, ".pdf": {}, ".svg": {}}.items():
        fig.savefig(FIG_DIR / f"{FIG_STEM}{suffix}", bbox_inches="tight", **kwargs)


def save_gray_preview() -> None:
    """Save a grayscale preview for color-independence checks."""
    image = plt.imread(FIG_DIR / f"{FIG_STEM}.png")
    rgb = image[..., :3]
    gray = np.dot(rgb, np.array([0.299, 0.587, 0.114]))
    plt.imsave(FIG_DIR / f"{FIG_STEM}_gray_preview.png", np.dstack([gray, gray, gray]))


def make_figure(ts: pd.DataFrame, metrics: pd.DataFrame) -> None:
    """Create the localized-release mechanism-axis figure."""
    configure_matplotlib()
    fig = plt.figure(figsize=(7.2, 4.7), constrained_layout=True)
    grid = fig.add_gridspec(2, 2)
    draw_retention(fig.add_subplot(grid[0, 0]), ts)
    draw_release(fig.add_subplot(grid[0, 1]), ts)
    draw_front_split(fig.add_subplot(grid[1, 0]), metrics)
    draw_mechanism_plane(fig.add_subplot(grid[1, 1]), metrics)
    save_figure(fig)
    plt.close(fig)
    save_gray_preview()


def write_outputs(metrics: pd.DataFrame, overview: dict[str, Any]) -> None:
    """Write mechanism-axis table, JSON and Markdown report."""
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    NOTE_DIR.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(OUT_TABLE, index=False)
    payload = {"summary": overview, "rows": metrics.to_dict(orient="records")}
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# Localized-Release Mechanism Axes",
        "",
        f"- Common early window: `{overview['common_time_s']:.6g} s`",
        f"- All final outlet fractions zero: `{overview['all_outlet_fractions_zero']}`",
        f"- Maximum final released fraction: `{overview['max_final_released_fraction']:.6f}`",
        f"- Maximum front-bulk gap: `{overview['max_front_bulk_gap_over_L']:.6f}`",
        "",
        "## Boundary",
        "",
        overview["claim_boundary"],
        "",
        "## Outputs",
        "",
        f"- Table: `{OUT_TABLE.relative_to(PROJECT_ROOT)}`",
        f"- Figure: `papers/paper2_voxel_topology_clogging/figures/{FIG_STEM}.pdf`",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(timeseries_path: Path = DEFAULT_TIMESERIES, summary_path: Path = DEFAULT_SUMMARY) -> dict[str, Any]:
    """Run the localized-release mechanism-axis analysis."""
    ts, summary = load_tables(timeseries_path, summary_path)
    metrics, overview = summarize_axes(ts, summary)
    write_outputs(metrics, overview)
    make_figure(ts, metrics)
    return overview


def main() -> int:
    """Run the command-line workflow."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeseries", type=Path, default=DEFAULT_TIMESERIES)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args()
    print(json.dumps(run(args.timeseries, args.summary), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
