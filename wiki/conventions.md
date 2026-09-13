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
| $(\tau_0, \tau_3)$ | Newtonian / 1.5 PN chirp times at $f_0 = f_{\rm low}$; **the bank coordinates here** | Owen & Sathyaprakash 1999 eqs. 3.3–3.4; Sathyaprakash 1994 | 2026-09-09 |
| $c_\alpha$ | SVD phase-basis coefficients, mismatch Euclidean by construction | Roulet et al. 2019 eq. 15 — used only for `bank-spacing-cross-check-svd` | 2026-09-09 |

## Non-negotiable choices

Settled 2026-09-09 (see [[log]]). These are inputs, not results — every one has a
defensible alternative that was considered and rejected for the reason given.

| choice | value | why this and not the alternative |
|---|---|---|
| Detector / PSD | single detector; `pycbc.psd.aLIGOZeroDetHighPower`, analytic, sampled on the analysis frequency grid | canonical curve, reproducible with no external file, directly comparable to the Owen / Cokelaer literature. Rejected: day-2 `psd_reference.npz` (adds an untracked-file dependency); an O3 measured PSD (non-stationarity breaks the analytic Gaussian threshold — that is the v2 item). |
| Bank / metric coordinates | $(\tau_0, \tau_3)$ chirp times, referenced to $f_0 = f_{\rm low} = 20\ \mathrm{Hz}$ | Owen's metric is near-constant in these coordinates, so square / hexagonal placement is a literal grid and the numeric-vs-analytic metric check is cleanest. Rejected: $(\mathcal{M}_c,\eta)$ and $(m_1,m_2)$ — metric varies fastest exactly where `volume-loss-rule` wants to measure the departure, near $\eta = 0.25$. |
| Frequency band | $f_{\rm low} = 20\ \mathrm{Hz}$, $f_{\rm high} = 1024\ \mathrm{Hz}$ | standard for $5$–$50\,M_\odot$ in aLIGO design; a $10+10\,M_\odot$ ISCO is $\approx 220\ \mathrm{Hz}$, so 1024 Hz is well clear. Rejected: 15 Hz (longer segments, marginal metric change); 30–2048 Hz (loses low-band SNR). |
| Segment length | $T_{\rm seg}$ = next power of two above the longest TaylorF2 duration in range (the $5+5\,M_\odot$ corner from 20 Hz), $\Delta f = 1/T_{\rm seg}$ | duration is a derived quantity, not a free choice; power of two for the FFT. |
| Waveform family | TaylorF2 (frequency domain, 3.5 PN phase) for the Owen-metric comparison and everything downstream of it (stages 2–5); IMRPhenomD (`pycbc.waveform`) only for the "missing physics" contrast in stage 1 | Owen's analytic metric *is* the TaylorF2 metric — comparing against a different family would confound model error with metric error. |
| Mass range | component masses $m_1, m_2 \in [5, 50]\,M_\odot$, $m_1 \ge m_2$; no spin | matches the README scope. **Open:** whether to additionally cap total mass $M \le 100\,M_\odot$ (automatic here) or chirp mass — see [[todo]]. |
| Minimal match target | $\mathrm{MM} = 0.97$ | course-standard; the covering check and volume-loss curves are computed *as a function of* MM, with 0.97 the headline point. |
| Detection threshold $\rho^\*$ | solve $\rho^\*$ from a target false-alarm probability over the whole analysis, folding in a trials factor $\approx N_{\rm templates} \times N_{\rm indep\ time\ samples}$ | ties the threshold to bank density, which is the whole point of the claim. Rejected: flat $\rho^\* = 8$ (decouples threshold from the bank); per-template FAP with no trials correction (kept as a reported intermediate). **Open:** the target FAP value and the observation time behind $N_{\rm indep\ time\ samples}$ — see [[todo]]. |

## Corrections

*(dated entries, as they happen)*
