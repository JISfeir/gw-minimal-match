#!/usr/bin/env python
"""Export the small arrays the shipped figures need, from results/ into data/.

results/ is git-ignored because it is rebuildable; data/ is tracked. Figures must
regenerate from a clean clone, so anything a figure reads lives here, not there.
Rebuild: .venv/bin/python scripts/export_figure_data.py
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "work" / "d1"))
from audit import draw                                              # noqa: E402
from geometry import Boundary, MU_MAX, analytic_metric, clamp_physical, in_region, tau  # noqa: E402

RESULTS = ROOT / "results" / "d1"
DATA = ROOT / "data"
BANKS = ("main_hexagonal", "main_square", "extended_hexagonal", "extended_square")
MM_GRID = (0.95, 0.96, 0.97, 0.98, 0.99)


def covering_arrays(n=3000, seed=20260925):
    """Per-injection best match and border flag, for the cumulative-match figure."""
    out = {}
    for region in ("main", "extended"):
        boundary = Boundary(region, cache_dir=RESULTS)
        rng = np.random.default_rng(seed)
        injections = draw(region, n, rng)
        point = np.asarray([tau(*m) for m in injections])
        metric = np.asarray([analytic_metric(*m) for m in injections])
        border = np.empty(n, dtype=bool)
        for i in range(n):
            edge = boundary.tau - point[i]
            border[i] = np.min(np.einsum("ij,jk,ik->i", edge, metric[i], edge)) <= MU_MAX
        out[f"{region}_masses"] = injections
        out[f"{region}_border"] = border
        for lattice in ("hexagonal", "square"):
            raw = np.loadtxt(RESULTS / "banks" / f"bank_{region}_{lattice}_mm097.txt")
            match = np.empty(n)
            for i in range(n):
                delta = raw[:, 2:4] - point[i]
                match[i] = 1.0 - np.min(np.einsum("ij,jk,ik->i", delta, metric[i], delta))
            out[f"{region}_{lattice}_match"] = match
            print(f"  {region}_{lattice}: {n} injections, worst mu {1 - match.min():.6f}")
    return out


def mismatch_map(region="main", lattice="hexagonal", side=90):
    """A 2-D map over (m1, m2). Figure rule F3: the metric depends on both masses,
    so at least one figure must not collapse them."""
    raw = np.loadtxt(RESULTS / "banks" / f"bank_{region}_{lattice}_mm097.txt")
    lo, hi = (5.0, 31.0) if region == "main" else (5.0, 50.0)
    grid1 = np.linspace(lo, hi, side)
    grid2 = np.linspace(lo, hi, side)
    field = np.full((side, side), np.nan)
    for i, m1 in enumerate(grid1):
        for j, m2 in enumerate(grid2):
            if m2 > m1 or not in_region(m1, m2, region):
                continue
            a, b = clamp_physical(m1, m2)
            point = np.asarray(tau(a, b))
            metric = analytic_metric(a, b)
            delta = raw[:, 2:4] - point
            field[j, i] = np.min(np.einsum("ij,jk,ik->i", delta, metric, delta))
    print(f"  map {region}_{lattice}: {np.isfinite(field).sum()} cells, "
          f"worst mu {np.nanmax(field):.6f}")
    return {"grid_m1": grid1, "grid_m2": grid2, "mismatch": field}


def main():
    DATA.mkdir(exist_ok=True)
    print("covering arrays")
    np.savez_compressed(DATA / "fig_covering.npz", **covering_arrays())
    print("mismatch map")
    np.savez_compressed(DATA / "fig_mismatch_map.npz", **mismatch_map())
    for name in ("part_d_mm097.json", "part_e_mm097.json", "part_f_mm097.json",
                 "part_f_optimum.json"):
        shutil.copy(RESULTS / name, DATA / name)
        print(f"  copied {name}")
    # the two adaptive-hunt witnesses the dverify r03 audit reproduced
    (DATA / "fig_witnesses.json").write_text(json.dumps({
        "main_hexagonal": {"m1": 25.66516036451493, "m2": 5.816990546682748,
                           "mismatch": 0.032220597236526316},
        "extended_hexagonal": {"m1": 38.374673950832516, "m2": 5.606087551134845,
                               "mismatch": 0.03615253316239979},
        "source": "jobs/2026-09-25_112044_derive-dverify r03 verifier, reproduced by hand",
    }, indent=2) + "\n")
    print("wrote data/fig_witnesses.json")


if __name__ == "__main__":
    main()
