#!/usr/bin/env python3
"""Mine cross-observable mechanism indicators from Paper 2 source tables."""

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

OUT_SOURCE = TABLE_DIR / "paper2_deep_mechanism_mining_source.csv"
OUT_CORR = TABLE_DIR / "paper2_deep_mechanism_correlation_source.csv"
OUT_JSON = DATA_DIR / "paper2_deep_mechanism_mining.json"
OUT_NOTE = NOTE_DIR / "paper2_deep_mechanism_mining.md"
OUT_FIG = FIG_DIR / "paper2_figS27_deep_mechanism_mining"


def read_table(name: str) -> pd.DataFrame:
    """Read a required Paper 2 source table."""
    path = TABLE_DIR / name
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def minmax(values: pd.Series) -> pd.Series:
    """Return a 0--1 normalized series, preserving zeros for constant inputs."""
    arr = values.astype(float)
    vmin = float(arr.min())
    vmax = float(arr.max())
    if np.isclose(vmax, vmin):
        return pd.Series(np.zeros(len(arr)), index=arr.index)
    return (arr - vmin) / (vmax - vmin)


def linear_fit(x: np.ndarray, y: np.ndarray) -> dict[str, float]:
    """Return slope, intercept and R2 for a simple linear fit."""
    if len(x) < 2:
        return {"slope": float("nan"), "intercept": float("nan"), "r2": float("nan")}
    slope, intercept = np.polyfit(x, y, 1)
    pred = slope * x + intercept
    ss_res = float(np.sum((y - pred) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return {"slope": float(slope), "intercept": float(intercept), "r2": float(r2)}


def build_deep_metrics() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Build derived mechanism metrics and an exploratory correlation matrix."""
    drive = read_table("paper2_drag_scaling_source.csv").copy()
    drive = drive[drive["evidence_family"].eq("drive_state")].copy()
    loading = read_table("paper2_fig4_loading_summary_source.csv").copy()
    openfoam = read_table("paper2_openfoam_pressure_evidence_source.csv").copy()
    localized = read_table("explicit_localized_production_summary.csv").copy()
    split908 = read_table("paper2_908_population_split_evidence.csv").iloc[0].to_dict()
    dim = read_table("paper2_dimensionless_mechanism_map_source.csv").copy()

    drive["log10_drag_to_weight"] = np.log10(drive["stokes_drag_to_weight_recomputed"].astype(float))
    drive_fit = linear_fit(
        drive["log10_drag_to_weight"].to_numpy(float),
        drive["final_BTC"].to_numpy(float),
    )

    loading = loading.merge(
        openfoam[["debris_total_number", "relative_delta_p_to_first_valid_case"]],
        on="debris_total_number",
        how="left",
    )
    loading["pressure_increase_percent"] = (
        loading["relative_delta_p_to_first_valid_case"].astype(float) - 1.0
    ) * 100.0
    loading["normalized_Bmax"] = minmax(loading["subvoxel_max_blockage_ratio"])
    loading["normalized_BTC"] = minmax(loading["final_BTC"])
    loading["normalized_pressure_increase"] = minmax(loading["pressure_increase_percent"])
    loading_fit = linear_fit(
        loading["debris_total_number"].to_numpy(float) / 1000.0,
        loading["subvoxel_max_blockage_ratio"].to_numpy(float),
    )
    pressure_fit = linear_fit(
        loading["debris_total_number"].to_numpy(float) / 1000.0,
        loading["pressure_increase_percent"].to_numpy(float),
    )

    localized["front_bulk_gap_over_L"] = (
        localized["final_x_max_over_L"].astype(float) - localized["final_x_q99_over_L"].astype(float)
    )
    localized["rare_tail_fraction_beyond_0p95"] = 0.0
    localized.loc[
        localized["job_id"].eq("908_high_inventory_dt5e9_to_10ms"),
        "rare_tail_fraction_beyond_0p95",
    ] = float(split908["fraction_beyond_0p95"])

    corr_cols = [
        "final_BTC",
        "max_blockage_ratio",
        "connectivity_loss",
        "front_bulk_gap_over_L",
        "source_fraction",
        "profile_pressure_increase_ratio",
        "voxel_conductance_loss",
    ]
    corr_input = dim[[col for col in corr_cols if col in dim.columns]].apply(pd.to_numeric, errors="coerce")
    corr = corr_input.corr(method="spearman", min_periods=3).fillna(0.0)
    corr_long = corr.reset_index().melt(id_vars="index", var_name="metric_y", value_name="spearman_r")
    corr_long = corr_long.rename(columns={"index": "metric_x"})

    rows: list[dict[str, Any]] = []
    for _, row in drive.iterrows():
        rows.append(
            {
                "axis": "drive",
                "case_label": row["case_label"],
                "drive_to_weight": row["stokes_drag_to_weight_recomputed"],
                "final_BTC": row["final_BTC"],
                "max_blockage_ratio": row["max_blockage_ratio"],
                "connectivity_loss": row["connectivity_loss"],
                "derived_indicator": "BTC rises with Stokes-scale drive while connectivity loss remains zero",
            }
        )
    for _, row in localized.iterrows():
        rows.append(
            {
                "axis": "localized_source",
                "case_label": row["job_id"],
                "source_fraction": row["final_source_fraction"],
                "downstream_fraction": row["final_downstream_fraction"],
                "outlet_fraction": row["final_outlet_fraction"],
                "front_bulk_gap_over_L": row["front_bulk_gap_over_L"],
                "rare_tail_fraction_beyond_0p95": row["rare_tail_fraction_beyond_0p95"],
                "derived_indicator": "Source-retained bulk can coexist with a sparse near-outlet front",
            }
        )
    for _, row in loading.iterrows():
        rows.append(
            {
                "axis": "loading_hydraulic",
                "case_label": row["case_name"],
                "debris_total_number": row["debris_total_number"],
                "final_BTC": row["final_BTC"],
                "max_blockage_ratio": row["subvoxel_max_blockage_ratio"],
                "pressure_increase_percent": row["pressure_increase_percent"],
                "connectivity_loss": row["connectivity_loss"],
                "Ib_no_pressure": row["Ib_no_pressure"],
                "derived_indicator": "Inventory amplifies local blockage much more than cropped-domain pressure response",
            }
        )
    source = pd.DataFrame(rows)

    summary = {
        "decision": "deep_mechanism_mining_ready",
        "drive_fit_log10_FdW_to_BTC": drive_fit,
        "loading_fit_Bmax_per_1000_particles": loading_fit,
        "pressure_fit_percent_per_1000_particles": pressure_fit,
        "max_final_BTC": float(drive["final_BTC"].max()),
        "max_loading_Bmax": float(loading["subvoxel_max_blockage_ratio"].max()),
        "max_openfoam_pressure_increase_percent": float(loading["pressure_increase_percent"].max()),
        "max_localized_front_bulk_gap_over_L": float(localized["front_bulk_gap_over_L"].max()),
        "max_rare_tail_fraction_beyond_0p95": float(localized["rare_tail_fraction_beyond_0p95"].max()),
        "connectivity_loss_cases": int((pd.to_numeric(dim["connectivity_loss"], errors="coerce").fillna(0) > 0).sum()),
        "source_rows": len(source),
        "correlation_metrics": list(corr.columns),
        "claim_boundary": (
            "Derived data-mining indicators from existing Paper 2 source tables; exploratory synthesis only, "
            "not a fitted universal transition law and not pressure-calibrated safety evidence."
        ),
    }
    return source, corr_long, summary


def setup_axes() -> tuple[plt.Figure, np.ndarray]:
    """Create a publication-sized four-panel figure."""
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
            "savefig.dpi": 600,
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.75), dpi=600)
    return fig, axes


def add_label(ax: plt.Axes, label: str) -> None:
    """Add a compact panel label."""
    ax.text(-0.13, 1.05, label, transform=ax.transAxes, fontweight="bold", fontsize=9, va="top")


def plot_figure(summary: dict[str, Any]) -> None:
    """Create the deep-mechanism-mining supplementary figure."""
    drive = read_table("paper2_drag_scaling_source.csv")
    drive = drive[drive["evidence_family"].eq("drive_state")].copy()
    loading = read_table("paper2_fig4_loading_summary_source.csv").merge(
        read_table("paper2_openfoam_pressure_evidence_source.csv")[
            ["debris_total_number", "relative_delta_p_to_first_valid_case"]
        ],
        on="debris_total_number",
        how="left",
    )
    localized = read_table("explicit_localized_production_summary.csv")
    dim = read_table("paper2_dimensionless_mechanism_map_source.csv")

    loading["pressure_increase_percent"] = (loading["relative_delta_p_to_first_valid_case"] - 1.0) * 100.0
    loading["normalized_Bmax"] = minmax(loading["subvoxel_max_blockage_ratio"])
    loading["normalized_BTC"] = minmax(loading["final_BTC"])
    loading["normalized_pressure_increase"] = minmax(loading["pressure_increase_percent"])
    localized["front_bulk_gap_over_L"] = localized["final_x_max_over_L"] - localized["final_x_q99_over_L"]

    fig, axes = setup_axes()
    ax = axes[0, 0]
    colors = ["#0072B2", "#009E73", "#D55E00"]
    ax.scatter(
        drive["stokes_drag_to_weight_recomputed"],
        drive["final_BTC"],
        s=80 + 1.2e6 * drive["max_blockage_ratio"],
        c=colors,
        edgecolor="black",
        linewidth=0.5,
        zorder=3,
    )
    for _, row in drive.iterrows():
        label = str(row["case_label"]).replace("_", "\n")
        if row["final_BTC"] > 0.05:
            offset = (-86, -2)
        elif row["final_BTC"] > 0.0:
            offset = (4, -18)
        else:
            offset = (4, 6)
        ax.annotate(
            label,
            (row["stokes_drag_to_weight_recomputed"], row["final_BTC"]),
            xytext=offset,
            textcoords="offset points",
            fontsize=6,
        )
    ax.set_xscale("log")
    ax.set_xlabel(r"Stokes drag-to-weight ratio, $F_d/W$")
    ax.set_ylabel("Final BTC")
    ax.set_ylim(-0.004, 0.095)
    ax.set_title("Drive-axis breakthrough without topology loss", fontsize=8)
    ax.grid(True, color="0.9", linewidth=0.5)
    add_label(ax, "a")

    ax = axes[0, 1]
    labels = ["906\nupstream", "907\ndownstream", "908\nhigh inv."]
    x = np.arange(len(localized))
    ax.bar(x, localized["final_source_fraction"], color="#56B4E9", label="source retained")
    ax.bar(
        x,
        localized["final_downstream_fraction"],
        bottom=localized["final_source_fraction"],
        color="#E69F00",
        label="downstream",
    )
    ax.bar(
        x,
        localized["final_outlet_fraction"],
        bottom=localized["final_source_fraction"] + localized["final_downstream_fraction"],
        color="#CC79A7",
        label="outlet",
    )
    ax.scatter(x, localized["front_bulk_gap_over_L"], marker="D", s=28, color="black", label=r"$x_{max}-x_{99}$")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Fraction or normalized gap")
    ax.set_title("Localized release splits retained bulk and sparse front", fontsize=8)
    ax.legend(fontsize=6, loc="upper center", bbox_to_anchor=(0.5, 1.03), ncol=2, handlelength=1.2)
    add_label(ax, "b")

    ax = axes[1, 0]
    x = loading["debris_total_number"] / 1000.0
    ax.plot(x, loading["normalized_Bmax"], marker="o", color="#0072B2", label=r"$B_{max}$")
    ax.plot(x, loading["normalized_BTC"], marker="s", color="#D55E00", label="BTC")
    ax.plot(x, loading["normalized_pressure_increase"], marker="^", color="#009E73", label=r"$\Delta p$ increase")
    ax.set_xlabel(r"Injected debris count ($10^3$)")
    ax.set_ylabel("Normalized response")
    ax.set_title("Inventory responses do not collapse to one observable", fontsize=8)
    ax.grid(True, color="0.9", linewidth=0.5)
    ax.legend(fontsize=6, loc="best")
    ax.text(
        0.03,
        0.05,
        f"max $B_{{max}}$={summary['max_loading_Bmax']:.2e}\nmax $\\Delta p$={summary['max_openfoam_pressure_increase_percent']:.3f}%",
        transform=ax.transAxes,
        fontsize=6,
    )
    add_label(ax, "c")

    ax = axes[1, 1]
    corr_cols = ["final_BTC", "max_blockage_ratio", "connectivity_loss", "front_bulk_gap_over_L", "source_fraction"]
    corr_input = dim[[col for col in corr_cols if col in dim.columns]].apply(pd.to_numeric, errors="coerce")
    corr = corr_input.corr(method="spearman", min_periods=3).fillna(0.0)
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1)
    short = ["BTC", r"$B_{max}$", r"$C_{loss}$", "front gap", "source"]
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.index)))
    ax.set_xticklabels(short[: len(corr.columns)], rotation=35, ha="right")
    ax.set_yticklabels(short[: len(corr.index)])
    for i in range(corr.shape[0]):
        for j in range(corr.shape[1]):
            ax.text(j, i, f"{corr.iat[i, j]:.2f}", ha="center", va="center", fontsize=6)
    ax.set_title("Exploratory cross-observable correlation", fontsize=8)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cbar.set_label("Spearman r", fontsize=7)
    cbar.ax.tick_params(labelsize=6)
    add_label(ax, "d")

    fig.tight_layout(pad=1.1, w_pad=1.2, h_pad=1.45)
    for suffix in (".png", ".pdf", ".svg"):
        fig.savefig(OUT_FIG.with_suffix(suffix), bbox_inches="tight")
    plt.close(fig)


def write_note(summary: dict[str, Any]) -> None:
    """Write a Markdown note summarizing the mined mechanism indicators."""
    lines = [
        "# Paper 2 Deep Mechanism Mining",
        "",
        f"- Decision: `{summary['decision']}`",
        f"- Drive-axis log10(Fd/W) to BTC slope: {summary['drive_fit_log10_FdW_to_BTC']['slope']:.4g}",
        f"- Loading-axis Bmax slope per 1000 particles: {summary['loading_fit_Bmax_per_1000_particles']['slope']:.4g}",
        f"- OpenFOAM pressure-increase slope per 1000 particles: {summary['pressure_fit_percent_per_1000_particles']['slope']:.4g}% per 1000 particles",
        f"- Maximum localized front-bulk gap: {summary['max_localized_front_bulk_gap_over_L']:.4f} L",
        f"- Connectivity-loss cases in dimensionless map: {summary['connectivity_loss_cases']}",
        f"- Source table: `{OUT_SOURCE.relative_to(PROJECT_ROOT)}`",
        f"- Correlation table: `{OUT_CORR.relative_to(PROJECT_ROOT)}`",
        f"- Figure: `{OUT_FIG.with_suffix('.pdf').relative_to(PROJECT_ROOT)}`",
        f"- Boundary: {summary['claim_boundary']}",
        "",
    ]
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    """Generate deep mechanism mining tables, summary and figure."""
    source, corr, summary = build_deep_metrics()
    OUT_SOURCE.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    source.to_csv(OUT_SOURCE, index=False)
    corr.to_csv(OUT_CORR, index=False)
    OUT_JSON.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_note(summary)
    plot_figure(summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
