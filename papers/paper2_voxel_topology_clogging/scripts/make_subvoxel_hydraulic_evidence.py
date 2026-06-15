#!/usr/bin/env python3
"""Assemble sub-voxel hydraulic evidence for Paper 2.

This workflow treats fine debris as a sub-voxel pore-volume reduction rather
than as explicit STL geometry. It combines DEM-derived blockage profiles,
Ergun pressure proxies and returned OpenFOAM screening results into one
auditable evidence table.
"""

from __future__ import annotations

import argparse
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

DEFAULT_PRESSURE_PROXY = TABLE_DIR / "paper2_pressure_proxy_source.csv"
DEFAULT_OPENFOAM = TABLE_DIR / "paper2_openfoam_handoff_results_summary.csv"
OUT_TABLE = TABLE_DIR / "paper2_subvoxel_hydraulic_evidence_source.csv"
OUT_JSON = DATA_DIR / "paper2_subvoxel_hydraulic_evidence_summary.json"
OUT_NOTE = NOTE_DIR / "subvoxel_hydraulic_evidence_note.md"
OUT_FIG = FIG_DIR / "paper2_figS18_subvoxel_hydraulic_evidence"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pressure-proxy", type=Path, default=DEFAULT_PRESSURE_PROXY, help="Ergun pressure-proxy CSV.")
    parser.add_argument("--openfoam", type=Path, default=DEFAULT_OPENFOAM, help="Parsed OpenFOAM result CSV.")
    return parser.parse_args()


def configure_matplotlib() -> None:
    """Configure compact journal-style matplotlib defaults."""
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


def load_optional_csv(path: Path) -> pd.DataFrame:
    """Load a CSV if it exists; otherwise return an empty frame."""
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame()
    return pd.read_csv(path)


def parse_bool(value: object) -> bool:
    """Parse bool-like CSV values conservatively."""
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def openfoam_by_debris(openfoam: pd.DataFrame) -> dict[int, dict[str, object]]:
    """Map returned OpenFOAM records to debris counts inferred from case names."""
    if openfoam.empty or "case_name" not in openfoam.columns:
        return {}
    mapped: dict[int, dict[str, object]] = {}
    for row in openfoam.to_dict(orient="records"):
        case_name = str(row.get("case_name", ""))
        for value in (3000, 6000, 10000):
            if f"N{value}" in case_name:
                mapped[value] = row
                break
    return mapped


def build_evidence_table(pressure_proxy: pd.DataFrame, openfoam: pd.DataFrame) -> pd.DataFrame:
    """Build the sub-voxel hydraulic evidence table."""
    required = {
        "debris_total_number",
        "subvoxel_max_blockage_ratio",
        "subvoxel_mean_blockage_ratio",
        "profile_pressure_increase_ratio",
        "peak_local_pressure_increase_ratio",
        "baseline_pressure_drop_pa",
        "profile_mean_pressure_drop_pa",
        "peak_local_equivalent_pressure_drop_pa",
    }
    missing = sorted(required.difference(pressure_proxy.columns))
    if missing:
        raise ValueError(f"pressure proxy table missing columns: {missing}")
    of_map = openfoam_by_debris(openfoam)
    rows: list[dict[str, object]] = []
    for item in pressure_proxy.sort_values("debris_total_number").to_dict(orient="records"):
        n_debris = int(item["debris_total_number"])
        of = of_map.get(n_debris, {})
        max_b = float(item["subvoxel_max_blockage_ratio"])
        peak_ratio = float(item["peak_local_pressure_increase_ratio"])
        rows.append(
            {
                "debris_total_number": n_debris,
                "subvoxel_mean_blockage_ratio": float(item["subvoxel_mean_blockage_ratio"]),
                "subvoxel_max_blockage_ratio": max_b,
                "ergun_profile_pressure_increase_ratio": float(item["profile_pressure_increase_ratio"]),
                "ergun_peak_local_pressure_increase_ratio": peak_ratio,
                "ergun_baseline_pressure_drop_pa": float(item["baseline_pressure_drop_pa"]),
                "ergun_profile_mean_pressure_drop_pa": float(item["profile_mean_pressure_drop_pa"]),
                "ergun_peak_local_equivalent_pressure_drop_pa": float(item["peak_local_equivalent_pressure_drop_pa"]),
                "openfoam_delta_p_pa": float(of["delta_p_inlet_minus_outlet"]) if "delta_p_inlet_minus_outlet" in of and pd.notna(of["delta_p_inlet_minus_outlet"]) else np.nan,
                "openfoam_default_checkmesh_ok": parse_bool(of.get("checkMesh_ok", False)) if of else False,
                "openfoam_skew6_checkmesh_ok": parse_bool(of.get("checkMesh_skew6_ok", False)) if of else False,
                "openfoam_max_skewness": float(of["max_skewness"]) if "max_skewness" in of and pd.notna(of["max_skewness"]) else np.nan,
                "hydraulic_regime": classify_hydraulic_regime(max_b=max_b, peak_pressure_ratio=peak_ratio),
                "evidence_boundary": "sub-voxel Ergun proxy plus returned OpenFOAM screening metadata; not experimental pressure validation",
            }
        )
    return pd.DataFrame(rows)


