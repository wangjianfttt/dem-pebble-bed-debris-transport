# Paper 2 Supplementary Tables

These tables are generated from the source CSV files used by the manuscript figures. They are intended for auditability and reviewer traceability, not for replacing the main-text figures.

## table_s1_case_matrix

File: `papers/paper2_voxel_topology_clogging/supplementary/table_s1_case_matrix.csv`

Rows: 9, columns: 11

| table_group | case_id | evidence_level | df_over_dp | gas_velocity_m_s | debris_count_or_inventory | final_BTC_or_outlet_fraction | retention_or_source_fraction | x_mean_over_L | x_q99_or_centroid_over_L | note |
|---|---|---|---|---|---|---|---|---|---|---|
| representative_drive_state | paper1_df0p025_ug1_seed401 | production_result | 0.025 | 1 | 2917 | 0 |  | 0.208378 | 0.208459 | low_drive_no_breakthrough |
| representative_drive_state | paper1_df0p0225_ug2_seed401 | production_result | 0.0225 | 2 | 2830 | 0.0183333 |  | 0.35751 | 0.357226 | intermediate_drive_weak_breakthrough |
| representative_drive_state | paper1_df0p02_ug3_seed401 | production_result | 0.02 | 3 | 2752 | 0.082 |  | 0.502586 | 0.499818 | high_drive_stronger_breakthrough |
| loading_scan | paper1_df0p0225_ug2_seed401_baseline3000 | production_result_single_seed | 0.0225 | 2 | 3000 | 0.0183333 | 0.981667 | 0.35751 | 0.351818 | baseline_3000 |
| loading_scan | paper1_load6000_df0p0225_ug2_seed401 | production_result_single_seed | 0.0225 | 2 | 6000 | 0.0141667 | 0.985833 | 0.359757 | 0.354261 | loading_scan |
| loading_scan | paper1_load10000_df0p0225_ug2_seed401 | production_result_single_seed | 0.0225 | 2 | 10000 | 0.0156 | 0.9844 | 0.3603 | 0.354547 | loading_scan |
| localized_internal_release | paper2_local_damage_slab_x012_018_df0p1_n15000_seed906_explicit | production_target_reached | 0.1 |  | 15000 | 0 | 0.579333 | 0.395763 | 0.625438 | 906 upstream source, N=15000 |
| localized_internal_release | paper2_local_damage_slab_x024_030_df0p1_n15000_seed907_explicit | production_target_reached | 0.1 |  | 15000 | 0 | 0.896133 | 0.612659 | 0.683754 | 907 downstream source, N=15000 |

## table_s2_structural_metrics

File: `papers/paper2_voxel_topology_clogging/supplementary/table_s2_structural_metrics.csv`

Rows: 6, columns: 8

| case_group | case_id | outlet_connected_void_fraction | largest_connected_void_fraction | topological_charge | max_blockage_ratio | Ib_no_pressure | pressure_increase_ratio |
|---|---|---|---|---|---|---|---|
| representative_drive_state | paper1_df0p025_ug1_seed401 | 0.999528 | 0.999528 | -0.00169122 | 2.20848e-05 |  |  |
| representative_drive_state | paper1_df0p0225_ug2_seed401 | 0.999528 | 0.999528 | -0.00169122 | 1.0632e-05 |  |  |
| representative_drive_state | paper1_df0p02_ug3_seed401 | 0.999528 | 0.999528 | -0.00169122 | 2.75479e-05 |  |  |
| loading_scan | paper1_df0p0225_ug2_seed401_baseline3000 | 0.999528 | 0.999528 | -0.00169122 | 1.0632e-05 | 5.316e-06 | 3.77204e-06 |
| loading_scan | paper1_load6000_df0p0225_ug2_seed401 | 0.999528 | 0.999528 | -0.00169122 | 2.0833e-05 | 1.04165e-05 | 7.60944e-06 |
| loading_scan | paper1_load10000_df0p0225_ug2_seed401 | 0.999528 | 0.999528 | -0.00169122 | 3.54879e-05 | 1.77439e-05 | 1.25812e-05 |

## table_s3_resolution_and_status

File: `papers/paper2_voxel_topology_clogging/supplementary/table_s3_resolution_and_status.csv`

Rows: 8, columns: 6

| group | item | status | metric_1 | metric_2 | note |
|---|---|---|---|---|---|
| voxel_resolution | 0.20 mm | available | 0.418333 | 0.996279 | porosity, outlet-connected void fraction |
| voxel_resolution | 0.25 mm | available | 0.411398 | 0.99208 | porosity, outlet-connected void fraction |
| voxel_resolution | 0.30 mm | available | 0.423019 | 0.983652 | porosity, outlet-connected void fraction |
| voxel_resolution | 0.40 mm | available | 0.444457 | 0.952827 | porosity, outlet-connected void fraction |
| voxel_resolution | 0.50 mm | available | 0.409973 | 0.742697 | porosity, outlet-connected void fraction |
| localized_release_job | 906 upstream source, N=15000 | production_target_reached | 0.04 | 0.04 | target_time_s, available_time_s; Does the upstream internal source eventually produce outlet breakthrough over the full 40 ms window? |
| localized_release_job | 907 downstream source, N=15000 | production_target_reached | 0.01 | 0.01005 | target_time_s, available_time_s; Does a downstream source reach the outlet faster than the upstream source under the same physical drag? |
| localized_release_job | 908 upstream source, N=30000 | production_target_reached | 0.01 | 0.01 | target_time_s, available_time_s; Does higher local source inventory intensify release or blockage without changing drag? |

## table_s4_mechanism_evidence_matrix

File: `papers/paper2_voxel_topology_clogging/supplementary/table_s4_mechanism_evidence_matrix.csv`

Rows: 9, columns: 6

