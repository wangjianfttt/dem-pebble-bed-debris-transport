# Paper 2 Author Confirmation Sheet

Use this sheet before journal submission. It is a control document: do not mark an item complete unless the corresponding author has author-approved wording or metadata.

## Submission Metadata To Confirm

| Section | Status | Missing fields | Why it matters |
|---|---|---|---|
| repository | complete | none | Required for Data availability and Code availability. |
| funding | complete | none | Required for the manuscript Funding section and journal metadata. |
| competing_interests | complete | none | Required by the journal and must be confirmed by all authors. |
| acknowledgements | complete | none | Required to avoid unapproved computing-resource or collaborator wording. |
| corresponding_author | open | name, email | Required for the journal submission system and cover-letter metadata. |
| ai_tool_use | optional_open | statement | Required if journal or institutional policy asks for AI/tool-use disclosure. |

## Author Approval Checks

| Item | Confirmation owner | Confirmed? | Notes |
|---|---|---|---|
| Final title | All authors | no | Separating breakthrough from pore-network clogging indicators in gas-driven fine-debris transport through Li4SiO4 pebble beds |
| Author order | All authors | no | Jian Wang; Mingzong Liu; Mingzhun Lei; Qigang Wu; Kaisong Wang; Haishun Deng |
| Affiliations | Each author | no | Check spelling and institution names in LaTeX front matter. |
| Corresponding author | Corresponding author | no | Fill name and email in submission_metadata.yaml. |
| Scientific scope | Corresponding author | no | Confirm bounded DEM-based pre-clogging migration/retention framing. |
| Voxel wording | Corresponding author | no | Confirm wording stays as DEM-derived voxel reconstruction, not experimental CT. |
| Data/code deposit | Corresponding author | no | Upload archive, obtain DOI/accession, confirm license. |
| Funding | Corresponding author | no | Insert confirmed grant or approved no-funding wording. |
| Competing interests | All authors | no | Each author confirms the statement. |
| Acknowledgements | Corresponding author | no | Confirm computing resources, collaborators and institutional wording. |
| AI/tool-use disclosure | Corresponding author | no | Add only if required by journal or institution policy. |

## Exact Workflow After Confirmation

1. Edit `papers/paper2_voxel_topology_clogging/submission/submission_metadata.yaml`.
2. Set each confirmed required section to `confirmed: true` and replace all `TBC` values.
3. Run `python3 papers/paper2_voxel_topology_clogging/scripts/audit_submission_metadata_gaps.py`.
4. Run `python3 papers/paper2_voxel_topology_clogging/scripts/apply_submission_metadata.py --apply`.
5. Recompile the LaTeX manuscript and rerun the final submission gate.

## Current Decision

- Required metadata sections still open: `1`
- Optional metadata sections still open: `1`
- Ready to apply metadata: `False`
