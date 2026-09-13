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
