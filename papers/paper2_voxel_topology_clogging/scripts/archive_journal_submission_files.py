#!/usr/bin/env python3
"""Create a compressed archive for staged Paper 2 journal-submission files."""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
DEFAULT_STAGING_DIR = PAPER_DIR / "submission_package" / "journal_submission_files"
DEFAULT_ARCHIVE_DIR = PAPER_DIR / "submission_package" / "archives"
ARCHIVE_STEM = "paper2_journal_submission_files"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staging-dir", type=Path, default=DEFAULT_STAGING_DIR, help="Directory produced by stage_journal_submission_files.py.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_ARCHIVE_DIR, help="Directory for archive outputs.")
    parser.add_argument("--force", action="store_true", help="Replace an existing archive.")
    return parser.parse_args()


def file_sha256(path: Path) -> str:
    """Compute the SHA256 checksum of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_staged_files(staging_dir: Path) -> list[Path]:
    """Return all staged files in stable archive order."""
    if not staging_dir.exists():
        raise FileNotFoundError(f"Missing staging directory: {staging_dir}")
    files = sorted(path for path in staging_dir.rglob("*") if path.is_file())
    if not files:
        raise ValueError(f"No files found in staging directory: {staging_dir}")
    return files


def create_zip_archive(staging_dir: Path, archive_path: Path, force: bool = False) -> dict[str, object]:
    """Create a zip archive from staged journal-submission files."""
    if archive_path.exists() and not force:
        raise FileExistsError(f"Archive exists; use --force to replace: {archive_path}")
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    if archive_path.exists():
        archive_path.unlink()

    files = iter_staged_files(staging_dir)
    root_name = staging_dir.name
    with zipfile.ZipFile(archive_path, mode="w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in files:
            arcname = Path(root_name) / path.relative_to(staging_dir)
            zf.write(path, arcname.as_posix())

    checksum = file_sha256(archive_path)
    sha_path = archive_path.with_suffix(archive_path.suffix + ".sha256")
    sha_path.write_text(f"{checksum}  {archive_path.name}\n", encoding="utf-8")
    return {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "staging_dir": str(staging_dir),
        "archive_path": str(archive_path),
        "sha256_path": str(sha_path),
        "archive_size_bytes": archive_path.stat().st_size,
        "sha256": checksum,
        "staged_file_count": len(files),
    }


def main() -> int:
    """Run the journal-submission archive workflow."""
    args = parse_args()
    archive_path = args.out_dir / f"{ARCHIVE_STEM}.zip"
    summary = create_zip_archive(args.staging_dir, archive_path, force=args.force)
    summary_path = args.out_dir / f"{ARCHIVE_STEM}_archive_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({**summary, "summary_path": str(summary_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
