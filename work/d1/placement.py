"""D-1 rebuild: local-metric bank placement at MM = 0.97.

Rewritten 2026-09-23 after job qDEF's r06 verifier refuted the delivered banks and
the refutations were reproduced independently (wiki/log.md 2026-09-23).  Two rules
change from the pre-registered spec; both are dated amendments, not silent fixes.

AMENDMENT 1 -- eta = 1/4.  The spec projected non-physical daughters onto the line
DURING growth and let them breed from there.  Measured consequence in the delivered
banks: the projected templates collapse onto a 1-D curve and nothing re-spaces them.
Proper distance between neighbours along the line was 0.680 (hexagonal) and 1.139
(square) against a covering radius R = 0.1732: 3.93x and 6.58x R, i.e. 1.96x and 3.29x
the diameter 2R = 0.3464.  179/208 resp. 109/110 consecutive gaps exceeded 2R.
(The ratios were mislabelled as multiples of the diameter until the d1verify r01
verifier caught the arithmetic on 2026-09-23.)  Cokelaer 2007 p. 6 pushes back
as an OPTIONAL FINAL STEP, "once the reproduction is over".  Here: grow without
projecting, push back at the end, then repair the boundary strip greedily.

AMENDMENT 2 -- fertility.  The spec asked whether a cell's own covering ellipse
reaches the region, using the metric AT THE CELL.  Where TaylorF2 loses support that
metric goes degenerate and the test becomes void; see geometry.Boundary.  The
distance is now evaluated with the metric at the region boundary point.

Still a stand-in, and said so plainly: `reconnect_to_existing` is a proximity
threshold at `collision_fraction` of the local spacing, NOT Cokelaer's explicit
mother/daughter/adjacent-daughter connectors.  The realized spacing it produces is
measured and reported rather than assumed.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

from geometry import (COVERING_RADIUS, EQUAL_MASS_RANGE, ETA_MAX, LATTICE_OFFSETS, MM,
                      MU_MAX, REGION_VERTICES, Boundary, analytic_metric,
                      canonical_eigensystem, clamp_physical, eta_of_tau, in_region,
                      masses_of_tau, tau)

CACHE = Path("/home/juan/gw-minimal-match/results/d1")


def push_back_to_equal_mass(point, eigenvectors):
    """Cokelaer's final step: move a non-physical cell onto eta = 1/4 along the
    shortest of the four local eigenvector rays.  Returns (step, point, axis, sign)."""
    candidates = []
    for axis in range(2):
        for sign in (-1.0, 1.0):
            direction = sign * eigenvectors[:, axis]
            residual = lambda step: eta_of_tau(point + step * direction) - ETA_MAX
            upper = 1e-5
            for _ in range(80):
                trial = point + upper * direction
                if np.any(trial <= 0.0):
                    break
                if residual(upper) <= 0.0:
                    try:
                        root = brentq(residual, 0.0, upper, xtol=1e-14, rtol=1e-13)
                    except ValueError:
                        break
                    candidates.append((root, point + root * direction, axis, int(sign)))
                    break
                upper *= 1.4
    return min(candidates, key=lambda item: item[0]) if candidates else None


def grow(region, lattice, boundary, collision_fraction=0.5, max_cells=200_000,
         verbose=True, seed_masses=None):
    """Grow the lattice cell by cell, each cell stepping with the metric at its own
    position.  Cells on the non-physical side of eta = 1/4 are created as lattice
    nodes (inheriting the mother's metric, since q1bC's metric is undefined there)
    and are never delivered directly -- they exist so the lattice stays regular up to
    the boundary, and they are pushed back afterwards."""
    offsets_proper = LATTICE_OFFSETS[lattice](COVERING_RADIUS)
    spacing = float(np.linalg.norm(offsets_proper[0]))
    cells, n_metric_calls = [], 0
    tau_buffer = np.empty((1024, 2))

    def make_cell(point, generation, mother=None):
        nonlocal n_metric_calls
        if np.any(np.asarray(point) <= 0.0):
            return None
        eta = eta_of_tau(point)
        physical = eta <= ETA_MAX + 2e-13
        if physical:
            mass = masses_of_tau(point)
            if mass is None:
                return None
            try:
                metric = analytic_metric(*clamp_physical(*mass))
            except (RuntimeError, ValueError):
                return None
            n_metric_calls += 1
            reference = None if mother is None else mother["eigenvectors"]
            values, vectors = canonical_eigensystem(metric, reference)
            inside = in_region(*mass, region)
            inherited = False
        else:
            if mother is None:
                return None
            mass, metric = None, mother["metric"]
            values, vectors = mother["eigenvalues"], mother["eigenvectors"]
            inside, inherited = False, True
        mu_to_region = 0.0 if inside else boundary.min_mismatch_to_region(point)
        return {"id": len(cells), "tau": np.asarray(point, dtype=float), "masses": mass,
                "metric": metric, "eigenvalues": values, "eigenvectors": vectors,
                "physical": physical, "inside_region": inside,
                "metric_inherited": inherited, "generation": generation,
                "fertile": bool(mu_to_region <= MU_MAX), "mu_to_region": mu_to_region}

    def collides(point, metric):
        if not cells:
            return False
        delta = tau_buffer[:len(cells)] - point
        return bool(np.min(np.einsum("ij,jk,ik->i", delta, metric, delta))
                    < (collision_fraction * spacing) ** 2)

    def append(cell):
        nonlocal tau_buffer
        if len(cells) >= len(tau_buffer):
            tau_buffer = np.vstack([tau_buffer, np.empty_like(tau_buffer)])
        tau_buffer[len(cells)] = cell["tau"]
        cells.append(cell)

    # Seed at the centroid of the region's mass-space vertices, NOT at a corner.
    # The old spec seeded (5, 5) and (30, 5); (5, 5) is the extreme-tau0 corner and
    # sits ON eta = 1/4, so every inward hexagonal step crosses the line.  That bank
    # could only grow because it projected during growth -- the very rule amendment 1
    # removes.  With an interior seed the lattice grows outward in all directions and
    # stops one step past the boundary.  Seed choice is a convention; SEED_SENSITIVITY
    # in audit.py measures what it is worth.
    seed_tau = tau(*clamp_physical(*(seed_masses if seed_masses is not None
                                     else np.mean(REGION_VERTICES[region], axis=0))))
    seed = make_cell(seed_tau, 0)
    if seed is None or not seed["fertile"]:
        raise RuntimeError("invalid seed cell")
    append(seed)
    frontier, generation, started = [0], 0, time.monotonic()

    while frontier:
        generation += 1
        next_frontier = []
        for cell_id in frontier:
            mother = cells[cell_id]
            if not mother["fertile"]:
                continue
            steps = mother["eigenvectors"] @ (
                offsets_proper / np.sqrt(mother["eigenvalues"])).T
            for direction in range(len(offsets_proper)):
                point = mother["tau"] + steps[:, direction]
                if collides(point, mother["metric"]):
                    continue
                child = make_cell(point, generation, mother)
                if child is None:
                    continue
                append(child)
                if child["fertile"]:
                    next_frontier.append(child["id"])
                if len(cells) >= max_cells:
                    raise RuntimeError(f"placement exceeded max_cells={max_cells}")
        frontier = next_frontier
        if verbose and generation % 20 == 0:
            print(f"  generation={generation} cells={len(cells)} "
                  f"elapsed={time.monotonic() - started:.1f}s", flush=True)
    return {"cells": cells, "spacing": spacing, "n_metric_calls": n_metric_calls,
            "n_generations": generation, "growth_seconds": time.monotonic() - started}


# The strip grid is specified by a PROPER spacing, not by a count.  The first version
# used 400 points uniform in total mass, which on the equal-mass edge -- proper length
# 129.2, metric largest at low mass -- left adjacent samples up to 1.6556 apart, 9.6x
# the covering radius.  That is precisely the gap the r01 verifier found holes in.
STRIP_SPACING = COVERING_RADIUS / 3.0


def boundary_strip(region, spacing=STRIP_SPACING, cache_dir=CACHE, coarse=2000):
    """Sample the physical strip within one covering radius of EVERY region boundary.

    Generalised 2026-09-24.  The previous version repaired only the eta = 1/4 strip; the
    d1verify r03 verifier then found the residual holes had simply MOVED to the m2 = 5
    edge -- worst mu 0.033124 at (28.28, 5), 89/1681 under an adaptive search, at
    1.35 R to 3.59 R from the equal-mass curve.  The main region's edges have proper
    lengths 114.6, 11.9 and 129.2, so the m2 = 5 edge was always going to need the same
    treatment as eta = 1/4.

    Each edge is resampled uniformly in PROPER LENGTH, and at each edge point the strip
    runs inward (toward the region's mass-space centroid) to the depth at which the
    proper distance from the edge reaches one covering radius, found by bisection.  The
    grid stays rectangular per edge with a validity mask, so `strip_fill_distance` can
    measure its cells.
    """
    cache = Path(cache_dir) / f"bstrip_{region}_sp{spacing:.5f}.npz"
    n_depth = int(np.ceil(COVERING_RADIUS / spacing)) + 1
    if cache.exists():
        blob = np.load(cache)
        count = int(blob["n_edges"])
        return [{key: blob[f"e{i}_{key}"] for key in ("masses", "tau", "metrics", "valid")}
                for i in range(count)]

    vertices = np.asarray(REGION_VERTICES[region], dtype=float)
    centroid = vertices.mean(axis=0)
    edges = []
    for index in range(len(vertices)):
        start_mass = vertices[index]
        stop_mass = vertices[(index + 1) % len(vertices)]

        # pass 1: coarse walk to measure the edge's proper length
        fractions = np.linspace(0.0, 1.0, coarse + 1)
        points = [clamp_physical(*(start_mass + f * (stop_mass - start_mass))) for f in fractions]
        point_tau = np.asarray([tau(*m) for m in points])
        cumulative = [0.0]
        for k in range(coarse):
            middle = clamp_physical(*(0.5 * (np.asarray(points[k]) + np.asarray(points[k + 1]))))
            step = point_tau[k + 1] - point_tau[k]
            cumulative.append(cumulative[-1]
                              + float(np.sqrt(step @ analytic_metric(*middle) @ step)))
        cumulative = np.asarray(cumulative)

        # pass 2: resample uniformly in proper length
        count = max(int(np.ceil(cumulative[-1] / spacing)) + 1, 2)
        chosen = np.interp(np.linspace(0.0, cumulative[-1], count), cumulative, fractions)

        shape = (count, n_depth)
        masses = np.zeros(shape + (2,))
        tau_grid = np.zeros(shape + (2,))
        metrics = np.zeros(shape + (2, 2))
        valid = np.zeros(shape, dtype=bool)
        for i, f in enumerate(chosen):
            base = clamp_physical(*(start_mass + f * (stop_mass - start_mass)))
            if not in_region(*base, region):
                continue
            base_tau = np.asarray(tau(*base))
            try:
                base_metric = analytic_metric(*base)
            except (RuntimeError, ValueError):
                continue
            inward = centroid - np.asarray(base)
            norm = float(np.linalg.norm(inward))
            if norm == 0.0:
                continue
            inward = inward / norm

            # Walk inward accumulating proper length with the LOCAL metric at each
            # step.  Measuring the depth with the metric at the EDGE point instead --
            # the previous two attempts -- is wrong by a large factor: at the equal-mass
            # edge near (13.1, 13.1) the base metric called a step R/3, and the local
            # metric at that depth measured 0.2865, five times more.  The strip is
            # "within one covering radius of the edge" only if the radius is measured
            # where the points are.
            walk_depth = [0.0]
            walk_mass = [np.asarray(base, dtype=float)]
            position, position_tau, position_metric = np.asarray(base, dtype=float), base_tau, base_metric
            travelled, reach, guess = 0.0, 0.0, norm * 1e-3
            while travelled < COVERING_RADIUS and reach < norm:
                trial_reach = min(reach + guess, norm)
                trial = np.asarray(clamp_physical(*(np.asarray(base) + trial_reach * inward)))
                offset = np.asarray(tau(*trial)) - position_tau
                length = float(np.sqrt(offset @ position_metric @ offset))
                if length > 0.6 * spacing and guess > norm * 1e-9:
                    guess *= 0.5
                    continue
                if length < 0.3 * spacing and trial_reach < norm:
                    guess *= 1.6
                    continue
                try:
                    position_metric = analytic_metric(*trial)
                except (RuntimeError, ValueError):
                    break
                travelled += length
                reach, position, position_tau = trial_reach, trial, np.asarray(tau(*trial))
                walk_depth.append(travelled)
                walk_mass.append(position)
            if len(walk_depth) < 2:
                continue
            walk_depth = np.asarray(walk_depth)
            walk_mass = np.asarray(walk_mass)
            wanted = np.linspace(0.0, min(COVERING_RADIUS, walk_depth[-1]), n_depth)
            sampled = np.column_stack([np.interp(wanted, walk_depth, walk_mass[:, k])
                                       for k in range(2)])

            for j, sample_mass in enumerate(sampled):
                sample = clamp_physical(*sample_mass)
                if not in_region(*sample, region):
                    continue
                try:
                    metrics[i, j] = base_metric if j == 0 else analytic_metric(*sample)
                except (RuntimeError, ValueError):
                    continue
                masses[i, j] = sample
                tau_grid[i, j] = tau(*sample)
                valid[i, j] = True
        edges.append({"masses": masses, "tau": tau_grid, "metrics": metrics, "valid": valid})

    cache.parent.mkdir(parents=True, exist_ok=True)
    blob = {"n_edges": len(edges)}
    for i, edge in enumerate(edges):
        for key, value in edge.items():
            blob[f"e{i}_{key}"] = value
    np.savez(cache, **blob)
    return edges


def strip_fill_distance(edges):
    """Largest distance from any point of a grid cell to its nearest corner.

    THIS IS THE 2026-09-24 CORRECTION.  The previous version measured the largest
    ADJACENT AXIAL step delta and asserted every point was within delta/2 of a sample.
    The d1verify r03 verifier refuted that with elementary geometry: the far point of a
    square cell is its centre, at delta/sqrt(2) from every corner, not delta/2.  Its
    counterexample -- delta = 0.09687, every corner covered to mu = 0.015568, centre at
    mu = 0.037352 > 0.03 -- reproduces here to twelve digits.

    For a parallelogram cell the worst point is the centre, at half the longer diagonal
    from the nearest corner, so that is what is measured; each diagonal is evaluated in
    every corner's metric and the largest taken.  A cell with only one valid edge
    contributes half that edge.
    """
    worst = 0.0
    for edge in edges:
        tau_grid, metrics, valid = edge["tau"], edge["metrics"], edge["valid"]
        rows, columns = valid.shape
        for i in range(rows - 1):
            for j in range(columns - 1):
                corners = [(i, j), (i + 1, j), (i, j + 1), (i + 1, j + 1)]
                present = [c for c in corners if valid[c]]
                if len(present) < 2:
                    continue
                if len(present) == 4:
                    pairs = [(corners[0], corners[3]), (corners[1], corners[2])]
                else:
                    pairs = [(a, b) for k, a in enumerate(present) for b in present[k + 1:]]
                for a, b in pairs:
                    step = tau_grid[b] - tau_grid[a]
                    for c in present:
                        worst = max(worst, 0.5 * float(np.sqrt(step @ metrics[c] @ step)))
    return worst


def worst_mismatch(bank_tau, sample_tau, sample_metrics):
    """min over the bank of d^T g_sample d, per sample.  The metric is the SAMPLE's,
    which is what the covering Monte Carlo uses and what a covering claim means."""
    out = np.empty(len(sample_tau))
    for index, (point, metric) in enumerate(zip(sample_tau, sample_metrics)):
        delta = bank_tau - point
        out[index] = np.min(np.einsum("ij,jk,ik->i", delta, metric, delta))
    return out


def repair_boundary(bank_tau, bank_masses, region, max_added=20000):
    """Greedy covering repair of the declared strip along EVERY region boundary.

    Cokelaer's push-back collapses a 2-D neighbourhood of eta = 1/4 onto a 1-D curve and
    nothing in his method re-spaces it; that collapse is what the delivered qDEF banks
    died of.  This step repairs it: the still-uncovered strip sample with the largest
    quadratic mismatch receives a template AT ITS OWN POSITION, and the sweep repeats.

    The threshold is tightened to mu_target = (R - fill)^2, where `fill` is the measured
    worst distance from a point of a grid cell to its nearest corner.  Covering every
    sample to radius R - fill then puts the whole cell within R.  Two corrections are
    baked in, both forced by the d1verify audit: `fill` is half the longer cell diagonal
    and NOT half the axial step (r03's counterexample), and the strip follows every edge
    and not only eta = 1/4 (r03 found the residual holes had moved to m2 = 5).

    This remains a margin argument under LOCAL FLATNESS -- the quadratic form with a
    single metric is not geodesic distance -- so the off-grid and adaptive probes stay
    the empirical check and are reported separately.  The r03 verifier's finite-point
    triangle bound is the rigorous version, and it needs the metric inflation between
    sample and probe, which it measured at most 1.0152 over the tested sets.
    """
    edges = boundary_strip(region)
    strip_tau = np.vstack([edge["tau"][edge["valid"]] for edge in edges])
    strip_metrics = np.vstack([edge["metrics"][edge["valid"]] for edge in edges])
    strip_masses = np.vstack([edge["masses"][edge["valid"]] for edge in edges])
    fill = strip_fill_distance(edges)
    radius_target = COVERING_RADIUS - fill
    if radius_target <= 0.0:
        raise RuntimeError(
            f"strip grid too coarse to guarantee anything: fill distance {fill:.4f} "
            f"exceeds the covering radius {COVERING_RADIUS:.4f}")
    mu_target = radius_target ** 2

    bank_tau = np.asarray(bank_tau, dtype=float).reshape(-1, 2)
    added_tau, added_masses = [], []
    before = worst_mismatch(bank_tau, strip_tau, strip_metrics)
    current = before.copy()
    unfixable = np.zeros(len(strip_tau), dtype=bool)
    while True:
        uncovered = np.flatnonzero((current > mu_target) & ~unfixable)
        if uncovered.size == 0 or len(added_tau) >= max_added:
            break
        pick = uncovered[int(np.argmax(current[uncovered]))]
        new_masses = clamp_physical(*strip_masses[pick])
        new_tau = np.asarray(tau(*new_masses))
        added_tau.append(new_tau)
        added_masses.append(new_masses)
        offset = strip_tau - new_tau
        contribution = np.einsum("ij,ijk,ik->i", offset, strip_metrics, offset)
        current = np.minimum(current, contribution)
        if current[pick] > mu_target:
            unfixable[pick] = True
    # A repair that ran out of budget, or gave up on a sample, must NOT quietly hand
    # back a bank: the counts went into metadata and nothing read them (d1verify r04).
    remaining = int((current > mu_target).sum())
    if remaining or unfixable.any() or len(added_tau) >= max_added:
        raise RuntimeError(
            f"boundary repair did not complete: {remaining} samples above mu_target, "
            f"{int(unfixable.sum())} unfixable, {len(added_tau)} added "
            f"(max_added={max_added}). The bank is NOT written.")
    return {"added_tau": np.asarray(added_tau).reshape(-1, 2),
            "added_masses": np.asarray(added_masses).reshape(-1, 2),
            "strip_spacing_target": float(STRIP_SPACING),
            "strip_cell_fill_distance": float(fill),
            "repair_radius_target": float(radius_target),
            "repair_mu_target": float(mu_target),
            "repair_margin_note": "mu_target = (R - fill)^2 with fill = half the longer "
                                  "cell diagonal; local-flatness margin, not a theorem",
            "n_strip_samples": int(len(strip_tau)),
            "n_strip_per_edge": [int(edge["valid"].sum()) for edge in edges],
            "n_strip_above_mu_target_before": int((before > mu_target).sum()),
            "n_strip_above_mu_target_after": int((current > mu_target).sum()),
            "n_strip_above_mm_after": int((current > MU_MAX).sum()),
            "n_strip_unfixable": int(unfixable.sum()),
            "strip_worst_before": float(before.max()),
            "strip_worst_after": float(current.max())}


def build(region, lattice, boundary, collision_fraction=0.5, verbose=True,
          seed_masses=None):
    grown = grow(region, lattice, boundary, collision_fraction, verbose=verbose,
                 seed_masses=seed_masses)
    cells = grown["cells"]
    retained = [cell for cell in cells if cell["fertile"]]

    direct, pushed = [], []
    for cell in retained:
        if cell["physical"]:
            direct.append((cell["masses"], cell["tau"], cell["inside_region"], 0))
    # Push-back, then deduplicate against everything already kept.  Many non-physical
    # nodes project onto nearly the same point of eta = 1/4, which is how the old
    # banks ended up with an irregular on-line row; the same proximity rule that
    # governs growth governs the projected row.
    kept_tau = [np.asarray(row[1]) for row in direct]
    threshold = (collision_fraction * grown["spacing"]) ** 2
    for cell in retained:
        if cell["physical"]:
            continue
        answer = push_back_to_equal_mass(cell["tau"], cell["eigenvectors"])
        if answer is None:
            continue
        _, point, _, _ = answer
        mass = masses_of_tau(point)
        if mass is None:
            continue
        try:
            metric = analytic_metric(*clamp_physical(*mass))
        except (RuntimeError, ValueError):
            continue
        delta = np.asarray(kept_tau) - np.asarray(point)
        if len(kept_tau) and np.min(np.einsum("ij,jk,ik->i", delta, metric, delta)) < threshold:
            continue
        kept_tau.append(np.asarray(point))
        pushed.append((mass, np.asarray(point), in_region(*mass, region), 1))

    rows = direct + pushed
    bank_masses = np.asarray([row[0] for row in rows])
    bank_tau = np.asarray([row[1] for row in rows])
    repair = repair_boundary(bank_tau, bank_masses, region)

    all_masses = np.vstack([bank_masses, repair["added_masses"]]) if len(repair["added_masses"]) \
        else bank_masses
    all_tau = np.vstack([bank_tau, repair["added_tau"]]) if len(repair["added_tau"]) else bank_tau
    origin = ([0] * len(direct)) + ([1] * len(pushed)) + ([2] * len(repair["added_tau"]))
    inside = [int(row[2]) for row in rows] + [
        int(in_region(*m, region)) for m in repair["added_masses"]]

    return {"region": region, "lattice": lattice, "minimal_match": MM,
            "covering_radius": COVERING_RADIUS,
            "proper_lattice_spacing": grown["spacing"],
            "collision_fraction_of_local_spacing": collision_fraction,
            "masses": all_masses, "tau": all_tau,
            "origin": np.asarray(origin), "inside_region": np.asarray(inside),
            "n_templates": int(len(all_masses)),
            "n_from_lattice": len(direct), "n_pushed_back": len(pushed),
            "n_boundary_repair": int(len(repair["added_tau"])),
            "n_cells_created": len(cells),
            "n_cells_nonphysical": int(sum(not c["physical"] for c in cells)),
            "n_generations": grown["n_generations"],
            "n_metric_calls": grown["n_metric_calls"],
            "growth_seconds": grown["growth_seconds"],
            "boundary_repair": {k: v for k, v in repair.items() if not k.startswith("added")},
            "rng_seed": None,
            "rng_note": "deterministic placement; no random numbers are drawn",
            "fertility_rule": "min over region-boundary samples of d^T g_boundary d <= 1 - MM "
                              "(amended 2026-09-23; was d^T g_cell d, which is void where "
                              "the metric degenerates)",
            "eta_boundary_rule": "grow without projecting; push non-physical fertile cells "
                                 "back onto eta = 1/4 after reproduction (Cokelaer 2007 p. 6); "
                                 "then greedy covering repair of the strip along EVERY region "
                                 "edge, not only eta = 1/4 (widened 2026-09-24 after the "
                                 "residual holes moved to the m2 = 5 edge)",
            "connector_rule": "STAND-IN: proximity threshold at collision_fraction of the "
                              "local spacing, not Cokelaer's explicit connectors",
            "metric_source": "q1bC out/lib/metric.py analytic_metric (3.5PN, frozen)"}


def write_bank(result, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"bank_{result['region']}_{result['lattice']}_mm097"
    rows = np.column_stack([result["masses"], result["tau"],
                            result["inside_region"], result["origin"]])
    path = output_dir / f"{stem}.txt"
    temporary = path.with_suffix(".txt.tmp")
    np.savetxt(temporary, rows, fmt=("%.17g", "%.17g", "%.17g", "%.17g", "%d", "%d"),
               header="m1_Msun m2_Msun tau0_s tau3_s inside_region "
                      "origin(0=lattice,1=pushed_back,2=boundary_repair)")
    os.replace(temporary, path)
    metadata = {key: value for key, value in result.items()
                if key not in ("masses", "tau", "origin", "inside_region")}
    metadata.update({
        "bank_file": path.name,
        "columns": ["m1_Msun", "m2_Msun", "tau0_s", "tau3_s", "inside_region", "origin"],
        "n_inside_region": int(result["inside_region"].sum()),
        "mass_extrema_msun": {
            "m1_min": float(result["masses"][:, 0].min()),
            "m1_max": float(result["masses"][:, 0].max()),
            "m2_min": float(result["masses"][:, 1].min()),
            "m2_max": float(result["masses"][:, 1].max())},
        "placement_code": "work/d1/placement.py"})
    meta_path = output_dir / f"{stem}.json"
    temporary = meta_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(metadata, indent=2, sort_keys=True, default=float) + "\n")
    os.replace(temporary, meta_path)
    return path, meta_path, metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", choices=("pilot", "main", "extended"), required=True)
    parser.add_argument("--lattice", choices=("hexagonal", "square"), required=True)
    parser.add_argument("--boundary-spacing", type=float, default=None,
                        help="proper spacing of boundary samples; default R/4")
    parser.add_argument("--collision-fraction", type=float, default=0.5)
    parser.add_argument("--output-dir", default="results/d1/banks")
    args = parser.parse_args()
    boundary = Boundary(args.region, args.boundary_spacing, CACHE)
    result = build(args.region, args.lattice, boundary, args.collision_fraction)
    path, meta_path, metadata = write_bank(result, args.output_dir)
    print(json.dumps(metadata, indent=2, sort_keys=True, default=float))
    print(f"wrote {path} and {meta_path}")


if __name__ == "__main__":
    main()
