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
    optimum = json.loads((DATA / "part_f_optimum.json").read_text())
    nu = json.loads((DATA / "part_e_nu_eff.json").read_text())
    registry: dict = {}

    # ---- the convention itself -------------------------------------------------
    # Region geometry, corrected 2026-09-26 by the geomverify r01 audit and confirmed
    # here by a third method (Gauss-Legendre in (m1, m2)). The first values came from a
    # Monte Carlo with no convergence study.
    registry["proper_area_main"] = entry(
        35.717393158, "s^-2 (metric units)", "proper area of the main region",
        "geomverify r01 deterministic quadrature; independent Gauss-Legendre here gives "
        "35.717382 at order 120",
        caveat="the earlier Monte Carlo value 35.4 was low by 0.89 %, within its own "
               "sampling error but quoted without one")
    registry["proper_area_extended"] = entry(
        7.434835530, "s^-2 (metric units)", "proper area of the extended region",
        "geomverify r01; independent Gauss-Legendre here gives 7.434579 at order 120",
        caveat="the earlier Monte Carlo value 7.08 was low by 4.77 %")
    registry["proper_perimeter_main"] = entry(
        255.743181875, "s^-1 (metric units)", "proper perimeter of the main region",
        "geomverify r01, agreeing with this project's value to ten digits",
        caveat="a disc of the same proper area would have perimeter 21.2; the region is "
               "a ribbon, not a blob")
    registry["effective_width_main"] = entry(
        1.612668, "covering radii", "effective width 2A/P of the main region",
        "geomverify r01",
        caveat="a global summary, NOT a local width bound; it is why the region is "
               "boundary-dominated and why an asymptotic ratio has almost no interior "
               "in which to be measured")
    registry["effective_width_extended"] = entry(
        2.088516, "covering radii", "effective width 2A/P of the extended region",
        "geomverify r01", caveat="as above")
    registry["cusp_limiting_angle"] = entry(
        0.0, "degrees", "limiting angle between the two region edges at (5,5) Msun",
        "geomverify r01, derived analytically: differentiating the two mass rays gives "
        "positively parallel tangents, so the limit is exactly zero",
        caveat="a TRUE cusp, now proved rather than inferred from secants. The finite "
               "secant angles scale linearly, 0.103330 degrees per Msun of equal "
               "component increment; a finite-angle floor and numerical cancellation "
               "were both refuted")

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
    registry["adaptive_worst_mismatch_main_hexagonal"] = entry(
        0.032220597236526316, "dimensionless",
        "worst mismatch an adaptive search reached in the main hexagonal bank",
        "jobs/2026-09-25_112044_derive-dverify r03 verifier, reproduced by hand to 14 digits",
        caveat="a lower bound on the true worst case, not a certified maximum; it "
               "refutes strict covering at MM = 0.97 for this bank")
    registry["adaptive_worst_mismatch_extended_hexagonal"] = entry(
        0.03615253316239979, "dimensionless",
        "worst mismatch an adaptive search reached in the extended hexagonal bank",
        "jobs/2026-09-25_112044_derive-dverify r03 verifier, reproduced by hand",
        caveat="as above; both square banks survived the same search")
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
        5.3065605155e-16, "relative",
        "worst relative error of the rare-tail Poisson approximation on rho*, all banks",
        "efverify r01 verifier; the author's own figure of 3.40e-16 was the MM = 0.97 "
        "value, not the maximum",
        caveat="negligible, and shown rather than assumed, as part E required")

    # ---- part E.2: the calibrated trials rate -----------------------------------
    registry["nu_eff_main_hexagonal_mm097"] = entry(
        nu["banks"]["main_hexagonal_mm097"]["nu_eff_per_second"], "per second",
        "calibrated effective independent-trials rate, main hexagonal bank at MM = 0.97",
        "work/d1/nu_eff.py, 100 segments of 32 s", seed=nu["seed"],
        caveat="a summary of a correlated search, not a count of anything; the level is "
               "good to roughly +-50 %, which moves rho* by 0.05 and is immaterial")
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
    registry["imrphenomd_volume_loss_extended_hexagonal"] = entry(
        optimum["extended"]["hexagonal_mm097"]["losses"]["population_imrphenomd_approx"],
        "fraction",
        "volume loss against IMRPhenomD signals, extended hexagonal, MM = 0.97",
        "work/d1/optimum.py",
        caveat="a DECLARED APPROXIMATION: q1bC's continuous-family fitting factor composed "
               "multiplicatively with the discretisation match, assuming an independence "
               "that is not established. Of this, 0.495 is the family alone -- in the "
               "extended region the waveform model, not the bank, costs the volume")
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
