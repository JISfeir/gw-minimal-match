"""Part F, closing piece: V_eff(MM) and its maximum.

V_eff(MM) = <M_bank^3> / rho*(MM)^3, up to a constant. The hypothesis pre-registered in
the objective is that between MM = 0.97 and 0.99 the threshold increase costs about as
much volume as the finer bank recovers, so that an optimum exists. It is a hypothesis to
test, not a result to confirm.

THE CAVEAT THAT MUST TRAVEL WITH EVERY POINT BELOW MM = 0.97, from q1bC part C: the
quadratic predictor's worst relative error over direction was measured INSIDE the 10 %
criterion at mu_pred = 0.03 (8.74 % main, 8.98 % extended) and FAILS at mu_pred = 0.05,
at 19/21 main and 17/39 extended mass points. So MM = 0.95 and 0.96 rest on a predictor
outside its validated range, and any optimum located there is provisional, not a result.

Injection metrics are computed ONCE and reused across every bank, since they depend on
the injection and not on MM.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.interpolate import griddata

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit import draw
from geometry import analytic_metric, tau
from threshold import OPERATING_POINTS, naive_trials, solve_threshold
from volume import interpolate_ff, load_fitting_factors

RESULTS = Path("/home/juan/gw-minimal-match/results/d1")
MM_GRID = (0.95, 0.96, 0.97, 0.98, 0.99)
VALIDATED_FROM = 0.97


def prepare(region, n, seed):
    rng = np.random.default_rng(seed)
    injections = draw(region, n, rng)
    point = np.asarray([tau(*m) for m in injections])
    metric = np.asarray([analytic_metric(*m) for m in injections])
    ff_masses, ff_values = load_fitting_factors()
    ff = interpolate_ff(injections, ff_masses, ff_values)
    return injections, point, metric, ff


def match_against(bank_tau, point, metric):
    out = np.empty(len(point))
    for i in range(len(point)):
        delta = bank_tau - point[i]
        out[i] = 1.0 - np.min(np.einsum("ij,jk,ik->i", delta, metric[i], delta))
    return out


def run(region, n=2000, seed=20260927, bootstrap=400):
    injections, point, metric, ff = prepare(region, n, seed)
    rng = np.random.default_rng(seed + 1)
    indices = rng.integers(0, n, size=(bootstrap, n))
    rows = {}
    for lattice in ("hexagonal", "square"):
        for mm in MM_GRID:
            path = RESULTS / "banks" / f"bank_{region}_{lattice}_mm{round(mm * 100):03d}.txt"
            if not path.exists():
                continue
            raw = np.loadtxt(path)
            match = match_against(raw[:, 2:4], point, metric)
            combined = ff * match
            n_trials = naive_trials(len(raw))
            entry = {"minimal_match": mm, "n_templates": int(len(raw)),
                     "outside_validated_range": mm < VALIDATED_FROM,
                     "losses": {
                         "worst_case_1_minus_MM3": 1.0 - mm ** 3,
                         "linear_expansion": 3.0 * (1.0 - mm),
                         "population_taylorf2": 1.0 - float(np.mean(match ** 3)),
                         "population_imrphenomd_approx": 1.0 - float(np.mean(combined ** 3))},
                     "rho_star": {}, "v_eff": {}, "v_eff_error": {}}
            boot_tf2 = np.mean(match[indices] ** 3, axis=1)
            boot_imr = np.mean(combined[indices] ** 3, axis=1)
            for name, (fap, _) in OPERATING_POINTS.items():
                rho = solve_threshold(fap, n_trials)
                entry["rho_star"][name] = rho
                entry["v_eff"][name] = {
                    "taylorf2": float(np.mean(match ** 3)) / rho ** 3,
                    "imrphenomd_approx": float(np.mean(combined ** 3)) / rho ** 3}
                entry["v_eff_error"][name] = {
                    "taylorf2": float(boot_tf2.std(ddof=1)) / rho ** 3,
                    "imrphenomd_approx": float(boot_imr.std(ddof=1)) / rho ** 3}
            rows[f"{lattice}_mm{round(mm * 100):03d}"] = entry
    return rows


def summarise(region, rows):
    print(f"\n=== {region} ===")
    for lattice in ("hexagonal", "square"):
        series = [(v["minimal_match"], v) for k, v in rows.items() if k.startswith(lattice)]
        if not series:
            continue
        series.sort()
        print(f"\n  {lattice}")
        print(f"    {'MM':>5s} {'N':>6s} {'rho*':>7s} {'1-MM^3':>8s} {'1-<M^3>':>9s} "
              f"{'V_eff TF2':>12s} {'+-':>10s} {'V_eff IMR':>12s}  note")
        for mm, v in series:
            op = "far_1_per_100yr"
            ve = v["v_eff"][op]; err = v["v_eff_error"][op]
            flag = "OUTSIDE validated range" if v["outside_validated_range"] else ""
            print(f"    {mm:5.2f} {v['n_templates']:6d} {v['rho_star'][op]:7.4f} "
                  f"{v['losses']['worst_case_1_minus_MM3']:8.5f} "
                  f"{v['losses']['population_taylorf2']:9.5f} "
                  f"{ve['taylorf2']:12.6e} {err['taylorf2']:10.2e} "
                  f"{ve['imrphenomd_approx']:12.6e}  {flag}")
        for leg in ("taylorf2", "imrphenomd_approx"):
            best = max(series, key=lambda s: s[1]["v_eff"]["far_1_per_100yr"][leg])
            mm, v = best
            ve = v["v_eff"]["far_1_per_100yr"][leg]
            err = v["v_eff_error"]["far_1_per_100yr"][leg]
            rivals = [s for s in series
                      if abs(s[1]["v_eff"]["far_1_per_100yr"][leg] - ve) < 2 * err]
            span = f"{min(r[0] for r in rivals):.2f}-{max(r[0] for r in rivals):.2f}"
            note = " (provisional: below the validated range)" if mm < VALIDATED_FROM else ""
            print(f"    -> {leg:18s} max at MM = {mm:.2f}; within 2 sigma: {span}{note}")


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    out = {}
    for region in ("main", "extended"):
        rows = run(region, n)
        if rows:
            out[region] = rows
            summarise(region, rows)
    path = RESULTS / "part_f_optimum.json"
    path.write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
