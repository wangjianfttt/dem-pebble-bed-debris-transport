#!/usr/bin/env python3
"""Mine front-tail lag and retained-bulk mechanisms from Paper 2 source tables."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
TABLE_DIR = PAPER_DIR / "tables"
FIG_DIR = PAPER_DIR / "figures"
DATA_DIR = PAPER_DIR / "data"
NOTE_DIR = PAPER_DIR / "notes"

OUT_SOURCE = TABLE_DIR / "paper2_tail_lag_mechanism_source.csv"
OUT_EVENTS = TABLE_DIR / "paper2_tail_lag_event_source.csv"
OUT_JSON = DATA_DIR / "paper2_tail_lag_mechanism_mining.json"
OUT_NOTE = NOTE_DIR / "paper2_tail_lag_mechanism_mining.md"
OUT_FIG = FIG_DIR / "paper2_figS28_tail_lag_mechanism_mining"


def read_table(name: str) -> pd.DataFrame:
    """Read a required Paper 2 source table."""
    path = TABLE_DIR / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def first_threshold(data: pd.DataFrame, column: str, threshold: float) -> dict[str, Any]:
    """Return the first threshold-crossing event for one time-series column."""
    hits = data[pd.to_numeric(data[column], errors="coerce") >= threshold]
    if hits.empty:
        return {
            "series": column,
            "threshold": threshold,
            "detected": False,
            "time_s": np.nan,
            "value": np.nan,
        }
    row = hits.iloc[0]
    return {
        "series": column,
        "threshold": threshold,
        "detected": True,
        "time_s": float(row["time_s"]),
        "value": float(row[column]),
    }


def linear_fit(x: np.ndarray, y: np.ndarray) -> dict[str, float]:
    """Return slope, intercept and R2 for a simple linear fit."""
    mask = np.isfinite(x) & np.isfinite(y)
    x = x[mask]
    y = y[mask]
    if len(x) < 2:
        return {"slope": float("nan"), "intercept": float("nan"), "r2": float("nan")}
    slope, intercept = np.polyfit(x, y, 1)
    pred = slope * x + intercept
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return {"slope": float(slope), "intercept": float(intercept), "r2": float(r2)}


def build_tail_lag_metrics() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Build derived indicators for sparse-front, retained-bulk and delayed breakthrough behavior."""
    dep = read_table("paper2_time_resolved_deposition_source.csv").copy()
    quant = read_table("paper2_908_spatial_quantiles.csv").copy()
    localized = read_table("paper2_fig7_localized_time_dynamics_source.csv").copy()
    cdf = read_table("paper2_908_spatial_cdf_curves.csv").copy()

    dep["tail_bulk_gap_over_L"] = dep["x_q99_over_L"] - dep["x_mean_over_L"]
    dep["btc_positive"] = dep["BTC"] > 0
    first_btc = dep[dep["btc_positive"]].iloc[0]
    dep["time_to_first_btc_s"] = dep["elapsed_time"] - float(first_btc["elapsed_time"])
    dep["front_to_blockage_gap_over_L"] = dep["x_q99_over_L"] - dep["blockage_centroid_over_L"]

    quant["tail_bulk_gap_over_L"] = quant["x_max_over_L"] - quant["x_p99_over_L"]
    quant["rare_tail_ratio"] = np.divide(
        quant["fraction_x_gt_0p95"],
        quant["fraction_x_gt_0p40"],
        out=np.zeros(len(quant), dtype=float),
        where=quant["fraction_x_gt_0p40"].to_numpy(float) > 0,
    )
    quant["front_speed_over_L_per_ms"] = (
        quant["x_max_over_L"].diff() / quant["time_s"].diff() / 1000.0
    )

    localized["released_fraction"] = 1.0 - localized["source_fraction"]
    localized["retained_to_downstream_ratio"] = np.divide(
        localized["source_fraction"],
        localized["downstream_fraction"],
        out=np.full(len(localized), np.nan),
        where=localized["downstream_fraction"].to_numpy(float) > 0,
    )
    localized["tail_bulk_gap_over_L"] = localized["x_max_over_L"] - localized["x_q99_over_L"]

    event_rows = [
        {"family": "representative", **first_threshold(dep.rename(columns={"elapsed_time": "time_s"}), "x_q99_over_L", 0.9)},
        {"family": "representative", **first_threshold(dep.rename(columns={"elapsed_time": "time_s"}), "BTC", 0.001)},
        {"family": "high_inventory_908", **first_threshold(quant, "x_max_over_L", 0.9)},
        {"family": "high_inventory_908", **first_threshold(quant, "fraction_x_gt_0p95", 1.0e-5)},
        {"family": "localized_release", **first_threshold(localized, "released_fraction", 0.01)},
        {"family": "localized_release", **first_threshold(localized, "front_bulk_gap_over_L", 0.5)},
    ]
    events = pd.DataFrame(event_rows)

    dep_fit = linear_fit(dep["tail_bulk_gap_over_L"].to_numpy(float), dep["BTC"].to_numpy(float))
    q_fit = linear_fit(quant["tail_bulk_gap_over_L"].to_numpy(float), quant["fraction_x_gt_0p95"].to_numpy(float))

    source_rows: list[dict[str, Any]] = []
    source_rows.append(
        {
            "family": "representative_time_resolved",
            "n_frames": int(len(dep)),
            "first_BTC_time_s": float(first_btc["elapsed_time"]),
            "final_BTC": float(dep["BTC"].iloc[-1]),
            "final_tail_bulk_gap_over_L": float(dep["tail_bulk_gap_over_L"].iloc[-1]),
            "max_front_to_blockage_gap_over_L": float(dep["front_to_blockage_gap_over_L"].max()),
            "max_peak_blockage_ratio": float(dep["peak_blockage_ratio"].max()),
            "mechanism": "leading-tail breakthrough grows while the blockage centroid remains far upstream",
        }
    )
    source_rows.append(
        {
            "family": "high_inventory_908_sparse_front",
            "n_frames": int(len(quant)),
            "first_xmax_0p9_time_s": float(events.loc[events["series"].eq("x_max_over_L"), "time_s"].iloc[0]),
            "final_xmax_over_L": float(quant["x_max_over_L"].iloc[-1]),
            "final_x_p99_over_L": float(quant["x_p99_over_L"].iloc[-1]),
            "final_tail_bulk_gap_over_L": float(quant["tail_bulk_gap_over_L"].iloc[-1]),
            "final_fraction_x_gt_0p95": float(quant["fraction_x_gt_0p95"].iloc[-1]),
            "max_rare_tail_ratio": float(quant["rare_tail_ratio"].max()),
            "mechanism": "a tiny rare-front population approaches the outlet while the 99th percentile remains near the source",
        }
    )
    for job_id, group in localized.groupby("job_id", sort=True):
        final = group.iloc[-1]
        source_rows.append(
            {
                "family": "localized_release",
                "job_id": job_id,
                "n_frames": int(len(group)),
                "final_source_fraction": float(final["source_fraction"]),
                "final_downstream_fraction": float(final["downstream_fraction"]),
                "final_outlet_fraction": float(final["outlet_fraction"]),
                "final_front_bulk_gap_over_L": float(final["front_bulk_gap_over_L"]),
                "max_front_bulk_gap_over_L": float(group["front_bulk_gap_over_L"].max()),
                "max_released_fraction": float(group["released_fraction"].max()),
                "mechanism": "localized source retention dominates over downstream leakage",
            }
        )

    source = pd.DataFrame(source_rows)
    summary = {
        "decision": "tail_lag_mechanism_ready",
        "source_rows": int(len(source)),
        "event_rows": int(len(events)),
        "representative_first_BTC_time_s": float(first_btc["elapsed_time"]),
        "representative_final_BTC": float(dep["BTC"].iloc[-1]),
        "representative_final_tail_bulk_gap_over_L": float(dep["tail_bulk_gap_over_L"].iloc[-1]),
        "representative_max_front_to_blockage_gap_over_L": float(dep["front_to_blockage_gap_over_L"].max()),
        "representative_tail_gap_to_BTC_fit": dep_fit,
        "high_inventory_908_final_tail_bulk_gap_over_L": float(quant["tail_bulk_gap_over_L"].iloc[-1]),
        "high_inventory_908_final_fraction_x_gt_0p95": float(quant["fraction_x_gt_0p95"].iloc[-1]),
        "high_inventory_908_tail_gap_to_rare_tail_fit": q_fit,
        "localized_max_front_bulk_gap_over_L": float(localized["front_bulk_gap_over_L"].max()),
        "localized_min_final_source_fraction": float(localized.groupby("job_id")["source_fraction"].last().min()),
        "cdf_rows": int(len(cdf)),
        "claim_boundary": (
            "Derived from existing time-resolved and spatial-quantile source tables; supports a sparse-front/"
            "retained-bulk mechanism, not an experimentally calibrated residence-time distribution or universal tailing law."
        ),
    }
    return source, events, summary


