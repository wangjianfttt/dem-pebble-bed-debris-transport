#!/usr/bin/env python3
"""Stage Paper 2 journal-submission files separately from the data/code deposit."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
DEFAULT_OUT = PAPER_DIR / "submission_package" / "journal_submission_files"

SKIP_STAGED_SUFFIXES = {".aux", ".log", ".fls", ".fdb_latexmk", ".out", ".blg", ".bbl", ".spl"}

SUBMISSION_ITEMS = [
    {
        "group": "manuscript",
        "paths": [
            "papers/paper2_voxel_topology_clogging/latex/main.pdf",
            "papers/paper2_voxel_topology_clogging/latex/main.tex",
            "papers/paper2_voxel_topology_clogging/references/paper2_references.bib",
            "papers/paper2_voxel_topology_clogging/submission/highlights.md",
            "papers/paper2_voxel_topology_clogging/submission/word/highlights_CES.docx",
        ],
        "purpose": "Main manuscript PDF, LaTeX source, bibliography and highlights.",
    },
    {
        "group": "main_figures",
        "paths": [
            "papers/paper2_voxel_topology_clogging/figures/paper2_fig1_voxel_topology_framework.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_fig2_baseline_voxel_topology.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_fig3_representative_debris_blockage.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_908_spatial_distribution_evidence.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_fig7_localized_time_dynamics.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_openfoam_model_mesh_main.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_fig4_loading_clogging_response.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_fig6_mechanism_synthesis.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_fig8_response_landscape.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_fig9_sparse_front_diagnostics.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_fig10_time_resolved_deposition.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_graphical_abstract.png",
            "papers/paper2_voxel_topology_clogging/figures/paper2_graphical_abstract.pdf",
            "papers/paper2_voxel_topology_clogging/figures/paper2_graphical_abstract.svg",
            "papers/paper2_voxel_topology_clogging/submission/word/graphical_abstract_CES.docx",
        ],
        "purpose": "Main manuscript figure PDFs and graphical abstract.",
    },
    {
        "group": "supplementary_material",
        "paths": [
            "papers/paper2_voxel_topology_clogging/supplementary/supplementary_material.pdf",
            "papers/paper2_voxel_topology_clogging/supplementary/supplementary_material.tex",
            "papers/paper2_voxel_topology_clogging/supplementary",
            "papers/paper2_voxel_topology_clogging/notes/paper2_figure_package_audit.md",
            "papers/paper2_voxel_topology_clogging/data/paper2_figure_package_audit.json",
            "papers/paper2_voxel_topology_clogging/tables/paper2_figure_package_audit.csv",
            "papers/paper2_voxel_topology_clogging/notes/paper2_main_figure_order_audit.md",
            "papers/paper2_voxel_topology_clogging/data/paper2_main_figure_order_audit.json",
            "papers/paper2_voxel_topology_clogging/notes/paper2_latex_figure_layout_audit.md",
            "papers/paper2_voxel_topology_clogging/data/paper2_latex_figure_layout_audit.json",
            "papers/paper2_voxel_topology_clogging/notes/elsevier_portal_visual_consistency_audit.md",
            "papers/paper2_voxel_topology_clogging/data/elsevier_portal_visual_consistency_audit.json",
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
        "purpose": "Supplementary tables, supplementary figure catalogue and supplementary figure PDFs.",
    },
    {
        "group": "cover_and_declarations",
        "paths": [
            "papers/paper2_voxel_topology_clogging/submission/cover_letter_draft.md",
            "papers/paper2_voxel_topology_clogging/submission/word/cover_letter_CES.docx",
            "papers/paper2_voxel_topology_clogging/submission/ces_novelty_statement.md",
            "papers/paper2_voxel_topology_clogging/submission/claim_boundary_statement.md",
            "papers/paper2_voxel_topology_clogging/submission/submission_checklist.md",
            "papers/paper2_voxel_topology_clogging/submission/submission_metadata_template.md",
            "papers/paper2_voxel_topology_clogging/submission/author_declarations_checklist.md",
            "papers/paper2_voxel_topology_clogging/submission/author_confirmation_sheet.md",
            "papers/paper2_voxel_topology_clogging/submission/author_confirmation_request.md",
            "papers/paper2_voxel_topology_clogging/submission/author_confirmation_request.json",
            "papers/paper2_voxel_topology_clogging/submission/author_confirmation_email_zh_en.md",
            "papers/paper2_voxel_topology_clogging/submission/reviewer_precheck.md",
            "papers/paper2_voxel_topology_clogging/submission/reviewer_precheck.json",
            "papers/paper2_voxel_topology_clogging/submission/submission_metadata_gaps.json",
            "papers/paper2_voxel_topology_clogging/submission/front_matter_audit.json",
            "papers/paper2_voxel_topology_clogging/submission/front_matter_audit.md",
            "papers/paper2_voxel_topology_clogging/submission/editor_response_map.json",
            "papers/paper2_voxel_topology_clogging/submission/editor_response_map.md",
            "papers/paper2_voxel_topology_clogging/submission/final_author_action_sheet.json",
            "papers/paper2_voxel_topology_clogging/submission/final_author_action_sheet.md",
            "papers/paper2_voxel_topology_clogging/submission/final_metadata_completion_packet.json",
            "papers/paper2_voxel_topology_clogging/submission/final_metadata_completion_packet.md",
            "papers/paper2_voxel_topology_clogging/submission/final_submission_action_list.json",
            "papers/paper2_voxel_topology_clogging/submission/final_submission_action_list.md",
            "papers/paper2_voxel_topology_clogging/submission/repository_upload_packet.json",
            "papers/paper2_voxel_topology_clogging/submission/repository_upload_packet.md",
            "papers/paper2_voxel_topology_clogging/submission/elsevier_portal_checklist.json",
            "papers/paper2_voxel_topology_clogging/submission/elsevier_portal_checklist.md",
            "papers/paper2_voxel_topology_clogging/submission/submission_decision_ledger.json",
            "papers/paper2_voxel_topology_clogging/submission/submission_decision_ledger.md",
            "papers/paper2_voxel_topology_clogging/submission/submission_decision_ledger.csv",
            "papers/paper2_voxel_topology_clogging/submission/journal_fallback_front_matter.json",
            "papers/paper2_voxel_topology_clogging/submission/journal_fallback_front_matter.md",
            "papers/paper2_voxel_topology_clogging/notes/paper2_manuscript_argument_map.md",
            "papers/paper2_voxel_topology_clogging/data/paper2_manuscript_argument_map.json",
            "papers/paper2_voxel_topology_clogging/tables/paper2_manuscript_argument_map.csv",
            "papers/paper2_voxel_topology_clogging/notes/paper2_benchmark_boundary_matrix.md",
            "papers/paper2_voxel_topology_clogging/data/paper2_benchmark_boundary_matrix.json",
            "papers/paper2_voxel_topology_clogging/tables/paper2_benchmark_boundary_matrix.csv",
            "papers/paper2_voxel_topology_clogging/notes/paper2_abstract_evidence_alignment.md",
            "papers/paper2_voxel_topology_clogging/data/paper2_abstract_evidence_alignment.json",
            "papers/paper2_voxel_topology_clogging/tables/paper2_abstract_evidence_alignment.csv",
            "papers/paper2_voxel_topology_clogging/submission/submission_form_packet.json",
            "papers/paper2_voxel_topology_clogging/submission/submission_form_packet.md",
            "papers/paper2_voxel_topology_clogging/submission/repository_deposit",
            "papers/paper2_voxel_topology_clogging/submission/data_code_deposit_manifest.md",
        ],
        "purpose": "Cover-letter draft, claim boundaries, repository-deposit metadata and pre-submission declaration checklists.",
    },
]


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output staging directory.")
    parser.add_argument("--force", action="store_true", help="Remove an existing output directory before staging.")
    return parser.parse_args()


def file_sha256(path: Path) -> str:
    """Compute the SHA256 checksum of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_path(src: Path, dst: Path) -> None:
    """Copy one file or directory into the submission staging directory."""
    if src.is_dir():
        for child in src.iterdir():
            copy_path(child, dst / child.name)
    else:
        if src.suffix in SKIP_STAGED_SUFFIXES:
            return
        if dst.parent.name == "supplementary" and src.name in {"supplementary_material.pdf", "supplementary_material.tex"}:
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            with src.open("rb") as source, dst.open("wb") as target:
                shutil.copyfileobj(source, target, length=1024 * 1024)
            shutil.copystat(src, dst)
        except OSError as exc:
            raise OSError(f"Failed to copy submission file {src} -> {dst}: {exc}") from exc


