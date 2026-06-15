#!/usr/bin/env python3
"""Build a cross-observable response map for Paper 2.

The analysis converts existing source tables into a compact response matrix.
It is intended to support the mechanism claim that breakthrough, source
release, sparse-front advance, local blockage, pressure proxies and topology
loss are not interchangeable observables in the present pre-clogging window.
No fitted law is inferred from the small bounded data set.
"""

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

DEFAULT_REPRESENTATIVE = TABLE_DIR / "paper2_fig3_representative_state_source.csv"
DEFAULT_LOADING = TABLE_DIR / "paper2_fig4_loading_summary_source.csv"
DEFAULT_PRESSURE = TABLE_DIR / "paper2_pressure_proxy_source.csv"
DEFAULT_VOXEL_PRESSURE = TABLE_DIR / "paper2_voxel_pressure_pilot_source.csv"
DEFAULT_LOCALIZED = TABLE_DIR / "paper2_localized_mechanism_axes.csv"

OUT_CASE_TABLE = TABLE_DIR / "paper2_observable_response_cases.csv"
OUT_RESPONSE_TABLE = TABLE_DIR / "paper2_observable_response_summary.csv"
OUT_JSON = DATA_DIR / "paper2_observable_response_map.json"
OUT_MD = NOTE_DIR / "paper2_observable_response_map.md"
FIG_STEM = "paper2_figS21_observable_response_map"


METRIC_LABELS = {
    "released_fraction": "released",
    "outlet_fraction": "BTC/outlet",
    "penetration_over_L": "penetration",
    "front_bulk_gap_over_L": "front-bulk gap",
    "max_blockage_ratio": "local blockage",
    "pressure_proxy_ratio": "pressure proxy",
    "voxel_conductance_loss": "conductance loss",
    "connectivity_loss": "connectivity loss",
}


def configure_matplotlib() -> None:
    """Configure a compact publication plotting style."""

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


def load_inputs(
    representative_path: Path = DEFAULT_REPRESENTATIVE,
    loading_path: Path = DEFAULT_LOADING,
    pressure_path: Path = DEFAULT_PRESSURE,
    voxel_pressure_path: Path = DEFAULT_VOXEL_PRESSURE,
    localized_path: Path = DEFAULT_LOCALIZED,
) -> dict[str, pd.DataFrame]:
    """Load and validate source tables for the response map."""

    paths = {
        "representative": representative_path,
        "loading": loading_path,
        "pressure": pressure_path,
        "voxel_pressure": voxel_pressure_path,
        "localized": localized_path,
    }
    missing_files = [str(path) for path in paths.values() if not path.exists()]
    if missing_files:
        raise FileNotFoundError(f"Missing source files: {missing_files}")

    tables = {name: pd.read_csv(path) for name, path in paths.items()}
    required = {
        "representative": {
            "role",
            "drag_to_weight_ratio",
            "final_BTC",
            "x_mean_over_L",
            "subvoxel_max_blockage_ratio",
            "voxel_outlet_connected_fraction_x",
        },
        "loading": {
            "debris_total_number",
            "final_BTC",
            "x_q99_m",
            "subvoxel_max_blockage_ratio",
            "connectivity_loss",
            "Ib_no_pressure",
        },
        "pressure": {
            "debris_total_number",
            "profile_pressure_increase_ratio",
        },
        "voxel_pressure": {
            "case_label",
            "debris_total_number",
            "conductance_loss",
        },
        "localized": {
            "label",
            "particle_count",
            "final_released_fraction",
            "final_downstream_fraction",
            "final_outlet_fraction",
            "final_x99_over_L",
            "final_xmax_over_L",
            "final_front_bulk_gap_over_L",
        },
    }
    missing_cols: dict[str, list[str]] = {}
    for name, cols in required.items():
        missing = sorted(cols.difference(tables[name].columns))
        if missing:
            missing_cols[name] = missing
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    return tables


def _loading_penetration_over_l(x_q99_m: float) -> float:
    """Convert a loading-scan q99 coordinate to normalized axial position."""

    domain_length_m = 0.045
    return float(x_q99_m) / domain_length_m


