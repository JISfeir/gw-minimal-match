# TODO

What is unresolved. A number that is needed and cannot be found goes here — do not invent
it.

## Plan to hand-in (2026-09-14 → 2026-09-27)

Settled 2026-09-13. Quota split: workers, lead and writer on Codex (`gpt-6-astra` — preflight
it first); verifier on Claude, so the check is a different model family from the work.
Claude Pro is kept for verifiers and interactive sessions. Two Codex resets: the first for
steps 3–5, the second for step 6 or the paper. Before every job: `/usage` (Claude) and
`/status` (Codex); every job keeps the round-2 checkpoint. Jobs are launched by hand.

### Figure rules — apply at every step that makes, checks or ships a figure

Found in the step-1 review of job q12 (2026-09-13): its Figure 1 plotted each point at
$(\mu, 1-\mu)$ and $(\mu, 1/(1-\mu))$, so the points sit on the curve by construction and
the figure could not have failed; its Figure 2 overlaid numeric and analytic metrics on a
10–200 scale, where the claimed 0.74 % agreement is invisible and a 3 % disagreement would
look the same. No check caught it: `checks.py` tests numbers, the provenance gate tests
tags, the writer inspected layout, the verifier read legends. The objective itself asked
for the circular figure.

- **F1. Measurement against prediction.** A figure whose y-values are computed from its
  x-values by the formula under test is not evidence. Plot what was measured against what
  was predicted — e.g. recovered SNR from injections into Gaussian noise against
  $\rho_{\rm opt}\cdot$match — or plot the residual.
- **F2. Show the claimed precision.** If the claim is agreement to X %, plot the relative
  error on a scale where X % is visible, not two overlaid curves.
- **F3. Do not collapse dimensions silently.** The metric depends on $(m_1, m_2)$, not only
  on $M$: use a 2-D map, or colour/mark by mass ratio. Axis labels carry units ($g_{ij}$ in
  $\mathrm{s}^{-2}$ in chirp-time coordinates).
- **F4. Every figure states how it could fail.** Its provenance record says what the
  figure would look like if the result were wrong. A figure for which that sentence cannot
  be written is decoration, and does not go in the page or the paper.
- **F5. One source of figures.** Only `scripts/make_figures.py` produces figures that ship.
  Nothing from a job's `out/` is copied in as an image; stale job PNGs (q12's
  `snr_vs_mismatch.png`, `metric_comparison.png`) are not ported.

### Steps

- [x] **0. Housekeeping** (Sun 13) — installed `python-is-python3`, `poppler-utils`,
      `texlive-latex-recommended` + `latexmk`, `gh` (logged in as JISfeir); q12 objective
      committed; repo pushed private to `github.com/JISfeir/gw-minimal-match`.
- [ ] **1. Review job q12** (Mon 14) — follow two numbers in `out/report.html` to the code
      that made them and ask what it assumed (day 1); a fresh Codex session with no context
      reads `out/` and tries to break it (homework: second opinion). Also check every
      figure against F1–F4.
      - [x] Figures reviewed → figure rules above.
      - [x] Two numbers followed to code (2026-09-13). `q1_cutoff_floor` (73–99.7 %)
            reproduced to 5 digits with independent code at 5+5, 24+16, 35+35, 50+50;
            pycbc TaylorF2 ends exactly at $f_{\rm ISCO}=1/(6^{3/2}\pi M)$. The fraction is a
            reading of match $=\sqrt{\text{SNR}^2\text{ fraction below }f_c}\times$(match below
            $f_c$), not an additive split, and it measures LAL's cutoff convention, not
            physics. `metric_gradient_field` (97 %) is $1-0.672/24.188$, a coordinate-
            dependent Frobenius rate; the frozen/moving ratio has median 0.089, so the cutoff
            dominates the variation everywhere, and the neighbours of 50+50 (17.4, 12.8)
            show the maximum is not an edge artefact. Common cause: see "Moving ISCO cutoff".
      - [ ] Fresh Codex second opinion.
