# CES-submission-v1.0

Tag: `v1.0.0-ces-submission`

Archived DOI: `10.5281/zenodo.20699272`

This release contains the lightweight code and processed data package supporting the CES-targeted manuscript on DEM-derived fine-debris transport and pore-network clogging indicators in Li4SiO4 pebble beds.

## Included

- Manuscript LaTeX source and compiled PDF preview.
- Main and supplementary figure exports.
- Processed figure source tables and derived diagnostic tables.
- Paper-specific figure/data scripts.
- Shared Python modules for DEM dump parsing, transport metrics, voxel topology, fractal analysis and model utilities.
- Selected lightweight DEM input decks and repeat-case setup files.

## Not Included

- Full raw DEM dump and restart files.
- A pressure-calibrated clogging criterion.
- A universal clogging transition law.

## Boundary

The release supports a staged assessment interpretation:

1. BTC: transport/contamination indicator.
2. Local blockage: deposition-localization indicator.
3. Connected-pore loss: structural-degradation indicator.
4. Pressure-drop increase: hydraulic confirmation.

The workflow remains bounded to the studied parameter space, present DEM assumptions, finite voxel resolution and lack of resolved hydraulic feedback.