def classify_hydraulic_regime(max_b: float, peak_pressure_ratio: float) -> str:
    """Classify the hydraulic consequence of the current DEM debris loading."""
    if max_b < 1.0e-4 and peak_pressure_ratio < 1.0e-3:
        return "pre-clogging perturbation"
    if max_b < 1.0e-2 and peak_pressure_ratio < 1.0e-1:
        return "incipient hydraulic perturbation"
    return "strong hydraulic obstruction"


def summarize(table: pd.DataFrame) -> dict[str, object]:
    """Create a JSON-friendly summary."""
    return {
        "rows": int(len(table)),
        "debris_total_numbers": [int(value) for value in table["debris_total_number"]],
        "max_subvoxel_blockage_ratio": float(table["subvoxel_max_blockage_ratio"].max()),
        "max_ergun_peak_local_pressure_increase_ratio": float(table["ergun_peak_local_pressure_increase_ratio"].max()),
        "openfoam_screening_cases": int(table["openfoam_delta_p_pa"].notna().sum()),
        "openfoam_strict_checkmesh_cases": int(table["openfoam_default_checkmesh_ok"].sum()),
        "openfoam_engineering_skew6_cases": int(table["openfoam_skew6_checkmesh_ok"].sum()),
        "dominant_interpretation": (
            "current loading cases remain in a pre-clogging hydraulic perturbation regime; stronger local release or higher retained debris loading is needed for critical blockage evidence"
            if (table["hydraulic_regime"] == "pre-clogging perturbation").all()
            else "some loading cases show hydraulic obstruction beyond the pre-clogging perturbation regime"
        ),
        "evidence_boundary": "The table combines a sub-voxel Ergun proxy and returned OpenFOAM screening metadata. It is not experimental pressure validation.",
    }


