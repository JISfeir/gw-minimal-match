#!/usr/bin/env python3
"""Acceptance test, written by hand. It pins what the paper claims.

This is not a unit test suite: it is the specification. Each test fixes a number the
paper reports, with a tolerance chosen from how that number was measured, so that a
change in the pipeline that moves a reported value fails here before it reaches print.

Tolerances are deliberate:
  * exact closed forms are pinned to 1e-12;
  * counts are pinned exactly -- placement is deterministic and reproduces byte for byte;
  * Monte-Carlo quantities get a tolerance from their own reported error, never tighter;
  * quantities an independent audit re-measured are pinned to span BOTH measurements,
    because agreeing with only our own number would defeat the point.

Run:  .venv/bin/python -m pytest tests/test_acceptance.py    (or: python tests/test_acceptance.py)
"""
from __future__ import annotations

import json
import math
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


def load(name):
    return json.loads((DATA / name).read_text())


class Conventions(unittest.TestCase):
    def test_worst_case_volume_loss_is_a_closed_form(self):
        registry = load("project_numbers.json")
        self.assertAlmostEqual(registry["worst_case_volume_loss_mm097"]["value"],
                               0.087327, places=12)

    def test_linear_expansion_is_a_different_number(self):
        """3(1-MM) exceeds 1-MM^3 by 3.060909 %. The paper must never merge them."""
        exact, linear = 1 - 0.97 ** 3, 3 * (1 - 0.97)
        self.assertAlmostEqual(100 * (linear / exact - 1), 3.060908997, places=6)


class PartDBanks(unittest.TestCase):
    """Placement is deterministic, so counts are pinned exactly."""

    EXPECTED = {"main_hexagonal": (1772, 744, 129, 899),
                "main_square": (2273, 1524, 86, 663),
                "extended_hexagonal": (336, 169, 10, 157),
                "extended_square": (488, 400, 5, 83)}

    def test_counts_and_composition(self):
        part_d = load("part_d_mm097.json")
        for bank, (total, lattice, pushed, repair) in self.EXPECTED.items():
            row = part_d[bank]
            self.assertEqual(row["n_templates"], total, bank)
            self.assertEqual(row["composition"]["lattice"], lattice, bank)
            self.assertEqual(row["composition"]["pushed_back"], pushed, bank)
            self.assertEqual(row["composition"]["boundary_repair"], repair, bank)

    def test_the_repair_share_is_lattice_dependent(self):
        """The reason the hexagonal/square ratio is not a property of the lattices."""
        part_d = load("part_d_mm097.json")
        share = {k: part_d[k]["composition"]["boundary_repair"] / part_d[k]["n_templates"]
                 for k in self.EXPECTED}
        self.assertGreater(share["main_hexagonal"], 0.50)
        self.assertLess(share["extended_square"], 0.18)

    def test_strict_covering_fails_for_both_hexagonal_banks(self):
        """Witnesses from the dverify r03 audit, reproduced by hand to 14 digits."""
        registry = load("project_numbers.json")
        for key in ("adaptive_worst_mismatch_main_hexagonal",
                    "adaptive_worst_mismatch_extended_hexagonal"):
            self.assertGreater(registry[key]["value"], 0.03, key)

    def test_uniform_sampling_does_not_see_those_holes(self):
        """The methodological point: three of four banks look perfect under uniform
        injections, and an adaptive search refutes two of them."""
        part_d = load("part_d_mm097.json")
        self.assertEqual(part_d["main_hexagonal"]["all"]["fraction_at_or_above"], 1.0)

    def test_both_regions_are_boundary_dominated(self):
        part_d = load("part_d_mm097.json")
        self.assertGreater(part_d["main_hexagonal"]["border_fraction_injection_metric"], 0.75)
        self.assertGreater(part_d["extended_hexagonal"]["border_fraction_injection_metric"], 0.90)


class PartEThreshold(unittest.TestCase):
    def test_thresholds_at_the_operating_point(self):
        part_e = load("part_e_mm097.json")
        expected = {"main_hexagonal": 8.5996, "main_square": 8.6286,
                    "extended_hexagonal": 8.4041, "extended_square": 8.4484}
        for bank, value in expected.items():
            self.assertAlmostEqual(
                part_e["banks"][bank]["rho_star"]["far_1_per_100yr"], value, places=3, msg=bank)

    def test_poisson_approximation_is_negligible(self):
        """Shown, not assumed, as part E required. The bound spans both the author's
        MM = 0.97 figure and the audit's all-bank maximum."""
        part_e = load("part_e_mm097.json")
        self.assertLess(part_e["worst_poisson_relative_error"], 1e-14)


