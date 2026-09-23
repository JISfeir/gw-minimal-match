# Log

Append-only. What was ingested, decided, corrected, and when. Newest at the bottom.

## 2026-09-04

- Repository scaffolded. Claim and v1 scope fixed (see `README.md`).
- Directory layout and provenance machinery carried over from the course day-5 material
  (`day5/exercise/b` provenance gate + skill + convention files; the "paper as a
  repository" layout; the `build-project-wiki` pattern).
- Environment: local `.venv` (numpy, scipy, matplotlib, sympy, pycbc/lalsuite, astropy),
  pinned in `requirements.txt`. No conda.
- Open: the one-page project spec — mass range, GPS/PSD, waveform family per stage,
  $\mathrm{MM}$ target, central figure per stage, the checklist. In [[todo]].
- One change to the copied `Stop` hook (`.claude/hooks/provenance_gate.py`): its
  `figures_in_tree()` also skips `/paper/`, so `paper/main.pdf` (a build artifact, and
  the deliverable document — not a result figure) does not read as an unrecorded figure.
  Result figures still live in `figures/` and are still checked. Everything else in the
  hook, the skill and the three convention files is verbatim from `day5/exercise/b`.
- `scripts/check_provenance.py` is new here — a repository-wide superset of the hook's
  checks, for a reviewer to run against the whole tree.

## 2026-09-05

- Read Roulet, Dai, Venumadhav, Zackay & Zaldarriaga 2019 (arXiv:1904.01683) in full —
  see [[sources/roulet2019_svd_bank]]. Its SVD-based placement generalizes Owen's
  analytic metric to a data-driven construction with mismatch exactly Euclidean in the
  fitted coordinates.
- Added claim `bank-spacing-cross-check-svd` to `structure/claims.yaml`: reuse the
  stage-2 TaylorF2 waveforms to build that basis restricted to our 2D non-spinning
  range, as a second, independent bank-spacing check alongside Owen — logged as a
  stretch item in [[todo]], after stages 1-4.
- Reworded claim `covering-at-mm097`: it now asks for the *fraction* of injections
  below target match per grid type, not an absolute "none" — square placement is
  expected to dip below target at cell corners where hexagonal does not, and that is a
  reportable result, not a failed check.

## 2026-09-09

- **One-page spec, first four choices settled** — full table with rejected
  alternatives in [[conventions]] under "Non-negotiable choices". In brief:
  - PSD: single detector, analytic `aLIGOZeroDetHighPower` from pycbc (not the day-2
    `.npz`, not a measured O3 curve — the latter is the v2 non-Gaussian item).
  - Bank coordinates: chirp times $(\tau_0, \tau_3)$ at $f_0 = 20\ \mathrm{Hz}$ (not
    $(\mathcal{M}_c,\eta)$ / $(m_1,m_2)$ — the metric is near-constant in chirp times,
    and the others distort most near $\eta = 0.25$ where `volume-loss-rule` measures).
  - Band: $20$–$1024\ \mathrm{Hz}$; segment length derived from the longest TaylorF2
    duration in range, rounded up to a power of two.
  - Threshold: $\rho^\*$ solved from a target FAP with a bank trials factor folded in,
    so the threshold depends on bank density (not a flat $\rho^\* = 8$).
- Still open before stage 1 (in [[todo]]): the target FAP value and the observation
  time behind the trials factor; whether to cap total or chirp mass on top of the
  component-mass box; the explicit five-stage breakdown and each stage's central figure.

## 2026-09-12

- Read Owen's primary source (arXiv:gr-qc/9511032v1) in full and added
  `wiki/sources/owen1995_template_metric.md`.
- Added a beginner-oriented, Spanish, MathJax-rendered guide at `page/index.html`.
- Added `scripts/reproduce_owen1995.py`, a standard-library-only reproduction of the
  noise moments, projected metric, eigensystem, chirp-time domain area, spacings, and
  template counts. Its deterministic output is `data/owen1995_reproduction.json`.
- Documented two clear typographical errors in Owen Eqs. 44–45 and 49, plus small
  numerical inconsistencies exposed by recomputation from the printed PSD.
- Added quantitative and claim-level provenance records for the guide.

## 2026-09-13

- Set the project up to run an `agent-team` job (course day 4) from inside the repo.
  The objective is `structure/objective.txt`: five questions mapped onto the claims in
  `structure/claims.yaml`, in the format of the day-4 prompts. Unlike those, it does
  not fence the team out of this repository — there is no worked answer here to hide,
  and the settled conventions are what the team needs. It may read the repo, treats it
  as prior work to check rather than verified input, and writes only inside its own
  `jobs/<id>/`.
- `jobs/` and `papers/` are git-ignored. `papers/` holds local copies of the six arXiv
  papers the objective lists; the job gets a copy of it.
- Second change to the copied `Stop` hook: `figures_in_tree()` also skips `/jobs/` and
  `/papers/`. A job's figures belong to the job's own registry until ported, and the
  papers are PDFs this project was handed, not figures it produced.
- Added `structure/objective-q12.txt`, a reduced objective with only questions 1–2
  (claims `mismatch-snr-loss`, `metric-vs-owen`), three papers, one HTML deliverable
  and one deliberately failing check. Reason: the machine runs on Claude Pro and
  ChatGPT Plus subscriptions, and a day-4-sized job (30–130M tokens) would exhaust
  their usage windows in its first round. This job doubles as a measurement of what a
  job costs in quota before launching the full five-question objective.
- Ran job `2026-09-13_061522_derive-q12` (06:15–07:17): 2 rounds, 11.0M tokens, 8 % of
  the Codex Plus window for the worker. 24 claims verified, 5 unclear, 4 refuted (the
  refuted ones superseded in round 2). The engine's check reported failure only because
  it calls bare `python`; re-run by hand, provenance and `out/checks.py` pass. Nothing was
  written in the project outside `jobs/`. Findings to carry in are in [[todo]].
- Plan to hand-in settled: eleven steps, 2026-09-14 → 2026-09-27, each tied to a course
  method. It lives in [[todo]].
- Step 1 (review of job q12), started a day early. Figures: Figure 1 is circular (points
  placed at $(\mu,1-\mu)$ and $1/\mathrm{match}$ by construction) and Figure 2 cannot show
  the precision it claims; the objective itself asked for the circular figure. Figure
  rules F1–F5 added to [[todo]] for every step.
- Two numbers followed to code. `q1_cutoff_floor` reproduced to 5 digits with code
  written in this session, independent of the job's (pycbc waveforms and PSD, own inner
  product): floor 0.00832 / 0.12766 / 0.30072 / 0.48049 at 5+5 / 24+16 / 35+35 / 50+50, and
  pycbc TaylorF2 ends exactly at $f_{\rm ISCO}$. `metric_gradient_field` read from the
  verifier's section E and its JSON. Both trace to one cause: TaylorF2's ISCO cutoff sits
  at 44 Hz at $M=100$. Recorded in [[todo]] as one decision for step 2.
