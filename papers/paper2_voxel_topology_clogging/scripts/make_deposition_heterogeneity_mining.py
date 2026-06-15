#!/usr/bin/env python3
"""Mine spatial heterogeneity of debris deposition from Paper 2 source tables."""

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

PROFILE_SOURCE = TABLE_DIR / "paper2_time_resolved_blockage_profile_source.csv"
DEPOSITION_SOURCE = TABLE_DIR / "paper2_time_resolved_deposition_source.csv"
DRIVE_PROFILE_SOURCE = TABLE_DIR / "paper2_fig3_blockage_profiles_source.csv"
OUT_TIME = TABLE_DIR / "paper2_deposition_heterogeneity_timeseries.csv"
OUT_DRIVE = TABLE_DIR / "paper2_deposition_heterogeneity_drive_source.csv"
OUT_JSON = DATA_DIR / "paper2_deposition_heterogeneity_mining.json"
OUT_NOTE = NOTE_DIR / "paper2_deposition_heterogeneity_mining.md"
OUT_FIG = FIG_DIR / "paper2_figS29_deposition_heterogeneity_mining"


def read_table(path: Path) -> pd.DataFrame:
    """Read a required CSV table."""
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def gini(values: np.ndarray) -> float:
    """Compute the Gini coefficient of a non-negative vector."""
    arr = np.asarray(values, dtype=float)
    if np.any(arr < 0):
        raise ValueError("Gini inputs must be non-negative.")
    total = float(arr.sum())
    if total <= 0:
        return 0.0
    ordered = np.sort(arr)
    cumulative = np.cumsum(ordered)
    n = len(ordered)
    return float((n + 1.0 - 2.0 * np.sum(cumulative) / cumulative[-1]) / n)


def profile_metrics(group: pd.DataFrame, x_col: str = "x_over_L") -> dict[str, float]:
    """Compute spatial heterogeneity metrics for one axial blockage profile."""
    weights = group["blockage_ratio"].to_numpy(dtype=float)
    x = group[x_col].to_numpy(dtype=float)
    n = len(weights)
    total = float(weights.sum())
    if n == 0:
        raise ValueError("Empty blockage profile.")
    if total <= 0:
        return {
            "total_blockage": 0.0,
            "peak_blockage": 0.0,
            "mean_blockage": 0.0,
            "peak_to_mean": 0.0,
            "gini": 0.0,
            "entropy_norm": 0.0,
            "participation_length_fraction": 0.0,
            "centroid_over_L": float("nan"),
            "spread_over_L": 0.0,
            "upstream_fraction_x_lt_0p2": 0.0,
            "downstream_fraction_x_gt_0p8": 0.0,
            "nonzero_bin_count": 0.0,
        }
    probability = weights / total
    positive = probability > 0
    entropy = -float(np.sum(probability[positive] * np.log(probability[positive]))) / np.log(n)
    participation = float(total**2 / np.sum(weights**2) / n)
    centroid = float(np.sum(x * weights) / total)
    spread = float(np.sqrt(np.sum(((x - centroid) ** 2) * weights) / total))
    mean = float(weights.mean())
    return {
        "total_blockage": total,
        "peak_blockage": float(weights.max()),
        "mean_blockage": mean,
        "peak_to_mean": float(weights.max() / mean) if mean > 0 else 0.0,
        "gini": gini(weights),
        "entropy_norm": entropy,
        "participation_length_fraction": participation,
        "centroid_over_L": centroid,
        "spread_over_L": spread,
        "upstream_fraction_x_lt_0p2": float(weights[x < 0.2].sum() / total),
        "downstream_fraction_x_gt_0p8": float(weights[x > 0.8].sum() / total),
        "nonzero_bin_count": float(np.count_nonzero(weights > 0)),
    }


