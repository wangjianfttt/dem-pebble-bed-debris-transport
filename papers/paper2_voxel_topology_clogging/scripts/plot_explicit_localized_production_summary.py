#!/usr/bin/env python3
"""Plot explicit localized-release production or diagnostic summaries."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
TABLE_DIR = PAPER_DIR / "tables"
FIG_DIR = PAPER_DIR / "figures"

PRODUCTION_TIMESERIES = TABLE_DIR / "explicit_localized_production_timeseries.csv"
PRODUCTION_SUMMARY = TABLE_DIR / "explicit_localized_production_summary.csv"
DIAGNOSTIC_TIMESERIES = TABLE_DIR / "explicit_localized_diagnostic_timeseries.csv"
DIAGNOSTIC_SUMMARY = TABLE_DIR / "explicit_localized_diagnostic_summary.csv"
DEFAULT_JOBS = PAPER_DIR / "production_localized_release_jobs.yaml"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["production", "diagnostic"], default="production")
    parser.add_argument("--timeseries", default=None, help="Optional custom timeseries CSV.")
    parser.add_argument("--summary", default=None, help="Optional custom summary CSV.")
    parser.add_argument("--out-stem", default=None, help="Output figure stem without extension.")
    return parser.parse_args()


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
    """Place a bold panel label in axes coordinates."""
    ax.text(-0.12, 1.05, label, transform=ax.transAxes, weight="bold", fontsize=9, va="top")


def case_label(job_id: str) -> str:
    """Return a compact label for one localized-release job."""
    if job_id.startswith("906"):
        return "906 upstream, N=15000"
    if job_id.startswith("907"):
        return "907 downstream, N=15000"
    if job_id.startswith("908"):
        return "908 upstream, N=30000"
    return job_id


def short_case_label(job_id: str) -> str:
    """Return a very compact plotting label for one localized-release job."""
    if job_id.startswith("906"):
        return "906 up"
    if job_id.startswith("907"):
        return "907 down"
    if job_id.startswith("908"):
        return "908 high-N"
    return job_id


def load_inputs(mode: str, timeseries: str | None = None, summary: str | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load production or diagnostic localized-release CSV outputs."""
    ts_path = Path(timeseries) if timeseries else (PRODUCTION_TIMESERIES if mode == "production" else DIAGNOSTIC_TIMESERIES)
    summary_path = Path(summary) if summary else (PRODUCTION_SUMMARY if mode == "production" else DIAGNOSTIC_SUMMARY)
    if not ts_path.exists():
        raise FileNotFoundError(f"Missing timeseries CSV: {ts_path}")
    if not summary_path.exists():
        raise FileNotFoundError(f"Missing summary CSV: {summary_path}")
    ts = pd.read_csv(ts_path)
    summ = pd.read_csv(summary_path)
    validate_inputs(ts, summ)
    return ts, summ


def validate_inputs(timeseries: pd.DataFrame, summary: pd.DataFrame) -> None:
    """Validate localized-release plotting inputs."""
    required_ts = {
        "job_id",
        "time_s",
        "source_fraction",
        "downstream_fraction",
        "outlet_fraction",
        "x_mean_over_L",
        "x_q99_over_L",
        "x_max_over_L",
        "debris_count_ok",
    }
    required_summary = {
        "job_id",
        "final_source_fraction",
        "final_downstream_fraction",
        "final_outlet_fraction",
        "final_time_s",
        "debris_count_ok",
    }
    missing_ts = sorted(required_ts.difference(timeseries.columns))
    missing_summary = sorted(required_summary.difference(summary.columns))
    if missing_ts:
        raise ValueError(f"Timeseries CSV missing columns: {missing_ts}")
    if missing_summary:
        raise ValueError(f"Summary CSV missing columns: {missing_summary}")
    if timeseries.empty:
        raise ValueError("Timeseries CSV is empty.")
    if summary.empty:
        raise ValueError("Summary CSV is empty.")


