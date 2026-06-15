# Paper 2 Benchmark Boundary Matrix

- Rows: `6`
- Status counts: `{"bounded": 2, "supported": 4}`
- Validation-level counts: `{"application_relevance_only": 2, "bounded_positioning": 1, "cropped_domain_screening": 1, "mechanistic_comparison": 1, "within_study_quantitative": 1}`

## Boundary

This matrix is a reviewer-facing benchmark boundary map. It supports comparison and positioning, not experimental validation, resolved gas-flow validation, pressure-calibrated Ib or engineering safety qualification.

## Matrix

| Benchmark | Validation level | Current evidence | What it supports | Remaining gap | Cannot claim |
|---|---|---|---|---|---|
| B01_packed_bed_fines_clogging | mechanistic_comparison | Fd/W=24.08-112.86; final BTC=0.000-0.082; x_mean/L=0.208-0.503 | DEM-derived pore-connectivity and topology diagnostics that separate breakthrough from structural clogging. | Returned cropped-domain OpenFOAM pressure checks are available, but they are screening evidence rather than experimental, LBM/OpenLB or blanket-scale pressure-flow validation. | Not a DEM-CFD replication and not a resolved gas-flow validation. |
| B02_packed_bed_deposition | within_study_quantitative | loading retention=0.982-0.986; sub-voxel max blockage=1.06e-05-3.55e-05; blockage centroid/L=0.352-0.355 | Connects local deposition profiles to DEM-derived outlet-connected void metrics and sub-voxel blockage. | Current deposition-loading scan is single-seed and bounded to 3000-10000 injected debris particles. | Not a universal deposition or loading law because the loading states are single-seed cases. |
| B03_porous_media_clogging_mechanisms | bounded_positioning | first BTC time=0.03159 s; representative final BTC=0.018; peak blockage=5.23e-05; loading connectivity loss=0.000-0.000 | Particle-resolved debris locations plus topology metrics show breakthrough without pore-network degradation in the analyzed window. | Critical clogging transition is not reached in the current data. | No universal critical transition is identified in the current cases. |
| B04_topology_morphology_descriptors | application_relevance_only | porosity=0.411; largest connected void fraction=0.992; outlet connected fraction=0.992; Df=2.694; Euler=-18225 | Applies pore-structure descriptors to a DEM-generated Li4SiO4 pebble bed and connects them to debris transport metrics. | Descriptors are numerical reconstruction metrics, not experimental CT measurements. | These are DEM-derived voxel metrics, not experimental CT measurements. |
| B05_pressure_flow_response | cropped_domain_screening | Ergun profile pressure increase=3.77e-06-1.26e-05; voxel-network conductance loss=0.00-9.18e-06; cropped conductance loss=1.52e-05-5.07e-05; 3D resistance-amplified conductance loss=1.52e-05-0.01; valid OpenFOAM cases=3; OpenFOAM delta-p=453.99-454.94 | Combines Ergun and voxel-network hydraulic proxies with returned cropped-domain OpenFOAM pressure checks for the peak-blockage handoff cases. | The returned OpenFOAM evidence is cropped-domain numerical screening, not experimental validation, not OpenLB/LBM cross-validation and not a blanket-scale pressure-flow solution. | Returned OpenFOAM pressure drops are not experimental pressure validation, not OpenLB/LBM cross-validation and not pressure-calibrated Ib. |
| B06_fusion_blanket_relevance | application_relevance_only | bed particles=10000; pebble diameter=1 mm; Young's modulus=90 GPa; debris inventory=3000-10000 | Uses 1 mm, physically stiff Li4SiO4 pebbles and bounded purge-driven debris transport analysis. | Not a validated blanket safety limit and not an experimental blanket test. | Not an experimental blanket test and not an engineering safety qualification. |

## Reviewer-use rule

Use quantitative rows as within-study evidence, mechanistic rows as positioning, and proxy rows only as bounded hydraulic scale checks. Do not convert any row into a validation claim unless the listed remaining gap is closed.
