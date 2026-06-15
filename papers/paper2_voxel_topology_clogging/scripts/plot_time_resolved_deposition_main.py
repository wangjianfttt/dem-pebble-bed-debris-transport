#!/usr/bin/env python3
"""Create a main-text time-resolved deposition figure for Paper 2."""

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

DEPOSITION = TABLE_DIR / "paper2_time_resolved_deposition_source.csv"
BLOCKAGE = TABLE_DIR / "paper2_time_resolved_blockage_profile_source.csv"
OUT_SOURCE = TABLE_DIR / "paper2_fig10_time_resolved_deposition_source.csv"
OUT_SUMMARY = DATA_DIR / "paper2_fig10_time_resolved_deposition.json"
OUT_NOTE = NOTE_DIR / "paper2_fig10_time_resolved_deposition.md"
FIG_STEM = "paper2_fig10_time_resolved_deposition"


def configure_matplotlib() -> None:
    """Configure compact journal-style plotting defaults."""
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
    """Add a small bold panel label to an axis."""
    ax.text(-0.13, 1.06, label, transform=ax.transAxes, weight="bold", fontsize=9, va="top")


def save_figure(fig: plt.Figure, stem: str) -> None:
    """Save a Matplotlib figure in raster and vector formats."""
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


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load and validate time-resolved deposition and blockage-profile tables."""
    dep = pd.read_csv(DEPOSITION)
    prof = pd.read_csv(BLOCKAGE)
    required_dep = {
        "elapsed_time",
        "BTC",
        "x_mean_over_L",
        "x_q90_over_L",
        "x_q99_over_L",
        "blockage_centroid_over_L",
        "peak_blockage_ratio",
        "peak_blockage_x_over_L",
    }
    required_prof = {"elapsed_time", "x_over_L", "blockage_ratio"}
    missing_dep = sorted(required_dep.difference(dep.columns))
    missing_prof = sorted(required_prof.difference(prof.columns))
    if missing_dep or missing_prof:
        raise ValueError(f"Missing columns: deposition={missing_dep}, blockage={missing_prof}")
    if dep.empty or prof.empty:
        raise ValueError("Time-resolved source tables must not be empty.")
    return dep.sort_values("elapsed_time").copy(), prof.sort_values(["elapsed_time", "x_over_L"]).copy()


def build_source_table(dep: pd.DataFrame, prof: pd.DataFrame) -> pd.DataFrame:
    """Build a compact source table for the main-text figure."""
    dep_source = dep.copy()
    dep_source["source_type"] = "time_trace"
    prof_source = prof.copy()
    prof_source["source_type"] = "blockage_profile"
    return pd.concat([dep_source, prof_source], ignore_index=True, sort=False)


def first_breakthrough_time(dep: pd.DataFrame) -> float | None:
    """Return the first elapsed time with non-zero BTC."""
    positive = dep[pd.to_numeric(dep["BTC"], errors="coerce") > 0.0]
    if positive.empty:
        return None
    return float(positive["elapsed_time"].iloc[0])


def make_figure(dep: pd.DataFrame, prof: pd.DataFrame) -> dict[str, object]:
    """Generate the time-resolved deposition and front-migration figure."""
    dep = dep.copy()
    prof = prof.copy()
    dep["time_ms"] = dep["elapsed_time"] * 1e3
    prof["time_ms"] = prof["elapsed_time"] * 1e3

    pivot = prof.pivot_table(index="x_over_L", columns="time_ms", values="blockage_ratio", aggfunc="mean")
    x_vals = pivot.index.to_numpy(dtype=float)
    t_vals = pivot.columns.to_numpy(dtype=float)
    z = pivot.to_numpy(dtype=float) * 1e6

    fb = first_breakthrough_time(dep)
    q99_09 = dep.loc[dep["x_q99_over_L"] >= 0.9, "elapsed_time"]
    q99_09_time = float(q99_09.iloc[0]) if not q99_09.empty else None

    fig, axes = plt.subplots(2, 2, figsize=(7.1, 5.45), constrained_layout=True)

    ax = axes[0, 0]
    im = ax.pcolormesh(t_vals, x_vals, z, shading="auto", cmap="cividis")
    ax.plot(dep["time_ms"], dep["x_mean_over_L"], color="#0072B2", lw=1.25, label="mean")
    ax.plot(dep["time_ms"], dep["x_q99_over_L"], color="#D55E00", lw=1.25, label="99th percentile")
    ax.plot(dep["time_ms"], dep["blockage_centroid_over_L"], color="#009E73", lw=1.05, ls="--", label="blockage centroid")
    if fb is not None:
        ax.axvline(fb * 1e3, color="#f2f2f2", lw=0.9, ls=":", alpha=0.95)
    ax.set_xlabel("elapsed time (ms)")
    ax.set_ylabel(r"axial position $x/L$")
    ax.set_title("Deposition field and moving front")
    ax.legend(
        loc="upper left",
        ncol=1,
        frameon=True,
        framealpha=0.86,
        facecolor="white",
        edgecolor="none",
        handlelength=1.8,
    )
    fig.colorbar(im, ax=ax, pad=0.01, fraction=0.05, label=r"$B(x,t)$ ($\times 10^{-6}$)")
    panel_label(ax, "a")

    ax = axes[0, 1]
    ax.plot(dep["time_ms"], dep["x_mean_over_L"], color="#0072B2", lw=1.35, label="mean")
    ax.plot(dep["time_ms"], dep["x_q90_over_L"], color="#CC79A7", lw=1.15, label="90th percentile")
    ax.plot(dep["time_ms"], dep["x_q99_over_L"], color="#D55E00", lw=1.35, label="99th percentile")
    ax.plot(dep["time_ms"], dep["peak_blockage_x_over_L"], color="#009E73", lw=1.05, ls="--", label="peak blockage")
    if fb is not None:
        ax.axvline(fb * 1e3, color="#555555", lw=0.8, ls=":", label="first non-zero BTC")
    if q99_09_time is not None:
        ax.axvline(q99_09_time * 1e3, color="#777777", lw=0.8, ls="-.", label=r"$x_{99}/L \geq 0.9$")
    ax.set_xlabel("elapsed time (ms)")
    ax.set_ylabel(r"axial position $x/L$")
    ax.set_ylim(0, 1.04)
    ax.set_title("Bulk and leading-tail migration")
    ax.legend(loc="upper left", ncol=1, frameon=True, framealpha=0.82, facecolor="white", edgecolor="none")
    ax.grid(True, linewidth=0.35, alpha=0.35)
    panel_label(ax, "b")

    ax = axes[1, 0]
    ax.plot(dep["time_ms"], dep["BTC"], color="#0072B2", lw=1.45)
    ax.scatter(dep["time_ms"], dep["BTC"], s=11, color="#0072B2", edgecolor="white", linewidth=0.25, zorder=3)
    if fb is not None:
        ax.axvline(fb * 1e3, color="#555555", lw=0.8, ls=":")
    if q99_09_time is not None:
        ax.axvline(q99_09_time * 1e3, color="#777777", lw=0.8, ls="-.")
    ax.set_xlabel("elapsed time (ms)")
    ax.set_ylabel("BTC")
    ax.set_title("Delayed weak breakthrough tail")
    ax.grid(True, linewidth=0.35, alpha=0.35)
    panel_label(ax, "c")

    ax = axes[1, 1]
    ax.plot(dep["time_ms"], dep["peak_blockage_ratio"] * 1e6, color="#D55E00", lw=1.35, label=r"$B_{max}$")
    ax.scatter(
        dep["time_ms"],
        dep["peak_blockage_ratio"] * 1e6,
        s=12,
        color="#D55E00",
        edgecolor="white",
        linewidth=0.25,
        zorder=3,
    )
    ax.plot(
        dep["time_ms"],
        dep["profile_mean_pressure_increase_ratio"] * 1e6,
        color="#009E73",
        lw=1.1,
        ls="--",
        label=r"mean $\Delta p$ proxy",
    )
    ax.set_xlabel("elapsed time (ms)")
    ax.set_ylabel(r"response ($\times 10^{-6}$)")
    ax.set_title("Local loading relaxes while proxy stays small")
    ax.legend(loc="upper right", frameon=True, framealpha=0.84, facecolor="white", edgecolor="none")
    ax.grid(True, linewidth=0.35, alpha=0.35)
    panel_label(ax, "d")

    save_figure(fig, FIG_STEM)
    plt.close(fig)

    peak_idx = dep["peak_blockage_ratio"].idxmax()
    final = dep.iloc[-1]
    summary = {
        "figure": FIG_STEM,
        "input_deposition_rows": int(len(dep)),
        "input_blockage_profile_rows": int(len(prof)),
        "first_nonzero_BTC_elapsed_s": fb,
        "q99_reaches_0p9_elapsed_s": q99_09_time,
        "final_BTC": float(final["BTC"]),
        "final_x_mean_over_L": float(final["x_mean_over_L"]),
        "final_x_q99_over_L": float(final["x_q99_over_L"]),
        "peak_blockage_ratio": float(dep.loc[peak_idx, "peak_blockage_ratio"]),
        "peak_blockage_time_s": float(dep.loc[peak_idx, "elapsed_time"]),
        "peak_blockage_x_over_L": float(dep.loc[peak_idx, "peak_blockage_x_over_L"]),
        "claim_boundary": "Representative time-resolved case only; supports delayed leading-tail breakthrough, not a universal speed law or critical-clogging threshold.",
    }
    return summary


def write_note(summary: dict[str, object]) -> None:
    """Write a short stage note for the generated figure."""
    lines = [
        "# Paper 2 Time-Resolved Deposition Figure",
        "",
        f"Figure: `{summary['figure']}`",
        f"Deposition trace rows: {summary['input_deposition_rows']}",
        f"Blockage profile rows: {summary['input_blockage_profile_rows']}",
        f"First non-zero BTC elapsed time: `{summary['first_nonzero_BTC_elapsed_s']}` s",
        f"Final BTC: `{summary['final_BTC']}`",
        "",
        "## Boundary",
        "",
        str(summary["claim_boundary"]),
    ]
    OUT_NOTE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    """Generate the time-resolved deposition figure and metadata."""
    configure_matplotlib()
    dep, prof = load_inputs()
    source = build_source_table(dep, prof)
    OUT_SOURCE.parent.mkdir(parents=True, exist_ok=True)
    source.to_csv(OUT_SOURCE, index=False)
    summary = make_figure(dep, prof)
    OUT_SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_note(summary)
    print(json.dumps(summary, indent=2))
    print(FIG_DIR / f"{FIG_STEM}.pdf")
    print(OUT_SOURCE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
