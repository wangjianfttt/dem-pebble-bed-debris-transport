#!/usr/bin/env python3
"""Plot spatial-distribution evidence for 908 sparse-front transport."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.postprocess.read_liggghts_dump import read_liggghts_dump  # noqa: E402


CASE_DIR = Path(
    "cases/clogging_scan/paper2_localized_release/"
    "paper2_local_damage_slab_x012_018_df0p1_n30000_seed908_explicit"
)
DEFAULT_PATTERN = (
    CASE_DIR
    / "paper2_local_damage_slab_x012_018_df0p1_n30000_seed908_explicit_dt5e9_type2_*.dump"
)
DEFAULT_FIGURE = Path(
    "papers/paper2_voxel_topology_clogging/figures/"
    "paper2_908_spatial_distribution_evidence"
)
DEFAULT_QUANTILES = Path(
    "papers/paper2_voxel_topology_clogging/tables/"
    "paper2_908_spatial_quantiles.csv"
)
DEFAULT_CDF = Path(
    "papers/paper2_voxel_topology_clogging/tables/"
    "paper2_908_spatial_cdf_curves.csv"
)
DEFAULT_JSON = Path(
    "papers/paper2_voxel_topology_clogging/data/"
    "paper2_908_spatial_distribution_evidence.json"
)
DEFAULT_NOTE = Path(
    "papers/paper2_voxel_topology_clogging/notes/"
    "paper2_908_spatial_distribution_evidence.md"
)


@dataclass(frozen=True)
class FrameData:
    """Container for one DEM dump frame."""

    step: int
    time_s: float
    x_over_l: np.ndarray


def parse_step(path: Path) -> int:
    """Extract the timestep from a 908 dump filename."""

    match = re.search(r"_(\d+)\.dump$", path.name)
    if not match:
        raise ValueError(f"Cannot parse timestep from dump filename: {path.name}")
    return int(match.group(1))


def load_frames(pattern: Path, dt: float, domain_lx: float, time_offset: float) -> list[FrameData]:
    """Load type-2 dump frames and return normalized axial positions."""

    files = sorted(Path().glob(str(pattern)))
    if not files:
        raise FileNotFoundError(f"No dump files matched pattern: {pattern}")
    frames: list[FrameData] = []
    for path in files:
        step = parse_step(path)
        try:
            df = read_liggghts_dump(path)
        except (OSError, ValueError) as exc:
            print(f"Skipping unreadable 908 dump {path}: {exc}", file=sys.stderr)
            continue
        if df.empty:
            print(f"Skipping empty 908 dump {path}", file=sys.stderr)
            continue
        if "type" in df.columns:
            type2 = df[df["type"].astype(int) == 2]
            if not type2.empty:
                df = type2
        x_over_l = (df["x"].to_numpy(dtype=float) / float(domain_lx)).clip(0.0, 1.2)
        frames.append(
            FrameData(
                step=step,
                time_s=step * float(dt) + float(time_offset),
                x_over_l=x_over_l,
            )
        )
    if not frames:
        raise ValueError(f"No readable 908 dump frames matched pattern: {pattern}")
    return sorted(frames, key=lambda frame: frame.step)


def quantile_table(frames: list[FrameData]) -> pd.DataFrame:
    """Compute axial-position quantiles and tail fractions for all frames."""

    rows: list[dict[str, Any]] = []
    for frame in frames:
        x = frame.x_over_l
        rows.append(
            {
                "step": frame.step,
                "time_s": frame.time_s,
                "n": int(x.size),
                "x_p50_over_L": float(np.quantile(x, 0.50)),
                "x_p90_over_L": float(np.quantile(x, 0.90)),
                "x_p99_over_L": float(np.quantile(x, 0.99)),
                "x_p999_over_L": float(np.quantile(x, 0.999)),
                "x_max_over_L": float(np.max(x)),
                "fraction_x_gt_0p40": float(np.mean(x > 0.40)),
                "fraction_x_gt_0p60": float(np.mean(x > 0.60)),
                "fraction_x_gt_0p80": float(np.mean(x > 0.80)),
                "fraction_x_gt_0p95": float(np.mean(x > 0.95)),
                "fraction_x_ge_1p00": float(np.mean(x >= 1.00)),
            }
        )
    return pd.DataFrame(rows)


def select_representative_frames(frames: list[FrameData], max_count: int = 5) -> list[FrameData]:
    """Select a small set of representative frames for CDF plotting."""

    if len(frames) <= max_count:
        return frames
    indices = np.linspace(0, len(frames) - 1, max_count).round().astype(int)
    return [frames[int(index)] for index in np.unique(indices)]


def cdf_table(frames: list[FrameData], grid_size: int = 501) -> pd.DataFrame:
    """Build CDF and survival curves on a common x/L grid."""

    grid = np.linspace(0.0, 1.0, grid_size)
    rows: list[pd.DataFrame] = []
    for frame in frames:
        x_sorted = np.sort(frame.x_over_l)
        cdf = np.searchsorted(x_sorted, grid, side="right") / x_sorted.size
        rows.append(
            pd.DataFrame(
                {
                    "step": frame.step,
                    "time_s": frame.time_s,
                    "x_over_L": grid,
                    "cdf": cdf,
                    "survival": 1.0 - cdf,
                }
            )
        )
    return pd.concat(rows, ignore_index=True)


def summarize_evidence(qdf: pd.DataFrame) -> dict[str, Any]:
    """Summarize final-frame spatial distribution evidence."""

    final = qdf.iloc[-1]
    return {
        "frame_count": int(len(qdf)),
        "first_step": int(qdf["step"].iloc[0]),
        "final_step": int(final["step"]),
        "final_time_s": float(final["time_s"]),
        "final_n": int(final["n"]),
        "final_x_p50_over_L": float(final["x_p50_over_L"]),
        "final_x_p90_over_L": float(final["x_p90_over_L"]),
        "final_x_p99_over_L": float(final["x_p99_over_L"]),
        "final_x_p999_over_L": float(final["x_p999_over_L"]),
        "final_x_max_over_L": float(final["x_max_over_L"]),
        "final_fraction_x_gt_0p60": float(final["fraction_x_gt_0p60"]),
        "final_fraction_x_gt_0p80": float(final["fraction_x_gt_0p80"]),
        "final_fraction_x_gt_0p95": float(final["fraction_x_gt_0p95"]),
        "final_fraction_x_ge_1p00": float(final["fraction_x_ge_1p00"]),
        "tail_fraction_95_to_100_over_L": float(
            final["fraction_x_gt_0p95"] - final["fraction_x_ge_1p00"]
        ),
        "claim_boundary": (
            "Spatial distribution evidence supports sparse-front transport "
            "and retained-bulk separation; outlet breakthrough requires "
            "fraction_x_ge_1p00 > 0."
        ),
    }


def plot_distribution(
    qdf: pd.DataFrame,
    cdf: pd.DataFrame,
    frames: list[FrameData],
    output_base: Path,
    source_region: tuple[float, float],
) -> None:
    """Create a publication-style multi-panel spatial distribution figure."""

    output_base.parent.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 8,
            "axes.linewidth": 0.7,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.major.width": 0.7,
            "ytick.major.width": 0.7,
            "legend.frameon": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.0), constrained_layout=True)
    ax_cdf, ax_surv, ax_quant, ax_hist = axes.ravel()

    selected_steps = sorted(cdf["step"].unique())
    cmap = plt.get_cmap("viridis")
    colors = {
        step: cmap(index / max(1, len(selected_steps) - 1))
        for index, step in enumerate(selected_steps)
    }

    for step, group in cdf.groupby("step"):
        label = f"{group['time_s'].iloc[0] * 1e3:.2f} ms"
        ax_cdf.plot(group["x_over_L"], group["cdf"], color=colors[step], lw=1.3, label=label)
        survival = group["survival"].clip(lower=1.0 / frames[0].x_over_l.size)
        ax_surv.plot(group["x_over_L"], survival, color=colors[step], lw=1.3)

    for ax in (ax_cdf, ax_surv, ax_hist):
        ax.axvspan(source_region[0], source_region[1], color="0.88", zorder=0)
        ax.set_xlim(0.0, 1.02)

    ax_cdf.set_xlabel(r"Axial position, $x/L$")
    ax_cdf.set_ylabel("Cumulative fraction")
    ax_cdf.legend(loc="lower right", ncols=1, fontsize=7)
    ax_cdf.text(0.02, 0.96, "a", transform=ax_cdf.transAxes, fontweight="bold", va="top")

    ax_surv.set_yscale("log")
    ax_surv.set_xlabel(r"Axial position, $x/L$")
    ax_surv.set_ylabel("Survival fraction")
    ax_surv.text(0.02, 0.96, "b", transform=ax_surv.transAxes, fontweight="bold", va="top")

    marker_map = {
        "x_p50_over_L": ("o", "P50"),
        "x_p90_over_L": ("s", "P90"),
        "x_p99_over_L": ("^", "P99"),
        "x_p999_over_L": ("D", "P99.9"),
        "x_max_over_L": ("x", "max"),
    }
    for column, (marker, label) in marker_map.items():
        ax_quant.plot(
            qdf["time_s"] * 1e3,
            qdf[column],
            marker=marker,
            ms=3.0,
            lw=0.8,
            label=label,
        )
    ax_quant.set_xlabel("Time (ms)")
    ax_quant.set_ylabel(r"Front position, $x/L$")
    ax_quant.set_xlim(0.0, max(qdf["time_s"] * 1e3) * 1.03)
    ax_quant.set_ylim(0.25, 1.03)
    ax_quant.legend(loc="upper left", ncols=2, fontsize=7)
    ax_quant.text(0.02, 0.96, "c", transform=ax_quant.transAxes, fontweight="bold", va="top")

    final_frame = frames[-1]
    bins = np.linspace(0.0, 1.0, 51)
    ax_hist.hist(
        final_frame.x_over_l.clip(0.0, 1.0),
        bins=bins,
        density=False,
        color="#4C78A8",
        edgecolor="white",
        linewidth=0.35,
        log=True,
    )
    ax_hist.set_xlabel(r"Axial position, $x/L$")
    ax_hist.set_ylabel("Particle count")
    ax_hist.set_ylim(0.8, None)
    ax_hist.text(0.02, 0.96, "d", transform=ax_hist.transAxes, fontweight="bold", va="top")

    for ext in ("png", "pdf", "svg"):
        fig.savefig(output_base.with_suffix(f".{ext}"), dpi=300)
    plt.close(fig)


def write_note(summary: dict[str, Any], note_path: Path) -> None:
    """Write a short Markdown note for manuscript traceability."""

    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(
        f"""# 908 Spatial Distribution Evidence

