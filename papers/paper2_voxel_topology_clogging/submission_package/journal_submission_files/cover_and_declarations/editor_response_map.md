# Paper 2 CES Editor Response Map

This document maps likely Chemical Engineering Science editorial concerns to evidence-supported responses. It is a pre-submission aid, not a reviewer response letter.

- Decision: `pass`
- Target journal: Chemical Engineering Science
- Concern count: 8
- High-risk concerns: `['E04_no_pressure_calibration']`
- Missing-evidence concerns: `[]`

## Response Map

### E01_not_case_specific: Is this only a fusion-blanket case study?

- Risk: `medium`
- Status: `supported`
- Short answer: No. The manuscript is framed as a packed-bed fine-particle transport diagnostic, with Li4SiO4 breeder beds as a high-consequence application.
- Suggested editor wording: The work targets a general gas-purged packed-bed mechanism: breakthrough, deposition and pore-network degradation are separated rather than conflated.
- Boundary: Application relevance is Li4SiO4 breeder beds; the claim is not a blanket safety qualification.
- Evidence:
  - `papers/paper2_voxel_topology_clogging/latex/main.tex`
  - `papers/paper2_voxel_topology_clogging/submission/cover_letter_draft.md`
  - `papers/paper2_voxel_topology_clogging/submission/ces_novelty_statement.md`
  - `papers/paper2_voxel_topology_clogging/submission/highlights.md`
  - `papers/paper2_voxel_topology_clogging/submission/journal_targeting_matrix.md`

### E02_dem_credibility: Is the DEM setup physically credible enough for a mechanism paper?

- Risk: `medium`
- Status: `supported`
- Short answer: The bed uses 10,000 physically stiff 1 mm Li4SiO4 pebbles with a 90 GPa Young's modulus and a fixed compacted skeleton for debris transport.
- Suggested editor wording: The DEM bed is not a soft-particle demonstrator; it is a stiff-particle packed-bed mechanism calculation with explicit modelling boundaries.
- Boundary: No experimental validation is claimed.
- Evidence:
  - `papers/paper2_voxel_topology_clogging/latex/main.tex`
  - `papers/paper2_voxel_topology_clogging/tables/paper2_fig1_baseline_topology_source.csv`
  - `papers/paper2_voxel_topology_clogging/tables/paper2_fig2_box_counting_source.csv`
  - `papers/paper2_voxel_topology_clogging/data/paper2_claim_evidence_ledger.json`

### E03_breakthrough_vs_clogging: Why is breakthrough not treated as clogging?

- Risk: `low`
- Status: `supported`
- Short answer: The evidence separates outlet arrival from local blockage and connected-pore loss; weak BTC occurs while outlet-connected void connectivity is retained.
- Suggested editor wording: Breakthrough is interpreted as a transport signal; clogging requires structural or hydraulic degradation evidence.
- Boundary: The conclusion is bounded to the current DEM parameter window.
- Evidence:
  - `papers/paper2_voxel_topology_clogging/tables/paper2_fig3_representative_state_source.csv`
  - `papers/paper2_voxel_topology_clogging/tables/paper2_fig4_loading_summary_source.csv`
  - `papers/paper2_voxel_topology_clogging/figures/paper2_fig1_voxel_topology_framework.pdf`
  - `papers/paper2_voxel_topology_clogging/figures/paper2_fig4_loading_clogging_response.pdf`

### E04_no_pressure_calibration: Do the available pressure checks support a safety-limit or pressure-calibrated clogging claim?

- Risk: `high`
- Status: `supported`
- Short answer: No. The manuscript uses returned cropped-domain OpenFOAM checks as bounded hydraulic screening evidence and does not make a pressure-calibrated safety claim.
- Suggested editor wording: The paper reports a bounded pre-clogging regime supported by structural metrics and cropped-domain pressure checks, not a pressure-calibrated safety limit.
- Boundary: Returned OpenFOAM pressure drops are cropped-domain numerical checks, not experimental validation, not blanket-scale flow evidence and not pressure-calibrated Ib.
- Evidence:
  - `papers/paper2_voxel_topology_clogging/submission/claim_boundary_statement.md`
  - `papers/paper2_voxel_topology_clogging/data/paper2_overclaim_guard.json`
  - `papers/paper2_voxel_topology_clogging/tables/paper2_benchmark_crosswalk.csv`
  - `papers/paper2_voxel_topology_clogging/supplementary/table_s6_pressure_proxy_summary.csv`
  - `papers/paper2_voxel_topology_clogging/data/paper2_openfoam_pressure_evidence_summary.json`
  - `papers/paper2_voxel_topology_clogging/tables/paper2_openfoam_pressure_evidence_source.csv`

