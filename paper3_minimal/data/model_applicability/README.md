# Model-applicability diagnostics

This directory contains processed data used to define what may and may not be
inferred from the unresolved CFD--DEM calculation.

## Contents

- `release_zone/`: 10, 15 and 20 cells per pebble diameter grid summaries and
  carrier fields filtered to the production CFD-cell scale.
- `interior_zone/`: corresponding 15 and 20 cells per pebble diameter results
  in an interior bed window, away from the upstream cut plane.
- `occupied_positions/`: 1,079 points valid in both the production and
  pore-resolved carrier fields, selected from 1,229 stratified fine-particle
  records.

The released bins allow the axial-velocity and superficial-flux relative-L2
differences to be recomputed. The occupied-position table allows the reported
fixed-coefficient force-magnitude ratio and direction-reversal fraction to be
recomputed.

## Interpretation boundary

The carrier-field calculations resolve the frozen pebble surfaces, not the
surfaces of the transported fines. In the occupied-position calculation, the
logged force-per-slip coefficient and production particle velocity are held
fixed while only the sampled carrier velocity is replaced. The result is
therefore a carrier-field sensitivity diagnostic. It must not be interpreted
as a corrected drag closure or direct validation of fine-particle surface
traction.

Raw OpenFOAM cases, processor directories, particle dumps, restart files and
full logs are excluded. Absolute local and remote paths were removed from the
released JSON files.
