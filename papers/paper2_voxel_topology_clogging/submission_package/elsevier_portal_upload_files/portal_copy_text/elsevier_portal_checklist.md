# Elsevier Portal Checklist

This checklist converts the current Paper 2 package into journal-portal actions. It is not an author approval record.

## Readiness

- Decision: `portal_ready_to_submit`
- Gate status: `ready_for_bounded_submission`
- Required open actions: 0
- Optional open actions: 0
- Missing upload files: `[]`

## Manuscript Metadata

- Journal: Chemical Engineering Science
- Article type: Research article
- Title: Separating breakthrough from pore-network clogging indicators in gas-driven fine-debris transport through Li4SiO4 pebble beds
- Authors: 7
- Affiliations: 2
- Abstract words: 334
- Keywords: 7
- Highlights: 5

## Copy-Ready Text

### Abstract

Fine debris in gas-purged ceramic breeder beds can contaminate downstream regions before a bed develops resolved hydraulic degradation, yet outlet breakthrough is often interpreted as part of a single clogging sequence. This can overstate hydraulic risk when a mobile debris tail reaches connected pathways without observed loss of purge access. Here we examine conditional transport-filtering separation with particle-resolved DEM debris tracking and DEM-derived pore reconstruction in a physically stiff Li4SiO4 bed containing 10,000 1 mm pebbles. The reconstructed baseline has a porosity of 0.4114, a largest connected void fraction of 0.9921 and a box-counting fractal dimension of 2.694. Within the limited parameter window considered here, increasing the Stokes drag-to-weight ratio shifts the debris population downstream and raises the final BTC from zero to 0.0820, whereas no measurable degradation of the outlet-connected pore skeleton is resolved under the present DEM assumptions. A high-inventory localized-release case shows a second conditional separation: a rare front approaches the outlet (x_\max/L=0.9946 at 10.00 ms) while the population bulk remains near the source (x_99/L=0.4202) and no particle crosses the outlet in the simulated window. Increasing the injected debris count from 3000 to 10000 raises the maximum local sub-voxel blockage from 1.1x10^-5 to 3.5x10^-5, yet the exploratory pressure-free index remains below 1.8x10^-5 because connectivity loss is not resolved in the present reconstruction. Returned cropped-domain OpenFOAM checks give a maximum 0.21% pressure-drop increase across the same peak-blockage handoff cases, which bounds but does not validate the hydraulic response and does not close the gas-solid feedback loop. These results are consistent with a pre-clogging migration/filtering regime in which weak breakthrough or near-outlet sparse-front formation is a transport indicator rather than, by itself, evidence of bed-scale pore-network degradation. The work provides a topology-informed workflow for staged clogging assessment: BTC flags transport and contamination, local blockage flags deposition localization, connected-pore loss flags structural degradation, and pressure-drop increase is required for hydraulic confirmation. It reports no resolved hydraulic degradation in the studied window, but requires two-way coupling for closure before validated clogging criteria can be claimed.

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

### Data Availability

The processed data and figure source tables supporting the quantitative claims are available in the public GitHub-Zenodo repository https://github.com/wangjianfttt/dem-pebble-bed-debris-transport, archived at DOI 10.5281/zenodo.20699272. Raw DEM dump and restart files are not included in the lightweight public deposit because of their size and are available from the corresponding author upon reasonable request.

### Code Availability

Paper-specific scripts for source-data preparation and figure generation are available in the same GitHub-Zenodo repository under papers/paper2_voxel_topology_clogging/scripts. Shared DEM, voxel, topology and transport utilities are provided under src/. The archived repository version is available at DOI 10.5281/zenodo.20699272.

### CRediT Author Statement

Jian Wang: Conceptualization, Methodology, Software, Investigation, Formal analysis, Visualization, Writing - original draft. Mingzhun Lei: Methodology, Project administration, Writing - review and editing. Haoxi Wang: Methodology, Writing - review and editing. Zhiyuan Liu: Application context, Methodology, Writing - review and editing. Haishun Deng: Application context, Validation planning, Writing - review and editing. Wei Wen: Data curation, Visualization, Writing - review and editing. Gang Shen: Supervision, Project administration, Writing - review and editing.

### Declaration Of Competing Interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

### Acknowledgements

This work was supported by the Anhui Provincial Natural Science Foundation (2408085QA030), the Anhui Intelligent Mine Technology and Equipment Engineering Research Center (AIMTEERC202307), the Science Foundation of the Institute of Plasma Physics, Chinese Academy of Sciences (DSJJ-2025-08), and the China Post-doctoral Science Foundation under Grant Number 2024M753266.

## Upload Checklist

- [x] `manuscript/main.pdf`
- [x] `manuscript/main.tex`
- [x] `manuscript/paper2_references.bib`
- [x] `manuscript/highlights.md`
- [x] `main_figures/paper2_fig1_voxel_topology_framework.pdf`
- [x] `main_figures/paper2_fig2_baseline_voxel_topology.pdf`
- [x] `main_figures/paper2_fig3_representative_debris_blockage.pdf`
- [x] `main_figures/paper2_908_spatial_distribution_evidence.pdf`
- [x] `main_figures/paper2_fig4_loading_clogging_response.pdf`
- [x] `main_figures/paper2_graphical_abstract.png`
- [x] `main_figures/paper2_graphical_abstract.pdf`
- [x] `main_figures/paper2_graphical_abstract.svg`
- [x] `supplementary_material/supplementary/supplementary_tables.md`
- [x] `supplementary_material/supplementary/supplementary_figures.md`
- [x] `cover_and_declarations/cover_letter_draft.md`
- [x] `cover_and_declarations/claim_boundary_statement.md`
- [x] `cover_and_declarations/reviewer_precheck.md`
- [x] `cover_and_declarations/editor_response_map.md`
- [x] `cover_and_declarations/final_submission_action_list.md`
- [x] `cover_and_declarations/repository_upload_packet.md`
- [x] `cover_and_declarations/submission_form_packet.md`
- [x] `cover_and_declarations/repository_deposit/repository_metadata.yaml`
- [x] `cover_and_declarations/repository_deposit/CITATION.cff`

## Required Administrative Actions

- [ ] `A01_repository`: Required for Data availability and Code availability.
- [ ] `A02_competing_interests`: Required by the journal and must be confirmed by all authors.
- [ ] `A03_acknowledgements`: Required to avoid unapproved computing-resource or collaborator wording.
- [ ] `A04_corresponding_author`: Required for the journal submission system and cover-letter metadata.

## Optional Administrative Actions


## Boundary Phrases

- Do not claim experimental CT; use DEM-derived voxel or pore reconstruction wording.
- Do not claim pressure-calibrated safety limits unless returned flow-solver or experimental pressure evidence is inserted.
- Do not claim a public repository DOI/accession until the repository record exists.

## Next Action

Confirm repository DOI/accession, competing-interest, acknowledgement and corresponding-author metadata, then rerun the submission gate before pressing submit.