### E05_not_experimental_ct: Are the voxel fields experimental CT data?

- Risk: `low`
- Status: `supported`
- Short answer: No. They are DEM-derived pore reconstructions generated from simulated particle coordinates.
- Suggested editor wording: Use DEM-derived pore reconstruction or DEM-derived voxel topology, not experimental CT.
- Boundary: Voxel topology is a numerical reconstruction and post-processing layer.
- Evidence:
  - `papers/paper2_voxel_topology_clogging/latex/main.tex`
  - `papers/paper2_voxel_topology_clogging/data/figure_provenance_manifest.json`
  - `papers/paper2_voxel_topology_clogging/notes/paper2_abstract_evidence_alignment.md`
  - `papers/paper2_voxel_topology_clogging/submission/front_matter_audit.json`

### E06_benchmark_strength: Are the comparisons strong enough for a high-level chemical-engineering journal?

- Risk: `medium`
- Status: `supported`
- Short answer: The benchmark crosswalk separates quantitative within-study metrics, semi-quantitative mechanism comparisons and bounded proxy comparisons.
- Suggested editor wording: The paper is positioned against packed-bed fines transport, deposition, porous-media clogging and morphology descriptors without claiming numerical replication.
- Boundary: Benchmarking is evidence mapping and positioning, not experimental or CFD validation.
- Evidence:
  - `papers/paper2_voxel_topology_clogging/data/paper2_benchmark_crosswalk.json`
  - `papers/paper2_voxel_topology_clogging/tables/paper2_benchmark_crosswalk.csv`
  - `papers/paper2_voxel_topology_clogging/notes/paper2_benchmark_crosswalk.md`
  - `papers/paper2_voxel_topology_clogging/supplementary/table_s5_literature_positioning_matrix.csv`

### E07_loading_and_source_limits: Do the loading and localized-release cases establish universal laws?

- Risk: `medium`
- Status: `supported`
- Short answer: No. They are supporting mechanism evidence and bounded loading responses; the manuscript explicitly avoids monotonic loading-law and source-position-law claims.
- Suggested editor wording: The available loading and source-position cases support the pre-clogging mechanism but do not define a universal transition curve.
- Boundary: Three loading states are single-seed responses; the localized-release rows reached their target windows but remain mechanism cases, not a fitted source-position law.
- Evidence:
  - `papers/paper2_voxel_topology_clogging/tables/paper2_fig4_loading_summary_source.csv`
  - `papers/paper2_voxel_topology_clogging/tables/explicit_localized_production_summary.csv`
  - `papers/paper2_voxel_topology_clogging/submission/reviewer_precheck.json`
  - `papers/paper2_voxel_topology_clogging/data/paper2_claim_evidence_ledger.json`

### E08_parameter_coverage_boundary: Does the parameter evidence support a phase map or full factorial sweep?

- Risk: `medium`
- Status: `supported`
- Short answer: No. The manuscript uses a discrete parameter-evidence coverage map to show which drive-state, loading-state and localized-source points support the mechanism interpretation.
- Suggested editor wording: The available parameter evidence is discrete and mechanism-directed; it supports the bounded pre-clogging interpretation without interpolating a phase map.
- Boundary: Not a full factorial parameter sweep, not an interpolated phase map and not a universal critical-clogging diagram.
- Evidence:
  - `papers/paper2_voxel_topology_clogging/latex/main.tex`
  - `papers/paper2_voxel_topology_clogging/figures/paper2_figS25_parameter_evidence_coverage.pdf`
  - `papers/paper2_voxel_topology_clogging/tables/paper2_parameter_evidence_coverage_source.csv`
  - `papers/paper2_voxel_topology_clogging/data/paper2_parameter_evidence_coverage_map.json`
  - `papers/paper2_voxel_topology_clogging/notes/paper2_parameter_evidence_coverage_map.md`

## Boundary Reminder

- Do not claim experimental validation.
- Do not claim experimental CT.
- Do not claim pressure-calibrated safety limits.
- Do not claim a universal critical clogging transition.

Boundary: Editor-facing response support only; this map does not create new scientific evidence.
