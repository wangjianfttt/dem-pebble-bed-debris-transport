#!/usr/bin/env python3
"""Analyze early explicit-localized debris-release segment outputs."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from src.postprocess.read_liggghts_dump import read_liggghts_dump  # noqa: E402


PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
CASE_DIR = (
    PROJECT_ROOT
    / "cases"
    / "clogging_scan"
    / "paper2_localized_release"
    / "paper2_local_damage_slab_x012_018_df0p1_n15000_seed906_explicit"
)
TABLE_DIR = PAPER_DIR / "tables"
FIG_DIR = PAPER_DIR / "figures"
DATA_DIR = PAPER_DIR / "data"

OUT_TABLE = TABLE_DIR / "explicit_localized_release_early_timeseries.csv"
OUT_JSON = DATA_DIR / "explicit_localized_release_1M_metrics.json"
OUT_FIG = FIG_DIR / "paper2_figS6_explicit_localized_release_early_segment"

BED_LENGTH = 0.045
SOURCE_X_MIN = 0.012
SOURCE_X_MAX = 0.018
DT = 1.0e-8


def configure_matplotlib() -> None:
    """Configure compact publication-style Matplotlib defaults."""
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


def available_type2_dumps(case_dir: Path = CASE_DIR) -> dict[int, Path]:
    """Return available type-2 dumps keyed by timestep."""
    patterns = [
        "explicit_10k_type2_*.dump",
        "explicit_seg50k_type2_*.dump",
        "explicit_seg250k_type2_*.dump",
        "explicit_seg500k_type2_*.dump",
        "explicit_seg1M_type2_*.dump",
    ]
    dumps: dict[int, Path] = {}
    for pattern in patterns:
        for path in case_dir.glob(pattern):
            match = re.search(r"_(\d+)\.dump$", path.name)
            if match:
                dumps[int(match.group(1))] = path
    if not dumps:
        raise FileNotFoundError(f"No explicit localized type-2 dumps found in {case_dir}")
    return dict(sorted(dumps.items()))


def parse_segment_log(path: Path) -> dict[str, Any]:
    """Extract basic stability metrics from one LIGGGHTS log file."""
    if not path.exists():
        return {}
    text = path.read_text(errors="ignore")
    rows = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[0].isdigit():
            try:
                rows.append((int(parts[0]), int(parts[1]), float(parts[2])))
            except ValueError:
                continue
    dangerous = re.findall(r"Dangerous builds = (\d+)", text)
    return {
        "thermo_rows": rows,
        "dangerous_builds": int(dangerous[-1]) if dangerous else None,
    }


def build_timeseries() -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build early-time migration timeseries and summary metrics."""
    dumps = available_type2_dumps()
    rows = []
    base = None
    for step, path in dumps.items():
        frame = read_liggghts_dump(path)
        if base is None:
            base = frame[["id", "x", "y", "z"]].rename(columns={"x": "x0", "y": "y0", "z": "z0"})
        merged = base.merge(frame[["id", "x", "y", "z", "vx", "vy", "vz"]], on="id")
        dx = merged["x"] - merged["x0"]
        rows.append(
            {
                "step": step,
                "time_s": step * DT,
                "debris_count": int(len(frame)),
                "btc_approx_x_ge_L": int((frame["x"] >= BED_LENGTH).sum()),
                "retained_in_source_slab_count": int(((frame["x"] >= SOURCE_X_MIN) & (frame["x"] <= SOURCE_X_MAX)).sum()),
                "downstream_of_source_count": int((frame["x"] > SOURCE_X_MAX).sum()),
                "upstream_of_source_count": int((frame["x"] < SOURCE_X_MIN).sum()),
                "x_mean_over_L": float(frame["x"].mean() / BED_LENGTH),
                "x_q50_over_L": float(frame["x"].quantile(0.50) / BED_LENGTH),
                "x_q90_over_L": float(frame["x"].quantile(0.90) / BED_LENGTH),
                "x_q99_over_L": float(frame["x"].quantile(0.99) / BED_LENGTH),
                "x_max_over_L": float(frame["x"].max() / BED_LENGTH),
                "dx_mean_m": float(dx.mean()),
                "dx_q90_m": float(dx.quantile(0.90)),
                "dx_q99_m": float(dx.quantile(0.99)),
                "dx_min_m": float(dx.min()),
                "dx_max_m": float(dx.max()),
                "vx_mean_m_s": float(frame["vx"].mean()),
                "vx_q95_m_s": float(frame["vx"].quantile(0.95)),
                "vx_max_m_s": float(frame["vx"].max()),
            }
        )
    table = pd.DataFrame(rows).sort_values("step")
    final = table.iloc[-1].to_dict()
    logs = {
        "short_10k": parse_segment_log(CASE_DIR / "explicit_10k.log"),
        "segment_50k": parse_segment_log(CASE_DIR / "explicit_segment_10k_to_50k.log"),
        "segment_250k": parse_segment_log(CASE_DIR / "explicit_segment_50k_to_250k.log"),
        "segment_500k": parse_segment_log(CASE_DIR / "explicit_segment_250k_to_500k.log"),
        "segment_1M": parse_segment_log(CASE_DIR / "explicit_segment_500k_to_1M.log"),
    }
    summary = {
        "case_name": CASE_DIR.name,
        "final_step": int(final["step"]),
        "final_time_s": float(final["time_s"]),
        "final_debris_count": int(final["debris_count"]),
        "final_btc_approx_x_ge_L": int(final["btc_approx_x_ge_L"]),
        "final_retained_in_source_slab_count": int(final["retained_in_source_slab_count"]),
        "final_downstream_of_source_count": int(final["downstream_of_source_count"]),
        "final_upstream_of_source_count": int(final["upstream_of_source_count"]),
        "final_x_mean_over_L": float(final["x_mean_over_L"]),
        "final_x_q90_over_L": float(final["x_q90_over_L"]),
        "final_x_q99_over_L": float(final["x_q99_over_L"]),
        "final_x_max_over_L": float(final["x_max_over_L"]),
        "final_dx_mean_m": float(final["dx_mean_m"]),
        "final_dx_q99_m": float(final["dx_q99_m"]),
        "final_dx_max_m": float(final["dx_max_m"]),
        "dangerous_builds": {
            key: value.get("dangerous_builds")
            for key, value in logs.items()
        },
        "interpretation": "At 1.0e-2 s the explicit localized release remains mostly retained in the source slab, with no outlet breakthrough and a slowly growing downstream tail.",
    }
    return table, summary


