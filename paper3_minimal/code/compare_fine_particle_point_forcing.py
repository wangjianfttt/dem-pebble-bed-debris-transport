#!/usr/bin/env python3
"""Diagnose carrier-field effects at occupied fine-particle positions.

This is deliberately not a resolved fine-particle drag validation.  It samples
the pore-resolved and production unresolved carrier velocities at positions
recorded by the formal CFD--DEM run.  The logged Koch--Hill force coefficient
is then held fixed while only the slip velocity is replaced.  The resulting
force change isolates sensitivity to carrier-field resolution without
pretending that the fine-particle surface traction has been resolved.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import glob
import hashlib
import json
from pathlib import Path

import numpy as np
import pyvista as pv


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_internal(case: Path, time_value: float):
    marker = case / "case.foam"
    marker.touch(exist_ok=True)
    reader = pv.OpenFOAMReader(str(marker))
    reader.set_active_time_value(time_value)
    reader.disable_all_cell_arrays()
    reader.enable_cell_array("U")
    mesh = reader.read()["internalMesh"]
    if "U" not in mesh.cell_data:
        raise RuntimeError(f"missing U in {case} at {time_value}")
    return mesh


def parse_probe_files(probe_dir: Path, x_min: float, x_max: float):
    rows = []
    for name in sorted(glob.glob(str(probe_dir / "KochHillDrag.logDat.*"))):
        processor = int(Path(name).suffix[1:])
        with open(name, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                if not line or line[0] in "#\n":
                    continue
                fields = line.replace("||", " ").split()
                if len(fields) != 16:
                    raise RuntimeError(
                        f"unexpected KochHill probe row with {len(fields)} fields: {line[:160]}"
                    )
                values = [float(value) for value in fields]
                position = np.asarray(values[13:16])
                if not (x_min <= position[0] <= x_max):
                    continue
                rows.append(
                    {
                        # CFDEM particleProbe writes the zero-based internal
                        # index, whereas the DEM dump uses one-based atom IDs.
                        "probe_index": int(values[0]),
                        "particle_id": int(values[0]) + 1,
                        "time_s": values[1],
                        "processor": processor,
                        "drag": np.asarray(values[2:5]),
                        "urel": np.asarray(values[5:8]),
                        "rep": values[8],
                        "beta": values[9],
                        "voidfraction_used": values[10],
                        "voidfraction_raw": values[11],
                        "voidfraction_clipped": bool(int(values[12])),
                        "position": position,
                    }
                )
    if not rows:
        raise RuntimeError("no probe rows in the requested axial window")
    return rows


def load_particle_contact(path: Path):
    result = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            pid = int(row["particle_id"])
            result[pid] = {
                "ever_contacted": row["ever_contacted"].strip().lower() == "true",
                "sampled_contact_fraction": float(row["sampled_contact_fraction"]),
                "early_sampled_contact_fraction": float(
                    row["early_sampled_contact_fraction"]
                ),
            }
    return result


def load_dem_velocities(
    rows,
    dump_dir: Path,
    base_timestep: int,
    dem_timestep_s: float,
):
    grouped = {}
    for row in rows:
        timestep = base_timestep + int(round(row["time_s"] / dem_timestep_s))
        row["dem_timestep"] = timestep
        grouped.setdefault(timestep, set()).add(row["particle_id"])

    velocity = {}
    position = {}
    for timestep, requested_ids in sorted(grouped.items()):
        path = dump_dir / f"debris{timestep}.liggghts_run"
        if not path.is_file():
            raise RuntimeError(f"missing DEM debris dump {path}")
        columns = None
        with path.open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                if line.startswith("ITEM: ATOMS "):
                    columns = line.split()[2:]
                    index = {name: i for i, name in enumerate(columns)}
                    required = {"id", "x", "y", "z", "vx", "vy", "vz"}
                    if not required.issubset(index):
                        raise RuntimeError(f"missing dump columns in {path}: {required - set(index)}")
                    continue
                if columns is None or line.startswith("ITEM:"):
                    continue
                fields = line.split()
                if len(fields) != len(columns):
                    continue
                particle_id = int(fields[index["id"]])
                if particle_id not in requested_ids:
                    continue
                key = (timestep, particle_id)
                position[key] = np.asarray(
                    [fields[index[axis]] for axis in ("x", "y", "z")], dtype=float
                )
                velocity[key] = np.asarray(
                    [fields[index[axis]] for axis in ("vx", "vy", "vz")], dtype=float
                )

    missing = [
        (row["dem_timestep"], row["particle_id"])
        for row in rows
        if (row["dem_timestep"], row["particle_id"]) not in velocity
    ]
    if missing:
        raise RuntimeError(f"missing {len(missing)} selected particle velocities")
    maximum_position_error = max(
        float(
            np.linalg.norm(
                row["position"]
                - position[(row["dem_timestep"], row["particle_id"])]
            )
        )
        for row in rows
    )
    for row in rows:
        row["particle_u"] = velocity[(row["dem_timestep"], row["particle_id"])]
    return maximum_position_error


def select_rows(rows, samples_per_particle_stratum: int):
    speeds = np.asarray([np.linalg.norm(row["urel"]) for row in rows])
    q1, q2 = np.quantile(speeds, [1.0 / 3.0, 2.0 / 3.0])
    for row, speed in zip(rows, speeds):
        row["unresolved_slip_speed_m_per_s"] = float(speed)
        row["slip_speed_stratum"] = "low" if speed <= q1 else "mid" if speed <= q2 else "high"

    groups = {}
    for row in rows:
        key = (
            row["particle_id"],
            row["voidfraction_clipped"],
            row["slip_speed_stratum"],
        )
        groups.setdefault(key, []).append(row)

    selected = []
    for key in sorted(groups):
        group = sorted(groups[key], key=lambda item: item["time_s"])
        count = min(samples_per_particle_stratum, len(group))
        indices = np.unique(np.linspace(0, len(group) - 1, count).round().astype(int))
        selected.extend(group[index] for index in indices)
    return selected, {"lower_tercile": float(q1), "upper_tercile": float(q2)}


def sample_velocity(mesh, points: np.ndarray):
    sampled = pv.PolyData(points).sample(mesh, pass_cell_data=True)
    valid = np.asarray(sampled.point_data["vtkValidPointMask"], dtype=bool)
    velocity = np.asarray(sampled.point_data["U"], dtype=float)
    return velocity, valid


def vector_metrics(candidate: np.ndarray, reference: np.ndarray):
    delta = candidate - reference
    reference_norm = np.linalg.norm(reference, axis=1)
    candidate_norm = np.linalg.norm(candidate, axis=1)
    valid_direction = (reference_norm > 0) & (candidate_norm > 0)
    cosine = np.full(len(reference), np.nan)
    cosine[valid_direction] = np.sum(
        candidate[valid_direction] * reference[valid_direction], axis=1
    ) / (candidate_norm[valid_direction] * reference_norm[valid_direction])
    ratio = np.divide(
        candidate_norm,
        reference_norm,
        out=np.full(len(reference), np.nan),
        where=reference_norm > 0,
    )
    return {
        "n": int(len(reference)),
        "relative_l2": float(np.linalg.norm(delta) / np.linalg.norm(reference)),
        "magnitude_ratio_p10_p50_p90": [
            float(value) for value in np.nanquantile(ratio, [0.1, 0.5, 0.9])
        ],
        "direction_cosine_p10_p50_p90": [
            float(value) for value in np.nanquantile(cosine, [0.1, 0.5, 0.9])
        ],
        "opposite_direction_fraction": float(np.nanmean(cosine < 0)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resolved-case", type=Path, required=True)
    parser.add_argument("--resolved-time", type=float, required=True)
    parser.add_argument("--unresolved-case", type=Path, required=True)
    parser.add_argument("--unresolved-time", type=float, default=0.0)
    parser.add_argument("--probe-dir", type=Path, required=True)
    parser.add_argument("--debris-dump-dir", type=Path, required=True)
    parser.add_argument("--contact-particle-csv", type=Path, required=True)
    parser.add_argument("--base-timestep", type=int, default=125000000)
    parser.add_argument("--dem-timestep-s", type=float, default=2.0e-9)
    parser.add_argument("--x-min", type=float, default=0.0)
    parser.add_argument("--x-max", type=float, default=0.010)
    parser.add_argument("--samples-per-particle-stratum", type=int, default=3)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    raw_rows = parse_probe_files(args.probe_dir, args.x_min, args.x_max)
    rows, terciles = select_rows(raw_rows, args.samples_per_particle_stratum)
    contact = load_particle_contact(args.contact_particle_csv)
    maximum_probe_dump_position_error = load_dem_velocities(
        rows, args.debris_dump_dir, args.base_timestep, args.dem_timestep_s
    )
    points = np.asarray([row["position"] for row in rows])

    resolved = read_internal(args.resolved_case, args.resolved_time)
    unresolved = read_internal(args.unresolved_case, args.unresolved_time)
    resolved_u, resolved_valid = sample_velocity(resolved, points)
    unresolved_u, unresolved_valid = sample_velocity(unresolved, points)
    valid = resolved_valid & unresolved_valid
    if np.count_nonzero(valid) < 0.7 * len(rows):
        raise RuntimeError(
            f"only {np.count_nonzero(valid)}/{len(rows)} samples were valid in both fields"
        )

    validity_diagnostic = {
        "selected_rows": int(len(rows)),
        "valid_in_both_fields": int(np.count_nonzero(valid)),
        "invalid_in_either_field": int(np.count_nonzero(~valid)),
        "valid_fraction": float(np.mean(valid)),
        "invalid_voidfraction_clipped_fraction": float(
            np.mean([row["voidfraction_clipped"] for row, keep in zip(rows, valid) if not keep])
        )
        if np.any(~valid)
        else None,
        "valid_voidfraction_clipped_fraction": float(
            np.mean([row["voidfraction_clipped"] for row, keep in zip(rows, valid) if keep])
        ),
        "invalid_particle_contact_fraction_median": float(
            np.nanmedian(
                [
                    contact.get(row["particle_id"], {}).get(
                        "sampled_contact_fraction", np.nan
                    )
                    for row, keep in zip(rows, valid)
                    if not keep
                ]
            )
        )
        if np.any(~valid)
        else None,
        "valid_particle_contact_fraction_median": float(
            np.nanmedian(
                [
                    contact.get(row["particle_id"], {}).get(
                        "sampled_contact_fraction", np.nan
                    )
                    for row, keep in zip(rows, valid)
                    if keep
                ]
            )
        ),
    }

    rows = [row for row, keep in zip(rows, valid) if keep]
    resolved_u = resolved_u[valid]
    unresolved_u = unresolved_u[valid]
    logged_urel = np.asarray([row["urel"] for row in rows])
    logged_drag = np.asarray([row["drag"] for row in rows])

    particle_u = np.asarray([row["particle_u"] for row in rows])
    logged_carrier_u = particle_u + logged_urel
    resolved_slip = resolved_u - particle_u
    logged_slip_norm = np.linalg.norm(logged_urel, axis=1)
    logged_drag_norm = np.linalg.norm(logged_drag, axis=1)
    force_per_slip = np.divide(
        logged_drag_norm,
        logged_slip_norm,
        out=np.zeros(len(rows)),
        where=logged_slip_norm > 0,
    )
    replacement_drag = resolved_slip * force_per_slip[:, None]

    output_rows = []
    for i, row in enumerate(rows):
        meta = contact.get(row["particle_id"], {})
        item = {
            "particle_id": row["particle_id"],
            "probe_index": row["probe_index"],
            "dem_timestep": row["dem_timestep"],
            "time_s": row["time_s"],
            "processor": row["processor"],
            "x_m": row["position"][0],
            "y_m": row["position"][1],
            "z_m": row["position"][2],
            "voidfraction_raw": row["voidfraction_raw"],
            "voidfraction_used": row["voidfraction_used"],
            "voidfraction_clipped": row["voidfraction_clipped"],
            "slip_speed_stratum": row["slip_speed_stratum"],
            "ever_contacted": meta.get("ever_contacted"),
            "sampled_contact_fraction": meta.get("sampled_contact_fraction"),
            "early_sampled_contact_fraction": meta.get(
                "early_sampled_contact_fraction"
            ),
        }
        for label, vector in (
            ("unresolved_u", unresolved_u[i]),
            ("logged_carrier_u", logged_carrier_u[i]),
            ("resolved_u", resolved_u[i]),
            ("particle_u", particle_u[i]),
            ("logged_urel", logged_urel[i]),
            ("resolved_replacement_slip", resolved_slip[i]),
            ("logged_drag", logged_drag[i]),
            ("replacement_drag", replacement_drag[i]),
        ):
            for axis, value in zip("xyz", vector):
                item[f"{label}_{axis}"] = float(value)
        output_rows.append(item)

    groups = {"all": np.ones(len(rows), dtype=bool)}
    clipped = np.asarray([row["voidfraction_clipped"] for row in rows])
    groups["voidfraction_not_clipped"] = ~clipped
    groups["voidfraction_clipped"] = clipped
    for stratum in ("low", "mid", "high"):
        groups[f"slip_{stratum}"] = np.asarray(
            [row["slip_speed_stratum"] == stratum for row in rows]
        )
    contact_fraction = np.asarray(
        [contact.get(row["particle_id"], {}).get("sampled_contact_fraction", np.nan) for row in rows]
    )
    groups["particle_contact_fraction_below_median"] = contact_fraction <= np.nanmedian(
        contact_fraction
    )
    groups["particle_contact_fraction_above_median"] = contact_fraction > np.nanmedian(
        contact_fraction
    )

    grouped = {}
    for name, mask in groups.items():
        if np.count_nonzero(mask) < 3:
            continue
        grouped[name] = {
            "carrier_velocity": vector_metrics(
                resolved_u[mask], logged_carrier_u[mask]
            ),
            "production_field_sampling_consistency": vector_metrics(
                unresolved_u[mask], logged_carrier_u[mask]
            ),
            "fixed_coefficient_drag": vector_metrics(
                replacement_drag[mask], logged_drag[mask]
            ),
        }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / "fine_particle_point_forcing_samples.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)
    summary = {
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "resolved_case": str(args.resolved_case.resolve()),
        "resolved_time": args.resolved_time,
        "unresolved_case": str(args.unresolved_case.resolve()),
        "unresolved_time": args.unresolved_time,
        "probe_dir": str(args.probe_dir.resolve()),
        "debris_dump_dir": str(args.debris_dump_dir.resolve()),
        "maximum_probe_to_dem_dump_position_error_m": maximum_probe_dump_position_error,
        "comparison_window_x_m": [args.x_min, args.x_max],
        "raw_probe_rows_in_window": len(raw_rows),
        "selected_rows_before_field_validity": len(valid),
        "valid_selected_rows": len(rows),
        "field_sampling_validity": validity_diagnostic,
        "slip_speed_tercile_boundaries_m_per_s": terciles,
        "groups": grouped,
        "interpretation": (
            "Point-sampling diagnostic. The production particle velocity and "
            "logged Koch--Hill force-per-slip coefficient are retained while the "
            "sampled carrier velocity is replaced by the pore-resolved value. "
            "This isolates carrier-field sensitivity and is not a resolved "
            "fine-particle surface-traction validation."
        ),
        "sample_csv_sha256": sha256(csv_path),
    }
    json_path = args.output_dir / "fine_particle_point_forcing_summary.json"
    json_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
