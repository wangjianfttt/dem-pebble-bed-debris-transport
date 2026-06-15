#!/usr/bin/env python3
"""Build an integrated mechanism-evidence map for Paper 2."""

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

REPRESENTATIVE = TABLE_DIR / "paper2_fig3_representative_state_source.csv"
FRONT_METRICS = TABLE_DIR / "paper2_front_migration_metrics_source.csv"
FRONT_EVENTS = TABLE_DIR / "paper2_front_migration_events_source.csv"
LOCALIZED_SUMMARY = TABLE_DIR / "explicit_localized_production_summary.csv"
LOADING_SUMMARY = TABLE_DIR / "paper2_fig4_loading_summary_source.csv"

OUT_CSV = TABLE_DIR / "paper2_mechanism_evidence_matrix.csv"
OUT_JSON = DATA_DIR / "paper2_mechanism_evidence.json"
OUT_FIG = FIG_DIR / "paper2_figS11_mechanism_evidence_map"


def configure_matplotlib() -> None:
    """Configure compact journal-style Matplotlib defaults."""
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


def panel_label(ax: plt.Axes, label: str, x: float = -0.12, y: float = 1.05) -> None:
    """Place a bold panel label."""
    ax.text(x, y, label, transform=ax.transAxes, weight="bold", fontsize=9, va="top")


def read_csv(path: Path) -> pd.DataFrame:
    """Read a required CSV file."""
    if not path.exists():
        raise FileNotFoundError(path)
    data = pd.read_csv(path)
    if data.empty:
        raise ValueError(f"Empty input table: {path}")
    return data


def build_evidence_matrix(
    representative: pd.DataFrame,
    front_metrics: pd.DataFrame,
    front_events: pd.DataFrame,
    localized: pd.DataFrame,
    loading: pd.DataFrame,
) -> pd.DataFrame:
    """Return a compact mechanism-evidence matrix from existing source tables."""
    rows: list[dict[str, Any]] = []
    rep = representative.sort_values("drag_to_weight_ratio")
    rows.append(
        {
            "mechanism": "drive-controlled migration",
            "evidence": "Representative states",
            "metric": "Fd/W range",
            "value": f"{rep['drag_to_weight_ratio'].min():.2f}-{rep['drag_to_weight_ratio'].max():.2f}",
            "interpretation": "Higher drag-to-weight ratio moves the debris cloud downstream.",
            "source": REPRESENTATIVE.as_posix(),
        }
    )
    rows.append(
        {
            "mechanism": "drive-controlled migration",
            "evidence": "Representative states",
            "metric": "final BTC range",
            "value": f"{rep['final_BTC'].min():.5f}-{rep['final_BTC'].max():.5f}",
            "interpretation": "Breakthrough increases with stronger downstream migration in the selected states.",
            "source": REPRESENTATIVE.as_posix(),
        }
    )
    front = front_metrics.iloc[0]
    rows.extend(
        [
            {
                "mechanism": "delayed leading-tail breakthrough",
                "evidence": "Time-resolved representative case",
                "metric": "first BTC time",
                "value": f"{front['first_breakthrough_time_s']:.5f} s",
                "interpretation": "Outlet arrival occurs after debris-front migration through the connected skeleton.",
                "source": FRONT_METRICS.as_posix(),
            },
            {
                "mechanism": "delayed leading-tail breakthrough",
                "evidence": "Time-resolved representative case",
                "metric": "q99 speed / mean speed",
                "value": f"{front['x_q99_speed_m_per_s'] / front['x_mean_speed_m_per_s']:.2f}",
                "interpretation": "The leading tail advances faster than the mean cloud.",
                "source": FRONT_METRICS.as_posix(),
            },
            {
                "mechanism": "delayed leading-tail breakthrough",
                "evidence": "Event ordering",
                "metric": "q99>=0.9 minus first BTC",
                "value": f"{front['q99_09_minus_first_BTC_s']:.5f} s",
                "interpretation": "A weak outlet signal appears before the 99th percentile occupies the near-outlet region.",
                "source": FRONT_EVENTS.as_posix(),
            },
        ]
    )
    localized_final = localized.copy()
    rows.append(
        {
            "mechanism": "source-zone retention",
            "evidence": "Explicit internal-source production windows",
            "metric": "source fraction at 10 ms",
            "value": f"{localized_final['final_source_fraction'].min():.4f}-{localized_final['final_source_fraction'].max():.4f}",
            "interpretation": "Internal debris release remains retention dominated over the analyzed window.",
            "source": LOCALIZED_SUMMARY.as_posix(),
        }
    )
    rows.append(
        {
            "mechanism": "source-position effect",
            "evidence": "Explicit internal-source production windows",
            "metric": "leading x/L at 10 ms",
            "value": f"{localized_final['final_x_max_over_L'].min():.3f}-{localized_final['final_x_max_over_L'].max():.3f}",
            "interpretation": "Source position changes leading-tail location without producing outlet release.",
            "source": LOCALIZED_SUMMARY.as_posix(),
        }
    )
    rows.extend(
        [
            {
                "mechanism": "pre-clogging loading response",
                "evidence": "Loading scan",
                "metric": "max blockage range",
                "value": f"{loading['subvoxel_max_blockage_ratio'].min():.2e}-{loading['subvoxel_max_blockage_ratio'].max():.2e}",
                "interpretation": "Local blockage grows with inventory but remains a sub-voxel perturbation.",
                "source": LOADING_SUMMARY.as_posix(),
            },
            {
                "mechanism": "pre-clogging loading response",
                "evidence": "Loading scan",
                "metric": "connectivity loss range",
                "value": f"{loading['connectivity_loss'].min():.1e}-{loading['connectivity_loss'].max():.1e}",
                "interpretation": "The outlet-connected void skeleton is retained in the current loading window.",
                "source": LOADING_SUMMARY.as_posix(),
            },
        ]
    )
    return pd.DataFrame(rows)