- Where the inspiral stage ends had never been decided: the $f_{\rm ISCO}$ cutoff is LAL's
  TaylorF2 default, recorded nowhere in [[conventions]]. Measured the SNR² fraction of
  IMRPhenomD below $f_{\rm ISCO}$ against total mass (98 % at $M=10$ to 27 % at $M=100$).
- **Decision: mass range split.** Main results for $M \le 35\,M_\odot$, following the
  inspiral low-mass search range in FINDCHIRP (Allen et al. 2012); $35 < M \le 100$ reported
  as the region where TaylorF2 cut at ISCO stops being usable. A threshold near 60 had been
  proposed from the q12 metric-variation rate; checked against the papers in `papers/`,
  none uses it (PyCBC 2016: post-Newtonian templates only below $4\,M_\odot$), so it was
  dropped in favour of the cited value. Details and what to carry into step 2 in [[todo]].
- Codex reviewed the objective independently (fresh session, no context). Its citations
  were checked against the files and nearly all of it accepted; it caught a real error in
  claim `covering-at-mm097` (a correctly spaced square lattice does cover — Owen Eq. 3.16).
  Disposition in [[todo]].
- **Step 2 closed early.** `structure/objective-q1b345.txt` written: six parts A–F in
  dependency order, both mass regions apart, figure rules, negative controls that must be
  rejected, one offline report. `structure/claims.yaml` rewritten (two claims corrected, two
  added: `model-error-decomposition`, `detection-threshold`; every claim has a `region`).
  [[conventions]] gains the mismatch symbol $\mu$, $f_{\rm ISCO}$, $N_{\rm eff}$, the ISCO
  cutoff, the mass split, the quadratic-validity criterion (≤ 10 % at
  $\mu_{\rm pred}=1-\mathrm{MM}$, pre-registered) and the equal-MM lattice comparison, plus
  four dated corrections. README scope and named simplifications updated;
  `structure/objective.txt` marked as the master map, not to be run. FAP and observation
  time stay free parameters for now.

