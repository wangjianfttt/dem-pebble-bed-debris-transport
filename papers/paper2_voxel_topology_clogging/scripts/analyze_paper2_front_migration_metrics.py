#!/usr/bin/env python3
"""Extract debris-front migration metrics from Paper 2 time-resolved deposition data."""

from __future__ import annotations

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
FIG_DIR = PAPER_DIR / "figures"
NOTE_DIR = PAPER_DIR / "notes"

TIME_RESOLVED_SOURCE = TABLE_DIR / "paper2_time_resolved_deposition_source.csv"
METRICS_OUT = TABLE_DIR / "paper2_front_migration_metrics_source.csv"
EVENTS_OUT = TABLE_DIR / "paper2_front_migration_events_source.csv"
JSON_OUT = PAPER_DIR / "data" / "paper2_front_migration_metrics.json"
FIG_OUT = FIG_DIR / "paper2_figS5_front_migration_metrics"
NOTE_OUT = NOTE_DIR / "stage_report_front_migration_2026-06-09.md"

BED_LENGTH_M = 0.045


def configure_matplotlib() -> None:
    """Configure a compact publication-oriented plotting style."""
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


def load_time_resolved_data(path: Path = TIME_RESOLVED_SOURCE) -> pd.DataFrame:
    """Load and validate the time-resolved deposition source table."""
    if not path.exists():
        raise FileNotFoundError(f"Missing time-resolved source table: {path}")
    data = pd.read_csv(path)
    required = {
        "case_name",
        "elapsed_time",
        "BTC",
        "x_mean_over_L",
        "x_q90_over_L",
        "x_q99_over_L",
        "blockage_centroid_over_L",
        "peak_blockage_ratio",
        "peak_blockage_x_over_L",
    }
    missing = sorted(required - set(data.columns))
    if missing:
        raise ValueError(f"Missing required columns in {path}: {missing}")
    data = data.sort_values("elapsed_time").reset_index(drop=True)
    if data.empty:
        raise ValueError(f"No rows found in {path}")
    return data