def setup_style() -> None:
    """Configure a compact publication style for the supplementary figure."""
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8,
            "axes.linewidth": 0.7,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.major.size": 3,
            "ytick.major.size": 3,
            "legend.frameon": False,
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
            "savefig.dpi": 600,
        }
    )


def add_panel_label(ax: plt.Axes, label: str) -> None:
    """Add a compact panel label."""
    ax.text(-0.12, 1.05, label, transform=ax.transAxes, fontweight="bold", fontsize=9, va="top")


def plot_tail_lag_figure(summary: dict[str, Any]) -> None:
    """Create a four-panel figure summarizing the front-tail lag mechanism."""
    dep = read_table("paper2_time_resolved_deposition_source.csv").copy()
    quant = read_table("paper2_908_spatial_quantiles.csv").copy()
    cdf = read_table("paper2_908_spatial_cdf_curves.csv").copy()
    localized = read_table("paper2_fig7_localized_time_dynamics_source.csv").copy()

    dep["tail_bulk_gap_over_L"] = dep["x_q99_over_L"] - dep["x_mean_over_L"]
    dep["front_to_blockage_gap_over_L"] = dep["x_q99_over_L"] - dep["blockage_centroid_over_L"]
    quant["tail_bulk_gap_over_L"] = quant["x_max_over_L"] - quant["x_p99_over_L"]
    localized["released_fraction"] = 1.0 - localized["source_fraction"]

    setup_style()
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 6.1), dpi=600)
    plt.subplots_adjust(left=0.08, right=0.98, bottom=0.08, top=0.93, wspace=0.35, hspace=0.42)
    ax = axes[0, 0]
    ax.plot(dep["elapsed_time"] * 1000.0, dep["x_mean_over_L"], color="#0072B2", lw=1.2, label="mean")
    ax.plot(dep["elapsed_time"] * 1000.0, dep["x_q99_over_L"], color="#D55E00", lw=1.2, label="q99")
    ax.plot(
        dep["elapsed_time"] * 1000.0,
        dep["blockage_centroid_over_L"],
        color="#009E73",
        lw=1.2,
        label="blockage centroid",
    )
    ax.axvline(summary["representative_first_BTC_time_s"] * 1000.0, color="0.25", ls="--", lw=0.8)
    ax.set_xlabel("elapsed time (ms)")
    ax.set_ylabel("position, x/L")
    ax.set_ylim(0.0, 1.05)
    ax.legend(loc="upper left", ncol=1, fontsize=6.7)
    ax.set_title("Tail-bulk separation", fontsize=8)
    add_panel_label(ax, "a")

    ax = axes[0, 1]
    ax.scatter(
        dep["front_to_blockage_gap_over_L"],
        dep["BTC"],
        c=dep["elapsed_time"] * 1000.0,
        cmap="viridis",
        s=24,
        edgecolor="none",
    )
    fit = summary["representative_tail_gap_to_BTC_fit"]
    xs = np.linspace(float(dep["front_to_blockage_gap_over_L"].min()), float(dep["front_to_blockage_gap_over_L"].max()), 80)
    ax.plot(xs, fit["slope"] * xs + fit["intercept"], color="0.2", lw=0.9)
    ax.set_xlabel(r"q99-front minus blockage centroid, $\Delta x/L$")
    ax.set_ylabel("BTC")
    ax.set_title("Weak breakthrough after separation", fontsize=8)
    ax.text(0.04, 0.90, rf"$R^2={fit['r2']:.2f}$", transform=ax.transAxes, fontsize=7)
    add_panel_label(ax, "b")

    ax = axes[1, 0]
    selected_steps = [quant["step"].min(), 180000, 380000, quant["step"].max()]
    colors = ["#0072B2", "#CC79A7", "#E69F00", "#D55E00"]
    for step, color in zip(selected_steps, colors):
        subset = cdf[cdf["step"].eq(step)]
        if subset.empty:
            continue
        label = f"{float(subset['time_s'].iloc[0]) * 1000:.2f} ms"
        ax.semilogy(subset["x_over_L"], subset["survival"].clip(lower=1.0e-6), color=color, lw=1.1, label=label)
    ax.axvline(0.95, color="0.4", ls="--", lw=0.8)
    ax.set_xlabel("position, x/L")
    ax.set_ylabel("survival fraction")
    ax.set_ylim(8.0e-6, 1.2)
    ax.set_title("Rare-front survival tail", fontsize=8)
    ax.legend(loc="lower left", fontsize=6.5)
    add_panel_label(ax, "c")

    ax = axes[1, 1]
    label_map = {
        "906_upstream_source_continue_1M_to_4M": "upstream 15k",
        "907_downstream_source_dt5e9_to_10ms": "downstream 15k",
        "908_high_inventory_dt5e9_to_10ms": "center 30k",
    }
    colors = ["#0072B2", "#009E73", "#CC79A7"]
    for color, (job_id, group) in zip(colors, localized.groupby("job_id", sort=True)):
        label = label_map.get(job_id, str(job_id))
        ax.plot(group["time_ms"], group["source_fraction"], color=color, lw=1.1, label=label)
        ax.plot(group["time_ms"], group["downstream_fraction"], color=color, lw=0.9, ls="--")
    ax.plot([], [], color="0.2", lw=1.1, label="retained")
    ax.plot([], [], color="0.2", lw=0.9, ls="--", label="downstream")
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("fraction")
    ax.set_ylim(-0.03, 1.05)
    ax.set_title("Retained bulk dominates", fontsize=8)
    ax.legend(loc="center right", fontsize=5.8, handlelength=1.5)
    add_panel_label(ax, "d")

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for suffix in (".png", ".pdf", ".svg"):
        fig.savefig(OUT_FIG.with_suffix(suffix), bbox_inches="tight")
    plt.close(fig)