## 2026-09-14

- Corrected the threshold model before launching q1bC: qDEF had treated
  $1-\exp(-N_{\rm eff}p)$ as the exact combination of trials. The exact independent-trials
  relation is $1-(1-p)^{N_{\rm eff}}$; the exponential is the rare-tail Poisson approximation.
  qDEF must calibrate $N_{\rm eff}$ from simulated maxima, check stability in segment length
  and threshold, and quantify the approximation error. The separate conversion from FAR to FAP
  is explicitly conditional on a Poisson false-alarm process.
- Second Codex review, of `structure/objective-q1b345.txt`: no large conceptual changes, six
  details and a reservation about the job's size. All accepted; disposition in [[todo]].
- Checking its first point found a real error in [[conventions]]: the metric is not
  near-constant in $(\tau_0,\tau_3)$ even for $M\le35$ — job q12's analytic metric has
  template density varying ×3.0 (×12 in the extended region), only the orientation stable.
  Placement therefore uses the local metric.
- **Decisions (user):**
  - Split into two jobs: `structure/objective-q1bC.txt` (A–C, freezes `out/lib/`,
    `out/data/`, `out/manifest.json`) and `structure/objective-qDEF.txt` (D–F), which gates
    on q1bC being frozen with matching hashes and passing checks, else `[[BLOCKED]]`.
    `objective-q1b345.txt` removed (superseded; in git history).
  - Placement: Cokelaer 2007 with local metric, $\eta=1/4$ projection, physical
    out-of-box templates kept; sensitivities global metric anchored at 12.5+6.25 and 40+20
    $M_\odot$, and discarding non-physical cells; interior and border injections apart.
  - Threshold operating point FAR = 1/(100 yr), $T_{\rm obs}$ = 1 yr, FAP
    $=1-e^{-0.01}=0.0099502$ exactly; $\nu_{\rm eff}$ from segments, extrapolated;
    FAR = 1/yr as a permissive sensitivity only; 5σ as global probability $2.8665\times10^{-7}$.
  - Part A at the deterministic lag (Rice); global fitting-factor search; $V_{\rm eff}$ as
    the quantity to maximise.
