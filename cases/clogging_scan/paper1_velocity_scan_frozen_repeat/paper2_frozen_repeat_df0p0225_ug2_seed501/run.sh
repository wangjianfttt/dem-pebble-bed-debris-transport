#!/usr/bin/env bash
set -euo pipefail

KNOWN_BIN="/Users/wangjian-macbook13/Library/CloudStorage/SynologyDrive-mac/颗粒破碎研究claude/LIGGGHTS-INL-inl/src/lmp_mpi_no_vtk"
if command -v liggghts-iNL >/dev/null 2>&1; then
  DEFAULT_BIN="liggghts-iNL"
elif command -v liggghts-inl >/dev/null 2>&1; then
  DEFAULT_BIN="liggghts-inl"
elif command -v liggghts >/dev/null 2>&1; then
  DEFAULT_BIN="liggghts"
elif [[ -x "$KNOWN_BIN" ]]; then
  DEFAULT_BIN="$KNOWN_BIN"
else
  DEFAULT_BIN="liggghts-iNL"
fi

LIGGGHTS_BIN="${LIGGGHTS_BIN:-$DEFAULT_BIN}"
LIGGGHTS_MPI_NP="${LIGGGHTS_MPI_NP:-1}"

if [[ "$LIGGGHTS_MPI_NP" -gt 1 ]]; then
  exec mpirun -np "$LIGGGHTS_MPI_NP" "$LIGGGHTS_BIN" -in in.debris_injection
fi

exec "$LIGGGHTS_BIN" -in in.debris_injection
