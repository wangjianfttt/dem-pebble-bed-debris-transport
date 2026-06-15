#!/usr/bin/env python3
"""Collect formal near-threshold repeat-seed results for Paper 2."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
MANIFEST = PAPER_DIR / "data" / "paper2_near_threshold_repeat_case_manifest.json"
BASELINE_PROCESSED = PROJECT_ROOT / "data" / "processed" / "paper1_velocity_scan_frozen" / "paper1_df0p0225_ug2_seed401.json"
OUT_DIR = PROJECT_ROOT / "data" / "processed" / "paper1_velocity_scan_frozen"
OUT_CSV = PAPER_DIR / "tables" / "paper2_near_threshold_repeat_summary.csv"
OUT_JSON = PAPER_DIR / "data" / "paper2_near_threshold_repeat_summary.json"
OUT_MD = PAPER_DIR / "notes" / "paper2_near_threshold_repeat_summary.md"
FIG_STEM = "paper2_figS17_near_threshold_repeat_seed_status"
FIG_DIR = PAPER_DIR / "figures"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST, help="Repeat-case manifest JSON.")
    parser.add_argument("--analyze-missing-dumps", action="store_true", help="Run analyze_debris_transport.py for cases with dumps but no processed JSON.")
    parser.add_argument("--allow-incomplete-analysis", action="store_true", help="Allow analysis of partial dumps without a final restart. Use only for diagnostics, not manuscript evidence.")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    """Load a required JSON object."""
    if not path.exists():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def metric_from_processed(path: Path) -> dict[str, Any]:
    """Extract repeat-seed metrics from a processed transport JSON file."""
    data = load_json(path)
    btc_t = data.get("BTC_t", [])
    r_t = data.get("R_t", [])
    final_btc = float(btc_t[-1]["BTC"]) if btc_t else np.nan
    final_retention = float(r_t[-1]["R"]) if r_t else np.nan
    axis = data.get("flow_axis", "x")
    position = data.get("final_flow_axis_position_summary", {})
    x_mean = position.get(f"{axis}_mean")
    return {
        "final_BTC": final_btc,
        "final_retention": final_retention,
        "first_breakthrough_elapsed_s": data.get("breakthrough_elapsed_from_first_output"),
        "observed_duration_s": data.get("observed_duration_from_first_output"),
        "particle_count_last_frame_type2": data.get("particle_count_last_frame_type2"),
        "max_blockage_ratio": data.get("max_blockage_ratio"),
        "mean_position_m": x_mean,
        "processed_path": str(path.relative_to(PROJECT_ROOT)),
    }


def latest_all_dump(case_dir: Path, pattern: str) -> Path | None:
    """Return the latest all-particle dump matching a case pattern."""
    dumps = sorted(case_dir.glob(pattern))
    if not dumps:
        return None
    return max(dumps, key=lambda path: path.stat().st_mtime)


def count_dump_files(case_dir: Path, pattern: str) -> int:
    """Count dump files matching a glob pattern in a case directory."""
    return len(list(case_dir.glob(pattern)))


def parse_preflight_log(path: Path) -> dict[str, Any]:
    """Extract lightweight completion diagnostics from a LIGGGHTS preflight log."""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    diagnostics: dict[str, Any] = {}
    for line in text.splitlines():
        if line.startswith("Loop time of "):
            parts = line.split()
            if len(parts) >= 13:
                try:
                    diagnostics["preflight_loop_time_s"] = float(parts[3])
                    diagnostics["preflight_steps"] = int(parts[8])
                    diagnostics["preflight_final_atoms"] = int(parts[11])
                except ValueError:
                    pass
        elif line.startswith("Dangerous builds ="):
            try:
                diagnostics["preflight_dangerous_builds"] = int(line.split("=")[1].strip())
            except ValueError:
                pass
        elif " - a total of " in line and " particle templates " in line and " inserted so far." in line:
            parts = line.strip().split()
            try:
                diagnostics["preflight_inserted_particles"] = int(parts[4])
            except (IndexError, ValueError):
                pass
    return diagnostics


def preflight_status(case: dict[str, Any], case_dir: Path) -> dict[str, Any]:
    """Summarize whether a short non-evidence preflight completed for a repeat case."""
    case_name = str(case["case_name"])
    log_path = case_dir / f"{case_name}_preflight.log"
    restart_path = case_dir / f"{case_name}_preflight.restart"
    all_dump_count = count_dump_files(case_dir, f"{case_name}_preflight_all_*.dump")
    type2_dump_count = count_dump_files(case_dir, f"{case_name}_preflight_type2_*.dump")
    log_exists = log_path.exists()
    restart_exists = restart_path.exists()
    diagnostics = parse_preflight_log(log_path)
    completed = (
        log_exists
        and restart_exists
        and all_dump_count > 0
        and type2_dump_count > 0
        and diagnostics.get("preflight_steps") == 10000
        and diagnostics.get("preflight_final_atoms", 0) >= 10000
        and diagnostics.get("preflight_dangerous_builds", 1) == 0
    )
    partial = log_exists or restart_exists or all_dump_count > 0 or type2_dump_count > 0
    status = "passed" if completed else "incomplete" if partial else "not_run"
    row = {
        "preflight_status": status,
        "preflight_log": None if not log_exists else str(log_path.relative_to(PROJECT_ROOT)),
        "preflight_restart_exists": bool(restart_exists),
        "preflight_all_dump_count": int(all_dump_count),
        "preflight_type2_dump_count": int(type2_dump_count),
        "preflight_boundary": "Short 10k-step executable check only; not formal manuscript evidence.",
    }
    row.update(diagnostics)
    return row


def run_transport_analysis(case: dict[str, Any], dump_path: Path) -> None:
    """Run the shared debris-transport analyzer for one completed repeat case."""
    case_dir = PROJECT_ROOT / str(case["case_dir"])
    out_path = PROJECT_ROOT / str(case["processed_target"])
    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "analyze_debris_transport.py"),
        "--dump",
        str(dump_path),
        "--config",
        str(case_dir / "base.yaml"),
        "--debris-config",
        str(case_dir / "debris.yaml"),
        "--out",
        str(out_path),
        "--flow-axis",
        "x",
        "--figure-dir",
        str(PAPER_DIR / "figures" / "repeat_seed_diagnostics" / str(case["case_name"])),
    ]
    subprocess.run(cmd, check=True)


def production_completion_status(case: dict[str, Any], case_dir: Path) -> dict[str, Any]:
    """Return completion status for the formal production run."""
    case_name = str(case["case_name"])
    final_restart = case_dir / f"{case_name}.restart"
    exit_file = case_dir / "production.exit"
    return {
        "production_final_restart_exists": bool(final_restart.exists()),
        "production_exit_code": None if not exit_file.exists() else exit_file.read_text(encoding="utf-8", errors="replace").strip(),
    }


def build_rows(manifest: dict[str, Any], analyze_missing_dumps: bool = False, allow_incomplete_analysis: bool = False) -> list[dict[str, Any]]:
    """Build formal repeat-seed summary rows."""
    rows = [
        {
            "case_name": "paper1_df0p0225_ug2_seed401",
            "seed_offset": 401,
            "df_over_dp": 0.0225,
            "gas_velocity_m_s": 2.0,
            "debris_total_number": 3000,
            "case_dir": "cases/clogging_scan/paper1_velocity_scan/paper1_df0p0225_ug2_seed401",
            "evidence_status": "formal_processed",
            "claim_boundary": "Formal frozen-bed reference row already post-processed.",
            **metric_from_processed(BASELINE_PROCESSED),
        }
    ]
    for case in manifest.get("cases", []):
        case_dir = PROJECT_ROOT / str(case["case_dir"])
        processed = PROJECT_ROOT / str(case["processed_target"])
        dump = latest_all_dump(case_dir, str(case.get("dump_file_all", f"{case['case_name']}_all_*.dump")))
        if analyze_missing_dumps and dump and not processed.exists():
            completion = production_completion_status(case, case_dir)
            if allow_incomplete_analysis or completion["production_final_restart_exists"]:
                run_transport_analysis(case, dump)
        row = dict(case)
        row.update(preflight_status(case, case_dir))
        row.update(production_completion_status(case, case_dir))
        row["dump_path"] = None if dump is None else str(dump.relative_to(PROJECT_ROOT))
        if processed.exists():
            row.update(metric_from_processed(processed))
            row["evidence_status"] = "formal_processed"
            row["claim_boundary"] = "Formal frozen-bed repeat row with processed DEM transport metrics."
        elif dump is not None:
            row.update(
                {
                    "evidence_status": "dump_available_not_processed",
                    "final_BTC": np.nan,
                    "final_retention": np.nan,
                    "first_breakthrough_elapsed_s": np.nan,
                    "observed_duration_s": np.nan,
                    "particle_count_last_frame_type2": np.nan,
                    "max_blockage_ratio": np.nan,
                    "mean_position_m": np.nan,
                }
            )
            if not row["production_final_restart_exists"]:
                row["claim_boundary"] = "Partial production dump exists, but final restart is absent; do not use as manuscript evidence."
        else:
            row.update(
                {
                    "evidence_status": "case_generated_not_run",
                    "final_BTC": np.nan,
                    "final_retention": np.nan,
                    "first_breakthrough_elapsed_s": np.nan,
                    "observed_duration_s": np.nan,
                    "particle_count_last_frame_type2": np.nan,
                    "max_blockage_ratio": np.nan,
                    "mean_position_m": np.nan,
                }
            )
        rows.append(row)
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize repeat-seed evidence status."""
    table = pd.DataFrame(rows)
    status_counts = table["evidence_status"].value_counts().to_dict()
    processed = table[table["evidence_status"] == "formal_processed"].copy()
    btc_values = processed["final_BTC"].dropna().astype(float)
    preflight_counts = table["preflight_status"].value_counts().to_dict() if "preflight_status" in table else {}
    ready = int(len(processed)) >= 3
    summary: dict[str, Any] = {
        "decision": "repeat_seed_evidence_ready" if ready else "repeat_seed_cases_pending",
        "row_count": int(len(table)),
        "formal_processed_count": int(len(processed)),
        "status_counts": {str(key): int(value) for key, value in status_counts.items()},
        "preflight_status_counts": {str(key): int(value) for key, value in preflight_counts.items()},
        "preflight_pass_count": int(preflight_counts.get("passed", 0)),
        "missing_or_pending_cases": table[table["evidence_status"] != "formal_processed"]["case_name"].tolist(),
        "claim_boundary": "Repeat-seed uncertainty can enter the manuscript only after at least three formal processed rows are available.",
        "preflight_boundary": "Passed preflight rows verify executable setup and output plumbing only; they are not DEM transport evidence.",
    }
    if len(btc_values):
        summary["final_BTC_mean"] = float(btc_values.mean())
        summary["final_BTC_min"] = float(btc_values.min())
        summary["final_BTC_max"] = float(btc_values.max())
    return summary


