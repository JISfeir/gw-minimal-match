# Minimal-match project wiki — Index

Read this first. Every page is reachable from here. Pages link Obsidian-style: `[[page]]`.

**This wiki is DERIVED.** Everything in it restates something that exists elsewhere —
code, a paper, a raw source. If a page ever contradicts the code or a source, the page is
wrong and gets corrected. When in doubt about a fact, read the source, not the wiki.

## Utility

- [[conventions]] — the notation contract: what each symbol means *here*, sign choices, every non-negotiable
- [[environment]] — how to build and run (venv + `requirements.txt`; no conda)
- [[reproducibility]] — what is not tracked in git and the command that rebuilds each piece
- [[log]] — append-only: what was ingested, decided, corrected, and when
- [[todo]] — what is unresolved; a number that could not be found goes here

## Concepts

One page per idea, each canonical for its topic. *(to be filled)*

- `concepts/` — match & overlap, the parameter-space metric, minimal match, the covering problem, fitting factor, sensitive volume, the analytic Gaussian threshold, trials factor

## Sources

One page per thing read.

- [[sources/papers]] — **the canonical list of `papers/`**: every arXiv source, why it is
  there, its checksum, and the rule for adding one. `papers/` is git-ignored; rebuild with
  `bash scripts/fetch_papers.sh`
- [[sources/owen1995_template_metric]] — the primary source for matched-filter mismatch,
  the parameter-space metric, minimal match, and the 1PN worked example
- [[sources/roulet2019_svd_bank]] — the SVD-based placement algorithm; our second,
  independent bank-spacing cross-check
- `sources/` — still to write pages for: Owen & Sathyaprakash 1999; Cokelaer 2007;
  Usman et al. 2016; Croce et al. 2004; Keppel 2013

## Code

One page per module or script. *(to be filled)*

- `code/` — `src/` modules and `scripts/`

## Results

One page per computed result, with the command that made it. *(to be filled)*

## Figures

One page per figure: what is on the axes, what to take from it, what produced it. *(to be filled)*

## The argument

The claim skeleton is `structure/claims.yaml` at the repo root, not here — this wiki is
notes, that file is a deliverable.

## Human-facing notes

- `page/index.html` — beginner-oriented guide to understanding and reproducing Owen
  (1995), with rendered LaTeX and a deterministic reference calculation
