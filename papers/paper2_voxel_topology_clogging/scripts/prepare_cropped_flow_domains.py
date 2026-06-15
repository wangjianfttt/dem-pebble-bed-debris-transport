#!/usr/bin/env python3
"""Prepare cropped pore-domain inputs around peak debris-deposition zones."""

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

from src.voxel.flow_domain import (  # noqa: E402
    axial_blockage_field,
    crop_voxel_box,
    hydraulic_resistance_multiplier_field,
    select_peak_blockage_window,
    summarize_flow_domain,
    write_flow_domain,
)
from src.voxel.io import load_voxel_npz  # noqa: E402


PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
DEFAULT_VOXEL = PROJECT_ROOT / "data/processed/ct_pipeline_li4sio4_1mm_10k_axial_cuboid_piston_compacted/bed_voxel_effective.npz"
DEFAULT_BLOCKAGE = PAPER_DIR / "tables/paper2_fig4_loading_blockage_source.csv"
DEFAULT_OUT_DIR = PAPER_DIR / "flow_domains"
OUT_TABLE = PAPER_DIR / "tables/paper2_cropped_flow_domain_manifest.csv"
OUT_JSON = PAPER_DIR / "data/paper2_cropped_flow_domain_summary.json"
OUT_FIG = PAPER_DIR / "figures/paper2_figS13_cropped_flow_domains"
OUT_REPORT = PAPER_DIR / "notes/stage_report_cropped_flow_domain_preparation_2026-06-09.md"