| mechanism | evidence | metric | value | interpretation | source |
|---|---|---|---|---|---|
| drive-controlled migration | Representative states | Fd/W range | 24.08-112.86 | Higher drag-to-weight ratio moves the debris cloud downstream. | /Users/wangjian-macbook13/Library/CloudStorage/SynologyDrive-mac/论文相关/分数阶模型研究/project/papers/paper2_voxel_topology_clogging/tables/paper2_fig3_representative_state_source.csv |
| drive-controlled migration | Representative states | final BTC range | 0.00000-0.08200 | Breakthrough increases with stronger downstream migration in the selected states. | /Users/wangjian-macbook13/Library/CloudStorage/SynologyDrive-mac/论文相关/分数阶模型研究/project/papers/paper2_voxel_topology_clogging/tables/paper2_fig3_representative_state_source.csv |
| delayed leading-tail breakthrough | Time-resolved representative case | first BTC time | 0.03159 s | Outlet arrival occurs after debris-front migration through the connected skeleton. | /Users/wangjian-macbook13/Library/CloudStorage/SynologyDrive-mac/论文相关/分数阶模型研究/project/papers/paper2_voxel_topology_clogging/tables/paper2_front_migration_metrics_source.csv |
| delayed leading-tail breakthrough | Time-resolved representative case | q99 speed / mean speed | 1.44 | The leading tail advances faster than the mean cloud. | /Users/wangjian-macbook13/Library/CloudStorage/SynologyDrive-mac/论文相关/分数阶模型研究/project/papers/paper2_voxel_topology_clogging/tables/paper2_front_migration_metrics_source.csv |
| delayed leading-tail breakthrough | Event ordering | q99>=0.9 minus first BTC | 0.00405 s | A weak outlet signal appears before the 99th percentile occupies the near-outlet region. | /Users/wangjian-macbook13/Library/CloudStorage/SynologyDrive-mac/论文相关/分数阶模型研究/project/papers/paper2_voxel_topology_clogging/tables/paper2_front_migration_events_source.csv |
| source-zone retention | Explicit internal-source production windows | source fraction at 10 ms | 0.8961-0.9015 | Internal debris release remains retention dominated over the analyzed window. | /Users/wangjian-macbook13/Library/CloudStorage/SynologyDrive-mac/论文相关/分数阶模型研究/project/papers/paper2_voxel_topology_clogging/tables/explicit_localized_production_summary.csv |
| source-position effect | Explicit internal-source production windows | leading x/L at 10 ms | 0.853-0.983 | Source position changes leading-tail location without producing outlet release. | /Users/wangjian-macbook13/Library/CloudStorage/SynologyDrive-mac/论文相关/分数阶模型研究/project/papers/paper2_voxel_topology_clogging/tables/explicit_localized_production_summary.csv |
| pre-clogging loading response | Loading scan | max blockage range | 1.06e-05-3.55e-05 | Local blockage grows with inventory but remains a sub-voxel perturbation. | /Users/wangjian-macbook13/Library/CloudStorage/SynologyDrive-mac/论文相关/分数阶模型研究/project/papers/paper2_voxel_topology_clogging/tables/paper2_fig4_loading_summary_source.csv |

## table_s5_literature_positioning_matrix

File: `papers/paper2_voxel_topology_clogging/supplementary/table_s5_literature_positioning_matrix.csv`

Rows: 9, columns: 10

| reference_key | study_context | method_family | tracks_fine_particles | reports_breakthrough_or_retention | uses_internal_structure_or_voxels | uses_connectivity_or_topology_metrics | uses_pressure_or_flow_response | role_in_current_paper | current_paper_addition |
|---|---|---|---|---|---|---|---|---|---|
| Natsui2012FinesClogging | packed-bed fines clogging | DEM-CFD | yes | partial | no | no | yes | Scale and mechanism reference for gas-solid fines clogging in packed beds. | Adds DEM-derived voxel connectivity and topology diagnostics to distinguish breakthrough from structural clogging. |
| Boccardo2019PackedBedDeposition | fine and ultrafine deposition in packed-bed reactors | pore/packed-bed deposition modelling | yes | yes | partial | no | partial | Reference for particle deposition and retention in packed-bed pore pathways. | Links deposition profiles to DEM-derived pore connectivity and a pressure-free clogging pre-screening index. |
| Wang2024IJMF | gas-powder flow in packed beds | two-way coupled CFD-DEM | yes | yes | no | no | yes | Closest author-side reference for gas-powder packed-bed transport and physical scale. | Moves from flow/particle transport toward DEM-derived pore-structure and topology interpretation in Li4SiO4 breeder beds. |
| Mays2005Clogging | particle clogging in porous media | hydrodynamic clogging theory | conceptual | yes | no | no | yes | Supports the distinction between particle retention and hydraulic clogging. | Provides DEM-resolved debris locations and voxel connectivity evidence for that distinction in a breeder pebble bed. |
| Dressaire2017Clogging | microfluidic clogging | review/mechanistic synthesis | conceptual | partial | no | no | yes | Supports multi-stage clogging interpretation and the non-equivalence of transport and blockage signals. | Applies this separation to DEM-derived pebble-bed debris migration and pore-connectivity diagnostics. |
| Parvan2020Clogging | particle retention and clogging in porous media | pore-scale lattice Boltzmann modelling | yes | yes | yes | partial | yes | Reference for pore-scale particle retention/clogging mechanisms and pressure response. | Focuses on DEM-generated Li4SiO4 pebble beds and separates BTC, local blockage and outlet-connected pore skeleton metrics. |
| Armstrong2019Minkowski | porous-media morphology | Minkowski/topology review | no | no | yes | yes | partial | Supports Euler/Minkowski-style topology descriptors for porous media. | Combines such descriptors with DEM debris transport and retention metrics. |
| Dathe2005Fractal | fractal pore/solid morphology | fractal porous-media analysis | no | no | yes | partial | no | Supports box-counting fractal interpretation of solid and pore structures. | Uses fractal dimension as one descriptor in a DEM-derived voxel-topology workflow. |

## table_s6_pressure_proxy_summary

File: `papers/paper2_voxel_topology_clogging/supplementary/table_s6_pressure_proxy_summary.csv`

Rows: 3, columns: 14

| debris_total_number | gas_velocity_m_s | baseline_pressure_gradient_pa_m | profile_mean_pressure_gradient_pa_m | peak_local_pressure_gradient_pa_m | baseline_pressure_drop_pa | profile_mean_pressure_drop_pa | peak_local_equivalent_pressure_drop_pa | profile_pressure_increase_ratio | peak_local_pressure_increase_ratio | subvoxel_max_blockage_ratio | pressure_proxy_type | pressure_proxy_not_cfd | evidence_boundary |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3000 | 2 | 38962 | 38962.2 | 38963 | 1753.29 | 1753.3 | 1753.34 | 3.77204e-06 | 2.50582e-05 | 5.93256e-06 | Ergun with epsilon_t = epsilon0 * (1 - B) | True | Ergun proxy only; not CFD, not measured pressure, not used to calibrate Ib |
| 6000 | 2 | 38962 | 38962.3 | 38963.9 | 1753.29 | 1753.31 | 1753.38 | 7.60944e-06 | 4.86776e-05 | 1.15243e-05 | Ergun with epsilon_t = epsilon0 * (1 - B) | True | Ergun proxy only; not CFD, not measured pressure, not used to calibrate Ib |
| 10000 | 2 | 38962 | 38962.5 | 38965.3 | 1753.29 | 1753.31 | 1753.44 | 1.25812e-05 | 8.24549e-05 | 1.95207e-05 | Ergun with epsilon_t = epsilon0 * (1 - B) | True | Ergun proxy only; not CFD, not measured pressure, not used to calibrate Ib |

## table_s7_voxel_pressure_pilot_summary