def build_case_table(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Assemble comparable observables from representative, loading and localized cases."""

    rows: list[dict[str, Any]] = []

    for row in tables["representative"].itertuples(index=False):
        rows.append(
            {
                "case_group": "drive scan",
                "case_label": str(row.role).replace("_", " "),
                "control_label": "Fd/W",
                "control_value": float(row.drag_to_weight_ratio),
                "released_fraction": np.nan,
                "outlet_fraction": float(row.final_BTC),
                "penetration_over_L": float(row.x_mean_over_L),
                "front_bulk_gap_over_L": np.nan,
                "max_blockage_ratio": float(row.subvoxel_max_blockage_ratio),
                "pressure_proxy_ratio": np.nan,
                "voxel_conductance_loss": np.nan,
                "connectivity_loss": float(1.0 - row.voxel_outlet_connected_fraction_x / row.voxel_outlet_connected_fraction_x),
            }
        )

    pressure = tables["pressure"].set_index("debris_total_number")
    voxel_pressure = tables["voxel_pressure"].set_index("debris_total_number")
    for row in tables["loading"].sort_values("debris_total_number").itertuples(index=False):
        n = int(row.debris_total_number)
        conductance_loss = np.nan
        if n in voxel_pressure.index:
            conductance_loss = float(voxel_pressure.loc[n, "conductance_loss"])
        rows.append(
            {
                "case_group": "loading scan",
                "case_label": f"N={n}",
                "control_label": "Ndebris",
                "control_value": n,
                "released_fraction": np.nan,
                "outlet_fraction": float(row.final_BTC),
                "penetration_over_L": _loading_penetration_over_l(float(row.x_q99_m)),
                "front_bulk_gap_over_L": np.nan,
                "max_blockage_ratio": float(row.subvoxel_max_blockage_ratio),
                "pressure_proxy_ratio": float(pressure.loc[n, "profile_pressure_increase_ratio"]),
                "voxel_conductance_loss": conductance_loss,
                "connectivity_loss": float(row.connectivity_loss),
            }
        )

    for row in tables["localized"].itertuples(index=False):
        rows.append(
            {
                "case_group": "localized release",
                "case_label": str(row.label),
                "control_label": "source/inventory",
                "control_value": int(row.particle_count),
                "released_fraction": float(row.final_released_fraction),
                "outlet_fraction": float(row.final_outlet_fraction),
                "penetration_over_L": float(row.final_x99_over_L),
                "front_bulk_gap_over_L": float(row.final_front_bulk_gap_over_L),
                "max_blockage_ratio": np.nan,
                "pressure_proxy_ratio": np.nan,
                "voxel_conductance_loss": np.nan,
                "connectivity_loss": 0.0,
            }
        )

    case_table = pd.DataFrame(rows)
    if case_table.empty:
        raise ValueError("No cases were assembled for observable response analysis.")
    return case_table


def normalize_case_table(case_table: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:
    """Normalize each metric to [0, 1] across finite values."""

    normalized = case_table[metrics].astype(float).copy()
    for metric in metrics:
        finite = np.isfinite(normalized[metric].to_numpy(dtype=float))
        if finite.sum() == 0:
            continue
        lo = float(normalized.loc[finite, metric].min())
        hi = float(normalized.loc[finite, metric].max())
        if np.isclose(hi, lo):
            normalized.loc[finite, metric] = 0.0
        else:
            normalized.loc[finite, metric] = (normalized.loc[finite, metric] - lo) / (hi - lo)
    return normalized


def _spearman_by_rank(x: pd.Series, y: pd.Series) -> float:
    """Compute a small-sample Spearman rank correlation without SciPy."""

    data = pd.DataFrame({"x": x.astype(float), "y": y.astype(float)}).dropna()
    if len(data) < 3:
        return float("nan")
    if np.isclose(data["x"].max(), data["x"].min()) or np.isclose(data["y"].max(), data["y"].min()):
        return float("nan")
    return float(data["x"].rank().corr(data["y"].rank()))


def build_response_summary(case_table: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Summarize response amplitude and key decoupling indicators."""

    metrics = list(METRIC_LABELS)
    rows: list[dict[str, Any]] = []
    for metric in metrics:
        values = case_table[metric].astype(float)
        finite = values[np.isfinite(values)]
        if finite.empty:
            continue
        rows.append(
            {
                "metric": metric,
                "metric_label": METRIC_LABELS[metric],
                "finite_case_count": int(finite.size),
                "min_value": float(finite.min()),
                "max_value": float(finite.max()),
                "absolute_range": float(finite.max() - finite.min()),
                "all_zero": bool(np.isclose(finite.max(), 0.0) and np.isclose(finite.min(), 0.0)),
                "groups_available": ";".join(sorted(case_table.loc[finite.index, "case_group"].unique())),
            }
        )
    summary_table = pd.DataFrame(rows)

    localized = case_table[case_table["case_group"] == "localized release"].copy()
    loading = case_table[case_table["case_group"] == "loading scan"].copy()
    drive = case_table[case_table["case_group"] == "drive scan"].copy()

    idx_gap = localized["front_bulk_gap_over_L"].idxmax()
    idx_release = localized["released_fraction"].idxmax()
    idx_pressure = loading["pressure_proxy_ratio"].idxmax()
    idx_blockage = loading["max_blockage_ratio"].idxmax()

    summary = {
        "case_count": int(len(case_table)),
        "case_group_counts": {str(k): int(v) for k, v in case_table["case_group"].value_counts().sort_index().items()},
        "metric_count": int(len(summary_table)),
        "connectivity_loss_max": float(case_table["connectivity_loss"].max(skipna=True)),
        "localized_highest_front_gap_case": str(case_table.loc[idx_gap, "case_label"]),
        "localized_highest_release_case": str(case_table.loc[idx_release, "case_label"]),
        "loading_highest_pressure_case": str(case_table.loc[idx_pressure, "case_label"]),
        "loading_highest_blockage_case": str(case_table.loc[idx_blockage, "case_label"]),
        "localized_release_front_gap_spearman": _spearman_by_rank(
            localized["released_fraction"],
            localized["front_bulk_gap_over_L"],
        ),
        "loading_inventory_blockage_spearman": _spearman_by_rank(
            loading["control_value"],
            loading["max_blockage_ratio"],
        ),
        "loading_inventory_pressure_spearman": _spearman_by_rank(
            loading["control_value"],
            loading["pressure_proxy_ratio"],
        ),
        "drive_drag_btc_spearman": _spearman_by_rank(
            drive["control_value"],
            drive["outlet_fraction"],
        ),
        "claim_boundary": (
            "Derived cross-observable synthesis of existing DEM and voxel post-processing outputs. "
            "It supports mechanism separation only; it is not a fitted response law, not a completed "
            "BTC for the high-inventory case, not CFD validation and not a pressure-calibrated "
            "critical-clogging criterion."
        ),
    }
    return summary_table, summary


def draw_response_map(case_table: pd.DataFrame, response_summary: pd.DataFrame, out_stem: str = FIG_STEM) -> None:
    """Draw the observable response heatmap and response-amplitude panel."""

    configure_matplotlib()
    metrics = list(METRIC_LABELS)
    normalized = normalize_case_table(case_table, metrics)
    heat = normalized.to_numpy(dtype=float)
    masked = np.ma.masked_invalid(heat)

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(7.2, 3.75),
        gridspec_kw={"width_ratios": [1.68, 1.00], "wspace": 0.70},
        constrained_layout=False,
    )
    ax = axes[0]
    cmap = mpl.colormaps["viridis"].copy()
    cmap.set_bad("#eeeeee")
    im = ax.imshow(masked, aspect="auto", cmap=cmap, vmin=0.0, vmax=1.0)
    ax.set_xticks(np.arange(len(metrics)))
    ax.set_xticklabels([METRIC_LABELS[m] for m in metrics], rotation=45, ha="right")
    ax.set_yticks(np.arange(len(case_table)))
    ax.set_yticklabels(case_table["case_label"].tolist())
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title("Normalized observable response")
    ax.text(-0.13, 1.06, "a", transform=ax.transAxes, weight="bold", fontsize=9, va="top")
    cbar = fig.colorbar(im, ax=ax, fraction=0.040, pad=0.020)
    cbar.ax.set_title("scaled", fontsize=7.2, pad=4)

    ax2 = axes[1]
    localized = case_table[case_table["case_group"] == "localized release"]
    loading = case_table[case_table["case_group"] == "loading scan"]
    drive = case_table[case_table["case_group"] == "drive scan"]
    contrasts = pd.DataFrame(
        [
            {
                "contrast": "Fd/W-BTC",
                "rank_association": _spearman_by_rank(drive["control_value"], drive["outlet_fraction"]),
                "color": "#0072B2",
            },
            {
                "contrast": "N-blockage",
                "rank_association": _spearman_by_rank(loading["control_value"], loading["max_blockage_ratio"]),
                "color": "#0072B2",
            },
            {
                "contrast": "N-pressure proxy",
                "rank_association": _spearman_by_rank(loading["control_value"], loading["pressure_proxy_ratio"]),
                "color": "#0072B2",
            },
            {
                "contrast": "release-gap",
                "rank_association": _spearman_by_rank(localized["released_fraction"], localized["front_bulk_gap_over_L"]),
                "color": "#D55E00",
            },
            {
                "contrast": "connectivity loss",
                "rank_association": 0.0,
                "color": "#777777",
            },
        ]
    )
    y = np.arange(len(contrasts))
    ax2.axvline(0.0, color="#555555", linewidth=0.75)
    ax2.scatter(
        contrasts["rank_association"],
        y,
        s=42,
        color=contrasts["color"],
        edgecolor="#222222",
        linewidth=0.35,
        zorder=3,
    )
    for row in contrasts.itertuples(index=False):
        ax2.plot([0.0, row.rank_association], [y[contrasts.index[contrasts["contrast"] == row.contrast][0]]] * 2, color=row.color, linewidth=1.0, alpha=0.75)
    ax2.set_yticks(y)
    ax2.set_yticklabels(contrasts["contrast"])
    ax2.set_xlim(-1.08, 1.08)
    ax2.set_xlabel("rank association")
    ax2.set_title("Axis-specific response")
    ax2.grid(axis="x", linewidth=0.35, alpha=0.35)
    ax2.text(-0.20, 1.06, "b", transform=ax2.transAxes, weight="bold", fontsize=9, va="top")

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "pdf", "svg"):
        fig.savefig(FIG_DIR / f"{out_stem}.{suffix}", dpi=450 if suffix == "png" else None, bbox_inches="tight")

    gray_fig, gray_ax = plt.subplots(figsize=(3.4, 2.5))
    gray = np.ma.masked_invalid(heat)
    gray_cmap = mpl.colormaps["Greys"].copy()
    gray_cmap.set_bad("#eeeeee")
    gray_ax.imshow(gray, aspect="auto", cmap=gray_cmap, vmin=0.0, vmax=1.0)
    gray_ax.set_xticks([])
    gray_ax.set_yticks([])
    gray_ax.set_title("grayscale preview", fontsize=8)
    gray_fig.savefig(FIG_DIR / f"{out_stem}_gray_preview.png", dpi=300, bbox_inches="tight")
    plt.close(gray_fig)
    plt.close(fig)


