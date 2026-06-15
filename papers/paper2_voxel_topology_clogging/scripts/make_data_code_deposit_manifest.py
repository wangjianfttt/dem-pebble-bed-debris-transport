#!/usr/bin/env python3
"""Create a data/code deposit manifest for Paper 2."""

from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
OUT_JSON = PAPER_DIR / "data" / "data_code_deposit_manifest.json"
OUT_MD = PAPER_DIR / "submission" / "data_code_deposit_manifest.md"
FIGURE_PROVENANCE = PAPER_DIR / "data" / "figure_provenance_manifest.json"


DEPOSIT_GROUPS = [
    {
        "group": "manuscript",
        "include": [
            "papers/paper2_voxel_topology_clogging/latex/main.tex",
            "papers/paper2_voxel_topology_clogging/latex/main.pdf",
            "papers/paper2_voxel_topology_clogging/references/paper2_references.bib",
        ],
        "purpose": "Manuscript source, compiled preview and bibliography.",
        "required_for_reproduction": True,
    },
    {
        "group": "source_data",
        "include": [
            "papers/paper2_voxel_topology_clogging/data",
            "papers/paper2_voxel_topology_clogging/tables",
            "papers/paper2_voxel_topology_clogging/flow_domains",
        ],
        "purpose": "Processed source data, cropped pore-domain inputs, audits and quantitative claim tables.",
        "required_for_reproduction": True,
    },
    {
        "group": "figure_exports",
        "include": ["papers/paper2_voxel_topology_clogging/figures"],
        "purpose": "Figure exports for main and supplementary figures; the lightweight archive stages PDF/SVG exports and omits PNG previews when CloudStorage raster files are not reliably readable.",
        "required_for_reproduction": True,
    },
    {
        "group": "paper_scripts",
        "include": [],
        "purpose": "Provenance-listed figure/data scripts plus deposit/provenance manifest generators; internal submission-packaging helpers are excluded from the lightweight public deposit.",
        "required_for_reproduction": True,
    },
    {
        "group": "selected_dem_inputs",
        "include": ["cases/clogging_scan/paper1_velocity_scan_frozen_repeat"],
        "purpose": "Selected small DEM input decks for formal near-threshold repeat-seed evidence generation; generated dumps/restarts should be archived separately after runs.",
        "required_for_reproduction": False,
    },
    {
        "group": "supplementary_material",
        "include": ["papers/paper2_voxel_topology_clogging/supplementary"],
        "purpose": "Supplementary tables, supplementary-figure catalogue and OpenFOAM model/mesh pressure-note boundary.",
        "required_for_reproduction": True,
    },
    {
        "group": "submission_notes",
        "include": [
            "papers/paper2_voxel_topology_clogging/CURRENT_PROJECT_STATUS.md",
            "papers/paper2_voxel_topology_clogging/submission",
            "papers/paper2_voxel_topology_clogging/remote_bundle/REMOTE_RUN_README.md",
            "papers/paper2_voxel_topology_clogging/notes/figure_provenance_manifest.md",
            "papers/paper2_voxel_topology_clogging/notes/paper2_manuscript_readiness.md",
            "papers/paper2_voxel_topology_clogging/notes/reviewer_risk_matrix.md",
            "papers/paper2_voxel_topology_clogging/notes/paper2_dimensionless_mechanism_map.md",
            "papers/paper2_voxel_topology_clogging/notes/paper2_high_impact_evidence_upgrade_plan.md",
        ],
        "purpose": "Claim boundaries, submission checklist, cover-letter draft, repository deposit metadata and evidence audits.",
        "required_for_reproduction": False,
    },
    {
        "group": "shared_code",
        "include": ["src"],
        "purpose": "Shared DEM, transport, voxel, topology and model utilities used by the paper-specific scripts.",
        "required_for_reproduction": True,
    },
]

RAW_ARCHIVE_CANDIDATES = [
    {
        "path": "cases/clogging_scan/paper2_localized_release",
        "reason": "Contains LIGGGHTS inputs, logs, dumps and restart files for localized-release production and diagnostic jobs.",
        "deposit_policy": "optional_raw_archive_large_files",
    },
    {
        "path": "data/raw",
        "reason": "Project-level raw DEM dump location for smaller baseline or synthetic inputs.",
        "deposit_policy": "include_if_size_allows_or_archive_separately",
    },
]


def path_size_bytes(path: Path) -> int:
    """Return total size in bytes for a file or directory."""
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    return sum(file.stat().st_size for file in path.rglob("*") if file.is_file())


def rel(path: Path) -> str:
    """Return a project-relative path string."""
    return str(path.relative_to(PROJECT_ROOT))


