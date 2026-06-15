#!/usr/bin/env pvpython
"""Render publication-style OpenFOAM model and mesh figures with ParaView.

Run this script with ParaView's ``pvpython`` or ``pvbatch``. It creates a
``.foam`` marker for the selected OpenFOAM case when needed, renders the solid
interface and computational-domain outline, and renders a central mesh slice
with cell edges visible.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from paraview.simple import (  # type: ignore
    ColorBy,
    Delete,
    GetActiveViewOrCreate,
    OpenFOAMReader,
    Outline,
    Render,
    ResetCamera,
    STLReader,
    SaveScreenshot,
    SetActiveSource,
    Show,
    Slice,
)

try:
    from paraview.simple import _DisableFirstRenderCameraReset as disable_first_render_camera_reset  # type: ignore
except ImportError:  # pragma: no cover - ParaView-version dependent
    def disable_first_render_camera_reset() -> None:
        """Compatibility fallback for ParaView builds without the helper."""
        return None


def script_path() -> Path:
    """Return this script path under both pvpython and paraview --script."""
    if "__file__" in globals():
        return Path(__file__).resolve()
    for arg in sys.argv:
        candidate = Path(arg)
        if candidate.name == "render_openfoam_paraview_figures.py" and candidate.exists():
            return candidate.resolve()
    fallback = Path.cwd() / "project" / "papers" / "paper2_voxel_topology_clogging" / "scripts" / "render_openfoam_paraview_figures.py"
    if fallback.exists():
        return fallback.resolve()
    raise RuntimeError("Cannot locate render_openfoam_paraview_figures.py; run from the repository root or use pvpython.")


PROJECT_ROOT = script_path().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
DEFAULT_CASE = PAPER_DIR / "flow_solver_results" / "openfoam" / "N10000_peak_blockage"
DEFAULT_OUT = PAPER_DIR / "figures" / "openfoam_paraview"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the ParaView rendering workflow."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=Path, default=DEFAULT_CASE, help="OpenFOAM case directory.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT, help="Directory for rendered figure files.")
    parser.add_argument("--case-label", default=None, help="Optional label used in output filenames.")
    parser.add_argument("--width", type=int, default=3200, help="Screenshot width in pixels.")
    parser.add_argument("--height", type=int, default=2200, help="Screenshot height in pixels.")
    return parser.parse_args()


def require_case_files(case_dir: Path) -> Path:
    """Validate the OpenFOAM case and return the solid-interface STL path."""
    required = [
        case_dir / "constant" / "polyMesh" / "boundary",
        case_dir / "constant" / "polyMesh" / "points",
        case_dir / "constant" / "polyMesh" / "faces",
    ]
    missing = [str(path) for path in required if not path.exists()]
    stl_path = case_dir / "constant" / "triSurface" / "solid_interface.stl"
    if not stl_path.exists():
        missing.append(str(stl_path))
    if missing:
        raise FileNotFoundError("OpenFOAM case is incomplete; missing: " + ", ".join(missing))
    return stl_path


def make_case_marker(case_dir: Path) -> Path:
    """Create and return the empty ``.foam`` file used by ParaView."""
    marker = case_dir / f"{case_dir.name}.foam"
    marker.touch(exist_ok=True)
    return marker


def setup_view(width: int, height: int):
    """Create a white-background ParaView render view with fixed dimensions."""
    view = GetActiveViewOrCreate("RenderView")
    view.ViewSize = [width, height]
    try:
        view.UseColorPaletteForBackground = 0
    except Exception:
        pass
    try:
        view.BackgroundColorMode = "Single Color"
    except Exception:
        pass
    view.Background = [1.0, 1.0, 1.0]
    try:
        view.Background2 = [1.0, 1.0, 1.0]
    except Exception:
        pass
    view.OrientationAxesVisibility = 0
    return view


def load_openfoam_case(case_marker: Path):
    """Load the OpenFOAM case using ParaView's OpenFOAM reader."""
    reader = OpenFOAMReader(FileName=str(case_marker))
    reader.CaseType = "Reconstructed Case"
    reader.SkipZeroTime = 1
    reader.MeshRegions = ["internalMesh"]
    try:
        reader.CellArrays = ["p", "U"]
    except Exception:
        pass
    return reader


def domain_bounds(reader) -> tuple[float, float, float, float, float, float]:
    """Return the reader bounds after updating the pipeline."""
    reader.UpdatePipeline()
    bounds = reader.GetDataInformation().GetBounds()
    if bounds is None or len(bounds) != 6:
        raise RuntimeError("Unable to determine OpenFOAM domain bounds.")
    return tuple(float(value) for value in bounds)