def evidence_status(summary: pd.DataFrame, mode: str) -> str:
    """Return a concise evidence-status string for the figure."""
    if mode == "production":
        if "target_time_reached" in summary.columns:
            completed = int(summary["target_time_reached"].astype(bool).sum())
        else:
            completed = int(summary["job_id"].nunique())
        return f"target-time completion: {completed}/3 jobs"
    n_jobs = int(summary["job_id"].nunique())
    return f"diagnostic view: {n_jobs}/3 jobs, not manuscript evidence"


def load_job_targets(path: Path = DEFAULT_JOBS) -> pd.DataFrame:
    """Load configured localized-release production targets."""
    if not path.exists():
        return pd.DataFrame(columns=["job_id", "target_physical_time_s", "priority"])
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    rows = []
    for job in data.get("jobs", []):
        rows.append(
            {
                "job_id": job["job_id"],
                "target_physical_time_s": float(job["target_physical_time_s"]),
                "priority": int(job.get("priority", 999)),
            }
        )
    return pd.DataFrame(rows)


def save_figure(fig: plt.Figure, stem: str) -> None:
    """Save figure in PNG, PDF and SVG formats."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for suffix, kwargs in {".png": {"dpi": 600}, ".pdf": {}, ".svg": {}}.items():
        fig.savefig(FIG_DIR / f"{stem}{suffix}", bbox_inches="tight", **kwargs)


def job_colors(job_ids: list[str]) -> dict[str, str]:
    """Return stable, colorblind-aware colors keyed by job id."""
    palette = ["#4d4d4d", "#2166ac", "#b2182b", "#1b7837"]
    return {job_id: palette[i % len(palette)] for i, job_id in enumerate(job_ids)}


def draw_fraction_timeseries(ax: plt.Axes, ts: pd.DataFrame) -> None:
    """Draw source and downstream fractions for all available production jobs."""
    job_ids = list(dict.fromkeys(ts.sort_values(["job_id", "time_s"])["job_id"].astype(str)))
    colors = job_colors(job_ids)
    for job_id in job_ids:
        group = ts[ts["job_id"].astype(str) == job_id].sort_values("time_s")
        time_ms = group["time_s"].to_numpy(dtype=float) * 1e3
        label = short_case_label(job_id)
        ax.plot(time_ms, group["source_fraction"], color=colors[job_id], linewidth=1.15, linestyle="-", label=f"{label} source")
        ax.plot(time_ms, group["downstream_fraction"], color=colors[job_id], linewidth=1.15, linestyle="--", label=f"{label} downstream")
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("debris fraction")
    ax.set_title("Release partition")
    ax.set_ylim(-0.02, 1.02)
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.legend(loc="center right", ncol=1)
    panel_label(ax, "a")


def draw_front_metrics(ax: plt.Axes, ts: pd.DataFrame) -> None:
    """Draw q99 and leading-particle positions for all available production jobs."""
    job_ids = list(dict.fromkeys(ts.sort_values(["job_id", "time_s"])["job_id"].astype(str)))
    colors = job_colors(job_ids)
    for job_id in job_ids:
        group = ts[ts["job_id"].astype(str) == job_id].sort_values("time_s")
        time_ms = group["time_s"].to_numpy(dtype=float) * 1e3
        label = short_case_label(job_id)
        ax.plot(time_ms, group["x_q99_over_L"], color=colors[job_id], linewidth=1.1, linestyle="--", label=f"{label} q99")
        ax.plot(time_ms, group["x_max_over_L"], color=colors[job_id], linewidth=1.1, linestyle="-", label=f"{label} max")
    ax.axhline(1.0, color="#777777", linewidth=0.9, linestyle=":")
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("x / L")
    ax.set_title("Migration front")
    ax.set_ylim(0, 1.05)
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.legend(loc="lower right", ncol=1)
    panel_label(ax, "b")


def draw_final_partition(ax: plt.Axes, summary: pd.DataFrame) -> None:
    """Draw final source, downstream and outlet fractions for available jobs."""
    ordered = summary.sort_values(["job_id"]).copy()
    labels = [short_case_label(str(job_id)) for job_id in ordered["job_id"]]
    y = np.arange(len(ordered))
    left = np.zeros(len(ordered))
    parts = [
        ("source", "final_source_fraction", "#4d4d4d"),
        ("downstream", "final_downstream_fraction", "#2166ac"),
        ("outlet", "final_outlet_fraction", "#b2182b"),
    ]
    for label, column, color in parts:
        values = ordered[column].to_numpy(dtype=float)
        ax.barh(y, values, left=left, color=color, edgecolor="#222222", linewidth=0.35, label=label)
        left += values
    ax.set_yticks(y, labels)
    ax.set_xlim(0, 1)
    ax.set_xlabel("final debris fraction")
    ax.set_title("Final partition")
    ax.legend(loc="lower right")
    panel_label(ax, "c")


def draw_job_completion(ax: plt.Axes, summary: pd.DataFrame, mode: str) -> None:
    """Draw target-time completion for configured localized-release jobs."""
    targets = load_job_targets()
    if targets.empty:
        targets = summary[["job_id", "final_time_s"]].rename(columns={"final_time_s": "target_physical_time_s"})
        targets["priority"] = np.arange(len(targets))
    summary_columns = ["job_id", "final_time_s"]
    if "target_time_reached" in summary.columns:
        summary_columns.append("target_time_reached")
    merged = targets.merge(summary[summary_columns], on="job_id", how="left")
    merged["final_time_s"] = merged["final_time_s"].fillna(0.0)
    merged["completion"] = np.clip(merged["final_time_s"] / merged["target_physical_time_s"], 0.0, 1.0)
    merged = merged.sort_values("priority")
    y = np.arange(len(merged))
    reached = merged.get("target_time_reached", pd.Series(False, index=merged.index)).astype(bool)
    colors = np.where(reached, "#1b7837", np.where(merged["final_time_s"] > 0, "#2166ac", "#d9d9d9"))
    bars = ax.barh(y, merged["completion"], color=colors, edgecolor="#222222", linewidth=0.35)
    for bar, is_reached, final_time in zip(bars, reached, merged["final_time_s"]):
        if final_time > 0 and not is_reached:
            bar.set_hatch("///")
    ax.axvline(1.0, color="#4d4d4d", linewidth=0.9, linestyle=":")
    ax.set_yticks(y, [short_case_label(str(job_id)) for job_id in merged["job_id"]])
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("fraction of target time")
    ax.set_title(evidence_status(summary, mode))
    ax.grid(True, axis="x", linewidth=0.35, alpha=0.35)
    for yi, (_, row) in zip(y, merged.iterrows()):
        if row["final_time_s"] > 0:
            ax.text(row["completion"] + 0.025, yi, f"{row['final_time_s'] * 1e3:.2f} ms", va="center", fontsize=6.8)
        else:
            ax.text(0.025, yi, "pending", va="center", fontsize=6.8, color="#555555")
    panel_label(ax, "d")


def make_figure(timeseries: pd.DataFrame, summary: pd.DataFrame, mode: str, stem: str) -> Path:
    """Create the localized-release summary figure and return the PNG path."""
    configure_matplotlib()
    fig = plt.figure(figsize=(7.2, 4.8), constrained_layout=True)
    grid = fig.add_gridspec(2, 2)
    ax_a = fig.add_subplot(grid[0, 0])
    ax_b = fig.add_subplot(grid[0, 1])
    ax_c = fig.add_subplot(grid[1, 0])
    ax_d = fig.add_subplot(grid[1, 1])
    draw_fraction_timeseries(ax_a, timeseries)
    draw_front_metrics(ax_b, timeseries)
    draw_final_partition(ax_c, summary)
    draw_job_completion(ax_d, summary, mode)
    save_figure(fig, stem)
    plt.close(fig)
    return FIG_DIR / f"{stem}.png"


def main() -> int:
    """Run the localized-release plotting workflow."""
    args = parse_args()
    ts, summary = load_inputs(args.mode, args.timeseries, args.summary)
    stem = args.out_stem or f"paper2_figS8_explicit_localized_{args.mode}_summary"
    path = make_figure(ts, summary, args.mode, stem)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
