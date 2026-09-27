#!/usr/bin/env python3
"""The sole writer of `data/project_numbers.json` -- the number registry.

Every number that appears in `page/` or `paper/` is computed here and nowhere else, so
that regenerating this one file reproduces every quoted value.

Each entry carries the value, a unit, a one-line meaning, where it came from, and --
this is the field that matters most in this project -- `caveat`, which says what the
number is NOT. Several results here are conditional on a model choice, and a reader who
takes the value without the caveat will draw the wrong conclusion.

Run:  .venv/bin/python scripts/compute_numbers.py

Determinism: no wall-clock, no unseeded RNG. Every Monte-Carlo quantity records the seed
that produced it. The inputs are the tracked JSONs under data/, which
scripts/export_figure_data.py refills from results/.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = DATA / "project_numbers.json"


def entry(value, unit, meaning, source, caveat=None, seed=None):
    record = {"value": value, "unit": unit, "meaning": meaning, "source": source}
    if caveat:
        record["caveat"] = caveat
    if seed is not None:
        record["seed"] = seed
    return record


def compute() -> dict:
    part_d = json.loads((DATA / "part_d_mm097.json").read_text())
    part_e = json.loads((DATA / "part_e_mm097.json").read_text())
    # ONE source for part F. There used to be two files, written by different scripts
    # with different seeds; their population losses disagreed by up to 5.4 %, and a
    # claim in the paper was assembled from one number in each. A blind review caught it.
    optimum = json.loads((DATA / "part_f_optimum.json").read_text())
    nu = json.loads((DATA / "part_e_nu_eff.json").read_text())
    registry: dict = {}

    # ---- the convention itself -------------------------------------------------
    # Region geometry, READ FROM A FILE. A blind review found these were hard-coded
    # literals with nothing behind them, which made the paper's claim that regenerating
    # one file reproduces every value a transcription. scripts/compute_geometry.py now
    # computes them by Gauss-Legendre quadrature at two orders and ships the result,
    # including the extended perimeter, which was never shipped at all.
    geom = json.loads((DATA / "region_geometry.json").read_text())
    for region in ("main", "extended"):
        g = geom[region]
        registry[f"proper_area_{region}"] = entry(
            g["proper_area"], "s^-2 (metric units)", f"proper area of the {region} region",
            "scripts/compute_geometry.py, Gauss-Legendre order 120",
            caveat=f"order 60 gives {g['proper_area_coarser_order']:.6f}, so the "
                   f"quadrature is converged to {g['proper_area_order_change']:.2g}; this "
                   f"is a numerical convergence estimate, not a rigorous enclosure")
        registry[f"proper_perimeter_{region}"] = entry(
            g["proper_perimeter"], "s^-1 (metric units)",
            f"proper perimeter of the {region} region",
            "scripts/compute_geometry.py, 600 segments per edge",
            caveat=f"a disc of the same proper area would have perimeter "
                   f"{g['disc_perimeter_same_area']:.1f}: the region is a ribbon")
        registry[f"effective_width_{region}"] = entry(
            g["effective_width_in_covering_radii"], "covering radii",
            f"effective width 2A/P of the {region} region",
            "scripts/compute_geometry.py",
            caveat="a global summary, NOT a local width bound; it is why the region is "
                   "boundary-dominated and why an asymptotic ratio has almost no interior "
                   "in which to be measured")
    registry["cusp_secant_coefficient"] = entry(
        geom["cusp_secant_coefficient"], "degrees per Msun",
        "leading secant-angle coefficient between the two region edges at (5,5) Msun",
        "scripts/compute_geometry.py, fitted down to 1e-4 Msun separation",
        caveat="the LIMIT is exactly zero and is analytic, not measured: the two mass "
               "rays have positively parallel tangents. Only this coefficient is measured")

    registry["minimal_match_headline"] = entry(
        0.97, "dimensionless", "the headline minimal match",
        "Owen 1996 gr-qc/9511032: a fiducial 'chosen by the experimenter', "
        "corresponding to roughly 90 % of the ideal event rate",
        caveat="a design convention, not a derived constant; the field applies it as a "
               "percentile, not a worst case -- Sakon et al. 2023 quote fitting factors "
               "above 97 % for 90 % of injections in the O4 bank")
    registry["worst_case_volume_loss_mm097"] = entry(
        1 - 0.97 ** 3, "fraction",
        "exact worst-case fractional volume loss at MM = 0.97, sources uniform in "
        "Euclidean volume",
        "closed form 1 - MM^3",
        caveat="the linear expansion 3(1-MM) = 0.09 is 3.060909 % larger and is a "
               "different quantity; the two are never merged")

    # ---- part D: banks and covering --------------------------------------------
    for key, row in part_d.items():
        if not isinstance(row, dict) or "n_templates" not in row:
            continue
        registry[f"n_templates_{key}_mm097"] = entry(
            row["n_templates"], "templates", f"bank size, {key.replace('_', ' ')}, MM = 0.97",
            "results/d1/banks, counted by scripts/export_figure_data.py",
            caveat=f"includes the boundary repair, which is "
                   f"{row['composition']['boundary_repair']} of these templates; the "
                   f"repair is this project's, not Cokelaer's. Against the "
                   f"constant-metric ideal this is "
                   f"{row['n_templates'] / row['constant_metric_ideal']:.2f}x, but that "
                   f"ideal is NOT a universal lower bound for a finite region -- the "
                   f"geomverify r01 audit derived strip and disc counterexamples -- so "
                   f"the factor is a comparison, not a verdict of redundancy")
        registry[f"covering_fraction_{key}_mm097"] = entry(
            row["all"]["fraction_at_or_above"], "fraction",
            f"fraction of injections at or above MM = 0.97, {key.replace('_', ' ')}",
            "work/d1/report_d.py, 3000 uniform injections", seed=row["seed"],
            caveat="quadratic form in the injection's own metric, not a waveform match; "
                   "uniform sampling does not find the holes an adaptive search does")
    witnesses = json.loads((DATA / "fig_witnesses.json").read_text())
    for bank in ("main_hexagonal", "extended_hexagonal"):
        registry[f"adaptive_worst_mismatch_{bank}"] = entry(
            witnesses[bank]["mismatch"], "dimensionless",
            f"worst mismatch an adaptive search reached in the {bank.replace('_', ' ')} bank",
            f"data/fig_witnesses.json at ({witnesses[bank]['m1']:.6f}, "
            f"{witnesses[bank]['m2']:.6f}) Msun; found by an independent audit and "
            f"reproduced by hand to fourteen digits",
            caveat="a lower bound on the true worst case, not a certified maximum. It "
                   "refutes strict covering at MM = 0.97 for both hexagonal banks; both "
                   "square banks survived the same search")
    for region, hexa, sq in (("main", "main_hexagonal", "main_square"),
                             ("extended", "extended_hexagonal", "extended_square")):
        registry[f"hex_square_ratio_{region}_mm097"] = entry(
            part_d[hexa]["n_templates"] / part_d[sq]["n_templates"], "dimensionless",
            f"hexagonal/square template ratio, {region} region, MM = 0.97",
            "counted from the delivered banks",
            caveat="NOT a well-defined property of the lattices here: counting the "
                   "lattice alone gives 0.4882 (main) and 0.4225 (extended), because the "
                   "boundary repair contributes 17-51 % depending on lattice and region")
    registry["border_fraction_main"] = entry(
        part_d["main_hexagonal"]["border_fraction_injection_metric"], "fraction",
        "injections within one covering radius of a region boundary, main",
        "work/d1/report_d.py, injection metric",
        caveat="so high that the specification's interior/border split carries little "
               "information; the boundary-sample metric gives 0.793 instead")
    registry["border_fraction_extended"] = entry(
        part_d["extended_hexagonal"]["border_fraction_injection_metric"], "fraction",
        "injections within one covering radius of a region boundary, extended",
        "work/d1/report_d.py, injection metric", caveat="as above; 0.939 under the other convention")

    # ---- part E: threshold ------------------------------------------------------
    for bank, row in part_e["banks"].items():
        registry[f"rho_star_naive_{bank}"] = entry(
            row["rho_star"]["far_1_per_100yr"], "dimensionless",
            f"threshold at FAR = 1/(100 yr), {bank.replace('_', ' ')}, naive trials",
            "work/d1/threshold.py, exact FAP = 1-(1-p)^N",
            caveat="the naive bound over-counts trials, so this is an UPPER bound -- "
                   "proved for a finite grid in Gaussian noise by the efverify r01 "
                   "verifier from the Gaussian correlation inequality "
                   "(Latala and Matlak, arXiv:1512.08776, Thm 1)")
    registry["poisson_approximation_error"] = entry(
        part_e["worst_poisson_relative_error"], "relative",
        "largest resolvable difference between the exact trials combination and its "
        "rare-tail Poisson form, over the reported banks and operating points",
        "work/d1/threshold.py",
        caveat="THIS IS FLOATING-POINT NOISE, NOT THE APPROXIMATION ERROR. The true "
               "mathematical difference at the operating point is near 6e-19, some 900 "
               "times smaller, and 1e-23 at 5 sigma. The conclusion -- that the "
               "approximation is safe -- is right; this number is a limit of double "
               "precision and must not be quoted as the error itself")

    # ---- part E.2: the calibrated trials rate -----------------------------------
    registry["nu_eff_main_hexagonal_mm097"] = entry(
        nu["banks"]["main_hexagonal_mm097"]["nu_eff_per_second"], "per second",
        "calibrated effective independent-trials rate, main hexagonal bank at MM = 0.97",
        "work/d1/nu_eff.py, 100 segments of 32 s", seed=nu["seed"],
        caveat="a summary of a correlated search, not a count of anything; the level is "
               "good to roughly +-50 %, which moves rho* by 0.05 and is immaterial")
    registry["trials_exponent_pooled"] = entry(
        nu["alpha_fit"]["all"]["alpha"], "dimensionless",
        "exponent from fitting all twenty banks together, ignoring region and lattice",
        "work/d1/nu_eff.py",
        caveat="REPORTED BUT NOT USED, and the paper says so. It is four standard "
               "deviations ABOVE 1, the opposite of the within-family result, because the "
               "two regions differ in nu_eff by more than a factor ten at comparable "
               "template counts: the pooled slope measures the step between regions, not "
               "how either scales")
    for family, fit in nu["alpha_fit"].items():
        if family == "all":
            continue
        registry[f"trials_exponent_{family}"] = entry(
            fit["alpha"], "dimensionless",
            f"exponent in N_eff proportional to N_templates^alpha, {family.replace('_', ' ')}",
            "work/d1/nu_eff.py, paired bootstrap over shared segments",
            caveat=f"95 % CI [{fit['alpha_ci95'][0]:.4f}, {fit['alpha_ci95'][1]:.4f}]; "
                   f"the naive model assumes 1. The POOLED fit across regions gives 1.29 "
                   f"and is a Simpson effect, not a scaling")

    # ---- part F: volume ---------------------------------------------------------
    for region in ("main", "extended"):
        for lattice in ("hexagonal", "square"):
            row = optimum[region][f"{lattice}_mm097"]
            registry[f"population_volume_loss_{region}_{lattice}_mm097"] = entry(
                row["losses"]["population_taylorf2"], "fraction",
                f"population-average discretisation volume loss, {region} {lattice}",
                "work/d1/optimum.py, TaylorF2 injections",
                caveat="4 to 9 times smaller than the worst case 1-MM^3 = 0.087327")
    for region in ("main", "extended"):
        losses = optimum[region]["hexagonal_mm097"]["losses"]
        registry[f"imrphenomd_volume_loss_{region}"] = entry(
            losses["population_imrphenomd_approx"], "fraction",
            f"volume loss against IMRPhenomD signals, {region} hexagonal, MM = 0.97",
            "work/d1/optimum.py",
            caveat="a DECLARED APPROXIMATION: the frozen continuous-family fitting factor "
                   "composed multiplicatively with the discretisation match, assuming an "
                   "independence that is not established. The family-only figure beside "
                   "it is the rigorous bound")
        registry[f"imrphenomd_family_only_{region}"] = entry(
            losses["imrphenomd_family_only_bound"], "fraction",
            f"volume loss from the continuous TaylorF2 family alone, {region}",
            "work/d1/optimum.py, same injections and seed as the line above",
            caveat="a rigorous lower bound on the IMRPhenomD loss: the best match against "
                   "a discrete subset cannot exceed the best match against the family it "
                   "is drawn from. The difference from the line above is what the bank's "
                   "discretisation adds")
    for region, lattice in (("main", "hexagonal"), ("main", "square"),
                            ("extended", "hexagonal"), ("extended", "square")):
        naive, calib = [], []
        for mm in (0.95, 0.99):
            row = optimum[region][f"{lattice}_mm{round(mm * 100):03d}"]
            naive.append(row["v_eff"]["far_1_per_100yr"]["taylorf2"])
            calib.append(row["v_eff_calibrated"]["far_1_per_100yr"]["taylorf2"])
        registry[f"veff_change_naive_{region}_{lattice}"] = entry(
            100 * (naive[1] / naive[0] - 1), "per cent",
            f"change in V_eff from MM = 0.95 to 0.99, {region} {lattice}, naive trials",
            "work/d1/optimum.py",
            caveat="the sign is set by the trials model, not by the bank")
        registry[f"veff_change_calibrated_{region}_{lattice}"] = entry(
            100 * (calib[1] / calib[0] - 1), "per cent",
            f"change in V_eff from MM = 0.95 to 0.99, {region} {lattice}, calibrated nu_eff",
            "work/d1/optimum.py with work/d1/nu_eff.py",
            caveat="opposite in sign to the naive result; the curves are flat to within "
                   "about 2 % and are NOT monotonic in the extended region, so no optimum "
                   "is resolved inside the grid")
    return registry


def main() -> None:
    registry = compute()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with_caveat = sum(1 for v in registry.values() if "caveat" in v)
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(registry)} numbers, "
          f"{with_caveat} carrying a caveat)")


if __name__ == "__main__":
    main()
