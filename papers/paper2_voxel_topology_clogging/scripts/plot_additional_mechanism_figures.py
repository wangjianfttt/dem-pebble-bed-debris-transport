#!/usr/bin/env python3
"""Create additional mechanism-focused Paper 2 figures from existing source tables."""

from __future__ import annotations

import json
from pathlib import Path

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
OBSERVABLES = TABLE_DIR / "paper2_observable_response_cases.csv"
Q908 = TABLE_DIR / "paper2_908_spatial_quantiles.csv"


def configure_matplotlib() -> None:
    """Configure a compact journal-style Matplotlib theme."""
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
            "legend.fontsize": 6.8,
            "legend.frameon": False,
        }
    )


def panel_label(ax: plt.Axes, label: str) -> None:
    """Add a small bold panel label."""
    ax.text(-0.12, 1.06, label, transform=ax.transAxes, weight="bold", fontsize=9, va="top")


def save_figure(fig: plt.Figure, stem: str) -> None:
    """Save a figure in manuscript-ready raster and vector formats."""
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


def minmax_scale(values: pd.Series) -> pd.Series:
    """Min-max scale a numeric series while preserving missing values."""
    numeric = pd.to_numeric(values, errors="coerce")
    finite = numeric[np.isfinite(numeric)]
    if finite.empty:
        return numeric * np.nan
    lo = float(finite.min())
    hi = float(finite.max())
    if np.isclose(hi, lo):
        scaled = numeric.copy()
        scaled[np.isfinite(scaled)] = 0.0 if np.isclose(hi, 0.0) else 1.0
        return scaled
    return (numeric - lo) / (hi - lo)


