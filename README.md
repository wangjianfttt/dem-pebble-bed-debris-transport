# DEM Pebble-Bed Debris Transport

Code and lightweight processed data for the manuscript:

**Separating breakthrough from pore-network clogging indicators in gas-driven fine-debris transport through Li4SiO4 pebble beds**

This repository supports a bounded DEM-derived workflow for fine-debris transport, deposition, pore-network reconstruction and staged clogging assessment in a Li4SiO4 ceramic breeder pebble bed. The workflow separates:

- BTC as a transport/contamination indicator;
- local blockage as a deposition-localization indicator;
- connected-pore loss as a structural-degradation indicator;
- pressure-drop increase as hydraulic confirmation.

The repository does not provide a universal clogging transition law, a safety criterion or a pressure-calibrated failure model. The manuscript conclusions are bounded to the studied parameter space, present DEM assumptions, finite voxel resolution and lack of resolved two-way hydraulic feedback.

## Repository Contents

- `src/`: shared Python utilities for DEM dump parsing, voxelization, topology metrics, transport metrics and model fitting.
- `papers/paper2_voxel_topology_clogging/latex/`: manuscript source and compiled PDF preview.
- `papers/paper2_voxel_topology_clogging/scripts/`: paper-specific data mining, figure generation and audit scripts.
- `papers/paper2_voxel_topology_clogging/tables/`: processed figure source tables and derived metric tables.
- `papers/paper2_voxel_topology_clogging/data/`: processed JSON/CSV audit and result files.
- `papers/paper2_voxel_topology_clogging/figures/`: main and supplementary figure exports.
- `papers/paper2_voxel_topology_clogging/supplementary/`: supplementary tables and figure catalogue.
- `cases/`: selected lightweight DEM input decks and repeat-case setup files.

Large raw DEM dump/restart files are not included in this lightweight repository because of size. They are retained by the authors and can be requested for audit or reproduction needs.

## Archived DOI

This repository release is archived on Zenodo:

**DOI:** [10.5281/zenodo.20699272](https://doi.org/10.5281/zenodo.20699272)

## Quick Start

Create a Python environment with common scientific packages:

```bash
python -m pip install numpy pandas scipy matplotlib pyyaml pytest
```

Run selected paper scripts from the repository root, for example:

```bash
python papers/paper2_voxel_topology_clogging/scripts/plot_additional_mechanism_figures.py
python papers/paper2_voxel_topology_clogging/scripts/audit_abstract_evidence_alignment.py
python papers/paper2_voxel_topology_clogging/scripts/audit_main_figure_order.py
```

Compile the manuscript if a TeX distribution is available:

```bash
cd papers/paper2_voxel_topology_clogging/latex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

## Main Release

Recommended citation release:

- Release name: `CES-submission-v1.0`
- Tag: `v1.0.0-ces-submission`

## Citation

If you use this repository, cite the associated manuscript and this repository release. A `CITATION.cff` file is included for GitHub citation metadata.

## Scope Boundary

This repository is intended for manuscript review, reuse of processed source data and reproduction of plotted diagnostics. It is not a complete raw DEM archive and should not be interpreted as a validated hydraulic clogging predictor.
