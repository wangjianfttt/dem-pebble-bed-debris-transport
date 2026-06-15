# Paper 2 Final Submission Action List

- Decision: `admin_actions_required`
- Gate status: `not_ready_for_submission`
- Required open actions: 5
- Optional open actions: 1
- High-impact scientific actions pending: 0
- Missing upload files: `[]`
- Journal submission archive: `papers/paper2_voxel_topology_clogging/submission_package/archives/paper2_journal_submission_files.zip`
- Data/code archive: `papers/paper2_voxel_topology_clogging/deposit/archives/paper2_lightweight_deposit.zip`

## Required Actions

| ID | Section | Owner | Missing fields | Required output |
|---|---|---|---|---|
| A01_repository | repository | corresponding author or data manager | name, identifier, url, license | repository name, DOI/accession, URL and license in submission_metadata.yaml |
| A02_funding | funding | corresponding author | statement | approved funding statement in submission_metadata.yaml |
| A03_competing_interests | competing_interests | all authors | confirmation | author-confirmed competing-interest statement |
| A04_acknowledgements | acknowledgements | corresponding author | statement | approved acknowledgement and computing-resource wording |
| A05_corresponding_author | corresponding_author | corresponding author | name, email | name and email for the journal submission system |

## Optional Or Policy-Dependent Actions

| ID | Section | Owner | Missing fields | Required output |
|---|---|---|---|---|
| A06_ai_tool_use | ai_tool_use | corresponding author or institution policy owner | statement | AI/tool-use disclosure if journal or institutional policy requires it |

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