def save_figure(table: pd.DataFrame) -> None:
    """Save a compact early-segment figure."""
    configure_matplotlib()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.35), constrained_layout=True)
    time_ms = table["time_s"] * 1000.0

    axes[0].plot(time_ms, table["x_mean_over_L"], color="#2f5d8c", lw=1.25, marker="o", ms=3, label="mean")
    axes[0].plot(time_ms, table["x_q90_over_L"], color="#7a5195", lw=1.25, marker="s", ms=3, label="q90")
    axes[0].plot(time_ms, table["x_q99_over_L"], color="#ef5675", lw=1.25, marker="^", ms=3, label="q99")
    axes[0].axhspan(SOURCE_X_MIN / BED_LENGTH, SOURCE_X_MAX / BED_LENGTH, color="0.9", zorder=-1)
    axes[0].set_xlabel("time (ms)")
    axes[0].set_ylabel("axial position, x/L")
    axes[0].legend(loc="upper left")

    axes[1].plot(time_ms, table["retained_in_source_slab_count"], color="#00876c", lw=1.25, marker="o", ms=3, label="source")
    axes[1].plot(time_ms, table["downstream_of_source_count"], color="#d95f02", lw=1.25, marker="s", ms=3, label="downstream")
    axes[1].plot(time_ms, table["btc_approx_x_ge_L"], color="0.2", lw=1.25, marker="^", ms=3, label="outlet")
    axes[1].set_xlabel("time (ms)")
    axes[1].set_ylabel("particle count")
    axes[1].legend(loc="center left")

    final_step = int(table["step"].iloc[-1])
    final_dump = read_liggghts_dump(available_type2_dumps()[final_step])
    bins = np.linspace(0.0, BED_LENGTH, 21)
    axes[2].hist(final_dump["x"] / BED_LENGTH, bins=bins / BED_LENGTH, color="#4c78a8", alpha=0.85)
    axes[2].axvspan(SOURCE_X_MIN / BED_LENGTH, SOURCE_X_MAX / BED_LENGTH, color="0.85", zorder=-1)
    axes[2].set_xlabel(f"x/L at {final_step // 1000}k")
    axes[2].set_ylabel("count")

    for label, ax in zip(("a", "b", "c"), axes):
        ax.text(0.02, 0.96, label, transform=ax.transAxes, ha="left", va="top", fontweight="bold")

    for suffix in ("png", "pdf", "svg"):
        fig.savefig(f"{OUT_FIG}.{suffix}", dpi=300)
    plt.close(fig)


def main() -> int:
    """Run analysis and save reproducible outputs."""
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    table, summary = build_timeseries()
    table.to_csv(OUT_TABLE, index=False)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    save_figure(table)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