def configure_matplotlib() -> None:
    """Configure a simple publication-oriented figure style."""
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "pdf.fonttype": 42,
            "svg.fonttype": "none",
            "font.size": 8,
            "axes.spines.right": False,
            "axes.spines.top": False,
        }
    )


def make_status_figure(rows: list[dict[str, Any]]) -> None:
    """Create a compact repeat-seed status figure."""
    configure_matplotlib()
    table = pd.DataFrame(rows)
    table["seed_label"] = table["seed_offset"].astype(str)
    colors = {
        "formal_processed": "#4d4d4d",
        "dump_available_not_processed": "#d9a441",
        "case_generated_not_run": "#9eb6d8",
    }
    fig, ax = plt.subplots(figsize=(3.6, 2.45), constrained_layout=True)
    y = np.arange(len(table))
    x = table["final_BTC"].astype(float)
    x_plot = x.fillna(0.0)
    for yi, (_, row) in zip(y, table.iterrows()):
        ax.scatter(
            x_plot.loc[row.name],
            yi,
            s=72,
            color=colors.get(row["evidence_status"], "#cccccc"),
            edgecolor="#222222",
            linewidth=0.45,
        )
        label = "pending" if pd.isna(row["final_BTC"]) else f"{row['final_BTC']:.4f}"
        ax.text(x_plot.loc[row.name] + 0.0015, yi, label, va="center", fontsize=7)
    ax.set_yticks(y, [f"seed {seed}" for seed in table["seed_label"]])
    ax.set_xlabel("final BTC")
    ax.set_title("Near-threshold repeat seeds")
    ax.set_xlim(-0.002, max(0.03, float(x_plot.max()) + 0.01))
    ax.grid(True, axis="x", linewidth=0.35, alpha=0.35)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for suffix, kwargs in {".png": {"dpi": 600}, ".pdf": {}, ".svg": {}}.items():
        fig.savefig(FIG_DIR / f"{FIG_STEM}{suffix}", bbox_inches="tight", **kwargs)
    plt.close(fig)


