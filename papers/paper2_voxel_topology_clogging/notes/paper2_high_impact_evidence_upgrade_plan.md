# High-Impact Evidence Upgrade Plan

This plan prioritizes the smallest additional evidence needed to move Paper 2 from a bounded CES-ready manuscript toward a higher-risk CEJ-level submission.

- Decision: `all_primary_scientific_evidence_and_mechanism_map_ready_for_admin_and_polish`
- Actions: 5
- Top priority: `none_scientific_evidence_ready`
- Boundary: This is an execution plan only; it does not create new scientific evidence until runs are completed and imported.

## Action Matrix

| Priority | Action | Evidence gap | Current evidence | Minimum success criterion | Boundary |
|---:|---|---|---|---|---|
| 1 | `E01_openfoam_first_pressure_case` | pressure-response calibration for hydraulic consequence | valid_pressure_cases=3, strict_pressure_cases=3, engineering_screening_cases=3, uncoupled_hydraulic_field_cases=0, solver_hydraulic_field_coupled_cases=3, pressure_drop_unique_values=3, unique_flow_geometries=3, geometry_distinguishable=True, manuscript_ready=True | Complete strict pressure evidence already available for the current handoff. | No OpenFOAM pressure claim until returned archive is imported and evidence gate passes. |
| 2 | `E02_complete_906_localized_release` | longer internal-source retention/migration window | final_time_s=0.04, target_s=0.04 | Reach target time and refresh localized production summary with retention, downstream fraction and outlet fraction. | Still not a complete source-location scaling law unless additional source positions/seeds are completed. |
| 3 | `E03_repeat_seed_near_threshold` | near-threshold stochasticity and seed uncertainty | summary_decision=repeat_seed_evidence_ready; final_BTC_mean=0.016444444444444446; range=0.013333333333333334--0.018333333333333333 | At least three frozen-bed processed rows with final BTC, first-breakthrough time and retention for the near-threshold state. | Formal repeat-seed uncertainty is available and inserted only as stochastic variability evidence; it is not a critical-transition law. |
| 4 | `E04_908_high_inventory_diagnostic` | higher-inventory localized blockage stress test | final_time_s=0.01, target_s=0.01 | Reach 10 ms without numerical instability and quantify whether Bmax or connectivity loss leaves the O(1e-5) window. | Diagnostic-only until target time and stability checks are complete. |
| 5 | `E05_expand_dimensionless_map` | full regime-map density | Current dimensionless map is a derived nine-row synthesis covering drive, loading and localized-source mechanism axes. | At least three drive rows, three loading rows and three localized-source rows have explicit source files, evidence boundaries and no mixed frozen/unfrozen interpretation. | Still not universal unless the scan covers broader df/dp, ug, loading and seed variability. |

## Run Commands

### E01_openfoam_first_pressure_case

```bash
python3 papers/paper2_voxel_topology_clogging/scripts/make_openfoam_manuscript_snippet.py
```

### E02_complete_906_localized_release

```bash
ONLY=906_upstream_source_continue_1M_to_4M NP=${NP:-16} LIGGGHTS_BIN=${LIGGGHTS_BIN:-lmp_mpi_no_vtk} bash papers/paper2_voxel_topology_clogging/scripts/run_explicit_localized_production_queue.sh
```

### E03_repeat_seed_near_threshold

```bash
Prepare frozen repeat cases for missing seeds, run LIGGGHTS, then post-process with analyze_debris_transport.py.
```

### E04_908_high_inventory_diagnostic

```bash
ONLY=908_high_inventory_dt5e9_to_10ms NP=${NP:-16} LIGGGHTS_BIN=${LIGGGHTS_BIN:-lmp_mpi_no_vtk} bash papers/paper2_voxel_topology_clogging/scripts/run_explicit_localized_production_queue.sh
```

### E05_expand_dimensionless_map

```bash
python3 papers/paper2_voxel_topology_clogging/scripts/make_dimensionless_mechanism_map.py
```

## Stop Criteria

- If OpenFOAM first case fails mesh or solver gates, fix handoff settings before running the three-case pressure series.
- If repeat seeds show strong stochastic spread, frame near-threshold breakthrough probabilistically rather than as a sharp deterministic threshold.
- If localized high-inventory cases still show no connectivity loss, do not keep escalating inventory without pressure-flow evidence.