File: `papers/paper2_voxel_topology_clogging/supplementary/table_s7_voxel_pressure_pilot_summary.csv`

Rows: 4, columns: 13

| case_label | debris_total_number | pressure_model | status | through_pore_voxels | conductance | relative_conductance | relative_resistance | conductance_loss | max_blockage_ratio | not_cfd | not_lbm | evidence_boundary |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 0 | voxel-network Darcy-Laplace | solved | 233619 | 2.27579 | 1 | 1 | 0 | 0 | True | True | voxel-network pressure pilot; not CFD/LBM and not pressure-calibrated Ib |
| N=3000 | 3000 | voxel-network Darcy-Laplace | solved | 233619 | 2.27578 | 0.999997 | 1 | 2.75298e-06 | 5.93256e-06 | True | True | voxel-network pressure pilot; not CFD/LBM and not pressure-calibrated Ib |
| N=6000 | 6000 | voxel-network Darcy-Laplace | solved | 233619 | 2.27578 | 0.999994 | 1.00001 | 5.54909e-06 | 1.15243e-05 | True | True | voxel-network pressure pilot; not CFD/LBM and not pressure-calibrated Ib |
| N=10000 | 10000 | voxel-network Darcy-Laplace | solved | 233619 | 2.27577 | 0.999991 | 1.00001 | 9.17882e-06 | 1.95207e-05 | True | True | voxel-network pressure pilot; not CFD/LBM and not pressure-calibrated Ib |

## table_s8_cropped_flow_domain_manifest

File: `papers/paper2_voxel_topology_clogging/supplementary/table_s8_cropped_flow_domain_manifest.csv`

Rows: 3, columns: 15

| case_label | debris_total_number | crop_role | x_peak_blockage_m | x_applied_lower_m | x_applied_upper_m | shape_x | shape_y | shape_z | porosity | through_connected_void_fraction_x | voxel_npz | pore_mask_npy | metadata_json | evidence_boundary |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N=3000 | 3000 | peak_blockage_window | 0.012375 | 0.00825 | 0.0165 | 33 | 60 | 53 | 0.407118 | 0.990731 | papers/paper2_voxel_topology_clogging/flow_domains/N3000_peak_blockage/voxel_crop.npz | papers/paper2_voxel_topology_clogging/flow_domains/N3000_peak_blockage/pore_mask.npy | papers/paper2_voxel_topology_clogging/flow_domains/N3000_peak_blockage/metadata.json | cropped pore-domain and debris-resistance input for future pressure-flow solvers; not a solver result |
| N=6000 | 6000 | peak_blockage_window | 0.012375 | 0.00825 | 0.0165 | 33 | 60 | 53 | 0.407118 | 0.990731 | papers/paper2_voxel_topology_clogging/flow_domains/N6000_peak_blockage/voxel_crop.npz | papers/paper2_voxel_topology_clogging/flow_domains/N6000_peak_blockage/pore_mask.npy | papers/paper2_voxel_topology_clogging/flow_domains/N6000_peak_blockage/metadata.json | cropped pore-domain and debris-resistance input for future pressure-flow solvers; not a solver result |
| N=10000 | 10000 | peak_blockage_window | 0.012375 | 0.00825 | 0.0165 | 33 | 60 | 53 | 0.407118 | 0.990731 | papers/paper2_voxel_topology_clogging/flow_domains/N10000_peak_blockage/voxel_crop.npz | papers/paper2_voxel_topology_clogging/flow_domains/N10000_peak_blockage/pore_mask.npy | papers/paper2_voxel_topology_clogging/flow_domains/N10000_peak_blockage/metadata.json | cropped pore-domain and debris-resistance input for future pressure-flow solvers; not a solver result |

## table_s9_cropped_flow_permeability_summary

File: `papers/paper2_voxel_topology_clogging/supplementary/table_s9_cropped_flow_permeability_summary.csv`

Rows: 3, columns: 13

| case_label | debris_total_number | pressure_model | baseline_conductance | loaded_conductance | relative_resistance | local_conductance_loss | whole_domain_conductance_loss | local_to_whole_loss_ratio | max_blockage_ratio_in_profile | not_cfd | not_lbm | evidence_boundary |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N=3000 | 3000 | cropped voxel-network Darcy-Laplace | 12.6853 | 12.6851 | 1.00002 | 1.52122e-05 | 2.75298e-06 | 5.52571 | 5.93256e-06 | True | True | cropped voxel-network conductance check consuming the 3D hydraulic-resistance field when available; not CFD/LBM and not a calibrated pressure-drop measurement |
| N=6000 | 6000 | cropped voxel-network Darcy-Laplace | 12.6853 | 12.6849 | 1.00003 | 3.03764e-05 | 5.54909e-06 | 5.47412 | 1.15243e-05 | True | True | cropped voxel-network conductance check consuming the 3D hydraulic-resistance field when available; not CFD/LBM and not a calibrated pressure-drop measurement |
| N=10000 | 10000 | cropped voxel-network Darcy-Laplace | 12.6853 | 12.6847 | 1.00005 | 5.06777e-05 | 9.17882e-06 | 5.52116 | 1.95207e-05 | True | True | cropped voxel-network conductance check consuming the 3D hydraulic-resistance field when available; not CFD/LBM and not a calibrated pressure-drop measurement |

## table_s10_cropped_flow_permeability_sensitivity

File: `papers/paper2_voxel_topology_clogging/supplementary/table_s10_cropped_flow_permeability_sensitivity.csv`

Rows: 15, columns: 10

| case_label | debris_total_number | conductance_mapping | conductance_exponent | relative_resistance | local_conductance_loss | max_blockage_ratio_in_profile | not_cfd | not_lbm | evidence_boundary |
|---|---|---|---|---|---|---|---|---|---|
| N=3000 | 3000 | g=(1-B)^n | 1 | 1 | 3.4761e-06 | 5.93256e-06 | True | True | exponent sensitivity of a cropped scalar voxel-network conductance proxy; not CFD/LBM and not a calibrated pressure-drop measurement |
| N=3000 | 3000 | g=(1-B)^n | 2 | 1.00001 | 6.95219e-06 | 5.93256e-06 | True | True | exponent sensitivity of a cropped scalar voxel-network conductance proxy; not CFD/LBM and not a calibrated pressure-drop measurement |
| N=3000 | 3000 | g=(1-B)^n | 3 | 1.00001 | 1.04284e-05 | 5.93256e-06 | True | True | exponent sensitivity of a cropped scalar voxel-network conductance proxy; not CFD/LBM and not a calibrated pressure-drop measurement |
| N=3000 | 3000 | g=(1-B)^n | 5 | 1.00002 | 1.73804e-05 | 5.93256e-06 | True | True | exponent sensitivity of a cropped scalar voxel-network conductance proxy; not CFD/LBM and not a calibrated pressure-drop measurement |
| N=3000 | 3000 | g=(1-B)^n | 8 | 1.00003 | 2.78086e-05 | 5.93256e-06 | True | True | exponent sensitivity of a cropped scalar voxel-network conductance proxy; not CFD/LBM and not a calibrated pressure-drop measurement |
| N=6000 | 6000 | g=(1-B)^n | 1 | 1.00001 | 6.94437e-06 | 1.15243e-05 | True | True | exponent sensitivity of a cropped scalar voxel-network conductance proxy; not CFD/LBM and not a calibrated pressure-drop measurement |
| N=6000 | 6000 | g=(1-B)^n | 2 | 1.00001 | 1.38887e-05 | 1.15243e-05 | True | True | exponent sensitivity of a cropped scalar voxel-network conductance proxy; not CFD/LBM and not a calibrated pressure-drop measurement |
| N=6000 | 6000 | g=(1-B)^n | 3 | 1.00002 | 2.0833e-05 | 1.15243e-05 | True | True | exponent sensitivity of a cropped scalar voxel-network conductance proxy; not CFD/LBM and not a calibrated pressure-drop measurement |

