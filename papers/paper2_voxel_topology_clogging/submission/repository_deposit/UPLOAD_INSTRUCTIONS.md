# Repository Upload Instructions

These notes prepare the Paper 2 lightweight data/code deposit for Zenodo, OSF, Figshare, or a GitHub release linked to an archival DOI.

## Upload Package

Upload:

- `papers/paper2_voxel_topology_clogging/deposit/archives/paper2_lightweight_deposit.zip`
- `papers/paper2_voxel_topology_clogging/deposit/archives/paper2_lightweight_deposit.zip.sha256`

Optional, if repository size limits and policy allow:

- `cases/clogging_scan/paper2_localized_release`
- `data/raw`

Large raw DEM dump/restart files may also be deposited as a separate raw-data record and cross-linked to the lightweight deposit.

## Metadata Fields

Use `repository_metadata.yaml` as the source for:

- title;
- creators;
- description;
- keywords;
- license;
- related identifiers.

Use `CITATION.cff` for citation metadata when the repository supports it.

## Values That Must Be Confirmed

Do not submit the repository record until these values are final:

- repository DOI/accession;
- license;
- manuscript DOI, if already available;
- funding statement;
- competing-interest confirmation;
- acknowledgement wording;
- corresponding-author metadata.

## After DOI Assignment

1. Insert the repository DOI/accession into `submission_metadata.yaml`.
2. Set the repository section to `confirmed: true`.
3. Rerun:

```bash
python3 papers/paper2_voxel_topology_clogging/scripts/audit_submission_metadata_gaps.py
python3 papers/paper2_voxel_topology_clogging/scripts/apply_submission_metadata.py --apply
cd papers/paper2_voxel_topology_clogging/latex && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
cd ../../..
PYTHONPATH=. python3 papers/paper2_voxel_topology_clogging/scripts/audit_paper2_manuscript_readiness.py
python3 papers/paper2_voxel_topology_clogging/scripts/audit_latex_citations.py
python3 papers/paper2_voxel_topology_clogging/scripts/audit_final_submission_gate.py
python3 papers/paper2_voxel_topology_clogging/scripts/stage_data_code_deposit.py --force
python3 papers/paper2_voxel_topology_clogging/scripts/archive_data_code_deposit.py --force
python3 papers/paper2_voxel_topology_clogging/scripts/stage_journal_submission_files.py --force
python3 papers/paper2_voxel_topology_clogging/scripts/archive_journal_submission_files.py --force
python3 papers/paper2_voxel_topology_clogging/scripts/stage_elsevier_portal_upload_files.py --force
python3 papers/paper2_voxel_topology_clogging/scripts/archive_elsevier_portal_upload_files.py --force
python3 papers/paper2_voxel_topology_clogging/scripts/audit_release_archive_consistency.py
python3 papers/paper2_voxel_topology_clogging/scripts/make_current_project_status.py
```

The `cd ../../..` step returns from the LaTeX directory to the repository root before running project-level scripts.

## Boundary Statement

This deposit supports a bounded DEM-based pre-clogging migration and retention study. It should not be described as experimental CT validation, a pressure-calibrated safety limit, or a universal critical clogging transition data set.