- [ ] **2. Close the decisions** (Tue 15) — everything under "Decisions for step 2" below,
      written into [[conventions]] and `structure/claims.yaml`. Name each claim's central
      figure and write its F4 sentence now, before any job makes it.
- [ ] **3. Job q345** (launch Tue 15 night → checkpoint Wed 16 → done Thu 17) — questions
      3–5 of `structure/objective.txt`, updated with step 2 and allowed to reuse job q12's
      code as prior work. Add the day-2 check first: ⟨ρ²⟩ = 2 and the FAP tail on
      signal-free Gaussian noise before trusting ρ\*. 2 workers (the covering Monte Carlo
      parallelises); steer with `job resume --say`; try extra rounds (day 4). The objective
      carries F1–F5 verbatim, replaces "recovered-SNR fraction against mismatch" with
      injections into Gaussian noise (measured recovered SNR against $\rho_{\rm opt}\cdot$match,
      with $\langle\rho^2\rangle = \rho_{\rm opt}^2\,\mathrm{match}^2 + 2$), and asks the
      verifier to check each figure against F1–F4, not only its legend.
- [ ] **4. Blind review** (Thu 17–Fri 18) — two fresh reviewers, one per backend, read the
      q345 `out/` with no logs or model names; the claims are what survives (day 3). Each
      reviewer is asked, per figure: could it have looked different if the result were
      wrong?
- [ ] **5. Port into the repo** (Sat 19–Sun 20) — write `tests/test_acceptance.py` by hand,
      pinning the key job numbers with tolerances; `feature` job with `--acceptance-guard`
      builds `src/` (overlap, metric, threshold, bank), `scripts/compute_numbers.py`,
      `scripts/make_figures.py`, under the provenance hook (day 3 gate, day 5). Run
      `compute_numbers.py` twice for a bitwise check; figures with `SOURCE_DATE_EPOCH`; fill
      the README reproducibility categories. Add an F4 field ("how this figure could fail")
      to `.claude/provenance/figures.md` so the gate asks for it; figures rebuilt from
      scratch under F1–F3 (F5).
- [ ] **6. SVD cross-check — optional** (Mon 21–Tue 22) — only if steps 1–5 are done by Sun
      20 night; small `derive` job on the second Codex reset. Otherwise future work in the
      paper. See "Stretch" below. Its covering figure follows F1–F4 like the rest.
- [ ] **7. Paper** (Tue 22–Wed 23) — simplifications first; a controlled measurement with an
      independent analytic check, not a reproduction of Roulet et al.; every number via
      `\dataref` from `data/project_numbers.json`; `draft` job with a Claude verifier
      checking each number against the registry; build with `latexmk`. Each caption says
      what the figure tests and how it could have failed (F4).
- [ ] **8. HTML page** (Wed 23–Thu 24) — move the Owen guide to `page/owen.html`;
      `page/index.html` becomes the project page, same content and numbers as the PDF,
      offline (homework: same content in two formats). Same figures as the PDF, from
      `scripts/make_figures.py` (F5).
- [ ] **9. Publish and reproduce from a clean clone** (Thu 24–Fri 25) — make the repo public;
      a fresh agent in a clone under `/tmp` follows only the README (day 3); fix what
      breaks. The clean clone must regenerate every shipped figure.
