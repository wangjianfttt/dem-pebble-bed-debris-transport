#!/usr/bin/env python3
"""Create an archive for the minimal Paper 2 Elsevier portal upload package."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from archive_journal_submission_files import create_zip_archive  # noqa: E402

DEFAULT_STAGING_DIR = PAPER_DIR / "submission_package" / "elsevier_portal_upload_files"
DEFAULT_ARCHIVE_DIR = PAPER_DIR / "submission_package" / "archives"
ARCHIVE_STEM = "paper2_elsevier_portal_upload_files"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staging-dir", type=Path, default=DEFAULT_STAGING_DIR, help="Directory produced by stage_elsevier_portal_upload_files.py.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_ARCHIVE_DIR, help="Directory for archive outputs.")
    parser.add_argument("--force", action="store_true", help="Replace an existing archive.")
    return parser.parse_args()


def main() -> int:
    """Run the portal-upload archive workflow."""
    args = parse_args()
    archive_path = args.out_dir / f"{ARCHIVE_STEM}.zip"
    summary = create_zip_archive(args.staging_dir, archive_path, force=args.force)
    summary["purpose"] = "Minimal Elsevier portal-facing upload archive for Paper 2."
    summary_path = args.out_dir / f"{ARCHIVE_STEM}_archive_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({**summary, "summary_path": str(summary_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
