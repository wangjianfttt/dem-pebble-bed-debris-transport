# Paper 2 Submission Form Packet

This file collects copy-ready fields for the journal submission system. Do not treat placeholder or unconfirmed declaration text as final author-approved metadata.

## Journal

Chemical Engineering Science

## Title

Separating breakthrough from pore-network clogging indicators in gas-driven fine-debris transport through Li4SiO4 pebble beds

## Authors

- Jian Wang (aff1,aff2)
- Mingzong Liu (aff1)
- Mingzhun Lei (aff2)
- Qigang Wu (aff2)
- Kaisong Wang (aff1)
- Haishun Deng (aff1)

## Affiliations

- aff1: School of Mechanical Engineering, Anhui University of Science and Technology, Huainan 232001, China
- aff2: Institute of Plasma Physics, Chinese Academy of Sciences, Hefei 230031, China

## Abstract

Fine debris in gas-purged ceramic breeder beds can contaminate downstream regions before a bed develops resolved hydraulic degradation, yet outlet breakthrough is often interpreted as part of a single clogging sequence. This can overstate hydraulic risk when a mobile debris tail reaches connected pathways without observed loss of purge access. Here we examine conditional transport-filtering separation with particle-resolved DEM debris tracking and DEM-derived pore reconstruction in a physically stiff Li4SiO4 bed containing 10,000 1 mm pebbles. The reconstructed baseline has a porosity of 0.4114, a largest connected void fraction of 0.9921 and a box-counting fractal dimension of 2.694. Within the limited parameter window considered here, increasing the Stokes drag-to-weight ratio shifts the debris population downstream and raises the final BTC from zero to 0.0820, whereas no measurable degradation of the outlet-connected pore skeleton is resolved under the present DEM assumptions. A high-inventory localized-release case shows a second conditional separation: a rare front approaches the outlet (x_\max/L=0.9946 at 10.00 ms) while the population bulk remains near the source (x_99/L=0.4202) and no particle crosses the outlet in the simulated window. Increasing the injected debris count from 3000 to 10000 raises the maximum local sub-voxel blockage from 1.1x10^-5 to 3.5x10^-5, yet the exploratory pressure-free index remains below 1.8x10^-5 because connectivity loss is not resolved in the present reconstruction. Returned cropped-domain OpenFOAM checks give a maximum 0.21% pressure-drop increase across the same peak-blockage handoff cases, which bounds but does not validate the hydraulic response and does not close the gas-solid feedback loop. These results are consistent with a pre-clogging migration/filtering regime in which weak breakthrough or near-outlet sparse-front formation is a transport indicator rather than, by itself, evidence of bed-scale pore-network degradation. The work provides a topology-informed workflow for staged clogging assessment: BTC flags transport and contamination, local blockage flags deposition localization, connected-pore loss flags structural degradation, and pressure-drop increase is required for hydraulic confirmation. It reports no resolved hydraulic degradation in the studied window, but requires two-way coupling for closure before validated clogging criteria can be claimed.

## Keywords

- ceramic breeder pebble bed
- Li4SiO4
- discrete element method
- DEM-derived pore reconstruction
- fine debris
- structural screening index
- breakthrough curve

## Highlights

- DEM resolves fines transport in a stiff gas-purged Li4SiO4 pebble bed.
- Breakthrough is decoupled from pore-network degradation by topology metrics.
- Drive, source release and inventory activate different debris observables.
- Discrete coverage mapping bounds evidence without phase-map claims.
- Cropped-domain pressure checks support a bounded pre-clogging regime.

## Graphical Abstract Files

- png: `/Users/wangjian-macbook13/Library/CloudStorage/SynologyDrive-mac/论文相关/分数阶模型研究/project/papers/paper2_voxel_topology_clogging/figures/paper2_graphical_abstract.png`
- pdf: `/Users/wangjian-macbook13/Library/CloudStorage/SynologyDrive-mac/论文相关/分数阶模型研究/project/papers/paper2_voxel_topology_clogging/figures/paper2_graphical_abstract.pdf`
- svg: `/Users/wangjian-macbook13/Library/CloudStorage/SynologyDrive-mac/论文相关/分数阶模型研究/project/papers/paper2_voxel_topology_clogging/figures/paper2_graphical_abstract.svg`

## Submission Scope Note

Chemical Engineering Science submission framed as a mechanistic packed-bed transport study; the manuscript is bounded to DEM-derived pre-clogging migration, retention and pore-structure diagnostics.

## Data Availability

The processed data and figure source tables supporting the quantitative claims are provided in the Paper 2 data/ and tables/ directories of the submitted project package. Raw DEM output files are retained locally because of their size and are available from the corresponding author upon reasonable request.

## Code Availability

Paper-specific scripts for source-data preparation and figure generation are provided in the Paper 2 scripts/ directory of the submitted project package. Shared DEM, voxel, topology and transport utilities are provided under the project-level src/ and scripts/ directories.

## CRediT Author Statement

Jian Wang: Conceptualization, Methodology, Software, Investigation, Formal analysis, Visualization, Writing - original draft. Mingzong Liu: Methodology, Supervision, Writing - review and editing. Mingzhun Lei: Fusion-blanket context, Methodology, Writing - review and editing. Qigang Wu: Fusion-blanket context, Validation planning, Writing - review and editing. Kaisong Wang: Data curation, Visualization, Writing - review and editing. Haishun Deng: Supervision, Project administration, Writing - review and editing.

## Funding

This research did not receive any specific grant from funding agencies in the public, commercial or not-for-profit sectors.

## Declaration Of Competing Interest

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to influence the work reported in this paper.

## Acknowledgements

The authors thank the maintainers of LIGGGHTS-INL and the open-source Python scientific-computing ecosystem used in this work.

## Metadata Confirmation Status

- repository: `True`
- funding: `True`
- competing_interests: `True`
- acknowledgements: `True`
- corresponding_author: `False`
- ai_tool_use: `False`

## Remaining Administrative Note

Unconfirmed administrative metadata: corresponding_author, ai_tool_use.
