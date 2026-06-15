#!/usr/bin/env python3
"""Build a compact mechanism-decoupling matrix for Paper 2.

The figure is designed to support a specific manuscript claim: source-zone
release, sparse-front advance, local blockage and pore-network degradation are
non-equivalent observables in the present pre-clogging window. It intentionally
uses point and matrix encodings instead of fitted lines because the available
localized-release and loading scans are small bounded evidence sets.
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

DEFAULT_LOCALIZED = TABLE_DIR / "paper2_localized_mechanism_axes.csv"
DEFAULT_LOADING = TABLE_DIR / "paper2_fig4_loading_summary_source.csv"
DEFAULT_PRESSURE = TABLE_DIR / "paper2_pressure_proxy_source.csv"

OUT_TABLE = TABLE_DIR / "paper2_mechanistic_decoupling_matrix.csv"
OUT_JSON = DATA_DIR / "paper2_mechanistic_decoupling_matrix.json"
OUT_MD = NOTE_DIR / "paper2_mechanistic_decoupling_matrix.md"
FIG_STEM = "paper2_figS20_mechanistic_decoupling_matrix"


def configure_matplotlib() -> None:
    """Configure a restrained publication plotting style."""

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


def load_inputs(localized_path: Path, loading_path: Path, pressure_path: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load and validate source tables for the decoupling matrix."""

    for path in (localized_path, loading_path, pressure_path):
        if not path.exists():
            raise FileNotFoundError(path)
    localized = pd.read_csv(localized_path)
    loading = pd.read_csv(loading_path)
    pressure = pd.read_csv(pressure_path)

    required_localized = {
        "job_id",
        "label",
        "particle_count",
        "final_time_s",
        "final_released_fraction",
        "final_downstream_fraction",
        "final_outlet_fraction",
        "final_front_bulk_gap_over_L",
        "final_gap_to_outlet_over_L",
    }
    required_loading = {
        "debris_total_number",
        "final_BTC",
        "subvoxel_max_blockage_ratio",
        "connectivity_loss",
        "Ib_no_pressure",
    }
    required_pressure = {
        "debris_total_number",
        "profile_pressure_increase_ratio",
        "peak_local_pressure_increase_ratio",
    }
    missing = {
        "localized": sorted(required_localized.difference(localized.columns)),
        "loading": sorted(required_loading.difference(loading.columns)),
        "pressure": sorted(required_pressure.difference(pressure.columns)),
    }
    missing = {name: cols for name, cols in missing.items() if cols}
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return localized, loading, pressure


