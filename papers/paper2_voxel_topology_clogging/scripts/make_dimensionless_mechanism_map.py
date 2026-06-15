#!/usr/bin/env python3
"""Build a dimensionless mechanism map from existing Paper 2 evidence tables."""

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
NOTES_DIR = PAPER_DIR / "notes"

REPRESENTATIVE = TABLE_DIR / "paper2_fig3_representative_state_source.csv"
LOADING = TABLE_DIR / "paper2_fig4_loading_summary_source.csv"
PRESSURE_PROXY = TABLE_DIR / "paper2_pressure_proxy_source.csv"
VOXEL_PRESSURE = TABLE_DIR / "paper2_voxel_pressure_pilot_source.csv"
LOCALIZED_PRODUCTION = TABLE_DIR / "explicit_localized_production_summary.csv"

OUT_TABLE = TABLE_DIR / "paper2_dimensionless_mechanism_map_source.csv"
OUT_SUPP_TABLE = PAPER_DIR / "supplementary" / "table_s12_dimensionless_mechanism_map.csv"
OUT_JSON = DATA_DIR / "paper2_dimensionless_mechanism_map.json"
OUT_MD = NOTES_DIR / "paper2_dimensionless_mechanism_map.md"
FIG_STEM = "paper2_figS16_dimensionless_mechanism_map"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-table", type=Path, default=OUT_TABLE, help="Output source-data CSV.")
    parser.add_argument("--out-json", type=Path, default=OUT_JSON, help="Output summary JSON.")
    parser.add_argument("--out-md", type=Path, default=OUT_MD, help="Output mechanism-note Markdown.")
    parser.add_argument("--fig-stem", default=FIG_STEM, help="Output figure stem under the Paper 2 figure directory.")
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


def read_required_csv(path: Path) -> pd.DataFrame:
    """Read a required CSV table and reject empty tables."""
    if not path.exists():
        raise FileNotFoundError(path)
    frame = pd.read_csv(path)
    if frame.empty:
        raise ValueError(f"Required table is empty: {path}")
    return frame


def classify_mechanism(row: pd.Series) -> str:
    """Classify one evidence row into a bounded mechanism regime."""
    btc = float(row.get("final_BTC", 0.0))
    blockage = float(row.get("max_blockage_ratio", row.get("subvoxel_max_blockage_ratio", 0.0)))
    connectivity_loss = float(row.get("connectivity_loss", 0.0))
    source_fraction = float(row.get("source_fraction", np.nan))
    x_max = float(row.get("x_max_over_L", np.nan))
    if np.isfinite(source_fraction) and np.isfinite(x_max) and source_fraction > 0.5 and x_max > 0.95:
        return "source-retained sparse front"
    if connectivity_loss > 0.01:
        return "connectivity loss"
    if blockage >= 1e-3:
        return "local blockage"
    if btc >= 0.01:
        return "breakthrough without topology loss"
    return "retention/internal filtering"


