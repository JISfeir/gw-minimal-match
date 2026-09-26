"""Part E -- the detection threshold, in a declared-approximate form.

WHAT IS EXACT HERE AND WHAT IS NOT, stated up front because part E's whole value is the
honesty of its trials model:

  * The single-sample tail P(|z| > r) = exp(-r^2/2) is q1bC part A's result, verified
    there on simulated noise. Taken as given.
  * The exact combination over N independent trials, FAP = 1 - (1 - p)^N, is used
    throughout; the rare-tail Poisson form 1 - exp(-N p) is evaluated alongside so its
    error is shown rather than assumed.
  * N_eff IS NOT CALIBRATED HERE. The pre-registered part E calls for estimating an
    effective independent-trial rate from simulated Gaussian noise filtered through the
    bank. That is not done. Instead the NAIVE BOUND is used:
        N_naive = N_templates * f_sample * T_obs,
    which treats every template and every sample as independent and therefore
    OVER-counts trials, so the rho* it yields is an UPPER bound on the threshold. The
    gap between the naive bound and a calibrated nu_eff is the thing this part does not
    measure, and every number below carries that caveat.

Operating point and sensitivities are the pre-registered ones (wiki/conventions.md).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).resolve().parent))

RESULTS = Path("/home/juan/gw-minimal-match/results/d1")
SECONDS_PER_YEAR = 365.25 * 24 * 3600
F_SAMPLE = 2048.0          # Nyquist for f_high = 1024 Hz
T_OBS = 1.0                # years, pre-registered

OPERATING_POINTS = {
    # name: (target FAP, how it was defined)
    "far_1_per_100yr": (1.0 - math.exp(-0.01),
                        "FAR = 1/(100 yr), T_obs = 1 yr, FAP = 1 - exp(-FAR T_obs)"),
    "far_1_per_yr": (1.0 - math.exp(-1.0),
                     "FAR = 1/yr, permissive sensitivity -- NOT a detection significance"),
    "five_sigma": (float(norm.sf(5.0)),
                   "5 sigma by its one-sided global probability, 2.8665e-7"),
}


def single_sample_tail(rho):
    """q1bC part A, verified there: signal-free |z| has P(|z| > r) = exp(-r^2/2)."""
    return math.exp(-0.5 * rho * rho)


def solve_threshold(target_fap, n_trials):
    """Invert FAP = 1 - (1 - p(rho*))^N exactly for rho*."""
    def residual(rho):
        p = single_sample_tail(rho)
        # log1p form: (1-p)^N underflows to 1 for the p we work at
        return -np.expm1(n_trials * np.log1p(-p)) - target_fap
    return brentq(residual, 1.0, 40.0, xtol=1e-12, rtol=1e-14)


def poisson_threshold(target_fap, n_trials):
    """The rare-tail approximation FAP ~ 1 - exp(-N p), for comparison only."""
    def residual(rho):
        return -np.expm1(-n_trials * single_sample_tail(rho)) - target_fap
    return brentq(residual, 1.0, 40.0, xtol=1e-12, rtol=1e-14)


def naive_trials(n_templates, t_obs_years=T_OBS):
    return n_templates * F_SAMPLE * t_obs_years * SECONDS_PER_YEAR


def report(counts):
    out = {"convention": {"f_sample_hz": F_SAMPLE, "t_obs_years": T_OBS,
                          "seconds_per_year": SECONDS_PER_YEAR,
                          "trials_model": "naive bound N = N_templates * f_sample * T_obs; "
                                          "NOT a calibrated nu_eff; over-counts trials, so "
                                          "rho* is an upper bound"},
           "operating_points": {}, "banks": {}}
    for name, (fap, how) in OPERATING_POINTS.items():
        out["operating_points"][name] = {"target_fap": fap, "definition": how}
    print(f"{'bank':22s} {'N_tmpl':>7s} {'N_trials':>11s}  "
          + "  ".join(f"{k:>16s}" for k in OPERATING_POINTS))
    for label, n in counts.items():
        n_trials = naive_trials(n)
        row = {"n_templates": n, "n_trials_naive": n_trials, "rho_star": {},
               "rho_star_poisson": {}, "poisson_relative_error": {}}
        cells = []
        for name, (fap, _) in OPERATING_POINTS.items():
            exact = solve_threshold(fap, n_trials)
            approx = poisson_threshold(fap, n_trials)
            row["rho_star"][name] = exact
            row["rho_star_poisson"][name] = approx
            row["poisson_relative_error"][name] = abs(approx - exact) / exact
            cells.append(f"{exact:16.4f}")
        out["banks"][label] = row
        print(f"{label:22s} {n:7d} {n_trials:11.3e}  " + "  ".join(cells))
    worst = max(r["poisson_relative_error"][k] for r in out["banks"].values()
                for k in OPERATING_POINTS)
    out["worst_poisson_relative_error"] = worst
    print(f"\nrare-tail Poisson approximation: worst relative error on rho* = {worst:.2e}")
    return out


def main():
    part_d = json.loads((RESULTS / "part_d_mm097.json").read_text())
    counts = {k: part_d[k]["n_templates"] for k in
              ("main_hexagonal", "main_square", "extended_hexagonal", "extended_square")}
    print("Part E at the headline MM = 0.97, naive-trials model\n")
    out = report(counts)
    out["source"] = "counts from results/d1/part_d_mm097.json"
    (RESULTS / "part_e_mm097.json").write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(f"\nwrote {RESULTS / 'part_e_mm097.json'}")


if __name__ == "__main__":
    main()