def describe_path(path_text: str) -> dict[str, object]:
    """Describe one project-relative deposit path."""
    path = PROJECT_ROOT / path_text
    return {
        "path": path_text,
        "exists": path.exists(),
        "is_dir": path.is_dir(),
        "size_bytes": path_size_bytes(path),
    }


def reproducibility_script_paths() -> list[str]:
    """Return paper-specific scripts that are directly tied to figure provenance."""
    scripts = {
        "papers/paper2_voxel_topology_clogging/scripts/make_data_code_deposit_manifest.py",
        "papers/paper2_voxel_topology_clogging/scripts/stage_data_code_deposit.py",
        "papers/paper2_voxel_topology_clogging/scripts/archive_data_code_deposit.py",
        "papers/paper2_voxel_topology_clogging/scripts/make_figure_provenance_manifest.py",
    }
    if FIGURE_PROVENANCE.exists():
        records = json.loads(FIGURE_PROVENANCE.read_text(encoding="utf-8"))
        if isinstance(records, list):
            for record in records:
                if not isinstance(record, dict):
                    continue
                script = record.get("script")
                if isinstance(script, str) and script:
                    scripts.add(script)
                for key in ("scripts", "script_dependencies"):
                    values = record.get(key)
                    if isinstance(values, list):
                        scripts.update(str(value) for value in values if value)
    return sorted(path for path in scripts if (PROJECT_ROOT / path).exists())


def build_manifest() -> dict[str, object]:
    """Build the data/code deposit manifest."""
    groups = []
    for group in DEPOSIT_GROUPS:
        include = reproducibility_script_paths() if group["group"] == "paper_scripts" else group["include"]
        entries = [describe_path(path_text) for path_text in include]
        groups.append(
            {
                **group,
                "include": include,
                "entries": entries,
                "all_entries_exist": all(bool(entry["exists"]) for entry in entries),
                "total_size_bytes": sum(int(entry["size_bytes"]) for entry in entries),
            }
        )
    raw_entries = []
    for item in RAW_ARCHIVE_CANDIDATES:
        entry = describe_path(str(item["path"]))
        raw_entries.append({**item, **entry})
    return {
        "paper": "paper2_voxel_topology_clogging",
        "recommended_repository": "Zenodo/OSF/GitHub release; DOI or accession not yet assigned",
        "groups": groups,
        "raw_archive_candidates": raw_entries,
        "deposit_boundary": (
            "The lightweight deposit should include processed source data, scripts, figures, supplementary material and manuscript source. "
            "Large DEM dump/restart files can be archived separately when repository size limits require it."
        ),
    }


def format_size(num_bytes: int) -> str:
    """Format a byte count as a compact human-readable string."""
    value = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024.0 or unit == "GB":
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} GB"


def write_markdown(manifest: dict[str, object]) -> None:
    """Write a Markdown data/code deposit manifest."""
    lines = [
        "# Paper 2 Data and Code Deposit Manifest",
        "",
        "This manifest identifies the files recommended for a public data/code deposit supporting the Paper 2 manuscript.",
        "",
        f"Recommended repository: {manifest['recommended_repository']}",
        "",
        "## Lightweight Deposit",
        "",
        "| Group | Required | Size | Purpose | Paths |",
        "|---|---|---:|---|---|",
    ]
    for group in manifest["groups"]:
        paths = "<br>".join(f"`{entry['path']}`" for entry in group["entries"])
        lines.append(
            "| {group} | {required} | {size} | {purpose} | {paths} |".format(
                group=group["group"],
                required="yes" if group["required_for_reproduction"] else "no",
                size=format_size(int(group["total_size_bytes"])),
                purpose=group["purpose"],
                paths=paths,
            )
        )
    lines.extend(
        [
            "",
            "## Optional Raw Archive",
            "",
            "| Path | Size | Policy | Reason |",
            "|---|---:|---|---|",
        ]
    )
    for entry in manifest["raw_archive_candidates"]:
        lines.append(
            "| `{path}` | {size} | {policy} | {reason} |".format(
                path=entry["path"],
                size=format_size(int(entry["size_bytes"])),
                policy=entry["deposit_policy"],
                reason=entry["reason"],
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            str(manifest["deposit_boundary"]),
            "",
            "A DOI/accession has not yet been assigned. Insert the final repository DOI/accession in the manuscript Data availability statement before submission.",
        ]
    )
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    """Generate JSON and Markdown data/code deposit manifests."""
    manifest = build_manifest()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    write_markdown(manifest)
    missing_groups = [group["group"] for group in manifest["groups"] if not group["all_entries_exist"]]
    print(OUT_JSON)
    print(OUT_MD)
    print(json.dumps({"groups": len(manifest["groups"]), "missing_groups": missing_groups}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
