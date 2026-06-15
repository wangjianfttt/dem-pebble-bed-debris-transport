#!/usr/bin/env python3
"""Create a bounded parameter-evidence coverage map for Paper 2.

The figure is intentionally a discrete evidence map rather than an interpolated
regime diagram. It shows where the current DEM-derived mechanism evidence
exists and where the paper must avoid claiming full parameter-space coverage.
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
FIG_DIR = PAPER_DIR / "figures"
DATA_DIR = PAPER_DIR / "data"
NOTE_DIR = PAPER_DIR / "notes"

DIMENSIONLESS = TABLE_DIR / "paper2_dimensionless_mechanism_map_source.csv"
REPEAT_SEED = TABLE_DIR / "paper2_repeat_seed_manuscript_summary_source.csv"
OUT_TABLE = TABLE_DIR / "paper2_parameter_evidence_coverage_source.csv"
OUT_JSON = DATA_DIR / "paper2_parameter_evidence_coverage_map.json"
OUT_MD = NOTE_DIR / "paper2_parameter_evidence_coverage_map.md"
FIG_STEM = "paper2_figS25_parameter_evidence_coverage"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-table", type=Path, default=OUT_TABLE, help="Output source-data CSV.")
    parser.add_argument("--out-json", type=Path, default=OUT_JSON, help="Output summary JSON.")
    parser.add_argument("--out-md", type=Path, default=OUT_MD, help="Output Markdown note.")
    parser.add_argument("--fig-stem", default=FIG_STEM, help="Output figure stem under the figure directory.")
    return parser.parse_args()


def configure_matplotlib() -> None:
    """Configure an Elsevier-friendly, colorblind-safe figure style."""
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
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "legend.frameon": False,
        }
    )


def read_csv(path: Path) -> pd.DataFrame:
    """Read a non-empty CSV table."""
    if not path.exists():
        raise FileNotFoundError(path)
    table = pd.read_csv(path)
    if table.empty:
        raise ValueError(f"Required table is empty: {path}")
    return table


def evidence_level(row: pd.Series) -> str:
    """Return a compact evidence-level label for one mechanism-map row."""
    family = str(row["evidence_family"])
    if family == "drive_state":
        return "drive final-state DEM"
    if family == "loading_state":
        return "single-seed loading DEM"
    if family == "localized_source_state":
        return "target-time localized DEM"
    return "derived evidence"


def coverage_strength(row: pd.Series) -> int:
    """Return an ordinal evidence-strength score for plotting only."""
    family = str(row["evidence_family"])
    if family == "localized_source_state":
        return 3
    if family == "drive_state":
        return 2
    if family == "loading_state":
        return 2
    return 1


def supported_observables_for_family(family: str) -> list[str]:
    """Return observables that are directly supported for one evidence family."""
    if family == "drive_state":
        return ["BTC", "blockage", "connectivity"]
    if family == "loading_state":
        return ["BTC", "blockage", "connectivity"]
    if family == "localized_source_state":
        return ["BTC", "sparse-front gap"]
    return []


def build_coverage_table() -> pd.DataFrame:
    """Build the parameter-evidence coverage table from current source data."""
    dim = read_csv(DIMENSIONLESS)
    table = dim.copy()
    required = {
        "evidence_family",
        "case_label",
        "df_over_dp",
        "gas_velocity_m_s",
        "drag_to_weight_ratio",
        "debris_total_number",
        "final_BTC",
        "max_blockage_ratio",
        "connectivity_loss",
        "front_bulk_gap_over_L",
        "mechanism_regime",
        "claim_boundary",
    }
    missing = sorted(required.difference(table.columns))
    if missing:
        raise ValueError(f"Dimensionless mechanism map missing columns: {missing}")

    table["evidence_level"] = table.apply(evidence_level, axis=1)
    table["coverage_strength"] = table.apply(coverage_strength, axis=1)
    table["has_drive_coordinate"] = table["drag_to_weight_ratio"].notna()
    table["has_loading_coordinate"] = table["dimensionless_loading"].notna()
    table["has_localized_source_coordinate"] = table["evidence_family"].eq("localized_source_state")
    table["parameter_axis"] = table["evidence_family"].map(
        {
            "drive_state": "df/dp and gas velocity",
            "loading_state": "debris inventory",
            "localized_source_state": "source position and inventory",
        }
    )
    table["supported_observables"] = table["evidence_family"].map(
        lambda family: "; ".join(supported_observables_for_family(str(family)))
    )
    table["coverage_boundary"] = table["claim_boundary"].astype(str)
    return table


def coverage_summary(table: pd.DataFrame) -> dict[str, Any]:
    """Summarize what parameter coverage is and is not supported."""
    family_counts = table["evidence_family"].value_counts().sort_index().to_dict()
    repeat_count = None
    if REPEAT_SEED.exists():
        repeat = read_csv(REPEAT_SEED)
        repeat_count = int(repeat["formal_processed_count"].iloc[0])
    return {
        "row_count": int(len(table)),
        "family_counts": {str(k): int(v) for k, v in family_counts.items()},
        "df_over_dp_range_with_gas_velocity": [
            float(table.loc[table["gas_velocity_m_s"].notna(), "df_over_dp"].min()),
            float(table.loc[table["gas_velocity_m_s"].notna(), "df_over_dp"].max()),
        ],
        "gas_velocity_range_m_s": [
            float(table["gas_velocity_m_s"].dropna().min()),
            float(table["gas_velocity_m_s"].dropna().max()),
        ],
        "debris_total_number_range": [
            int(table["debris_total_number"].min()),
            int(table["debris_total_number"].max()),
        ],
        "formal_repeat_seed_count": repeat_count,
        "mechanism_regimes": sorted(table["mechanism_regime"].dropna().astype(str).unique().tolist()),
        "boundary": "Discrete evidence coverage only; not a full factorial sweep, interpolated phase map or universal critical-clogging diagram.",
    }


def panel_label(ax: plt.Axes, label: str) -> None:
    """Add a small bold panel label."""
    ax.text(-0.12, 1.05, label, transform=ax.transAxes, fontsize=9, fontweight="bold", va="top")


def save_figure(fig: plt.Figure, stem: str) -> None:
    """Save PNG, PDF, SVG and grayscale preview exports."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for suffix, kwargs in {".png": {"dpi": 600}, ".pdf": {}, ".svg": {}}.items():
        fig.savefig(FIG_DIR / f"{stem}{suffix}", bbox_inches="tight", **kwargs)
    preview = FIG_DIR / f"{stem}_gray_preview.png"
    fig.savefig(preview, dpi=300, bbox_inches="tight", pil_kwargs={"compress_level": 6})
    try:
        from PIL import Image, ImageOps

        with Image.open(preview) as image:
            ImageOps.grayscale(image.convert("RGB")).save(preview)
    except ImportError:
        pass


