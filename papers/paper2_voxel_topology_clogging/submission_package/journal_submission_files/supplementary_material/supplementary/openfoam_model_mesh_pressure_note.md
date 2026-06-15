# OpenFOAM Cropped-Domain Model, Mesh and Pressure-Check Note

This note links the OpenFOAM pressure-check figure, the main-text ParaView model/mesh render, the supplementary render set and the tabulated solver outputs. It is intended for reviewer traceability and should be read with main-text Fig. 6, Supplementary Figs. S23--S24, S26 and Supplementary Table S11.

## What Fig. S24 Shows

Fig. S24 visualizes one representative returned OpenFOAM cropped-domain case, `N10000_peak_blockage`, using ParaView. Panel a shows the solid-interface surface and computational-domain outline. Panel b shows a central mesh slice through the cropped domain, including the locally refined snappyHexMesh cells around the solid interface.

The render documents the geometry and mesh structure used for the bounded pressure-flow check. It does not introduce a new pressure value, a new DEM result or an experimental validation image.

The main-text figure, `paper2_openfoam_model_mesh_main`, is assembled from the same ParaView renders. It keeps the representative domain and central mesh slice, and adds a local mesh-detail crop for readability at journal width. This main-text figure documents model and mesh context only; it does not add pressure evidence beyond Fig. S23 or new geometry evidence beyond the ParaView render manifest.

## What Fig. S26 Adds

Fig. S26 arranges the three returned OpenFOAM pressure-check cases, `N3000_peak_blockage`, `N6000_peak_blockage` and `N10000_peak_blockage`, into a case-by-case ParaView matrix. The left column shows the cropped-domain render for each case, and the right column shows the corresponding central mesh slice. This comparison is included for geometry/mesh traceability across the returned case set; it does not add pressure evidence beyond the solver outputs summarized in Fig. S23 and Table S11.

## How Fig. S24 Connects to Fig. S23

Fig. S23 reports the returned cropped-domain OpenFOAM pressure response for the 3000, 6000 and 10000 debris handoff cases. The pressure checks use cropped peak-blockage domains and Darcy--Forchheimer porous-force fields derived from the debris-resistance inputs.

Main-text Fig. 6 and Supplementary Figs. S24 and S26 provide the visual mesh/domain context for that OpenFOAM handoff route. They support interpretability of the solver setup but are not used to calculate the pressure-drop trend shown in Fig. S23.

## Evidence Boundary

The OpenFOAM results are bounded numerical checks for cropped domains. They support the manuscript statement that, in the present cases, hydraulic response remains perturbative while local debris deposition and weak breakthrough are already observable.

They should not be described as:

- experimental pressure measurements;
- full-device or blanket-scale CFD validation;
- OpenLB/LBM cross-validation;
- pressure calibration for the structural clogging index `Ib`;
- proof of a universal critical-clogging transition.

## Reproducibility Pointers

- Pressure source data: `papers/paper2_voxel_topology_clogging/tables/paper2_openfoam_pressure_evidence_source.csv`
- Pressure screening table: `papers/paper2_voxel_topology_clogging/tables/paper2_openfoam_pressure_screening_source.csv`
- ParaView render manifest: `papers/paper2_voxel_topology_clogging/figures/openfoam_paraview/N10000_peak_blockage_paraview_render_manifest.json`
- ParaView render script: `papers/paper2_voxel_topology_clogging/scripts/render_openfoam_paraview_figures.py`
- Figure assembly script: `papers/paper2_voxel_topology_clogging/scripts/assemble_openfoam_paraview_figure.py`
- Main-text-style assembly script: `papers/paper2_voxel_topology_clogging/scripts/assemble_openfoam_paraview_main_figure.py`

## Regeneration

```bash
for case in N3000_peak_blockage N6000_peak_blockage N10000_peak_blockage; do
  /Applications/ParaView-5.13.3.app/Contents/bin/pvpython \
    papers/paper2_voxel_topology_clogging/scripts/render_openfoam_paraview_figures.py \
    --case papers/paper2_voxel_topology_clogging/flow_solver_results/openfoam/${case} \
    --out-dir papers/paper2_voxel_topology_clogging/figures/openfoam_paraview \
    --case-label ${case} \
    --width 3600 --height 2400
done

python3 papers/paper2_voxel_topology_clogging/scripts/assemble_openfoam_paraview_figure.py \
  --render-dir papers/paper2_voxel_topology_clogging/figures/openfoam_paraview \
  --case-label N10000_peak_blockage \
  --out papers/paper2_voxel_topology_clogging/figures/paper2_figS24_openfoam_model_mesh \
  --layout horizontal

python3 papers/paper2_voxel_topology_clogging/scripts/assemble_openfoam_paraview_main_figure.py \
  --render-dir papers/paper2_voxel_topology_clogging/figures/openfoam_paraview \
  --case-label N10000_peak_blockage \
  --out papers/paper2_voxel_topology_clogging/figures/paper2_openfoam_model_mesh_main

python3 papers/paper2_voxel_topology_clogging/scripts/assemble_openfoam_paraview_case_matrix.py \
  --render-dir papers/paper2_voxel_topology_clogging/figures/openfoam_paraview \
  --out papers/paper2_voxel_topology_clogging/figures/paper2_figS26_openfoam_case_matrix
```