- Verified while writing: the FAR quote is in 1908.11170 Sec. 8.5; agent-team lowercases job
  names (`--name q1bC` → `…_derive-q1bc`), so qDEF's gate matches the lowercase id; `job
  freeze` sets `"status": "frozen"`.

## 2026-09-16

- **Framing question answered: what is the bank density traded against?** Asked whether
  minimising template count still matters for computational cost. It does not, in this mass
  range. Owen & Sathyaprakash 1999 scale power as $m_{\rm min}^{-8/3}$ from
  $m_{\rm min}=0.2\,M_\odot$; our $5\,M_\odot$ divides their 780 Gflops by $\approx5.4\times10^3$,
  giving $\sim0.15$ Gflops. Corroborated without scaling by Cokelaer 2007 Table IV
  (2422 / 1764 templates for 3–30 $M_\odot$), Roulet et al. 2019 Table I (46 templates for
  $M>40$ against 316 262 for the whole 1–100 $M_\odot$ bank) and Usman et al. 2016 Table 1
  (bank generation 4.7 CPU-days against 515.5 for filtering + $\chi^2$, i.e. 0.9 %).
  Recorded as a dated correction in [[conventions]]: the price of a finer bank here is the
  threshold through the trials factor, not flops — which is what part F already optimises,
  but was nowhere stated as a decision. The $\rm README$ still asks "how dense" without
  naming the cost; worth a line when the paper is written.
- **Part F is not virgin territory.** Croce, Demma, Longo, Marano, Matta, Pierro & Pinto
  2004 (gr-qc/0404096) is its direct predecessor: its Sec. I question (ii) is our
  `volume-loss-rule` verbatim, and its Sec. V reports that using the correlated whole-bank
  no-signal distribution for the threshold gives "a sizeable increase ($\ge 5\%$) in the
  detectable fraction ... over the naive $\propto\Gamma^3$ estimate", plus a knee in
  $\Gamma$ vs $N$ beyond which more templates buy nothing. Both are now pre-registered
  expectations on the claim. Keppel 2013 (arXiv:1303.2005, Secs. III–IV) covers the other
  axis, MM at fixed computational cost, and is cited to mark the axis we do *not* take.
  `volume-loss-rule` reworded: a measurement of a known trade-off for this configuration,
  with the closed loop, the calibrated $\nu_{\rm eff}$ and the separated losses as what is
  ours. New `prior_work` field on the claim — `check_provenance.py` tolerates extra keys.
- **Part D.4 had too weak a control.** It compared the hexagonal/square ratio only against
  the constant-metric 0.770. Cokelaer 2007 Table III + Sec. III.B already *measures* 39.5 %
  mean reduction (ratio $\approx0.60$) and attributes the excess over the geometric 29 % to
  the evolution of the metric. Both references are now pre-registered in
  `structure/objective-qDEF.txt` and in claim `covering-at-mm097`, with the reading fixed in
  advance: landing near 0.770 means the local metric is not in play and is a bug to chase,
  not a result.
- **`papers/` had no reproducibility entry**, in breach of the rule stated at the top of
  [[reproducibility]], and `.gitignore` pointed at `structure/objective.txt` — a file
  carrying a `NOT TO BE RUN AS IS` header — as the list of what belongs there. Fixed:
  new [[sources/papers]] is the canonical table (arXiv id, file, what each is used for,
  checksums, and the rule that a cited paper must be present because jobs run offline),
  new `scripts/fetch_papers.sh` rebuilds the directory, and [[reproducibility]] gained rows
  for both `papers/` and `jobs/` — the latter marked explicitly **not rebuildable**.
- Three papers added to `papers/`: gr-qc/0404096 (Croce 2004, v2), 1303.2005 (Keppel 2013,
  v1) and 2211.16674 (Sakon et al. 2023, v6 — the O4 bank: $1.8\times10^6$ templates, 4-D
  aligned spin, binary-tree placement, no analytic metric; context only, never evidence).
- Not done: no number in this session came from code, so nothing was written to
  `provenance/`. The $\sim0.15$ Gflops and the $\rho^*$ sensitivity sketch
  ($\rm MM$ 0.97 → 0.99 costing $\approx-4.5\%$ of volume through $\rho^*$ against
  $\approx+3.1\%$ recovered by covering) are back-of-envelope only and are **not** project
  numbers. If either enters the report it must be computed and registered first.

## 2026-09-19

- **Job q1bC, rounds 3 and 4** (resumed 2026-09-16 and 2026-09-19). Both stopped early on the
  spend tripwire, not on failure. Job total after round 4: 40.6M tokens, $23.71. Budget raised
  by hand in `spec.json`, 20M → 45M → 55M; no other key touched.
- **Round 3 — Part B, partial.** The worker call ended `ok=false` with its batch children still
  running: 9 of 28 signals delivered, the nine lightest ($M=10$–$29\,M_\odot$), all main. The
  r03 verifier reproduced all nine independently and added four findings that now bind the
  rest of the project:
  - **Common support must be an explicit mask on the actual last nonzero bin.** PyCBC's
    IMRPhenomD `f_final = f_ISCO` ends one bin early at all 37 points tested; at $(50,50)$
    $\mu_{\rm common}$ moves 0.00310 → 0.00385, a 24 % change. **Carry into [[conventions]]
    when q1bC is ported.**
  - $\lfloor f_{\rm ISCO}/\Delta f\rfloor$ fails at exact-integer edges: at
    $(48.971084, 5.189652)$ the ratio is 2597.9999999999995 and LAL keeps bin 2598.
  - **Cutoff sawtooth.** Both objectives jump when the template's last bin changes: 1.9e-6 to
    2.7e-5 (main), 3.2e-5 to 2.9e-4 (extended). Nothing may be quoted finer, and Nelder–Mead
    stalls on the jumps — the verifier's own extended numbers did not converge for this reason.
  - **A gate that cannot fail is not a check.** The "exhaustive candidate identity" gate passed
    692,973 pairs while testing only round-off, because the full and common correlation arrays
    are exactly proportional. Same failure shape as round 1's vacuous check. This is now a
    standing requirement: every gate states the physical circumstance that makes it fail.
  - Negative result worth keeping: the global fitting-factor search **confirms q12's local one**
    to within 7.8e-6 at all nine signals. The worker's 10-digit values are lower bounds, not
    converged maxima.
- **Round 4 — Part C, complete and independently verified.** `checks.py`: 57 PASS, 8 FAIL, exit
  1; all twelve Part C gates pass, and the eight failures are the unfinished Part B signals plus
  the integration gate. The r04 verifier rebuilt the analytic metric by a different route —
  differentiating LAL's own Fourier phase numerically rather than re-reading PN coefficients —
  and reproduced `out/lib/metric.py` at all 60 mass points to ≤ 9.2e-8; the 28 q12 rows are
  bit-identical. q12's headline "0.74 %" is pinned: 0.007386, set by $(50,50)$.
  - **Pre-registered criterion, the answer.** The quadratic predictor meets the 10 % criterion
    at $\mu_{\rm pred}=0.03$ in both regions (main 3.0–8.7 %, extended 3.4–9.0 %) with about one
    percentage point of margin, and **fails at $\mu_{\rm pred}=0.05$** (19/21 main, 17/39
    extended). Physical templates fail 16/21 main and 39/39 extended at MM = 0.97.
    **Consequence for qDEF: any MM curve below about 0.97 rests on a predictor outside its
    validated range.** Say so where those curves are drawn.
  - **Why the physical case fails, measured not asserted.** Exact decomposition
    $\mu_{\rm phys} = (1-\sqrt F) + \sqrt F\,\mu_{\rm common}$: the lost-support term is 14–78 %
    of $\mu_{\rm phys}$ (median 60 %). The excess is the moving hard cutoff, not the phase metric.
  - **Signed asymmetry, not yet in any deliverable.** The fixed-support error is always
    conservative ($\mu_{\rm exact} < \mu_{\rm pred}$); the dangerous under-prediction is bounded
    by 1.1 % (main) and 4.3 % (extended) at MM = 0.97. More useful to qDEF than the two-sided
    criterion.
  - **Two gates weaker than their stated failure mode**, found by fault injection: the Part C
    "fresh worst-direction" gate has a NaN hole (Python's built-in `max()` silently skips a NaN
    that is not first, so a stale extremum angle still prints residual 0 and exits 0), and
    "exported metric grid" regenerates only 5 of 60 rows. Neither changes a result; both must be
    fixed before the manifest.
- **CORRECTION — the Part B scope cut was never a human decision.** The round-4 steering message
  told the team that Part B "closes as main-region-only", and `reports/r04-verifier.md` records
  it as *"deliberately descoped by the human"*. It was proposed by the assistant in session and
  written into the instruction without the decision being put to, or taken by, the human. **The
  attribution is wrong and the cut is reverted: the extended region is back in Part B's scope.**
  It was also the wrong call on the merits — the mass range was split at 35 $M_\odot$ *because*
  TaylorF2 cut at ISCO stops being usable above it, the r03 verifier measured the identity gap
  at up to 2.3e-2 in extended against 2.64e-4 in main, and Part C already covers 39 extended
  mass points, so a main-only Part B cannot report the two regions apart as claim
  `model-error-decomposition` requires. Recorded here because the job's own reports will keep
  the wrong attribution; this page is the dated record.
- **Finishing Part B is cheap if the loop is inverted.** Round 3 spent 8.2M tokens on nine
  signals iterating signal by signal (~1010–1045 s each). The r03 verifier did all 28 signals
  per template in one pass: 52,403 templates in 17 min on 11 processes. The remaining 19 signals
  are tens of minutes of compute; the round-3 cost was a loop structure and a lost batch, not
  the physics. Instruction prepared in `jobs/q1bc-finish-say.txt`.
- **Step 6 (SVD cross-check) cut**, per the plan's own "if time slips, step 6 is cut first".
  q1bC is four days behind the plan and qDEF has not started. See [[todo]].

## 2026-09-21

- **Job q1bC FROZEN.** 8 rounds, 73.5M tokens, $50.42. `out/checks.py`: **76 PASS, 0 FAIL,
  exit 0**; `out/manifest.json` written last, as the objective required. qDEF's GATE was
  simulated by hand before freezing and passes every step: `status` now `frozen`; 581/581
  manifest sha256 recomputed and matching, 0 missing; the recorded check command re-run from
  the job directory exits 0 and its merged stdout+stderr hashes to the recorded
  `7b73a664…6475`. *(First attempt at that last check reported a mismatch — my error: the
  manifest declares `check_output_capture: "stdout and stderr merged in emitted order"` and I
  captured stdout only, losing a PyCBC pkg-config warning line.)*
- **Rounds 7–8.** Round 7 did the integration and wrote the manifest. **Round 8's worker
  produced nothing while reporting that it had corrected two numbers and added regressions** —
  the verifier checked the filesystem rather than the report: *"refuted by the filesystem:
  none of it happened."* Worth remembering as the failure mode a report-reading review misses.
- **The two weak Part C gates are genuinely repaired**, closed by the r08 verifier's own
  injections rather than by inheriting round 7's: a metric non-spot row scaled 1 %, and
  extremum angles shifted by **1e-7** at the boundary cells (35,24) and (5,5) — the case that
  previously slipped through Python's builtin `max()` skipping NaN — all now FAIL, with a
  clean control still passing.
- **Three defects survive in the frozen package because no gate reads them.** Recorded rather
  than patched: patching would mean reopening a job whose worker just failed at exactly that
  task, and the package's value is that it verifies byte for byte.
  1. **A false bound.** The weighted common term range is published as 0.021–0.030; it is
     **0.020–0.030**. Counterexample re-derived from waveforms: extended cell (40,20),
     $\sqrt F\,\mu_{\rm common} = 0.0200600$ with $F = 0.908995$, $\mu_{\rm common} = 0.021040$,
     $\mu_{\rm phys} = 0.066648$ — so 69.9 % of that cell's mismatch is lost support and 30.1 %
     is the common term. The 0.021 came from a round-4 rounding that a later re-derivation
     contradicted. **This one is load-bearing**: the argument of `metric-vs-owen` is that
     $\sqrt F\,\mu_{\rm common}$ stays pinned near $\mu_{\rm pred}=0.03$, which is what shows the
     excess of $\mu_{\rm phys}$ is the moving cutoff and not a defective phase metric. It also
     sits in `out/data/qdef_guidance.json`, **which qDEF reads**.
  2. **A false sentence.** "The fixed-support worst error is conservative in each cell" fails
     at $\mu_{\rm pred}=0.01$: extended (30,24) is +1.458 % on the under-prediction side. True
     at the tested radii 0.03 and 0.05 only, and nothing between 0.01 and 0.03 was measured.
  3. **Two dangling docstring pointers** from `out/lib/` into `work/`, which qDEF may not read.
- **Errata pre-registered in `structure/objective-qDEF.txt`** rather than patched into the
  frozen package, so the consumer carries the correction and the package stays verifiable.
  Fixes for the port are in [[todo]] step 5.
- **New section in the qDEF objective: "WHAT q1bC ESTABLISHED".** The objective told the team
  to import q1bC's `out/lib/` and read its `out/data/` but never said what q1bC had actually
  found; the team would have had to reverse-engineer it. It now carries the single-sample
  statistic for part E, the fitting-factor result and its quoting precision for part F, and
  for part D the metric's validity: **the pre-registered 10 % criterion is met at MM = 0.97
  (worst 8.74 % main, 8.98 % extended, 1.019 pp of margin) and FAILS at MM = 0.95 (19/21 main,
  17/39 extended)**, with the instruction that every curve and optimum below about MM = 0.97
  carries that caveat and is reported as provisional. Also the signed asymmetry (dangerous
  under-prediction bounded by 1.1 % main / 4.3 % extended), the `boundary_limited` flag that
  must not be averaged over silently, the actual-last-bin cutoff rule, and what q1bC did *not*
  establish.
- **agent-team harness fixed** (separate repo, `/home/juan/agent-team`). Of this job's 18 codex
  calls, 11 failed, every one reported as `Reading additional input from stdin...` — which
  turns out to be an informational line codex prints on *successful* runs too. Cause: codex
  reports failures as `{"type":"error"}` events **on stdout**, while `_stream_run` discarded the
  exit code and `_finalize` took the error from stderr, so every real cause was thrown away
  and the only possible response was to relaunch the round. A second bug: `_codex_last_message`
  did not understand codex 0.154's `item.completed` envelope, so partial output could never be
  salvaged from a killed call — which is how round 3 lost 19 signals. Both fixed and tested
  end to end; the harness suite is 75/76 with the one failure pre-existing. **Rounds 7–8 then
  saw 1 failure in 7 calls against 11 in 18 before**, after the user reported Codex quota had
  reset — consistent with quota having been the underlying cause all along, though the
  original error text is gone for good, which was the bug.

## 2026-09-21 (later) — qDEF launched, and a correction to this project's own spec

- **Job qDEF created and run to its checkpoint**: `2026-09-21_223117_derive-qdef`, 2 rounds,
  5.37M tokens, $6.32. Staffing: 2 workers on codex `gpt-5.6-sol` at high, lead and writer on
  `gpt-6-astra`, verifier on Claude at high. An acceptance gate (`tests/test_qdef_acceptance.py`,
  hash-pinned) asserts q1bC's frozen package still verifies and qDEF's deliverable is real; it
  was red before the run, as a gate must be.
- **The GATE on q1bC passed and was recorded by the team**: `reports/r01-gate-result.json`,
  595 files hashed, `passed: true`, output sha256 `7b73a664…6475`, manifest sha256 recorded.
  The freeze machinery works end to end.
- **Every codex call failed: Codex quota exhausted.** The error is now explicit in the log —
  *"You've hit your usage limit … try again at Sep 22nd, 2026 3:31 AM"* — because of the
  harness fix on 2026-09-20. Before it, this read "Reading additional input from stdin…" and
  was undiagnosable. **This confirms the quota hypothesis for q1bC's 11 failed calls.** No
  Part D, E or F work exists yet; the $6.32 is entirely the Claude verifier, which used both
  rounds to audit inputs instead.
- **CORRECTION — the D.4 pre-registered discriminator was wrong, and it was mine.** On
  2026-09-16 this project pre-registered "about 0.60, what Cokelaer 2007 MEASURES" as the
  local-metric reference for the hexagonal/square template-count ratio. **Cokelaer's Table III
  tabulates $N_{\rm sq}/N_{\rm hex}-1$, not $1-N_{\rm hex}/N_{\rm sq}$**: recomputing all 20
  cells from his Tables I and II, the first convention reproduces Table III to **0.48 pp** and
  the second is off by up to **17.05 pp**. His Sec. III.B "expected 29 %" is likewise
  $3\sqrt3/4-1=0.2990$ in the inverted convention, not $1-0.770=0.230$. The direct ratio
  Cokelaer actually measures is **0.7191 mean, range [0.6605, 0.7866]**; from Table III's
  39.5 % average, $1/1.395 = 0.7168$.
  **Consequence, and it is why this mattered:** the ideal 0.770 and Cokelaer's measured 0.72
  are *close together* — metric evolution buys about 5 points of ratio, not 17. The spec as
  written would have sent a correct local-metric implementation chasing a nonexistent bug, or
  invited tuning until it produced a number that does not exist in the literature. Found by
  qDEF's r02 verifier reading the paper; independently recomputed here before accepting it.
  Corrected in `structure/objective-qDEF.txt` (D.4), `structure/claims.yaml`
  (`covering-at-mm097`) and [[sources/papers]]. The discriminator is now: ideal 0.770,
  Cokelaer-measured 0.717–0.719, finding = outside roughly [0.65, 0.79].
- **The "24 % at (50,50)" f_final figure is disputed and must not be quoted.** q1bC's r03
  verifier recorded $\mu_{\rm common}$ moving 0.00310 → 0.00385 there; qDEF's r02 verifier
  measured the one-bin-early effect against the frozen physical endpoints and got at most
  1.3 % in any reading. They may be measuring different configurations. Both recorded, per the
  project's rule on disagreeing sources; the operative rule (actual last nonzero bin, never
  `floor`, never `f_final`) is confirmed by both and unaffected.
- **The cutoff knife-edge needs its 17-digit masses.** The spec printed
  $(48.971084, 5.189652)$, at which the effect does not reproduce ($f_{\rm ISCO}/\Delta f =
  2598.0000039$). The real pair is $(48.971084127318335, 5.189651954428283)$. Fixed.
- **Also worth recording, because it is the failure mode this project exists to catch:** in
  first attempting to check the Cokelaer claim, the assistant transcribed two of Table I's
  four rows from memory rather than from the PDF, and produced a confident refutation of the
  verifier that was itself wrong. Caught only because the arithmetic disagreed with Table III
  under *both* conventions. The same shape as q1bC's round-8 worker reporting work it had not
  done. Numbers get read from the source, every time, including by the reviewer.

## 2026-09-23

- **The real blocker in qDEF was a missing file, not the Codex quota.** The project's
  `.codex/hooks.json` runs `python3 .claude/hooks/provenance_gate.py` by a RELATIVE path.
  Codex finds that config by walking up from the job directory but runs it with the job as
  cwd, so it needs a job-local target. Job q1bC had one — a deliberate no-op shim written in
  its day, docstring: *"provide a successful job-local target instead of letting every Stop
  event feed an error back into the model indefinitely"*. **qDEF had no `.claude` at all**, so
  every Stop event returned an error and the lead answered `[[BLOCKED]]` for three rounds
  while we chased quota. Shim copied in; `jobs/qdef-resume.sh` now installs it if absent.
  Rounds 1–5 of qDEF (≈21M tokens, no science) are largely attributable to this.
- **Round 6 then ran end to end** — every codex call succeeded — and delivered D-1: four banks
  at MM = 0.97, main and extended, hexagonal and square, deterministic (two re-runs reproduce
  the delivered files byte for byte). Counts 1049 / 1069 / 342 / 403.
- **And the r06 verifier refuted it, three ways. The banks are not usable.**
  1. **The main banks do not cover at MM = 0.97.** 1500 injections per region, seed 20260923:
     the fraction with $\mu > 0.03$ is **1.93 %** (hexagonal) and **7.87 %** (square) against
     an ideal of 0. Ten holes per bank re-checked with real TaylorF2 waveform matches confirm
     9/10 and 6/10, so the corrected figures are ~1.7 % and ~4.7 % — **real holes, not a
     quadratic-predictor artefact**. They cluster on the $\eta = 1/4$ side (29/29 hexagonal,
     83/118 square), which points at the projection rule: putting daughters on the line
     leaves a gap just inside it. This is the same 2.6 %/7.4 % shortfall r04/r05 left open.
  2. **The extended banks are contaminated by a degenerate-metric artefact.** Templates run
     away to $(m_1, m_2) = (215.95, 0.0695)\,M_\odot$, far outside the $[5,50]$ box. There
     $f_{\rm ISCO} = 20.34$ Hz leaves **12 support bins**, the metric has condition number
     $1.8\times10^6$, and the fertility test returns 0.000401 against a boundary point **143 s
     away** in chirp time. The real TaylorF2 match of such a template against (50,5), (30,5),
     (50,50), (17.5,17.5) and (40,20) is **0.054–0.092**: it covers nothing. Contamination is
     41 % of the hexagonal bank and 26 % of the square one, so **any D-2 hexagonal/square
     ratio taken from these extended banks is invalid**. The growth stops only where
     `analytic_metric` raises "insufficient support" — an implementation accident, not a
     physical boundary. The main banks are clean by comparison ($m_2^{\min}$ 4.23/3.98,
     $m_1^{\max}$ 32.7/32.8).
  3. **The delivered check cannot fail on a bank defect** — the third time this shape has
     appeared in this project. Its negative controls feed synthetic arrays to helper
     functions; two of the three are never called on a delivered bank, and the spacing check
     tests a metadata scalar rather than measured inter-template distances. Injected defects:
     deleting every 5th main-square template (1069 → 855, a 20 % covering failure) → **PASS,
     exit 0**; replacing the main-hexagonal bank with the square lattice's rows → **PASS,
     exit 0**.
- **This is a result, not just a failure**, and it belongs in the paper: placing with a local
  metric in the extended region breaks down because the metric goes degenerate where TaylorF2
  loses support, and the fertility criterion stops being numerically meaningful before any
  physical boundary is reached.
- **A prediction of mine was wrong.** Trimming the worker's mandated reading from ~50k to ~12k
  tokens was predicted here to cut a worker call from ~5M to ~1M. Round 6's workers cost
  **3.68M and 4.58M**. The context was not the lever; the hook was. Caveat in both directions:
  the token counter now includes `reasoning_output_tokens`, which it previously dropped, so
  these figures are not directly comparable with the earlier ones.
- **Decision: stop running qDEF as a team job.** Next step is to rework D-1 interactively —
  the $\eta = 1/4$ projection rule and the fertility test are the two defects — and then send
  the result to an independent blind review, which is step 4 of the plan. The team's
  verification is what caught every error in this project, including two of the assistant's;
  what is being dropped is the round loop, not the check.
- Harness fixes committed in `/home/juan/agent-team` as `0b4de7d`: codex's real error is now
  reported instead of its harmless stdin notice, the `item.completed` envelope is understood
  so partial output can be salvaged, and `reasoning_output_tokens` is counted.