def draw_drive_panel(ax: plt.Axes, representative: pd.DataFrame) -> None:
    """Draw final BTC and mean penetration against drag-to-weight ratio."""
    rep = representative.sort_values("drag_to_weight_ratio")
    x = rep["drag_to_weight_ratio"].to_numpy(dtype=float)
    btc = rep["final_BTC"].to_numpy(dtype=float)
    xmean = rep["x_mean_over_L"].to_numpy(dtype=float)
    sizes = 55 + 430 * (btc / btc.max() if btc.max() > 0 else btc)
    scatter = ax.scatter(
        x,
        xmean,
        s=sizes,
        c=btc,
        cmap="Blues",
        vmin=0,
        vmax=max(0.085, float(btc.max())),
        edgecolor="#222222",
        linewidth=0.45,
        zorder=3,
    )
    ax.set_xlabel(r"$F_d/W$")
    ax.set_ylabel("mean x/L")
    ax.set_ylim(0.15, 0.56)
    ax.set_title("Drive-controlled migration")
    ax.grid(True, linewidth=0.35, alpha=0.35)
    cbar = ax.figure.colorbar(scatter, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("final BTC")
    panel_label(ax, "a")


def draw_event_panel(ax: plt.Axes, events: pd.DataFrame) -> None:
    """Draw ordered front and breakthrough events as a horizontal event map."""
    ordered_names = ["x_q99_over_L>=0.5", "BTC>0", "x_q99_over_L>=0.9", "x_q99_over_L>=0.99"]
    labels = ["q99 >= 0.5", "first BTC", "q99 >= 0.9", "q99 >= 0.99"]
    rows = []
    for name, label in zip(ordered_names, labels):
        row = events[events["event"] == name]
        if row.empty or not bool(row.iloc[0]["detected"]):
            continue
        rows.append((label, float(row.iloc[0]["elapsed_time"])))
    y = np.arange(len(rows))
    times = [row[1] * 1e3 for row in rows]
    ax.hlines(y, 0, times, color="#d0d0d0", linewidth=1.0, zorder=1)
    ax.scatter(times, y, s=55, color="#4d4d4d", edgecolor="#222222", linewidth=0.45, zorder=3)
    ax.set_yticks(y, [row[0] for row in rows])
    ax.set_xlabel("elapsed time (ms)")
    ax.set_title("Event ordering")
    ax.grid(True, axis="x", linewidth=0.35, alpha=0.35)
    panel_label(ax, "b")


def draw_localized_panel(ax: plt.Axes, localized: pd.DataFrame) -> None:
    """Draw final partition fractions for explicit localized-release cases."""
    labels = [str(job).split("_")[0] for job in localized["job_id"]]
    y = np.arange(len(localized))
    source = localized["final_source_fraction"].to_numpy(dtype=float)
    downstream = localized["final_downstream_fraction"].to_numpy(dtype=float)
    outlet = localized["final_outlet_fraction"].to_numpy(dtype=float)
    ax.barh(y, source, color="#b7c4bb", edgecolor="#333333", linewidth=0.35, label="source")
    ax.barh(y, downstream, left=source, color="#7b9dbd", edgecolor="#333333", linewidth=0.35, label="downstream")
    ax.barh(y, outlet, left=source + downstream, color="#c44e52", edgecolor="#333333", linewidth=0.35, label="outlet")
    ax.set_yticks(y, labels)
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("final fraction")
    ax.set_title("Internal-source retention")
    ax.legend(loc="lower right", ncols=3)
    ax.grid(True, axis="x", linewidth=0.35, alpha=0.35)
    panel_label(ax, "c")


def draw_loading_panel(ax: plt.Axes, loading: pd.DataFrame) -> None:
    """Draw loading response as local blockage versus connectivity loss."""
    ordered = loading.sort_values("debris_total_number")
    x = ordered["debris_total_number"].to_numpy(dtype=float)
    blockage = ordered["subvoxel_max_blockage_ratio"].to_numpy(dtype=float)
    loss = ordered["connectivity_loss"].to_numpy(dtype=float)
    ax.scatter(x, blockage, s=58, color="#4d4d4d", edgecolor="#222222", linewidth=0.45, label="max blockage")
    ax.scatter(x, np.maximum(loss, 1e-7), s=52, marker="s", facecolor="white", edgecolor="#1b7837", linewidth=1.0, label="connectivity loss")
    ax.set_yscale("log")
    ax.set_xlabel("injected debris count")
    ax.set_ylabel("dimensionless signal")
    ax.set_title("Loading without connectivity loss")
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.legend(loc="upper left")
    panel_label(ax, "d")


def save_figure(fig: plt.Figure, stem: Path) -> None:
    """Save PNG, PDF and SVG exports for a Matplotlib figure."""
    stem.parent.mkdir(parents=True, exist_ok=True)
    for suffix, kwargs in {".png": {"dpi": 600}, ".pdf": {}, ".svg": {}}.items():
        fig.savefig(stem.with_suffix(suffix), bbox_inches="tight", **kwargs)


def write_outputs(matrix: pd.DataFrame, payload: dict[str, Any]) -> None:
    """Write mechanism evidence table and JSON summary."""
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    matrix.to_csv(OUT_CSV, index=False)
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> int:
    """Create the integrated mechanism-evidence table and supplementary figure."""
    configure_matplotlib()
    representative = read_csv(REPRESENTATIVE)
    front_metrics = read_csv(FRONT_METRICS)
    front_events = read_csv(FRONT_EVENTS)
    localized = read_csv(LOCALIZED_SUMMARY)
    loading = read_csv(LOADING_SUMMARY)

    matrix = build_evidence_matrix(representative, front_metrics, front_events, localized, loading)
    payload = {
        "evidence_rows": int(len(matrix)),
        "representative_cases": int(len(representative)),
        "localized_cases": int(len(localized)),
        "loading_cases": int(len(loading)),
        "claim_boundary": "Integrated mechanism evidence supports a pre-clogging migration/filtering interpretation, not a pressure-calibrated critical-clogging transition.",
        "outputs": {"csv": OUT_CSV.as_posix(), "figure_stem": OUT_FIG.as_posix()},
    }
    write_outputs(matrix, payload)

    fig = plt.figure(figsize=(7.2, 4.8), constrained_layout=True)
    grid = fig.add_gridspec(2, 2)
    draw_drive_panel(fig.add_subplot(grid[0, 0]), representative)
    draw_event_panel(fig.add_subplot(grid[0, 1]), front_events)
    draw_localized_panel(fig.add_subplot(grid[1, 0]), localized)
    draw_loading_panel(fig.add_subplot(grid[1, 1]), loading)
    save_figure(fig, OUT_FIG)
    plt.close(fig)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
