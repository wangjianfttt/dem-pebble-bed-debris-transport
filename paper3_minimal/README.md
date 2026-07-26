# Paper 3 minimal code and processed data

This directory contains the smallest checked subset needed to reproduce the
principal numerical summaries retained for Paper 3:

- the completed 12-case, \(2\times2\times3\) post-equilibrated transport matrix;
- pooled and leave-one-release-out fractional first-passage comparisons;
- pairwise and leave-one-release-out mobile--immobile model comparisons;
- four-cell multiscale CTRW summaries;
- particle-ID-paired initial-velocity and gravity-control comparisons; and
- four completed 20 s Xie et al. retention cases at
  \(d_f/d_p=0.10,0.15,0.20,0.25\).

The package contains processed CSV/JSON tables and the code that recomputes
their main internal consistency checks. It is deliberately not a complete
CFD--DEM solver archive.

## Run

Python 3.10 or newer is recommended.

```bash
python -m pip install -r requirements.txt
python code/verify_release.py
```

The last command checks all SHA256 values, the 12-case design, the four
first-passage cells and 12 held-out folds, 24 ordered mobile--immobile pairs
and 12 leave-one-out predictions, 12 CTRW cases, 2,400 particle-paired
mechanism rows, and all four Xie cases. It also rebuilds the Xie comparison in
a temporary directory and checks:

- 20 s end time for every case;
- 4,104 fine particles per case and exact retained/outlet balance;
- the 19--20 s and 18--20 s late-time windows;
- four calculated retention fractions
  `0.035575, 0.360624, 0.953704, 1.000000`;
- RMSE `0.137333`, MAE `0.082098`, Pearson correlation `0.957843`; and
- monotonic increase with size ratio.

## Directory layout

- `code/`: five original analysis/check scripts plus one package-wide runner.
- `data/main_transport/`: release-level and paired summaries for 12 cases.
- `data/first_passage/`: pooled and held-out first-passage summaries.
- `data/mobile_immobile/`: pairwise and leave-one-out prediction tables.
- `data/ctrw/`: release and four-cell multiscale CTRW summaries.
- `data/mechanism/`: particle-paired mechanism differences and intervals.
- `data/xie/`: digitized reference values and compact per-particle/per-time
  results for four 20 s cases.
- `SHA256SUMS`: hashes of every file in this directory except itself.

## Intentionally excluded

No manuscript source or PDF, cover letter, figure/image, OpenFOAM processor
directory, LIGGGHTS dump/restart, full log, remote submission/monitoring script,
or raw CFD--DEM time directory is included.

The existing repository DOI `10.5281/zenodo.20699272` belongs to Paper 2 and
does not identify this Paper 3 directory.

## Literature comparison

The Xie reference values were digitized from Fig. 21 of:

Xie et al., *Chemical Engineering Science* 231 (2021) 116261,
<https://doi.org/10.1016/j.ces.2020.116261>.