def configure_matplotlib() -> None:
    """Configure compact publication-style plotting."""
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
    parser.add_argument("--voxel", type=Path, default=DEFAULT_VOXEL, help="Effective bed voxel .npz file.")
    parser.add_argument("--blockage", type=Path, default=DEFAULT_BLOCKAGE, help="Axial blockage profile CSV.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR, help="Directory for cropped flow-domain inputs.")
    parser.add_argument("--half-width", type=float, default=0.004, help="Half width of each axial crop window in metres.")
    return parser.parse_args()


def prepare_domains(voxel_path: Path, blockage_path: Path, out_dir: Path, half_width_m: float) -> pd.DataFrame:
    """Prepare cropped flow domains for each loading state in a blockage table."""
    voxel, metadata = load_voxel_npz(voxel_path)
    blockage = pd.read_csv(blockage_path)
    domain = metadata["domain"]
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for n_debris in sorted(blockage["debris_total_number"].astype(int).unique()):
        bounds = select_peak_blockage_window(blockage, n_debris, half_width_m=half_width_m, domain=domain)
        cropped, cropped_metadata = crop_voxel_box(voxel, metadata, bounds)
        group = blockage[blockage["debris_total_number"].astype(int) == n_debris]
        peak = group.loc[group["blockage_ratio"].astype(float).idxmax()]
        case_dir = out_dir / f"N{n_debris}_peak_blockage"
        cropped_metadata["flow_domain_role"] = "peak_blockage_crop_for_future_pressure_flow_solver"
        cropped_metadata["flow_axis"] = "x"
        cropped_metadata["source_blockage_profile"] = str(blockage_path.relative_to(PROJECT_ROOT))
        cropped_metadata["debris_total_number"] = int(n_debris)
        cropped_metadata["evidence_boundary"] = "input domain only; not CFD, not LBM and not measured pressure"
        written = write_flow_domain(case_dir, cropped, cropped_metadata)
        blockage_field = axial_blockage_field(blockage, n_debris, cropped, cropped_metadata, axis="x")
        resistance_field = hydraulic_resistance_multiplier_field(cropped, blockage_field, axis="x")
        blockage_path_out = case_dir / "blockage_field.npy"
        resistance_path_out = case_dir / "hydraulic_resistance_multiplier_field.npy"
        np.save(blockage_path_out, blockage_field.astype(np.float32))
        np.save(resistance_path_out, resistance_field.astype(np.float32))
        cropped_metadata["blockage_field_npy"] = str(blockage_path_out.relative_to(PROJECT_ROOT))
        cropped_metadata["hydraulic_resistance_multiplier_field_npy"] = str(resistance_path_out.relative_to(PROJECT_ROOT))
        cropped_metadata["hydraulic_resistance_model"] = "slice-local Ergun viscous resistance multiplier from epsilon_t = epsilon0 * (1 - B)"
        (case_dir / "metadata.json").write_text(json.dumps(cropped_metadata, indent=2), encoding="utf-8")
        summary = summarize_flow_domain(cropped, cropped_metadata, axis="x")
        crop = cropped_metadata["crop_box"]["x"]
        rows.append(
            {
                "case_label": f"N={n_debris}",
                "debris_total_number": int(n_debris),
                "crop_role": "peak_blockage_window",
                "x_peak_blockage_m": float(peak["x_center"]),
                "x_requested_lower_m": float(bounds["x"][0]),
                "x_requested_upper_m": float(bounds["x"][1]),
                "x_applied_lower_m": float(crop["applied_lower"]),
                "x_applied_upper_m": float(crop["applied_upper"]),
                "crop_length_m": float(crop["applied_upper"] - crop["applied_lower"]),
                "voxel_size_m": summary["voxel_size_m"],
                "shape_x": summary["shape_x"],
                "shape_y": summary["shape_y"],
                "shape_z": summary["shape_z"],
                "porosity": summary["porosity"],
                "pore_voxels": summary["pore_voxels"],
                "solid_voxels": summary["solid_voxels"],
                "through_connected_void_fraction_x": summary["through_connected_void_fraction_x"],
                "max_blockage_ratio_in_profile": float(group["blockage_ratio"].max()),
                "mean_blockage_ratio_in_crop": float(blockage_field[cropped == 0].mean()) if np.any(cropped == 0) else 0.0,
                "max_blockage_ratio_in_crop": float(blockage_field.max()),
                "mean_resistance_multiplier_in_pores": float(resistance_field[cropped == 0].mean()) if np.any(cropped == 0) else 1.0,
                "max_resistance_multiplier_in_pores": float(resistance_field[cropped == 0].max()) if np.any(cropped == 0) else 1.0,
                "voxel_npz": str(Path(written["voxel_npz"]).relative_to(PROJECT_ROOT)),
                "pore_mask_npy": str(Path(written["pore_mask_npy"]).relative_to(PROJECT_ROOT)),
                "blockage_field_npy": str(blockage_path_out.relative_to(PROJECT_ROOT)),
                "hydraulic_resistance_multiplier_field_npy": str(resistance_path_out.relative_to(PROJECT_ROOT)),
                "metadata_json": str(Path(written["metadata_json"]).relative_to(PROJECT_ROOT)),
                "evidence_boundary": "cropped pore-domain and debris-resistance input for future pressure-flow solvers; not a solver result",
            }
        )
    table = pd.DataFrame(rows)
    OUT_TABLE.parent.mkdir(parents=True, exist_ok=True)
    OUT_TABLE.write_text(table.to_csv(index=False), encoding="utf-8")
    summary = {
        "voxel_path": str(voxel_path.relative_to(PROJECT_ROOT)),
        "blockage_profile": str(blockage_path.relative_to(PROJECT_ROOT)),
        "out_dir": str(out_dir.relative_to(PROJECT_ROOT)),
        "half_width_m": half_width_m,
        "cases": table.to_dict(orient="records"),
        "evidence_boundary": "These are cropped input domains only; no CFD/LBM calculation has been run here.",
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_out_dir_readme(out_dir, table, half_width_m)
    save_figure(blockage, table)
    write_stage_report(table)
    return table


def write_out_dir_readme(out_dir: Path, table: pd.DataFrame, half_width_m: float) -> None:
    """Write a README for the flow-domain collection."""
    lines = [
        "# Paper 2 Cropped Flow-Domain Inputs",
        "",
        "These folders contain cropped DEM-derived voxel pore domains centred on peak local blockage locations in the loading scan.",
        "",
        f"Default half-width: {half_width_m:.4g} m.",
        "",
        "| Case | x window (m) | shape | porosity | through-connected pore fraction | max B | max resistance multiplier |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in table.iterrows():
        lines.append(
            "| {case} | {lo:.6g}-{hi:.6g} | {sx}x{sy}x{sz} | {por:.6f} | {conn:.6f} | {bmax:.3e} | {rmax:.6g} |".format(
                case=row["case_label"],
                lo=row["x_applied_lower_m"],
                hi=row["x_applied_upper_m"],
                sx=int(row["shape_x"]),
                sy=int(row["shape_y"]),
                sz=int(row["shape_z"]),
                por=float(row["porosity"]),
                conn=float(row["through_connected_void_fraction_x"]),
                bmax=float(row["max_blockage_ratio_in_crop"]),
                rmax=float(row["max_resistance_multiplier_in_pores"]),
            )
        )
    lines.extend(
        [
            "",
            "Boundary: these files prepare reproducible local pore domains and debris-induced hydraulic-resistance fields for later OpenFOAM/OpenLB/LBM or voxel-network calculations. They are not pressure-drop evidence in the current manuscript.",
        ]
    )
    (out_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def save_figure(blockage: pd.DataFrame, table: pd.DataFrame) -> None:
    """Save the cropped-flow-domain supplementary figure."""
    configure_matplotlib()
    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
    colors = {3000: "#2166ac", 6000: "#b2182b", 10000: "#4daf4a"}
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), constrained_layout=True)

    for n_debris, group in blockage.groupby("debris_total_number"):
        group = group.sort_values("x_center")
        axes[0].plot(
            group["x_center"] / 0.045,
            group["blockage_ratio"],
            marker="o",
            markersize=3.0,
            linewidth=1.0,
            color=colors.get(int(n_debris), "#4d4d4d"),
            label=f"N={int(n_debris)}",
        )
    for _, row in table.iterrows():
        axes[0].axvspan(
            row["x_applied_lower_m"] / 0.045,
            row["x_applied_upper_m"] / 0.045,
            color=colors.get(int(row["debris_total_number"]), "#bdbdbd"),
            alpha=0.10,
            linewidth=0,
        )
    axes[0].set_xlabel("x/L")
    axes[0].set_ylabel("local blockage ratio")
    axes[0].ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    axes[0].grid(True, linewidth=0.35, alpha=0.35)
    axes[0].legend(loc="best")
    axes[0].text(0.02, 0.95, "a", transform=axes[0].transAxes, va="top", ha="left", weight="bold")

    x = np.arange(len(table))
    axes[1].bar(x - 0.18, table["porosity"], width=0.36, color="#969696", label="porosity")
    axes[1].bar(
        x + 0.18,
        table["through_connected_void_fraction_x"],
        width=0.36,
        color="#1b9e77",
        label="through-connected pores",
    )
    axes[1].set_xticks(x, [str(int(value)) for value in table["debris_total_number"]])
    axes[1].set_xlabel("injected debris count")
    axes[1].set_ylim(0.0, 1.05)
    axes[1].set_ylabel("fraction")
    axes[1].grid(True, axis="y", linewidth=0.35, alpha=0.35)
    axes[1].legend(loc="upper center", bbox_to_anchor=(0.5, 1.18), ncol=2, handlelength=1.2, columnspacing=1.0)
    axes[1].text(0.02, 0.95, "b", transform=axes[1].transAxes, va="top", ha="left", weight="bold")

    for suffix, kwargs in {".png": {"dpi": 600}, ".pdf": {}, ".svg": {}}.items():
        fig.savefig(f"{OUT_FIG}{suffix}", bbox_inches="tight", **kwargs)
    plt.close(fig)


def write_stage_report(table: pd.DataFrame) -> None:
    """Write a concise stage report for cropped-domain preparation."""
    lines = [
        "# Stage report: cropped flow-domain preparation",
        "",
        "Date: 2026-06-09",
        "",
        "## Scope",
        "",
        "This stage prepares cropped DEM-derived voxel pore-domain inputs around peak local blockage zones. It does not run OpenFOAM, OpenLB, LBM or any Navier-Stokes solver.",
        "",
        "## Files Added or Updated",
        "",
        "- `src/voxel/flow_domain.py`",
        "- `tests/test_voxel_flow_domain.py`",
        f"- `{OUT_TABLE.relative_to(PROJECT_ROOT)}`",
        f"- `{OUT_JSON.relative_to(PROJECT_ROOT)}`",
        f"- `{DEFAULT_OUT_DIR.relative_to(PROJECT_ROOT)}/`",
        f"- `{OUT_FIG.relative_to(PROJECT_ROOT)}.png/.pdf/.svg`",
        "",
        "## Key Results",
        "",
    ]
    for _, row in table.iterrows():
        lines.append(
            "- {case}: x={lo:.5f}-{hi:.5f} m, shape={sx}x{sy}x{sz}, porosity={por:.4f}, through-connected={conn:.4f}, max B={bmax:.3e}, max resistance multiplier={rmax:.6g}".format(
                case=row["case_label"],
                lo=float(row["x_applied_lower_m"]),
                hi=float(row["x_applied_upper_m"]),
                sx=int(row["shape_x"]),
                sy=int(row["shape_y"]),
                sz=int(row["shape_z"]),
                por=float(row["porosity"]),
                conn=float(row["through_connected_void_fraction_x"]),
                bmax=float(row["max_blockage_ratio_in_crop"]),
                rmax=float(row["max_resistance_multiplier_in_pores"]),
            )
        )
    lines.extend(
        [
            "",
            "## How To Run",
            "",
            "```bash",
            "python3 papers/paper2_voxel_topology_clogging/scripts/prepare_cropped_flow_domains.py",
            "pytest tests/test_voxel_flow_domain.py",
            "```",
            "",
            "## Next Step",
            "",
            "Use these cropped pore masks together with `blockage_field.npy` and `hydraulic_resistance_multiplier_field.npy` as small, tractable domains for an actual OpenFOAM/OpenLB/LBM pressure-flow calculation or a more detailed voxel-network permeability comparison.",
        ]
    )
    OUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    """Prepare cropped flow-domain inputs and supporting figure/table files."""
    args = parse_args()
    table = prepare_domains(args.voxel, args.blockage, args.out_dir, args.half_width)
    print(OUT_TABLE)
    print(json.dumps({"cases": len(table), "out_dir": str(args.out_dir)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
