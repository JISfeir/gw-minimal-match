# TODO

What is unresolved. A number that is needed and cannot be found goes here — do not invent
it.

## Before any computation: the one-page spec

Settled 2026-09-09 — full table with rejected alternatives in [[conventions]]:

- [x] Detector and PSD: single detector, analytic `aLIGOZeroDetHighPower` (pycbc).
- [x] Frequency band: $20$–$1024\ \mathrm{Hz}$; segment length = next power of two above
      the longest TaylorF2 duration in range ($5+5\,M_\odot$ from 20 Hz).
- [x] Parameter coordinates: chirp times $(\tau_0, \tau_3)$ at $f_0 = 20\ \mathrm{Hz}$.
      Mass range: component masses $\in [5, 50]\,M_\odot$, $m_1 \ge m_2$, no spin.
- [x] Waveform family: TaylorF2 for the Owen-metric comparison and everything downstream
      (stages 2–5); IMRPhenomD (pycbc) for the "missing physics" contrast in stage 1.
- [x] $\mathrm{MM}$ target: 0.97 (headline point; curves computed vs. MM).
- [~] $\rho^\*$: solve from a target FAP with a bank trials factor. **Method fixed, two
      inputs still open** (below).

Still open:

- [ ] **Target FAP** value behind $\rho^\*$ (e.g. $10^{-3}$ over the analysis) and the
      **observation time** behind $N_{\rm indep\ time\ samples}$ in the trials factor.
- [ ] Whether to cap **total mass** ($M \le 100\,M_\odot$, automatic here) or **chirp
      mass** on top of the component-mass box.
- [ ] The explicit **five-stage breakdown**, each stage's **central figure**, and the
      per-stage **"verified" checklist**.

## Open questions

- [ ] Single-template vs. against-a-bank framing for "how wrong before lost" — do both?
- [ ] Does $\Delta V/V \approx 3(1-\mathrm{MM})$ hold across the mass range, or break
      where the metric varies fastest? (This is a deliverable, not just a check.)

## Stretch: second bank-spacing cross-check (claim `bank-spacing-cross-check-svd`)

- [ ] Reuse the TaylorF2 waveforms sampled for the match map (stage 2) to build the
      SVD phase basis of [[sources/roulet2019_svd_bank]], restricted to our 2D
      non-spinning range. Place a regular grid in the resulting $c$-space and compare
      $N_{\rm templates}(\mathrm{MM})$ and the covering histogram against the
      Owen-metric bank. Cheap given stage-2 waveforms already exist; do after stages
      1-4 are solid, not before.
