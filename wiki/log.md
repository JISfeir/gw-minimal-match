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
