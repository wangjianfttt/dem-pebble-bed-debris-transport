#!/usr/bin/env python3
"""Stage a minimal Elsevier portal upload package for Paper 2."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
DEFAULT_OUT = PAPER_DIR / "submission_package" / "elsevier_portal_upload_files"

SKIP_STAGED_SUFFIXES = {".aux", ".log", ".fls", ".fdb_latexmk", ".out", ".blg", ".bbl", ".spl"}


PORTAL_UPLOAD_ITEMS = [
    {
        "group": "manuscript",
        "paths": [
            "papers/paper2_voxel_topology_clogging/latex/main.pdf",
            "papers/paper2_voxel_topology_clogging/latex/main.tex",
            "papers/paper2_voxel_topology_clogging/references/paper2_references.bib",
            "papers/paper2_voxel_topology_clogging/submission/highlights.md",
            "papers/paper2_voxel_topology_clogging/submission/word/highlights_CES.docx",
        ],
        "purpose": "Main manuscript, source files, bibliography and highlights.",
    },
    {
        "group": "main_figures",
        "paths": [
            "papers/paper2_voxel_topology_clogging/figures/paper2_fig1_voxel_topology_framework.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_fig2_baseline_voxel_topology.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_fig10_time_resolved_deposition.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_fig3_representative_debris_blockage.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_908_spatial_distribution_evidence.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_fig7_localized_time_dynamics.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_openfoam_model_mesh_main.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_fig9_sparse_front_diagnostics.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_fig4_loading_clogging_response.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_fig6_mechanism_synthesis.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_fig8_response_landscape.pdf",
        ],
        "purpose": "All figure PDFs referenced as main-text figures.",
    },
    {
        "group": "graphical_abstract",
        "paths": [
            "papers/paper2_voxel_topology_clogging/figures/paper2_graphical_abstract.png",
            "papers/paper2_voxel_topology_clogging/figures/paper2_graphical_abstract.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_graphical_abstract.svg",
            "papers/paper2_voxel_topology_clogging/submission/word/graphical_abstract_CES.docx",
        ],
        "purpose": "Graphical abstract in raster, editable/vector and Word-preview formats.",
    },
    {
        "group": "supplementary_material",
        "paths": [
            "papers/paper2_voxel_topology_clogging/supplementary/supplementary_material.pdf",
            "papers/paper2_voxel_topology_clogging/supplementary/supplementary_material.tex",
            "papers/paper2_voxel_topology_clogging/supplementary",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS1_voxel_size_sensitivity.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS2_voxel_coarsening_stress_test.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS3_ergun_pressure_proxy.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS4_time_resolved_deposition.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS5_front_migration_metrics.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS8_explicit_localized_production_summary.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS9_907_tail_capture_mechanism.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS10_source_position_comparison.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS11_mechanism_evidence_map.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS12_voxel_pressure_pilot.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS13_cropped_flow_domains.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS14_cropped_flow_permeability.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS15_cropped_flow_permeability_sensitivity.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS16_dimensionless_mechanism_map.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS17_near_threshold_repeat_seed_status.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS18_subvoxel_hydraulic_evidence.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS19_localized_mechanism_axes.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS20_mechanistic_decoupling_matrix.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS21_observable_response_map.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS22_3d_resistance_amplification_sensitivity.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS23_openfoam_pressure_evidence.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS24_openfoam_model_mesh.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS25_parameter_evidence_coverage.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS26_openfoam_case_matrix.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS27_deep_mechanism_mining.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS28_tail_lag_mechanism_mining.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_figS29_deposition_heterogeneity_mining.pdf",
        ],
        "purpose": "Formal supplementary text, tables and supplementary-figure PDFs.",
    },
    {
        "group": "cover_letter",
        "paths": [
            "papers/paper2_voxel_topology_clogging/submission/cover_letter_draft.md",
            "papers/paper2_voxel_topology_clogging/submission/word/cover_letter_CES.docx",
        ],
        "purpose": "Journal-facing cover letter in Word format plus markdown source.",
    },
    {
        "group": "portal_copy_text",
        "paths": [
            "papers/paper2_voxel_topology_clogging/submission/submission_form_packet.md",
            "papers/paper2_voxel_topology_clogging/submission/elsevier_portal_checklist.md",
        ],
        "purpose": "Copy-ready text helpers for the submission system; not intended as scientific evidence files.",
    },
]


FORBIDDEN_PORTAL_MARKERS = [
    "journal_fallback_front_matter",
    "submission_decision_ledger",
    "editor_response_map",
    "reviewer_precheck",
    "author_confirmation_request",
    "author_confirmation_email",
    "paper2_benchmark_boundary_matrix",
    "paper2_manuscript_argument_map",
]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output staging directory.")
    parser.add_argument("--force", action="store_true", help="Remove an existing output directory before staging.")
    return parser.parse_args()


def file_sha256(path: Path) -> str:
    """Compute a file SHA256 checksum."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_path(src: Path, dst: Path) -> None:
    """Copy a file or directory into the portal staging directory."""
    if src.is_dir():
        for child in src.iterdir():
            copy_path(child, dst / child.name)
        return
    if src.suffix in SKIP_STAGED_SUFFIXES:
        return
    if dst.parent.name == "supplementary" and src.name in {"supplementary_material.pdf", "supplementary_material.tex"}:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def staged_files(out_dir: Path) -> list[dict[str, object]]:
    """Return metadata for staged files."""
    rows: list[dict[str, object]] = []
    for path in sorted(p for p in out_dir.rglob("*") if p.is_file()):
        rel = path.relative_to(out_dir).as_posix()
        rows.append({"path": rel, "size_bytes": path.stat().st_size, "sha256": file_sha256(path)})
    return rows


