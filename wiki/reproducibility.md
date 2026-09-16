# Reproducibility

What a fresh clone of this repository does **not** include, and how to rebuild each
missing piece.

## Principle

> Any file or directory that exists locally but is not tracked in git MUST have a
> reproducibility entry on this page. Creating new untracked content includes adding its
> entry here.

`scripts/check_provenance.py` enforces a weaker version of this: it fails if a figure or a
reported number has no provenance record. This page is the human-maintained superset.

## Environment

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

`requirements.txt` is a full `pip freeze` from the reference platform (Linux x86_64,
CPython 3.12). No conda. See [[environment]].

## What is untracked

| Category | Location | Size (typical) | How to rebuild |
|---|---|---|---|
| Large numerical intermediates | `results/*.npz` | — | `python scripts/<the script that writes it>.py` — each documented on its own `wiki/results/` page with the full CLI and wall time |
| The number registry | `data/project_numbers.json` | small — **tracked**, listed here only because it is generated | `python scripts/compute_numbers.py` (its sole writer) |
| Owen 1995 numerical reproduction | `data/owen1995_reproduction.json` | small — **tracked** | `python3 scripts/reproduce_owen1995.py` (standard library only) |
| Figure files | `figures/*.pdf` | — **tracked** | `python scripts/make_figures.py` |
| LaTeX build artifacts | `paper/main.{aux,bbl,blg,log,out,pdf}` | <1 MB | `cd paper && pdflatex main && bibtex main && pdflatex main && pdflatex main` |
| arXiv reading copies | `papers/**` | ~10 MB | `bash scripts/fetch_papers.sh` — needs network, the only thing here that does. Canonical list and checksums: [[sources/papers]]. Added 2026-09-16; this row was missing while the directory existed |
| agent-team jobs | `jobs/**` | large | **not rebuildable** — each job is one run of a bounded agent team and carries its own `out/provenance.json`. Results are ported into the project by hand, and the port is what is tracked. Re-running would produce a different job, not this one |
| Python caches | `__pycache__/`, `.pytest_cache/` | trivial | auto |
| Provenance-gate scratch | `.claude/.session-start`, `.claude/hooks/.attempts` | trivial | auto, per session |

*(rows filled in as content appears; keep the table honest)*

## Determinism notes

- Set `SOURCE_DATE_EPOCH` to a fixed value before `scripts/make_figures.py` for
  byte-identical figure PDFs under a pinned matplotlib.
- Any Monte-Carlo step takes an explicit `--seed`; the seed used for each deposited
  result is recorded on that result's `wiki/results/` page and in its `provenance`
  entry's `choices`.
