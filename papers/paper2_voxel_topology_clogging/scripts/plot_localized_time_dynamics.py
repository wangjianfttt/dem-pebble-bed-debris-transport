#!/usr/bin/env python3
"""Create a main-text localized-release time-dynamics figure for Paper 2."""

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
DATA_DIR = PAPER_DIR / "data"
FIG_DIR = PAPER_DIR / "figures"
NOTE_DIR = PAPER_DIR / "notes"

SOURCE_TABLE = TABLE_DIR / "explicit_localized_production_timeseries.csv"
OUT_SOURCE = TABLE_DIR / "paper2_fig7_localized_time_dynamics_source.csv"
OUT_JSON = DATA_DIR / "paper2_fig7_localized_time_dynamics.json"
OUT_NOTE = NOTE_DIR / "paper2_fig7_localized_time_dynamics.md"
FIG_STEM = "paper2_fig7_localized_time_dynamics"

JOB_LABELS = {
    "906_upstream_source_continue_1M_to_4M": "906 upstream, 15k",
    "907_downstream_source_dt5e9_to_10ms": "907 downstream, 15k",
    "908_high_inventory_dt5e9_to_10ms": "908 upstream, 30k",
}
JOB_COLORS = {
    "906_upstream_source_continue_1M_to_4M": "#555555",
    "907_downstream_source_dt5e9_to_10ms": "#2166ac",
    "908_high_inventory_dt5e9_to_10ms": "#b2182b",
}


def configure_matplotlib() -> None:
    """Apply compact journal-style plotting defaults."""

    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 7.6,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.7,
            "axes.labelsize": 7.8,
            "axes.titlesize": 8.2,
            "xtick.labelsize": 6.9,
            "ytick.labelsize": 6.9,
            "legend.fontsize": 6.8,
            "legend.frameon": False,
        }
    )


def require_columns(table: pd.DataFrame, columns: set[str]) -> None:
    """Raise a clear error when a source table misses required columns."""

    missing = sorted(columns.difference(table.columns))
    if missing:
        raise ValueError(f"{SOURCE_TABLE} missing columns: {missing}")


def load_timeseries() -> pd.DataFrame:
    """Load and validate the localized-release time-series source table."""

    if not SOURCE_TABLE.exists():
        raise FileNotFoundError(f"Missing source table: {SOURCE_TABLE}")
    table = pd.read_csv(SOURCE_TABLE)
    require_columns(
        table,
        {
            "job_id",
            "step",
            "time_s",
            "source_fraction",
            "downstream_fraction",
            "outlet_fraction",
            "x_q90_over_L",
            "x_q99_over_L",
            "x_max_over_L",
            "debris_count_ok",
        },
    )
    table = table[table["job_id"].isin(JOB_LABELS)].copy()
    table = table[table["debris_count_ok"].astype(bool)].copy()
    if table.empty:
        raise ValueError("No valid localized-release rows found.")
    table["time_ms"] = 1000.0 * table["time_s"].astype(float)
    table["released_fraction"] = 1.0 - table["source_fraction"].astype(float)
    table["front_bulk_gap_over_L"] = table["x_max_over_L"].astype(float) - table["x_q99_over_L"].astype(float)
    table["job_label"] = table["job_id"].map(JOB_LABELS)
    return table.sort_values(["job_id", "time_s"])


def latest_rows(table: pd.DataFrame) -> pd.DataFrame:
    """Return the latest available row for each localized-release job."""

    return table.sort_values(["job_id", "time_s"]).groupby("job_id", as_index=False).tail(1)


