# Paper 2 Final Submission Action List

- Decision: `ready_to_submit`
- Gate status: `ready_for_bounded_submission`
- Required open actions: 0
- Optional open actions: 0
- High-impact scientific actions pending: 0
- Missing upload files: `[]`
- Journal submission archive: `papers/paper2_voxel_topology_clogging/submission_package/archives/paper2_journal_submission_files.zip`
- Data/code archive: `papers/paper2_voxel_topology_clogging/deposit/archives/paper2_lightweight_deposit.zip`

## Required Actions

| ID | Section | Owner | Missing fields | Required output |
|---|---|---|---|---|
| A01_repository | repository | corresponding author or data manager | confirmation | repository name, DOI/accession, URL and license in submission_metadata.yaml |
| A02_competing_interests | competing_interests | all authors | confirmation | author-confirmed competing-interest statement |
| A03_acknowledgements | acknowledgements | corresponding author | confirmation | approved acknowledgement and computing-resource wording |
| A04_corresponding_author | corresponding_author | corresponding author | confirmation | name and email for the journal submission system |

## Optional Or Policy-Dependent Actions

| ID | Section | Owner | Missing fields | Required output |
|---|---|---|---|---|

## High-Impact Scientific Actions

| Item | Status | Progress | Action |
|---|---|---:|---|
| none | none | n/a | none |

## Exact Final Verification Commands

```bash
python3 papers/paper2_voxel_topology_clogging/scripts/audit_submission_metadata_gaps.py
python3 papers/paper2_voxel_topology_clogging/scripts/apply_submission_metadata.py --apply
cd papers/paper2_voxel_topology_clogging/latex && pdflatex -interaction=nonstopmode main.tex && bibtex main && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex
PYTHONPATH=. python3 papers/paper2_voxel_topology_clogging/scripts/audit_paper2_manuscript_readiness.py
python3 papers/paper2_voxel_topology_clogging/scripts/audit_final_submission_gate.py
python3 papers/paper2_voxel_topology_clogging/scripts/stage_journal_submission_files.py --force
python3 papers/paper2_voxel_topology_clogging/scripts/archive_journal_submission_files.py --force
```

## Submission Boundary

- Submit only after all required actions are complete and the final gate changes from `not_ready_for_submission`.
- Keep the manuscript bounded to DEM-based pre-clogging migration/filtering.
- Do not add pressure-calibrated safety-limit language unless new pressure evidence is actually available.
- Do not describe DEM-derived pore reconstructions as experimental CT.

Boundary: Administrative action list only; it does not change scientific evidence or manuscript scope.