def write_outputs(source: pd.DataFrame, events: pd.DataFrame, summary: dict[str, Any]) -> None:
    """Write source tables, JSON summary and a compact Markdown note."""
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    NOTE_DIR.mkdir(parents=True, exist_ok=True)
    source.to_csv(OUT_SOURCE, index=False)
    events.to_csv(OUT_EVENTS, index=False)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    lines = [
        "# Tail-Lag Mechanism Mining",
        "",
        f"Decision: `{summary['decision']}`",
        f"Representative first BTC time: {summary['representative_first_BTC_time_s']:.5f} s",
        f"Representative final BTC: {summary['representative_final_BTC']:.5f}",
        f"Representative maximum q99-front/blockage-centroid gap: {summary['representative_max_front_to_blockage_gap_over_L']:.3f} L",
        f"High-inventory final sparse-tail fraction beyond 0.95L: {summary['high_inventory_908_final_fraction_x_gt_0p95']:.6g}",
        f"Localized-release maximum front-bulk gap: {summary['localized_max_front_bulk_gap_over_L']:.3f} L",
        "",
        "## Boundary",
        "",
        summary["claim_boundary"],
    ]
    OUT_NOTE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    """Run the tail-lag mechanism mining workflow."""
    source, events, summary = build_tail_lag_metrics()
    write_outputs(source, events, summary)
    plot_tail_lag_figure(summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