def write_outputs(case_table: pd.DataFrame, response_summary: pd.DataFrame, summary: dict[str, Any]) -> None:
    """Write source tables, JSON and Markdown report."""

    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    NOTE_DIR.mkdir(parents=True, exist_ok=True)

    case_table.to_csv(OUT_CASE_TABLE, index=False)
    response_summary.to_csv(OUT_RESPONSE_TABLE, index=False)
    OUT_JSON.write_text(
        json.dumps(
            {
                "summary": summary,
                "case_table": str(OUT_CASE_TABLE.relative_to(PROJECT_ROOT)),
                "response_table": str(OUT_RESPONSE_TABLE.relative_to(PROJECT_ROOT)),
                "figure": str((FIG_DIR / f"{FIG_STEM}.pdf").relative_to(PROJECT_ROOT)),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    lines = [
        "# Paper 2 Observable Response Map",
        "",
        "This derived analysis normalizes existing DEM and voxel observables across drive-scan, loading-scan and localized-release cases.",
        "",
        "## Main results",
        "",
        f"- Cases included: {summary['case_count']}.",
        f"- Connectivity-loss maximum: {summary['connectivity_loss_max']:.3g}.",
        f"- Highest localized front-bulk gap: {summary['localized_highest_front_gap_case']}.",
        f"- Highest localized release fraction: {summary['localized_highest_release_case']}.",
        f"- Highest loading pressure proxy: {summary['loading_highest_pressure_case']}.",
        f"- Highest loading blockage: {summary['loading_highest_blockage_case']}.",
        f"- Localized release vs front-gap Spearman rank correlation: {summary['localized_release_front_gap_spearman']:.3g}.",
        f"- Loading inventory vs blockage Spearman rank correlation: {summary['loading_inventory_blockage_spearman']:.3g}.",
        f"- Loading inventory vs pressure-proxy Spearman rank correlation: {summary['loading_inventory_pressure_spearman']:.3g}.",
        f"- Drive drag-to-weight vs BTC Spearman rank correlation: {summary['drive_drag_btc_spearman']:.3g}.",
        "",
        "## Boundary",
        "",
        summary["claim_boundary"],
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run() -> dict[str, Any]:
    """Run the observable-response workflow and return summary metadata."""

    tables = load_inputs()
    case_table = build_case_table(tables)
    response_summary, summary = build_response_summary(case_table)
    draw_response_map(case_table, response_summary)
    write_outputs(case_table, response_summary, summary)
    return summary


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-plot", action="store_true", help="Build tables and reports without regenerating the figure.")
    return parser.parse_args()


def main() -> int:
    """Command-line entry point."""

    args = parse_args()
    tables = load_inputs()
    case_table = build_case_table(tables)
    response_summary, summary = build_response_summary(case_table)
    if not args.no_plot:
        draw_response_map(case_table, response_summary)
    write_outputs(case_table, response_summary, summary)
    print(json.dumps(summary, indent=2))
    print(OUT_CASE_TABLE)
    print(OUT_RESPONSE_TABLE)
    print(FIG_DIR / f"{FIG_STEM}.pdf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