def set_camera(view, bounds: tuple[float, float, float, float, float, float], mode: str) -> None:
    """Set a deterministic oblique camera for model or mesh renders."""
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    cx = 0.5 * (xmin + xmax)
    cy = 0.5 * (ymin + ymax)
    cz = 0.5 * (zmin + zmax)
    dx = xmax - xmin
    dy = ymax - ymin
    dz = zmax - zmin
    span = max(dx, dy, dz)
    if mode == "mesh":
        view.CameraPosition = [cx + 0.18 * span, cy - 2.25 * span, cz + 0.12 * span]
        view.CameraFocalPoint = [cx, cy, cz]
        view.CameraViewUp = [0.0, 0.0, 1.0]
        view.CameraParallelScale = 0.56 * max(dx, dz)
    else:
        view.CameraPosition = [cx + 1.45 * span, cy - 1.95 * span, cz + 1.05 * span]
        view.CameraFocalPoint = [cx, cy, cz]
        view.CameraViewUp = [0.0, 0.0, 1.0]
        view.CameraParallelScale = 0.72 * max(dx, dy, dz)
    view.CameraParallelProjection = 1


def render_model(reader, stl_path: Path, out_png: Path, width: int, height: int) -> None:
    """Render solid interface plus computational-domain outline."""
    view = setup_view(width, height)
    stl = STLReader(FileNames=[str(stl_path)])
    stl_display = Show(stl, view)
    stl_display.Representation = "Surface"
    stl_display.DiffuseColor = [0.72, 0.74, 0.76]
    stl_display.Opacity = 0.72
    stl_display.Specular = 0.18
    stl_display.SpecularPower = 18.0

    outline = Outline(Input=reader)
    outline_display = Show(outline, view)
    outline_display.Representation = "Wireframe"
    outline_display.DiffuseColor = [0.12, 0.12, 0.12]
    outline_display.LineWidth = 3.0

    bounds = domain_bounds(reader)
    set_camera(view, bounds, "model")
    Render(view)
    SaveScreenshot(str(out_png), view, ImageResolution=[width, height], TransparentBackground=0)
    Delete(stl)
    Delete(outline)


def render_mesh_slice(reader, out_png: Path, width: int, height: int) -> None:
    """Render a central y-normal OpenFOAM mesh slice with cell edges."""
    view = setup_view(width, height)
    bounds = domain_bounds(reader)
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    slice_filter = Slice(Input=reader)
    slice_filter.SliceType = "Plane"
    slice_filter.SliceType.Origin = [
        0.5 * (xmin + xmax),
        0.5 * (ymin + ymax),
        0.5 * (zmin + zmax),
    ]
    slice_filter.SliceType.Normal = [0.0, 1.0, 0.0]
    slice_filter.Triangulatetheslice = 0
    slice_display = Show(slice_filter, view)
    slice_display.Representation = "Surface With Edges"
    slice_display.DiffuseColor = [0.74, 0.82, 0.88]
    slice_display.EdgeColor = [0.05, 0.05, 0.05]
    slice_display.LineWidth = 0.45
    ColorBy(slice_display, None)

    outline = Outline(Input=reader)
    outline_display = Show(outline, view)
    outline_display.Representation = "Wireframe"
    outline_display.DiffuseColor = [0.15, 0.15, 0.15]
    outline_display.LineWidth = 2.4

    set_camera(view, bounds, "mesh")
    ResetCamera(view)
    set_camera(view, bounds, "mesh")
    Render(view)
    SaveScreenshot(str(out_png), view, ImageResolution=[width, height], TransparentBackground=0)
    Delete(slice_filter)
    Delete(outline)


def main() -> None:
    """Render the requested OpenFOAM case and write a manifest."""
    args = parse_args()
    case_dir = args.case.resolve()
    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    label = args.case_label or case_dir.name

    disable_first_render_camera_reset()
    stl_path = require_case_files(case_dir)
    marker = make_case_marker(case_dir)
    reader = load_openfoam_case(marker)

    model_png = out_dir / f"{label}_model_domain_paraview.png"
    mesh_png = out_dir / f"{label}_mesh_slice_paraview.png"
    render_model(reader, stl_path, model_png, args.width, args.height)
    render_mesh_slice(reader, mesh_png, args.width, args.height)

    manifest = {
        "case_dir": str(case_dir),
        "case_marker": str(marker),
        "solid_interface_stl": str(stl_path),
        "model_render": str(model_png),
        "mesh_slice_render": str(mesh_png),
        "image_resolution": [args.width, args.height],
        "renderer": "ParaView OpenFOAMReader/STLReader",
    }
    manifest_path = out_dir / f"{label}_paraview_render_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
