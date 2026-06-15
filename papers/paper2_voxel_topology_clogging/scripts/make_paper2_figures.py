#!/usr/bin/env python3
"""Create manuscript figures for Paper 2 on voxel topology and clogging."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, Rectangle


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PAPER_DIR = PROJECT_ROOT / "papers" / "paper2_voxel_topology_clogging"
DATA_DIR = PAPER_DIR / "data"
FIG_DIR = PAPER_DIR / "figures"
TABLE_DIR = PAPER_DIR / "tables"

BASELINE_TOPOLOGY = DATA_DIR / "baseline_topology_metrics_effective.json"
BASELINE_VOXEL = PROJECT_ROOT / "data" / "processed" / "ct_pipeline_li4sio4_1mm_10k_axial_cuboid_piston_compacted" / "bed_voxel_effective.npz"
REPRESENTATIVE = DATA_DIR / "paper1_representative_ct_mechanisms.csv"
LOADING = DATA_DIR / "paper1_loading_voxel_mechanisms.csv"
LOADING_BTC = DATA_DIR / "paper1_loading_BTC_source.csv"
LOADING_BLOCKAGE = DATA_DIR / "paper1_high_load_blockage_source.csv"


def configure_matplotlib() -> None:
    """Configure a clean, journal-oriented Matplotlib style."""
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 8,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.8,
            "axes.labelsize": 8,
            "axes.titlesize": 8,
            "xtick.labelsize": 7.2,
            "ytick.labelsize": 7.2,
            "legend.fontsize": 7,
            "legend.frameon": False,
        }
    )


def panel_label(ax: plt.Axes, label: str, x: float = -0.12, y: float = 1.05) -> None:
    """Place a bold panel label in axes coordinates."""
    ax.text(x, y, label, transform=ax.transAxes, weight="bold", fontsize=9, va="top")


def panel_label_inside(ax: plt.Axes, label: str) -> None:
    """Place a bold panel label inside a crowded axes."""
    ax.text(
        0.02,
        0.98,
        label,
        transform=ax.transAxes,
        weight="bold",
        fontsize=9,
        va="top",
        ha="left",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8, "pad": 1.0},
    )


def save_figure(fig: plt.Figure, stem: str) -> None:
    """Save a figure as PNG, PDF, and SVG."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    for suffix, kwargs in {".png": {"dpi": 600}, ".pdf": {}, ".svg": {}}.items():
        fig.savefig(FIG_DIR / f"{stem}{suffix}", bbox_inches="tight", **kwargs)
    preview = FIG_DIR / f"{stem}_gray_preview.png"
    fig.savefig(preview, dpi=300, bbox_inches="tight", pil_kwargs={"compress_level": 6})
    try:
        from PIL import Image, ImageOps

        with Image.open(preview) as image:
            ImageOps.grayscale(image.convert("RGB")).save(preview)
    except ImportError:
        pass


def draw_workflow(ax: plt.Axes, representative: pd.DataFrame, loading: pd.DataFrame) -> None:
    """Draw a compact diagnostic triad separating breakthrough from clogging."""
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    max_btc = float(representative["final_BTC"].max())
    max_blockage = float(loading["subvoxel_max_blockage_ratio"].max()) * 1e6
    if "connectivity_loss" in loading:
        max_connectivity_loss = float(pd.to_numeric(loading["connectivity_loss"], errors="coerce").fillna(0).max())
    else:
        c0 = float(loading["voxel_outlet_connected_fraction_x"].iloc[0])
        max_connectivity_loss = float((1.0 - loading["voxel_outlet_connected_fraction_x"] / c0).max())

    ax.text(0.04, 0.90, "Diagnostic separation", ha="left", va="center", fontsize=8.0, weight="bold", color="#333333")
    rows = [
        ("outlet arrival", "BTC", max_btc, 0.10, "#6f91b4", f"max {max_btc:.3f}"),
        ("local loading", r"$B_{max}$", max_blockage / 40.0, 0.00, "#b34d4f", f"{max_blockage:.1f}e-6"),
        ("pore skeleton", r"$C_{loss}$", min(max_connectivity_loss / 0.01, 1.0), 0.0, "#1b7837", f"{max_connectivity_loss:.1e}"),
    ]
    for index, (label, symbol, value, floor, color, value_text) in enumerate(rows):
        y = 0.70 - index * 0.20
        x0, x1 = 0.12, 0.58
        ax.hlines(y, x0, x1, color="#d0d0d0", linewidth=2.2, zorder=1)
        xdot = x0 + (x1 - x0) * max(floor, min(value, 1.0))
        ax.scatter([xdot], [y], s=120, color=color, edgecolor="#222222", linewidth=0.5, zorder=3)
        ax.text(0.05, y, symbol, ha="center", va="center", fontsize=8.0, weight="bold", color=color)
        ax.text(0.14, y + 0.065, label, ha="left", va="center", fontsize=6.8, color="#333333")
        ax.text(0.60, y, value_text, ha="left", va="center", fontsize=6.8, color="#333333")

    ax.add_patch(FancyArrowPatch((0.73, 0.50), (0.80, 0.50), arrowstyle="-|>", mutation_scale=11, linewidth=1.0, color="#555555"))
    ax.add_patch(
        Rectangle((0.82, 0.37), 0.15, 0.26, facecolor="#f2f2f2", edgecolor="#4d4d4d", linewidth=0.7)
    )
    ax.text(0.895, 0.535, "pre-\nclogging", ha="center", va="center", fontsize=7.4, weight="bold", linespacing=0.9, color="#333333")
    ax.text(0.895, 0.415, "retained\nskeleton", ha="center", va="center", fontsize=5.9, color="#555555", linespacing=0.95)
    panel_label(ax, "a")


