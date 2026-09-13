# TODO

What is unresolved. A number that is needed and cannot be found goes here — do not invent
it.

## Plan to hand-in (2026-09-14 → 2026-09-27)

Settled 2026-09-13. Quota split: workers, lead and writer on Codex (`gpt-6-astra` — preflight
it first); verifier on Claude, so the check is a different model family from the work.
Claude Pro is kept for verifiers and interactive sessions. Two Codex resets: the first for
steps 3–5, the second for step 6 or the paper. Before every job: `/usage` (Claude) and
`/status` (Codex); every job keeps the round-2 checkpoint. Jobs are launched by hand.

- [ ] **0. Housekeeping** (Sun 13) — install `python-is-python3` (the derive check calls bare
      `python`), `poppler-utils` (agents can render PDFs), `texlive-latex-recommended` +
      `latexmk` (paper), `gh` (publishing); commit the q12 objective.
- [ ] **1. Review job q12** (Mon 14) — follow two numbers in `out/report.html` to the code
      that made them and ask what it assumed (day 1); a fresh Codex session with no context
      reads `out/` and tries to break it (homework: second opinion).
- [ ] **2. Close the decisions** (Tue 15) — everything under "Decisions for step 2" below,
      written into [[conventions]] and `structure/claims.yaml`.
- [ ] **3. Job q345** (launch Tue 15 night → checkpoint Wed 16 → done Thu 17) — questions
      3–5 of `structure/objective.txt`, updated with step 2 and allowed to reuse job q12's
      code as prior work. Add the day-2 check first: ⟨ρ²⟩ = 2 and the FAP tail on
      signal-free Gaussian noise before trusting ρ\*. 2 workers (the covering Monte Carlo
      parallelises); steer with `job resume --say`; try extra rounds (day 4).
- [ ] **4. Blind review** (Thu 17–Fri 18) — two fresh reviewers, one per backend, read the
      q345 `out/` with no logs or model names; the claims are what survives (day 3).
- [ ] **5. Port into the repo** (Sat 19–Sun 20) — write `tests/test_acceptance.py` by hand,
      pinning the key job numbers with tolerances; `feature` job with `--acceptance-guard`
      builds `src/` (overlap, metric, threshold, bank), `scripts/compute_numbers.py`,
      `scripts/make_figures.py`, under the provenance hook (day 3 gate, day 5). Run
      `compute_numbers.py` twice for a bitwise check; figures with `SOURCE_DATE_EPOCH`; fill
      the README reproducibility categories.
- [ ] **6. SVD cross-check — optional** (Mon 21–Tue 22) — only if steps 1–5 are done by Sun
      20 night; small `derive` job on the second Codex reset. Otherwise future work in the
      paper. See "Stretch" below.
- [ ] **7. Paper** (Tue 22–Wed 23) — simplifications first; a controlled measurement with an
      independent analytic check, not a reproduction of Roulet et al.; every number via
      `\dataref` from `data/project_numbers.json`; `draft` job with a Claude verifier
      checking each number against the registry; build with `latexmk`.
- [ ] **8. HTML page** (Wed 23–Thu 24) — move the Owen guide to `page/owen.html`;
      `page/index.html` becomes the project page, same content and numbers as the PDF,
      offline (homework: same content in two formats).
- [ ] **9. Publish and reproduce from a clean clone** (Thu 24–Fri 25) — `gh` repo + push; a
      fresh agent in a clone under `/tmp` follows only the README (day 3); fix what breaks.
- [ ] **10. Final review** (Sat 26) — two fresh reviewers against the registry and
      provenance; `scripts/check_provenance.py` clean; optional token audit.
- [ ] **11. Buffer and hand-in** (Sun 27) — release tag, link.

If time slips, step 6 is cut first.

## Decisions for step 2

The one-page spec was settled 2026-09-09 — full table with rejected alternatives in
[[conventions]]:

- [x] Detector and PSD: single detector, analytic `aLIGOZeroDetHighPower` (pycbc).
- [x] Frequency band: $20$–$1024\ \mathrm{Hz}$; segment length = next power of two above
      the longest TaylorF2 duration in range ($5+5\,M_\odot$ from 20 Hz).
- [x] Parameter coordinates: chirp times $(\tau_0, \tau_3)$ at $f_0 = 20\ \mathrm{Hz}$.
      Mass range: component masses $\in [5, 50]\,M_\odot$, $m_1 \ge m_2$, no spin.
- [x] Waveform family: TaylorF2 for the Owen-metric comparison and everything downstream
      (stages 2–5); IMRPhenomD (pycbc) for the "missing physics" contrast in stage 1.
- [x] $\mathrm{MM}$ target: 0.97 (headline point; curves computed vs. MM).
- [~] $\rho^\*$: solve from a target FAP with a bank trials factor. **Method fixed, two
      inputs still open** (below).

Still open:

- [ ] **Target FAP** value behind $\rho^\*$ (e.g. $10^{-3}$ over the analysis) and the
      **observation time** behind $N_{\rm indep\ time\ samples}$ in the trials factor.
- [ ] Whether to cap **total mass** ($M \le 100\,M_\odot$, automatic here) or **chirp
      mass** on top of the component-mass box.
- [ ] **Stage-1 example** (from job q12): 73–99.7 % of the TaylorF2-vs-IMRPhenomD mismatch
      is TaylorF2's ISCO truncation, not phase error. Compare against IMRPhenomD truncated at
      the TaylorF2 cutoff instead, or keep and reframe as a truncation example?
- [ ] **Moving ISCO cutoff** (from job q12): with the cutoff moving with mass the match has
      no quadratic metric, and the metric varies fastest at the 50+50 corner (≈97 % of it
      from the cutoff). This undercuts the "metric near-constant in $(\tau_0,\tau_3)$"
      rationale in [[conventions]] at high mass. Metric with the cutoff fixed per point and
      the high-mass breakdown reported, or a narrower mass range?
- [ ] The explicit **five-stage breakdown**, each stage's **central figure**, and the
      per-stage **"verified" checklist**.

## Corrections to carry in (from job q12)

- [ ] [[sources/owen1995_template_metric]]: the eigenvector misprint is on **both** lines of
      Owen Eq. 49 (arXiv v1 numbers it 3.15; TeX lines 1097–1098), not only the first. The
      equation numbers 44–45 and 49 are consistent with arXiv v1's sectioned (3.10),
      (3.11), (3.15).
- [ ] The analytic check is the **3.5 PN** projected metric: the Owen & Sathyaprakash 1999
      2PN metric differs from it by 10–66 % (median over components), so it is not a usable
      analytic check at our PN order.

## Open questions

- [ ] Single-template vs. against-a-bank framing for "how wrong before lost" — do both?
- [ ] Does $\Delta V/V \approx 3(1-\mathrm{MM})$ hold across the mass range, or break
      where the metric varies fastest? (This is a deliverable, not just a check.)

## Stretch: second bank-spacing cross-check (claim `bank-spacing-cross-check-svd`)

Step 6 of the plan.

- [ ] Reuse the TaylorF2 waveforms sampled for the match map (stage 2) to build the
      SVD phase basis of [[sources/roulet2019_svd_bank]], restricted to our 2D
      non-spinning range. Place a regular grid in the resulting $c$-space and compare
      $N_{\rm templates}(\mathrm{MM})$ and the covering histogram against the
      Owen-metric bank. Cheap given stage-2 waveforms already exist; do after stages
      1-4 are solid, not before.