## table_s11_benchmark_crosswalk

File: `papers/paper2_voxel_topology_clogging/supplementary/table_s11_benchmark_crosswalk.csv`

Rows: 6, columns: 6

| benchmark_id | reviewer_question | comparable_metric | current_numeric_evidence | comparison_type | cannot_claim |
|---|---|---|---|---|---|
| B01_packed_bed_fines_clogging | Does the numerical bed show fines migration and breakthrough behavior comparable to packed-bed fines-transport studies? | debris diameter, nominal particle Reynolds number, drag-to-weight ratio, final BTC, downstream debris centroid | df=20.0-100.0 um; Re_p=0.21-1.67; Fd/W=3.01-112.86; final BTC=0.000-0.082; x_mean/L=0.208-0.503 | semi-quantitative mechanism benchmark | Not a DEM-CFD replication, not an artificial drag multiplier and not a resolved gas-flow validation. |
| B02_packed_bed_deposition | Can deposition and retention be evaluated beyond a single outlet-count curve? | retention, local blockage profile, deposition/blockage centroid | loading retention=0.982-0.986; sub-voxel max blockage=1.06e-05-3.55e-05; blockage centroid/L=0.352-0.355 | quantitative within-study loading benchmark | Not a universal deposition or loading law because the loading states are single-seed cases. |
| B03_porous_media_clogging_mechanisms | Is breakthrough separated from structural clogging rather than inferred from penetration alone? | first breakthrough time, final BTC, peak blockage, connectivity loss | first BTC time=0.03159 s; representative final BTC=0.018; peak blockage=5.23e-05; loading connectivity loss=0.000-0.000 | mechanistic benchmark against clogging-stage concepts | No universal critical transition is identified in the current cases. |
| B04_topology_morphology_descriptors | Is the pore-structure evidence quantified with reproducible descriptors? | porosity, connected void fraction, outlet-connected fraction, fractal dimension, Euler number | porosity=0.411; largest connected void fraction=0.992; outlet connected fraction=0.992; Df=2.694; Euler=-18225 | quantitative morphology/topology benchmark | These are DEM-derived voxel metrics, not experimental CT measurements. |
| B05_pressure_flow_response | Is hydraulic degradation supported by pressure or flow evidence? | Ergun pressure proxy, voxel-network conductance, cropped-domain conductance, 3D resistance sensitivity, OpenFOAM availability | Ergun profile pressure increase=3.77e-06-1.26e-05; voxel-network conductance loss=0.00-9.18e-06; cropped conductance loss=1.52e-05-5.07e-05; 3D resistance-amplified conductance loss=1.52e-05-0.01; valid OpenFOAM cases=3; OpenFOAM delta-p=453.99-454.94 | bounded cropped-domain pressure benchmark | Returned OpenFOAM pressure drops are not experimental pressure validation, not OpenLB/LBM cross-validation and not pressure-calibrated Ib. |
| B06_fusion_blanket_relevance | Is the case physically relevant to ceramic breeder pebble beds without becoming an unvalidated safety claim? | pebble count, pebble diameter, material stiffness, porosity, connected void fraction, drag-to-weight range and purge-driven fines transport outputs | bed particles=10000; pebble diameter=1 mm; Young's modulus=90 GPa; porosity=0.411; outlet connected fraction=0.992; Fd/W=3.01-112.86; debris inventory=3000-10000 | application-relevance benchmark | Not an experimental blanket test, not a component-scale blanket flow calculation and not an engineering safety qualification. |

## table_s12_dimensionless_mechanism_map

File: `papers/paper2_voxel_topology_clogging/supplementary/table_s12_dimensionless_mechanism_map.csv`

Rows: 9, columns: 23

| evidence_family | case_label | df_over_dp | gas_velocity_m_s | drag_to_weight_ratio | dimensionless_loading | final_BTC | retention | source_fraction | downstream_fraction | x_mean_over_L | x_q99_over_L | x_max_over_L | front_bulk_gap_over_L | final_time_s | blockage_centroid_over_L | max_blockage_ratio | connectivity_loss | Ib_no_pressure | profile_pressure_increase_ratio | voxel_conductance_loss | mechanism_regime | claim_boundary |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drive_state | low_drive_no_breakthrough | 0.025 | 1 | 24.0759 | 0.0455781 | 0 | 1 |  |  | 0.208378 |  |  | 0 |  | 0.208411 | 2.20848e-05 | 0 | 1.10424e-05 |  |  | retention/internal filtering | representative DEM-derived final-state evidence; not a full parameter sweep |
| drive_state | intermediate_drive_weak_breakthrough | 0.0225 | 2 | 59.4465 | 0.0322355 | 0.0183333 | 0.981667 |  |  | 0.35751 |  |  | 0 |  | 0.351818 | 1.0632e-05 | 0 | 5.316e-06 |  |  | breakthrough without topology loss | representative DEM-derived final-state evidence; not a full parameter sweep |
| drive_state | high_drive_stronger_breakthrough | 0.02 | 3 | 112.856 | 0.022016 | 0.082 | 0.918 |  |  | 0.502586 |  |  | 0 |  | 0.487779 | 2.75479e-05 | 0 | 1.37739e-05 |  |  | breakthrough without topology loss | representative DEM-derived final-state evidence; not a full parameter sweep |
| loading_state | N=3000 | 0.0225 | 2 |  | 0.0341719 | 0.0183333 | 0.981667 |  |  | 0.35751 |  |  | 0 |  | 0.351818 | 1.0632e-05 | 0 | 5.316e-06 | 3.77204e-06 | 2.75298e-06 | breakthrough without topology loss | single-seed loading evidence with pressure proxies only; not a calibrated transition |
| loading_state | N=6000 | 0.0225 | 2 |  | 0.0683437 | 0.0141667 | 0.985833 |  |  | 0.359757 |  |  | 0 |  | 0.354261 | 2.0833e-05 | 0 | 1.04165e-05 | 7.60944e-06 | 5.54909e-06 | breakthrough without topology loss | single-seed loading evidence with pressure proxies only; not a calibrated transition |
| loading_state | N=10000 | 0.0225 | 2 |  | 0.113906 | 0.0156 | 0.9844 |  |  | 0.3603 |  |  | 0 |  | 0.354547 | 3.54879e-05 | 0 | 1.77439e-05 | 1.25812e-05 | 9.17882e-06 | breakthrough without topology loss | single-seed loading evidence with pressure proxies only; not a calibrated transition |
| localized_source_state | 906 | 0.1 |  |  | 15 | 0 | 1 | 0.579333 | 0.420333 | 0.395763 | 0.625438 | 0.998104 | 0.372667 | 0.04 |  | 0 | 0 | 0 |  |  | source-retained sparse front | localized-source target-time evidence; supports sparse-front/source-retention mechanism, not a source-position law or critical transition |
| localized_source_state | 907 | 0.1 |  |  | 15 | 0 | 1 | 0.896133 | 0.100933 | 0.612659 | 0.683754 | 0.982607 | 0.298853 | 0.01005 |  | 0 | 0 | 0 |  |  | source-retained sparse front | localized-source target-time evidence; supports sparse-front/source-retention mechanism, not a source-position law or critical transition |

