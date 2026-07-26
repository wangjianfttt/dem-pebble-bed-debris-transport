#!/usr/bin/env python3
"""Run the complete consistency check for the minimal Paper 3 release."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DATA = ROOT / "data"
sys.path.insert(0, str(HERE))

from build_xie2021_full_validation import collect  # noqa: E402
from verify_mobile_immobile_summary_consistency import (  # noqa: E402
    verify as verify_mobile_immobile,
    verify_pairwise,
)
from verify_multiscale_ctrw_design_consistency import verify as verify_ctrw  # noqa: E402
from verify_pooled_first_passage_consistency import verify as verify_fpt  # noqa: E402
from verify_transport_mechanism_pairing_consistency import (  # noqa: E402
    verify as verify_mechanism,
)


EXPECTED_CELLS = {
    (0.10, 0.05),
    (0.10, 0.10),
    (0.20, 0.05),
    (0.20, 0.10),
}
EXPECTED_SEEDS = {20260713, 20260714, 20260715}
EXPECTED_XIE_RETENTION = {
    0.10: 0.03557504873294347,
    0.15: 0.36062378167641324,
    0.20: 0.9537037037037037,
    0.25: 1.0,
}
FORBIDDEN_PARTS = {
    "manuscript",
    "figures",
    "processor0",
    "restart",
    "dump",
    "logs",
}
FORBIDDEN_SUFFIXES = {
    ".pdf",
    ".tex",
    ".png",
    ".jpg",
    ".jpeg",
    ".svg",
    ".vtk",
    ".vtu",
    ".vtp",
    ".dump",
    ".restart",
    ".gz",
    ".zip",
}
FORBIDDEN_TEXT = (
    "/Users/",
    "/n96pfs/",
    "ysn96pc0041",
    "github_pat_",
    "ghp_",
    "BEGIN PRIVATE KEY",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"empty CSV: {path.relative_to(ROOT)}")
    return rows


def verify_sha256() -> int:
    manifest = ROOT / "SHA256SUMS"
    if not manifest.is_file():
        raise ValueError("SHA256SUMS is missing")
    listed: set[Path] = set()
    for line in manifest.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"missing or linked file in SHA256SUMS: {relative}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            raise ValueError(f"SHA256 mismatch: {relative}")
        listed.add(Path(relative))
    actual_files = {
        path.relative_to(ROOT)
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.name != "SHA256SUMS"
        and "__pycache__" not in path.parts
    }
    if listed != actual_files:
        raise ValueError("SHA256SUMS file set does not match the release")
    return len(listed)


def verify_public_scope() -> int:
    files = [path for path in ROOT.rglob("*") if path.is_file()]
    for path in files:
        relative = path.relative_to(ROOT)
        lowered_parts = {part.lower() for part in relative.parts}
        if lowered_parts & FORBIDDEN_PARTS or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            raise ValueError(f"forbidden file in minimal release: {relative}")
        if (
            path.resolve() != Path(__file__).resolve()
            and path.suffix.lower() in {".py", ".csv", ".json", ".md", ".txt", ""}
        ):
            text = path.read_text(encoding="utf-8", errors="replace")
            for token in FORBIDDEN_TEXT:
                if token in text:
                    raise ValueError(f"private path or credential pattern in {relative}")
    return len(files)


def verify_main_transport() -> dict[str, object]:
    base = DATA / "main_transport"
    releases = read_csv(base / "postequilibrated_primary_release_metrics.csv")
    cells = {
        (round(float(row["gas_velocity_m_s"]), 8), round(float(row["df_over_dp"]), 8))
        for row in releases
    }
    seeds = {int(row["release_seed"]) for row in releases}
    if (
        len(releases) != 12
        or cells != EXPECTED_CELLS
        or seeds != EXPECTED_SEEDS
        or any(row["role"] != "primary" for row in releases)
        or any(row["selected_mesh_route"] != "coarse_2p5dp" for row in releases)
    ):
        raise ValueError("the 12-case main transport design is incomplete")
    for cell in EXPECTED_CELLS:
        selected = [
            row
            for row in releases
            if (
                round(float(row["gas_velocity_m_s"]), 8),
                round(float(row["df_over_dp"]), 8),
            )
            == cell
        ]
        if {int(row["release_seed"]) for row in selected} != EXPECTED_SEEDS:
            raise ValueError(f"incomplete release seeds for design cell {cell}")

    design = read_csv(base / "postequilibrated_design_cell_summary.csv")
    if len(design) != 248 or any(int(row["count"]) != 3 for row in design):
        raise ValueError("the four-cell design summaries are incomplete")
    paired = read_csv(base / "postequilibrated_paired_contrasts.csv")
    paired_summary = read_csv(base / "postequilibrated_paired_contrast_summary.csv")
    if (
        len(paired) != 930
        or len(paired_summary) != 310
        or any(int(row["count"]) != 3 for row in paired_summary)
    ):
        raise ValueError("the paired transport contrasts are incomplete")
    return {
        "case_count": 12,
        "design_cell_count": 4,
        "release_seeds": sorted(EXPECTED_SEEDS),
        "design_summary_rows": len(design),
        "paired_contrast_rows": len(paired),
    }


def verify_xie() -> dict[str, object]:
    paired, histories, summary = collect(
        DATA / "xie/reference/reference_digitized.csv",
        DATA / "xie/cases",
    )
    calculated = {
        round(float(row["df_over_dp"]), 8): float(row["cfdem_retained_fraction"])
        for row in paired
    }
    if set(calculated) != set(EXPECTED_XIE_RETENTION):
        raise ValueError("the four Xie size ratios are incomplete")
    for ratio, expected in EXPECTED_XIE_RETENTION.items():
        if not math.isclose(calculated[ratio], expected, rel_tol=0.0, abs_tol=1.0e-12):
            raise ValueError(f"Xie retained fraction mismatch at {ratio}")
    expected_summary = {
        "rmse_retained_fraction": 0.13733346604198188,
        "mae_retained_fraction": 0.08209760512392092,
        "pearson_correlation": 0.9578432115761643,
    }
    for field, expected in expected_summary.items():
        if not math.isclose(
            float(summary[field]), expected, rel_tol=0.0, abs_tol=1.0e-12
        ):
            raise ValueError(f"Xie {field} mismatch")
    if summary["monotonic_trend_reproduced"] is not True or len(histories) != 804:
        raise ValueError("Xie history or monotonic-trend check failed")
    return {
        "comparison_point_count": 4,
        "history_row_count": len(histories),
        "retained_fraction": calculated,
        **expected_summary,
        "monotonic_trend_reproduced": True,
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="paper3-minimal-check-") as directory:
        output = Path(directory)
        report = {
            "status": "complete",
            "checksummed_file_count": verify_sha256(),
            "minimal_public_file_count": verify_public_scope(),
            "main_transport": verify_main_transport(),
            "pooled_first_passage": verify_fpt(
                DATA / "first_passage/pooled_first_passage_summary.csv",
                DATA / "first_passage/pooled_first_passage_leave_one_release_out.csv",
            ),
            "mobile_immobile": verify_mobile_immobile(
                DATA / "mobile_immobile/leave_one_out_mobile_immobile_predictions.csv",
                DATA / "mobile_immobile/leave_one_out_mobile_immobile_summary.json",
            ),
            "mobile_immobile_pairwise": verify_pairwise(
                DATA / "mobile_immobile/pairwise_mobile_immobile_predictions.csv",
                DATA / "mobile_immobile/pairwise_mobile_immobile_summary.json",
            ),
            "ctrw": verify_ctrw(
                DATA / "ctrw/multiscale_ctrw_case_metrics.csv",
                DATA / "ctrw/waiting_time_robustness_case_metrics.csv",
                DATA / "ctrw/multiscale_ctrw_design_metrics.csv",
            ),
            "mechanism": verify_mechanism(
                DATA / "mechanism/transport_mechanism_paired_particle_differences.csv",
                DATA / "mechanism/transport_mechanism_paired_bootstrap.csv",
                DATA / "mechanism/transport_mechanism_sensitivity_changes.csv",
            ),
            "xie_20s": verify_xie(),
            "temporary_directory_used": output.name,
        }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