def write_outputs(table: pd.DataFrame) -> dict[str, Any]:
    """Write source data, summary JSON and a short provenance note."""

    latest = latest_rows(table)
    OUT_SOURCE.parent.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    NOTE_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT_SOURCE, index=False)
    summary = {
        "source_table": str(SOURCE_TABLE.relative_to(PROJECT_ROOT)),
        "figure_stem": FIG_STEM,
        "job_count": int(latest["job_id"].nunique()),
        "max_final_time_ms": float(latest["time_ms"].max()),
        "latest": [
            {
                "job_id": row["job_id"],
                "label": row["job_label"],
                "step": int(row["step"]),
                "time_ms": float(row["time_ms"]),
                "source_fraction": float(row["source_fraction"]),
                "downstream_fraction": float(row["downstream_fraction"]),
                "outlet_fraction": float(row["outlet_fraction"]),
                "x_q99_over_L": float(row["x_q99_over_L"]),
                "x_max_over_L": float(row["x_max_over_L"]),
                "front_bulk_gap_over_L": float(row["front_bulk_gap_over_L"]),
            }
            for _, row in latest.iterrows()
        ],
        "claim_boundary": (
            "The figure visualizes existing DEM tracking outputs for localized-release cases. "
            "It does not establish a source-position scaling law or a pressure-calibrated clogging threshold."
        ),
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    OUT_NOTE.write_text(
        "# Paper 2 Fig. 5 Localized Time Dynamics\n\n"
        f"- Source table: `{SOURCE_TABLE.relative_to(PROJECT_ROOT)}`.\n"
        f"- Jobs plotted: `{summary['job_count']}`.\n"
        f"- Longest imported window: `{summary['max_final_time_ms']:.3f} ms`.\n"
        "- Boundary: this is a DEM-tracking visualization, not a fitted source-position law.\n",
        encoding="utf-8",
    )
    return summary


def _plot_job_lines(ax: plt.Axes, table: pd.DataFrame, y: str, ylabel: str, panel: str) -> None:
    """Plot a scalar time trace for each localized-release job."""

    for job_id, job in table.groupby("job_id", sort=False):
        ax.plot(
            job["time_ms"],
            job[y],
            lw=1.45,
            color=JOB_COLORS[job_id],
            label=JOB_LABELS[job_id],
        )
        ax.scatter(job["time_ms"].iloc[-1], job[y].iloc[-1], s=14, color=JOB_COLORS[job_id], zorder=5)
    ax.set_xlabel("time (ms)")
    ax.set_ylabel(ylabel)
    ax.text(0.0, 1.03, panel, transform=ax.transAxes, weight="bold", va="bottom")
    ax.grid(alpha=0.18, lw=0.5)


def make_figure(table: pd.DataFrame) -> None:
    """Render the localized-release time-dynamics figure."""

    configure_matplotlib()
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.15), constrained_layout=True)
    ax_a, ax_b, ax_c, ax_d = axes.ravel()

    _plot_job_lines(ax_a, table, "source_fraction", "source-slab fraction", "a")
    _plot_job_lines(ax_b, table, "downstream_fraction", "downstream fraction", "b")

    for job_id, job in table.groupby("job_id", sort=False):
        color = JOB_COLORS[job_id]
        ax_c.plot(job["time_ms"], job["x_q99_over_L"], lw=1.35, color=color)
        ax_c.plot(job["time_ms"], job["x_max_over_L"], lw=1.0, color=color, ls="--")
        ax_c.scatter(job["time_ms"].iloc[-1], job["x_q99_over_L"].iloc[-1], s=13, color=color, zorder=5)
        ax_c.scatter(
            job["time_ms"].iloc[-1],
            job["x_max_over_L"].iloc[-1],
            s=13,
            facecolor="white",
            edgecolor=color,
            zorder=5,
        )
    ax_c.axhline(1.0, color="#333333", lw=0.7, ls=":", alpha=0.8)
    ax_c.set_xlabel("time (ms)")
    ax_c.set_ylabel(r"axial coordinate $x/L$")
    ax_c.text(0.0, 1.03, "c", transform=ax_c.transAxes, weight="bold", va="bottom")
    ax_c.text(0.98, 0.06, "solid: $x_{99}$\ndashed: $x_{max}$", transform=ax_c.transAxes, ha="right", va="bottom", fontsize=6.8)
    ax_c.grid(alpha=0.18, lw=0.5)

    for job_id, job in table.groupby("job_id", sort=False):
        ax_d.plot(
            job["released_fraction"],
            job["front_bulk_gap_over_L"],
            lw=1.0,
            color=JOB_COLORS[job_id],
            alpha=0.55,
        )
        ax_d.scatter(
            job["released_fraction"],
            job["front_bulk_gap_over_L"],
            s=8,
            color=JOB_COLORS[job_id],
            alpha=0.35,
            edgecolors="none",
        )
        last = job.iloc[-1]
        ax_d.scatter(
            last["released_fraction"],
            last["front_bulk_gap_over_L"],
            s=28,
            color=JOB_COLORS[job_id],
            label=JOB_LABELS[job_id],
            zorder=6,
        )
    ax_d.set_xlabel("released fraction")
    ax_d.set_ylabel(r"$x_{max}-x_{99}$")
    ax_d.text(0.0, 1.03, "d", transform=ax_d.transAxes, weight="bold", va="bottom")
    ax_d.grid(alpha=0.18, lw=0.5)
    ax_d.legend(loc="best")

    ax_a.legend(loc="best")
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf", "svg"):
        fig.savefig(FIG_DIR / f"{FIG_STEM}.{ext}", dpi=450 if ext == "png" else None)
    plt.close(fig)


def main() -> None:
    """Entry point for CLI execution."""

    table = load_timeseries()
    summary = write_outputs(table)
    make_figure(table)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