def plot_evidence(table: pd.DataFrame) -> list[str]:
    """Save a two-panel journal-style hydraulic evidence figure."""
    configure_matplotlib()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), constrained_layout=True)
    x = table["debris_total_number"].to_numpy(dtype=float)

    axes[0].scatter(
        x,
        table["subvoxel_max_blockage_ratio"],
        s=44,
        marker="o",
        color="#2166ac",
        edgecolor="#222222",
        linewidth=0.5,
        label="max",
    )
    axes[0].scatter(
        x,
        table["subvoxel_mean_blockage_ratio"],
        s=42,
        marker="s",
        facecolor="white",
        edgecolor="#2166ac",
        linewidth=1.0,
        label="mean",
    )
    axes[0].set_yscale("log")
    axes[0].set_xlabel("injected debris count")
    axes[0].set_ylabel("sub-voxel blockage ratio")
    axes[0].grid(True, axis="y", linewidth=0.35, alpha=0.35)
    axes[0].legend(loc="best")
    axes[0].text(0.02, 0.95, "a", transform=axes[0].transAxes, va="top", ha="left", weight="bold")

    axes[1].scatter(
        x,
        table["ergun_profile_pressure_increase_ratio"],
        s=44,
        marker="o",
        color="#4d4d4d",
        edgecolor="#222222",
        linewidth=0.5,
        label="profile mean",
    )
    axes[1].scatter(
        x,
        table["ergun_peak_local_pressure_increase_ratio"],
        s=42,
        marker="D",
        facecolor="white",
        edgecolor="#b2182b",
        linewidth=1.0,
        label="peak local",
    )
    axes[1].set_yscale("log")
    axes[1].set_xlabel("injected debris count")
    axes[1].set_ylabel("Ergun pressure-increase ratio")
    axes[1].grid(True, axis="y", linewidth=0.35, alpha=0.35)
    axes[1].legend(loc="best")
    axes[1].text(0.02, 0.95, "b", transform=axes[1].transAxes, va="top", ha="left", weight="bold")

    outputs = []
    for suffix, kwargs in {".png": {"dpi": 600}, ".pdf": {}, ".svg": {}}.items():
        path = OUT_FIG.with_suffix(suffix)
        fig.savefig(path, bbox_inches="tight", **kwargs)
        outputs.append(str(path.relative_to(PROJECT_ROOT)))
    plt.close(fig)
    return outputs


def write_note(table: pd.DataFrame, summary: dict[str, object], figures: list[str]) -> None:
    """Write a concise note describing interpretation and limits."""
    NOTE_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Sub-voxel hydraulic evidence",
        "",
        "This note consolidates DEM-derived sub-voxel blockage, Ergun pressure proxies and returned OpenFOAM screening metadata.",
        "",
        "## Main interpretation",
        "",
        f"- Maximum sub-voxel blockage ratio: {summary['max_subvoxel_blockage_ratio']:.6e}",
        f"- Maximum Ergun peak-local pressure-increase ratio: {summary['max_ergun_peak_local_pressure_increase_ratio']:.6e}",
        f"- OpenFOAM screening cases imported: {summary['openfoam_screening_cases']}",
        f"- OpenFOAM strict default checkMesh cases: {summary['openfoam_strict_checkmesh_cases']}",
        f"- OpenFOAM engineering skewThreshold=6 cases: {summary['openfoam_engineering_skew6_cases']}",
        "",
        "Current loading cases are best interpreted as a pre-clogging hydraulic perturbation regime. They support transport and retention analysis, but they do not yet support a sharp critical-blockage pressure-transition claim.",
        "",
        "## Outputs",
        "",
        f"- `{OUT_TABLE.relative_to(PROJECT_ROOT)}`",
        f"- `{OUT_JSON.relative_to(PROJECT_ROOT)}`",
    ]
    lines.extend(f"- `{figure}`" for figure in figures)
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "The hydraulic proxy is based on sub-voxel effective porosity and Ergun scaling. The OpenFOAM result is a screening calculation for the bed-skeleton pore geometry and currently has engineering, not strict default, checkMesh acceptance.",
        ]
    )
    OUT_NOTE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    """Run the sub-voxel hydraulic evidence workflow."""
    args = parse_args()
    pressure_proxy = load_optional_csv(args.pressure_proxy)
    openfoam = load_optional_csv(args.openfoam)
    table = build_evidence_table(pressure_proxy, openfoam)
    OUT_TABLE.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUT_TABLE, index=False)
    status = summarize(table)
    figures = plot_evidence(table)
    status["figure_outputs"] = figures
    OUT_JSON.write_text(json.dumps(status, indent=2), encoding="utf-8")
    write_note(table, status, figures)
    print(json.dumps(status, indent=2))
    print(OUT_TABLE)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
