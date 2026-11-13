import math

import pytest

from eeetools import drives, hv, power, signals
from eeetools.__main__ import main


# --- high voltage ---------------------------------------------------------
def test_paschen_air_1cm_atmospheric_is_about_30kv():
    v = hv.paschen_breakdown_voltage(760, 1.0)
    assert 30e3 < v < 36e3


def test_paschen_minimum_is_lowest_point():
    pd_min, v_min = hv.paschen_minimum()
    assert v_min == pytest.approx(hv.paschen_breakdown_voltage(pd_min, 1.0))
    assert hv.paschen_breakdown_voltage(pd_min * 0.8, 1.0) > v_min
    assert hv.paschen_breakdown_voltage(pd_min * 1.5, 1.0) > v_min
    assert 250 < v_min < 400  # air: a few hundred volts


def test_paschen_rejects_left_of_asymptote():
    with pytest.raises(ValueError):
        hv.paschen_breakdown_voltage(0.1, 1.0)


def test_relative_air_density_reference():
    assert hv.relative_air_density(101.3, 20) == pytest.approx(1.0)


def test_peek_gradient_1cm_conductor():
    assert hv.peek_corona_inception_gradient(1.0) == pytest.approx(39.03)


def test_coaxial_field_peaks_at_conductor():
    inner = hv.coaxial_field(100e3, 0.01, 0.01, 0.02718281828)
    outer = hv.coaxial_field(100e3, 0.02718281828, 0.01, 0.02718281828)
    assert inner == pytest.approx(100e3 / 0.01, rel=1e-6)
    assert inner > outer


def test_coaxial_capacitance():
    c = hv.coaxial_capacitance_per_m(0.01, 0.01 * math.e, eps_r=2.3)
    assert c == pytest.approx(2 * math.pi * hv.EPS0 * 2.3)


def test_marx_generator():
    out = hv.marx_generator(0.1e-6, 100e3, 10)
    assert out["output_voltage"] == pytest.approx(1e6)
    assert out["discharge_capacitance"] == pytest.approx(10e-9)
    assert out["stored_energy"] == pytest.approx(5000)


def test_impulse_efficiency():
    assert hv.impulse_voltage_efficiency(10e-9, 1e-9) == pytest.approx(10 / 11)


# --- signals --------------------------------------------------------------
def test_db_round_trip():
    assert signals.db_power(100) == pytest.approx(20)
    assert signals.db_voltage(10) == pytest.approx(20)
    assert signals.from_db_power(3.0103) == pytest.approx(2, rel=1e-4)
    assert signals.from_db_voltage(signals.db_voltage(7.5)) == pytest.approx(7.5)


def test_rc_and_lc():
    assert signals.rc_cutoff_hz(1e3, 1e-6) == pytest.approx(159.155, rel=1e-5)
    assert signals.lc_resonance_hz(1e-3, 1e-6) == pytest.approx(5032.92, rel=1e-5)


def test_sampling():
    assert signals.nyquist_rate_hz(20e3) == 40e3
    assert signals.alias_frequency_hz(7e3, 10e3) == pytest.approx(3e3)
    assert signals.alias_frequency_hz(3e3, 10e3) == pytest.approx(3e3)


def test_adc():
    assert signals.adc_ideal_snr_db(12) == pytest.approx(74.0)
    assert signals.enob(74.0) == pytest.approx(12)


def test_rms_of_sine():
    n = 1000
    wave = [math.sin(2 * math.pi * k / n) for k in range(n)]
    assert signals.rms(wave) == pytest.approx(1 / math.sqrt(2), rel=1e-6)


def test_r2r_dac():
    assert signals.r2r_dac_output(8, 4, 1.8) == pytest.approx(0.9)
    assert signals.r2r_dac_output(15, 4, 1.8) == pytest.approx(1.6875)
    with pytest.raises(ValueError):
        signals.r2r_dac_output(16, 4, 1.8)


# --- power ----------------------------------------------------------------
def test_three_phase_power():
    out = power.three_phase_power(415, 100, 0.8)
    assert out["S"] == pytest.approx(71880.1, rel=1e-5)
    assert out["P"] == pytest.approx(57504.1, rel=1e-5)
    assert out["Q"] == pytest.approx(43128.1, rel=1e-5)


def test_pf_correction():
    kvar = power.pf_correction_kvar(100, 0.7, 0.95)
    assert kvar == pytest.approx(69.15, rel=1e-3)
    assert power.capacitance_for_kvar(kvar, 415) == pytest.approx(4.26e-4, rel=1e-2)


def test_per_unit():
    assert power.base_impedance(33, 100) == pytest.approx(10.89)
    assert power.per_unit_change_of_base(0.1, 11, 50, 11, 100) == pytest.approx(0.2)
    assert power.fault_level_mva(100, 0.05) == pytest.approx(2000)


def test_transformer_efficiency_peaks_where_losses_match():
    x = power.max_efficiency_load_fraction(1.0, 4.0)
    assert x == pytest.approx(0.5)
    peak = power.transformer_efficiency(100, x, 0.8, 1.0, 4.0)
    assert peak == pytest.approx(40 / 42)
    assert peak > power.transformer_efficiency(100, 0.3, 0.8, 1.0, 4.0)
    assert peak > power.transformer_efficiency(100, 1.0, 0.8, 1.0, 4.0)


def test_voltage_drop():
    assert power.voltage_drop_percent(100, 0.1, 0.05, 0.8, 415) == pytest.approx(4.59, rel=1e-2)


# --- drives ---------------------------------------------------------------
def test_synchronous_speed_and_slip():
    ns = drives.synchronous_speed_rpm(50, 4)
    assert ns == 1500
    s = drives.slip(ns, 1440)
    assert s == pytest.approx(0.04)
    assert drives.rotor_frequency_hz(50, s) == pytest.approx(2.0)
    with pytest.raises(ValueError):
        drives.synchronous_speed_rpm(50, 3)


def test_shaft_torque():
    assert drives.torque_nm(7500, 1440) == pytest.approx(49.74, rel=1e-3)


def test_induction_torque_peaks_at_breakdown_slip():
    args = dict(r1=0.5, x1=1.0, r2=0.4, x2=1.0, frequency_hz=50, poles=4)
    sm = drives.breakdown_slip(0.5, 1.0, 0.4, 1.0)
    t_max = drives.induction_torque_nm(230, sm, **args)
    assert t_max > drives.induction_torque_nm(230, sm * 0.7, **args)
    assert t_max > drives.induction_torque_nm(230, sm * 1.4, **args)
    assert drives.induction_torque_nm(230, 0, **args) == 0


def test_dc_motor_speed():
    assert drives.dc_motor_speed_rpm(220, 20, 0.5, 1.4) == pytest.approx(1432.4, rel=1e-4)


def test_vf_control():
    assert drives.vf_voltage(25, 400, 50) == pytest.approx(200)
    assert drives.vf_voltage(60, 400, 50) == 400


# --- cli ------------------------------------------------------------------
def test_cli(capsys):
    assert main(["drives", "synchronous_speed_rpm", "frequency_hz=50", "poles=4"]) == 0
    assert capsys.readouterr().out.strip() == "1500"
    assert main(["drives", "synchronous_speed_rpm", "frequency_hz=50", "poles=3"]) == 2
    assert main(["hv"]) == 0
