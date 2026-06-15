# Paper 2 Reviewer Precheck

This file lists likely Chemical Engineering Science reviewer questions and the current evidence-supported answers. It is a pre-submission control document, not a response letter.

## Status

- Decision: `scientifically_bounded_admin_pending`
- Reviewer-risk summary: `{"bounded": 8, "needs_confirmation": 1, "resolved": 2}`
- Major risk count: 7
- Unresolved risk count: 0
- Needs-confirmation count: 1
- Literature-positioning rows: 9

## Likely Reviewer Questions

### Q1. Pressure calibration

**Likely question:** Is the clogging index pressure-calibrated, and can it be interpreted as a safety limit?

**Evidence-supported answer:** No. The structural index is not pressure-calibrated; Supplementary Table S19 separates pressure-free structural screening, closure proxies, scalar conductance tests and returned cropped-domain OpenFOAM checks so that the current evidence is not overread as validation-grade flow evidence.

**Preferred wording:** `structural pre-screening index with a bounded pressure/flow evidence ladder`

**Avoid wording:** `pressure-calibrated safety criterion`

**Evidence locations:**

- `latex/main.tex: Methods and Results hydraulic-consequence checks`
- `tables/paper2_openfoam_pressure_evidence_source.csv`
- `supplementary/openfoam_model_mesh_pressure_note.md`
- `supplementary/supplementary_figures.md: Fig. S23--S24`
- `supplementary/table_s6_pressure_proxy_summary.csv`
- `supplementary/table_s19_pressure_evidence_ladder.csv`
- `data/paper2_pressure_evidence_ladder.json`
- `submission/claim_boundary_statement.md`

### Q2. Critical clogging

**Likely question:** Do the current simulations demonstrate a critical clogging transition?

**Evidence-supported answer:** No. The current cases support a pre-clogging migration/filtering regime.

**Preferred wording:** `pre-clogging migration/filtering regime`

**Avoid wording:** `universal critical clogging transition`

**Evidence locations:**

- `latex/main.tex: Discussion and Conclusions`
- `tables/paper2_fig4_loading_summary_source.csv`
- `data/reviewer_risk_matrix.json`

### Q3. Experimental imaging

**Likely question:** Are the voxel fields experimental CT data?

**Evidence-supported answer:** No. They are DEM-derived voxel reconstructions from simulated particle coordinates.

**Preferred wording:** `DEM-derived voxel reconstruction`

**Avoid wording:** `experimental CT validation`

**Evidence locations:**

- `latex/main.tex: Introduction and Methods`
- `submission/claim_boundary_statement.md`
- `data/figure_provenance_manifest.json`

### Q4. Gas-particle forcing

**Likely question:** Does the model resolve local purge-gas redistribution inside the pore space?

**Evidence-supported answer:** No. The current model uses one-way Stokes drag; Supplementary Table S18 reports the dimensional debris diameter, nominal particle-Reynolds-number and drag-to-weight range so that the force scale is auditable, while coupled pore-flow remains future work.

**Preferred wording:** `one-way Stokes drag with a dimensional drag-scaling audit`

**Avoid wording:** `resolved pore-scale gas flow`

**Evidence locations:**

- `latex/main.tex: DEM debris transport and voxel analysis workflow`
- `supplementary/table_s18_drag_scaling_summary.csv`
- `data/paper2_drag_scaling_summary.json`
- `submission/claim_boundary_statement.md`
- `RESEARCH_PLAN.md`

### Q5. Localized release

**Likely question:** Do the localized internal-release cases establish a source-position or source-strength law?

**Evidence-supported answer:** No. Three localized-release production rows reached their target windows and support retained-bulk/sparse-front decoupling, but they do not define a source-position or source-strength law.

**Preferred wording:** `target-time mechanism evidence for retained-bulk/sparse-front decoupling`

**Avoid wording:** `complete source-location scaling law`

**Evidence locations:**

- `latex/main.tex: Results and Discussion`
- `tables/explicit_localized_production_summary.csv`
- `figures/paper2_908_spatial_distribution_evidence.pdf`
- `figures/paper2_fig9_sparse_front_diagnostics.pdf`
- `supplementary/supplementary_tables.md`

### Q6. Loading scan

**Likely question:** Can the three loading states be interpreted as a monotonic law?

**Evidence-supported answer:** No. They are single-seed bounded loading responses with different injection histories.

**Preferred wording:** `bounded loading responses`

**Avoid wording:** `monotonic breakthrough law`

**Evidence locations:**

- `latex/main.tex: Debris loading amplifies local accumulation`
- `tables/paper2_fig4_loading_summary_source.csv`
- `figures/paper2_fig4_loading_clogging_response.pdf`

### Q7. Repeat-seed uncertainty

**Likely question:** Are near-threshold repeat-seed results available, and are partial repeat runs cited as evidence?

**Evidence-supported answer:** Yes. Three formal near-threshold repeat-seed rows have been post-processed and are used only to bound stochastic variability, not to define a sharp transition.

**Preferred wording:** `repeat-seed uncertainty bounds stochastic variability`

**Avoid wording:** `partial repeat-run results prove robustness`

**Evidence locations:**

- `data/paper2_near_threshold_repeat_summary.json`
- `tables/paper2_near_threshold_repeat_summary.csv`
- `supplementary/table_s14_near_threshold_repeat_seed_summary.csv`
- `submission/submission_decision_ledger.md`

### Q8. Literature positioning

**Likely question:** How is this work positioned relative to packed-bed deposition, clogging and morphology studies?

**Evidence-supported answer:** It integrates BTC, retention, local blockage and DEM-derived topology in a bounded pre-clogging framework.

**Preferred wording:** `qualitative positioning matrix`

**Avoid wording:** `numerical validation against experiments or CFD`

**Evidence locations:**

- `supplementary/table_s5_literature_positioning_matrix.csv`
- `references/citation_support_map.md`
- `latex/main.tex: Introduction`

### Q9. Parameter coverage

**Likely question:** Does the available parameter evidence define a phase map, full factorial sweep or universal critical-clogging diagram?

**Evidence-supported answer:** No. Supplementary Fig. S25 is a discrete parameter-evidence coverage map that records which drive-state, loading-state and localized-source points support the bounded mechanism interpretation.

**Preferred wording:** `discrete parameter-evidence coverage map`

**Avoid wording:** `phase map or full factorial critical-clogging diagram`

**Evidence locations:**

- `latex/main.tex: mechanism synthesis paragraph citing Supplementary Fig. S25`
- `figures/paper2_figS25_parameter_evidence_coverage.pdf`
- `tables/paper2_parameter_evidence_coverage_source.csv`
- `data/paper2_parameter_evidence_coverage_map.json`
- `notes/paper2_parameter_evidence_coverage_map.md`

## Literature Positioning Rows

The following reference keys are covered in Supplementary Table S5:

- `Natsui2012FinesClogging`
- `Boccardo2019PackedBedDeposition`
- `Wang2024IJMF`
- `Mays2005Clogging`
- `Dressaire2017Clogging`
- `Parvan2020Clogging`
- `Armstrong2019Minkowski`
- `Dathe2005Fractal`
- `ThisWork`

## Submission Boundary Reminder

Submit the manuscript as a bounded DEM-based pre-clogging migration and retention study. Do not present it as an experimental validation, a pressure-calibrated safety-limit paper or a universal critical-clogging transition paper.
