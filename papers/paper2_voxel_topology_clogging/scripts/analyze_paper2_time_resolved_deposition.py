#!/usr/bin/env python3
"""Analyze time-resolved debris deposition for a representative Paper 2 case."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from src.models.ergun import ergun_pressure_gradient
from src.postprocess.read_liggghts_dump import read_liggghts_dump


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
DATA_DIR = PAPER_DIR / "data"
TABLE_DIR = PAPER_DIR / "tables"
FIG_DIR = PAPER_DIR / "figures"
NOTE_DIR = PAPER_DIR / "notes"

CASE_DIR = PROJECT_ROOT / "cases" / "clogging_scan" / "paper1_velocity_scan" / "paper1_df0p0225_ug2_seed401"
CASE_NAME = "paper1_df0p0225_ug2_seed401"
BASE_CONFIG = PROJECT_ROOT / "configs" / "base_li4sio4_1mm_10k_axial_cuboid.yaml"
BASELINE_VOXEL = PROJECT_ROOT / "data" / "processed" / "ct_pipeline_li4sio4_1mm_10k_axial_cuboid_piston_compacted" / "bed_voxel_effective.npz"
BASELINE_TOPOLOGY = DATA_DIR / "baseline_topology_metrics_effective.json"
BTC_SOURCE = TABLE_DIR / "paper2_fig4_loading_btc_source.csv"

OUT_SUMMARY = TABLE_DIR / "paper2_time_resolved_deposition_source.csv"
OUT_PROFILE = TABLE_DIR / "paper2_time_resolved_blockage_profile_source.csv"
OUT_FIG = FIG_DIR / "paper2_figS4_time_resolved_deposition"
OUT_NOTE = NOTE_DIR / "stage_report_time_resolved_deposition_2026-06-09.md"

STANDARD_FINAL_TIMESTEP = 16038000
N_BINS = 20


def configure_matplotlib() -> None:
    """Configure a compact publication-oriented Matplotlib style."""
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


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML mapping."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping: {path}")
    return data


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON mapping."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON mapping: {path}")
    return data


def standard_type2_dumps() -> list[Path]:
    """Return the standard-window type-2 dumps for the representative case."""
    patterns = [f"{CASE_NAME}_type2_*.dump", f"{CASE_NAME}_cont_type2_*.dump"]
    found: dict[int, Path] = {}
    for pattern in patterns:
        for path in CASE_DIR.glob(pattern):
            timestep = timestep_from_name(path)
            if timestep <= STANDARD_FINAL_TIMESTEP:
                found[timestep] = path
    if not found:
        raise FileNotFoundError(f"No standard-window type2 dumps found in {CASE_DIR}")
    return [found[timestep] for timestep in sorted(found)]


def timestep_from_name(path: Path) -> int:
    """Extract the trailing LIGGGHTS timestep from a dump filename."""
    match = re.search(r"_(\d+)\.dump$", path.name)
    if match is None:
        raise ValueError(f"Cannot parse timestep from {path.name}")
    return int(match.group(1))


def baseline_pore_volumes() -> tuple[np.ndarray, np.ndarray, float, dict[str, Any]]:
    """Return x-bin centers, pore volumes, voxel size and metadata from baseline voxel."""
    data = np.load(BASELINE_VOXEL, allow_pickle=True)
    voxel = data["voxel"]
    metadata = json.loads(str(data["metadata"]))
    voxel_size = float(metadata["voxel_size"])
    domain = metadata["domain"]
    void = voxel == 0
    x_edges = np.linspace(float(domain["x_min"]), float(domain["x_max"]), N_BINS + 1)
    x_centers = 0.5 * (x_edges[:-1] + x_edges[1:])
    index_edges = np.floor((x_edges - float(domain["x_min"])) / voxel_size).astype(int)
    index_edges[0] = 0
    index_edges[-1] = voxel.shape[0]
    pore_volumes = []
    for left, right in zip(index_edges[:-1], index_edges[1:]):
        right = max(left + 1, min(right, voxel.shape[0]))
        pore_volumes.append(float(void[left:right, :, :].sum() * voxel_size**3))
    return x_centers, np.asarray(pore_volumes, dtype=float), voxel_size, metadata


def debris_volume_profile(frame: pd.DataFrame, x_edges: np.ndarray) -> np.ndarray:
    """Compute debris volume per x bin for one frame."""
    if frame.empty:
        return np.zeros(len(x_edges) - 1, dtype=float)
    radii = frame["radius"].to_numpy(dtype=float)
    volumes = 4.0 * np.pi * radii**3 / 3.0
    bins = np.digitize(frame["x"].to_numpy(dtype=float), x_edges, right=False) - 1
    bins = np.clip(bins, 0, len(x_edges) - 2)
    profile = np.zeros(len(x_edges) - 1, dtype=float)
    np.add.at(profile, bins, volumes)
    return profile


def weighted_centroid(x_centers: np.ndarray, weights: np.ndarray, length: float) -> float:
    """Return weighted x centroid normalized by bed length."""
    total = float(weights.sum())
    if total <= 0.0:
        return float("nan")
    return float(np.sum(x_centers * weights) / total / length)


def build_time_resolved_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build summary and x-resolved blockage profile tables."""
    config = load_yaml(BASE_CONFIG)
    baseline = load_json(BASELINE_TOPOLOGY)
    x_centers, pore_volumes, _, metadata = baseline_pore_volumes()
    domain = metadata["domain"]
    x_edges = np.linspace(float(domain["x_min"]), float(domain["x_max"]), N_BINS + 1)
    length = float(domain["Lx"])
    epsilon0 = float(baseline["porosity"])
    dp = float(config["dp"])
    mu = float(config["mu_g"])
    rho = float(config["rho_g"])
    u = 2.0
    dt = float(config["dt"])
    baseline_gradient = float(ergun_pressure_gradient(epsilon0, dp, mu, rho, u))

    btc = pd.read_csv(BTC_SOURCE)
    btc = btc[btc["debris_total_number"].astype(int) == 3000].copy()
    btc_lookup = {round(float(row["time"]), 8): float(row["BTC"]) for row in btc.to_dict(orient="records")}

    summary_rows: list[dict[str, Any]] = []
    profile_rows: list[dict[str, Any]] = []
    dumps = standard_type2_dumps()
    first_time = timestep_from_name(dumps[0]) * dt
    for dump in dumps:
        timestep = timestep_from_name(dump)
        time = timestep * dt
        elapsed = time - first_time
        frame = read_liggghts_dump(dump)
        debris = frame[frame["type"] == 2].copy()
        volume = debris_volume_profile(debris, x_edges)
        blockage = np.divide(volume, pore_volumes, out=np.zeros_like(volume), where=pore_volumes > 0)
        eps_profile = np.clip(epsilon0 * (1.0 - blockage), 1.0e-6, 0.999999)
        gradient_profile = ergun_pressure_gradient(eps_profile, dp, mu, rho, u)
        peak_index = int(np.argmax(blockage)) if len(blockage) else 0
        peak_blockage = float(blockage[peak_index]) if len(blockage) else 0.0
        x_values = debris["x"].to_numpy(dtype=float) if not debris.empty else np.array([], dtype=float)
        summary_rows.append(
            {
                "case_name": CASE_NAME,
                "timestep": timestep,
                "time": time,
                "elapsed_time": elapsed,
                "BTC": btc_lookup.get(round(time, 8), float("nan")),
                "particle_count": int(len(debris)),
                "x_mean_over_L": float(np.mean(x_values) / length) if len(x_values) else float("nan"),
                "x_q90_over_L": float(np.quantile(x_values, 0.90) / length) if len(x_values) else float("nan"),
                "x_q99_over_L": float(np.quantile(x_values, 0.99) / length) if len(x_values) else float("nan"),
                "blockage_centroid_over_L": weighted_centroid(x_centers, blockage, length),
                "peak_blockage_ratio": peak_blockage,
                "peak_blockage_x_m": float(x_centers[peak_index]),
                "peak_blockage_x_over_L": float(x_centers[peak_index] / length),
                "profile_mean_pressure_increase_ratio": max(0.0, float(gradient_profile.mean() - baseline_gradient) / baseline_gradient),
                "peak_local_pressure_increase_ratio": max(0.0, float(gradient_profile[peak_index] - baseline_gradient) / baseline_gradient),
            }
        )
        for x_center, b_value in zip(x_centers, blockage):
            profile_rows.append(
                {
                    "case_name": CASE_NAME,
                    "timestep": timestep,
                    "time": time,
                    "elapsed_time": elapsed,
                    "x_center_m": float(x_center),
                    "x_over_L": float(x_center / length),
                    "blockage_ratio": float(b_value),
                }
            )
    return pd.DataFrame(summary_rows), pd.DataFrame(profile_rows)