def build_matrix(localized: pd.DataFrame, loading: pd.DataFrame, pressure: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build one long-form table of mechanism observables.

    Missing values are deliberate: source-release observables are not defined
    for the injection loading cases, while local blockage observables are not
    available for the current localized-release monitoring cases.
    """

    rows: list[dict[str, Any]] = []
    for row in localized.itertuples(index=False):
        rows.append(
            {
                "case_group": "localized release",
                "case_label": str(row.label),
                "particle_count": int(row.particle_count),
                "final_time_s": float(row.final_time_s),
                "released_fraction": float(row.final_released_fraction),
                "downstream_fraction": float(row.final_downstream_fraction),
                "outlet_fraction": float(row.final_outlet_fraction),
                "front_bulk_gap_over_L": float(row.final_front_bulk_gap_over_L),
                "gap_to_outlet_over_L": float(row.final_gap_to_outlet_over_L),
                "max_blockage_ratio": np.nan,
                "pressure_increase_ratio": np.nan,
                "connectivity_loss": 0.0,
                "Ib_no_pressure": np.nan,
            }
        )

    pressure_by_n = pressure.set_index("debris_total_number")
    for row in loading.sort_values("debris_total_number").itertuples(index=False):
        pressure_row = pressure_by_n.loc[int(row.debris_total_number)]
        rows.append(
            {
                "case_group": "loading scan",
                "case_label": f"N={int(row.debris_total_number)}",
                "particle_count": int(row.debris_total_number),
                "final_time_s": np.nan,
                "released_fraction": np.nan,
                "downstream_fraction": np.nan,
                "outlet_fraction": float(row.final_BTC),
                "front_bulk_gap_over_L": np.nan,
                "gap_to_outlet_over_L": np.nan,
                "max_blockage_ratio": float(row.subvoxel_max_blockage_ratio),
                "pressure_increase_ratio": float(pressure_row["profile_pressure_increase_ratio"]),
                "connectivity_loss": float(row.connectivity_loss),
                "Ib_no_pressure": float(row.Ib_no_pressure),
            }
        )

    matrix = pd.DataFrame(rows)
    summary = {
        "row_count": int(len(matrix)),
        "localized_case_count": int((matrix["case_group"] == "localized release").sum()),
        "loading_case_count": int((matrix["case_group"] == "loading scan").sum()),
        "localized_release_range": [
            float(matrix["released_fraction"].min(skipna=True)),
            float(matrix["released_fraction"].max(skipna=True)),
        ],
        "front_bulk_gap_range_over_L": [
            float(matrix["front_bulk_gap_over_L"].min(skipna=True)),
            float(matrix["front_bulk_gap_over_L"].max(skipna=True)),
        ],
        "max_blockage_range": [
            float(matrix["max_blockage_ratio"].min(skipna=True)),
            float(matrix["max_blockage_ratio"].max(skipna=True)),
        ],
        "pressure_increase_ratio_range": [
            float(matrix["pressure_increase_ratio"].min(skipna=True)),
            float(matrix["pressure_increase_ratio"].max(skipna=True)),
        ],
        "max_connectivity_loss": float(matrix["connectivity_loss"].max(skipna=True)),
        "all_outlet_crossing_zero_for_localized": bool(
            (matrix.loc[matrix["case_group"] == "localized release", "outlet_fraction"] == 0.0).all()
        ),
        "claim_boundary": (
            "Derived synthesis of existing localized-release and loading evidence. "
            "It supports observable decoupling only; it is not a fitted law, not a completed BTC, "
            "not pressure-calibrated and not a critical-transition criterion."
        ),
    }
    return matrix, summary


def normalize_columns(table: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Normalize selected columns to [0, 1] while preserving NaN."""

    out = table[columns].astype(float).copy()
    for col in columns:
        values = out[col].to_numpy(dtype=float)
        finite = np.isfinite(values)
        if finite.sum() == 0:
            continue
        lo = float(np.nanmin(values))
        hi = float(np.nanmax(values))
        if np.isclose(hi, lo):
            out.loc[finite, col] = 0.0
        else:
            out.loc[finite, col] = (out.loc[finite, col] - lo) / (hi - lo)
    return out


def draw_localized_plane(ax: plt.Axes, matrix: pd.DataFrame) -> None:
    """Draw source release against final front-bulk separation for localized cases."""

    colors = {
        "906 upstream": "#4d4d4d",
        "907 downstream": "#2166ac",
        "908 high inventory": "#b2182b",
    }
    subset = matrix[matrix["case_group"] == "localized release"].copy()
    for row in subset.itertuples(index=False):
        ax.scatter(
            row.released_fraction,
            row.front_bulk_gap_over_L,
            s=45 + row.particle_count / 500,
            color=colors.get(row.case_label, "#777777"),
            edgecolor="#222222",
            linewidth=0.35,
            label=row.case_label,
            zorder=3,
        )
    ax.set_xlabel("released fraction")
    ax.set_ylabel("front-bulk gap, $x_{max}-x_{99}$")
    ax.set_xlim(0.0, 0.12)
    ax.set_ylim(0.0, 0.70)
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.legend(loc="lower right", handletextpad=0.4)
    panel_label(ax, "a")


def draw_observable_matrix(ax: plt.Axes, matrix: pd.DataFrame) -> None:
    """Draw a normalized observable matrix with unavailable cells masked."""

    columns = [
        "released_fraction",
        "front_bulk_gap_over_L",
        "outlet_fraction",
        "max_blockage_ratio",
        "pressure_increase_ratio",
        "connectivity_loss",
    ]
    labels = [
        "source\nrelease",
        "sparse\nfront",
        "outlet\ncounting",
        "local\nblockage",
        "pressure\nproxy",
        "connectivity\nloss",
    ]
    plot_data = normalize_columns(matrix, columns)
    arr = plot_data.to_numpy(dtype=float)
    masked = np.ma.masked_invalid(arr)
    cmap = mpl.colormaps["viridis"].copy()
    cmap.set_bad("#eeeeee")
    image = ax.imshow(masked, aspect="auto", cmap=cmap, vmin=0.0, vmax=1.0)
    ax.set_xticks(np.arange(len(columns)), labels)
    ax.set_yticks(np.arange(len(matrix)), matrix["case_label"].astype(str))
    ax.tick_params(axis="x", rotation=0)
    ax.set_xlabel("observable")
    ax.set_ylabel("case")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks(np.arange(-0.5, len(columns), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(matrix), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.8)
    ax.tick_params(which="minor", bottom=False, left=False)
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            if not np.isfinite(arr[i, j]):
                ax.text(j, i, "NA", ha="center", va="center", color="#777777", fontsize=6.5)
            elif columns[j] == "connectivity_loss" and np.isclose(matrix.iloc[i][columns[j]], 0.0):
                ax.text(j, i, "0", ha="center", va="center", color="#222222", fontsize=6.5)
    cbar = ax.figure.colorbar(image, ax=ax, fraction=0.035, pad=0.02)
    cbar.set_label("column-normalized magnitude")
    cbar.ax.tick_params(labelsize=6.8)
    panel_label(ax, "b")


def draw_metric_strip(ax: plt.Axes, matrix: pd.DataFrame) -> None:
    """Draw absolute local blockage and pressure-proxy magnitudes for loading cases."""

    subset = matrix[matrix["case_group"] == "loading scan"].copy()
    x = np.arange(len(subset))
    ax.scatter(x - 0.08, subset["max_blockage_ratio"], marker="o", s=32, color="#0072b2", label="max blockage")
    ax.scatter(x + 0.08, subset["pressure_increase_ratio"], marker="s", s=32, color="#d55e00", label="pressure proxy")
    ax.set_yscale("log")
    ax.set_xticks(x, subset["case_label"])
    ax.set_ylabel("absolute magnitude")
    ax.grid(True, axis="y", which="both", linewidth=0.35, alpha=0.35)
    ax.legend(loc="upper left")
    panel_label(ax, "c")


def save_figure(fig: plt.Figure) -> None:
    """Save figure exports in PNG, PDF and SVG formats."""

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for suffix, kwargs in {".png": {"dpi": 600}, ".pdf": {}, ".svg": {}}.items():
        fig.savefig(FIG_DIR / f"{FIG_STEM}{suffix}", bbox_inches="tight", **kwargs)


def save_gray_preview() -> None:
    """Save a grayscale PNG preview for color-independence checks."""

    image = plt.imread(FIG_DIR / f"{FIG_STEM}.png")
    rgb = image[..., :3]
    gray = np.dot(rgb, np.array([0.299, 0.587, 0.114]))
    plt.imsave(FIG_DIR / f"{FIG_STEM}_gray_preview.png", np.dstack([gray, gray, gray]))


def make_figure(matrix: pd.DataFrame) -> None:
    """Create the mechanism-decoupling multi-panel figure."""

    configure_matplotlib()
    fig = plt.figure(figsize=(7.2, 4.9), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, width_ratios=[1.0, 1.35], height_ratios=[1.0, 0.78])
    draw_localized_plane(fig.add_subplot(grid[0, 0]), matrix)
    draw_observable_matrix(fig.add_subplot(grid[:, 1]), matrix)
    draw_metric_strip(fig.add_subplot(grid[1, 0]), matrix)
    save_figure(fig)
    plt.close(fig)
    save_gray_preview()


def write_outputs(matrix: pd.DataFrame, summary: dict[str, Any]) -> None:
    """Write table, JSON and Markdown outputs."""

    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    NOTE_DIR.mkdir(parents=True, exist_ok=True)
    matrix.to_csv(OUT_TABLE, index=False)
    OUT_JSON.write_text(
        json.dumps({"summary": summary, "rows": matrix.to_dict(orient="records")}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Mechanistic Decoupling Matrix",
        "",
        f"- Rows: `{summary['row_count']}`",
        f"- Localized cases: `{summary['localized_case_count']}`",
        f"- Loading cases: `{summary['loading_case_count']}`",
        f"- Localized released-fraction range: `{summary['localized_release_range'][0]:.6g}` to `{summary['localized_release_range'][1]:.6g}`",
        f"- Front-bulk gap range: `{summary['front_bulk_gap_range_over_L'][0]:.6g}` to `{summary['front_bulk_gap_range_over_L'][1]:.6g}`",
        f"- Max blockage range: `{summary['max_blockage_range'][0]:.6g}` to `{summary['max_blockage_range'][1]:.6g}`",
        f"- Maximum connectivity loss: `{summary['max_connectivity_loss']:.6g}`",
        "",
        "## Boundary",
        "",
        summary["claim_boundary"],
        "",
        "## Outputs",
        "",
        f"- Table: `{OUT_TABLE.relative_to(PROJECT_ROOT)}`",
        f"- Figure: `papers/paper2_voxel_topology_clogging/figures/{FIG_STEM}.pdf`",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(
    localized_path: Path = DEFAULT_LOCALIZED,
    loading_path: Path = DEFAULT_LOADING,
    pressure_path: Path = DEFAULT_PRESSURE,
) -> dict[str, Any]:
    """Run the complete decoupling-matrix workflow."""

    localized, loading, pressure = load_inputs(localized_path, loading_path, pressure_path)
    matrix, summary = build_matrix(localized, loading, pressure)
    write_outputs(matrix, summary)
    make_figure(matrix)
    return summary


def main() -> int:
    """Command-line entry point."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--localized", type=Path, default=DEFAULT_LOCALIZED)
    parser.add_argument("--loading", type=Path, default=DEFAULT_LOADING)
    parser.add_argument("--pressure", type=Path, default=DEFAULT_PRESSURE)
    args = parser.parse_args()
    print(json.dumps(run(args.localized, args.loading, args.pressure), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