def forbidden_matches(files: list[dict[str, object]]) -> list[str]:
    """Return staged paths that look like internal-only submission materials."""
    matches: list[str] = []
    for row in files:
        path = str(row["path"])
        if any(marker in path for marker in FORBIDDEN_PORTAL_MARKERS):
            matches.append(path)
    return matches


def write_readme(out_dir: Path) -> None:
    """Write a README explaining the portal-upload package boundary."""
    lines = [
        "# Paper 2 Elsevier Portal Upload Files",
        "",
        "This directory contains a minimal portal-facing upload package. It intentionally excludes internal reviewer-risk maps, fallback-journal materials, audit ledgers and author-confirmation requests.",
        "",
        "## Contents",
        "",
    ]
    for item in PORTAL_UPLOAD_ITEMS:
        lines.append(f"- `{item['group']}`: {item['purpose']}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- Use the separate internal `journal_submission_files` archive for reproducibility and audit handoff.",
            "- Use this portal package for files that may be uploaded or copied into the Elsevier submission system.",
        ]
    )
    out_dir.joinpath("README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def stage_portal_upload_files(out_dir: Path = DEFAULT_OUT, force: bool = False) -> dict[str, object]:
    """Stage a minimal set of files for the Elsevier submission portal."""
    if out_dir.exists():
        if not force:
            raise FileExistsError(f"Output exists; use --force: {out_dir}")
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    missing: list[str] = []
    for item in PORTAL_UPLOAD_ITEMS:
        group_dir = out_dir / item["group"]
        for path_text in item["paths"]:
            src = PROJECT_ROOT / path_text
            if not src.exists():
                missing.append(path_text)
                continue
            copy_path(src, group_dir / src.name)

    write_readme(out_dir)
    files = staged_files(out_dir)
    forbidden = forbidden_matches(files)
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Minimal Elsevier portal-facing upload package for Paper 2.",
        "boundary": "Excludes internal fallback, reviewer-risk, audit-ledger and author-confirmation materials.",
        "items": PORTAL_UPLOAD_ITEMS,
        "missing": missing,
        "forbidden_internal_files": forbidden,
        "file_count": len(files),
        "total_size_bytes": sum(int(row["size_bytes"]) for row in files),
        "files": files,
    }
    (out_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> int:
    """Run the portal upload staging workflow."""
    args = parse_args()
    manifest = stage_portal_upload_files(args.out, force=args.force)
    print(json.dumps({"out": str(args.out), "missing": manifest["missing"], "forbidden_internal_files": manifest["forbidden_internal_files"], "file_count": manifest["file_count"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
