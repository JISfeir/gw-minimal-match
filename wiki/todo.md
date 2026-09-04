# TODO

What is unresolved. A number that is needed and cannot be found goes here — do not invent
it.

## Before any computation: the one-page spec

- [ ] Detector and PSD: which curve (aLIGO design zero-det-high-power? the day-2
      `psd_reference.npz`?), and the source of the array.
- [ ] Frequency band: $f_{\rm low}$, $f_{\rm high}$ / sampling, segment length.
- [ ] Parameter coordinates: $(m_1, m_2)$ vs $(\mathcal{M}_c, \eta)$, and the mass range.
- [ ] Waveform family per stage: TaylorF2 for the analytic Owen-metric comparison;
      IMRPhenomD (pycbc) for the "missing physics" effect in stage 1.
- [ ] $\mathrm{MM}$ target (0.97) and the false-alarm probability behind $\rho^\*$.
- [ ] The central figure of each of the five stages.
- [ ] The checklist: what counts as "verified" for each stage.

## Open questions

- [ ] Single-template vs. against-a-bank framing for "how wrong before lost" — do both?
- [ ] Does $\Delta V/V \approx 3(1-\mathrm{MM})$ hold across the mass range, or break
      where the metric varies fastest? (This is a deliverable, not just a check.)
