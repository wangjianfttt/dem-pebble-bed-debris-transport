# Paper 2 Final Metadata Completion Packet

- Decision: `metadata_completion_required_before_submission`
- Journal: Chemical Engineering Science
- Title: Separating breakthrough from pore-network clogging indicators in gas-driven fine-debris transport through Li4SiO4 pebble beds
- Required open sections: 0
- Optional/policy-dependent open sections: 0

## Ready Archives

| Archive | Path | Size bytes | SHA256 |
|---|---|---:|---|
| data_code_deposit | `papers/paper2_voxel_topology_clogging/deposit/archives/paper2_lightweight_deposit.zip` | 32636860 | `2a1b14bb852219a68b56967e2cca1e775bd9e49706b1749301b119c2ee76846a` |

## Journal Submission Archive Tracking

- Archive path: `papers/paper2_voxel_topology_clogging/submission_package/archives/paper2_journal_submission_files.zip`
- Current SHA source after final archiving: `papers/paper2_voxel_topology_clogging/submission/release_archive_consistency.md`
- Summary JSON: `papers/paper2_voxel_topology_clogging/submission_package/archives/paper2_journal_submission_files_archive_summary.json`
- Boundary: The journal-submission archive SHA is intentionally not embedded in this packet, because the packet itself is staged inside that archive. Use CURRENT_PROJECT_STATUS.md or release_archive_consistency.md after final archiving for the current journal-package SHA.

## Confirmation Checklist

| Section | Required | Confirmed | Missing fields | Why |
|---|---|---|---|---|
| repository | `True` | `True` | none | Required for Data availability and Code availability. |
| competing_interests | `True` | `True` | none | Required by the journal and must be confirmed by all authors. |
| acknowledgements | `True` | `True` | none | Required to avoid unapproved computing-resource or collaborator wording. |
| corresponding_author | `True` | `True` | none | Required for the journal submission system and cover-letter metadata. |

## Fill This YAML Into submission_metadata.yaml

```yaml
repository:
  confirmed: true
  name: <repository record name>
  identifier: <repository DOI/accession>
  url: <repository landing-page URL>
  license: <confirmed license>
competing_interests:
  confirmed: true
  statement: The authors declare that they have no known competing financial interests
    or personal relationships that could have appeared to influence the work reported
    in this paper.
acknowledgements:
  confirmed: true
  statement: <author-approved acknowledgements and computing-resource wording>
corresponding_author:
  confirmed: true
  name: <corresponding author name>
  email: <corresponding author email>
```

## Repository Upload

- Upload packet: `papers/paper2_voxel_topology_clogging/submission/repository_upload_packet.md`
- Zenodo metadata draft: `papers/paper2_voxel_topology_clogging/submission/repository_deposit/zenodo_metadata_draft.json`

License options to confirm:
- CC-BY-4.0 for data/figures if authors want a permissive attribution data license
- MIT or BSD-3-Clause for reusable code if a separate software license is desired
- A single repository-level license chosen by the corresponding author or institution

## Copy-Ready Journal Fields

### Keywords
- ceramic breeder pebble bed
- Li4SiO4
- discrete element method
- DEM-derived pore reconstruction
- fine debris
- structural screening index
- breakthrough curve

### Highlights
- DEM resolves fines transport in a stiff gas-purged Li4SiO4 pebble bed.
- Topology metrics separate breakthrough from pore-network degradation in the sampled cases.
- Drive, source release and inventory activate different debris observables.
- Discrete coverage mapping bounds evidence without phase-map claims.
- Cropped-domain pressure checks support a bounded pre-clogging interpretation.

### CRediT Statement

Jian Wang: Conceptualization, Methodology, Software, Investigation, Formal analysis, Visualization, Writing - original draft. Mingzhun Lei: Methodology, Project administration, Writing - review and editing. Haoxi Wang: Methodology, Writing - review and editing. Zhiyuan Liu: Application context, Methodology, Writing - review and editing. Haishun Deng: Application context, Validation planning, Writing - review and editing. Wei Wen: Data curation, Visualization, Writing - review and editing. Gang Shen: Supervision, Project administration, Writing - review and editing.

### Current Data Availability Wording

The processed data and figure source tables supporting the quantitative claims are available in the public GitHub-Zenodo repository https://github.com/wangjianfttt/dem-pebble-bed-debris-transport, archived at DOI 10.5281/zenodo.20699272. Raw DEM dump and restart files are not included in the lightweight public deposit because of their size and are available from the corresponding author upon reasonable request.

### Current Code Availability Wording

Paper-specific scripts for source-data preparation and figure generation are available in the same GitHub-Zenodo repository under papers/paper2_voxel_topology_clogging/scripts. Shared DEM, voxel, topology and transport utilities are provided under src/. The archived repository version is available at DOI 10.5281/zenodo.20699272.

### Current Competing-Interest Wording

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

## Post-Confirmation Commands

```bash
python3 papers/paper2_voxel_topology_clogging/scripts/audit_submission_metadata_gaps.py
python3 papers/paper2_voxel_topology_clogging/scripts/apply_submission_metadata.py --apply
cd papers/paper2_voxel_topology_clogging/latex && latexmk -pdf -interaction=nonstopmode main.tex
PYTHONPATH=. python3 papers/paper2_voxel_topology_clogging/scripts/audit_paper2_manuscript_readiness.py
python3 papers/paper2_voxel_topology_clogging/scripts/audit_final_submission_gate.py
python3 papers/paper2_voxel_topology_clogging/scripts/stage_journal_submission_files.py --force
python3 papers/paper2_voxel_topology_clogging/scripts/archive_journal_submission_files.py --force
```

## Boundaries

- Do not claim a public repository DOI/accession until it exists.
- Do not call DEM-derived voxel fields experimental CT.
- Do not claim pressure-calibrated Ib or a universal critical-clogging transition.
