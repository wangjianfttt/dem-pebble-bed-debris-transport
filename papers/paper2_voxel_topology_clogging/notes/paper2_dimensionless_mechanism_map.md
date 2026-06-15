# Dimensionless Mechanism Map

This derived note combines existing Paper 2 evidence into a dimensionless mechanism map. It does not add new DEM or CFD data.

## Main Result

- The available drive-state rows support drag-to-weight ratio as a compact migration coordinate.
- The available loading rows show increasing local blockage with dimensionless debris inventory.
- Connectivity loss remains zero in the present window, so these rows support a pre-clogging transport/filtering regime only.

## Summary Metrics

- Rows: 9
- Drive-state rows: 3
- Loading-state rows: 3
- Localized-source rows: 3
- Mechanism regimes: `['breakthrough without topology loss', 'retention/internal filtering', 'source-retained sparse front']`
- Maximum final BTC: `0.082`
- Maximum local blockage ratio: `3.54879e-05`
- Maximum front-bulk gap: `0.574439`
- Maximum connectivity loss: `0`

## Boundary

Derived synthesis from existing Paper 2 tables; no new DEM or CFD result.
The map is not a universal transition diagram, not a pressure-calibrated safety limit, and not experimental CT evidence.

## Source Table

`papers/paper2_voxel_topology_clogging/tables/paper2_dimensionless_mechanism_map_source.csv`

## Drive-State Correlations

- FdW_vs_final_BTC: `0.981588`
- FdW_vs_x_mean_over_L: `0.992231`
- FdW_vs_blockage_centroid_over_L: `0.991280`

## Loading-State Correlations

- dimensionless_loading_vs_max_blockage: `0.999784`
- debris_count_vs_Ib_no_pressure: `0.999784`
- debris_count_vs_connectivity_loss: `constant input/output`

## Localized-Source Correlations

- source_fraction_vs_downstream_fraction: `-0.999993`
- source_fraction_vs_front_bulk_gap: `0.254605`
- downstream_fraction_vs_x_mean: `-0.341307`