def draw_metric_summary(ax: plt.Axes, metrics: dict[str, float]) -> None:
    """Draw compact baseline topology metrics as a structural-reference summary."""
    names = ["porosity", "largest void", "outlet void", "Df / 3"]
    values = [
        metrics["porosity"],
        metrics["largest_connected_void_fraction"],
        metrics["outlet_connected_fraction"],
        metrics["fractal_dimension"] / 3.0,
    ]
    colors = ["#4d4d4d", "#2166ac", "#1b7837", "#b2182b"]
    y = np.arange(len(names))[::-1]
    ax.scatter(values, y, s=55, color=colors, edgecolor="#222222", linewidth=0.45, zorder=3)
    ax.hlines(y, 0.0, values, color="#d6d6d6", linewidth=1.0, zorder=1)
    for value, yi in zip(values, y):
        ax.text(min(value + 0.025, 1.02), yi, f"{value:.3f}", va="center", fontsize=6.8, color="#333333")
    ax.set_yticks(y, names)
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("normalized value")
    ax.set_title("Connected structural reference")
    ax.grid(True, axis="x", linewidth=0.35, alpha=0.35)
    ax.text(
        0.02,
        0.03,
        f"Euler = {metrics['euler_number']:.0f}\nQ = {metrics['topological_charge']:.3f}",
        transform=ax.transAxes,
        fontsize=7,
        va="bottom",
        ha="left",
    )
    panel_label(ax, "b")


def draw_representative_states(ax: plt.Axes, representative: pd.DataFrame) -> None:
    """Draw breakthrough against drag-to-weight ratio for representative drive states."""
    role_order = ["low_drive_no_breakthrough", "intermediate_drive_weak_breakthrough", "high_drive_stronger_breakthrough"]
    colors = {
        "low_drive_no_breakthrough": "#7b9dbd",
        "intermediate_drive_weak_breakthrough": "#c44e52",
        "high_drive_stronger_breakthrough": "#4d4d4d",
    }
    labels = {
        "low_drive_no_breakthrough": "low drive",
        "intermediate_drive_weak_breakthrough": "weak breakthrough",
        "high_drive_stronger_breakthrough": "stronger breakthrough",
    }
    ordered_rows = []
    for role in role_order:
        row = representative[representative["role"] == role].iloc[0]
        ordered_rows.append(row)
        ax.scatter(
            row["drag_to_weight_ratio"],
            row["final_BTC"],
            s=52 + row["subvoxel_max_blockage_ratio"] * 1e6 * 2.8,
            color=colors[role],
            edgecolor="#222222",
            linewidth=0.45,
            label=labels[role],
        )
        ax.annotate(
            labels[role],
            xy=(row["drag_to_weight_ratio"], row["final_BTC"]),
            xytext=(5, 4),
            textcoords="offset points",
            fontsize=6.7,
            color=colors[role],
        )
    ax.set_xlabel(r"$F_d/W$")
    ax.set_ylabel("final BTC")
    ax.set_xlim(15, 130)
    ax.set_ylim(-0.004, 0.088)
    ax.set_title("Transport axis: drive primarily affects penetration")
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.text(0.04, 0.91, r"point size: $B_{\max}$", transform=ax.transAxes, fontsize=6.7, color="#555555")
    panel_label(ax, "c")


def draw_loading_connectivity(ax: plt.Axes, loading: pd.DataFrame) -> None:
    """Draw loading-dependent blockage and connectivity loss."""
    completed = loading.sort_values("debris_total_number")
    y = np.arange(len(completed))
    blockage = completed["subvoxel_max_blockage_ratio"].to_numpy(dtype=float) * 1e6
    if "connectivity_loss" in completed:
        connectivity_loss = completed["connectivity_loss"].to_numpy(dtype=float)
    else:
        c0 = float(completed["voxel_outlet_connected_fraction_x"].iloc[0])
        connectivity_loss = 1.0 - completed["voxel_outlet_connected_fraction_x"].to_numpy(dtype=float) / c0
    labels = [f"{int(n)}" for n in completed["debris_total_number"]]
    ax.hlines(y, 0.0, blockage, color="#d0d0d0", linewidth=1.0, zorder=1)
    ax.scatter(blockage, y, s=60, marker="o", color="#4d4d4d", edgecolor="#222222", linewidth=0.45, label=r"$B_{\max}$", zorder=3)
    ax.set_yticks(y, labels)
    ax.set_xlabel(r"max local blockage $B_{\max}$ ($\times 10^{-6}$)")
    ax.set_ylabel(r"injected debris count $N_f$")
    ax.set_xlim(0, max(42, float(blockage.max()) + 8))
    ax.set_ylim(-0.5, len(completed) - 0.5)
    ax.set_title("Deposition axis: loading raises local blockage")
    ax.grid(True, axis="x", linewidth=0.35, alpha=0.35)
    if np.allclose(connectivity_loss, 0.0):
        ax.text(0.04, 0.90, r"relative $C_{loss}=0$ for all", transform=ax.transAxes, fontsize=6.8, color="#1b7837")
    panel_label(ax, "d")