- [ ] **10. Final review** (Sat 26) — two fresh reviewers against the registry and
      provenance; `scripts/check_provenance.py` clean; optional token audit. Figure audit:
      every figure in page and paper against F1–F5.
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
- [x] **Mass range split — decided 2026-09-13.** Main results for **$M \le 35\,M_\odot$**
      (component box $[5,50]$, so in practice $m_1 \le 30$); **$35 < M \le 100\,M_\odot$** is
      reported as an extended region, the place where TaylorF2 cut at ISCO stops being a
      usable model. Supersedes the total- vs chirp-mass cap question.
      - *Why 35, cited:* FINDCHIRP (Allen et al. 2012, gr-qc/0509116, Sec. I) — the LSC's
        inspiral **low-mass** search covered $2 < M < 35\,M_\odot$ and a separate
        **high-mass** search $25 < M < 100\,M_\odot$; it notes higher-order corrections to
        post-Newtonian templates matter for heavier black-hole systems. Context: Usman et
        al. 2016 (1508.02357, Sec. 7) — advanced-LIGO PyCBC uses post-Newtonian templates
        only for $M < 4\,M_\odot$, EOB above; Cokelaer 2007 (0706.4437) uses TaylorF2 with
        components 3–30 $M_\odot$ cut at $f_{\rm LSO}$. Owen & Sathyaprakash 1999's
        $M_{\max}=100\,M_\odot$ is a cost estimate, not a validity range. No paper uses 60:
        that value was read off the q12 metric-variation rate by eye and is dropped.
      - *Why a split and not only a cap:* job q12 already computed the high-mass region, and
        its breakdown is a result. Evidence (step-1 review, 2026-09-13): SNR² of IMRPhenomD
        below $f_{\rm ISCO}$ is 98 / 92 / 84 / 76 / 67 / 58 / 49 / 27 % at
        $M$ = 10 / 20 / 30 / 40 / 50 / 60 / 70 / 100 ($q=1$; $q=4$ adds 5–8 points); the
        metric-variation rate stays ≈1.2–1.3 up to $M\approx57$, then 3.3 at $M\approx65$
        and 12.8 at $M\approx86$. Both q12 findings (stage-1 truncation, moving cutoff) trace
        to $f_{\rm ISCO}=44$ Hz at $M=100$.
      - *Framing for page and paper:* the whole v1 range lies above where searches trusted
        post-Newtonian templates alone; say so among the simplifications, first.
      - [ ] Carry into step 2: README scope, [[conventions]] "Mass range" row,
        `structure/claims.yaml` (claims state which region they hold in; the
        "metric near-constant in $(\tau_0,\tau_3)$" rationale is qualified to $M \le 35$),
        and the q345 objective (both regions, reported separately).
- [ ] **ISCO cutoff is an unrecorded convention** (step-1 review, 2026-09-13). Templates end
      at $f_{\rm ISCO}=1/(6^{3/2}\pi M)$ (test-mass Schwarzschild; $v=1/\sqrt6$,
      $Mf\approx0.0217$) only because that is LAL's TaylorF2 default — verified: pycbc
      TaylorF2's last nonzero bin is exactly $f_{\rm ISCO}$. [[conventions]] mentions ISCO only
      to justify 1024 Hz for a 10+10 binary. Add it as a non-negotiable choice with the
      alternatives: cut at 1024 Hz (q12: worsens every same-mass match by 0.009–0.107), a
      fixed $Mf$, IMRPhenomD's own transition frequencies (inspiral phase to $Mf\approx0.018$
      per Khan et al. 2016, arXiv:1508.07253 — **unverified, from memory**; check before
      citing).
- [ ] **Stage-1 example** (from job q12): 73–99.7 % of the TaylorF2-vs-IMRPhenomD mismatch
      is TaylorF2's ISCO truncation, not phase error — still 73 % at 5+5, so the mass split
      does not remove it. Compare against IMRPhenomD truncated at the TaylorF2 cutoff
      instead, or keep and reframe as a truncation example?
- [ ] The explicit **five-stage breakdown**, each stage's **central figure** (with its F4
      sentence), and the per-stage **"verified" checklist**.

## Corrections to carry in (from job q12)

- [ ] [[sources/owen1995_template_metric]]: the eigenvector misprint is on **both** lines of
      Owen Eq. 49 (arXiv v1 numbers it 3.15; TeX lines 1097–1098), not only the first. The
      equation numbers 44–45 and 49 are consistent with arXiv v1's sectioned (3.10),
      (3.11), (3.15). Confirmed by rendering the arXiv PDF, pp. 21–22 (2026-09-13).
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
