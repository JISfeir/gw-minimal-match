# Final figure audit — 2026-09-28

This is the fresh-review disposition for the six figures shipped by
`scripts/make_figures.py`.  “Conditional” means that the visual is valid only for the
model named in its axes and caption; it is not a direct waveform or operating-tail
measurement.  A conditional result may ship when that boundary is local and explicit.

| Figure | F1 measurement vs prediction | F2 claimed precision visible | F3 dimensions explicit | F4 falsification sentence | F5 single source |
|---|---|---|---|---|---|
| `d_covering_cumulative` | Conditional: sampled best match is evaluated with the quadratic metric, not waveform overlaps | Pass: log ordinate exposes rare failures | Pass: region, lattice and interior/border subsets are explicit | Pass: any nonzero CDF left of MM = 0.97 refutes sampled covering | Pass |
| `d_counts_and_ratio` | Pass: delivered bank counts are compared with geometric and published references | Pass: the ratio has its own resolved panel | Pass: region and lattice are explicit | Pass: one MM-independent line near the ideal would refute the boundary/implementation dependence | Pass |
| `d_mismatch_map_main_hex` | Conditional: grid and adaptive witness use the analytic quadratic metric | Pass after revision: the colour scale is the residual `mu - 0.03` | Pass: both component masses, with units, are axes | Pass: a positive residual is the visible failure condition | Pass |
| `e_trials_measured_vs_naive` | Pass: counts inferred from simulated-noise maxima are compared with the naive prediction | Pass after revision: per-bank errors and paired-bootstrap exponent intervals are visible | Pass: region and lattice remain separate | Pass: independence or proportional growth has a stated visual pattern | Pass |
| `f_volume_losses` | Conditional: population points are quadratic-metric predictions under the declared injection measure | Pass after revision: bootstrap bars are drawn and an inset resolves the exact/linear difference | Pass: the population reduction is declared; region and lattice remain explicit | Pass: population points on the worst-case curve would refute the conclusion | Pass |
| `f_veff_vs_mm` | Conditional: a derived proxy combines metric-predicted matches with two trials scenarios | Conditional but acceptable: dominant trials/tail uncertainty is unquantified, so precision-style bars were removed and the plot is explicitly a scenario comparison | Pass: region, lattice and trials scenario are explicit | Pass: agreement of scenarios or a stable interior peak would refute the stated conclusions | Pass |

## Portfolio boundary

The earlier q1bC package contains the central A–C diagnostics for the single-sample
statistic, waveform-family mismatch decomposition and quadratic-metric validation.  They
are not among these six shipped figures.  Copying their job images would violate F5, and
their full numerical inputs are not part of a clean clone.  The page-limited paper therefore
uses their verified identities/results in prose and declares the frozen-package boundary;
the current clean-clone figure portfolio covers D–F.  A future expansion may port A–C data
and rebuild those visuals in `scripts/make_figures.py`, but this review does not pretend
that they are present now.

## Enforcement added by this review

- Every PDF and PNG record in `provenance/claims.yaml` now has a non-empty
  `how_this_could_fail` field.
- `scripts/check_provenance.py` and `tests/test_acceptance.py` enforce that field.
- The four abbreviated PDF captions now carry their own falsification condition; the HTML
  continues to use the complete generated captions.
- Only `scripts/make_figures.py` writes shipped figures, and every displayed asset is
  regenerated from tracked `data/` inputs.
