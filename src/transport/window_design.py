"""Physical time-window estimates for debris migration DEM cases."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TransportWindowEstimate:
    """Container for one physical transport-window estimate."""

    gas_velocity: float
    df_over_dp: float
    bed_length: float
    debris_diameter: float
    stokes_relaxation_time: float
    nominal_advective_time: float
    recommended_runtime: float
    recommended_output_interval_steps: int
    feasible_short_run: bool


def stokes_relaxation_time(debris_density: float, debris_diameter: float, gas_viscosity: float) -> float:
    """Return the Stokes particle velocity relaxation time.

    The estimate is ``tau_p = rho_d * df^2 / (18 * mu_g)`` and is used only as
    a physical scale check. It does not replace pore-scale DEM transport.
    """
    if debris_density <= 0:
        raise ValueError("debris_density must be positive.")
    if debris_diameter <= 0:
        raise ValueError("debris_diameter must be positive.")
    if gas_viscosity <= 0:
        raise ValueError("gas_viscosity must be positive.")
    return float(debris_density) * float(debris_diameter) ** 2 / (18.0 * float(gas_viscosity))


def nominal_advective_time(bed_length: float, gas_velocity: float, path_length_factor: float = 1.0) -> float:
    """Estimate a lower-bound migration time from bed length and gas velocity."""
    if bed_length <= 0:
        raise ValueError("bed_length must be positive.")
    if gas_velocity <= 0:
        raise ValueError("gas_velocity must be positive.")
    if path_length_factor <= 0:
        raise ValueError("path_length_factor must be positive.")
    return float(path_length_factor) * float(bed_length) / float(gas_velocity)


def recommend_output_interval_steps(runtime: float, dt: float, frames_target: int, min_interval_steps: int) -> int:
    """Return an output interval that targets a desired number of frames."""
    if runtime <= 0:
        raise ValueError("runtime must be positive.")
    if dt <= 0:
        raise ValueError("dt must be positive.")
    if frames_target <= 0:
        raise ValueError("frames_target must be positive.")
    if min_interval_steps <= 0:
        raise ValueError("min_interval_steps must be positive.")
    estimated = int(round(runtime / float(dt) / int(frames_target)))
    return max(int(min_interval_steps), estimated)


def estimate_transport_window(
    dp: float,
    debris_density: float,
    gas_viscosity: float,
    dt: float,
    gas_velocity: float,
    df_over_dp: float,
    bed_length: float,
    path_length_factor: float = 1.5,
    safety_factor: float = 1.2,
    max_recommended_runtime_s: float = 0.1,
    output_frames_target: int = 50,
    min_output_interval_steps: int = 10000,
) -> TransportWindowEstimate:
    """Estimate whether a physical DEM transport case is a feasible short run."""
    if dp <= 0:
        raise ValueError("dp must be positive.")
    if df_over_dp <= 0:
        raise ValueError("df_over_dp must be positive.")
    if safety_factor <= 0:
        raise ValueError("safety_factor must be positive.")
    if max_recommended_runtime_s <= 0:
        raise ValueError("max_recommended_runtime_s must be positive.")

    debris_diameter = float(dp) * float(df_over_dp)
    tau_p = stokes_relaxation_time(debris_density, debris_diameter, gas_viscosity)
    advective_time = nominal_advective_time(bed_length, gas_velocity, path_length_factor)
    runtime = float(safety_factor) * advective_time
    interval = recommend_output_interval_steps(runtime, dt, output_frames_target, min_output_interval_steps)
    return TransportWindowEstimate(
        gas_velocity=float(gas_velocity),
        df_over_dp=float(df_over_dp),
        bed_length=float(bed_length),
        debris_diameter=debris_diameter,
        stokes_relaxation_time=tau_p,
        nominal_advective_time=advective_time,
        recommended_runtime=runtime,
        recommended_output_interval_steps=interval,
        feasible_short_run=runtime <= float(max_recommended_runtime_s),
    )