## Purpose

This evidence checks whether the near-outlet front is a bulk migration event or
a sparse-tail event. It uses the full type-2 particle distribution, not only the
maximum particle position.

## Final Frame

- Final step: `{summary['final_step']}`
- Final time: `{summary['final_time_s']:.6g} s`
- Particle count: `{summary['final_n']}`
- `P50(x/L)`: `{summary['final_x_p50_over_L']:.6f}`
- `P90(x/L)`: `{summary['final_x_p90_over_L']:.6f}`
- `P99(x/L)`: `{summary['final_x_p99_over_L']:.6f}`
- `P99.9(x/L)`: `{summary['final_x_p999_over_L']:.6f}`
- `max(x/L)`: `{summary['final_x_max_over_L']:.6f}`
- Fraction beyond `x/L = 0.80`: `{summary['final_fraction_x_gt_0p80']:.6f}`
- Fraction beyond `x/L = 0.95`: `{summary['final_fraction_x_gt_0p95']:.6f}`
- Fraction crossing outlet `x/L >= 1`: `{summary['final_fraction_x_ge_1p00']:.6f}`

## Interpretation

The final distribution supports sparse-front transport rather than bulk
breakthrough. The leading front reaches the outlet-side region, but P99 and
lower percentiles remain far upstream. A manuscript claim should therefore
focus on front/bulk decoupling and retained-bulk transport.