def staged_files(out_dir: Path) -> list[dict[str, object]]:
    """Return staged file metadata."""
    rows = []
    for path in sorted(p for p in out_dir.rglob("*") if p.is_file()):
        rel = path.relative_to(out_dir).as_posix()
        rows.append({"path": rel, "size_bytes": path.stat().st_size, "sha256": file_sha256(path)})
    return rows


def write_readme(out_dir: Path) -> None:
    """Write a README for the journal submission package."""
    lines = [
        "# Paper 2 Journal Submission Files",
        "",
        "This directory stages manuscript-facing files for journal submission. It is separate from the public data/code deposit archive.",
        "",
        "## Contents",
        "",
    ]
    for item in SUBMISSION_ITEMS:
        lines.append(f"- `{item['group']}`: {item['purpose']}")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This package contains manuscript, figure, supplementary and declaration files. It does not include raw DEM dump/restart files or the data/code deposit zip.",
            "",
            "Administrative metadata should be checked before submission: repository DOI/accession, competing interests, acknowledgements and corresponding-author metadata.",
        ]
    )
    (out_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def stage_submission_files(out_dir: Path, force: bool = False) -> dict[str, object]:
    """Stage journal-submission files and return manifest metadata."""
    if out_dir.exists():
        if not force:
            raise FileExistsError(f"Output directory exists; use --force to replace: {out_dir}")
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    groups = []
    missing = []
    for item in SUBMISSION_ITEMS:
        copied = []
        group_dir = out_dir / item["group"]
        for rel_path in item["paths"]:
            src = PROJECT_ROOT / rel_path
            if not src.exists():
                missing.append(rel_path)
                copied.append({"path": rel_path, "copied": False})
                continue
            dst = group_dir / src.name
            copy_path(src, dst)
            copied.append({"path": rel_path, "copied": True})
        groups.append({**item, "entries": copied})

    write_readme(out_dir)
    rows = staged_files(out_dir)
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "paper": "paper2_voxel_topology_clogging",
        "staging_directory": str(out_dir),
        "missing": missing,
        "groups": groups,
        "file_count": len(rows),
        "total_size_bytes": sum(int(row["size_bytes"]) for row in rows),
        "files": rows,
    }
    (out_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> int:
    """Run the journal-submission staging workflow."""
    args = parse_args()
    manifest = stage_submission_files(args.out, force=args.force)
    print(json.dumps({"out": str(args.out), "missing": manifest["missing"], "file_count": manifest["file_count"], "total_size_bytes": manifest["total_size_bytes"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
