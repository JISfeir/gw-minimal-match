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
