"""Part F -- detection volume, its separated losses, and V_eff.

THE THREE LOSSES ARE KEPT APART, as part F requires, because they are different things:
  1 - MM^3        the exact worst-case fractional volume loss at fixed threshold, for
                  sources uniform in Euclidean volume;
  3 (1 - MM)      its linear expansion, which is NOT the same number;
  1 - <M^3>       the population-average discretisation loss, measured from injections.

TWO LEGS, and only the first is fully computed here:
  TaylorF2 injections   pure discretisation. M_bank is the best match in the bank,
                        from the quadratic form in the injection's own metric.
  IMRPhenomD injections DECLARED APPROXIMATION. The exact quantity is the best match of
                        an IMRPhenomD signal against the whole TaylorF2 BANK, which needs
                        a fitting-factor search per injection and is not done here.
                        Instead q1bC part B's frozen ff_full -- the fitting factor of the
                        CONTINUOUS TaylorF2 family, at 28 mass points, both regions -- is
                        interpolated and composed multiplicatively with the discretisation
                        match. That composition assumes the two losses are independent,
                        which is not established. <ff_full^3> alone is reported beside it
                        as an INTERPOLATED FAMILY-ONLY ESTIMATE. The exact continuous-family
                        loss would be a lower bound on discrete-bank loss, but the 28-point
                        interpolation has no demonstrated one-sided error bound.

V_eff(MM) = <M_bank^3> / rho*(MM)^3, up to a constant, with rho* from part E's naive
trials model -- an upper bound on the threshold, so V_eff is a lower bound.
V_eff ignores noise fluctuations of |z| near threshold; q1bC part A's Rice distribution
is what would be needed to say how much that matters, and it is not folded in here.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import griddata

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit import draw
from geometry import MM, MU_MAX, analytic_metric, tau
from threshold import OPERATING_POINTS, naive_trials, solve_threshold

ROOT = Path(os.environ.get("GWMM_PROJECT", Path(__file__).resolve().parents[2]))
RESULTS = ROOT / "results" / "d1"
Q1BC = Path(os.environ.get(
    "GWMM_FROZEN_PACKAGE",
    str(ROOT / "jobs" / "2026-09-14_041516_derive-q1bc" / "out")))


def load_fitting_factors():
    """q1bC part B, frozen: ff_full at 28 signal mass points, both regions."""
    rows = json.loads((Q1BC / "data/part_b_summary.json").read_text())["rows"]
    masses = np.asarray([r["signal_masses"] for r in rows], dtype=float)
    ff = np.asarray([r["ff_full"] for r in rows], dtype=float)
    return masses, ff


def interpolate_ff(points, masses, ff):
    """Linear where the 28 points hull it, nearest outside. Declared, not exact."""
    out = griddata(masses, ff, points, method="linear")
    missing = ~np.isfinite(out)
    if missing.any():
        out[missing] = griddata(masses, ff, points[missing], method="nearest")
    return out


def measure(region, lattice, n, seed, mm=None):
    mm = MM if mm is None else mm
    tag = f"mm{round(mm * 100):03d}"
    raw = np.loadtxt(RESULTS / "banks" / f"bank_{region}_{lattice}_{tag}.txt")
    bank_tau = raw[:, 2:4]
    rng = np.random.default_rng(seed)
    injections = draw(region, n, rng)
    match = np.empty(n)
    for index, (m1, m2) in enumerate(injections):
        point = np.asarray(tau(m1, m2))
        metric = analytic_metric(m1, m2)
        delta = bank_tau - point
        match[index] = 1.0 - np.min(np.einsum("ij,jk,ik->i", delta, metric, delta))

    ff_masses, ff_values = load_fitting_factors()
    ff = interpolate_ff(injections, ff_masses, ff_values)
    combined = ff * match

    mu_max = 1.0 - mm
    result = {
        "region": region, "lattice": lattice, "minimal_match": mm,
        "n_templates": int(len(raw)), "n_injections": n, "seed": seed,
        "losses": {
            "worst_case_1_minus_MM3": 1.0 - mm ** 3,
            "linear_expansion_3_1_minus_MM": 3.0 * mu_max,
            "population_average_taylorf2": 1.0 - float(np.mean(match ** 3)),
            "population_average_imrphenomd_approx": 1.0 - float(np.mean(combined ** 3)),
            "imrphenomd_upper_bound_family_only": 1.0 - float(np.mean(ff ** 3)),
        },
        "mean_match_cubed": {"taylorf2": float(np.mean(match ** 3)),
                             "imrphenomd_approx": float(np.mean(combined ** 3)),
                             "family_only_bound": float(np.mean(ff ** 3))},
        "match_stats": {"min": float(match.min()), "median": float(np.median(match)),
                        "fraction_below_MM": float(np.mean(match < mm))},
        "ff_stats": {"min": float(ff.min()), "median": float(np.median(ff)),
                     "max": float(ff.max())},
    }
    n_trials = naive_trials(len(raw))
    result["rho_star"] = {}
    result["v_eff"] = {}
    for name, (fap, _) in OPERATING_POINTS.items():
        rho = solve_threshold(fap, n_trials)
        result["rho_star"][name] = rho
        result["v_eff"][name] = {
            "taylorf2": result["mean_match_cubed"]["taylorf2"] / rho ** 3,
            "imrphenomd_approx": result["mean_match_cubed"]["imrphenomd_approx"] / rho ** 3,
        }
    return result


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20260926
    out = {}
    print(f"Part F at MM = {MM}, {n} injections, seed {seed}\n")
    print(f"{'bank':22s} {'1-MM^3':>8s} {'3(1-MM)':>8s} {'1-<M^3> TF2':>12s} "
          f"{'1-<M^3> IMR':>12s} {'FF bound':>10s}")
    for region in ("main", "extended"):
        for lattice in ("hexagonal", "square"):
            key = f"{region}_{lattice}"
            r = measure(region, lattice, n, seed)
            out[key] = r
            L = r["losses"]
            print(f"{key:22s} {L['worst_case_1_minus_MM3']:8.5f} "
                  f"{L['linear_expansion_3_1_minus_MM']:8.5f} "
                  f"{L['population_average_taylorf2']:12.5f} "
                  f"{L['population_average_imrphenomd_approx']:12.5f} "
                  f"{L['imrphenomd_upper_bound_family_only']:10.5f}")
    print()
    print("V_eff (arbitrary units) at FAR = 1/(100 yr), TaylorF2 / IMRPhenomD-approx:")
    for key, r in out.items():
        v = r["v_eff"]["far_1_per_100yr"]
        print(f"  {key:22s} {v['taylorf2']:.6e}   {v['imrphenomd_approx']:.6e}"
              f"   (rho* = {r['rho_star']['far_1_per_100yr']:.4f})")
    path = RESULTS / f"part_f_mm{round(MM * 100):03d}.json"
    path.write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