## table_s13_mechanism_claim_table

File: `papers/paper2_voxel_topology_clogging/supplementary/table_s13_mechanism_claim_table.csv`

Rows: 3, columns: 9

| claim_id | mechanism_claim | primary_coordinate | evidence_rows | coordinate_range | response_range | quantitative_support | manuscript_use | boundary |
|---|---|---|---|---|---|---|---|---|
| M01_drive_controls_migration | Increasing Stokes drag-to-weight ratio shifts the debris cloud downstream and increases weak breakthrough. | drag_to_weight_ratio | 3 | 24.076 to 112.86 | BTC=0 to 0.082; x_mean/L=0.20838 to 0.50259 | corr(Fd/W,BTC)=0.982; corr(Fd/W,x_mean/L)=0.992 | Supports the drive-state result and the statement that Fd/W is a compact migration coordinate. | Representative final states only; not a full velocity-size parameter sweep. |
| M02_loading_controls_local_blockage | Increasing dimensionless debris inventory raises local sub-voxel blockage and the pressure-free structural index. | dimensionless_loading | 3 | 0.034172 to 0.11391 | Bmax=1.0632e-05 to 3.5488e-05; Ib0=5.316e-06 to 1.7744e-05 | corr(Phi_f,Bmax)=1.000; corr(Phi_f,Ib0)=1.000 | Supports the loading-scan result without implying a critical transition. | Three single-seed loading states; pressure term is proxy-free and not pressure calibrated. |
| M03_breakthrough_decouples_from_topology_loss | Weak outlet breakthrough and local deposition occur without measurable outlet-connected pore-skeleton loss in the analyzed window. | BTC, Bmax and C_loss considered jointly | 6 | BTC=0 to 0.082; Bmax=1.0632e-05 to 3.5488e-05 | C_loss=0 to 0; outlet_connected=0.999528 to 0.999528 | max(C_loss)=0; min(outlet_connected_fraction)=0.999528 | Supports the central claim that breakthrough is a transport signal, not direct evidence of pore-network clogging. | Pre-clogging window only; no universal critical clogging transition is identified. |

## table_s14_near_threshold_repeat_seed_summary

File: `papers/paper2_voxel_topology_clogging/supplementary/table_s14_near_threshold_repeat_seed_summary.csv`

Rows: 1, columns: 12

| formal_processed_count | final_BTC_mean | final_BTC_std | final_BTC_min | final_BTC_max | final_retention_mean | final_retention_std | first_breakthrough_elapsed_s_mean | first_breakthrough_elapsed_s_std | max_blockage_ratio_mean | max_blockage_ratio_std | evidence_boundary |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 0.0164444 | 0.00271484 | 0.0133333 | 0.0183333 | 0.983556 | 0.00271484 | 0.03807 | 0.00140296 | 5.82317e-06 | 1.17452e-07 | near-threshold fixed-bed repeat-seed uncertainty only; not a critical transition, not a full parameter sweep and not pressure-calibrated evidence |

## table_s15_3d_resistance_amplification_sensitivity

File: `papers/paper2_voxel_topology_clogging/supplementary/table_s15_3d_resistance_amplification_sensitivity.csv`

Rows: 18, columns: 11

| case_label | debris_total_number | resistance_mapping | amplification_factor | relative_resistance | local_conductance_loss | mean_excess_resistance | max_excess_resistance | not_cfd | not_lbm | evidence_boundary |
|---|---|---|---|---|---|---|---|---|---|---|
| N=3000 | 3000 | R_eff=1+factor*(R-1); g=1/R_eff | 1 | 1.00002 | 1.52122e-05 | 1.46824e-05 | 2.57492e-05 | True | True | 3D hydraulic-resistance amplification sensitivity in a scalar voxel-network Darcy-Laplace model; not CFD/LBM and not a calibrated pressure-drop measurement |
| N=3000 | 3000 | R_eff=1+factor*(R-1); g=1/R_eff | 3 | 1.00005 | 4.56349e-05 | 1.46824e-05 | 2.57492e-05 | True | True | 3D hydraulic-resistance amplification sensitivity in a scalar voxel-network Darcy-Laplace model; not CFD/LBM and not a calibrated pressure-drop measurement |
| N=3000 | 3000 | R_eff=1+factor*(R-1); g=1/R_eff | 10 | 1.00015 | 0.0001521 | 1.46824e-05 | 2.57492e-05 | True | True | 3D hydraulic-resistance amplification sensitivity in a scalar voxel-network Darcy-Laplace model; not CFD/LBM and not a calibrated pressure-drop measurement |
| N=3000 | 3000 | R_eff=1+factor*(R-1); g=1/R_eff | 30 | 1.00046 | 0.000456161 | 1.46824e-05 | 2.57492e-05 | True | True | 3D hydraulic-resistance amplification sensitivity in a scalar voxel-network Darcy-Laplace model; not CFD/LBM and not a calibrated pressure-drop measurement |
| N=3000 | 3000 | R_eff=1+factor*(R-1); g=1/R_eff | 100 | 1.00152 | 0.00151892 | 1.46824e-05 | 2.57492e-05 | True | True | 3D hydraulic-resistance amplification sensitivity in a scalar voxel-network Darcy-Laplace model; not CFD/LBM and not a calibrated pressure-drop measurement |
| N=3000 | 3000 | R_eff=1+factor*(R-1); g=1/R_eff | 300 | 1.00456 | 0.00454292 | 1.46824e-05 | 2.57492e-05 | True | True | 3D hydraulic-resistance amplification sensitivity in a scalar voxel-network Darcy-Laplace model; not CFD/LBM and not a calibrated pressure-drop measurement |
| N=6000 | 6000 | R_eff=1+factor*(R-1); g=1/R_eff | 1 | 1.00003 | 3.03764e-05 | 2.93609e-05 | 5.00679e-05 | True | True | 3D hydraulic-resistance amplification sensitivity in a scalar voxel-network Darcy-Laplace model; not CFD/LBM and not a calibrated pressure-drop measurement |
| N=6000 | 6000 | R_eff=1+factor*(R-1); g=1/R_eff | 3 | 1.00009 | 9.11235e-05 | 2.93609e-05 | 5.00679e-05 | True | True | 3D hydraulic-resistance amplification sensitivity in a scalar voxel-network Darcy-Laplace model; not CFD/LBM and not a calibrated pressure-drop measurement |

