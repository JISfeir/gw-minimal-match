# Conventions

The notation contract for this project: what each symbol means **here**, where the
literature uses it for something else, and every non-negotiable choice. The most valuable
page in the wiki. Record the date each convention was settled — a reader needs to know
whether an earlier draft predates it.

A convention with a correction attached is worth ten without one. When this project makes
a mistake, the fix goes here, dated.

## Symbols

*(to be filled as the work starts — seed entries below)*

| symbol | meaning here | note / where the literature differs | settled |
|---|---|---|---|
| $h(f)$ | frequency-domain waveform, one polarization, dominant mode | — | |
| $\langle a \mid b \rangle$ | noise-weighted inner product $4\,\mathrm{Re}\!\int a\,b^\* / S_n\,df$ | some authors drop the factor 4 or the Re | |
| $S_n(f)$ | one-sided PSD | two-sided differs by a factor 2 | |
| match / overlap | $\langle a\mid b\rangle$ maximized over time and phase, normalized | — | |
| $\mathrm{FF}$ (fitting factor) | match maximized over the *bank* / template parameters | Apostolatos 1995 | |
| $\mathcal{M}$ (mismatch) | $1 - \mathrm{match}$ | Owen 1996 calls the metric $g_{ij}$ from this | |
| $\mathrm{MM}$ (minimal match) | worst-case nearest-template match the bank guarantees | typically 0.97 | |
| $g_{ij}$ | metric on parameter space, $\mathrm{match}\approx 1 - g_{ij}\Delta\theta^i\Delta\theta^j$ | Owen 1996 eq. 2.10 | |
| $\rho$ | matched-filter SNR | — | |
| $\rho^\*$ | detection threshold, from an analytic Gaussian false-alarm rate | — | |
| $(m_1, m_2)$ | component masses, source frame, $m_1 \ge m_2$ | also used: $(\mathcal{M}_c, \eta)$ | |

## Non-negotiable choices

*(to be filled — e.g. detector/PSD, frequency band, waveform family per stage, mass range,
$\mathrm{MM}$ target, false-alarm probability behind $\rho^\*$)*

## Corrections

*(dated entries, as they happen)*
