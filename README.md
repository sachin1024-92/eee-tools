# eee-tools

Small, tested calculators for Electrical & Electronics Engineering students and working engineers. Pure Python, no dependencies.

| Module | What it covers |
|---|---|
| `eeetools.hv` | Paschen breakdown voltage and minimum, Peek's corona inception gradient, relative air density, coaxial field and capacitance, Marx impulse generator, void field enhancement |
| `eeetools.signals` | dB conversions, RC cutoff, LC resonance, Nyquist rate and aliasing, ideal ADC SNR and ENOB, RMS, R-2R DAC output |
| `eeetools.power` | Three-phase P/Q/S, power-factor correction, per-unit base changes, fault level, transformer efficiency, feeder voltage drop |
| `eeetools.drives` | Synchronous speed and slip, shaft torque, induction-motor torque and breakdown slip, DC motor speed, V/f control |

## Install

```bash
git clone https://github.com/sachin1024-92/eee-tools.git
cd eee-tools
pip install -e .
```

## Use it from Python

```python
from eeetools import hv, power, drives

hv.paschen_breakdown_voltage(pressure_torr=760, gap_cm=1.0)   # ~35.5 kV for 1 cm of air
power.pf_correction_kvar(real_power_kw=100, pf_initial=0.7, pf_target=0.95)  # 69.2 kvar
drives.synchronous_speed_rpm(frequency_hz=50, poles=4)        # 1500 rpm
```

## Use it from the terminal

```bash
python -m eeetools                       # list modules
python -m eeetools hv                    # list functions in a module
python -m eeetools power pf_correction_kvar real_power_kw=100 pf_initial=0.7 pf_target=0.95
```

## Tests

```bash
pip install -e ".[dev]"
pytest
```

Every formula is checked against a hand-worked value or a physical property (for example, induction torque is highest at the breakdown slip).

## Notes on the models

These are textbook formulas, good for coursework, quick estimates and sanity checks. Paschen's law uses the standard constants for air and applies to uniform fields; Peek's law is empirical. Do not use them as the only basis for insulation or protection design.

## License

MIT
