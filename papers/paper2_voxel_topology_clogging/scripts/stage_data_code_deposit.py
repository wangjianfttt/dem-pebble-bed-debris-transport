#!/usr/bin/env python3
"""Stage a lightweight public data/code deposit for Paper 2."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
MANIFEST_PATH = PAPER_DIR / "data" / "data_code_deposit_manifest.json"
DEFAULT_OUT = PAPER_DIR / "deposit" / "paper2_lightweight_deposit"

EXCLUDE_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".DS_Store",
    "main.aux",
    "main.bbl",
    "main.blg",
    "main.fdb_latexmk",
    "main.fls",
    "main.log",
    "main.out",
    "main.spl",
    # Historical next-case generator can be CloudStorage-offloaded and is not
    # required to reproduce the submitted figures or source tables.
    "generate_explicit_localized_next_cases.py",
    # Remote-transfer helper can short-read from CloudStorage; returned
    # OpenFOAM evidence and ParaView renders are archived separately.
    "make_openfoam_remote_transfer_bundle.py",
    "crop_voxel_to_bed.py",
    "debris_li4sio4_1mm_10k_piston_axial_ug2_df005.yaml",
    # Author-facing confirmation drafts include the current deposit checksum.
    # Keeping them inside the deposit would create an unavoidable self-reference.
    "author_confirmation_request.json",
    "author_confirmation_request.md",
    "author_confirmation_email_zh_en.md",
    # Release-status and upload-packet files embed the archive checksum or size.
    # Including them inside the archive creates a self-referential freshness loop.
    "CURRENT_PROJECT_STATUS.md",
    "final_author_action_sheet.json",
    "final_author_action_sheet.md",
    "final_metadata_completion_packet.json",
    "final_metadata_completion_packet.md",
    "final_submission_gate.json",
    "final_submission_gate.md",
    "release_archive_consistency.json",
    "release_archive_consistency.md",
    "repository_upload_packet.json",
    "repository_upload_packet.md",
    # Packaging/freshness audit outputs are volatile submission-state files.
    # They are retained in the journal submission package, not the public
    # reproducibility deposit, to avoid making the deposit stale whenever an
    # audit is rerun.
    "elsevier_portal_visual_consistency_audit.json",
    "elsevier_portal_visual_consistency_audit.md",
    "journal_submission_freshness_audit.json",
    "journal_submission_freshness_audit.md",
    "elsevier_portal_freshness_audit.json",
    "elsevier_portal_freshness_audit.md",
    "data_code_deposit_freshness_audit.json",
    "data_code_deposit_freshness_audit.md",
    "supplementary_figure_reference_audit.json",
    "supplementary_figure_reference_audit.md",
    "supplementary_table_reference_audit.json",
    "supplementary_table_reference_audit.md",
    # Portal-packaging helpers are regenerated locally from submission metadata
    # and are not needed for reproducing the scientific figures or tables.
    "make_elsevier_portal_checklist.py",
    # The graphical-abstract source is a packaging helper; the exported
    # graphical abstract remains included as an always-included figure.
    "make_graphical_abstract.py",
}

EXCLUDE_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".dump",
    ".restart",
    ".vtk",
    ".vtp",
    ".pid",
    ".png",
    ".data",
    ".exit",
    ".liggghts",
    ".log",
    # Binary NumPy flow-domain arrays are archived through the flow-solver
    # handoff route. Keeping them out of the lightweight public deposit avoids
    # CloudStorage short-read stalls while preserving scripts and tabular data.
    ".npy",
}
COPY_CHUNK_BYTES = 256 * 1024
COPY_RETRIES = 5
ALWAYS_INCLUDE_NAMES = {"paper2_graphical_abstract.png"}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=MANIFEST_PATH, help="Path to data/code deposit manifest JSON.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output staging directory.")
    parser.add_argument("--force", action="store_true", help="Remove an existing output directory before staging.")
    return parser.parse_args()


def load_manifest(path: Path) -> dict[str, object]:
    """Load a deposit manifest from JSON."""
    if not path.exists():
        raise FileNotFoundError(f"Missing deposit manifest: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def should_skip(path: Path) -> bool:
    """Return whether a file or directory should be excluded from the lightweight deposit."""
    if path.name in ALWAYS_INCLUDE_NAMES:
        return False
    if path.name in EXCLUDE_NAMES or path.suffix in EXCLUDE_SUFFIXES:
        return True
    if path.name.startswith("restart"):
        return True
    return path.name.startswith("paper2_figS6_") or path.name.startswith("paper2_figS7_")


def copy_path(src: Path, dst: Path) -> None:
    """Copy one file or directory into the staging directory."""
    if should_skip(src):
        return
    if src.is_dir():
        for child in src.iterdir():
            if should_skip(child):
                continue
            copy_path(child, dst / child.name)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            copied = 0
            file_size = src.stat().st_size
            with dst.open("wb") as target:
                while copied < file_size:
                    for attempt in range(COPY_RETRIES):
                        try:
                            with src.open("rb") as source:
                                source.seek(copied)
                                chunk = source.read(min(COPY_CHUNK_BYTES, file_size - copied))
                            if not chunk and copied < file_size:
                                raise OSError(f"Short read at byte {copied} of {file_size}")
                            break
                        except OSError:
                            if attempt == COPY_RETRIES - 1:
                                raise
                            time.sleep(0.5 * (attempt + 1))
                    if not chunk:
                        raise OSError(f"Unexpected short read at byte {copied} of {file_size}")
                    target.write(chunk)
                    copied += len(chunk)
            shutil.copystat(src, dst)
        except OSError as exc:
            raise OSError(f"Failed to copy deposit file {src} -> {dst}: {exc}") from exc


def file_sha256(path: Path) -> str:
    """Compute the SHA256 checksum of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def staged_files(out_dir: Path) -> list[dict[str, object]]:
    """Return staged file metadata with relative paths, sizes and checksums."""
    rows = []
    for path in sorted(p for p in out_dir.rglob("*") if p.is_file()):
        rel = path.relative_to(out_dir).as_posix()
        rows.append({"path": rel, "size_bytes": path.stat().st_size, "sha256": file_sha256(path)})
    return rows