def save_time_resolved_figure(summary: pd.DataFrame, profile: pd.DataFrame) -> None:
    """Save the time-resolved deposition figure."""
    configure_matplotlib()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(7.2, 5.2), constrained_layout=True)
    grid = fig.add_gridspec(2, 2)
    axes = [fig.add_subplot(grid[i, j]) for i in range(2) for j in range(2)]

    axes[0].plot(summary["elapsed_time"], summary["BTC"], color="#2166ac", linewidth=1.2)
    axes[0].set_xlabel("elapsed time (s)")
    axes[0].set_ylabel("BTC")
    axes[0].grid(True, linewidth=0.35, alpha=0.35)
    axes[0].text(0.03, 0.95, "a", transform=axes[0].transAxes, va="top", ha="left", weight="bold")

    axes[1].plot(summary["elapsed_time"], summary["x_mean_over_L"], color="#4d4d4d", linewidth=1.1, label="mean")
    axes[1].plot(summary["elapsed_time"], summary["x_q99_over_L"], color="#b2182b", linewidth=1.1, label="q99")
    axes[1].set_xlabel("elapsed time (s)")
    axes[1].set_ylabel("debris position x/L")
    axes[1].set_ylim(0, 1.04)
    axes[1].grid(True, linewidth=0.35, alpha=0.35)
    axes[1].legend(loc="best")
    axes[1].text(0.03, 0.95, "b", transform=axes[1].transAxes, va="top", ha="left", weight="bold")

    pivot = profile.pivot_table(index="x_over_L", columns="elapsed_time", values="blockage_ratio", aggfunc="mean").sort_index()
    image = axes[2].imshow(
        pivot.to_numpy(),
        origin="lower",
        aspect="auto",
        extent=[summary["elapsed_time"].min(), summary["elapsed_time"].max(), pivot.index.min(), pivot.index.max()],
        cmap="magma",
    )
    axes[2].set_xlabel("elapsed time (s)")
    axes[2].set_ylabel("x/L")
    fig.colorbar(image, ax=axes[2], label="blockage ratio")
    axes[2].text(0.03, 0.95, "c", transform=axes[2].transAxes, va="top", ha="left", weight="bold", color="white")

    axes[3].scatter(
        summary["peak_blockage_ratio"],
        summary["peak_local_pressure_increase_ratio"],
        color="#4d4d4d",
        s=26,
        edgecolor="#222222",
        linewidth=0.25,
    )
    axes[3].set_xlabel("peak blockage ratio")
    axes[3].set_ylabel("peak pressure-increase ratio")
    axes[3].ticklabel_format(axis="x", style="sci", scilimits=(0, 0))
    axes[3].ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    axes[3].grid(True, linewidth=0.35, alpha=0.35)
    axes[3].text(0.03, 0.95, "d", transform=axes[3].transAxes, va="top", ha="left", weight="bold")

    for suffix, kwargs in {".png": {"dpi": 600}, ".pdf": {}, ".svg": {}}.items():
        fig.savefig(f"{OUT_FIG}{suffix}", bbox_inches="tight", **kwargs)
    plt.close(fig)


