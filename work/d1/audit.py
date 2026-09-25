"""Covering audit of a D-1 bank: the test that judges the placement.

Injections are drawn uniformly in (m1, m2) over the region -- a declared choice, not
the astrophysical population -- and each injection's mismatch to the bank is the
quadratic form evaluated with THE INJECTION'S OWN metric, which is what a covering
claim means and what the retention rule now uses too.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geometry import (COVERING_RADIUS, MU_MAX, analytic_metric, clamp_physical,
                      in_region, tau)


def draw(region, n, rng):
    out = []
    while len(out) < n:
        block = rng.uniform(5.0, 50.0, size=(4 * n, 2))
        m1 = np.maximum(block[:, 0], block[:, 1])
        m2 = np.minimum(block[:, 0], block[:, 1])
        for a, b in zip(m1, m2):
            if in_region(a, b, region):
                out.append(clamp_physical(a, b))
                if len(out) == n:
                    break
    return np.asarray(out)


def audit(bank_tau, region, n=2000, seed=20260923, boundary=None):
    rng = np.random.default_rng(seed)
    injections = draw(region, n, rng)
    bank_tau = np.asarray(bank_tau, dtype=float).reshape(-1, 2)
    worst = np.empty(n)
    border = np.zeros(n, dtype=bool)
    for index, (m1, m2) in enumerate(injections):
        point = np.asarray(tau(m1, m2))
        metric = analytic_metric(m1, m2)
        delta = bank_tau - point
        worst[index] = np.min(np.einsum("ij,jk,ik->i", delta, metric, delta))
        if boundary is not None:
            edge = boundary.tau - point
            border[index] = bool(np.min(np.einsum("ij,ijk,ik->i", edge, boundary.metrics, edge))
                                 <= MU_MAX)
    def split(mask):
        if mask.sum() == 0:
            return {"n": 0}
        sub = worst[mask]
        frac = float(np.mean(sub > MU_MAX))
        return {"n": int(mask.sum()), "fraction_below_target": frac,
                "monte_carlo_error": float(np.sqrt(frac * (1 - frac) / mask.sum())),
                "worst_mismatch": float(sub.max()),
                "median_mismatch": float(np.median(sub))}
    frac = float(np.mean(worst > MU_MAX))
    return {"region": region, "n_injections": n, "seed": seed,
            "n_templates": int(len(bank_tau)),
            "fraction_below_target": frac,
            "monte_carlo_error": float(np.sqrt(frac * (1 - frac) / n)),
            "worst_mismatch": float(worst.max()),
            "interior": split(~border), "border": split(border),
            "injections": injections, "worst": worst, "is_border": border}


def load_bank(path):
    array = np.loadtxt(path)
    return array[:, 2:4], array


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("bank")
    parser.add_argument("--region", required=True)
    parser.add_argument("--n", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260923)
    parser.add_argument("--holes", type=int, default=0)
    args = parser.parse_args()
    bank_tau, raw = load_bank(args.bank)
    result = audit(bank_tau, args.region, args.n, args.seed)
    printable = {k: v for k, v in result.items()
                 if k not in ("injections", "worst", "is_border")}
    print(json.dumps(printable, indent=2))
    if args.holes:
        bad = result["injections"][result["worst"] > MU_MAX]
        order = np.argsort(-result["worst"][result["worst"] > MU_MAX])
        print("\nworst holes (m1, m2, eta, mu):")
        for index in order[:args.holes]:
            m1, m2 = bad[index]
            eta = m1 * m2 / (m1 + m2) ** 2
            mu = result["worst"][result["worst"] > MU_MAX][index]
            print(f"  ({m1:7.3f}, {m2:7.3f})  M={m1+m2:7.3f}  eta={eta:.5f}  mu={mu:.5f}")
