"""Part D at the headline point MM = 0.97: counts, ratio, covering.

Covering is reported against BOTH bars, which is the 2026-09-25 re-scope:
  - worst case: does ANY injection fall below the nominal minimal match;
  - percentile: the fraction at or above it, which is how the field states the
    criterion in practice (Sakon et al. 2023 quote fitting factors above 97 % for
    90 % of injections in the O4 bank).
Interior and border are split at one covering radius in local metric distance from
any region boundary, as part D asks.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geometry import (COVERING_RADIUS, MU_MAX, Boundary, analytic_metric,
                      clamp_physical, in_region, tau)

BANKS = Path("/home/juan/gw-minimal-match/results/d1/banks")
CACHE = Path("/home/juan/gw-minimal-match/results/d1")
# Constant-metric ideals from the proper area. CORRECTED 2026-09-26: the first
# values came from a Monte Carlo with no convergence study and were low by 0.89 %
# (main) and 4.77 % (extended). The geomverify r01 audit recomputed them by
# deterministic quadrature, and a third method here -- Gauss-Legendre in (m1, m2)
# rather than their (M, m2) -- agrees to 4-5 digits.
PROPER_AREA = {"main": 35.717393158, "extended": 7.434835530}
_HEX_CELL = 3 * 3 ** 0.5 / 2 * 0.03
_SQUARE_CELL = 2 * 0.03
AREA_IDEAL = {(r, "hexagonal"): round(PROPER_AREA[r] / _HEX_CELL)
              for r in PROPER_AREA} | {
              (r, "square"): round(PROPER_AREA[r] / _SQUARE_CELL) for r in PROPER_AREA}


def draw(region, n, rng):
    out = []
    while len(out) < n:
        block = rng.uniform(5.0, 50.0, size=(4 * n, 2))
        hi = np.maximum(block[:, 0], block[:, 1])
        lo = np.minimum(block[:, 0], block[:, 1])
        for a, b in zip(hi, lo):
            if in_region(a, b, region):
                out.append(clamp_physical(a, b))
                if len(out) == n:
                    break
    return np.asarray(out)


def measure(region, lattice, n, seed, boundary):
    path = BANKS / f"bank_{region}_{lattice}_mm097.txt"
    raw = np.loadtxt(path)
    bank_tau = raw[:, 2:4]
    rng = np.random.default_rng(seed)
    injections = draw(region, n, rng)
    worst = np.empty(n)
    is_border = np.zeros(n, dtype=bool)
    border_boundary_metric = np.zeros(n, dtype=bool)   # the old, mis-specified statistic
    for index, (m1, m2) in enumerate(injections):
        point = np.asarray(tau(m1, m2))
        metric = analytic_metric(m1, m2)
        delta = bank_tau - point
        worst[index] = np.min(np.einsum("ij,jk,ik->i", delta, metric, delta))
        edge = boundary.tau - point
        # The INJECTION's metric, not the boundary samples'.  Part D defines border as
        # within one covering radius "in local metric distance", and template distances
        # above use the injection metric, so the border test must too.  The first version
        # used boundary.metrics -- defensible for the fertility test, where the question
        # is whether a cell reaches the region, but not the statistic declared here.
        # Found by the dverify r03 verifier by source inspection.
        is_border[index] = bool(
            np.min(np.einsum("ij,jk,ik->i", edge, metric, edge)) <= MU_MAX)
        border_boundary_metric[index] = bool(
            np.min(np.einsum("ij,ijk,ik->i", edge, boundary.metrics, edge)) <= MU_MAX)

    def block(mask):
        if mask.sum() == 0:
            return {"n": 0}
        sub = worst[mask]
        below = float(np.mean(sub > MU_MAX))
        return {"n": int(mask.sum()),
                "fraction_below_minimal_match": below,
                "monte_carlo_error": float(np.sqrt(below * (1 - below) / mask.sum())),
                "fraction_at_or_above": 1.0 - below,
                "worst_mismatch": float(sub.max()),
                "median_mismatch": float(np.median(sub)),
                "match_at_90th_percentile": float(1.0 - np.percentile(sub, 90)),
                "match_at_99th_percentile": float(1.0 - np.percentile(sub, 99))}

    return {"region": region, "lattice": lattice, "n_templates": int(len(raw)),
            "composition": {"lattice": int((raw[:, 5] == 0).sum()),
                            "pushed_back": int((raw[:, 5] == 1).sum()),
                            "boundary_repair": int((raw[:, 5] == 2).sum())},
            "constant_metric_ideal": AREA_IDEAL[(region, lattice)],
            "over_density_vs_ideal": len(raw) / AREA_IDEAL[(region, lattice)],
            "seed": seed, "n_injections": n,
            "all": block(np.ones(n, dtype=bool)),
            "border_fraction_injection_metric": float(is_border.mean()),
            "border_fraction_boundary_metric": float(border_boundary_metric.mean()),
            "interior": block(~is_border), "border": block(is_border)}


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20260925
    results = {}
    for region in ("main", "extended"):
        boundary = Boundary(region, cache_dir=CACHE)
        for lattice in ("hexagonal", "square"):
            key = f"{region}_{lattice}"
            results[key] = measure(region, lattice, n, seed, boundary)
            r = results[key]
            print(f"{key:22s} N={r['n_templates']:5d} "
                  f"(lat {r['composition']['lattice']}, push {r['composition']['pushed_back']}, "
                  f"rep {r['composition']['boundary_repair']})  "
                  f"ideal {r['constant_metric_ideal']}, x{r['over_density_vs_ideal']:.2f}")
            for name in ("all", "interior", "border"):
                b = r[name]
                if b.get("n"):
                    print(f"    {name:9s} n={b['n']:5d}  at/above MM = {b['fraction_at_or_above']*100:7.3f} %"
                          f"   worst mu = {b['worst_mismatch']:.6f}"
                          f"   match@90th = {b['match_at_90th_percentile']:.5f}")
    print()
    print("D-2  hexagonal / square template-count ratio")
    print("     references: 0.7698 ideal constant metric; 0.717-0.719 Cokelaer 2007 measured")
    for region in ("main", "extended"):
        h = results[f"{region}_hexagonal"]["n_templates"]
        s = results[f"{region}_square"]["n_templates"]
        results[f"ratio_{region}"] = h / s
        print(f"     {region:9s} {h:5d} / {s:5d} = {h/s:.4f}")
    out = CACHE / "part_d_mm097.json"
    out.write_text(json.dumps(results, indent=2, default=float) + "\n")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