def build_heterogeneity_metrics() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Build time-resolved and drive-state deposition heterogeneity metrics."""
    profile = read_table(PROFILE_SOURCE)
    deposition = read_table(DEPOSITION_SOURCE)
    drive_profile = read_table(DRIVE_PROFILE_SOURCE)

    time_rows: list[dict[str, Any]] = []
    for elapsed, group in profile.groupby("elapsed_time", sort=True):
        metrics = profile_metrics(group)
        dep_row = deposition[np.isclose(deposition["elapsed_time"], elapsed)]
        btc = float(dep_row["BTC"].iloc[0]) if not dep_row.empty else float("nan")
        particle_count = int(dep_row["particle_count"].iloc[0]) if not dep_row.empty else 0
        time_rows.append({"elapsed_time": float(elapsed), "BTC": btc, "particle_count": particle_count, **metrics})
    time_metrics = pd.DataFrame(time_rows)

    drive_rows: list[dict[str, Any]] = []
    max_x = float(drive_profile["x_center_m"].max())
    for role, group in drive_profile.groupby("role", sort=True):
        work = group.copy()
        work["x_over_L"] = work["x_center_m"] / max_x
        metrics = profile_metrics(work, x_col="x_over_L")
        first = group.iloc[0]
        drive_rows.append(
            {
                "role": role,
                "state_label": first["state_label"],
                "case_name": first["case_name"],
                "final_BTC": float(first["final_BTC"]),
                "drag_to_weight_ratio": float(first["drag_to_weight_ratio"]),
                **metrics,
            }
        )
    drive_metrics = pd.DataFrame(drive_rows)

    initial = time_metrics.iloc[0]
    final = time_metrics.iloc[-1]
    peak = time_metrics.iloc[int(time_metrics["peak_blockage"].idxmax())]
    summary = {
        "decision": "deposition_heterogeneity_ready",
        "time_frame_count": int(len(time_metrics)),
        "drive_state_count": int(len(drive_metrics)),
        "initial_gini": float(initial["gini"]),
        "final_gini": float(final["gini"]),
        "initial_peak_to_mean": float(initial["peak_to_mean"]),
        "final_peak_to_mean": float(final["peak_to_mean"]),
        "initial_participation_length_fraction": float(initial["participation_length_fraction"]),
        "final_participation_length_fraction": float(final["participation_length_fraction"]),
        "final_downstream_fraction_x_gt_0p8": float(final["downstream_fraction_x_gt_0p8"]),
        "peak_blockage_time_s": float(peak["elapsed_time"]),
        "peak_blockage_value": float(peak["peak_blockage"]),
        "peak_blockage_gini": float(peak["gini"]),
        "max_drive_state_downstream_fraction": float(drive_metrics["downstream_fraction_x_gt_0p8"].max()),
        "min_drive_state_gini": float(drive_metrics["gini"].min()),
        "claim_boundary": (
            "Derived from existing axial blockage profiles; describes spatial heterogeneity of numerical deposition "
            "fields, not pore-scale bridge statistics, experimental imaging or a universal clogging law."
        ),
    }
    return time_metrics, drive_metrics, summary


def setup_style() -> None:
    """Configure compact publication-style Matplotlib defaults."""
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


def plot_heterogeneity_figure(time_metrics: pd.DataFrame, drive_metrics: pd.DataFrame, summary: dict[str, Any]) -> None:
    """Create a four-panel deposition heterogeneity figure."""
    profile = read_table(PROFILE_SOURCE)
    pivot = profile.pivot_table(index="x_over_L", columns="elapsed_time", values="blockage_ratio", aggfunc="mean")
    t_ms = pivot.columns.to_numpy(dtype=float) * 1000.0
    x_over_l = pivot.index.to_numpy(dtype=float)
    z = pivot.to_numpy(dtype=float) * 1.0e6

    setup_style()
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.9), dpi=600)
    plt.subplots_adjust(left=0.08, right=0.98, bottom=0.08, top=0.93, wspace=0.34, hspace=0.42)

    ax = axes[0, 0]
    image = ax.pcolormesh(t_ms, x_over_l, z, shading="auto", cmap="cividis")
    ax.plot(time_metrics["elapsed_time"] * 1000.0, time_metrics["centroid_over_L"], color="white", lw=1.1)
    ax.set_xlabel("elapsed time (ms)")
    ax.set_ylabel("position, x/L")
    ax.set_title("Axial deposition field")
    fig.colorbar(image, ax=ax, pad=0.01, fraction=0.055, label=r"$B(x,t)$ ($\times 10^{-6}$)")
    add_panel_label(ax, "a")

    ax = axes[0, 1]
    ax.plot(time_metrics["elapsed_time"] * 1000.0, time_metrics["gini"], color="#D55E00", lw=1.15, label="Gini")
    ax.plot(
        time_metrics["elapsed_time"] * 1000.0,
        time_metrics["entropy_norm"],
        color="#0072B2",
        lw=1.15,
        label="entropy",
    )
    ax.plot(
        time_metrics["elapsed_time"] * 1000.0,
        time_metrics["participation_length_fraction"],
        color="#009E73",
        lw=1.15,
        label="participation",
    )
    ax.set_xlabel("elapsed time (ms)")
    ax.set_ylabel("normalized metric")
    ax.set_ylim(-0.03, 1.03)
    ax.set_title("Localization relaxes into spreading")
    ax.legend(loc="center right", fontsize=6.4)
    add_panel_label(ax, "b")

    ax = axes[1, 0]
    ax.scatter(
        time_metrics["peak_to_mean"],
        time_metrics["BTC"],
        c=time_metrics["elapsed_time"] * 1000.0,
        cmap="viridis",
        s=24,
        edgecolor="none",
    )
    ax.set_xlabel("peak/mean blockage")
    ax.set_ylabel("BTC")
    ax.set_title("Breakthrough grows after peak dilution")
    ax.invert_xaxis()
    add_panel_label(ax, "c")

    ax = axes[1, 1]
    order = drive_metrics.sort_values("drag_to_weight_ratio")
    sizes = 60 + 7000 * order["peak_blockage"]
    scatter = ax.scatter(
        order["downstream_fraction_x_gt_0p8"],
        order["gini"],
        s=sizes,
        c=order["final_BTC"],
        cmap="plasma",
        edgecolor="black",
        linewidth=0.4,
    )
    for _, row in order.iterrows():
        label = str(row["state_label"])
        offset = (6, -10) if "low" in label else (6, 4)
        ax.annotate(
            label,
            (row["downstream_fraction_x_gt_0p8"], row["gini"]),
            xytext=offset,
            textcoords="offset points",
            fontsize=6.2,
        )
    ax.set_xlim(-0.008, 0.205)
    ax.set_ylim(0.645, 0.835)
    ax.set_xlabel("downstream blockage fraction, x/L > 0.8")
    ax.set_ylabel("Gini coefficient")
    ax.set_title("Drive states separate spread from tailing")
    fig.colorbar(scatter, ax=ax, pad=0.01, fraction=0.055, label="final BTC")
    add_panel_label(ax, "d")

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for suffix in (".png", ".pdf", ".svg"):
        fig.savefig(OUT_FIG.with_suffix(suffix), bbox_inches="tight")
    plt.close(fig)


def write_outputs(time_metrics: pd.DataFrame, drive_metrics: pd.DataFrame, summary: dict[str, Any]) -> None:
    """Write source tables, summary JSON and a Markdown note."""
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    NOTE_DIR.mkdir(parents=True, exist_ok=True)
    time_metrics.to_csv(OUT_TIME, index=False)
    drive_metrics.to_csv(OUT_DRIVE, index=False)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    lines = [
        "# Deposition Heterogeneity Mining",
        "",
        f"Decision: `{summary['decision']}`",
        f"Initial to final Gini: {summary['initial_gini']:.3f} to {summary['final_gini']:.3f}",
        f"Initial to final peak/mean blockage: {summary['initial_peak_to_mean']:.2f} to {summary['final_peak_to_mean']:.2f}",
        f"Initial to final participation length fraction: {summary['initial_participation_length_fraction']:.3f} to {summary['final_participation_length_fraction']:.3f}",
        f"Final downstream blockage fraction: {summary['final_downstream_fraction_x_gt_0p8']:.3f}",
        "",
        "## Boundary",
        "",
        summary["claim_boundary"],
    ]
    OUT_NOTE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    """Run the deposition heterogeneity mining workflow."""
    time_metrics, drive_metrics, summary = build_heterogeneity_metrics()
    write_outputs(time_metrics, drive_metrics, summary)
    plot_heterogeneity_figure(time_metrics, drive_metrics, summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
