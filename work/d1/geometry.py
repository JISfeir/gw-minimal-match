"""Region geometry and the q1bC metric, shared by the D-1 rebuild.

Everything here is chirp-time (tau0, tau3) at f0 = 20 Hz.  The metric, the chirp-time
map and the inverse mass map are imported from q1bC's frozen out/lib and are not
rebuilt; see wiki/log.md 2026-09-23.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np

Q1BC = Path("/home/juan/gw-minimal-match/jobs/2026-09-14_041516_derive-q1bc/out")
if str(Q1BC) not in sys.path:
    sys.path.insert(0, str(Q1BC))
from lib.metric import analytic_metric, masses, tau, total_eta  # noqa: E402

# The minimal match is a DESIGN CONVENTION, not a derived constant: Owen 1996 sets 0.97
# as a fiducial "chosen by the experimenter", corresponding to 1 - 0.97^3 = 8.7 % of the
# ideal event rate.  Part F needs curves over MM, so it is settable; every cache file is
# keyed by the resulting spacing, so different values never collide.
MM = float(os.environ.get("GWMM_MINIMAL_MATCH", "0.97"))
MU_MAX = 1.0 - MM                      # 0.03, the covering radius squared
COVERING_RADIUS = float(np.sqrt(MU_MAX))
MLO, MHI, MSPLIT = 5.0, 50.0, 35.0
ETA_MAX = 0.25

# Every edge below is a straight line in (m1, m2), so linear interpolation in mass
# space is exact and the curvature lives entirely in the map to chirp time.
REGION_VERTICES = {
    "main": ((5.0, 5.0), (30.0, 5.0), (17.5, 17.5)),
    "extended": ((30.0, 5.0), (50.0, 5.0), (50.0, 50.0), (17.5, 17.5)),
    "pilot": ((5.0, 5.0), (10.0, 5.0), (7.5, 7.5)),
}
SEED_MASSES = {"pilot": (5.0, 5.0), "main": (5.0, 5.0), "extended": (30.0, 5.0)}
# Total mass along the eta = 1/4 edge of each region.
EQUAL_MASS_RANGE = {"pilot": (10.0, 15.0), "main": (10.0, 35.0), "extended": (35.0, 100.0)}

LATTICE_OFFSETS = {
    "hexagonal": lambda r: (np.sqrt(3.0) * r) * np.column_stack(
        (np.cos(np.arange(6) * np.pi / 3.0), np.sin(np.arange(6) * np.pi / 3.0))),
    # Owen 1996 Eq. 3.16: dx_j = sqrt(2 (1 - MM) / E_j); in eigen-normalised
    # coordinates E_j = 1, so the step is sqrt(2) R and the cell centre -- its worst
    # point -- sits at mismatch exactly 1 - MM.
    "square": lambda r: (np.sqrt(2.0) * r) * np.array(
        ((1.0, 0.0), (-1.0, 0.0), (0.0, 1.0), (0.0, -1.0))),
}


def in_region(m1: float, m2: float, region: str) -> bool:
    eps = 2e-10
    if region == "pilot":
        return MLO - eps <= m2 <= m1 + eps <= 10.0 + eps and m1 + m2 <= 15.0 + eps
    if not (MLO - eps <= m2 <= m1 + eps and m1 <= MHI + eps):
        return False
    total = m1 + m2
    if region == "main":
        return total <= MSPLIT + eps
    return MSPLIT - eps <= total <= 100.0 + eps


_ETA_SCALE = None


def eta_of_tau(point) -> float:
    """eta from chirp times.  Exact: tau0 ~ M^-5/3 eta^-1, tau3 ~ M^-2/3 eta^-1, so
    tau0^(2/3) tau3^(-5/3) is proportional to eta with no mass dependence left."""
    global _ETA_SCALE
    if _ETA_SCALE is None:
        reference = tau(12.5, 6.25)
        _ETA_SCALE = total_eta(reference)[1] / (
            reference[0] ** (2.0 / 3.0) * reference[1] ** (-5.0 / 3.0))
    return float(_ETA_SCALE * point[0] ** (2.0 / 3.0) * point[1] ** (-5.0 / 3.0))


def clamp_physical(m1: float, m2: float):
    """Nudge m2 down by the few ulps that put eta back at or below 1/4.

    On the equal-mass edge m1 == m2 exactly, yet m1*m2/(m1+m2)**2 can round to
    0.25000000000000006 -- at m = 22.13125 it does -- and q1bC's frozen metric
    rejects that with "invalid phase input".  Float hygiene only: the correction is
    ~1e-15 Msun and never moves a mass by anything measurable.
    """
    m1 = float(m1); m2 = float(m2)
    for _ in range(8):
        if m1 * m2 / (m1 + m2) ** 2 <= ETA_MAX:
            return m1, m2
        m2 = float(np.nextafter(m2, 0.0))
    raise ValueError(f"cannot clamp ({m1}, {m2}) to eta <= 1/4")


def masses_of_tau(point):
    if np.any(np.asarray(point) <= 0.0):
        return None
    if not (0.0 < eta_of_tau(point) <= ETA_MAX + 2e-13):
        return None
    try:
        result = np.asarray(masses(point), dtype=float)
    except ValueError:
        return None
    return result if np.all(np.isfinite(result)) else None


def canonical_eigensystem(metric, orientation_reference=None):
    """Ascending eigenvalues and a deterministic right-handed eigenbasis."""
    values, vectors = np.linalg.eigh(metric)
    if values[0] <= 0.0:
        raise ValueError("metric is not positive definite")
    first = vectors[:, 0].copy()
    if orientation_reference is None:
        flip = first[int(np.argmax(np.abs(first)))] < 0.0
    else:
        flip = np.dot(first, np.asarray(orientation_reference)[:, 0]) < 0.0
    if flip:
        first = -first
    return values, np.column_stack((first, np.array([-first[1], first[0]])))


class Boundary:
    """Boundary points of a region WITH the metric evaluated at each of them.

    The fertility test uses the metric here, not the metric at the candidate cell.
    That is the 2026-09-23 amendment: a cell far outside the region carries a
    degenerate metric (condition number 1.8e6 where TaylorF2 keeps 12 in-band bins),
    whose mu = 0.03 ellipse has a 4.6e4 s semi-axis, so every such cell tested as
    fertile.  The boundary metric is well conditioned, and it is also the metric the
    covering Monte Carlo uses, so retention and the test that judges it now measure
    the same thing.
    """

    def __init__(self, region: str, target_spacing: float = None, cache_dir=None,
                 coarse_per_edge: int = 400):
        """Sample each edge uniformly in PROPER length, not in mass.

        Sampling 400 points per edge -- what the first rebuild did -- leaves gaps of
        up to 1.6457 in proper distance on the main region's long edges, against a
        covering radius of 0.1732: 30.6 % of gaps wider than R and 18 % wider than 2R.
        The fertility test and the interior/border split both read this boundary, so
        both were blind to whole stretches of it.  Here the edges are re-sampled at a
        fixed proper spacing (default R/4), which costs metric calls but makes
        "within one covering radius of the region" mean what it says.
        """
        self.region = region
        if target_spacing is None:
            target_spacing = COVERING_RADIUS / 4.0
        self.target_spacing = target_spacing
        cache = None
        if cache_dir is not None:
            cache = Path(cache_dir) / f"boundary_{region}_ps{target_spacing:.5f}.npz"
        if cache is not None and cache.exists():
            blob = np.load(cache)
            self.masses, self.tau, self.metrics = blob["masses"], blob["tau"], blob["metrics"]
            self.samples_per_edge = None
            return
        vertices = REGION_VERTICES[region]
        mass_points = []
        for index, start in enumerate(vertices):
            start = np.asarray(start)
            stop = np.asarray(vertices[(index + 1) % len(vertices)])
            # pass 1: coarse walk to measure the edge's proper length
            coarse = [clamp_physical(*(start + f * (stop - start)))
                      for f in np.linspace(0.0, 1.0, coarse_per_edge + 1)]
            coarse_tau = np.asarray([tau(*m) for m in coarse])
            cumulative = [0.0]
            for k in range(coarse_per_edge):
                middle = clamp_physical(*(0.5 * (np.asarray(coarse[k]) + np.asarray(coarse[k + 1]))))
                metric = analytic_metric(*middle)
                step = coarse_tau[k + 1] - coarse_tau[k]
                cumulative.append(cumulative[-1] + float(np.sqrt(step @ metric @ step)))
            cumulative = np.asarray(cumulative)
            length = cumulative[-1]
            # pass 2: resample uniformly in proper length
            count = max(int(np.ceil(length / target_spacing)), 2)
            wanted = np.linspace(0.0, length, count, endpoint=False)
            fractions = np.interp(wanted, cumulative, np.linspace(0.0, 1.0, coarse_per_edge + 1))
            for f in fractions:
                mass_points.append(clamp_physical(*(start + f * (stop - start))))
        self.masses = np.asarray(mass_points)
        self.tau = np.asarray([tau(*m) for m in self.masses])
        self.metrics = np.asarray([analytic_metric(*m) for m in self.masses])
        self.samples_per_edge = None
        if cache is not None:
            cache.parent.mkdir(parents=True, exist_ok=True)
            np.savez(cache, masses=self.masses, tau=self.tau, metrics=self.metrics)

    def min_mismatch_to_region(self, point) -> float:
        """min over boundary samples of d^T g_boundary d -- the quadratic mismatch
        between `point` and the nearest point of the region, judged where the region
        is, not where the point is."""
        delta = self.tau - np.asarray(point)
        return float(np.min(np.einsum("ij,ijk,ik->i", delta, self.metrics, delta)))
