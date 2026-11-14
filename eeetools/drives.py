"""Electric machines & drives calculators."""

from __future__ import annotations

import math


def synchronous_speed_rpm(frequency_hz: float, poles: int) -> float:
    if poles < 2 or poles % 2:
        raise ValueError("poles must be an even number >= 2")
    return 120.0 * frequency_hz / poles


def slip(sync_rpm: float, rotor_rpm: float) -> float:
    if sync_rpm <= 0:
        raise ValueError("synchronous speed must be positive")
    return (sync_rpm - rotor_rpm) / sync_rpm


def rotor_frequency_hz(supply_hz: float, slip_value: float) -> float:
    return slip_value * supply_hz


def torque_nm(power_w: float, speed_rpm: float) -> float:
    """Shaft torque from mechanical power and speed."""
    if speed_rpm <= 0:
        raise ValueError("speed must be positive")
    return power_w * 60.0 / (2.0 * math.pi * speed_rpm)


def induction_torque_nm(
    phase_voltage: float,
    slip_value: float,
    r1: float,
    x1: float,
    r2: float,
    x2: float,
    frequency_hz: float,
    poles: int,
    phases: int = 3,
) -> float:
    """Developed torque from the approximate equivalent circuit (rotor referred to stator)."""
    if slip_value == 0:
        return 0.0
    ws = 2.0 * math.pi * synchronous_speed_rpm(frequency_hz, poles) / 60.0
    z_sq = (r1 + r2 / slip_value) ** 2 + (x1 + x2) ** 2
    return phases * phase_voltage**2 * (r2 / slip_value) / (ws * z_sq)


def breakdown_slip(r1: float, x1: float, r2: float, x2: float) -> float:
    """Slip at maximum (pull-out) torque."""
    return r2 / math.sqrt(r1**2 + (x1 + x2) ** 2)


def dc_motor_speed_rpm(terminal_voltage: float, armature_current: float, armature_resistance: float, k_phi: float) -> float:
    """DC motor speed. ``k_phi`` is the back-EMF constant in V per rad/s."""
    if k_phi <= 0:
        raise ValueError("k_phi must be positive")
    back_emf = terminal_voltage - armature_current * armature_resistance
    return back_emf / k_phi * 60.0 / (2.0 * math.pi)


def vf_voltage(frequency_hz: float, rated_voltage: float, rated_frequency_hz: float, boost_voltage: float = 0.0) -> float:
    """Stator voltage command for constant V/f control, clamped at rated voltage."""
    if rated_frequency_hz <= 0 or frequency_hz < 0:
        raise ValueError("frequencies must be positive")
    v = boost_voltage + (rated_voltage - boost_voltage) * frequency_hz / rated_frequency_hz
    return min(v, rated_voltage)