def write_readme(out_dir: Path, manifest: dict[str, object], rows: list[dict[str, object]]) -> None:
    """Write a README for the staged deposit."""
    required_groups = [g for g in manifest["groups"] if g["required_for_reproduction"]]
    optional_groups = [g for g in manifest["groups"] if not g["required_for_reproduction"]]
    raw_candidates = manifest.get("raw_archive_candidates", [])
    lines = [
        "# Paper 2 Lightweight Data and Code Deposit",
        "",
        "This directory stages the lightweight public deposit for the manuscript:",
        "",
        "`Separating breakthrough from pore-network clogging indicators in gas-driven fine-debris transport through Li4SiO4 pebble beds`",
        "",
        "## Scope",
        "",
        "The deposit contains processed source data, figure exports, figure-generation scripts, supplementary material, manuscript source, and shared analysis utilities. It does not claim to contain all large DEM restart/dump files.",
        "",
        "## Required Reproduction Groups",
        "",
    ]
    for group in required_groups:
        lines.append(f"- `{group['group']}`: {group['purpose']}")
    lines.extend(["", "## Optional Documentation Groups", ""])
    for group in optional_groups:
        lines.append(f"- `{group['group']}`: {group['purpose']}")
    lines.extend(["", "## Large Raw Data Boundary", ""])
    for item in raw_candidates:
        lines.append(f"- `{item['path']}`: {item['deposit_policy']}; {item['reason']}")
    lines.extend(
        [
            "",
            "## Reproducibility Notes",
            "",
            "- Use `MANIFEST.json` for staged file checksums and sizes.",
            "- Use `deposit_source_manifest.json` for the original project-relative deposit plan.",
            "- A public repository record has not yet been assigned; add the repository URL, persistent identifier and licence to the manuscript Data and Code availability statements before journal submission.",
            "",
            "## Staging Summary",
            "",
            f"- Files staged: {len(rows)}",
            f"- Total staged size: {sum(int(row['size_bytes']) for row in rows)} bytes",
        ]
    )
    (out_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def stage_deposit(manifest: dict[str, object], out_dir: Path, force: bool = False) -> dict[str, object]:
    """Stage the lightweight deposit and return summary metadata."""
    if out_dir.exists():
        if not force:
            raise FileExistsError(f"Output directory exists; use --force to replace: {out_dir}")
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    copied_groups = []
    for group in manifest["groups"]:
        copied_entries = []
        for entry in group["entries"]:
            src = PROJECT_ROOT / str(entry["path"])
            if not src.exists():
                copied_entries.append({**entry, "copied": False})
                continue
            copy_path(src, out_dir / str(entry["path"]))
            copied_entries.append({**entry, "copied": True})
        copied_groups.append({**group, "entries": copied_entries})

    source_manifest = out_dir / "deposit_source_manifest.json"
    source_manifest.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    rows = staged_files(out_dir)
    write_readme(out_dir, manifest, rows)
    rows = staged_files(out_dir)
    staged_manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "paper": manifest.get("paper"),
        "staging_directory": str(out_dir),
        "source_manifest": str(MANIFEST_PATH),
        "groups": copied_groups,
        "file_count": len(rows),
        "total_size_bytes": sum(int(row["size_bytes"]) for row in rows),
        "files": rows,
    }
    (out_dir / "MANIFEST.json").write_text(json.dumps(staged_manifest, indent=2), encoding="utf-8")
    return staged_manifest


def main() -> int:
    """Run the staging workflow."""
    args = parse_args()
    manifest = load_manifest(args.manifest)
    staged = stage_deposit(manifest, args.out, force=args.force)
    print(json.dumps({"out": str(args.out), "file_count": staged["file_count"], "total_size_bytes": staged["total_size_bytes"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
