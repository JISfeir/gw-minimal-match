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
