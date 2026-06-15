# Paper 2 Cropped Flow-Domain Inputs

These folders contain cropped DEM-derived voxel pore domains centred on peak local blockage locations in the loading scan.

Default half-width: 0.004 m.

| Case | x window (m) | shape | porosity | through-connected pore fraction | max B | max resistance multiplier |
|---|---:|---:|---:|---:|---:|---:|
| N=3000 | 0.00825-0.0165 | 33x60x53 | 0.407118 | 0.990731 | 5.933e-06 | 1.00003 |
| N=6000 | 0.00825-0.0165 | 33x60x53 | 0.407118 | 0.990731 | 1.152e-05 | 1.00005 |
| N=10000 | 0.00825-0.0165 | 33x60x53 | 0.407118 | 0.990731 | 1.952e-05 | 1.00008 |

Boundary: these files prepare reproducible local pore domains and debris-induced hydraulic-resistance fields for later OpenFOAM/OpenLB/LBM or voxel-network calculations. They are not pressure-drop evidence in the current manuscript.
