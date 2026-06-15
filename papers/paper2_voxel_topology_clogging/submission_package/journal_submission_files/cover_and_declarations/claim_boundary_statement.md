# Claim Boundary Statement

This document defines the claims that are supported by the current Paper 2 evidence package and the claims that must not be made without additional simulations, pressure calibration or experimental data.

## Supported Claims

- The 10,000-particle Li4SiO4 DEM bed has a DEM-derived voxel porosity of 0.4114, largest connected void fraction of 0.9921 and fractal dimension of 2.694.
- Increasing drag-to-weight ratio shifts the debris cloud downstream and can produce weak outlet breakthrough.
- In the representative breakthrough states, the outlet-connected pore skeleton remains retained in the current voxel-skeleton metric.
- Increasing debris loading from 3000 to 10000 particles increases local sub-voxel blockage but keeps the pressure-free clogging index at `O(1e-5)`.
- The completed 906, 907 and 908 localized-release target rows show retained source-zone populations, slow downstream leakage and sparse-front formation without outlet crossing.
- The high-inventory 908 case shows that a rare front can approach the outlet while the population bulk remains near the source.
- Returned cropped-domain OpenFOAM checks are available as bounded numerical pressure-flow screening evidence for peak-blockage handoff cases.
- The current result supports a pre-clogging migration/filtering regime.
- fine-particle breakthrough, local debris accumulation and pore-network degradation are separable responses in the present DEM-derived reconstruction framework.

## Claims Not Supported By Current Evidence

- A universal critical clogging transition.
- A pressure-calibrated safety criterion.
- Experimental CT validation.
- A monotonic debris-loading law.
- A complete source-location phase map.
- Pore-resolved purge-gas redistribution or two-way gas-particle coupling.

## Exact Language To Prefer

- "DEM-derived voxel reconstruction" rather than "CT".
- "Voxel-based pore-structure analysis" rather than "experimental imaging".
- "Pressure-free structural pre-screening index" rather than "pressure-calibrated clogging index".
- "Pre-clogging migration/filtering regime" rather than "critical clogging transition".
- "One-way Stokes drag" rather than "resolved gas flow".

## Current Highest-Risk Claims

1. Localized release: the 906/907/908 target rows support retained-bulk/sparse-front decoupling, but they do not define a complete source-position or source-inventory scaling law.
2. Clogging index: cropped-domain OpenFOAM pressure checks are available, but the pressure term is still not calibrated against experimental, LBM/OpenLB or blanket-scale flow evidence.
3. Loading scan: the three loading states are single-seed responses and should not be used to infer a universal law.

## Recommended One-Sentence Scope

This paper provides a DEM-derived voxel-topology framework for interpreting fine-debris migration and retention in a Li4SiO4 pebble bed and shows that the current cases remain in a pre-clogging migration/filtering regime rather than a pressure-calibrated critical-clogging transition.
