# Paper 2 Author Confirmation Request

This document collects only author- or repository-confirmed metadata. Do not fill uncertain items from memory.

## Manuscript

- Journal: Chemical Engineering Science
- Title: Separating breakthrough from pore-network clogging indicators in gas-driven fine-debris transport through Li4SiO4 pebble beds
- Authors: Jian Wang, Mingzong Liu, Mingzhun Lei, Qigang Wu, Kaisong Wang, Haishun Deng
- Current gate status: `not_ready_for_submission`
- Missing upload files: 0

## Ready Archives

| Item | Path | Size bytes | SHA256 |
|---|---|---:|---|
| data_code_archive | `papers/paper2_voxel_topology_clogging/deposit/archives/paper2_lightweight_deposit.zip` | 32636860 | `2a1b14bb852219a68b56967e2cca1e775bd9e49706b1749301b119c2ee76846a` |

Journal submission archive tracking:

- Archive path: `papers/paper2_voxel_topology_clogging/submission_package/archives/paper2_journal_submission_files.zip`
- Current SHA source: `papers/paper2_voxel_topology_clogging/submission/release_archive_consistency.md`
- Boundary: The journal-submission archive SHA is intentionally not embedded here because this request is staged inside that archive. Use CURRENT_PROJECT_STATUS.md or release_archive_consistency.md after final archiving for the current journal-package SHA.

## Required Confirmations

Required open items: 1

### corresponding_author

- Status: `open`
- Needed: name, email
- Why: Required for the journal submission system and cover-letter metadata.

Author-confirmed wording/value:

```text
TBC
```

Please confirm:

```yaml
name: TBC
email: TBC
orcid: optional
```

## Optional/Policy-Dependent Confirmation

Optional open items: 1

### ai_tool_use

- Status: `optional_open`
- Needed: statement
- Why: Required if journal or institutional policy asks for AI/tool-use disclosure.

Author-confirmed wording/value:

```text
TBC
```

## Scientific Scope Warnings To Preserve

These are not administrative blockers, but the wording should remain bounded during submission.

| Item | Status | Gate interpretation |
|---|---|---|
| critical_clogging_transition | not_supported_current_scope | acceptable only if manuscript remains bounded to pre-clogging migration/retention scope |

## After Confirmation

1. Fill `papers/paper2_voxel_topology_clogging/submission/submission_metadata.yaml`.
2. Set each confirmed section to `confirmed: true`.
3. Run:

```bash
python3 papers/paper2_voxel_topology_clogging/scripts/apply_submission_metadata.py --apply
PYTHONPATH=. python3 papers/paper2_voxel_topology_clogging/scripts/audit_paper2_manuscript_readiness.py
python3 papers/paper2_voxel_topology_clogging/scripts/audit_final_submission_gate.py
```