def linear_fit_metric(data: pd.DataFrame, column: str, max_elapsed: float | None = None) -> dict[str, float]:
    """Fit a linear migration rate for one normalized front-position column."""
    work = data[["elapsed_time", column]].dropna().copy()
    if max_elapsed is not None:
        work = work[work["elapsed_time"] <= max_elapsed]
    if len(work) < 2:
        raise ValueError(f"At least two rows are required to fit {column}")
    x = work["elapsed_time"].to_numpy(dtype=float)
    y = work[column].to_numpy(dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    prediction = slope * x + intercept
    ss_res = float(np.sum((y - prediction) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0.0 else 1.0
    return {
        "slope_over_L_per_s": float(slope),
        "speed_m_per_s": float(slope * BED_LENGTH_M),
        "intercept_over_L": float(intercept),
        "fit_r2": float(r2),
        "fit_rows": int(len(work)),
    }


def first_event(data: pd.DataFrame, column: str, threshold: float) -> dict[str, Any]:
    """Return the first row where a column reaches a threshold."""
    hits = data[data[column] >= threshold]
    if hits.empty:
        return {
            "event": f"{column}>={threshold:g}",
            "detected": False,
            "elapsed_time": np.nan,
            "BTC": np.nan,
            column: np.nan,
        }
    row = hits.iloc[0]
    return {
        "event": f"{column}>={threshold:g}",
        "detected": True,
        "elapsed_time": float(row["elapsed_time"]),
        "BTC": float(row["BTC"]),
        column: float(row[column]),
    }


def compute_front_metrics(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Compute front-migration rates, delay times and peak-deposition metrics."""
    first_btc_rows = data[data["BTC"] > 0.0]
    if first_btc_rows.empty:
        first_btc_time = np.nan
        first_btc = np.nan
    else:
        first_btc = first_btc_rows.iloc[0]
        first_btc_time = float(first_btc["elapsed_time"])

    fit_limit = None if np.isnan(first_btc_time) else first_btc_time
    mean_fit = linear_fit_metric(data, "x_mean_over_L", fit_limit)
    q90_fit = linear_fit_metric(data, "x_q90_over_L", fit_limit)
    q99_fit = linear_fit_metric(data, "x_q99_over_L", fit_limit)
    centroid_fit = linear_fit_metric(data, "blockage_centroid_over_L", fit_limit)

    final = data.iloc[-1]
    peak = data.iloc[int(data["peak_blockage_ratio"].idxmax())]

    event_rows = [
        first_event(data, "x_q90_over_L", 0.5),
        first_event(data, "x_q99_over_L", 0.5),
        first_event(data, "x_q99_over_L", 0.9),
        first_event(data, "x_q99_over_L", 0.99),
    ]
    if not first_btc_rows.empty:
        event_rows.append(
            {
                "event": "BTC>0",
                "detected": True,
                "elapsed_time": first_btc_time,
                "BTC": float(first_btc["BTC"]),
                "x_mean_over_L": float(first_btc["x_mean_over_L"]),
                "x_q90_over_L": float(first_btc["x_q90_over_L"]),
                "x_q99_over_L": float(first_btc["x_q99_over_L"]),
            }
        )
    else:
        event_rows.append({"event": "BTC>0", "detected": False})

    q99_09_time = next((row["elapsed_time"] for row in event_rows if row["event"] == "x_q99_over_L>=0.9"), np.nan)
    q99_09_minus_first_btc = float(q99_09_time - first_btc_time) if not np.isnan(first_btc_time) and not np.isnan(q99_09_time) else np.nan

    metrics = {
        "case_name": str(final["case_name"]),
        "n_frames": int(len(data)),
        "fit_window": "pre_first_breakthrough",
        "first_breakthrough_time_s": first_btc_time,
        "first_breakthrough_BTC": float(first_btc["BTC"]) if not first_btc_rows.empty else np.nan,
        "final_time_s": float(final["elapsed_time"]),
        "final_BTC": float(final["BTC"]),
        "final_x_mean_over_L": float(final["x_mean_over_L"]),
        "final_x_q90_over_L": float(final["x_q90_over_L"]),
        "final_x_q99_over_L": float(final["x_q99_over_L"]),
        "x_mean_speed_m_per_s": mean_fit["speed_m_per_s"],
        "x_mean_fit_r2": mean_fit["fit_r2"],
        "x_q90_speed_m_per_s": q90_fit["speed_m_per_s"],
        "x_q90_fit_r2": q90_fit["fit_r2"],
        "x_q99_speed_m_per_s": q99_fit["speed_m_per_s"],
        "x_q99_fit_r2": q99_fit["fit_r2"],
        "blockage_centroid_speed_m_per_s": centroid_fit["speed_m_per_s"],
        "blockage_centroid_fit_r2": centroid_fit["fit_r2"],
        "peak_blockage_time_s": float(peak["elapsed_time"]),
        "peak_blockage_ratio": float(peak["peak_blockage_ratio"]),
        "peak_blockage_x_over_L": float(peak["peak_blockage_x_over_L"]),
        "q99_09_time_s": q99_09_time,
        "q99_09_minus_first_BTC_s": q99_09_minus_first_btc,
    }
    events = pd.DataFrame(event_rows)
    return pd.DataFrame([metrics]), events, metrics


def save_front_figure(data: pd.DataFrame, metrics: dict[str, Any]) -> None:
    """Save a supplementary figure summarizing front migration and delayed breakthrough."""
    configure_matplotlib()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 4.9), constrained_layout=True)
    ax0, ax1, ax2, ax3 = axes.ravel()

    time = data["elapsed_time"].to_numpy(dtype=float)
    ax0.plot(time, data["x_mean_over_L"], color="#2f5d8c", lw=1.25, label="mean")
    ax0.plot(time, data["x_q90_over_L"], color="#7a5195", lw=1.25, label="q90")
    ax0.plot(time, data["x_q99_over_L"], color="#ef5675", lw=1.25, label="q99")
    ax0.axvline(metrics["first_breakthrough_time_s"], color="0.25", lw=0.8, ls="--")
    ax0.set_xlabel("elapsed time (s)")
    ax0.set_ylabel("front position, x/L")
    ax0.set_ylim(0.0, 1.05)
    ax0.legend(loc="upper left", ncol=3, handlelength=1.8, columnspacing=0.8)
    ax0.text(0.02, 0.96, "a", transform=ax0.transAxes, ha="left", va="top", fontweight="bold")

    ax1.plot(time, data["BTC"], color="#00876c", lw=1.25)
    ax1.scatter(time, data["BTC"], s=10, color="#00876c", alpha=0.7)
    ax1.axvline(metrics["first_breakthrough_time_s"], color="0.25", lw=0.8, ls="--")
    ax1.set_xlabel("elapsed time (s)")
    ax1.set_ylabel("BTC")
    ax1.text(0.02, 0.96, "b", transform=ax1.transAxes, ha="left", va="top", fontweight="bold")

    ax2.scatter(
        data["peak_blockage_x_over_L"],
        data["peak_blockage_ratio"],
        c=time,
        cmap="viridis",
        s=18,
        linewidths=0.0,
    )
    ax2.set_xlabel("peak blockage position, x/L")
    ax2.set_ylabel("peak blockage ratio")
    ax2.ticklabel_format(axis="y", style="sci", scilimits=(-2, 2))
    ax2.text(0.02, 0.96, "c", transform=ax2.transAxes, ha="left", va="top", fontweight="bold")

    speeds = pd.Series(
        {
            "mean": metrics["x_mean_speed_m_per_s"],
            "q90": metrics["x_q90_speed_m_per_s"],
            "q99": metrics["x_q99_speed_m_per_s"],
            "centroid": metrics["blockage_centroid_speed_m_per_s"],
        }
    )
    colors = ["#2f5d8c", "#7a5195", "#ef5675", "#665c54"]
    ax3.bar(np.arange(len(speeds)), speeds.values, color=colors, width=0.62)
    ax3.set_xticks(np.arange(len(speeds)), speeds.index)
    ax3.set_ylabel("pre-BTC speed (m/s)")
    ax3.text(0.02, 0.96, "d", transform=ax3.transAxes, ha="left", va="top", fontweight="bold")

    for suffix in ("png", "pdf", "svg"):
        fig.savefig(f"{FIG_OUT}.{suffix}", dpi=300)
    plt.close(fig)


def save_outputs(metrics: pd.DataFrame, events: pd.DataFrame, metrics_dict: dict[str, Any]) -> None:
    """Write source tables, JSON metrics and a short stage report."""
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    NOTE_DIR.mkdir(parents=True, exist_ok=True)
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(METRICS_OUT, index=False)
    events.to_csv(EVENTS_OUT, index=False)
    JSON_OUT.write_text(json.dumps(metrics_dict, indent=2), encoding="utf-8")

    m = metrics_dict
    NOTE_OUT.write_text(
        "\n".join(
            [
                "# Stage Report: Front-Migration Mechanism Metrics",
                "",
                "Date: 2026-06-09",
                "",
                "## Purpose",
                "",
                "Extract quantitative debris-front migration metrics from the existing time-resolved deposition table for the representative Paper 2 case.",
                "",
                "## Inputs",
                "",
                f"- `{TIME_RESOLVED_SOURCE.relative_to(PROJECT_ROOT)}`",
                "",
                "## Outputs",
                "",
                f"- `{METRICS_OUT.relative_to(PROJECT_ROOT)}`",
                f"- `{EVENTS_OUT.relative_to(PROJECT_ROOT)}`",
                f"- `{JSON_OUT.relative_to(PROJECT_ROOT)}`",
                f"- `{FIG_OUT.relative_to(PROJECT_ROOT)}.[png,pdf,svg]`",
                "",
                "## Key Results",
                "",
                f"- Frames analyzed: {int(m['n_frames'])}.",
                f"- First non-zero BTC time: {m['first_breakthrough_time_s']:.5f} s.",
                f"- Final BTC: {m['final_BTC']:.6f}.",
                f"- Pre-breakthrough mean-cloud speed: {m['x_mean_speed_m_per_s']:.3f} m/s (R2={m['x_mean_fit_r2']:.3f}).",
                f"- Pre-breakthrough q99-front speed: {m['x_q99_speed_m_per_s']:.3f} m/s (R2={m['x_q99_fit_r2']:.3f}).",
                f"- Peak instantaneous blockage: {m['peak_blockage_ratio']:.6e} at elapsed {m['peak_blockage_time_s']:.5f} s and x/L={m['peak_blockage_x_over_L']:.3f}.",
                "",
                "## Interpretation",
                "",
                "The leading q99 front advances faster than the mean debris cloud before outlet arrival, which supports a delayed leading-tail breakthrough mechanism. The peak local blockage remains small and migrates through a connected bed skeleton, so the result remains a pre-clogging migration/filtering mechanism rather than evidence for a critical connectivity transition.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    """Run the front-migration mechanism analysis."""
    data = load_time_resolved_data()
    metrics, events, metrics_dict = compute_front_metrics(data)
    save_outputs(metrics, events, metrics_dict)
    save_front_figure(data, metrics_dict)
    print(json.dumps(metrics_dict, indent=2))


if __name__ == "__main__":
    main()