def make_mechanism_landscape() -> dict[str, object]:
    """Generate a cross-case response landscape without fitting sparse samples."""
    dim = pd.read_csv(DIMENSIONLESS)
    obs = pd.read_csv(OBSERVABLES)

    heat_cols = [
        "released_fraction",
        "outlet_fraction",
        "penetration_over_L",
        "front_bulk_gap_over_L",
        "max_blockage_ratio",
        "pressure_proxy_ratio",
        "voxel_conductance_loss",
        "connectivity_loss",
    ]
    labels = {
        "released_fraction": "release",
        "outlet_fraction": "outlet",
        "penetration_over_L": "penetration",
        "front_bulk_gap_over_L": "front-gap",
        "max_blockage_ratio": r"$B_{max}$",
        "pressure_proxy_ratio": r"$\Delta p$ proxy",
        "voxel_conductance_loss": "conductance loss",
        "connectivity_loss": r"$C_{loss}$",
    }
    heat = pd.DataFrame({col: minmax_scale(obs[col]) for col in heat_cols})
    heat_source = obs[["case_group", "case_label", "control_label", "control_value"]].join(
        heat.add_prefix("normalized_")
    )
    heat_source.to_csv(TABLE_DIR / "paper2_fig8_observable_heatmap_source.csv", index=False)

    fig, axes = plt.subplots(2, 2, figsize=(7.1, 5.35), constrained_layout=True)
    ax = axes[0, 0]
    families = {
        "drive_state": ("o", "#0072B2", "drive axis"),
        "loading_state": ("s", "#D55E00", "loading axis"),
    }
    for family, (marker, color, label) in families.items():
        sub = dim[dim["evidence_family"] == family].copy()
        x = sub["dimensionless_loading"].to_numpy(float)
        y = sub["final_BTC"].to_numpy(float)
        sizes = 48 + 1.45e6 * sub["max_blockage_ratio"].to_numpy(float)
        ax.scatter(
            x,
            y,
            color=color,
            s=sizes,
            marker=marker,
            edgecolor="#222222",
            linewidth=0.45,
            label=label,
            zorder=3,
        )
        for _, row in sub.iterrows():
            case_label = str(row["case_label"])
            short_label = (
                "low"
                if "low_drive" in case_label
                else "weak"
                if "weak_breakthrough" in case_label
                else "strong"
                if "stronger_breakthrough" in case_label
                else f"N={int(row['debris_total_number'])}"
            )
            offset = (-20, 6) if short_label == "weak" else ((8, -11) if short_label == "N=3000" else (3, 3))
            ax.annotate(
                short_label,
                xy=(float(row["dimensionless_loading"]), float(row["final_BTC"])),
                xytext=offset,
                textcoords="offset points",
                fontsize=6.0,
                color="#333333",
            )
    ax.set_xscale("log")
    ax.set_xlabel(r"dimensionless debris loading")
    ax.set_ylabel("final BTC")
    ax.set_title("Discrete response states")
    ax.grid(True, linewidth=0.35, alpha=0.35)
    family_handles, family_labels = ax.get_legend_handles_labels()
    ax.legend(
        family_handles,
        family_labels,
        loc="center right",
        handletextpad=0.4,
        borderpad=0.2,
        labelspacing=0.35,
    )
    panel_label(ax, "a")

    ax = axes[0, 1]
    loading = dim[dim["evidence_family"] == "loading_state"].copy()
    ax.scatter(
        loading["debris_total_number"],
        loading["max_blockage_ratio"] * 1e6,
        s=70,
        c=loading["voxel_conductance_loss"] * 1e6,
        cmap="magma",
        edgecolor="#222222",
        linewidth=0.45,
        zorder=3,
    )
    for _, row in loading.iterrows():
        ax.annotate(
            f"{int(row['debris_total_number'])}",
            xy=(float(row["debris_total_number"]), float(row["max_blockage_ratio"]) * 1e6),
            xytext=(4, 4),
            textcoords="offset points",
            fontsize=6.2,
        )
    ax.set_xlabel(r"injected debris count $N_f$")
    ax.set_ylabel(r"$B_{max}$ ($\times 10^{-6}$)")
    ax.set_title("Inventory response")
    ax.margins(x=0.10, y=0.12)
    ax.grid(True, linewidth=0.35, alpha=0.35)
    panel_label(ax, "b")

    ax = axes[1, 0]
    mat = heat.to_numpy(dtype=float)
    masked = np.ma.masked_invalid(mat)
    cmap = mpl.colormaps["cividis"].copy()
    cmap.set_bad("#eeeeee")
    im = ax.imshow(masked, aspect="auto", cmap=cmap, vmin=0.0, vmax=1.0)
    short_case_labels = (
        obs["case_label"]
        .astype(str)
        .replace(
            {
                "low drive no breakthrough": "low drive",
                "intermediate drive weak breakthrough": "weak drive",
                "high drive stronger breakthrough": "strong drive",
            }
        )
    )
    ax.set_yticks(np.arange(len(obs)), short_case_labels, fontsize=6.4)
    ax.set_xticks(np.arange(len(heat_cols)), [labels[col] for col in heat_cols], rotation=40, ha="right")
    ax.set_title("Observable fingerprint")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)
    fig.colorbar(im, ax=ax, pad=0.01, fraction=0.04, label="normalized value")
    panel_label(ax, "c")

    ax = axes[1, 1]
    ax.set_axis_off()
    ax.set_title("Staged clogging assessment", pad=3)
    stages = [
        ("BTC", "transport\ncontamination", "#0072B2"),
        (r"$B_{max}$", "deposition\nlocalization", "#D55E00"),
        (r"$C_{loss}$", "structural\ndegradation", "#CC79A7"),
        (r"$\Delta p$", "hydraulic\nconfirmation", "#009E73"),
    ]
    assessment_source = pd.DataFrame(
        {
            "stage": [item[0] for item in stages],
            "interpretation": [
                "transport_contamination_indicator",
                "deposition_localization_indicator",
                "structural_degradation_indicator",
                "hydraulic_confirmation",
            ],
            "boundary": [
                "does_not_by_itself_indicate_clogging",
                "sub_voxel_local_loading_indicator",
                "resolution_limited_connectivity_metric",
                "requires_pressure_solution_or_measurement",
            ],
        }
    )
    assessment_source.to_csv(TABLE_DIR / "paper2_fig8_staged_assessment_source.csv", index=False)
    xs = [0.13, 0.38, 0.63, 0.88]
    y = 0.60
    for idx, ((metric, role, color), x) in enumerate(zip(stages, xs)):
        ax.text(
            x,
            y,
            f"{metric}\n{role}",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=6.6,
            color="#111111",
            bbox={
                "boxstyle": "round,pad=0.25,rounding_size=0.08",
                "facecolor": "#ffffff",
                "edgecolor": color,
                "linewidth": 1.2,
            },
        )
        if idx < len(xs) - 1:
            ax.annotate(
                "",
                xy=(xs[idx + 1] - 0.095, y),
                xytext=(x + 0.095, y),
                xycoords=ax.transAxes,
                textcoords=ax.transAxes,
                arrowprops={"arrowstyle": "-|>", "lw": 0.75, "color": "#555555", "shrinkA": 0, "shrinkB": 0},
            )
    ax.text(
        0.5,
        0.18,
        "assessment order, not a universal transition law",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=6.8,
        color="#444444",
    )
    panel_label(ax, "d")

    save_figure(fig, "paper2_fig8_response_landscape")
    plt.close(fig)
    dim.to_csv(TABLE_DIR / "paper2_fig8_response_landscape_source.csv", index=False)
    return {
        "figure": "paper2_fig8_response_landscape",
        "input_rows_dimensionless": int(len(dim)),
        "input_rows_observable": int(len(obs)),
        "note": "Sparse case families are plotted as encoded states, not fitted response laws; panel d gives a staged assessment interpretation rather than a pressure-calibrated clogging criterion.",
    }