## Claim Boundary

{summary['claim_boundary']}
""",
        encoding="utf-8",
    )


def main() -> None:
    """Command-line entry point."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--pattern", type=Path, default=DEFAULT_PATTERN)
    parser.add_argument("--dt", type=float, default=5e-9)
    parser.add_argument("--time-offset", type=float, default=5e-5)
    parser.add_argument("--domain-lx", type=float, default=0.045)
    parser.add_argument("--source-start", type=float, default=0.012 / 0.045)
    parser.add_argument("--source-end", type=float, default=0.018 / 0.045)
    parser.add_argument("--figure", type=Path, default=DEFAULT_FIGURE)
    parser.add_argument("--quantiles", type=Path, default=DEFAULT_QUANTILES)
    parser.add_argument("--cdf", type=Path, default=DEFAULT_CDF)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--note", type=Path, default=DEFAULT_NOTE)
    args = parser.parse_args()

    frames = load_frames(args.pattern, args.dt, args.domain_lx, args.time_offset)
    qdf = quantile_table(frames)
    selected = select_representative_frames(frames)
    cdf = cdf_table(selected)
    summary = summarize_evidence(qdf)

    args.quantiles.parent.mkdir(parents=True, exist_ok=True)
    args.cdf.parent.mkdir(parents=True, exist_ok=True)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    qdf.to_csv(args.quantiles, index=False)
    cdf.to_csv(args.cdf, index=False)
    args.json.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_note(summary, args.note)
    plot_distribution(qdf, cdf, frames, args.figure, (args.source_start, args.source_end))

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