## table_s16_reviewer_evidence_closure_matrix

File: `papers/paper2_voxel_topology_clogging/supplementary/table_s16_reviewer_evidence_closure_matrix.csv`

Rows: 11, columns: 9

| risk_id | severity | closure_state | linked_claims | linked_benchmarks | primary_artifacts | closure_evidence | boundary_to_preserve | submission_decision |
|---|---|---|---|---|---|---|---|---|
| R01 | major | requires_review | C03_breakthrough_not_clogging; C07_pressure_proxy_small_response; C08_openfoam_pressure_returned | B03_porous_media_clogging_mechanisms; B05_pressure_flow_response | Fig. 6; Fig. S3; Fig. S22; Fig. S23; Tables S6-S7, S10-S11, S15 | Ib is kept pressure-free; Ergun, scalar voxel-network and cropped-domain OpenFOAM checks are reported as bounded pressure-flow evidence. | The manuscript states that Ib is a pressure-free structural pre-screening index and that the Ergun result is only a proxy. | revise_before_submission |
| R02 | major | requires_review | C03_breakthrough_not_clogging; C06_loading_increases_local_blockage; C09_no_universal_critical_transition | B02_packed_bed_deposition; B03_porous_media_clogging_mechanisms | Fig. 7; Fig. 9; Fig. 10; Tables S12-S14 | Current cases show migration, weak breakthrough and local blockage with zero measurable connectivity loss; transition language is explicitly excluded. | The manuscript frames the result as pre-clogging migration/filtering and states that identifying a bed-scale clogging threshold requires higher loading, localized release, or coupled flow. | revise_before_submission |
| R03 | major | bounded_by_current_evidence | C06_loading_increases_local_blockage | B02_packed_bed_deposition | Fig. 7; Fig. 9; Table S1; Table S14 | The loading scan is used as bounded single-seed response evidence; repeat-seed evidence is confined to the near-threshold fixed-bed window. | The manuscript says the loading data are bounded loading responses rather than a monotonic breakthrough law. | acceptable_if_claims_remain_bounded |
| R04 | major | closed_by_current_evidence | C05_internal_source_retention | B02_packed_bed_deposition; B03_porous_media_clogging_mechanisms | Fig. 4; Fig. 5; Fig. S8-S10; Fig. S19; Tables S1, S12-S13 | All three localized-release production rows reached target time and are interpreted as mechanism evidence rather than a source-position law. | 3/3 localized-release production jobs reached target physical time; the manuscript treats them as mechanism evidence rather than a fitted source-location law. | acceptable |
| R05 | major | bounded_by_current_evidence | C01_baseline_connected_pore_skeleton | B04_topology_morphology_descriptors | Fig. 1; Fig. 2; Fig. S1; Tables S2-S4 | The manuscript and figure labels use DEM-derived voxel reconstruction or pore field wording, not experimental CT wording. | The manuscript uses DEM-derived pore reconstruction and explicitly rejects experimental computed-tomography interpretation. | acceptable_for_numerical_study |
| R06 | major | bounded_by_current_evidence | C02_drag_to_weight_controls_migration; C08_openfoam_pressure_returned | B01_packed_bed_fines_clogging; B05_pressure_flow_response | Fig. 3; Fig. S16; Fig. S23; Fig. S24; Fig. S26; Tables S11-S12, S18 | Drag-to-weight trends are presented as one-way forcing results; Supplementary Table S18 documents debris diameter, nominal particle Reynolds number and recomputed Stokes drag-to-weight range; OpenFOAM checks are cropped-domain pressure-flow checks, not two-way DEM-CFD. | The manuscript states that the forcing is one-way Stokes drag, reports a dimensional drag-scaling audit, and does not solve the local gas field. | acceptable_as_first_mechanistic_model |
| R07 | minor | bounded_by_current_evidence | C03_breakthrough_not_clogging; C06_loading_increases_local_blockage | B02_packed_bed_deposition; B06_fusion_blanket_relevance | Methods; Fig. 7; Table S1 | Transport cases use a fixed compacted skeleton so debris migration is not confounded by large-pebble rearrangement. | Formal transport cases use a fixed compacted skeleton so the response is attributed to debris parameters. | acceptable |
| R08 | minor | bounded_by_current_evidence | C01_baseline_connected_pore_skeleton; C03_breakthrough_not_clogging | B03_porous_media_clogging_mechanisms; B04_topology_morphology_descriptors | Figure provenance manifest; Fig. 1; Fig. 6; Fig. 8; Fig. 11 | Figure provenance and revised captions keep panels data-linked and boundary-labeled without large explanatory text blocks. | A figure provenance manifest records source scripts, exports, and claim boundaries for each figure. | acceptable_with_final_visual_QA |

## table_s17_mechanism_state_classifier

File: `papers/paper2_voxel_topology_clogging/supplementary/table_s17_mechanism_state_classifier.csv`

Rows: 9, columns: 17