class PartETrials(unittest.TestCase):
    """The calibration the whole of part F turns on."""

    def test_n_eff_is_far_below_the_naive_bound_and_the_gap_widens(self):
        nu = load("part_e_nu_eff.json")
        coarse = nu["banks"]["main_hexagonal_mm095"]["ratio_to_naive"]
        dense = nu["banks"]["main_hexagonal_mm099"]["ratio_to_naive"]
        self.assertLess(coarse, 0.20)
        self.assertLess(dense, coarse)

    def test_exponent_is_far_from_one_in_every_family(self):
        """Pinned to span BOTH our five-point fits and the audit's independent endpoint
        estimate of 0.204994 with its 95 % CI [0.1225, 0.2910]."""
        nu = load("part_e_nu_eff.json")
        for family, fit in nu["alpha_fit"].items():
            if family == "all":
                continue
            self.assertGreater(fit["alpha"], 0.05, family)
            self.assertLess(fit["alpha"], 0.35, family)
            self.assertLess(fit["alpha_ci95"][1], 0.40, family)

    def test_the_pooled_fit_is_recorded_as_an_artefact(self):
        """It must stay in the file, and it must stay far from the within-family value,
        so that anyone who reads it is forced to notice the discrepancy."""
        nu = load("part_e_nu_eff.json")
        self.assertGreater(nu["alpha_fit"]["all"]["alpha"], 1.0)


class PartFVolume(unittest.TestCase):
    def test_population_loss_is_far_below_the_worst_case(self):
        optimum = load("part_f_optimum.json")
        worst = 1 - 0.97 ** 3
        for region in ("main", "extended"):
            for lattice in ("hexagonal", "square"):
                loss = optimum[region][f"{lattice}_mm097"]["losses"]["population_taylorf2"]
                self.assertLess(loss, worst / 3.5)

    def test_in_the_extended_region_the_family_costs_the_volume(self):
        """Both legs from the SAME file and seed. They used to come from two files with
        different seeds, and the earlier tolerance here was two percentage points for a
        claim of about one -- so it could not have caught the mismatch. A blind review
        did."""
        row = load("part_f_optimum.json")["extended"]["hexagonal_mm097"]["losses"]
        total = row["population_imrphenomd_approx"]
        family = row["imrphenomd_family_only_bound"]
        self.assertGreater(family, 0.45)
        self.assertLess(total - family, 0.010)     # discretisation adds under one point
        self.assertGreater(total - family, 0.002)  # but it is not zero either

    def test_the_trials_model_flips_the_sign_of_the_trend(self):
        """The headline of part F. Naive falls, calibrated rises, in all four banks."""
        optimum = load("part_f_optimum.json")
        for region in ("main", "extended"):
            for lattice in ("hexagonal", "square"):
                naive, calib = [], []
                for mm in (0.95, 0.99):
                    row = optimum[region][f"{lattice}_mm{round(mm * 100):03d}"]
                    naive.append(row["v_eff"]["far_1_per_100yr"]["taylorf2"])
                    calib.append(row["v_eff_calibrated"]["far_1_per_100yr"]["taylorf2"])
                self.assertLess(naive[1], naive[0], f"{region} {lattice} naive")
                self.assertGreater(calib[1], calib[0], f"{region} {lattice} calibrated")

    def test_the_effect_is_small_either_way(self):
        """Guards the other half of the claim: no reading of this should say MM matters
        much for V_eff."""
        registry = load("project_numbers.json")
        for key, value in registry.items():
            if key.startswith("veff_change_"):
                self.assertLess(abs(value["value"]), 4.0, key)

    def test_no_optimum_is_resolved_inside_the_grid(self):
        """Calibrated V_eff is NOT monotonic in the extended region. If a future change
        made it monotonic, the paper's wording would have to change with it."""
        optimum = load("part_f_optimum.json")
        series = [optimum["extended"][f"hexagonal_mm{round(mm * 100):03d}"]
                  ["v_eff_calibrated"]["far_1_per_100yr"]["taylorf2"]
                  for mm in (0.95, 0.96, 0.97, 0.98, 0.99)]
        steps = [b - a for a, b in zip(series, series[1:])]
        self.assertTrue(any(s < 0 for s in steps),
                        "extended hexagonal calibrated V_eff should not be monotonic")


class Registry(unittest.TestCase):
    def test_every_number_carries_a_caveat(self):
        """Several results here are conditional on a model choice. A number without the
        sentence saying what it is not is a number that will be misread."""
        registry = load("project_numbers.json")
        self.assertGreater(len(registry), 30)
        missing = [k for k, v in registry.items() if not v.get("caveat")]
        self.assertEqual(missing, [], f"numbers with no caveat: {missing}")

    def test_every_figure_has_a_provenance_entry(self):
        import yaml
        doc = yaml.safe_load((ROOT / "provenance" / "claims.yaml").read_text())
        recorded = {f["file"] for f in doc.get("figures") or []}
        on_disk = {f"figures/{p.name}" for p in (ROOT / "figures").glob("*.pdf")}
        self.assertTrue(on_disk)
        self.assertEqual(on_disk - recorded, set())


if __name__ == "__main__":
    unittest.main(verbosity=2)
