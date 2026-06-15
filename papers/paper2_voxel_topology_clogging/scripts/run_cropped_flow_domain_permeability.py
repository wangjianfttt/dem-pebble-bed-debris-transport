#!/usr/bin/env python3
"""Run local voxel-network conductance checks on cropped pore domains."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.voxel.io import load_voxel_npz  # noqa: E402
from src.voxel.permeability import conductance_from_resistance_multiplier, pressure_profile, solve_voxel_pressure  # noqa: E402


PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
DEFAULT_CROP_MANIFEST = PAPER_DIR / "tables/paper2_cropped_flow_domain_manifest.csv"
DEFAULT_BLOCKAGE = PAPER_DIR / "tables/paper2_fig4_loading_blockage_source.csv"
DEFAULT_WHOLE_DOMAIN = PAPER_DIR / "tables/paper2_voxel_pressure_pilot_source.csv"
OUT_TABLE = PAPER_DIR / "tables/paper2_cropped_flow_permeability_source.csv"
OUT_PROFILE = PAPER_DIR / "tables/paper2_cropped_flow_pressure_profiles.csv"
OUT_JSON = PAPER_DIR / "data/paper2_cropped_flow_permeability_summary.json"
OUT_FIG = PAPER_DIR / "figures/paper2_figS14_cropped_flow_permeability"
OUT_REPORT = PAPER_DIR / "notes/stage_report_cropped_flow_permeability_2026-06-09.md"


def configure_matplotlib() -> None:
    """Configure compact journal-style plotting."""
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


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crop-manifest", type=Path, default=DEFAULT_CROP_MANIFEST, help="Cropped flow-domain manifest.")
    parser.add_argument("--blockage", type=Path, default=DEFAULT_BLOCKAGE, help="Axial blockage profile CSV.")
    parser.add_argument("--whole-domain", type=Path, default=DEFAULT_WHOLE_DOMAIN, help="Whole-domain pressure pilot CSV.")
    parser.add_argument("--exponent", type=float, default=3.0, help="Conductance exponent applied to (1 - blockage).")
    return parser.parse_args()


def local_conductance_scale(
    shape: tuple[int, int, int],
    crop_x_min: float,
    voxel_size: float,
    blockage_profile: pd.DataFrame,
    exponent: float,
) -> np.ndarray:
    """Map a global axial blockage profile to a cropped 3D conductance scale."""
    if exponent <= 0.0:
        raise ValueError("exponent must be positive.")
    required = {"x_center", "blockage_ratio"}
    missing = sorted(required.difference(blockage_profile.columns))
    if missing:
        raise ValueError(f"blockage_profile missing columns: {missing}")
    x_centers = crop_x_min + (np.arange(shape[0], dtype=float) + 0.5) * voxel_size
    profile = blockage_profile.sort_values("x_center")
    blockage = np.interp(
        x_centers,
        profile["x_center"].to_numpy(dtype=float),
        profile["blockage_ratio"].to_numpy(dtype=float),
        left=float(profile["blockage_ratio"].iloc[0]),
        right=float(profile["blockage_ratio"].iloc[-1]),
    )
    scale = np.clip((1.0 - blockage) ** exponent, 1.0e-9, 1.0)
    return np.broadcast_to(scale[:, None, None], shape).copy()


def load_hydraulic_conductance(crop_row: pd.Series, void: np.ndarray) -> tuple[np.ndarray | None, dict[str, object]]:
    """Load the 3D hydraulic-resistance field for a cropped flow domain.

    Returns a conductance field and metadata describing whether the field was
    available. If the field is absent, the caller can fall back to the older
    axial-profile proxy.
    """
    direct_path = crop_row.get("hydraulic_resistance_multiplier_field_npy", "")
    if not pd.isna(direct_path) and str(direct_path).strip() != "":
        field_path = PROJECT_ROOT / str(direct_path)
    else:
        source_domain = crop_row.get("source_domain", "")
        if pd.isna(source_domain) or str(source_domain).strip() == "":
            return None, {"hydraulic_resistance_field_used": False, "hydraulic_resistance_field": ""}
        field_path = PROJECT_ROOT / str(source_domain) / "hydraulic_resistance_multiplier_field.npy"
    if not field_path.exists():
        return None, {"hydraulic_resistance_field_used": False, "hydraulic_resistance_field": str(field_path)}
    resistance = np.load(field_path)
    if resistance.shape != void.shape:
        raise ValueError(
            f"hydraulic resistance field shape {resistance.shape} does not match voxel shape {void.shape} for {crop_row.get('case_name', crop_row.get('case_label', 'case'))}."
        )
    conductance = conductance_from_resistance_multiplier(resistance, void_mask=void)
    pore_resistance = resistance[void]
    try:
        field_label = str(field_path.relative_to(PROJECT_ROOT))
    except ValueError:
        field_label = str(field_path)
    return conductance, {
        "hydraulic_resistance_field_used": True,
        "hydraulic_resistance_field": field_label,
        "mean_resistance_multiplier": float(np.mean(pore_resistance)),
        "max_resistance_multiplier": float(np.max(pore_resistance)),
        "min_hydraulic_conductance": float(np.min(conductance[void])),
        "mean_hydraulic_conductance": float(np.mean(conductance[void])),
    }


def run_cropped_permeability(
    crop_manifest: Path,
    blockage_path: Path,
    whole_domain_path: Path,
    exponent: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Run baseline and blockage-scaled conductance solves for each cropped domain."""
    manifest = pd.read_csv(crop_manifest)
    blockage = pd.read_csv(blockage_path)
    whole = pd.read_csv(whole_domain_path) if whole_domain_path.exists() else pd.DataFrame()

    rows = []
    profiles = []
    for _, crop_row in manifest.iterrows():
        n_debris = int(crop_row["debris_total_number"])
        voxel, metadata = load_voxel_npz(PROJECT_ROOT / str(crop_row["voxel_npz"]))
        void = voxel == 0
        baseline = solve_voxel_pressure(void, axis="x")
        if baseline.status != "solved":
            raise RuntimeError(f"Baseline local solve failed for N={n_debris}: {baseline.status}")
        group = blockage[blockage["debris_total_number"].astype(int) == n_debris]
        scale, hydraulic_meta = load_hydraulic_conductance(crop_row, void)
        if scale is None:
            scale = local_conductance_scale(
                void.shape,
                crop_x_min=float(crop_row["x_applied_lower_m"]),
                voxel_size=float(metadata["voxel_size"]),
                blockage_profile=group,
                exponent=exponent,
            )
            hydraulic_meta = {
                **hydraulic_meta,
                "mean_resistance_multiplier": np.nan,
                "max_resistance_multiplier": np.nan,
                "min_hydraulic_conductance": float(scale.min()),
                "mean_hydraulic_conductance": float(scale.mean()),
            }
        loaded = solve_voxel_pressure(void, axis="x", conductance=scale)
        rel_g = loaded.conductance / baseline.conductance if baseline.conductance > 0.0 else np.nan
        whole_match = whole[whole.get("debris_total_number", pd.Series(dtype=int)).astype(int) == n_debris] if not whole.empty else pd.DataFrame()
        whole_loss = float(whole_match["conductance_loss"].iloc[0]) if not whole_match.empty else np.nan
        local_loss = float(1.0 - rel_g)
        rows.append(
            {
                "case_label": f"N={n_debris}",
                "debris_total_number": n_debris,
                "pressure_model": "cropped voxel-network Darcy-Laplace",
                "conductance_exponent": exponent,
                "crop_x_min_m": float(crop_row["x_applied_lower_m"]),
                "crop_x_max_m": float(crop_row["x_applied_upper_m"]),
                "shape_x": int(voxel.shape[0]),
                "shape_y": int(voxel.shape[1]),
                "shape_z": int(voxel.shape[2]),
                "baseline_conductance": float(baseline.conductance),
                "loaded_conductance": float(loaded.conductance),
                "relative_conductance": float(rel_g),
                "relative_resistance": float(1.0 / rel_g) if rel_g > 0.0 else np.inf,
                "local_conductance_loss": local_loss,
                "whole_domain_conductance_loss": whole_loss,
                "local_to_whole_loss_ratio": float(local_loss / whole_loss) if whole_loss > 0.0 else np.nan,
                "max_blockage_ratio_in_profile": float(group["blockage_ratio"].max()),
                "mean_scale_in_crop": float(scale.mean()),
                "min_scale_in_crop": float(scale.min()),
                "hydraulic_resistance_field_used": bool(hydraulic_meta["hydraulic_resistance_field_used"]),
                "hydraulic_resistance_field": hydraulic_meta["hydraulic_resistance_field"],
                "mean_resistance_multiplier": hydraulic_meta["mean_resistance_multiplier"],
                "max_resistance_multiplier": hydraulic_meta["max_resistance_multiplier"],
                "min_hydraulic_conductance": hydraulic_meta["min_hydraulic_conductance"],
                "mean_hydraulic_conductance": hydraulic_meta["mean_hydraulic_conductance"],
                "not_cfd": True,
                "not_lbm": True,
                "evidence_boundary": "cropped voxel-network conductance check consuming the 3D hydraulic-resistance field when available; not CFD/LBM and not a calibrated pressure-drop measurement",
            }
        )
        for label, result in (("baseline", baseline), ("loaded", loaded)):
            profile = pressure_profile(result, axis="x")
            profiles.append(
                pd.DataFrame(
                    {
                        "case_label": f"N={n_debris}",
                        "debris_total_number": n_debris,
                        "state": label,
                        "x_index": np.arange(len(profile), dtype=int),
                        "x_over_crop_L": (np.arange(len(profile), dtype=float) + 0.5) / len(profile),
                        "mean_pressure": profile,
                    }
                )
            )
    table = pd.DataFrame(rows)
    profile_table = pd.concat(profiles, ignore_index=True)
    OUT_TABLE.parent.mkdir(parents=True, exist_ok=True)
    OUT_TABLE.write_text(table.to_csv(index=False), encoding="utf-8")
    OUT_PROFILE.write_text(profile_table.to_csv(index=False), encoding="utf-8")
    summary = {
        "crop_manifest": str(crop_manifest.relative_to(PROJECT_ROOT)),
        "blockage_profile": str(blockage_path.relative_to(PROJECT_ROOT)),
        "conductance_exponent": exponent,
        "cases": table.to_dict(orient="records"),
        "evidence_boundary": "Cropped voxel-network conductance check only; no CFD/LBM solver was run.",
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    save_figure(table, profile_table)
    write_stage_report(table)
    return table, profile_table


def save_figure(table: pd.DataFrame, profile_table: pd.DataFrame) -> None:
    """Save cropped-domain permeability figure."""
    configure_matplotlib()
    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), constrained_layout=True)

    x = np.arange(len(table))
    width = 0.34
    axes[0].bar(x - width / 2.0, table["whole_domain_conductance_loss"], width=width, color="#9e9e9e", label="whole bed")
    axes[0].bar(x + width / 2.0, table["local_conductance_loss"], width=width, color="#2166ac", label="cropped domain")
    axes[0].set_yscale("log")
    axes[0].set_xticks(x, [str(int(value)) for value in table["debris_total_number"]])
    axes[0].set_xlabel("injected debris count")
    axes[0].set_ylabel("conductance loss")
    axes[0].grid(True, axis="y", linewidth=0.35, alpha=0.35)
    axes[0].legend(loc="upper left")
    axes[0].text(0.02, 0.95, "a", transform=axes[0].transAxes, va="top", ha="left", weight="bold")

    loaded_profiles = profile_table[profile_table["state"] == "loaded"]
    for n_debris, group in loaded_profiles.groupby("debris_total_number"):
        axes[1].plot(group["x_over_crop_L"], group["mean_pressure"], linewidth=1.2, label=f"N={int(n_debris)}")
    baseline = profile_table[(profile_table["state"] == "baseline") & (profile_table["debris_total_number"] == int(table["debris_total_number"].iloc[0]))]
    axes[1].plot(baseline["x_over_crop_L"], baseline["mean_pressure"], color="#4d4d4d", linewidth=1.0, linestyle="--", label="baseline")
    axes[1].set_xlabel("local x/L")
    axes[1].set_ylabel("mean pressure")
    axes[1].grid(True, linewidth=0.35, alpha=0.35)
    axes[1].legend(loc="best")
    axes[1].text(0.02, 0.95, "b", transform=axes[1].transAxes, va="top", ha="left", weight="bold")

    for suffix, kwargs in {".png": {"dpi": 600}, ".pdf": {}, ".svg": {}}.items():
        fig.savefig(f"{OUT_FIG}{suffix}", bbox_inches="tight", **kwargs)
    plt.close(fig)


