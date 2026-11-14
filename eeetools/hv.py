"""High-voltage engineering calculators.

All quantities are SI unless the name says otherwise (kV, cm, torr).
"""

from __future__ import annotations

import math

EPS0 = 8.8541878128e-12  # F/m, vacuum permittivity


def paschen_breakdown_voltage(
    pressure_torr: float,
    gap_cm: float,
    a: float = 15.0,
    b: float = 365.0,
    gamma: float = 0.01,
) -> float:
    """Breakdown voltage (V) of a uniform-field gas gap from Paschen's law.

    V = B*p*d / ln(A*p*d / ln(1 + 1/gamma))

    Defaults ``a`` (1/(cm*torr)) and ``b`` (V/(cm*torr)) are the usual textbook
    constants for air. Raises ValueError to the left of the curve's asymptote,
    where the formula has no physical solution.
    """
    if pressure_torr <= 0 or gap_cm <= 0:
        raise ValueError("pressure and gap must be positive")
    pd = pressure_torr * gap_cm
    denom = math.log(a * pd / math.log(1.0 + 1.0 / gamma))
    if denom <= 0:
        raise ValueError(f"p*d = {pd:g} torr*cm is below the Paschen asymptote")
    return b * pd / denom


def paschen_minimum(a: float = 15.0, b: float = 365.0, gamma: float = 0.01) -> tuple[float, float]:
    """Return (pd_min in torr*cm, V_min in volts) of the Paschen curve."""
    k = math.log(1.0 + 1.0 / gamma)
    pd_min = math.e * k / a
    return pd_min, b * pd_min


def relative_air_density(pressure_kpa: float, temp_c: float) -> float:
    """Relative air density delta, referred to 101.3 kPa and 20 degC."""
    return (pressure_kpa / 101.3) * (293.0 / (273.0 + temp_c))


def peek_corona_inception_gradient(
    conductor_radius_cm: float,
    delta: float = 1.0,
    surface_factor: float = 1.0,
) -> float:
    """Visual corona inception gradient (kV peak/cm) at a round conductor surface.

    Peek's empirical law for parallel conductors:
    g_v = 30 * m * delta * (1 + 0.301 / sqrt(delta * r)).
    """
    if conductor_radius_cm <= 0 or delta <= 0:
        raise ValueError("radius and air density must be positive")
    return 30.0 * surface_factor * delta * (1.0 + 0.301 / math.sqrt(delta * conductor_radius_cm))


def coaxial_field(voltage: float, r: float, inner_radius: float, outer_radius: float) -> float:
    """Electric field (V/m) at radius ``r`` in a coaxial geometry."""
    if not 0 < inner_radius < outer_radius:
        raise ValueError("need 0 < inner_radius < outer_radius")
    if not inner_radius <= r <= outer_radius:
        raise ValueError("r must lie inside the insulation")
    return voltage / (r * math.log(outer_radius / inner_radius))


def coaxial_capacitance_per_m(inner_radius: float, outer_radius: float, eps_r: float = 1.0) -> float:
    """Capacitance per metre (F/m) of a coaxial cable."""
    if not 0 < inner_radius < outer_radius:
        raise ValueError("need 0 < inner_radius < outer_radius")
    return 2.0 * math.pi * EPS0 * eps_r / math.log(outer_radius / inner_radius)


def optimal_coaxial_ratio() -> float:
    """Outer/inner radius ratio that minimises the conductor-surface field (= e)."""
    return math.e


def marx_generator(stage_capacitance: float, charging_voltage: float, stages: int) -> dict[str, float]:
    """Ideal Marx impulse generator: erected voltage, discharge capacitance, energy."""
    if stages < 1:
        raise ValueError("stages must be >= 1")
    return {
        "output_voltage": stages * charging_voltage,
        "discharge_capacitance": stage_capacitance / stages,
        "stored_energy": 0.5 * stages * stage_capacitance * charging_voltage**2,
    }


def impulse_voltage_efficiency(generator_capacitance: float, load_capacitance: float) -> float:
    """Approximate voltage efficiency C1 / (C1 + C2) of an impulse generator."""
    if generator_capacitance <= 0 or load_capacitance < 0:
        raise ValueError("capacitances must be positive")
    return generator_capacitance / (generator_capacitance + load_capacitance)


def void_field_enhancement(eps_r: float) -> float:
    """Field in a thin flat gas void relative to the solid dielectric (= eps_r).

    Useful for partial-discharge inception estimates: a thin void perpendicular
    to the field sees eps_r times the stress of the surrounding insulation.
    """
    if eps_r < 1:
        raise ValueError("relative permittivity must be >= 1")
    return eps_r