def make_sparse_front_diagnostics() -> dict[str, object]:
    """Generate a time-resolved sparse-front diagnostic for case 908."""
    q = pd.read_csv(Q908)
    q = q.sort_values("time_s").copy()
    q["time_ms"] = q["time_s"] * 1e3
    q["front_minus_p99"] = q["x_max_over_L"] - q["x_p99_over_L"]
    q["tail_minus_p99"] = q["x_p999_over_L"] - q["x_p99_over_L"]
    source = q[
        [
            "step",
            "time_s",
            "time_ms",
            "x_p50_over_L",
            "x_p90_over_L",
            "x_p99_over_L",
            "x_p999_over_L",
            "x_max_over_L",
            "front_minus_p99",
            "tail_minus_p99",
            "fraction_x_gt_0p40",
            "fraction_x_gt_0p60",
            "fraction_x_gt_0p80",
            "fraction_x_gt_0p95",
            "fraction_x_ge_1p00",
        ]
    ]
    source.to_csv(TABLE_DIR / "paper2_fig9_sparse_front_diagnostics_source.csv", index=False)

    fig, axes = plt.subplots(2, 2, figsize=(7.1, 5.4), constrained_layout=True)
    ax = axes[0, 0]
    quantiles = [
        ("x_p50_over_L", "p50", "#4D4D4D"),
        ("x_p90_over_L", "p90", "#0072B2"),
        ("x_p99_over_L", "p99", "#009E73"),
        ("x_p999_over_L", "p99.9", "#E69F00"),
        ("x_max_over_L", "max", "#D55E00"),
    ]
    for col, label, color in quantiles:
        ax.plot(q["time_ms"], q[col], color=color, linewidth=1.15, label=label)
    ax.axhline(1.0, color="#777777", linestyle="--", linewidth=0.8)
    ax.set_xlabel("time (ms)")
    ax.set_ylabel(r"axial position $x/L$")
    ax.set_title("Bulk quantiles and rare front separate")
    ax.set_ylim(0.30, 1.03)
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.legend(ncol=3, loc="lower right")
    panel_label(ax, "a")

    ax = axes[0, 1]
    for col, label, color in [
        ("fraction_x_gt_0p40", r"$x/L>0.40$", "#0072B2"),
        ("fraction_x_gt_0p60", r"$x/L>0.60$", "#009E73"),
        ("fraction_x_gt_0p80", r"$x/L>0.80$", "#E69F00"),
        ("fraction_x_gt_0p95", r"$x/L>0.95$", "#D55E00"),
    ]:
        y = q[col].replace(0, np.nan)
        ax.plot(q["time_ms"], y, linewidth=1.15, color=color, label=label)
    ax.set_yscale("log")
    ax.set_xlabel("time (ms)")
    ax.set_ylabel("particle fraction")
    ax.set_title("Tail population remains small")
    ax.grid(True, which="both", linewidth=0.35, alpha=0.35)
    ax.legend(loc="lower right")
    panel_label(ax, "b")

    ax = axes[1, 0]
    ax.plot(q["time_ms"], q["front_minus_p99"], color="#D55E00", linewidth=1.2, label=r"$x_{max}-x_{99}$")
    ax.plot(q["time_ms"], q["tail_minus_p99"], color="#E69F00", linewidth=1.2, label=r"$x_{99.9}-x_{99}$")
    ax.set_xlabel("time (ms)")
    ax.set_ylabel(r"separation in $x/L$")
    ax.set_title("Sparse front is not a coherent bulk front")
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.legend(loc="upper left")
    panel_label(ax, "c")

    ax = axes[1, 1]
    ax.scatter(
        q["x_p99_over_L"],
        q["x_max_over_L"],
        c=q["time_ms"],
        cmap="viridis",
        s=24,
        edgecolor="#222222",
        linewidth=0.25,
    )
    ax.plot([0.38, 1.0], [0.38, 1.0], color="#777777", linestyle="--", linewidth=0.8)
    ax.set_xlabel(r"$x_{99}/L$")
    ax.set_ylabel(r"$x_{max}/L$")
    ax.set_title("Front advance outpaces population bulk")
    ax.grid(True, linewidth=0.35, alpha=0.35)
    cbar = fig.colorbar(ax.collections[0], ax=ax, pad=0.01, fraction=0.05)
    cbar.set_label("time (ms)")
    panel_label(ax, "d")

    save_figure(fig, "paper2_fig9_sparse_front_diagnostics")
    plt.close(fig)
    return {
        "figure": "paper2_fig9_sparse_front_diagnostics",
        "input_rows": int(len(q)),
        "final_time_ms": float(q["time_ms"].iloc[-1]),
        "final_x99_over_L": float(q["x_p99_over_L"].iloc[-1]),
        "final_xmax_over_L": float(q["x_max_over_L"].iloc[-1]),
        "final_fraction_beyond_0p95": float(q["fraction_x_gt_0p95"].iloc[-1]),
        "final_fraction_crossing_outlet": float(q["fraction_x_ge_1p00"].iloc[-1]),
    }


def main() -> int:
    """Build the additional mechanism figures and provenance source tables."""
    configure_matplotlib()
    summaries = [make_mechanism_landscape(), make_sparse_front_diagnostics()]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    NOTE_DIR.mkdir(parents=True, exist_ok=True)
    out_json = DATA_DIR / "paper2_additional_mechanism_figures.json"
    out_json.write_text(json.dumps(summaries, indent=2), encoding="utf-8")
    out_note = NOTE_DIR / "paper2_additional_mechanism_figures.md"
    out_note.write_text(
        "\n".join(
            [
                "# Additional Mechanism Figures",
                "",
                "These figures are mined from existing Paper 2 source tables to reduce prose-heavy mechanism exposition.",
                "Sparse categorical evidence is shown as encoded states or normalized heatmaps; no fitted trend law is implied.",
                "",
                f"- Fig. 9: `{FIG_DIR / 'paper2_fig8_response_landscape.pdf'}`",
                f"- Fig. 10: `{FIG_DIR / 'paper2_fig9_sparse_front_diagnostics.pdf'}`",
                f"- Summary JSON: `{out_json}`",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summaries, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