def write_stage_report(table: pd.DataFrame) -> None:
    """Write a concise stage report for cropped-domain conductance checks."""
    lines = [
        "# Stage report: cropped flow-domain conductance check",
        "",
        "Date: 2026-06-09",
        "",
        "## Scope",
        "",
        "This stage solves a scalar Darcy-Laplace network problem on cropped pore domains centred on the peak blockage zone. The preferred input is the three-dimensional hydraulic-resistance multiplier field generated from debris blockage. It is a local voxel-network sensitivity check, not CFD, not LBM and not measured pressure.",
        "",
        "## Files Added or Updated",
        "",
        f"- `{OUT_TABLE.relative_to(PROJECT_ROOT)}`",
        f"- `{OUT_PROFILE.relative_to(PROJECT_ROOT)}`",
        f"- `{OUT_JSON.relative_to(PROJECT_ROOT)}`",
        f"- `{OUT_FIG.relative_to(PROJECT_ROOT)}.png/.pdf/.svg`",
        "",
        "## Key Results",
        "",
    ]
    for _, row in table.iterrows():
        lines.append(
            "- {case}: local conductance loss={local:.6e}, whole-domain loss={whole:.6e}, ratio={ratio:.3g}, resistance field used={used}".format(
                case=row["case_label"],
                local=float(row["local_conductance_loss"]),
                whole=float(row["whole_domain_conductance_loss"]),
                ratio=float(row["local_to_whole_loss_ratio"]),
                used=str(bool(row["hydraulic_resistance_field_used"])).lower(),
            )
        )
    lines.extend(
        [
            "",
            "## How To Run",
            "",
            "```bash",
            "python3 papers/paper2_voxel_topology_clogging/scripts/run_cropped_flow_domain_permeability.py",
            "```",
            "",
            "## Boundary",
            "",
            "The result can support local sensitivity reasoning for the current pre-clogging cases. It must not be described as Navier-Stokes CFD, LBM, measured pressure or pressure-calibrated Ib.",
        ]
    )
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    """Run cropped-domain local conductance checks."""
    args = parse_args()
    table, _ = run_cropped_permeability(args.crop_manifest, args.blockage, args.whole_domain, args.exponent)
    print(OUT_TABLE)
    print(json.dumps({"cases": len(table), "max_local_loss": float(table["local_conductance_loss"].max())}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
