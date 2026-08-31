# Paper 3 minimal code and processed data

This directory contains the smallest checked subset needed to reproduce the
principal numerical summaries retained for Paper 3:

- the completed 12-case, \(2\times2\times3\) post-equilibrated transport matrix;
- pooled and leave-one-release-out fractional first-passage comparisons;
- pairwise and leave-one-release-out mobile--immobile model comparisons;
- four-cell multiscale CTRW summaries;
- particle-ID-paired initial-velocity and gravity-control comparisons; and
- four completed 20 s Xie et al. retention cases at
  \(d_f/d_p=0.10,0.15,0.20,0.25\); and
- processed release-zone and interior-window pore-resolved carrier-flow
  comparisons plus a fine-particle occupied-position sensitivity diagnostic;
  and
- twelve compact source-data tables and an R script that reproduce all five
  main-paper figures without requiring the raw CFD--DEM cases.

The package contains processed CSV/JSON tables and the code that recomputes
their main internal consistency checks. It is deliberately not a complete
CFD--DEM solver archive.

## Run

Python 3.10 or newer is recommended.

```bash
python -m pip install -r requirements.txt
python code/verify_release.py
```

To reproduce the five main figures with R 4.2 or newer, install `ggplot2`,
`patchwork`, `dplyr`, `tidyr`, `readr`, `scales`, `svglite`, and `ragg`, then
write the outputs to a directory outside this minimal package:

```bash
Rscript code/plotting/reproduce_main_figures.R ../paper3_reproduced_figures
```

The script writes SVG, PDF, 600-dpi TIFF, and PNG variants. None of these
generated image files is included in the repository release.

The last command checks all SHA256 values, the 12-case design, the four
first-passage cells and 12 held-out folds, 24 ordered mobile--immobile pairs
and 12 leave-one-out predictions, 12 CTRW cases, 2,400 particle-paired
mechanism rows, the three-point carrier-flow grid sequence, filtered
resolved--unresolved velocity comparisons, 1,079 valid occupied-position
samples, and all four Xie cases. It also rebuilds the Xie comparison in a
temporary directory and checks:

- 20 s end time for every case;
- 4,104 fine particles per case and exact retained/outlet balance;
- the 19--20 s and 18--20 s late-time windows;
- four calculated retention fractions
  `0.035575, 0.360624, 0.953704, 1.000000`;
- RMSE `0.137333`, MAE `0.082098`, Pearson correlation `0.957843`; and
- monotonic increase with size ratio.

For the model-applicability package, the same command independently recomputes
the filtered velocity relative-L2 differences from the released bin tables and
the fixed-coefficient force ratios from the released occupied-position rows.
The latter is a sensitivity diagnostic: it is not a corrected drag law or a
resolved fine-particle surface-force validation.

## Directory layout

- `code/`: analysis/check scripts plus one package-wide runner.
- `data/main_transport/`: release-level and paired summaries for 12 cases.
- `data/first_passage/`: pooled and held-out first-passage summaries.
- `data/mobile_immobile/`: pairwise and leave-one-out prediction tables.
- `data/ctrw/`: release and four-cell multiscale CTRW summaries.
- `data/mechanism/`: particle-paired mechanism differences and intervals.
- `data/model_applicability/`: processed grid, filtered carrier-field and
  occupied-position diagnostics used to define the interpretation limits of
  the unresolved CFD--DEM calculation.
- `data/figure_source/`: compact source tables consumed by the R figure script.
- `data/xie/`: digitized reference values and compact per-particle/per-time
  results for four 20 s cases.
- `code/plotting/`: self-contained R figure-reproduction code.
- `SHA256SUMS`: hashes of every file in this directory except itself.

## Intentionally excluded

No manuscript source or PDF, cover letter, figure/image, OpenFOAM processor
directory, LIGGGHTS dump/restart, full log, remote submission/monitoring script,
or raw CFD--DEM time directory is included.

The repository release containing this Paper 3 directory is archived at
<https://doi.org/10.5281/zenodo.21597645>. A later GitHub commit may contain
additional checked Paper 3 files; the DOI continues to identify the immutable
archived release stated on its landing page.

The released CSV/JSON files are sufficient for the package checks and paper
figures. Re-running the raw OpenFOAM-field extraction additionally requires
PyVista and the full OpenFOAM cases, which are intentionally not included in
this lightweight public package.

## Literature comparison

The Xie reference values were digitized from Fig. 21 of:

Xie et al., *Chemical Engineering Science* 231 (2021) 116261,
<https://doi.org/10.1016/j.ces.2020.116261>.