def plot_coverage(table: pd.DataFrame, stem: str) -> None:
    """Create the parameter-evidence coverage figure."""
    configure_matplotlib()
    colors = {
        "drive_state": "#0072B2",
        "loading_state": "#D55E00",
        "localized_source_state": "#009E73",
    }
    markers = {
        "drive_state": "o",
        "loading_state": "s",
        "localized_source_state": "^",
    }
    labels = {
        "drive_state": "drive states",
        "loading_state": "loading states",
        "localized_source_state": "localized source",
    }
    fig, axes = plt.subplots(2, 2, figsize=(7.1, 5.35), constrained_layout=True)

    ax = axes[0, 0]
    with_gas = table[table["gas_velocity_m_s"].notna()].copy()
    for family, sub in with_gas.groupby("evidence_family"):
        ax.scatter(
            sub["df_over_dp"],
            sub["gas_velocity_m_s"],
            s=42 + 0.0035 * sub["debris_total_number"],
            c=colors.get(family, "#666666"),
            marker=markers.get(family, "o"),
            edgecolor="#222222",
            linewidth=0.45,
            alpha=0.92,
            label=labels.get(family, family),
        )
    ax.set_xlabel(r"$d_f/d_p$")
    ax.set_ylabel(r"$u_g$ (m s$^{-1}$)")
    ax.set_title("Resolved gas-driven input points")
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.legend(loc="upper right", handletextpad=0.4)
    panel_label(ax, "a")

    ax = axes[0, 1]
    x = table["dimensionless_loading"].to_numpy(float)
    y = np.maximum(table["final_BTC"].to_numpy(float), 1e-5)
    for family, sub in table.groupby("evidence_family"):
        ax.scatter(
            sub["dimensionless_loading"],
            np.maximum(sub["final_BTC"], 1e-5),
            s=50 + 34 * sub["coverage_strength"],
            c=colors.get(family, "#666666"),
            marker=markers.get(family, "o"),
            edgecolor="#222222",
            linewidth=0.45,
            alpha=0.92,
            label=labels.get(family, family),
        )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel(r"dimensionless debris loading")
    ax.set_ylabel("final BTC (floor at 1e-5)")
    ax.set_title("Observable coverage without interpolation")
    ax.grid(True, which="both", linewidth=0.35, alpha=0.35)
    panel_label(ax, "b")

    ax = axes[1, 0]
    families = ["drive_state", "loading_state", "localized_source_state"]
    observables = ["final_BTC", "max_blockage_ratio", "connectivity_loss", "front_bulk_gap_over_L"]
    matrix = np.zeros((len(families), len(observables)), dtype=float)
    for i, family in enumerate(families):
        supported = set(supported_observables_for_family(family))
        for j, obs in enumerate(observables):
            label = {
                "final_BTC": "BTC",
                "max_blockage_ratio": "blockage",
                "connectivity_loss": "connectivity",
                "front_bulk_gap_over_L": "sparse-front gap",
            }[obs]
            if label in supported:
                matrix[i, j] = 0.75
    cmap = mpl.colors.ListedColormap(["#f2f2f2", "#9ecae1", "#3182bd"])
    im = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(np.arange(len(observables)), ["BTC", r"$B_{max}$", r"$C_{loss}$", "front gap"], rotation=30, ha="right")
    ax.set_yticks(np.arange(len(families)), ["drive", "loading", "localized"])
    ax.set_title("Which observables are covered")
    for i in range(len(families)):
        for j in range(len(observables)):
            ax.text(j, i, "yes" if matrix[i, j] > 0 else "-", ha="center", va="center", fontsize=7, color="#111111")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)
    panel_label(ax, "c")

    ax = axes[1, 1]
    boundary_rows = [
        ("drive", "not full size-velocity sweep"),
        ("loading", "single-seed loading states"),
        ("localized", "not source-position law"),
        ("pressure", "screening, not calibration"),
    ]
    y_pos = np.arange(len(boundary_rows))[::-1]
    ax.barh(y_pos, [1, 1, 1, 1], color=["#0072B2", "#D55E00", "#009E73", "#999999"], alpha=0.88)
    ax.set_yticks(y_pos, [row[0] for row in boundary_rows])
    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.set_title("Boundaries kept with evidence")
    for yv, (_, text) in zip(y_pos, boundary_rows):
        ax.text(0.03, yv, text, va="center", ha="left", fontsize=7, color="white")
    for spine in ax.spines.values():
        spine.set_visible(False)
    panel_label(ax, "d")

    save_figure(fig, stem)
    plt.close(fig)


