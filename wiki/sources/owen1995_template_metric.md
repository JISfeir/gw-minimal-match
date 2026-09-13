# Owen 1995/1996 — template metric and spacing

Primary source: Benjamin J. Owen, *Search templates for gravitational waves from
inspiraling binaries: Choice of template spacing*, arXiv:gr-qc/9511032v1 (submitted
1995), Phys. Rev. D 53, 6749–6761 (1996), DOI 10.1103/PhysRevD.53.6749.

## What was used

- Eqs. 1, 4–6, 10: noise-weighted inner product, SNR, and match.
- Eqs. 11–16: quadratic mismatch metric, minimal match, and hypercubic template count.
- Eqs. 17–18: historical analytic LIGO PSD and normalized noise moments.
- Eqs. 19, 35–38: restricted stationary-phase waveform and 1PN chirp-time coordinates.
- Eqs. 33–34: phase-derivative covariance and projection of coalescence time.
- Eqs. 40–54: two-dimensional metrics, eigendirections, and spacings.
- Secs. III B and III D: mass-domain area, template count, and historical compute cost.

The full pedagogical derivation is in `page/index.html`; the independent deterministic
calculation is `scripts/reproduce_owen1995.py`.

## Corrections needed for reproduction

1. Eqs. 44–45 print `(MM/0.03)^-1`; Eqs. 16 and 43 prove the intended factor is
   `((1-MM)/0.03)^-1`.
2. Eq. 49 contains `e_x1` on both sides of its first line; the right-hand basis vector
   must be `e_tau1`.
3. Reintegrating the printed noise model reproduces metric components to displayed
   precision, but the small printed eigenvalues and spacings are not perfectly internally
   consistent. Keep full precision until the final comparison.

## Scope warning

The PSDs, source-mass prior, 1PN model, square lattice, and compute-cost estimates are
historical. The transferable result is the geometric workflow, not those inputs.
