#!/usr/bin/env python3
"""Compute the region geometry and SHIP IT, so the registry cites data rather than
literals.

A blind review found that seven of the registry's numbers -- the proper areas,
perimeters, effective widths and the cusp coefficient -- were hard-coded in
compute_numbers.py with no file behind them, which makes the paper's claim that
regenerating one file reproduces every value a transcription rather than a computation.
It also found that proper_perimeter_extended was never shipped at all, so the extended
effective width could not be checked by anyone.

Areas and perimeters by deterministic Gauss-Legendre quadrature, at two orders so the
convergence is visible in the output rather than asserted. The cusp coefficient is the
secant angle between the two region edges at (5,5), fitted at decreasing separation.

Run:  .venv/bin/python scripts/compute_geometry.py     (~8 minutes)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "work" / "d1"))
from geometry import (COVERING_RADIUS, REGION_VERTICES, analytic_metric,  # noqa: E402
                      clamp_physical, in_region, tau)

OUT = ROOT / "data" / "region_geometry.json"
H = 1e-5


def density(m1, m2):
    """sqrt(det g) times |det d(tau)/d(m)| -- the proper area element in mass space."""
    a, b = clamp_physical(m1, m2)
    g = analytic_metric(a, b)
    jac = np.column_stack([
        (np.asarray(tau(a + H, b)) - np.asarray(tau(a - H, b))) / (2 * H),
        (np.asarray(tau(a, b + H)) - np.asarray(tau(a, b - H))) / (2 * H)])
    return float(np.sqrt(np.linalg.det(g)) * abs(np.linalg.det(jac)))


def area(region, order):
    x, w = np.polynomial.legendre.leggauss(order)
    lo, hi = (5.0, 30.0) if region == "main" else (5.0, 50.0)
    m1 = 0.5 * (hi - lo) * x + 0.5 * (hi + lo)
    w1 = 0.5 * (hi - lo) * w
    total = 0.0
    for a, wa in zip(m1, w1):
        if region == "main":
            b_lo, b_hi = 5.0, min(a, 35.0 - a)
        else:
            b_lo, b_hi = max(5.0, 35.0 - a), min(a, 100.0 - a)
        if b_hi <= b_lo:
            continue
        m2 = 0.5 * (b_hi - b_lo) * x + 0.5 * (b_hi + b_lo)
        w2 = 0.5 * (b_hi - b_lo) * w
        for b, wb in zip(m2, w2):
            if in_region(a, b, region):
                total += wa * wb * density(a, b)
    return total


def edge_length(start, stop, segments):
    """Proper length of a straight mass-space edge, midpoint rule."""
    points = [clamp_physical(*(np.asarray(start) + f * (np.asarray(stop) - np.asarray(start))))
              for f in np.linspace(0.0, 1.0, segments + 1)]
    taus = np.asarray([tau(*p) for p in points])
    total = 0.0
    for k in range(segments):
        middle = clamp_physical(*(0.5 * (np.asarray(points[k]) + np.asarray(points[k + 1]))))
        step = taus[k + 1] - taus[k]
        total += float(np.sqrt(step @ analytic_metric(*middle) @ step))
    return total


def perimeter(region, segments):
    vertices = REGION_VERTICES[region]
    edges = [edge_length(vertices[i], vertices[(i + 1) % len(vertices)], segments)
             for i in range(len(vertices))]
    return sum(edges), edges


def cusp_secant(separations=(1.0, 0.2, 0.05, 0.01, 1e-3, 1e-4)):
    """Angle between the two edges leaving (5,5), in the local metric, against
    separation. The limit is analytically zero -- the two mass rays have positively
    parallel tangents -- so what is measurable is the leading coefficient."""
    corner = clamp_physical(5.0, 5.0)
    base = np.asarray(tau(*corner))
    metric = analytic_metric(*corner)
    chol = np.linalg.cholesky(metric)
    rows = []
    for eps in separations:
        def direction(point):
            delta = np.asarray(tau(*clamp_physical(*point))) - base
            whitened = chol.T @ delta
            return whitened / np.linalg.norm(whitened)
        along_m2 = direction((5.0 + eps, 5.0))            # the m2 = 5 edge
        along_eq = direction((5.0 + eps, 5.0 + eps))      # the eta = 1/4 edge
        angle = np.degrees(np.arccos(np.clip(along_m2 @ along_eq, -1.0, 1.0)))
        rows.append({"separation_msun": eps, "angle_degrees": float(angle),
                     "angle_over_separation": float(angle / eps)})
    return rows


def main():
    out = {"covering_radius": COVERING_RADIUS,
           "note": "areas and perimeters at two orders each, so convergence is visible "
                   "rather than asserted; the cusp limit is analytic (exactly zero) and "
                   "only its leading secant coefficient is measured here"}
    for region in ("main", "extended"):
        coarse, fine = area(region, 60), area(region, 120)
        peri_c, _ = perimeter(region, 300)
        peri_f, edges = perimeter(region, 600)
        width = 2 * fine / peri_f
        out[region] = {
            "proper_area": fine, "proper_area_coarser_order": coarse,
            "proper_area_order_change": abs(fine - coarse),
            "proper_perimeter": peri_f, "proper_perimeter_coarser": peri_c,
            "proper_perimeter_change": abs(peri_f - peri_c),
            "edge_proper_lengths": edges,
            "effective_width": width,
            "effective_width_in_covering_radii": width / COVERING_RADIUS,
            "disc_perimeter_same_area": float(2 * np.sqrt(np.pi * fine)),
        }
        print(f"{region:9s} area {fine:.6f} (order 60: {coarse:.6f})  "
              f"perimeter {peri_f:.6f}  width {width / COVERING_RADIUS:.6f} R")
    out["cusp_secant_angles"] = cusp_secant()
    out["cusp_secant_coefficient"] = out["cusp_secant_angles"][-1]["angle_over_separation"]
    print(f"cusp leading coefficient {out['cusp_secant_coefficient']:.9f} deg/Msun")
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
