#!/usr/bin/env python3
"""Compare pore-resolved flow with the production unresolved CFD field.

The resolved field is volume-averaged over bins matching the production
22 x 6 x 5 CFD mesh.  Streamwise bin edges are configurable so that an
interior resolved window can be compared only over complete production CFD
cells, excluding the artificial resolved-domain inlet and outlet regions.  The
script is intended to run on the workstation, where PyVista can read OpenFOAM
cases directly.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path

import numpy as np
import pyvista as pv


DEFAULT_RESOLVED_X_EDGES = np.array([0.0, 0.0025, 0.0050, 0.0075, 0.0100])
Y_EDGES = np.linspace(0.0, 0.015, 7)
Z_EDGES = np.linspace(0.0, 0.013, 6)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_internal(case: Path, time_value: float, arrays: tuple[str, ...]):
    marker = case / "case.foam"
    marker.touch(exist_ok=True)
    reader = pv.OpenFOAMReader(str(marker))
    reader.set_active_time_value(time_value)
    reader.disable_all_cell_arrays()
    for name in arrays:
        reader.enable_cell_array(name)
    mesh = reader.read()["internalMesh"]
    missing = sorted(set(arrays) - set(mesh.cell_data.keys()))
    if missing:
        raise RuntimeError(f"missing arrays in {case}: {missing}")
    return mesh


def parse_edges(text: str) -> np.ndarray:
    edges = np.asarray([float(value) for value in text.split(",")], dtype=float)
    if len(edges) < 3 or np.any(np.diff(edges) <= 0):
        raise argparse.ArgumentTypeError(
            "x edges must contain at least three strictly increasing values"
        )
    return edges


def bin_indices(
    points: np.ndarray, x_edges: np.ndarray, grid_shape: tuple[int, int, int]
):
    ix = np.searchsorted(x_edges, points[:, 0], side="right") - 1
    iy = np.searchsorted(Y_EDGES, points[:, 1], side="right") - 1
    iz = np.searchsorted(Z_EDGES, points[:, 2], side="right") - 1
    valid = (
        (ix >= 0)
        & (ix < grid_shape[0])
        & (iy >= 0)
        & (iy < grid_shape[1])
        & (iz >= 0)
        & (iz < grid_shape[2])
    )
    flat = np.ravel_multi_index((ix[valid], iy[valid], iz[valid]), grid_shape)
    return valid, flat


def weighted_bins(
    flat: np.ndarray, values: np.ndarray, weights: np.ndarray, nbin: int
):
    denom = np.bincount(flat, weights=weights, minlength=nbin)
    if values.ndim == 1:
        numer = np.bincount(flat, weights=weights * values, minlength=nbin)
        return np.divide(numer, denom, out=np.full(nbin, np.nan), where=denom > 0)
    out = np.empty((nbin, values.shape[1]))
    for j in range(values.shape[1]):
        numer = np.bincount(flat, weights=weights * values[:, j], minlength=nbin)
        out[:, j] = np.divide(
            numer, denom, out=np.full(nbin, np.nan), where=denom > 0
        )
    return out


def metrics(candidate: np.ndarray, reference: np.ndarray):
    mask = np.isfinite(candidate) & np.isfinite(reference)
    a = candidate[mask]
    b = reference[mask]
    diff = a - b
    corr = float(np.corrcoef(a, b)[0, 1]) if len(a) > 1 and np.std(a) > 0 and np.std(b) > 0 else None
    denom = float(np.linalg.norm(b))
    return {
        "n": int(len(a)),
        "bias": float(np.mean(diff)),
        "mae": float(np.mean(np.abs(diff))),
        "rmse": float(np.sqrt(np.mean(diff**2))),
        "relative_l2": float(np.linalg.norm(diff) / denom) if denom > 0 else None,
        "pearson_r": corr,
    }


def weighted_quantile(values: np.ndarray, weights: np.ndarray, probabilities):
    order = np.argsort(values)
    v = np.asarray(values)[order]
    w = np.asarray(weights)[order]
    cumulative = np.cumsum(w) - 0.5 * w
    cumulative /= np.sum(w)
    return np.interp(np.asarray(probabilities), cumulative, v)


def speed_distribution(velocity: np.ndarray, weights: np.ndarray, superficial_u: float):
    speed = np.linalg.norm(velocity, axis=1)
    probabilities = np.array([0.10, 0.50, 0.90, 0.95, 0.99])
    quantiles = weighted_quantile(speed, weights, probabilities)
    ux_quantiles = weighted_quantile(velocity[:, 0], weights, probabilities)
    total = float(np.sum(weights))
    return {
        "speed_quantiles_m_per_s": {
            f"p{int(100 * q):02d}": float(value)
            for q, value in zip(probabilities, quantiles)
        },
        "ux_quantiles_m_per_s": {
            f"p{int(100 * q):02d}": float(value)
            for q, value in zip(probabilities, ux_quantiles)
        },
        "volume_fraction_speed_below_0p1_Us": float(
            np.sum(weights[speed < 0.1 * superficial_u]) / total
        ),
        "volume_fraction_speed_below_0p5_Us": float(
            np.sum(weights[speed < 0.5 * superficial_u]) / total
        ),
        "volume_fraction_speed_above_2_Us": float(
            np.sum(weights[speed > 2.0 * superficial_u]) / total
        ),
        "volume_fraction_speed_above_5_Us": float(
            np.sum(weights[speed > 5.0 * superficial_u]) / total
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resolved-case", type=Path, required=True)
    parser.add_argument("--resolved-time", type=float, required=True)
    parser.add_argument("--unresolved-case", type=Path, required=True)
    parser.add_argument("--unresolved-time", type=float, default=0.299)
    parser.add_argument(
        "--resolved-x-edges",
        type=parse_edges,
        default=DEFAULT_RESOLVED_X_EDGES,
        help="comma-separated x-bin edges in the local resolved coordinates",
    )
    parser.add_argument(
        "--unresolved-x-edges",
        type=parse_edges,
        default=None,
        help=(
            "comma-separated matching x-bin edges in the production unresolved "
            "coordinates; defaults to --resolved-x-edges"
        ),
    )
    parser.add_argument("--cells-per-dp", type=int, choices=(10, 15, 20), required=True)
    parser.add_argument(
        "--nominal-window-porosity",
        type=float,
        default=None,
        help="independent sphere--box volume result for x=0--10 mm",
    )
    parser.add_argument("--superficial-velocity", type=float, default=0.1)
    parser.add_argument("--fluid-density", type=float, default=0.164)
    parser.add_argument("--dynamic-viscosity", type=float, default=1.96e-5)
    parser.add_argument("--pebble-diameter", type=float, default=0.001)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    resolved_x_edges = np.asarray(args.resolved_x_edges, dtype=float)
    unresolved_x_edges = (
        resolved_x_edges
        if args.unresolved_x_edges is None
        else np.asarray(args.unresolved_x_edges, dtype=float)
    )
    if len(resolved_x_edges) != len(unresolved_x_edges):
        parser.error("resolved and unresolved x-edge lists must have equal length")
    if not np.allclose(np.diff(resolved_x_edges), np.diff(unresolved_x_edges)):
        parser.error("resolved and unresolved x-bin widths must match")
    grid_shape = (
        len(resolved_x_edges) - 1,
        len(Y_EDGES) - 1,
        len(Z_EDGES) - 1,
    )
    nbin = int(np.prod(grid_shape))

    resolved = read_internal(args.resolved_case, args.resolved_time, ("U", "p"))
    unresolved = read_internal(
        args.unresolved_case, args.unresolved_time, ("U", "p", "voidfraction")
    )

    rcentres = resolved.cell_centers().points
    rvalid, rflat = bin_indices(rcentres, resolved_x_edges, grid_shape)
    rvolumes_all = resolved.compute_cell_sizes(
        length=False, area=False, volume=True
    ).cell_data["Volume"]
    rvolumes = np.asarray(rvolumes_all)[rvalid]
    ru = np.asarray(resolved.cell_data["U"])[rvalid]
    rp = np.asarray(resolved.cell_data["p"])[rvalid]

    bin_volume = np.empty(nbin)
    for ix in range(grid_shape[0]):
        for iy in range(grid_shape[1]):
            for iz in range(grid_shape[2]):
                flat = np.ravel_multi_index((ix, iy, iz), grid_shape)
                bin_volume[flat] = (
                    (resolved_x_edges[ix + 1] - resolved_x_edges[ix])
                    * (Y_EDGES[iy + 1] - Y_EDGES[iy])
                    * (Z_EDGES[iz + 1] - Z_EDGES[iz])
                )

    fluid_volume = np.bincount(rflat, weights=rvolumes, minlength=len(bin_volume))
    resolved_epsilon = fluid_volume / bin_volume
    resolved_u = weighted_bins(rflat, ru, rvolumes, nbin)
    resolved_p = weighted_bins(rflat, rp, rvolumes, nbin)
    resolved_umag = weighted_bins(
        rflat, np.linalg.norm(ru, axis=1), rvolumes, nbin
    )
    resolved_u2 = weighted_bins(rflat, ru[:, 0] ** 2, rvolumes, nbin)
    resolved_ux_std = np.sqrt(np.maximum(0.0, resolved_u2 - resolved_u[:, 0] ** 2))

    ucentres = unresolved.cell_centers().points
    uvalid, uflat = bin_indices(ucentres, unresolved_x_edges, grid_shape)
    if len(np.unique(uflat)) != nbin:
        raise RuntimeError("unresolved bins are not one-to-one with the selected grid")
    order = np.argsort(uflat)
    unresolved_u = np.asarray(unresolved.cell_data["U"])[uvalid][order]
    unresolved_p = np.asarray(unresolved.cell_data["p"])[uvalid][order]
    unresolved_epsilon = np.asarray(unresolved.cell_data["voidfraction"])[uvalid][order]

    resolved_qx = resolved_epsilon * resolved_u[:, 0]
    unresolved_qx = unresolved_epsilon * unresolved_u[:, 0]

    rows = []
    for flat in range(len(bin_volume)):
        ix, iy, iz = np.unravel_index(flat, grid_shape)
        rows.append(
            {
                "ix": ix,
                "iy": iy,
                "iz": iz,
                "resolved_x_center_m": 0.5
                * (resolved_x_edges[ix] + resolved_x_edges[ix + 1]),
                "unresolved_x_center_m": 0.5
                * (unresolved_x_edges[ix] + unresolved_x_edges[ix + 1]),
                "y_center_m": 0.5 * (Y_EDGES[iy] + Y_EDGES[iy + 1]),
                "z_center_m": 0.5 * (Z_EDGES[iz] + Z_EDGES[iz + 1]),
                "resolved_fluid_volume_m3": fluid_volume[flat],
                "resolved_epsilon": resolved_epsilon[flat],
                "unresolved_epsilon_raw": unresolved_epsilon[flat],
                "unresolved_epsilon_drag_used": max(0.4, unresolved_epsilon[flat]),
                "resolved_ux_m_per_s": resolved_u[flat, 0],
                "resolved_uy_m_per_s": resolved_u[flat, 1],
                "resolved_uz_m_per_s": resolved_u[flat, 2],
                "resolved_mean_umag_m_per_s": resolved_umag[flat],
                "resolved_ux_std_within_bin_m_per_s": resolved_ux_std[flat],
                "unresolved_ux_m_per_s": unresolved_u[flat, 0],
                "unresolved_uy_m_per_s": unresolved_u[flat, 1],
                "unresolved_uz_m_per_s": unresolved_u[flat, 2],
                "resolved_qx_m_per_s": resolved_qx[flat],
                "unresolved_qx_m_per_s": unresolved_qx[flat],
                "resolved_p_m2_per_s2": resolved_p[flat],
                "unresolved_p_m2_per_s2": unresolved_p[flat],
            }
        )

    # Cross-sectional, fluid-volume-weighted pressure profiles and slopes.
    resolved_xcentres = 0.5 * (resolved_x_edges[:-1] + resolved_x_edges[1:])
    unresolved_xcentres = 0.5 * (unresolved_x_edges[:-1] + unresolved_x_edges[1:])
    p_res_x = np.empty(grid_shape[0])
    p_unres_x = np.empty(grid_shape[0])
    for ix in range(grid_shape[0]):
        mask = np.array([row["ix"] == ix for row in rows])
        p_res_x[ix] = np.average(resolved_p[mask], weights=fluid_volume[mask])
        p_unres_x[ix] = np.average(
            unresolved_p[mask], weights=unresolved_epsilon[mask] * bin_volume[mask]
        )
    slope_res, intercept_res = np.polyfit(resolved_xcentres, p_res_x, 1)
    slope_unres, intercept_unres = np.polyfit(unresolved_xcentres, p_unres_x, 1)

    result = {
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "resolved_case": str(args.resolved_case.resolve()),
        "resolved_time": args.resolved_time,
        "resolved_cells_per_dp": args.cells_per_dp,
        "resolved_internal_cells_total": int(resolved.n_cells),
        "resolved_cells_in_comparison_window": int(np.count_nonzero(rvalid)),
        "unresolved_case": str(args.unresolved_case.resolve()),
        "unresolved_time": args.unresolved_time,
        "comparison_window_m": {
            "resolved_x": [
                float(resolved_x_edges[0]),
                float(resolved_x_edges[-1]),
            ],
            "unresolved_x": [
                float(unresolved_x_edges[0]),
                float(unresolved_x_edges[-1]),
            ],
            "y": [0.0, 0.015],
            "z": [0.0, 0.013],
        },
        "coarse_bin_shape": grid_shape,
        "coarse_bins": nbin,
        "resolved_window_porosity": float(np.sum(fluid_volume) / np.sum(bin_volume)),
        "unresolved_window_mean_raw_voidfraction": float(np.mean(unresolved_epsilon)),
        "unresolved_fraction_below_drag_cutoff_0p4": float(np.mean(unresolved_epsilon < 0.4)),
        "void_space_speed_distribution": speed_distribution(
            ru, rvolumes, args.superficial_velocity
        ),
        "unresolved_cell_speed_distribution": speed_distribution(
            unresolved_u, unresolved_epsilon * bin_volume, args.superficial_velocity
        ),
        "metrics_resolved_minus_unresolved": {
            "raw_voidfraction": metrics(resolved_epsilon, unresolved_epsilon),
            "fluid_phase_ux_m_per_s": metrics(resolved_u[:, 0], unresolved_u[:, 0]),
            "superficial_qx_m_per_s": metrics(resolved_qx, unresolved_qx),
        },
        "cross_sectional_pressure": {
            "resolved_x_centres_m": resolved_xcentres.tolist(),
            "unresolved_x_centres_m": unresolved_xcentres.tolist(),
            "resolved_mean_p_m2_per_s2": p_res_x.tolist(),
            "unresolved_mean_p_m2_per_s2": p_unres_x.tolist(),
            "resolved_dpdx_m_per_s2_per_m": float(slope_res),
            "unresolved_dpdx_m_per_s2_per_m": float(slope_unres),
            "resolved_intercept_m2_per_s2": float(intercept_res),
            "unresolved_intercept_m2_per_s2": float(intercept_unres),
            "absolute_gradient_ratio_resolved_over_unresolved": float(abs(slope_res / slope_unres)),
        },
    }
    if args.nominal_window_porosity is not None:
        result["nominal_window_porosity_from_sphere_box_integration"] = (
            args.nominal_window_porosity
        )
        result["resolved_window_porosity_error"] = (
            result["resolved_window_porosity"] - args.nominal_window_porosity
        )
        result["unresolved_window_porosity_error"] = (
            result["unresolved_window_mean_raw_voidfraction"]
            - args.nominal_window_porosity
        )
        epsilon = args.nominal_window_porosity
        ergun_dynamic = (
            150.0
            * args.dynamic_viscosity
            * (1.0 - epsilon) ** 2
            / (epsilon**3 * args.pebble_diameter**2)
            * args.superficial_velocity
            + 1.75
            * args.fluid_density
            * (1.0 - epsilon)
            / (epsilon**3 * args.pebble_diameter)
            * args.superficial_velocity**2
        )
        ergun_kinematic = ergun_dynamic / args.fluid_density
        result["ergun_reference"] = {
            "porosity": epsilon,
            "superficial_velocity_m_per_s": args.superficial_velocity,
            "dynamic_pressure_gradient_Pa_per_m": ergun_dynamic,
            "kinematic_pressure_gradient_m_per_s2_per_m": ergun_kinematic,
            "resolved_to_ergun_gradient_ratio": float(abs(slope_res) / ergun_kinematic),
            "unresolved_to_ergun_gradient_ratio": float(abs(slope_unres) / ergun_kinematic),
        }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / f"carrier_field_bins_c{args.cells_per_dp}.csv"
    json_path = args.output_dir / f"carrier_field_comparison_c{args.cells_per_dp}.json"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result["output_sha256"] = {csv_path.name: sha256(csv_path)}
    json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
