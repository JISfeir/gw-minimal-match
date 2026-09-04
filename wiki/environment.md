# Environment

## How to build it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` is a complete `pip freeze` from the reference platform, so it pins
every transitive dependency, not just the direct ones.

**No conda.** Everything here installs from PyPI wheels, including the compiled pieces
(`lalsuite` behind `pycbc`). This is deliberate: the reproducible half of the project
should not depend on a conda installation.

## Reference platform

| | |
|---|---|
| OS | Linux x86_64 (WSL2 Ubuntu 24.04) |
| Python | CPython 3.12 |
| Key packages | numpy, scipy, matplotlib, sympy, pycbc (+ lalsuite), astropy |

Exact versions are in `requirements.txt`. Regenerate it after any install:

```bash
pip freeze > requirements.txt
```

## What each package is for

| package | used for |
|---|---|
| `numpy`, `scipy` | inner products, FFTs, linear algebra, the metric fit |
| `sympy` | deriving the analytic Owen metric symbolically for the check |
| `pycbc` (+ `lalsuite`) | waveform generation (TaylorF2, IMRPhenomD), PSD curves |
| `astropy` | cosmology / comoving volume for the sensitive-volume conversion |
| `matplotlib` | figures |

## Running code

The venv auto-activates only inside `~/GW-AI-course` (a `~/.bashrc` block from course
setup). This project is outside that tree, so activate it explicitly:

```bash
cd ~/gw-minimal-match && source .venv/bin/activate
```
