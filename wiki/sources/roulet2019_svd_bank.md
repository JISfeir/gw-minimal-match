# Roulet, Dai, Venumadhav, Zackay & Zaldarriaga 2019 — SVD template placement

**arXiv:1904.01683**, *"Template Bank for Compact Binary Coalescence Searches in
Gravitational Wave Data: A General Geometric Placement Algorithm."* Read in full
(PDF extracted 2026-09-05) for this project.

## What it does

Generalizes [[../conventions|Owen's metric-based placement]] (Owen 1996) from an
analytic, locally-linearized metric to a **data-driven, globally-Euclidean**
construction:

1. Sample many physical waveforms across the target parameter range.
2. Group by similar amplitude profile; take the **SVD of the unwrapped phase** across
   the group to get an orthonormal basis of phase functions.
3. The leading few components span a linear space of coefficients $c_\alpha$ in which
   the mismatch distance is Euclidean **by construction**, not just to leading order at
   one point:
   $$d^2_{c,\,c+\delta c} \approx \tfrac12 \sum_{\alpha} \delta c_\alpha^2 + O(\delta c^3) \qquad \text{(their Eq. 15)}$$
4. Place a **regular grid directly in $c$-space**, spacing $\Delta c \lesssim 1$ set by
   the target mismatch. No metric tensor, no derivatives of the waveform phase needed by
   hand — works for any frequency-domain waveform model.

## Why it matters here

Owen's metric is analytic but local (a Taylor expansion) and tied to the PN phasing.
This method needs no analytic metric at all — the "flat coordinates" are found
numerically from the same waveforms we already generate for the match map. That makes
it a **second, independent way to get a bank spacing** for our 2D non-spinning case,
cheap to add (see [[../todo]]) — claim `bank-spacing-cross-check-svd` in
`structure/claims.yaml`.

## Numbers worth having on hand

- Table I: real aligned-spin BBH banks, e.g. $\mathcal{M}_c\in(10,20)\,M_\odot$,
  $q\ge 1/18$, $|\chi|\le 0.99$ → **1607 templates**; $\mathcal{M}_c\in(20,40)$ →
  **225**; $\mathcal{M}_c>40$ → **46**. **Not directly comparable** to our count — they
  include spin and extreme mass ratio, we don't — useful only as an order-of-magnitude
  sanity check (ours, non-spinning and narrower, should be well below these).
- Fig. 5: cumulative fraction of random-injection trials that do **not** reach a given
  match, before/after grid refinement, per bank. This is the template for our own
  covering-check figure (claim `covering-at-mm097`) — same idea, our square vs.
  hexagonal vs. SVD-grid as the compared curves.
- Conclusion section: "effectualness and total number of templates comparable to other
  algorithms in the literature" — they did not do a direct numeric comparison against
  a metric-based bank for a small toy case; doing that for our 2D case is a genuine
  (small) original check, not a repeat of their result.

## Citation

Roulet, J., Dai, L., Venumadhav, T., Zackay, B., & Zaldarriaga, M. (2019).
*Template Bank for Compact Binary Coalescence Searches in Gravitational Wave Data: A
General Geometric Placement Algorithm.* arXiv:1904.01683.
