#!/usr/bin/env python3
"""Compute nominal sphere-volume porosity in an axial bed window.

The formal Paper 3 pebbles lie within the complete y/z cross-section to
nanometre-level DEM tolerance.  Sphere volume is therefore integrated exactly
between the two axial clipping planes.  Elastic sphere overlaps are not
subtracted; the result is the nominal DEM sphere-volume porosity, matching the
definition used for the full bed and the unresolved volume mapping.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_parser(script: Path):
    spec = importlib.util.spec_from_file_location("pore_plan", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse_liggghts_atoms


def sphere_volume_in_x_slab(x_min: float, x_max: float, centre: float, radius: float):
    lo = max(x_min, centre - radius)
    hi = min(x_max, centre + radius)
    if hi <= lo:
        return 0.0

    def primitive(x: float):
        return math.pi * (radius * radius * x - (x - centre) ** 3 / 3.0)

    return primitive(hi) - primitive(lo)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bed-dump", type=Path, required=True)
    parser.add_argument("--x-min", type=float, required=True)
    parser.add_argument("--x-max", type=float, required=True)
    parser.add_argument("--y-min", type=float, default=0.0)
    parser.add_argument("--y-max", type=float, default=0.015)
    parser.add_argument("--z-min", type=float, default=0.0)
    parser.add_argument("--z-max", type=float, default=0.013)
    parser.add_argument("--wall-tolerance", type=float, default=2.0e-8)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.x_max <= args.x_min:
        raise ValueError("x-max must exceed x-min")

    helper = Path(__file__).with_name("plan_pore_resolved_rebuild.py")
    parse_atoms = load_parser(helper)
    _, atoms = parse_atoms(args.bed_dump)
    if not atoms:
        raise RuntimeError("empty bed")

    y_under = min(atom["y"] - atom["diameter"] / 2 - args.y_min for atom in atoms)
    y_over = max(atom["y"] + atom["diameter"] / 2 - args.y_max for atom in atoms)
    z_under = min(atom["z"] - atom["diameter"] / 2 - args.z_min for atom in atoms)
    z_over = max(atom["z"] + atom["diameter"] / 2 - args.z_max for atom in atoms)
    maximum_wall_excursion = max(0.0, -y_under, y_over, -z_under, z_over)
    if maximum_wall_excursion > args.wall_tolerance:
        raise RuntimeError(
            "sphere surfaces cross y/z walls beyond tolerance: "
            f"{maximum_wall_excursion} > {args.wall_tolerance}"
        )

    contributions = []
    for atom in atoms:
        radius = atom["diameter"] / 2
        volume = sphere_volume_in_x_slab(args.x_min, args.x_max, atom["x"], radius)
        if volume > 0:
            contributions.append((atom, volume))

    solid_volume = sum(item[1] for item in contributions)
    box_volume = (
        (args.x_max - args.x_min)
        * (args.y_max - args.y_min)
        * (args.z_max - args.z_min)
    )
    full = sum(
        1
        for atom, volume in contributions
        if abs(volume - math.pi * atom["diameter"] ** 3 / 6) < 1e-20
    )
    result = {
        "bed_dump": str(args.bed_dump.resolve()),
        "bed_dump_sha256": sha256(args.bed_dump),
        "box_m": {
            "x": [args.x_min, args.x_max],
            "y": [args.y_min, args.y_max],
            "z": [args.z_min, args.z_max],
        },
        "box_volume_m3": box_volume,
        "pebbles_total": len(atoms),
        "pebbles_intersecting_window": len(contributions),
        "pebbles_fully_inside_window": full,
        "pebbles_axially_clipped": len(contributions) - full,
        "nominal_solid_volume_m3": solid_volume,
        "nominal_porosity": 1.0 - solid_volume / box_volume,
        "maximum_yz_wall_excursion_m": maximum_wall_excursion,
        "wall_tolerance_m": args.wall_tolerance,
        "definition": (
            "Sum of nominal DEM sphere volumes analytically clipped by the two "
            "x planes; nanometre y/z wall excursions are treated as numerical "
            "tolerance and elastic sphere overlaps are not subtracted."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
