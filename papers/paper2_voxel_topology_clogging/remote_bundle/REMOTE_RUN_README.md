# Paper 2 Localized-Release Remote Run Instructions

This bundle is for the remaining localized-release production jobs:

- `906_upstream_source_continue_1M_to_4M`
- `908_high_inventory_dt5e9_to_10ms`

The completed `907_downstream_source_dt5e9_to_10ms` job is skipped by the generated runner unless explicitly requested.

## On The Ubuntu Workstation

Unpack the bundle at a work directory:

```bash
tar -xzf paper2_localized_release_remote_*.tar.gz
cd paper2_localized_release_remote_*
```

Run the remaining production jobs:

```bash
NP=16 \
LIGGGHTS_BIN=/home/wangjian/LIGGGHTS-INL-inl/src/lmp_mpi_ubuntu-22.04 \
bash papers/paper2_voxel_topology_clogging/scripts/run_remaining_localized_production.sh
```

If only one job should be run:

```bash
ONLY=908_high_inventory_dt5e9_to_10ms \
NP=16 \
LIGGGHTS_BIN=/home/wangjian/LIGGGHTS-INL-inl/src/lmp_mpi_ubuntu-22.04 \
bash papers/paper2_voxel_topology_clogging/scripts/run_explicit_localized_production_queue.sh

bash papers/paper2_voxel_topology_clogging/scripts/collect_localized_remote_results.sh
```

## Return Files

After completion, the return archive is written under:

```text
papers/paper2_voxel_topology_clogging/remote_results/
```

Copy back both files:

```text
paper2_localized_release_results_*.tar.gz
paper2_localized_release_results_*.tar.gz.sha256
```

## Back On The Local Project

Import and refresh the local analysis:

```bash
python3 papers/paper2_voxel_topology_clogging/scripts/import_localized_remote_results.py \
  papers/paper2_voxel_topology_clogging/remote_results/paper2_localized_release_results_*.tar.gz
```

For a no-copy inspection first:

```bash
python3 papers/paper2_voxel_topology_clogging/scripts/import_localized_remote_results.py \
  papers/paper2_voxel_topology_clogging/remote_results/paper2_localized_release_results_*.tar.gz \
  --dry-run
```

## Evidence Boundary

Only jobs that reach their configured target physical time can support
source-position or source-inventory claims. Partial runs remain supporting or
diagnostic evidence only.
