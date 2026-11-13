"""Power-system calculators."""

from __future__ import annotations

import math


def three_phase_power(line_voltage: float, line_current: float, power_factor: float) -> dict[str, float]:
    """Real (W), reactive (var) and apparent (VA) power of a balanced 3-phase load."""
    if not 0 <= power_factor <= 1:
        raise ValueError("power factor must be between 0 and 1")
    s = math.sqrt(3.0) * line_voltage * line_current
    return {"S": s, "P": s * power_factor, "Q": s * math.sin(math.acos(power_factor))}


def pf_correction_kvar(real_power_kw: float, pf_initial: float, pf_target: float) -> float:
    """Capacitor bank rating (kvar) to raise the power factor of a load."""
    for pf in (pf_initial, pf_target):
        if not 0 < pf <= 1:
            raise ValueError("power factors must be in (0, 1]")
    if pf_target < pf_initial:
        raise ValueError("target power factor is below the initial one")
    return real_power_kw * (math.tan(math.acos(pf_initial)) - math.tan(math.acos(pf_target)))


def capacitance_for_kvar(kvar: float, line_voltage: float, frequency_hz: float = 50.0) -> float:
    """Per-phase capacitance (F) of a delta-connected bank delivering ``kvar``."""
    if line_voltage <= 0 or frequency_hz <= 0:
        raise ValueError("voltage and frequency must be positive")
    return (kvar * 1e3 / 3.0) / (2.0 * math.pi * frequency_hz * line_voltage**2)


def base_impedance(base_kv: float, base_mva: float) -> float:
    """Per-unit base impedance (ohm) from line-line kV and 3-phase MVA."""
    if base_mva <= 0:
        raise ValueError("base MVA must be positive")
    return base_kv**2 / base_mva


def per_unit_change_of_base(z_pu: float, kv_old: float, mva_old: float, kv_new: float, mva_new: float) -> float:
    """Convert a per-unit impedance to a new voltage / MVA base."""
    return z_pu * (kv_old / kv_new) ** 2 * (mva_new / mva_old)


def transformer_efficiency(
    rated_kva: float, load_fraction: float, power_factor: float, core_loss_kw: float, full_load_copper_loss_kw: float
) -> float:
    """Efficiency (0..1) of a transformer at a fraction of rated load."""
    output = rated_kva * load_fraction * power_factor
    losses = core_loss_kw + load_fraction**2 * full_load_copper_loss_kw
    if output <= 0:
        raise ValueError("output power must be positive")
    return output / (output + losses)


def max_efficiency_load_fraction(core_loss_kw: float, full_load_copper_loss_kw: float) -> float:
    """Load fraction at which transformer efficiency peaks (core loss = copper loss)."""
    if core_loss_kw <= 0 or full_load_copper_loss_kw <= 0:
        raise ValueError("losses must be positive")
    return math.sqrt(core_loss_kw / full_load_copper_loss_kw)


def fault_level_mva(base_mva: float, z_pu: float) -> float:
    """Three-phase short-circuit level behind a per-unit impedance."""
    if z_pu <= 0:
        raise ValueError("impedance must be positive")
    return base_mva / z_pu


def voltage_drop_percent(
    line_current: float, resistance: float, reactance: float, power_factor: float, line_voltage: float
) -> float:
    """Approximate 3-phase feeder voltage drop, % of line voltage (lagging load)."""
    if not 0 <= power_factor <= 1:
        raise ValueError("power factor must be between 0 and 1")
    sin_phi = math.sin(math.acos(power_factor))
    drop = math.sqrt(3.0) * line_current * (resistance * power_factor + reactance * sin_phi)
    return 100.0 * drop / line_voltage
