#!/usr/bin/env python3
"""Create a main-text mechanism-synthesis figure for Paper 2."""

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

LOCALIZED_TS = TABLE_DIR / "explicit_localized_production_timeseries.csv"
OBSERVABLE_CASES = TABLE_DIR / "paper2_observable_response_cases.csv"
REPRESENTATIVE = TABLE_DIR / "paper2_fig3_representative_state_source.csv"
LOADING = TABLE_DIR / "paper2_fig4_loading_summary_source.csv"
OUT_SOURCE = TABLE_DIR / "paper2_fig6_mechanism_synthesis_source.csv"
OUT_FAMILY_FINGERPRINT = TABLE_DIR / "paper2_fig6_family_fingerprint_source.csv"
OUT_JSON = DATA_DIR / "paper2_fig6_mechanism_synthesis.json"
OUT_NOTE = NOTE_DIR / "paper2_fig6_mechanism_synthesis.md"
FIG_STEM = "paper2_fig6_mechanism_synthesis"

JOB_LABELS = {
    "906_upstream_source_continue_1M_to_4M": "906 upstream",
    "907_downstream_source_dt5e9_to_10ms": "907 downstream",
    "908_high_inventory_dt5e9_to_10ms": "908 high inventory",
}
JOB_COLORS = {
    "906_upstream_source_continue_1M_to_4M": "#555555",
    "907_downstream_source_dt5e9_to_10ms": "#2166ac",
    "908_high_inventory_dt5e9_to_10ms": "#b2182b",
}
CASE_LABEL_SHORT = {
    "low drive no breakthrough": "low drive",
    "intermediate drive weak breakthrough": "mid drive",
    "high drive stronger breakthrough": "high drive",
    "906 upstream": "906 upstream",
    "907 downstream": "907 downstream",
    "908 high inventory": "908 high inventory",
}
METRICS = [
    "released_fraction",
    "outlet_fraction",
    "penetration_over_L",
    "front_bulk_gap_over_L",
    "max_blockage_ratio",
    "pressure_proxy_ratio",
    "voxel_conductance_loss",
    "connectivity_loss",
]
METRIC_LABELS = {
    "released_fraction": "released",
    "outlet_fraction": "BTC",
    "penetration_over_L": "penetration",
    "front_bulk_gap_over_L": "front-bulk gap",
    "max_blockage_ratio": "blockage",
    "pressure_proxy_ratio": "pressure proxy",
    "voxel_conductance_loss": "conductance loss",
    "connectivity_loss": "connectivity loss",
}


def configure_matplotlib() -> None:
    """Apply compact journal-style Matplotlib settings."""

    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 7.4,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.7,
            "axes.labelsize": 7.6,
            "axes.titlesize": 8.0,
            "xtick.labelsize": 6.8,
            "ytick.labelsize": 6.8,
            "legend.fontsize": 6.7,
            "legend.frameon": False,
        }
    )


def require_columns(table: pd.DataFrame, columns: set[str], name: str) -> None:
    """Raise a clear error if a source table is missing required columns."""

    missing = sorted(columns.difference(table.columns))
    if missing:
        raise ValueError(f"{name} missing columns: {missing}")


def load_inputs() -> dict[str, pd.DataFrame]:
    """Load source tables used by the mechanism-synthesis figure."""

    paths = {
        "localized": LOCALIZED_TS,
        "observable": OBSERVABLE_CASES,
        "representative": REPRESENTATIVE,
        "loading": LOADING,
    }
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing source tables: {missing}")

    tables = {name: pd.read_csv(path) for name, path in paths.items()}
    require_columns(
        tables["localized"],
        {
            "job_id",
            "time_s",
            "source_fraction",
            "downstream_fraction",
            "outlet_fraction",
            "x_q99_over_L",
            "x_max_over_L",
            "debris_count_ok",
        },
        "localized",
    )
    require_columns(tables["observable"], {"case_group", "case_label", *METRICS}, "observable")
    require_columns(tables["representative"], {"drag_to_weight_ratio", "final_BTC"}, "representative")
    require_columns(tables["loading"], {"debris_total_number", "subvoxel_max_blockage_ratio"}, "loading")
    return tables