def build_mechanism_table() -> pd.DataFrame:
    """Build a unified mechanism table from representative and loading evidence."""
    representative = read_required_csv(REPRESENTATIVE)
    loading = read_required_csv(LOADING)
    pressure = read_required_csv(PRESSURE_PROXY) if PRESSURE_PROXY.exists() else pd.DataFrame()
    voxel_pressure = read_required_csv(VOXEL_PRESSURE) if VOXEL_PRESSURE.exists() else pd.DataFrame()
    localized = read_required_csv(LOCALIZED_PRODUCTION) if LOCALIZED_PRODUCTION.exists() else pd.DataFrame()

    rep_rows = []
    for _, row in representative.iterrows():
        rep_rows.append(
            {
                "evidence_family": "drive_state",
                "case_label": row["role"],
                "case_name": row["case_name"],
                "df_over_dp": float(row["df_over_dp"]),
                "gas_velocity_m_s": float(row["gas_velocity"]),
                "drag_to_weight_ratio": float(row["drag_to_weight_ratio"]),
                "debris_total_number": int(row["debris_particle_count"]),
                "final_BTC": float(row["final_BTC"]),
                "retention": 1.0 - float(row["final_BTC"]),
                "source_fraction": np.nan,
                "downstream_fraction": np.nan,
                "x_mean_over_L": float(row["x_mean_over_L"]),
                "x_q99_over_L": np.nan,
                "x_max_over_L": np.nan,
                "front_bulk_gap_over_L": np.nan,
                "blockage_centroid_over_L": float(row["subvoxel_blockage_centroid_over_L"]),
                "max_blockage_ratio": float(row["subvoxel_max_blockage_ratio"]),
                "connectivity_loss": 0.0,
                "outlet_connected_void_fraction_x": float(row["voxel_outlet_connected_fraction_x"]),
                "Ib_no_pressure": 0.5 * float(row["subvoxel_max_blockage_ratio"]),
                "profile_pressure_increase_ratio": np.nan,
                "voxel_conductance_loss": np.nan,
                "final_time_s": np.nan,
                "claim_boundary": "representative DEM-derived final-state evidence; not a full parameter sweep",
            }
        )

    load_rows = []
    pressure_by_n = pressure.set_index("debris_total_number") if not pressure.empty else pd.DataFrame()
    voxel_by_n = voxel_pressure[voxel_pressure.get("debris_total_number", -1) > 0].set_index("debris_total_number") if not voxel_pressure.empty else pd.DataFrame()
    for _, row in loading.iterrows():
        n = int(row["debris_total_number"])
        p_ratio = float(pressure_by_n.loc[n, "profile_pressure_increase_ratio"]) if n in pressure_by_n.index else np.nan
        c_loss = float(row.get("connectivity_loss", 0.0))
        voxel_loss = float(voxel_by_n.loc[n, "conductance_loss"]) if n in voxel_by_n.index else np.nan
        load_rows.append(
            {
                "evidence_family": "loading_state",
                "case_label": f"N={n}",
                "case_name": row["case_name"],
                "df_over_dp": float(row["df_over_dp"]),
                "gas_velocity_m_s": float(row["gas_velocity"]),
                "drag_to_weight_ratio": np.nan,
                "debris_total_number": n,
                "final_BTC": float(row["final_BTC"]),
                "retention": float(row["final_retention"]),
                "source_fraction": np.nan,
                "downstream_fraction": np.nan,
                "x_mean_over_L": float(row["x_mean_m"]) / 0.045,
                "x_q99_over_L": np.nan,
                "x_max_over_L": np.nan,
                "front_bulk_gap_over_L": np.nan,
                "blockage_centroid_over_L": float(row["subvoxel_blockage_centroid_over_L"]),
                "max_blockage_ratio": float(row["subvoxel_max_blockage_ratio"]),
                "connectivity_loss": c_loss,
                "outlet_connected_void_fraction_x": float(row["voxel_outlet_connected_fraction_x"]),
                "Ib_no_pressure": float(row["Ib_no_pressure"]),
                "profile_pressure_increase_ratio": p_ratio,
                "voxel_conductance_loss": voxel_loss,
                "final_time_s": np.nan,
                "claim_boundary": "single-seed loading evidence with pressure proxies only; not a calibrated transition",
            }
        )

    localized_rows = []
    for _, row in localized.iterrows():
        source_fraction = float(row["final_source_fraction"])
        downstream_fraction = float(row["final_downstream_fraction"])
        x_q99 = float(row["final_x_q99_over_L"])
        x_max = float(row["final_x_max_over_L"])
        n = int(row["final_debris_count"])
        localized_rows.append(
            {
                "evidence_family": "localized_source_state",
                "case_label": str(row["job_id"]).split("_")[0],
                "case_name": row["case_name"],
                "df_over_dp": 0.1,
                "gas_velocity_m_s": np.nan,
                "drag_to_weight_ratio": np.nan,
                "debris_total_number": n,
                "final_BTC": float(row["final_outlet_fraction"]),
                "retention": 1.0 - float(row["final_outlet_fraction"]),
                "source_fraction": source_fraction,
                "downstream_fraction": downstream_fraction,
                "x_mean_over_L": float(row["final_x_mean_over_L"]),
                "x_q99_over_L": x_q99,
                "x_max_over_L": x_max,
                "front_bulk_gap_over_L": x_max - x_q99,
                "blockage_centroid_over_L": np.nan,
                "max_blockage_ratio": 0.0,
                "connectivity_loss": 0.0,
                "outlet_connected_void_fraction_x": np.nan,
                "Ib_no_pressure": 0.0,
                "profile_pressure_increase_ratio": np.nan,
                "voxel_conductance_loss": np.nan,
                "final_time_s": float(row["final_time_s"]),
                "claim_boundary": "localized-source target-time evidence; supports sparse-front/source-retention mechanism, not a source-position law or critical transition",
            }
        )

    table = pd.DataFrame(rep_rows + load_rows + localized_rows)
    table["mechanism_regime"] = table.apply(classify_mechanism, axis=1)
    table["dimensionless_loading"] = table["debris_total_number"] * table["df_over_dp"] ** 3
    table["breakthrough_to_blockage_ratio"] = table["final_BTC"] / np.maximum(table["max_blockage_ratio"], 1e-12)
    table["topology_loss_ratio"] = table["connectivity_loss"] / np.maximum(table["max_blockage_ratio"], 1e-12)
    table["front_bulk_gap_over_L"] = table["front_bulk_gap_over_L"].fillna(0.0)
    return table