| evidence_family | case_label | final_BTC | retention | source_fraction | x_mean_over_L | x_q99_over_L | x_max_over_L | front_bulk_gap_over_L | max_blockage_ratio | connectivity_loss | Ib_no_pressure | profile_pressure_increase_ratio | voxel_conductance_loss | mechanism_state | decision_basis | classification_boundary |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drive_state | low_drive_no_breakthrough | 0 | 1 |  | 0.208378 |  |  | 0 | 2.20848e-05 | 0 | 1.10424e-05 |  |  | internal retention with local deposition | Bmax>=1e-05 | Rule-based classification of existing DEM-derived evidence only; not a fitted transition law, not pressure-calibrated Ib and not experimental validation. |
| drive_state | intermediate_drive_weak_breakthrough | 0.0183333 | 0.981667 |  | 0.35751 |  |  | 0 | 1.0632e-05 | 0 | 5.316e-06 |  |  | breakthrough with local pre-clogging deposition | BTC>=0.01; Bmax>=1e-05 | Rule-based classification of existing DEM-derived evidence only; not a fitted transition law, not pressure-calibrated Ib and not experimental validation. |
| drive_state | high_drive_stronger_breakthrough | 0.082 | 0.918 |  | 0.502586 |  |  | 0 | 2.75479e-05 | 0 | 1.37739e-05 |  |  | breakthrough with local pre-clogging deposition | BTC>=0.01; Bmax>=1e-05 | Rule-based classification of existing DEM-derived evidence only; not a fitted transition law, not pressure-calibrated Ib and not experimental validation. |
| loading_state | N=3000 | 0.0183333 | 0.981667 |  | 0.35751 |  |  | 0 | 1.0632e-05 | 0 | 5.316e-06 | 3.77204e-06 | 2.75298e-06 | breakthrough with local pre-clogging deposition | BTC>=0.01; Bmax>=1e-05; bounded hydraulic proxy available | Rule-based classification of existing DEM-derived evidence only; not a fitted transition law, not pressure-calibrated Ib and not experimental validation. |
| loading_state | N=6000 | 0.0141667 | 0.985833 |  | 0.359757 |  |  | 0 | 2.0833e-05 | 0 | 1.04165e-05 | 7.60944e-06 | 5.54909e-06 | breakthrough with local pre-clogging deposition | BTC>=0.01; Bmax>=1e-05; bounded hydraulic proxy available | Rule-based classification of existing DEM-derived evidence only; not a fitted transition law, not pressure-calibrated Ib and not experimental validation. |
| loading_state | N=10000 | 0.0156 | 0.9844 |  | 0.3603 |  |  | 0 | 3.54879e-05 | 0 | 1.77439e-05 | 1.25812e-05 | 9.17882e-06 | breakthrough with local pre-clogging deposition | BTC>=0.01; Bmax>=1e-05; bounded hydraulic proxy available | Rule-based classification of existing DEM-derived evidence only; not a fitted transition law, not pressure-calibrated Ib and not experimental validation. |
| localized_source_state | 906 | 0 | 1 | 0.579333 | 0.395763 | 0.625438 | 0.998104 | 0.372667 | 0 | 0 | 0 |  |  | source-retained sparse-front slowdown | front_gap>=0.25 and xmax>=0.95; source_fraction>=0.5 | Rule-based classification of existing DEM-derived evidence only; not a fitted transition law, not pressure-calibrated Ib and not experimental validation. |
| localized_source_state | 907 | 0 | 1 | 0.896133 | 0.612659 | 0.683754 | 0.982607 | 0.298853 | 0 | 0 | 0 |  |  | source-retained sparse-front slowdown | front_gap>=0.25 and xmax>=0.95; source_fraction>=0.5 | Rule-based classification of existing DEM-derived evidence only; not a fitted transition law, not pressure-calibrated Ib and not experimental validation. |

## table_s18_drag_scaling_summary

File: `papers/paper2_voxel_topology_clogging/supplementary/table_s18_drag_scaling_summary.csv`

Rows: 9, columns: 14

| evidence_family | case_label | df_over_dp | gas_velocity_m_s | debris_diameter_um | particle_Re_superficial | stokes_drag_to_weight_recomputed | source_drag_to_weight_ratio | relative_difference_from_source | final_BTC | max_blockage_ratio | connectivity_loss | stokes_regime_note | model_boundary |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| drive_state | low_drive_no_breakthrough | 0.025 | 1 | 25 | 0.209184 | 24.0759 | 24.0759 | 0 | 0 | 2.20848e-05 | 0 | low-Re Stokes-scale forcing | One-way Stokes-scale forcing audit only; no resolved pore-scale gas redistribution, no artificial drag multiplier and no pressure-calibrated transition claim. |
| drive_state | intermediate_drive_weak_breakthrough | 0.0225 | 2 | 22.5 | 0.376531 | 59.4465 | 59.4465 | 0 | 0.0183333 | 1.0632e-05 | 0 | low-Re Stokes-scale forcing | One-way Stokes-scale forcing audit only; no resolved pore-scale gas redistribution, no artificial drag multiplier and no pressure-calibrated transition claim. |
| drive_state | high_drive_stronger_breakthrough | 0.02 | 3 | 20 | 0.502041 | 112.856 | 112.856 | 1.25921e-16 | 0.082 | 2.75479e-05 | 0 | low-Re Stokes-scale forcing | One-way Stokes-scale forcing audit only; no resolved pore-scale gas redistribution, no artificial drag multiplier and no pressure-calibrated transition claim. |
| loading_state | N=3000 | 0.0225 | 2 | 22.5 | 0.376531 | 59.4465 |  |  | 0.0183333 | 1.0632e-05 | 0 | low-Re Stokes-scale forcing | One-way Stokes-scale forcing audit only; no resolved pore-scale gas redistribution, no artificial drag multiplier and no pressure-calibrated transition claim. |
| loading_state | N=6000 | 0.0225 | 2 | 22.5 | 0.376531 | 59.4465 |  |  | 0.0141667 | 2.0833e-05 | 0 | low-Re Stokes-scale forcing | One-way Stokes-scale forcing audit only; no resolved pore-scale gas redistribution, no artificial drag multiplier and no pressure-calibrated transition claim. |
| loading_state | N=10000 | 0.0225 | 2 | 22.5 | 0.376531 | 59.4465 |  |  | 0.0156 | 3.54879e-05 | 0 | low-Re Stokes-scale forcing | One-way Stokes-scale forcing audit only; no resolved pore-scale gas redistribution, no artificial drag multiplier and no pressure-calibrated transition claim. |
| localized_source_state | 906 | 0.1 | 2 | 100 | 1.67347 | 3.00948 |  |  | 0 | 0 | 0 | finite-Re correction may be relevant | One-way Stokes-scale forcing audit only; no resolved pore-scale gas redistribution, no artificial drag multiplier and no pressure-calibrated transition claim. |
| localized_source_state | 907 | 0.1 | 2 | 100 | 1.67347 | 3.00948 |  |  | 0 | 0 | 0 | finite-Re correction may be relevant | One-way Stokes-scale forcing audit only; no resolved pore-scale gas redistribution, no artificial drag multiplier and no pressure-calibrated transition claim. |

## table_s19_pressure_evidence_ladder

File: `papers/paper2_voxel_topology_clogging/supplementary/table_s19_pressure_evidence_ladder.csv`

Rows: 6, columns: 10