def write_markdown(rows: list[dict[str, Any]], summary: dict[str, Any], out_path: Path = OUT_MD) -> None:
    """Write a Markdown repeat-seed status report."""
    table = pd.DataFrame(rows)
    lines = [
        "# Near-Threshold Repeat-Seed Summary",
        "",
        f"- Decision: `{summary['decision']}`",
        f"- Formal processed rows: {summary['formal_processed_count']}",
        f"- Status counts: `{summary['status_counts']}`",
        f"- Preflight status counts: `{summary['preflight_status_counts']}`",
        f"- Pending cases: `{summary['missing_or_pending_cases']}`",
        f"- Boundary: {summary['claim_boundary']}",
        f"- Preflight boundary: {summary['preflight_boundary']}",
        "",
        "## Rows",
        "",
        "| Seed | Case | Evidence status | Preflight | Final BTC | First breakthrough elapsed (s) | Boundary |",
        "|---:|---|---|---|---:|---:|---|",
    ]
    for _, row in table.iterrows():
        btc = "" if pd.isna(row["final_BTC"]) else f"{float(row['final_BTC']):.6g}"
        first = "" if pd.isna(row["first_breakthrough_elapsed_s"]) else f"{float(row['first_breakthrough_elapsed_s']):.6g}"
        lines.append(
            f"| {int(row['seed_offset'])} | `{row['case_name']}` | `{row['evidence_status']}` | `{row.get('preflight_status', 'not_applicable')}` | {btc} | {first} | {row['claim_boundary']} |"
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(manifest_path: Path = MANIFEST, analyze_missing_dumps: bool = False, allow_incomplete_analysis: bool = False) -> dict[str, Any]:
    """Write repeat-seed summary outputs."""
    rows = build_rows(load_json(manifest_path), analyze_missing_dumps=analyze_missing_dumps, allow_incomplete_analysis=allow_incomplete_analysis)
    summary = summarize(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT_CSV, index=False)
    OUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(rows, summary)
    make_status_figure(rows)
    return summary


def main() -> int:
    """Run the repeat-seed result collector."""
    args = parse_args()
    summary = write_outputs(args.manifest, analyze_missing_dumps=args.analyze_missing_dumps, allow_incomplete_analysis=args.allow_incomplete_analysis)
    print(json.dumps(summary, indent=2))
    print(OUT_CSV)
    print(OUT_JSON)
    print(OUT_MD)
    print(FIG_DIR / f"{FIG_STEM}.pdf")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