def correlation_summary(table: pd.DataFrame) -> dict[str, Any]:
    """Compute correlations used as mechanism-collapse diagnostics."""
    drive = table[table["evidence_family"] == "drive_state"].copy()
    loading = table[table["evidence_family"] == "loading_state"].copy()
    localized = table[table["evidence_family"] == "localized_source_state"].copy()
    summary: dict[str, Any] = {
        "row_count": int(len(table)),
        "drive_state_count": int(len(drive)),
        "loading_state_count": int(len(loading)),
        "localized_source_state_count": int(len(localized)),
        "mechanism_regimes": sorted(table["mechanism_regime"].unique().tolist()),
        "evidence_boundary": "Derived synthesis from existing Paper 2 tables; no new DEM or CFD result.",
    }
    def safe_corr(left: pd.Series, right: pd.Series) -> float | None:
        """Return Pearson correlation or None when either series is constant."""
        x = left.to_numpy(dtype=float)
        y = right.to_numpy(dtype=float)
        mask = np.isfinite(x) & np.isfinite(y)
        x = x[mask]
        y = y[mask]
        if len(x) < 2 or np.isclose(np.std(x), 0.0) or np.isclose(np.std(y), 0.0):
            return None
        return float(np.corrcoef(x, y)[0, 1])

    if len(drive) >= 3:
        summary["drive_correlations"] = {
            "FdW_vs_final_BTC": safe_corr(drive["drag_to_weight_ratio"], drive["final_BTC"]),
            "FdW_vs_x_mean_over_L": safe_corr(drive["drag_to_weight_ratio"], drive["x_mean_over_L"]),
            "FdW_vs_blockage_centroid_over_L": safe_corr(drive["drag_to_weight_ratio"], drive["blockage_centroid_over_L"]),
        }
    if len(loading) >= 3:
        summary["loading_correlations"] = {
            "dimensionless_loading_vs_max_blockage": safe_corr(loading["dimensionless_loading"], loading["max_blockage_ratio"]),
            "debris_count_vs_Ib_no_pressure": safe_corr(loading["debris_total_number"], loading["Ib_no_pressure"]),
            "debris_count_vs_connectivity_loss": safe_corr(loading["debris_total_number"], loading["connectivity_loss"]),
        }
    if len(localized) >= 3:
        summary["localized_source_correlations"] = {
            "source_fraction_vs_downstream_fraction": safe_corr(localized["source_fraction"], localized["downstream_fraction"]),
            "source_fraction_vs_front_bulk_gap": safe_corr(localized["source_fraction"], localized["front_bulk_gap_over_L"]),
            "downstream_fraction_vs_x_mean": safe_corr(localized["downstream_fraction"], localized["x_mean_over_L"]),
        }
    summary["max_values"] = {
        "final_BTC": float(table["final_BTC"].max()),
        "max_blockage_ratio": float(table["max_blockage_ratio"].max()),
        "connectivity_loss": float(table["connectivity_loss"].max()),
        "Ib_no_pressure": float(table["Ib_no_pressure"].max()),
        "front_bulk_gap_over_L": float(table["front_bulk_gap_over_L"].max()),
        "profile_pressure_increase_ratio": float(np.nanmax(table["profile_pressure_increase_ratio"].to_numpy(dtype=float))),
        "voxel_conductance_loss": float(np.nanmax(table["voxel_conductance_loss"].to_numpy(dtype=float))),
    }
    return summary


