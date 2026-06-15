# Cropped Flow-Domain Input

This directory contains a cropped DEM-derived voxel pore domain for later pressure-flow solvers.

- `voxel_crop.npz`: voxel labels, where 0 is pore and non-zero values are solid/debris labels.
- `pore_mask.npy`: uint8 pore mask, where 1 is pore and 0 is solid.
- `metadata.json`: voxel size, physical crop bounds and array shape.

Boundary: this is an input domain only. It is not a CFD, LBM or measured pressure result.
