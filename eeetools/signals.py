"""Signals & systems helpers."""

from __future__ import annotations

import math
from typing import Iterable


def db_power(ratio: float) -> float:
    """Power ratio to decibels."""
    if ratio <= 0:
        raise ValueError("ratio must be positive")
    return 10.0 * math.log10(ratio)


def db_voltage(ratio: float) -> float:
    """Voltage (amplitude) ratio to decibels."""
    if ratio <= 0:
        raise ValueError("ratio must be positive")
    return 20.0 * math.log10(ratio)


def from_db_power(db: float) -> float:
    return 10.0 ** (db / 10.0)


def from_db_voltage(db: float) -> float:
    return 10.0 ** (db / 20.0)


def rc_cutoff_hz(resistance: float, capacitance: float) -> float:
    """-3 dB frequency of a first-order RC filter."""
    if resistance <= 0 or capacitance <= 0:
        raise ValueError("R and C must be positive")
    return 1.0 / (2.0 * math.pi * resistance * capacitance)


def lc_resonance_hz(inductance: float, capacitance: float) -> float:
    if inductance <= 0 or capacitance <= 0:
        raise ValueError("L and C must be positive")
    return 1.0 / (2.0 * math.pi * math.sqrt(inductance * capacitance))


def nyquist_rate_hz(max_signal_hz: float) -> float:
    """Minimum sampling rate for a band-limited signal."""
    if max_signal_hz <= 0:
        raise ValueError("frequency must be positive")
    return 2.0 * max_signal_hz


def alias_frequency_hz(signal_hz: float, sample_hz: float) -> float:
    """Apparent frequency of a sampled tone, folded into [0, fs/2]."""
    if sample_hz <= 0 or signal_hz < 0:
        raise ValueError("frequencies must be positive")
    f = signal_hz % sample_hz
    return min(f, sample_hz - f)


def adc_ideal_snr_db(bits: int) -> float:
    """SNR of an ideal N-bit ADC for a full-scale sine: 6.02 N + 1.76 dB."""
    if bits < 1:
        raise ValueError("bits must be >= 1")
    return 6.02 * bits + 1.76


def enob(sinad_db: float) -> float:
    """Effective number of bits from a measured SINAD."""
    return (sinad_db - 1.76) / 6.02


def rms(samples: Iterable[float]) -> float:
    values = list(samples)
    if not values:
        raise ValueError("no samples")
    return math.sqrt(sum(v * v for v in values) / len(values))


def r2r_dac_output(code: int, bits: int, v_ref: float) -> float:
    """Ideal output voltage of an N-bit R-2R ladder DAC for a given input code."""
    if bits < 1 or not 0 <= code < 2**bits:
        raise ValueError("code out of range for this resolution")
    return v_ref * code / 2**bits