def panel_label(ax: plt.Axes, label: str, x: float = 0.02, y: float = 0.98) -> None:
    """Place a panel label inside an axes."""
    ax.text(x, y, label, transform=ax.transAxes, va="top", ha="left", fontsize=9, fontweight="bold")


def draw_drive_collapse(ax: plt.Axes, table: pd.DataFrame) -> None:
    """Draw drag-to-weight collapse for representative transport states."""
    drive = table[table["evidence_family"] == "drive_state"].sort_values("drag_to_weight_ratio")
    colors = {"retention/internal filtering": "#6f91b4", "breakthrough without topology loss": "#b34d4f"}
    markers = {"retention/internal filtering": "o", "breakthrough without topology loss": "s"}
    for _, row in drive.iterrows():
        ax.scatter(
            row["drag_to_weight_ratio"],
            row["final_BTC"],
            s=65 + 350 * row["x_mean_over_L"],
            marker=markers.get(row["mechanism_regime"], "^"),
            color=colors.get(row["mechanism_regime"], "#4d4d4d"),
            edgecolor="#222222",
            linewidth=0.45,
            zorder=3,
        )
        ax.annotate(
            f"{row['df_over_dp']:.4f}, {row['gas_velocity_m_s']:.0f} m/s",
            xy=(row["drag_to_weight_ratio"], row["final_BTC"]),
            xytext=(5, 4),
            textcoords="offset points",
            fontsize=6.3,
        )
    ax.axhspan(0.0, 0.01, facecolor="#f0f6fb", edgecolor="none", zorder=0)
    ax.text(0.04, 0.09, "retention dominated", transform=ax.transAxes, fontsize=6.6, color="#4f6f8c")
    ax.set_xlabel(r"Stokes drag-to-weight ratio $F_d/W$")
    ax.set_ylabel("final BTC")
    ax.set_title("Drive primarily affects penetration")
    ax.set_xlim(0, max(125, float(drive["drag_to_weight_ratio"].max()) * 1.08))
    ax.set_ylim(-0.005, max(0.095, float(drive["final_BTC"].max()) * 1.18))
    ax.grid(True, linewidth=0.35, alpha=0.35)
    panel_label(ax, "a")


def draw_transport_topology_plane(ax: plt.Axes, table: pd.DataFrame) -> None:
    """Draw the separation between transport signal and topology loss."""
    colors = {"drive_state": "#6f91b4", "loading_state": "#b34d4f", "localized_source_state": "#009E73"}
    markers = {"drive_state": "o", "loading_state": "s", "localized_source_state": "^"}
    y_offsets = {"drive_state": 1.0e-7, "loading_state": 1.7e-7, "localized_source_state": 2.5e-7}
    for family, group in table.groupby("evidence_family"):
        ax.scatter(
            group["final_BTC"],
            group["connectivity_loss"] + y_offsets.get(family, 1.0e-7),
            s=58 + 250 * np.clip(group["max_blockage_ratio"] / max(table["max_blockage_ratio"].max(), 1e-12), 0, 1),
            marker=markers.get(family, "o"),
            color=colors.get(family, "#4d4d4d"),
            edgecolor="#222222",
            linewidth=0.45,
            alpha=0.92,
        )
    ax.axhline(0.01, color="#4d4d4d", linestyle=":", linewidth=0.9)
    ax.text(0.98, 0.78, "topology-loss\nreference", transform=ax.transAxes, ha="right", fontsize=6.5, color="#555555")
    ax.set_yscale("log")
    ax.set_xlabel("final BTC")
    ax.set_ylabel(r"$C_{loss}$ + $10^{-7}$")
    ax.set_title("Breakthrough decouples from connectivity loss")
    ax.set_xlim(-0.004, max(0.09, float(table["final_BTC"].max()) * 1.12))
    ax.set_ylim(5e-8, 2e-2)
    ax.grid(True, which="both", linewidth=0.35, alpha=0.35)
    ax.scatter([], [], marker="o", color=colors["drive_state"], edgecolor="#222222", linewidth=0.45, label="drive")
    ax.scatter([], [], marker="s", color=colors["loading_state"], edgecolor="#222222", linewidth=0.45, label="loading")
    ax.scatter([], [], marker="^", color=colors["localized_source_state"], edgecolor="#222222", linewidth=0.45, label="localized")
    ax.legend(loc="upper right", bbox_to_anchor=(1.0, 0.63), handletextpad=0.35, borderaxespad=0.0)
    panel_label(ax, "b", x=0.03, y=0.94)


