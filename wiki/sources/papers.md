# Papers — the canonical list

`papers/` holds local reading copies of the arXiv sources this project cites. It is
**git-ignored**, so a fresh clone has none of it. This page is the canonical list; the
rebuild command is `bash scripts/fetch_papers.sh`, and the reproducibility entry is in
[[reproducibility]].

Added 2026-09-16. Before this, the only list lived in `structure/objective.txt`, which
carries a `NOT TO BE RUN AS IS` header — so the canonical list of papers was inside a
file marked obsolete, and `papers/` had no reproducibility entry at all despite the rule
on that page. Both fixed here.

## What is in it

| arXiv | dir | file | short | what it is used for |
|---|---|---|---|---|
| gr-qc/9511032 | `gr-qc-9511032/` | `owen1995.pdf` + `9511032.tex`, `fig*.ps` | Owen 1996 | the metric, minimal match, Eq. 3.16 square spacing, template counting. **The `.tex` matters**: claims and notes use arXiv v1 equation numbering, which the published PDF does not show |
| gr-qc/9808076 | `gr-qc-9808076/` | `owen-sathyaprakash-1999.pdf` | Owen & Sathyaprakash 1999 | placement in chirp times; the computational-cost scalings $m_{\rm min}^{-8/3}$ (power) and $m_{\rm min}^{-13/3}$ (storage) |
| gr-qc/0404096 | `gr-qc-0404096/` | `croce-2004.pdf` | Croce et al. 2004 | **the direct predecessor of part F**: the whole-bank no-signal distribution, and whether $1-\Gamma^3$ survives it. Sec. I questions (i)–(ii), Sec. V conclusions |
| gr-qc/0509116 | `gr-qc-0509116/` | `allen-findchirp.pdf` | Allen et al. 2012 | FINDCHIRP: the statistic, its distribution in Gaussian noise, the $2<M<35\,M_\odot$ low-mass range |
| 0706.4437 | `0706.4437/` | `cokelaer-2007.pdf` | Cokelaer 2007 | **the placement method used here**: local metric, cell-by-cell growth, boundary treatment. Table III and Sec. III.B: 39.5 % mean hexagonal/square size reduction against the 29 % constant-metric prediction. Table IV: 2422 square / 1764 hexagonal for $3$–$30\,M_\odot$ at MM $=0.95$ |
| 1303.2005 | `1303.2005/` | `keppel-2013.pdf` | Keppel 2013 | minimal match optimised at fixed computational cost, Secs. III–IV. The axis part F does **not** take |
| 1508.02357 | `1508.02357/` | `usman-2016.pdf` | Usman et al. 2016 | the PyCBC search. Table 1: bank generation 4.7 CPU-days against 515.5 for matched filtering + $\chi^2$ |
| 1904.01683 | `1904.01683/` | `roulet-2019.pdf` | Roulet et al. 2019 | SVD placement; Fig. 5 covering check; Table I bank sizes (316 262 total; 225 for $M\in(20,40)$, 46 for $M>40$) |
| 2211.16674 | `2211.16674/` | `sakon-2023.pdf` | Sakon et al. 2023 | **context only, never evidence**: the O4 bank — $1.8\times10^6$ templates, 4-D aligned spin, binary-tree ("manifold") placement, no analytic metric. What this project idealises away |

## Checksums

`bash scripts/fetch_papers.sh` prints these; `--check` verifies presence without fetching.
arXiv replaces PDFs on re-render, so treat a mismatch as "re-rendered upstream", not as
corruption — check the version line on page 1 before worrying.

```
54eb27621413991b  0706.4437/cokelaer-2007.pdf
e8179eb57943f584  1303.2005/keppel-2013.pdf
5c50996fd09f0f2e  1508.02357/usman-2016.pdf
12da9254b9bfbf59  1904.01683/roulet-2019.pdf
48f84ffd5413c6d7  2211.16674/sakon-2023.pdf
fba0a24ab2c5bd96  gr-qc-0404096/croce-2004.pdf
79284a4a750df285  gr-qc-0509116/allen-findchirp.pdf
88a89bf04edfdad2  gr-qc-9511032/9511032.tex
e41bf727fa36a2aa  gr-qc-9511032/fig1.ps
91eee9529f4047ec  gr-qc-9511032/fig2.ps
a3f194270ea45437  gr-qc-9511032/fig3.ps
8445d8c3b11105f4  gr-qc-9511032/owen1995.pdf
60d04b921428a7e6  gr-qc-9808076/owen-sathyaprakash-1999.pdf
```

Recorded versions as fetched: Croce `v2 24 Apr 2004`, Keppel `v1 8 Mar 2013`,
Sakon `v6 21 Dec 2023`.

## Rules

- A paper cited in `structure/claims.yaml` or in a job objective **must** be listed here and
  present in `papers/`. Jobs run with no network: a citation the team cannot open is a
  citation it cannot check, which the DISCIPLINE section of every objective forbids.
- Adding a paper means three edits: `scripts/fetch_papers.sh`, this table, and the
  `SOURCES` block of whichever objective needs it.
- Reading notes live beside this file, one page per paper — see
  [[sources/owen1995_template_metric]] and [[sources/roulet2019_svd_bank]].