def write_markdown(summary: dict[str, Any], out_md: Path) -> None:
    """Write a short Markdown note for the coverage map."""
    lines = [
        "# Paper 2 Parameter-Evidence Coverage Map",
        "",
        "This note accompanies Fig. S25 and records what the current parameter evidence covers. The map deliberately uses discrete points and coverage indicators rather than a fitted or interpolated phase map.",
        "",
        f"- Rows: {summary['row_count']}",
        f"- Evidence families: `{json.dumps(summary['family_counts'], sort_keys=True)}`",
        f"- Gas-driven df/dp range: `{summary['df_over_dp_range_with_gas_velocity']}`",
        f"- Gas-velocity range (m/s): `{summary['gas_velocity_range_m_s']}`",
        f"- Debris-count range: `{summary['debris_total_number_range']}`",
        f"- Formal repeat-seed count: `{summary['formal_repeat_seed_count']}`",
        "",
        "## Boundary",
        "",
        summary["boundary"],
        "",
        "Use this figure to show coverage and limitation, not to claim a continuous critical clogging transition.",
    ]
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(out_table: Path = OUT_TABLE, out_json: Path = OUT_JSON, out_md: Path = OUT_MD, fig_stem: str = FIG_STEM) -> dict[str, Any]:
    """Write source table, figure and summary outputs."""
    table = build_coverage_table()
    summary = coverage_summary(table)
    out_table.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(out_table, index=False)
    plot_coverage(table, fig_stem)
    write_markdown(summary, out_md)
    summary.update(
        {
            "out_table": str(out_table),
            "out_md": str(out_md),
            "figure_stem": fig_stem,
        }
    )
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> int:
    """Run the parameter-evidence coverage workflow."""
    args = parse_args()
    summary = write_outputs(args.out_table, args.out_json, args.out_md, args.fig_stem)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
