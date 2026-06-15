# Paper 2 Final Author Action Sheet

- Decision: `author_metadata_required_before_submission`
- Journal: Chemical Engineering Science
- Title: Separating breakthrough from pore-network clogging indicators in gas-driven fine-debris transport through Li4SiO4 pebble beds
- Gate status: `not_ready_for_submission`
- Missing upload files: `[]`
- Required open actions: 5
- Optional/policy-dependent actions: 1
- Note: the final gate currently reports the hard metadata blockers, while this sheet lists the broader author-confirmation and repository-deposit fields that should be resolved before actual journal submission.

## Ready Files

| Item | Path | Size bytes | SHA256 |
|---|---|---:|---|
| Data/code archive | `papers/paper2_voxel_topology_clogging/deposit/archives/paper2_lightweight_deposit.zip` | 32636860 | `2a1b14bb852219a68b56967e2cca1e775bd9e49706b1749301b119c2ee76846a` |

Journal submission archive tracking:

- Archive path: `papers/paper2_voxel_topology_clogging/submission_package/archives/paper2_journal_submission_files.zip`
- Current SHA source: `papers/paper2_voxel_topology_clogging/submission/release_archive_consistency.md`
- Boundary: The journal-submission archive SHA is intentionally not embedded in this sheet because the sheet is staged inside that archive. Use CURRENT_PROJECT_STATUS.md or release_archive_consistency.md after final archiving for the current journal-package SHA.

## Required Author Inputs

| ID | Section | Owner | Missing fields | Required output |
|---|---|---|---|---|
| A01_repository | repository | corresponding author or data manager | name, identifier, url, license | repository name, DOI/accession, URL and license in submission_metadata.yaml |
| A02_funding | funding | corresponding author | statement | approved funding statement in submission_metadata.yaml |
| A03_competing_interests | competing_interests | all authors | confirmation | author-confirmed competing-interest statement |
| A04_acknowledgements | acknowledgements | corresponding author | statement | approved acknowledgement and computing-resource wording |
| A05_corresponding_author | corresponding_author | corresponding author | name, email | name and email for the journal submission system |

## Optional Or Policy-Dependent Inputs

| ID | Section | Owner | Required output |
|---|---|---|---|
| A06_ai_tool_use | ai_tool_use | corresponding author or institution policy owner | AI/tool-use disclosure if journal or institutional policy requires it |

## Repository Upload

- Upload packet: `papers/paper2_voxel_topology_clogging/submission/repository_upload_packet.md`
- Zenodo metadata draft: `papers/paper2_voxel_topology_clogging/submission/repository_deposit/zenodo_metadata_draft.json`
- Submission metadata YAML to fill after DOI assignment: `papers/paper2_voxel_topology_clogging/submission/submission_metadata.yaml`

License options to confirm:

- CC-BY-4.0 for data/figures if authors want a permissive attribution data license
- MIT or BSD-3-Clause for reusable code if a separate software license is desired
- A single repository-level license chosen by the corresponding author or institution

## Post-Confirmation Commands

```bash
python3 papers/paper2_voxel_topology_clogging/scripts/audit_submission_metadata_gaps.py
python3 papers/paper2_voxel_topology_clogging/scripts/apply_submission_metadata.py --apply
cd papers/paper2_voxel_topology_clogging/latex && latexmk -pdf -interaction=nonstopmode main.tex
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

## Non-Negotiable Boundaries

- Do not call DEM-derived voxel fields experimental CT.
- Do not claim a pressure-calibrated safety limit.
- Do not claim a universal critical clogging transition.
- Do not claim a public repository DOI/accession until the repository record exists.
