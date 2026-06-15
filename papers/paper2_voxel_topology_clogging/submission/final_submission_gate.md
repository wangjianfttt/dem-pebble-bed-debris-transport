# Paper 2 Final Submission Gate

Gate status: `not_ready_for_submission`

Files are staged and repeat-seed production has completed, but author/repository confirmations remain before journal submission.

## Audit Summary

- Manuscript readiness: `{"needs_confirmation": 1, "not_required_for_preclogging_scope": 1, "not_supported_current_scope": 1, "supported": 139}`
- Reviewer risks: `{"bounded": 6, "needs_confirmation": 1, "resolved": 1, "unresolved": 3}`
- Submission metadata gaps: `{"optional_open": 1, "required_open": 1}`

## Upload-Ready Files

| Item | Exists | Size | Path |
|---|---:|---:|---|
| journal_submission_archive | True | 17560411 | `papers/paper2_voxel_topology_clogging/submission_package/archives/paper2_journal_submission_files.zip` |
| journal_submission_archive_sha256 | True | 102 | `papers/paper2_voxel_topology_clogging/submission_package/archives/paper2_journal_submission_files.zip.sha256` |
| journal_submission_archive_summary | True | 974 | `papers/paper2_voxel_topology_clogging/submission_package/archives/paper2_journal_submission_files_archive_summary.json` |
| journal_submission_manifest | True | 50514 | `papers/paper2_voxel_topology_clogging/submission_package/journal_submission_files/MANIFEST.json` |
| journal_submission_readme | True | 918 | `papers/paper2_voxel_topology_clogging/submission_package/journal_submission_files/README.md` |
| data_code_archive | True | 32636860 | `papers/paper2_voxel_topology_clogging/deposit/archives/paper2_lightweight_deposit.zip` |
| data_code_archive_sha256 | True | 97 | `papers/paper2_voxel_topology_clogging/deposit/archives/paper2_lightweight_deposit.zip.sha256` |
| data_code_archive_summary | True | 933 | `papers/paper2_voxel_topology_clogging/deposit/archives/paper2_lightweight_deposit_archive_summary.json` |

## Required Before Submission

| Item | Action | Evidence |
|---|---|---|
| metadata_corresponding_author | Confirm corresponding-author name and email for the journal submission system. Missing: name, email. | `papers/paper2_voxel_topology_clogging/submission/submission_metadata_gaps.json` |

## Scientific Scope Warnings

| Item | Status | Interpretation | Evidence |
|---|---|---|---|
| critical_clogging_transition | not_supported_current_scope | acceptable only if manuscript remains bounded to pre-clogging migration/retention scope | `Current loading scan has three single-seed states and no measurable connectivity loss.` |

## High-Impact Scientific Actions

| Item | Status | Progress | Action | Interpretation |
|---|---|---:|---|---|
| none | none | n/a | none | none |

## Unresolved Reviewer Risks

| Risk | Mitigation |
|---|---|
| R01: Pressure-free clogging index could be misread as a pressure-calibrated safety criterion. | Keep the current boundary language; upgrade only after CFD/OpenLB/OpenFOAM or measured pressure-gradient data are added. |
| R02: Critical clogging transition is not demonstrated by the current data. | Do not claim critical transition in title, abstract, or conclusions unless new localized/high-loading production runs generate connectivity loss or pressure increase. |
| R09: Title and framing could sound like an experiment or a critical-clogging paper. | Do not reintroduce experiment, CT, or critical transition wording unless the evidence changes. |

## Practical Decision

- The manuscript files and public data/code archive are prepared.
- The paper should be submitted only as a bounded DEM-based pre-clogging migration/retention study.
- Do not submit as a pressure-calibrated critical-clogging or safety-limit paper.
- Final submission still requires author/repository confirmations listed above.