def draw_loading_blockage(ax: plt.Axes, table: pd.DataFrame) -> None:
    """Draw loading against blockage without implying a fitted law."""
    loading = table[table["evidence_family"] == "loading_state"].sort_values("dimensionless_loading")
    ax.scatter(
        loading["dimensionless_loading"],
        loading["max_blockage_ratio"] * 1e6,
        s=70,
        marker="D",
        color="#4d4d4d",
        edgecolor="#222222",
        linewidth=0.45,
    )
    for _, row in loading.iterrows():
        ax.annotate(f"N={int(row['debris_total_number'])}", (row["dimensionless_loading"], row["max_blockage_ratio"] * 1e6), xytext=(5, 4), textcoords="offset points", fontsize=6.5)
    ax.set_xlabel(r"dimensionless debris inventory $N_f(d_f/d_p)^3$")
    ax.set_ylabel(r"$B_{\max}$ ($\times 10^{-6}$)")
    ax.set_title("Inventory raises local blockage")
    ax.set_xlim(0, float(loading["dimensionless_loading"].max()) * 1.25)
    ax.set_ylim(0, max(42, float(loading["max_blockage_ratio"].max()) * 1e6 * 1.22))
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.text(0.05, 0.88, "single-seed states", transform=ax.transAxes, fontsize=6.6, color="#555555")
    panel_label(ax, "c")