| level | evidence_class | model_or_data | case_count | response_metric | response_range | supports | cannot_claim | primary_artifacts | manuscript_boundary |
|---|---|---|---|---|---|---|---|---|---|
| L0 | pressure-free structural screen | local blockage plus outlet-connectivity loss | 3 | Ib_no_pressure | 5.32e-06-1.77e-05 | The present loading cases remain far below the pressure-free screening reference. | Does not measure pressure, flow redistribution or hydraulic safety margin. | papers/paper2_voxel_topology_clogging/tables/paper2_fig4_loading_summary_source.csv; Fig. 7 | Use as a pressure/flow evidence ladder for bounded hydraulic-consequence discussion only; not pressure-calibrated Ib, and do not collapse the levels into a critical-clogging transition. |
| L1 | packed-bed closure proxy | Ergun relation with local effective porosity from sub-voxel blockage | 3 | profile_pressure_increase_ratio | 3.77e-06-1.26e-05 | Local blockage produces only a perturbative pressure-gradient change under a conventional closure. | Not CFD, not measured pressure and not used to calibrate Ib. | papers/paper2_voxel_topology_clogging/tables/paper2_pressure_proxy_source.csv; Table S6 | Use as a pressure/flow evidence ladder for bounded hydraulic-consequence discussion only; not pressure-calibrated Ib, and do not collapse the levels into a critical-clogging transition. |
| L2 | scalar connected-pore conductance proxy | voxel-network Darcy-Laplace solve on the connected pore voxels | 4 | conductance_loss | 0.00e+00-9.18e-06 | The connected pore skeleton has only small conductance loss under the mapped blockage field. | Not Navier-Stokes CFD, not LBM and not pressure-calibrated permeability. | papers/paper2_voxel_topology_clogging/tables/paper2_voxel_pressure_pilot_source.csv; Table S7 | Use as a pressure/flow evidence ladder for bounded hydraulic-consequence discussion only; not pressure-calibrated Ib, and do not collapse the levels into a critical-clogging transition. |
| L3 | cropped scalar-flow sensitivity | local peak-blockage cropped domains with conductance mapping g=(1-B)^n | 3 | local_conductance_loss | 3.48e-06-9.27e-05 | The local peak-blockage domains remain perturbative across conductance exponents. | Not CFD, not LBM and not a calibrated pressure-drop measurement. | papers/paper2_voxel_topology_clogging/tables/paper2_cropped_flow_permeability_sensitivity_source.csv; Table S10 | Use as a pressure/flow evidence ladder for bounded hydraulic-consequence discussion only; not pressure-calibrated Ib, and do not collapse the levels into a critical-clogging transition. |
| L4 | 3D resistance-amplification stress test | reduced scalar voxel-network solve with amplified hydraulic-resistance fields | 3 | local_conductance_loss | 1.52e-05-0.015 | Even amplified excess resistance remains below a large conductance-loss response in the current window. | Not OpenFOAM CFD, not LBM, not measured pressure and not pressure-calibrated Ib. | papers/paper2_voxel_topology_clogging/tables/paper2_3d_resistance_amplification_sensitivity_source.csv; Table S15; Fig. S22 | Use as a pressure/flow evidence ladder for bounded hydraulic-consequence discussion only; not pressure-calibrated Ib, and do not collapse the levels into a critical-clogging transition. |
| L5 | returned cropped-domain OpenFOAM numerical check | OpenFOAM Darcy-Forchheimer porous-force runs on peak-blockage cropped domains | 3 | relative_delta_p_to_first_valid_case | 1-1 | Returned pressure drops change weakly across the three current peak-blockage handoff cases. | Not experimental validation, not blanket-scale CFD and not pressure-calibrated safety evidence. | papers/paper2_voxel_topology_clogging/tables/paper2_openfoam_pressure_evidence_source.csv; Table S11; Figs. S23-S24, S26 | Use as a pressure/flow evidence ladder for bounded hydraulic-consequence discussion only; not pressure-calibrated Ib, and do not collapse the levels into a critical-clogging transition. |

## Evidence Boundary

The localized internal-release production table distinguishes partial production continuations from target-time-completed production. Partial continuations are useful for stability and mechanism tracking, but they should not be cited as completed target-time production evidence.

The pressure-proxy table uses the conventional Ergun relation applied to sub-voxel blockage profiles. It is included for hydraulic traceability only and should not be cited as CFD, measured pressure, or pressure-calibrated Ib evidence.

The voxel-network pressure-pilot table solves a scalar Darcy-Laplace problem on the connected pore voxels. It is pressure-informed structural evidence, not Navier-Stokes CFD, not LBM and not a calibrated permeability measurement.

The cropped flow-domain table records pore-domain input files prepared for future pressure-flow solvers. These cropped domains are not solver results.

The cropped flow permeability table uses the same scalar voxel-network model on local peak-blockage domains. It is a local sensitivity check, not CFD, not LBM and not a calibrated pressure-drop measurement.

The cropped flow permeability-sensitivity table varies the conductance exponent in `g=(1-B)^n`. It is a proxy robustness check, not a substitute for resolved pore-scale flow.

The benchmark crosswalk table maps reviewer-facing benchmark questions to comparable metrics and current numerical evidence. It is a comparison guide, not a claim that the present cases numerically reproduce the cited studies.

The dimensionless mechanism-map table is a derived synthesis of existing drive-state and loading-state evidence. It should not be cited as a full parameter sweep, pressure-calibrated transition map, or new DEM/CFD result.

The mechanism claim table converts the dimensionless map into reviewer-facing claim rows. It is a derived evidence guide for the Results and Discussion, not a new simulation or a universal transition criterion.

The near-threshold repeat-seed table summarizes stochastic variability across formal processed fixed-bed repeats. It should not be cited as a critical-transition law, a full parameter sweep, or pressure-calibrated evidence.

The 3D resistance-amplification table varies the excess hydraulic-resistance field in a scalar voxel-network model. It is a reduced sensitivity test, not OpenFOAM CFD, not LBM, not measured pressure and not pressure-calibrated Ib evidence.

The reviewer evidence-closure matrix links plausible reviewer objections to current claim, benchmark, figure and table evidence. It is a response-planning and audit table, not a new validation layer and not a reason to remove the listed boundary wording.

The mechanism-state classifier table converts existing dimensionless mechanism-map rows into explicit rule-based state labels. It is a reviewer-facing interpretation aid, not a fitted transition law, not a universal phase diagram and not pressure-calibrated Ib evidence.

The drag-scaling table recomputes debris diameter, nominal particle Reynolds number and Stokes drag-to-weight ratio from the shared physical parameters. It is a model-boundary audit for one-way Stokes forcing, not resolved pore-scale gas flow and not evidence for an artificial drag multiplier.

The pressure/flow evidence-ladder table separates pressure-free structural screening, Ergun closure proxies, scalar voxel-network checks, resistance-amplification tests and returned cropped-domain OpenFOAM checks. It is a boundary table, not validation-grade flow evidence and not pressure-calibrated Ib.