def normalized_observable_table(observable: pd.DataFrame) -> pd.DataFrame:
    """Return [0, 1]-normalized observables while preserving missing values."""

    normalized = observable[["case_group", "case_label", *METRICS]].copy()
    for metric in METRICS:
        values = normalized[metric].astype(float)
        finite = np.isfinite(values)
        if finite.sum() == 0:
            continue
        lo = float(values[finite].min())
        hi = float(values[finite].max())
        if np.isclose(hi, lo):
            normalized.loc[finite, metric] = 0.0
        else:
            normalized.loc[finite, metric] = (values[finite] - lo) / (hi - lo)
    return normalized


def _rank_corr(x: pd.Series, y: pd.Series) -> float:
    """Compute a small-sample rank correlation without SciPy."""

    frame = pd.DataFrame({"x": x.astype(float), "y": y.astype(float)}).dropna()
    if len(frame) < 3:
        return float("nan")
    if np.isclose(frame["x"].min(), frame["x"].max()) or np.isclose(frame["y"].min(), frame["y"].max()):
        return float("nan")
    return float(frame["x"].rank().corr(frame["y"].rank()))


def mechanism_contrasts(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build compact mechanism-axis contrast values."""

    localized = tables["observable"][tables["observable"]["case_group"] == "localized release"].copy()
    representative = tables["representative"].copy()
    loading = tables["loading"].copy()
    return pd.DataFrame(
        [
            {
                "contrast": "drag -> BTC",
                "value": _rank_corr(representative["drag_to_weight_ratio"], representative["final_BTC"]),
                "family": "drive",
            },
            {
                "contrast": "inventory -> blockage",
                "value": _rank_corr(loading["debris_total_number"], loading["subvoxel_max_blockage_ratio"]),
                "family": "loading",
            },
            {
                "contrast": "release -> front gap",
                "value": _rank_corr(localized["released_fraction"], localized["front_bulk_gap_over_L"]),
                "family": "localized",
            },
            {
                "contrast": "connectivity loss",
                "value": 0.0,
                "family": "topology",
            },
        ]
    )


def family_fingerprint(normalized: pd.DataFrame) -> pd.DataFrame:
    """Condense case-level observables into mechanism-family activation scores."""

    rows: list[dict[str, Any]] = []
    family_labels = {
        "drive scan": "drive",
        "localized release": "localized",
        "loading scan": "loading",
    }
    observables = {
        "outlet arrival": "outlet_fraction",
        "penetration": "penetration_over_L",
        "sparse front": "front_bulk_gap_over_L",
        "local blockage": "max_blockage_ratio",
        "pressure proxy": "pressure_proxy_ratio",
        "connectivity loss": "connectivity_loss",
    }
    for case_group, group in normalized.groupby("case_group", sort=False):
        row: dict[str, Any] = {
            "case_group": case_group,
            "mechanism_family": family_labels.get(str(case_group), str(case_group)),
        }
        for label, column in observables.items():
            values = pd.to_numeric(group[column], errors="coerce")
            row[label] = float(values.max(skipna=True)) if values.notna().any() else np.nan
        rows.append(row)
    preferred_order = {"drive": 0, "localized": 1, "loading": 2}
    out = pd.DataFrame(rows)
    out["_order"] = out["mechanism_family"].map(preferred_order).fillna(99)
    return out.sort_values("_order").drop(columns="_order").reset_index(drop=True)


def write_source_tables(tables: dict[str, pd.DataFrame], normalized: pd.DataFrame, contrasts: pd.DataFrame) -> dict[str, Any]:
    """Write source data and return summary metadata for the figure."""

    localized = tables["localized"].copy()
    localized["front_bulk_gap_over_L"] = localized["x_max_over_L"] - localized["x_q99_over_L"]
    latest = localized.sort_values(["job_id", "time_s"]).groupby("job_id").tail(1)
    row908 = latest[latest["job_id"] == "908_high_inventory_dt5e9_to_10ms"].iloc[0]
    source = pd.concat(
        [
            latest.assign(source_block="localized_final"),
            normalized.assign(source_block="normalized_observables"),
            contrasts.assign(source_block="mechanism_contrasts"),
        ],
        ignore_index=True,
        sort=False,
    )
    OUT_SOURCE.parent.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    NOTE_DIR.mkdir(parents=True, exist_ok=True)
    source.to_csv(OUT_SOURCE, index=False)
    fingerprint = family_fingerprint(normalized)
    fingerprint.to_csv(OUT_FAMILY_FINGERPRINT, index=False)
    summary = {
        "localized_job_count": int(latest["job_id"].nunique()),
        "observable_case_count": int(len(normalized)),
        "final_908_step": int(row908["step"]) if "step" in row908 else None,
        "final_908_time_s": float(row908["time_s"]),
        "final_908_source_fraction": float(row908["source_fraction"]),
        "final_908_downstream_fraction": float(row908["downstream_fraction"]),
        "final_908_outlet_fraction": float(row908["outlet_fraction"]),
        "final_908_x99_over_L": float(row908["x_q99_over_L"]),
        "final_908_xmax_over_L": float(row908["x_max_over_L"]),
        "final_908_front_bulk_gap_over_L": float(row908["front_bulk_gap_over_L"]),
        "max_connectivity_loss": float(tables["observable"]["connectivity_loss"].max(skipna=True)),
        "family_fingerprint_rows": int(len(fingerprint)),
        "claim_boundary": (
            "This figure synthesizes existing DEM and voxel post-processing outputs. "
            "It is not a fitted law, not CFD validation and not a pressure-calibrated "
            "critical-clogging criterion."
        ),
    }
    OUT_JSON.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    OUT_NOTE.write_text(
        "# Paper 2 Fig. 8 Mechanism Synthesis\n\n"
        f"- Localized jobs: `{summary['localized_job_count']}`.\n"
        f"- Observable cases: `{summary['observable_case_count']}`.\n"
        f"- Latest 908 frame: `{summary['final_908_time_s']:.6g} s`, "
        f"`x99/L={summary['final_908_x99_over_L']:.4f}`, "
        f"`xmax/L={summary['final_908_xmax_over_L']:.4f}`.\n"
        f"- Maximum connectivity loss: `{summary['max_connectivity_loss']:.3g}`.\n\n"
        "## Boundary\n\n"
        f"{summary['claim_boundary']}\n",
        encoding="utf-8",
    )
    return summary


def panel_label(ax: plt.Axes, label: str) -> None:
    """Add a small panel label."""

    ax.text(-0.12, 1.06, label, transform=ax.transAxes, weight="bold", fontsize=9, va="top")


def draw_figure(tables: dict[str, pd.DataFrame], normalized: pd.DataFrame, contrasts: pd.DataFrame) -> None:
    """Render the four-panel mechanism synthesis figure."""

    configure_matplotlib()
    localized = tables["localized"].sort_values(["job_id", "time_s"]).copy()
    localized["front_bulk_gap_over_L"] = localized["x_max_over_L"] - localized["x_q99_over_L"]
    localized_latest = localized.sort_values(["job_id", "time_s"]).groupby("job_id").tail(1).copy()
    representative = tables["representative"].sort_values("drag_to_weight_ratio").copy()
    loading = tables["loading"].sort_values("debris_total_number").copy()

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.45), constrained_layout=True)
    ax_drive, ax_source, ax_loading, ax_heat = axes.ravel()

    ax_drive.scatter(
        representative["drag_to_weight_ratio"],
        representative["final_BTC"],
        s=74,
        c=representative["drag_to_weight_ratio"],
        cmap="Blues",
        edgecolor="#222222",
        linewidth=0.45,
        zorder=3,
    )
    for _, row in representative.iterrows():
        label = (
            "low"
            if row["final_BTC"] == 0
            else "weak"
            if row["final_BTC"] < 0.05
            else "stronger"
        )
        ax_drive.annotate(
            label,
            xy=(float(row["drag_to_weight_ratio"]), float(row["final_BTC"])),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=6.6,
        )
    ax_drive.set_xlabel(r"drag-to-weight ratio $F_d/W$")
    ax_drive.set_ylabel("final BTC")
    ax_drive.set_title("Drive activates outlet arrival")
    ax_drive.set_ylim(-0.006, 0.092)
    ax_drive.grid(True, lw=0.35, alpha=0.35)
    panel_label(ax_drive, "a")

    for _, row in localized_latest.iterrows():
        job_id = str(row["job_id"])
        label = JOB_LABELS.get(job_id, job_id).replace(" high inventory", "")
        ax_source.scatter(
            row["source_fraction"],
            row["front_bulk_gap_over_L"],
            s=55 + 0.004 * float(row["debris_count"]),
            color=JOB_COLORS.get(job_id, "#333333"),
            edgecolor="#222222",
            linewidth=0.45,
            label=JOB_LABELS.get(job_id, job_id),
            zorder=3,
        )
        ax_source.annotate(
            label,
            xy=(float(row["source_fraction"]), float(row["front_bulk_gap_over_L"])),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=6.3,
        )
    ax_source.set_xlabel("source-retained fraction")
    ax_source.set_ylabel(r"$x_{max}-x_{99}$")
    ax_source.set_title("Localized release splits bulk and front")
    ax_source.set_xlim(0.54, 0.93)
    ax_source.set_ylim(0.24, 0.63)
    ax_source.grid(True, lw=0.35, alpha=0.35)
    panel_label(ax_source, "b")

    ax_loading.scatter(
        loading["debris_total_number"],
        loading["subvoxel_max_blockage_ratio"] * 1e6,
        s=78,
        color="#1b9e77",
        edgecolor="#222222",
        linewidth=0.45,
        zorder=3,
    )
    for _, row in loading.iterrows():
        ax_loading.annotate(
            f"{int(row['debris_total_number'])}",
            xy=(float(row["debris_total_number"]), float(row["subvoxel_max_blockage_ratio"]) * 1e6),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=6.6,
        )
    ax_loading.set_xlabel(r"injected debris count $N_f$")
    ax_loading.set_ylabel(r"$B_{max}$ ($\times 10^{-6}$)")
    ax_loading.set_title("Inventory amplifies local blockage")
    ax_loading.margins(x=0.12, y=0.16)
    ax_loading.grid(True, lw=0.35, alpha=0.35)
    panel_label(ax_loading, "c")

    fingerprint = family_fingerprint(normalized)
    heat_metrics = [
        "outlet arrival",
        "penetration",
        "sparse front",
        "local blockage",
        "pressure proxy",
        "connectivity loss",
    ]
    heat = fingerprint[heat_metrics].astype(float).to_numpy()
    masked = np.ma.masked_invalid(heat)
    cmap = mpl.colormaps["cividis"].copy()
    cmap.set_bad("#efefef")
    im = ax_heat.imshow(masked, aspect="auto", cmap=cmap, vmin=0.0, vmax=1.0)
    case_labels = fingerprint["mechanism_family"].tolist()
    ax_heat.set_yticks(np.arange(len(case_labels)))
    ax_heat.set_yticklabels(case_labels)
    ax_heat.set_xticks(np.arange(len(heat_metrics)))
    ax_heat.set_xticklabels(heat_metrics, rotation=32, ha="right")
    ax_heat.set_title("Mechanism-family fingerprint")
    ax_heat.tick_params(length=0)
    for spine in ax_heat.spines.values():
        spine.set_visible(False)
    cbar = fig.colorbar(im, ax=ax_heat, fraction=0.046, pad=0.02)
    cbar.ax.set_title("scaled", fontsize=6.8, pad=4)
    panel_label(ax_heat, "d")

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for suffix in ("png", "pdf", "svg"):
        fig.savefig(FIG_DIR / f"{FIG_STEM}.{suffix}", dpi=500 if suffix == "png" else None, bbox_inches="tight")
    preview = FIG_DIR / f"{FIG_STEM}_gray_preview.png"
    fig.savefig(preview, dpi=300, bbox_inches="tight", pil_kwargs={"compress_level": 6})
    try:
        from PIL import Image, ImageOps

        with Image.open(preview) as image:
            ImageOps.grayscale(image.convert("RGB")).save(preview)
    except ImportError:
        pass
    plt.close(fig)


def run() -> dict[str, Any]:
    """Run the mechanism-synthesis figure workflow."""

    tables = load_inputs()
    normalized = normalized_observable_table(tables["observable"])
    contrasts = mechanism_contrasts(tables)
    summary = write_source_tables(tables, normalized, contrasts)
    draw_figure(tables, normalized, contrasts)
    return summary


def main() -> int:
    """Command-line entry point."""

    summary = run()
    print(json.dumps(summary, indent=2))
    print(FIG_DIR / f"{FIG_STEM}.pdf")
    print(OUT_SOURCE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
