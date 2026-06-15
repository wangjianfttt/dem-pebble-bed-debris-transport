# Paper 2 Repository Upload Packet

- Decision: `ready_for_repository_upload_packet`
- Repository DOI assigned: `True`
- Metadata source: `papers/paper2_voxel_topology_clogging/submission/repository_deposit/repository_metadata.yaml`
- Citation source: `papers/paper2_voxel_topology_clogging/submission/repository_deposit/CITATION.cff`
- Upload instructions: `papers/paper2_voxel_topology_clogging/submission/repository_deposit/UPLOAD_INSTRUCTIONS.md`
- Zenodo metadata draft: `papers/paper2_voxel_topology_clogging/submission/repository_deposit/zenodo_metadata_draft.json`

## Upload Files

| Role | Path | Size bytes | SHA256 |
|---|---|---:|---|
| data_code_archive | `papers/paper2_voxel_topology_clogging/deposit/archives/paper2_lightweight_deposit.zip` | 32636860 | `2a1b14bb852219a68b56967e2cca1e775bd9e49706b1749301b119c2ee76846a` |
| data_code_archive_sha256 | `papers/paper2_voxel_topology_clogging/deposit/archives/paper2_lightweight_deposit.zip.sha256` | 97 | `see file` |

## Repository Metadata Draft

- Title: Separating breakthrough from pore-network clogging indicators in gas-driven fine-debris transport through Li4SiO4 pebble beds
- Upload type: `dataset`
- Access right: `open`
- License: `GitHub-Zenodo archived public repository for manuscript review and reuse`
- Keywords: Li4SiO4, ceramic breeder pebble bed, discrete element method, fine debris, purge gas, breakthrough curve, voxel topology, particle retention
- Repository DOI: `10.5281/zenodo.20699272`
- Manuscript DOI: `TBC`

### Creators

- Wang, Jian (School of Mechanical Engineering, Anhui University of Science and Technology, Huainan 232001, China)
- Liu, Mingzong (School of Mechanical Engineering, Anhui University of Science and Technology, Huainan 232001, China)
- Lei, Mingzhun (Institute of Plasma Physics, Chinese Academy of Sciences, Hefei 230031, China)
- Wu, Qigang (Institute of Plasma Physics, Chinese Academy of Sciences, Hefei 230031, China)
- Wang, Kaisong (School of Mechanical Engineering, Anhui University of Science and Technology, Huainan 232001, China)
- Deng, Haishun (School of Mechanical Engineering, Anhui University of Science and Technology, Huainan 232001, China)

### Description

Lightweight data and code deposit supporting a DEM-derived voxel-topology study of gas-driven fine-debris transport and retention in Li4SiO4 ceramic breeder pebble beds. The deposit contains manuscript source, processed source data, figure-generation scripts, exported figures, supplementary material, metadata audits, and shared DEM post-processing, voxel-topology and transport analysis utilities. Large raw DEM dump/restart files are documented as optional raw-archive material and may be deposited separately if repository size limits require it.

### License Options To Confirm

- CC-BY-4.0 for data/figures if authors want a permissive attribution data license
- MIT or BSD-3-Clause for reusable code if a separate software license is desired
- A single repository-level license chosen by the corresponding author or institution

## Fields To Confirm After Upload

- `repository.name`
- `repository.identifier`
- `repository.url`
- `repository.license`
- `repository.confirmed`

## Post-Upload Commands

```bash
python3 papers/paper2_voxel_topology_clogging/scripts/audit_submission_metadata_gaps.py
python3 papers/paper2_voxel_topology_clogging/scripts/apply_submission_metadata.py --apply
cd papers/paper2_voxel_topology_clogging/latex && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
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

## Boundary

Repository DOI/accession has been assigned and inserted into the repository metadata.

Repository DOI/accession has been inserted; remaining checks concern manuscript/admin metadata.