def load_baseline_voxel() -> np.ndarray:
    """Load the effective baseline voxel array."""
    if not BASELINE_VOXEL.exists():
        raise FileNotFoundError(f"Missing baseline voxel file: {BASELINE_VOXEL}")
    data = np.load(BASELINE_VOXEL, allow_pickle=True)
    voxel = data["voxel"]
    if voxel.ndim != 3:
        raise ValueError(f"Expected a 3D voxel array, got shape {voxel.shape}")
    return voxel


def load_baseline_voxel_metadata() -> dict:
    """Load metadata stored alongside the effective baseline voxel array."""
    if not BASELINE_VOXEL.exists():
        raise FileNotFoundError(f"Missing baseline voxel file: {BASELINE_VOXEL}")
    data = np.load(BASELINE_VOXEL, allow_pickle=True)
    if "metadata" not in data.files:
        raise KeyError(f"Missing metadata in voxel file: {BASELINE_VOXEL}")
    return json.loads(str(data["metadata"]))


def box_counting_points(void_mask: np.ndarray) -> pd.DataFrame:
    """Compute box-counting points for a binary void mask."""
    min_dim = min(void_mask.shape)
    sizes = [2, 3, 4, 5, 6, 8, 10, 12, 15, 20]
    sizes = [s for s in sizes if s <= min_dim // 2]
    rows: list[dict[str, float]] = []
    for size in sizes:
        padded_shape = [int(np.ceil(n / size) * size) for n in void_mask.shape]
        padded = np.zeros(padded_shape, dtype=bool)
        padded[: void_mask.shape[0], : void_mask.shape[1], : void_mask.shape[2]] = void_mask
        reshaped = padded.reshape(
            padded_shape[0] // size,
            size,
            padded_shape[1] // size,
            size,
            padded_shape[2] // size,
            size,
        )
        occupied = reshaped.any(axis=(1, 3, 5))
        count = int(occupied.sum())
        rows.append(
            {
                "box_size_voxels": size,
                "box_count": count,
                "log_inverse_box_size": float(np.log(1.0 / size)),
                "log_count": float(np.log(count)),
            }
        )
    return pd.DataFrame(rows)


def fit_fractal_dimension(box_data: pd.DataFrame) -> tuple[float, float, np.ndarray]:
    """Fit the box-counting slope and return Df, R2 and fitted values."""
    x = box_data["log_inverse_box_size"].to_numpy(dtype=float)
    y = box_data["log_count"].to_numpy(dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    y_fit = slope * x + intercept
    ss_res = float(np.sum((y - y_fit) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    return float(slope), r2, y_fit


def draw_voxel_slice(ax: plt.Axes, voxel: np.ndarray) -> None:
    """Draw a representative x-z slice through the baseline voxel field."""
    y_index = voxel.shape[1] // 2
    slice_xz = voxel[:, y_index, :].T
    ax.imshow(slice_xz == 1, origin="lower", cmap="Greys", interpolation="nearest", aspect="auto")
    ax.set_title("Baseline voxel slice")
    ax.set_xlabel("x voxel")
    ax.set_ylabel("z voxel")
    panel_label(ax, "a")


def draw_axial_porosity_profile(ax: plt.Axes, voxel: np.ndarray, metadata: dict) -> None:
    """Draw the axial porosity profile with transverse variability bands."""
    void = voxel == 0
    voxel_size_mm = float(metadata["voxel_size"]) * 1e3
    x_mm = (np.arange(voxel.shape[0]) + 0.5) * voxel_size_mm
    yz_porosity = void.mean(axis=2)
    mean_porosity = yz_porosity.mean(axis=1)
    q10, q90 = np.quantile(yz_porosity, [0.10, 0.90], axis=1)
    ax.fill_between(x_mm, q10, q90, color="#d9d9d9", linewidth=0, label="10-90% transverse band")
    ax.plot(x_mm, mean_porosity, color="#2166ac", linewidth=1.15, label="axial mean")
    ax.axhline(float(mean_porosity.mean()), color="#4d4d4d", linewidth=0.9, linestyle=":", label="bed mean")
    ax.set_xlim(0, float(metadata["domain"]["Lx"]) * 1e3)
    ax.set_ylim(0, 1)
    ax.set_xlabel("axial position x (mm)")
    ax.set_ylabel("void fraction")
    ax.set_title("Axial porosity profile")
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.legend(loc="lower right")
    panel_label(ax, "a")


def draw_void_projection(ax: plt.Axes, voxel: np.ndarray, metadata: dict) -> None:
    """Draw a transverse-averaged pore map without showing a binary slice."""
    void_projection = (voxel == 0).mean(axis=1).T
    void_cmap = mpl.colors.LinearSegmentedColormap.from_list(
        "void_fraction_light",
        ["#f7fbff", "#d9e8f5", "#9cc3df", "#3c7fa8"],
    )
    extent = [
        0.0,
        float(metadata["domain"]["Lx"]) * 1e3,
        0.0,
        float(metadata["domain"]["Lz"]) * 1e3,
    ]
    image = ax.imshow(
        void_projection,
        origin="lower",
        cmap=void_cmap,
        interpolation="bilinear",
        aspect="auto",
        vmin=0.15,
        vmax=1,
        extent=extent,
    )
    ax.set_title("Transverse-averaged void map")
    ax.set_xlabel("axial position x (mm)")
    ax.set_ylabel("height z (mm)")
    cbar = ax.figure.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("void fraction")
    panel_label(ax, "b")


def draw_box_counting(ax: plt.Axes, box_data: pd.DataFrame, metrics: dict[str, float]) -> None:
    """Draw the baseline fractal box-counting fit."""
    df_fit, r2_fit, y_fit = fit_fractal_dimension(box_data)
    x = box_data["log_inverse_box_size"].to_numpy(dtype=float)
    y = box_data["log_count"].to_numpy(dtype=float)
    ax.scatter(x, y, s=42, color="#4d4d4d", edgecolor="#222222", linewidth=0.45, label="box counts")
    ax.plot(x, y_fit, color="#b2182b", linewidth=1.2, label="linear fit")
    ax.set_xlabel("log(1 / box size)")
    ax.set_ylabel("log(N)")
    ax.set_title("Box-counting fit")
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.text(
        0.62,
        0.08,
        f"Df = {metrics['fractal_dimension']:.3f}\nR2 = {metrics['fractal_fit_r2']:.3f}",
        transform=ax.transAxes,
        fontsize=7,
        va="bottom",
        ha="left",
    )
    ax.legend(loc="upper right")
    panel_label(ax, "c")


def draw_topology_bar(ax: plt.Axes, metrics: dict[str, float]) -> None:
    """Draw a compact topology metric dot summary."""
    names = ["porosity", "largest\nvoid", "outlet\nvoid", "Df/3", "|Q|"]
    values = [
        metrics["porosity"],
        metrics["largest_connected_void_fraction"],
        metrics["outlet_connected_fraction"],
        metrics["fractal_dimension"] / 3.0,
        abs(metrics["topological_charge"]),
    ]
    colors = ["#4d4d4d", "#2166ac", "#1b7837", "#b2182b", "#f4a582"]
    y = np.arange(len(names))[::-1]
    ax.hlines(y, 0, values, color="#cfcfcf", linewidth=1.0, zorder=1)
    ax.scatter(values, y, s=58, color=colors, edgecolor="#222222", linewidth=0.45, zorder=3)
    for value, yi in zip(values, y):
        ax.text(value + 0.025, yi, f"{value:.3f}", va="center", ha="left", fontsize=6.8)
    ax.set_yticks(y, names)
    ax.set_xlim(0, 1.08)
    ax.set_xlabel("normalized value")
    ax.set_title("Connected topology metrics")
    ax.grid(True, axis="x", linewidth=0.35, alpha=0.35)
    ax.text(
        0.38,
        0.08,
        f"Euler = {metrics['euler_number']:.0f}",
        transform=ax.transAxes,
        fontsize=7,
        ha="center",
        va="bottom",
    )
    panel_label(ax, "d")


def representative_style() -> tuple[dict[str, str], dict[str, str]]:
    """Return labels and colors for representative drive states."""
    labels = {
        "low_drive_no_breakthrough": "low drive",
        "intermediate_drive_weak_breakthrough": "weak BTC",
        "high_drive_stronger_breakthrough": "higher BTC",
    }
    colors = {
        "low_drive_no_breakthrough": "#6f91b4",
        "intermediate_drive_weak_breakthrough": "#b34d4f",
        "high_drive_stronger_breakthrough": "#4d4d4d",
    }
    return labels, colors


def load_representative_profiles(representative: pd.DataFrame) -> pd.DataFrame:
    """Load local blockage profiles for representative states."""
    rows: list[pd.DataFrame] = []
    labels, _ = representative_style()
    for _, row in representative.iterrows():
        profile_path = Path(row["profile_path"])
        if not profile_path.exists():
            raise FileNotFoundError(f"Missing blockage profile: {profile_path}")
        profile = pd.read_csv(profile_path)
        profile["role"] = row["role"]
        profile["state_label"] = labels[row["role"]]
        profile["case_name"] = row["case_name"]
        profile["final_BTC"] = row["final_BTC"]
        profile["drag_to_weight_ratio"] = row["drag_to_weight_ratio"]
        rows.append(profile)
    return pd.concat(rows, ignore_index=True)


def draw_state_map(ax: plt.Axes, representative: pd.DataFrame) -> None:
    """Draw representative state positions in drive-breakthrough space."""
    labels, colors = representative_style()
    markers = {
        "low_drive_no_breakthrough": "o",
        "intermediate_drive_weak_breakthrough": "s",
        "high_drive_stronger_breakthrough": "^",
    }
    for _, row in representative.iterrows():
        ax.scatter(
            row["drag_to_weight_ratio"],
            row["final_BTC"],
            s=62,
            marker=markers[row["role"]],
            color=colors[row["role"]],
            edgecolor="#222222",
            linewidth=0.45,
            zorder=3,
        )
        ax.annotate(
            labels[row["role"]],
            xy=(row["drag_to_weight_ratio"], row["final_BTC"]),
            xytext=(5, 4),
            textcoords="offset points",
            fontsize=6.8,
            color=colors[row["role"]],
        )
    ax.set_xlabel(r"$F_d/W$")
    ax.set_ylabel("final BTC")
    ax.set_title("Breakthrough increases with drive")
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.text(0.04, 0.92, "representative states", transform=ax.transAxes, fontsize=6.7, color="#555555")
    panel_label(ax, "a")


def draw_blockage_profiles(ax: plt.Axes, profiles: pd.DataFrame) -> None:
    """Draw local blockage profiles along the flow direction."""
    _, colors = representative_style()
    line_styles = {
        "low_drive_no_breakthrough": "-",
        "intermediate_drive_weak_breakthrough": "--",
        "high_drive_stronger_breakthrough": "-.",
    }
    markers = {
        "low_drive_no_breakthrough": "o",
        "intermediate_drive_weak_breakthrough": "s",
        "high_drive_stronger_breakthrough": "^",
    }
    role_order = [
        "low_drive_no_breakthrough",
        "intermediate_drive_weak_breakthrough",
        "high_drive_stronger_breakthrough",
    ]
    for role in role_order:
        group = profiles[profiles["role"] == role]
        group = group.sort_values("x_center_m")
        y_raw = group["blockage_ratio"].to_numpy(dtype=float) * 1e6
        y_smooth = pd.Series(y_raw).rolling(window=9, center=True, min_periods=1).mean().to_numpy()
        x_mm = group["x_center_m"].to_numpy(dtype=float) * 1e3
        ax.plot(x_mm, y_raw, color=colors[role], linewidth=0.45, alpha=0.18)
        ax.plot(
            x_mm,
            y_smooth,
            color=colors[role],
            linestyle=line_styles[role],
            linewidth=1.35,
            alpha=0.95,
            marker=markers[role],
            markersize=2.0,
            markerfacecolor="white",
            markeredgewidth=0.5,
            markevery=60,
            label=group["state_label"].iloc[0],
        )
        peak = group.loc[group["blockage_ratio"].idxmax()]
        peak_x = float(peak["x_center_m"]) * 1e3
        peak_y = float(peak["blockage_ratio"]) * 1e6
        ax.scatter(
            peak_x,
            peak_y,
            s=30,
            color=colors[role],
            edgecolor="#222222",
            linewidth=0.35,
            zorder=4,
        )
        ax.annotate(
            group["state_label"].iloc[0],
            xy=(peak_x, peak_y),
            xytext=(-7, 5) if peak_x > 40 else (5, 5),
            textcoords="offset points",
            fontsize=6.7,
            color=colors[role],
            ha="right" if peak_x > 40 else "left",
            va="bottom",
        )
    ax.axvspan(44.5, 45.5, color="#f0f0f0", zorder=0)
    ax.text(0.985, 0.07, "outlet plane", transform=ax.transAxes, ha="right", fontsize=6.8, color="#777777")
    ax.set_xlabel("axial position x (mm)")
    ax.set_ylabel(r"local blockage $B(x)$ ($\times 10^{-6}$)")
    ax.set_title("Deposition zone shifts with drive")
    ax.set_xlim(0, 45.5)
    ax.grid(True, linewidth=0.35, alpha=0.35)
    panel_label(ax, "b")


def draw_centroid_shift(ax: plt.Axes, representative: pd.DataFrame) -> None:
    """Draw debris centroid and mean position shifts without connecting sparse states."""
    labels, colors = representative_style()
    y_positions = np.arange(len(representative))[::-1]
    ordered = representative.copy()
    ordered["state_label"] = ordered["role"].map(labels)
    ordered = ordered.sort_values("drag_to_weight_ratio")
    y_positions = np.arange(len(ordered))
    for y, (_, row) in zip(y_positions, ordered.iterrows()):
        x0 = row["x_mean_over_L"]
        x1 = row["deposition_centroid_over_L"]
        ax.hlines(y, min(x0, x1), max(x0, x1), color=colors[row["role"]], linewidth=1.0, alpha=0.55, zorder=1)
        ax.scatter(x0, y - 0.06, marker="o", s=52, color=colors[row["role"]], edgecolor="#222222", linewidth=0.45, label="debris mean" if y == 0 else None, zorder=3)
        ax.scatter(x1, y + 0.06, marker="s", s=46, facecolor="white", edgecolor=colors[row["role"]], linewidth=1.1, label="blockage centroid" if y == 0 else None, zorder=3)
    ax.set_yticks(y_positions, ordered["state_label"])
    ax.set_xlim(0, 0.62)
    ax.set_xlabel("x / L")
    ax.set_title("Debris and blockage fronts advance")
    ax.grid(True, axis="x", linewidth=0.35, alpha=0.35)
    ax.legend(loc="lower right")
    panel_label(ax, "c")


def draw_connectivity_vs_btc(ax: plt.Axes, representative: pd.DataFrame) -> None:
    """Draw connectivity loss for representative states."""
    labels, colors = representative_style()
    markers = {
        "low_drive_no_breakthrough": "o",
        "intermediate_drive_weak_breakthrough": "s",
        "high_drive_stronger_breakthrough": "^",
    }
    ordered = representative.copy()
    ordered["state_label"] = ordered["role"].map(labels)
    ordered = ordered.sort_values("drag_to_weight_ratio")
    y_positions = np.arange(len(ordered))
    c0 = float(ordered["voxel_outlet_connected_fraction_x"].iloc[0])
    connectivity_loss = np.clip(1.0 - ordered["voxel_outlet_connected_fraction_x"].to_numpy(dtype=float) / c0, 0.0, 1.0)
    for y, (_, row) in zip(y_positions, ordered.iterrows()):
        loss = connectivity_loss[y]
        ax.scatter(
            loss,
            y,
            s=64,
            marker=markers[row["role"]],
            color=colors[row["role"]],
            edgecolor="#222222",
            linewidth=0.45,
            zorder=3,
        )
    ax.axvline(0.0, color="#1b7837", linewidth=1.0, linestyle=":")
    ax.hlines(y_positions, 0, np.maximum(connectivity_loss, 1e-12), color="#cfcfcf", linewidth=1.0, zorder=1)
    ax.set_yticks(y_positions, ordered["state_label"])
    ax.set_xlim(-0.002, 0.030)
    ax.set_xlabel(r"connectivity loss $C_{loss}$")
    ax.set_title("No reconstructed connectivity loss")
    ax.grid(True, axis="x", linewidth=0.35, alpha=0.35)
    ax.text(
        0.06,
        0.90,
        r"$C_{loss}=0$",
        transform=ax.transAxes,
        fontsize=6.7,
        color="#1b7837",
    )
    panel_label(ax, "d", x=-0.10, y=1.04)


def prepare_loading_summary(loading: pd.DataFrame) -> pd.DataFrame:
    """Prepare loading-scan structural metrics and a pressure-free clogging index."""
    summary = loading.sort_values("debris_total_number").copy()
    if summary.empty:
        raise ValueError("Loading summary is empty.")
    baseline_connectivity = float(summary["voxel_outlet_connected_fraction_x"].iloc[0])
    if baseline_connectivity <= 0:
        raise ValueError("Outlet-connected void fraction must be positive.")
    summary["connectivity_loss"] = np.clip(
        1.0 - summary["voxel_outlet_connected_fraction_x"].astype(float) / baseline_connectivity,
        0.0,
        1.0,
    )
    summary["Ib_no_pressure"] = 0.5 * summary["subvoxel_max_blockage_ratio"].astype(float) + 0.5 * summary["connectivity_loss"]
    summary["Ib_state"] = np.where(summary["Ib_no_pressure"] < 0.3, "safe", "blocked")
    summary["pressure_used"] = False
    return summary


def draw_loading_btc(ax: plt.Axes, btc: pd.DataFrame) -> None:
    """Draw time-resolved BTC curves for the loading scan."""
    colors = {3000: "#6f91b4", 6000: "#b34d4f", 10000: "#4d4d4d"}
    line_styles = {3000: "-", 6000: "--", 10000: "-."}
    markers = {3000: "o", 6000: "s", 10000: "^"}
    for number, group in btc.groupby("debris_total_number"):
        group = group.sort_values("elapsed_time")
        ax.plot(
            group["elapsed_time"] * 1e3,
            group["BTC"],
            color=colors.get(int(number), "#4d4d4d"),
            linestyle=line_styles.get(int(number), "-"),
            linewidth=1.25,
            marker=markers.get(int(number), "o"),
            markersize=2.3,
            markerfacecolor="white",
            markeredgewidth=0.55,
            markevery=6,
            label=f"$N_f$={int(number)}",
        )
        end = group.iloc[-1]
        ax.annotate(
            f"{int(number)}",
            xy=(end["elapsed_time"] * 1e3, end["BTC"]),
            xytext=(4, 0),
            textcoords="offset points",
            color=colors.get(int(number), "#4d4d4d"),
            fontsize=6.8,
            va="center",
            clip_on=False,
        )
    ax.set_xlim(28, 41)
    ax.set_ylim(-0.0005, max(0.020, float(btc["BTC"].max()) * 1.18))
    ax.set_xlabel("elapsed time after release (ms)")
    ax.set_ylabel("BTC")
    ax.set_title("Weak late breakthrough")
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.text(0.04, 0.92, r"labels: $N_f$", transform=ax.transAxes, fontsize=6.7, color="#555555")
    panel_label(ax, "a")


def draw_loading_final_metrics(ax: plt.Axes, summary: pd.DataFrame) -> None:
    """Draw final BTC as a horizontal dot plot for sparse loading states."""
    ordered = summary.sort_values("debris_total_number").copy()
    y = np.arange(len(ordered))
    btc = ordered["final_BTC"].to_numpy(dtype=float)
    labels = [f"{int(n)}" for n in ordered["debris_total_number"]]
    colors = ["#6f91b4", "#b34d4f", "#4d4d4d"]
    markers = ["o", "s", "^"]
    ax.hlines(y, 0.0, btc, color="#cfcfcf", linewidth=1.0, zorder=1)
    for yi, value, color, marker in zip(y, btc, colors, markers):
        ax.scatter(
            value,
            yi,
            s=68,
            marker=marker,
            color=color,
            edgecolor="#222222",
            linewidth=0.45,
            zorder=3,
        )
    ax.set_yticks(y, labels)
    ax.set_xlabel("final BTC")
    ax.set_ylabel(r"debris count $N_f$")
    ax.set_title("Final BTC is non-monotonic")
    ax.set_xlim(0, max(0.022, 1.25 * float(btc.max())))
    ax.set_ylim(-0.5, len(ordered) - 0.5)
    ax.grid(True, axis="x", linewidth=0.35, alpha=0.35)
    ax.text(0.04, 0.90, "single-seed states; no fit", transform=ax.transAxes, fontsize=6.7, color="#555555")
    panel_label_inside(ax, "b")


def draw_loading_blockage_profiles(ax: plt.Axes, blockage: pd.DataFrame) -> None:
    """Draw loading-dependent axial blockage profiles."""
    colors = {3000: "#6f91b4", 6000: "#b34d4f", 10000: "#4d4d4d"}
    line_styles = {3000: "-", 6000: "--", 10000: "-."}
    markers = {3000: "o", 6000: "s", 10000: "^"}
    for number, group in blockage.groupby("debris_total_number"):
        group = group.sort_values("x_center")
        ax.plot(
            group["x_center"] * 1e3,
            group["blockage_ratio"] * 1e6,
            color=colors.get(int(number), "#4d4d4d"),
            linestyle=line_styles.get(int(number), "-"),
            linewidth=1.25,
            marker=markers.get(int(number), "o"),
            markersize=2.2,
            markerfacecolor="white",
            markeredgewidth=0.55,
            markevery=3,
            label=f"$N_f$={int(number)}",
        )
        peak = group.loc[group["blockage_ratio"].idxmax()]
        ax.scatter(peak["x_center"] * 1e3, peak["blockage_ratio"] * 1e6, s=28, color=colors.get(int(number), "#4d4d4d"), edgecolor="#222222", linewidth=0.35, zorder=4)
    ax.set_xlabel("axial position x (mm)")
    ax.set_ylabel(r"local blockage $B(x)$ ($\times 10^{-6}$)")
    ax.set_title("Inventory raises deposition")
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.legend(loc="upper right")
    panel_label(ax, "c")


def draw_loading_clogging_index(ax: plt.Axes, summary: pd.DataFrame) -> None:
    """Draw the pressure-free clogging-index margin below the screening reference."""
    ordered = summary.sort_values("debris_total_number").copy()
    y = np.arange(len(ordered))
    threshold = 0.3
    ib_ratio = ordered["Ib_no_pressure"].to_numpy(dtype=float) / threshold
    order_margin = -np.log10(ib_ratio)
    labels = [f"{int(n)}" for n in ordered["debris_total_number"]]
    colors = ["#6f91b4", "#b34d4f", "#4d4d4d"]
    markers = ["o", "s", "^"]
    ax.axvline(0.0, color="#1b7837", linewidth=1.0, linestyle=":")
    ax.hlines(y, 0.0, order_margin, color="#cfcfcf", linewidth=1.0, zorder=1)
    for yi, value, color, marker in zip(y, ib_ratio, colors, markers):
        margin = -np.log10(value)
        ax.scatter(
            margin,
            yi,
            s=68,
            marker=marker,
            color=color,
            edgecolor="#222222",
            linewidth=0.45,
            zorder=3,
        )
    ax.set_yticks(y, labels)
    ax.set_xlim(0, max(5.2, float(order_margin.max()) + 0.35))
    ax.set_ylim(-0.5, len(ordered) - 0.5)
    ax.set_xlabel(r"orders below $I_b=0.3$")
    ax.set_ylabel(r"debris count $N_f$")
    ax.set_title("Far below screening reference")
    ax.grid(True, axis="x", linewidth=0.35, alpha=0.35)
    ax.text(0.04, 0.90, r"$-\log_{10}(I_b/0.3)$", transform=ax.transAxes, fontsize=6.7, color="#555555")
    panel_label(ax, "d")


def make_figure4() -> None:
    """Create Paper 2 Figure 4 for loading-dependent clogging response."""
    loading = pd.read_csv(LOADING)
    btc = pd.read_csv(LOADING_BTC)
    blockage = pd.read_csv(LOADING_BLOCKAGE)
    summary = prepare_loading_summary(loading)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    summary.to_csv(TABLE_DIR / "paper2_fig4_loading_summary_source.csv", index=False)
    btc.to_csv(TABLE_DIR / "paper2_fig4_loading_btc_source.csv", index=False)
    blockage.to_csv(TABLE_DIR / "paper2_fig4_loading_blockage_source.csv", index=False)

    fig = plt.figure(figsize=(7.2, 4.8), constrained_layout=True)
    grid = fig.add_gridspec(2, 2)
    ax_btc = fig.add_subplot(grid[0, 0])
    ax_final = fig.add_subplot(grid[0, 1])
    ax_blockage = fig.add_subplot(grid[1, 0])
    ax_ib = fig.add_subplot(grid[1, 1])
    draw_loading_btc(ax_btc, btc)
    draw_loading_final_metrics(ax_final, summary)
    draw_loading_blockage_profiles(ax_blockage, blockage)
    draw_loading_clogging_index(ax_ib, summary)
    save_figure(fig, "paper2_fig4_loading_clogging_response")
    plt.close(fig)


def make_figure3() -> None:
    """Create Paper 2 Figure 3 for representative debris-deposition states."""
    representative = pd.read_csv(REPRESENTATIVE)
    profiles = load_representative_profiles(representative)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    representative.to_csv(TABLE_DIR / "paper2_fig3_representative_state_source.csv", index=False)
    profiles.to_csv(TABLE_DIR / "paper2_fig3_blockage_profiles_source.csv", index=False)
    fig = plt.figure(figsize=(7.2, 4.8), constrained_layout=True)
    grid = fig.add_gridspec(2, 2)
    ax_state = fig.add_subplot(grid[0, 0])
    ax_profile = fig.add_subplot(grid[0, 1])
    ax_centroid = fig.add_subplot(grid[1, 0])
    ax_connectivity = fig.add_subplot(grid[1, 1])
    draw_state_map(ax_state, representative)
    draw_blockage_profiles(ax_profile, profiles)
    draw_centroid_shift(ax_centroid, representative)
    draw_connectivity_vs_btc(ax_connectivity, representative)
    save_figure(fig, "paper2_fig3_representative_debris_blockage")
    plt.close(fig)


def make_figure2() -> None:
    """Create Paper 2 Figure 2 showing baseline voxel topology and fractal fit."""
    metrics = json.loads(BASELINE_TOPOLOGY.read_text(encoding="utf-8"))
    voxel = load_baseline_voxel()
    metadata = load_baseline_voxel_metadata()
    void_mask = voxel == 0
    box_data = box_counting_points(void_mask)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    box_data.to_csv(TABLE_DIR / "paper2_fig2_box_counting_source.csv", index=False)
    fig = plt.figure(figsize=(7.2, 4.8), constrained_layout=True)
    grid = fig.add_gridspec(2, 2)
    ax_profile = fig.add_subplot(grid[0, 0])
    ax_projection = fig.add_subplot(grid[0, 1])
    ax_box = fig.add_subplot(grid[1, 0])
    ax_summary = fig.add_subplot(grid[1, 1])
    draw_axial_porosity_profile(ax_profile, voxel, metadata)
    draw_void_projection(ax_projection, voxel, metadata)
    draw_box_counting(ax_box, box_data, metrics)
    draw_topology_bar(ax_summary, metrics)
    save_figure(fig, "paper2_fig2_baseline_voxel_topology")
    plt.close(fig)


def make_figure1() -> None:
    """Create Paper 2 Figure 1 from existing topology and blockage evidence."""
    metrics = json.loads(BASELINE_TOPOLOGY.read_text(encoding="utf-8"))
    representative = pd.read_csv(REPRESENTATIVE)
    loading = pd.read_csv(LOADING)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    summary = pd.DataFrame(
        [
            {
                "porosity": metrics["porosity"],
                "largest_connected_void_fraction": metrics["largest_connected_void_fraction"],
                "outlet_connected_fraction": metrics["outlet_connected_fraction"],
                "fractal_dimension": metrics["fractal_dimension"],
                "fractal_fit_r2": metrics["fractal_fit_r2"],
                "euler_number": metrics["euler_number"],
                "topological_charge": metrics["topological_charge"],
            }
        ]
    )
    summary.to_csv(TABLE_DIR / "paper2_fig1_baseline_topology_source.csv", index=False)

    fig = plt.figure(figsize=(7.2, 4.5), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, width_ratios=[1.05, 1.0])
    ax_workflow = fig.add_subplot(grid[0, 0])
    ax_summary = fig.add_subplot(grid[0, 1])
    ax_rep = fig.add_subplot(grid[1, 0])
    ax_loading = fig.add_subplot(grid[1, 1])
    draw_workflow(ax_workflow, representative, loading)
    draw_metric_summary(ax_summary, metrics)
    draw_representative_states(ax_rep, representative)
    draw_loading_connectivity(ax_loading, loading)
    save_figure(fig, "paper2_fig1_voxel_topology_framework")
    plt.close(fig)


def main() -> int:
    """Generate the current Paper 2 figures."""
    configure_matplotlib()
    make_figure1()
    make_figure2()
    make_figure3()
    make_figure4()
    print(f"Wrote Paper 2 figures to: {FIG_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