def write_stage_report(summary: pd.DataFrame) -> None:
    """Write a stage report for the time-resolved deposition analysis."""
    NOTE_DIR.mkdir(parents=True, exist_ok=True)
    peak = summary.loc[summary["peak_blockage_ratio"].idxmax()]
    lines = [
        "# Stage Report: Time-Resolved Deposition",
        "",
        "Date: 2026-06-09",
        "",
        "## Scope",
        "",
        "This stage analyzes the standard-window type-2 dump sequence for the representative df/dp = 0.0225, ug = 2.0 m/s, N = 3000 case.",
        "",
        "## Outputs",
        "",
        f"- `{OUT_SUMMARY.relative_to(PROJECT_ROOT)}`",
        f"- `{OUT_PROFILE.relative_to(PROJECT_ROOT)}`",
        f"- `{OUT_FIG.relative_to(PROJECT_ROOT)}.png`",
        f"- `{OUT_FIG.relative_to(PROJECT_ROOT)}.pdf`",
        f"- `{OUT_FIG.relative_to(PROJECT_ROOT)}.svg`",
        "",
        "## Key Results",
        "",
        f"- frames analyzed: {len(summary)}",
        f"- final BTC: {summary['BTC'].iloc[-1]:.6f}",
        f"- final x_mean/L: {summary['x_mean_over_L'].iloc[-1]:.6f}",
        f"- final x99/L: {summary['x_q99_over_L'].iloc[-1]:.6f}",
        f"- maximum peak blockage: {peak['peak_blockage_ratio']:.6e} at elapsed time {peak['elapsed_time']:.6f} s and x/L = {peak['peak_blockage_x_over_L']:.6f}",
        "",
        "## Interpretation",
        "",
        "The time-resolved data show downstream debris-front migration and late outlet arrival during the standard window, while local blockage remains a small sub-voxel perturbation.",
    ]
    OUT_NOTE.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    """Run the time-resolved deposition workflow."""
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    summary, profile = build_time_resolved_tables()
    summary.to_csv(OUT_SUMMARY, index=False)
    profile.to_csv(OUT_PROFILE, index=False)
    save_time_resolved_figure(summary, profile)
    write_stage_report(summary)
    print(f"Wrote: {OUT_SUMMARY}")
    print(f"Wrote: {OUT_PROFILE}")
    print(f"Wrote: {OUT_FIG}.png/.pdf/.svg")
    print(f"Wrote: {OUT_NOTE}")
    print(summary.tail().to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