def draw_mechanism_matrix(ax: plt.Axes, table: pd.DataFrame) -> None:
    """Draw a compact evidence matrix across mechanism observables."""
    metrics = ["final_BTC", "max_blockage_ratio", "front_bulk_gap_over_L", "connectivity_loss", "Ib_no_pressure"]
    labels = ["BTC", r"$B_{max}$", "front-gap", r"$C_{loss}$", r"$I_b$"]
    normalized = table[metrics].copy()
    for column in metrics:
        max_value = float(normalized[column].max())
        normalized[column] = 0.0 if max_value <= 0 else normalized[column] / max_value
    order = ["low_drive_no_breakthrough", "intermediate_drive_weak_breakthrough", "high_drive_stronger_breakthrough", "N=3000", "N=6000", "N=10000", "906", "907", "908"]
    short_labels = {
        "low_drive_no_breakthrough": "low drive",
        "intermediate_drive_weak_breakthrough": "weak BTC",
        "high_drive_stronger_breakthrough": "higher BTC",
        "N=3000": "N=3000",
        "N=6000": "N=6000",
        "N=10000": "N=10000",
        "906": "upstream source",
        "907": "downstream source",
        "908": "high inventory",
    }
    plot_table = table.set_index("case_label").reindex([label for label in order if label in set(table["case_label"])])
    matrix = table.set_index("case_label").loc[plot_table.index, metrics].copy()
    for column in metrics:
        max_value = float(table[column].max())
        matrix[column] = 0.0 if max_value <= 0 else matrix[column] / max_value
    image = ax.imshow(matrix.to_numpy(dtype=float), cmap="viridis", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(np.arange(len(labels)), labels)
    ax.set_yticks(np.arange(len(matrix.index)), [short_labels.get(str(v), str(v)) for v in matrix.index])
    ax.set_title("Observable separation")
    cbar = ax.figure.colorbar(image, ax=ax, fraction=0.046, pad=0.03)
    cbar.set_label("column-normalized value")
    panel_label(ax, "d", x=0.03, y=0.94)


def save_figure(fig: plt.Figure, stem: str) -> None:
    """Save a figure in PNG, PDF and SVG formats."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for suffix, kwargs in {".png": {"dpi": 600}, ".pdf": {}, ".svg": {}}.items():
        fig.savefig(FIG_DIR / f"{stem}{suffix}", bbox_inches="tight", **kwargs)


def make_figure(table: pd.DataFrame, stem: str) -> None:
    """Create the dimensionless mechanism map figure."""
    configure_matplotlib()
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.5), constrained_layout=True)
    draw_drive_collapse(axes[0, 0], table)
    draw_transport_topology_plane(axes[0, 1], table)
    draw_loading_blockage(axes[1, 0], table)
    draw_mechanism_matrix(axes[1, 1], table)
    save_figure(fig, stem)
    plt.close(fig)


def write_markdown(table: pd.DataFrame, summary: dict[str, Any], out_path: Path) -> None:
    """Write a mechanism-note Markdown file."""
    lines = [
        "# Dimensionless Mechanism Map",
        "",
        "This derived note combines existing Paper 2 evidence into a dimensionless mechanism map. It does not add new DEM or CFD data.",
        "",
        "## Main Result",
        "",
        "- The available drive-state rows support drag-to-weight ratio as a compact migration coordinate.",
        "- The available loading rows show increasing local blockage with dimensionless debris inventory.",
        "- Connectivity loss remains zero in the present window, so these rows support a pre-clogging transport/filtering regime only.",
        "",
        "## Summary Metrics",
        "",
        f"- Rows: {summary['row_count']}",
        f"- Drive-state rows: {summary['drive_state_count']}",
        f"- Loading-state rows: {summary['loading_state_count']}",
        f"- Localized-source rows: {summary['localized_source_state_count']}",
        f"- Mechanism regimes: `{summary['mechanism_regimes']}`",
        f"- Maximum final BTC: `{summary['max_values']['final_BTC']:.6g}`",
        f"- Maximum local blockage ratio: `{summary['max_values']['max_blockage_ratio']:.6g}`",
        f"- Maximum front-bulk gap: `{summary['max_values']['front_bulk_gap_over_L']:.6g}`",
        f"- Maximum connectivity loss: `{summary['max_values']['connectivity_loss']:.6g}`",
        "",
        "## Boundary",
        "",
        summary["evidence_boundary"],
        "The map is not a universal transition diagram, not a pressure-calibrated safety limit, and not experimental CT evidence.",
        "",
        "## Source Table",
        "",
        f"`{OUT_TABLE.relative_to(PROJECT_ROOT)}`",
    ]
    if "drive_correlations" in summary:
        lines.extend(["", "## Drive-State Correlations", ""])
        for key, value in summary["drive_correlations"].items():
            value_text = "constant input/output" if value is None else f"{value:.6f}"
            lines.append(f"- {key}: `{value_text}`")
    if "loading_correlations" in summary:
        lines.extend(["", "## Loading-State Correlations", ""])
        for key, value in summary["loading_correlations"].items():
            value_text = "constant input/output" if value is None else f"{value:.6f}"
            lines.append(f"- {key}: `{value_text}`")
    if "localized_source_correlations" in summary:
        lines.extend(["", "## Localized-Source Correlations", ""])
        for key, value in summary["localized_source_correlations"].items():
            value_text = "constant input/output" if value is None else f"{value:.6f}"
            lines.append(f"- {key}: `{value_text}`")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(out_table: Path = OUT_TABLE, out_json: Path = OUT_JSON, out_md: Path = OUT_MD, fig_stem: str = FIG_STEM) -> dict[str, Any]:
    """Write all dimensionless mechanism-map outputs."""
    table = build_mechanism_table()
    summary = correlation_summary(table)
    out_table.parent.mkdir(parents=True, exist_ok=True)
    OUT_SUPP_TABLE.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(out_table, index=False)
    table.to_csv(OUT_SUPP_TABLE, index=False)
    out_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(table, summary, out_md)
    make_figure(table, fig_stem)
    return summary


def main() -> int:
    """Run the mechanism-map workflow."""
    args = parse_args()
    summary = write_outputs(args.out_table, args.out_json, args.out_md, args.fig_stem)
    print(json.dumps(summary, indent=2))
    print(args.out_table)
    print(args.out_json)
    print(args.out_md)
    print(FIG_DIR / f"{args.fig_stem}.pdf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
