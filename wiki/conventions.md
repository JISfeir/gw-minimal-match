# Conventions

The notation contract for this project: what each symbol means **here**, where the
literature uses it for something else, and every non-negotiable choice. The most valuable
page in the wiki. Record the date each convention was settled — a reader needs to know
whether an earlier draft predates it.

A convention with a correction attached is worth ten without one. When this project makes
a mistake, the fix goes here, dated.

## Symbols

| symbol | meaning here | note / where the literature differs | settled |
|---|---|---|---|
| $h(f)$ | frequency-domain waveform, one polarization, dominant mode | — | |
| $\langle a \mid b \rangle$ | noise-weighted inner product $4\,\mathrm{Re}\!\int a\,b^\* / S_n\,df$ | some authors drop the factor 4 or the Re | |
| $S_n(f)$ | one-sided PSD | two-sided differs by a factor 2 | |
| match | $\langle a\mid b\rangle$ maximized over time and phase, normalized | — | |
| $\mu$ (mismatch) | $1 - \mathrm{match}$ | **not** $\mathcal{M}$: that clashed with the match and with chirp mass, and job q12's figure legend "$1-\mathcal{M}$" came from it | 2026-09-13 |
| $\mathrm{FF}$ (fitting factor) | match maximized over the *bank* / template parameters | Apostolatos 1995 | |
| $\mathrm{MM}$ (minimal match) | worst-case nearest-template match the bank guarantees | typically 0.97 | |
| $g_{ij}$ | metric on parameter space, $\mu\approx g_{ij}\Delta\theta^i\Delta\theta^j$ | Owen 1996 Eq. 2.10 (arXiv v1 numbering) | |
| $M$ | total mass $m_1+m_2$ | — | 2026-09-13 |
| $\rho$ | matched-filter SNR | — | |
| $\lvert z\rvert$ | observed statistic: filter output maximized over phase, normalized so $\langle\lvert z\rvert^2\rangle = 2$ in signal-free Gaussian noise. At a fixed lag it is one sample: Rice-distributed, with $\langle\lvert z\rvert^2\rangle=\rho_{\rm opt}^2\,\mathrm{match}^2+2$ and signal-free tail $P(\lvert z\rvert>r)=e^{-r^2/2}$ (to be verified in job q1bC) | FINDCHIRP normalizes the same way; some pipelines use $\rho^2/2$ | 2026-09-14 |
| $\rho^\*$ | detection threshold on $\lvert z\rvert$ | — | |
| $\mathrm{FAR}$, $T_{\rm obs}$ | false-alarm rate; observation time | — | 2026-09-14 |
| $\mathrm{FAP}$ | false-alarm probability over the analysis; under a Poisson false-alarm process, $1-\exp(-\mathrm{FAR}\,T_{\rm obs})$; $\mathrm{FAR}\,T_{\rm obs}$ is only its small-rate approximation | — | 2026-09-14 |
| $\nu_{\rm eff}$, $N_{\rm eff}$ | effective rate of independent trials of the time- and bank-maximized statistic; $N_{\rm eff}=\nu_{\rm eff}T_{\rm obs}$ | $N_{\rm templates}\times$ (samples per second) $\times T_{\rm obs}$ is only an upper bound | 2026-09-14 |
| $V_{\rm eff}$ | effective detection volume up to a constant, $\langle M_{\rm bank}^3\rangle/\rho^{\*3}$ | ignores noise fluctuations of $\lvert z\rvert$ near threshold | 2026-09-14 |
| $(m_1, m_2)$ | component masses, source frame, $m_1 \ge m_2$ | also used: $(\mathcal{M}_c, \eta)$ | |
| $(\tau_0, \tau_3)$ | Newtonian / 1.5 PN chirp times at $f_0 = f_{\rm low}$; **the bank coordinates here** | Owen & Sathyaprakash 1999 eqs. 3.3–3.4; Sathyaprakash 1994 | 2026-09-09 |
| $f_{\rm ISCO}$ | $1/(6^{3/2}\pi M)$, test-mass Schwarzschild ISCO of the total mass; $v=1/\sqrt6$, $Mf\approx0.0217$ | Cokelaer 2007 calls it $f_{\rm LSO}$ | 2026-09-13 |
| $c_\alpha$ | SVD phase-basis coefficients, mismatch Euclidean by construction | Roulet et al. 2019 eq. 15 — used only for `bank-spacing-cross-check-svd` | 2026-09-09 |

## Non-negotiable choices

Settled 2026-09-09 unless dated otherwise (see [[log]]). These are inputs, not results —
every one has a defensible alternative that was considered and rejected for the reason
given.

| choice | value | why this and not the alternative |
|---|---|---|
| Detector / PSD | single detector; `pycbc.psd.aLIGOZeroDetHighPower`, analytic, sampled on the analysis frequency grid | canonical curve, reproducible with no external file, directly comparable to the Owen / Cokelaer literature. Rejected: day-2 `psd_reference.npz` (adds an untracked-file dependency); an O3 measured PSD (non-stationarity breaks the analytic Gaussian threshold — that is the v2 item). |
| Bank / metric coordinates | $(\tau_0, \tau_3)$ chirp times, referenced to $f_0 = f_{\rm low} = 20\ \mathrm{Hz}$ | the metric's **orientation** is nearly constant in these coordinates (major axis within 4.7° over the main region, 9° over the extended one, job q12), so lattices align naturally and the numeric-vs-analytic check is clean. *Corrected 2026-09-14:* its **magnitude is not** near-constant — see Corrections — so placement uses the local metric. Rejected: $(\mathcal{M}_c,\eta)$ and $(m_1,m_2)$. |
| Frequency band | $f_{\rm low} = 20\ \mathrm{Hz}$, $f_{\rm high} = 1024\ \mathrm{Hz}$ | standard for these masses in aLIGO design; the highest template cutoff in range is $f_{\rm ISCO}=440$ Hz ($M=10$), well below 1024 Hz. Rejected: 15 Hz (longer segments, marginal metric change); 30–2048 Hz (loses low-band SNR). |
| Segment length | $T_{\rm seg}$ = next power of two above the longest TaylorF2 duration in range (the $5+5\,M_\odot$ corner from 20 Hz), $\Delta f = 1/T_{\rm seg}$ | duration is a derived quantity, not a free choice; power of two for the FFT. |
| Waveform family | TaylorF2 (frequency domain, 3.5 PN phase) for templates, the metric comparison and everything downstream of it; IMRPhenomD (`pycbc.waveform`), to $f_{\rm high}$, as the physical signal in the model-error comparison and in volume-loss injections | Owen's analytic metric *is* the TaylorF2 metric — comparing against a different family would confound model error with metric error. EOB (SEOBNR) and IMRPhenomXAS were considered for the extended region and not adopted: no analytic metric exists for them, and SEOBNR ROM data files are not installed. |
| Template high-frequency cutoff | TaylorF2 ends at $f_{\rm ISCO}(M)$ — *settled 2026-09-13* | it is LAL's TaylorF2 default, verified: pycbc TaylorF2's last nonzero bin is exactly $f_{\rm ISCO}$; recorded because it had been inherited silently. Consequences carried as results, not hidden: the model-error comparison is split into common support and full signal, and the moving cutoff makes the physical match non-quadratic. Rejected: cut at $f_{\rm high}$ (job q12: worsens every same-mass match by 0.009–0.107, the waveform is not valid there); a fixed $Mf$ (no advantage over ISCO for a PN model); IMRPhenomD's own transition frequencies (inspiral phase to $Mf\approx0.018$ per Khan et al. 2016, arXiv:1508.07253 — **unverified, from memory**). |
| Mass range | component masses $m_1, m_2 \in [5, 50]\,M_\odot$, $m_1 \ge m_2$; no spin. **Two regions, always reported apart** — *settled 2026-09-13*: main $M\le35\,M_\odot$ (headline results); extended $35<M\le100\,M_\odot$ (where TaylorF2 cut at ISCO stops being usable) | 35 is the inspiral low-mass search range in FINDCHIRP (Allen et al. 2012, gr-qc/0509116, Sec. I: $2<M<35\,M_\odot$, with a separate high-mass search $25<M<100$). Context: Usman et al. 2016 use post-Newtonian templates only below $4\,M_\odot$; Cokelaer 2007 uses TaylorF2 with components 3–30 $M_\odot$. Measured here: IMRPhenomD SNR² below $f_{\rm ISCO}$ is 84 % at $M=30$, 67 % at 50, 27 % at 100. Rejected: a cap near 60 read off job q12 by eye (no paper uses it); a single box with no split (hides the breakdown). |
| Minimal match target | $\mathrm{MM} = 0.97$ | course-standard, and the PyCBC bank's ≤ 3 % SNR loss (Usman et al. 2016); the covering check and volume curves are computed *as a function of* MM, with 0.97 the headline point. |
| Quadratic-validity criterion | the metric is good enough to place a bank at MM wherever the worst relative error of the predicted mismatch, over direction, is ≤ 10 % at $\mu_{\rm pred}=1-\mathrm{MM}$ — *settled 2026-09-13, pre-registered before the jobs* | operational and coordinate-invariant: it compares the quadratic predictor with exact matches for displacements of fixed predicted mismatch. At MM = 0.97 a 10 % error bounds the guaranteed match between 0.967 and 0.973. Rejected: a derivative or norm of $g_{ij}$ components ("where the metric varies fastest") — coordinate-dependent. |
| Bank placement | **Cokelaer 2007**: each cell uses the metric at its own position and the lattice grows cell by cell to the region's boundary; hexagonal lattice, and square lattice aligned with the local eigenvectors with Owen spacing (Owen 1996 Eq. 3.16) — *settled 2026-09-14, pre-registered* | the metric's magnitude varies by a factor 3 in template density over the main region, so any single metric misplaces templates; Cokelaer's method is published, used for exactly this 2-D TaylorF2 problem, and in `papers/`. Cokelaer notes a square lattice laid along the coordinate axes instead of the eigenvectors "may create holes when the orientation of the ellipses varies significantly". **Sensitivity (s1):** a global metric anchored at predefined points, $m_1=12.5, m_2=6.25\,M_\odot$ (main) and $m_1=40, m_2=20\,M_\odot$ (extended) — interior points, $q=2$, near the middle of each region in $\log M$, fixed before any run. |
| Bank boundaries | cells on the non-physical side of $\eta = 1/4$ are **projected onto the $\eta=1/4$ line** along the local eigenvector; templates that are physical but outside the mass box are **kept** when they cover its borders — *settled 2026-09-14, pre-registered* | Cokelaer 2007's treatment: templates outside the box are required to cover it fully. **Sensitivity (s2):** non-physical cells discarded instead of projected. Injections are reported **apart**: *border* = within one covering radius, $\sqrt{1-\mathrm{MM}}$ in local metric distance, of any boundary of the region; *interior* = the rest. Without the split a below-target fraction could come from boundaries alone. |
| Lattice comparison | square and hexagonal lattices at **equal minimal match** (equal covering radius) — *settled 2026-09-13* | with Owen's spacing the square cell's worst point has mismatch exactly $1-\mathrm{MM}$, so ideal geometry covers with both, and the comparison is template count (constant-metric expectation hexagonal/square = 0.770). The Monte Carlo *tests* that expectation under a varying metric, the moving cutoff and boundaries; an excess below target is attributed, not assumed away. Rejected: equal density (a square lattice then fails at cell centres by construction). |
| Detection threshold $\rho^\*$ — operating point | $\mathrm{FAR} = 1/(100\ \mathrm{yr})$ over $T_{\rm obs} = 1\ \mathrm{yr}$; under the Poisson false-alarm-process convention, $\mathrm{FAP}=1-\exp(-\mathrm{FAR}\,T_{\rm obs}) = 1-e^{-0.01} = 0.0099502$, with 0.01 only its approximation — *settled 2026-09-14, pre-registered before any job reports an optimum* | one false alarm per century is the example threshold in the LIGO–Virgo noise guide (Abbott et al., arXiv:1908.11170, Sec. 8.5: "one false alarm per century of observation"); one year is the order of an observing run. Fixed now so the operating point cannot be chosen after seeing where an optimal MM falls. |
| Detection threshold — sensitivities | **$\mathrm{FAR}=1/\mathrm{yr}$** (under the same Poisson convention, $\mathrm{FAP}=1-e^{-1}=0.632$), a *permissive* operating point, never described as a detection significance (the IAS pipeline, arXiv:1902.10341, draws one false alarm per observing run as a reference line); **5σ defined by its global probability**, $\mathrm{FAP}=P(\mathcal{N}(0,1)>5)=2.8665\times10^{-7}$, one-sided — *settled 2026-09-14* | the years-equivalent of 5σ quoted for GW150914 (Usman et al. 2016: 1 in $2\times10^5$ yr) belongs to that search's data and trials, so it is not imported. |
| Detection threshold — method | exact single-sample tail of $\lvert z\rvert$ (verified in q1bC); $\nu_{\rm eff}$ calibrated from maxima on manageable simulated segments of Gaussian noise filtered through the bank, checked for stability in segment length and relevant tail threshold, and extrapolated as $N_{\rm eff}=\nu_{\rm eff}T_{\rm obs}$; independent trials combine as $\mathrm{FAP}=1-[1-p(\rho^\*)]^{N_{\rm eff}}$, while $1-\exp[-N_{\rm eff}p(\rho^\*)]$ is the rare-tail Poisson approximation whose error must be reported; loop $\mathrm{MM}\to N_{\rm templates}\to\nu_{\rm eff}\to\rho^\*$ closed — *corrected 2026-09-14* | ties the threshold to bank density, which is the whole point of the claim; with correlated trials, $N_{\rm eff}$ defines a calibrated model rather than making the independent-trials equation exact for the bank. Simulating a year of noise is unnecessary if the rate is stable. Rejected: flat $\rho^\*=8$ (decouples threshold from the bank); treating the naive trials count or the Poisson approximation as exact. |
| Effective-volume objective | $V_{\rm eff}(\mathrm{MM})=\langle M_{\rm bank}^3\rangle/\rho^\*(\mathrm{MM})^3$, maximized over MM with its uncertainty; for IMRPhenomD injections $M_{\rm bank}$ is the direct best match against the whole TaylorF2 bank — *settled 2026-09-14* | for sources uniform in Euclidean volume the detection distance scales as match/$\rho^\*$, so this is the volume up to a constant; it needs no "ideal continuous bank", whose template count and threshold would be undefined. Its omission of noise fluctuations near threshold is estimated with the Rice distribution. |

## Corrections

- **2026-09-16 — what the bank density is actually traded against.** The [[README]] asks "how
  dense must the bank be" without naming the cost of density, which left Owen's motivation —
  computing power — standing by default. In this mass range that motivation is dead. Owen &
  Sathyaprakash 1999 (gr-qc/9808076, abstract) scale the required power as
  $m_{\rm min}^{-8/3}$ and the storage as $m_{\rm min}^{-13/3}$; their $7.8\times10^{11}$ flops
  for advanced LIGO assume $m_{\rm min}=0.2\,M_\odot$, and our $m_{\rm min}=5\,M_\odot$ divides
  that by $(5/0.2)^{8/3}\approx5.4\times10^3$, i.e. $\sim0.15$ Gflops — under one core.
  Corroborated without scaling: Cokelaer 2007 Table IV gives 2422 square / 1764 hexagonal
  templates for $3$–$30\,M_\odot$ at MM $=0.95$; Roulet et al. 2019 Table I gives 225 templates
  for $M\in(20,40)$ and 46 for $M>40$ against 316 262 for the whole $1$–$100\,M_\odot$ bank; and
  Usman et al. 2016 Table 1 spends 4.7 CPU-days generating the bank against 515.5 on matched
  filtering and $\chi^2$ — 0.9 % of the pipeline. **Consequence: here the price of a finer bank
  is the detection threshold through the trials factor, not flops.** That is what part F
  optimises ($V_{\rm eff}$), and why it does not optimise template count at fixed cost the way
  Keppel 2013 does. Where flops still bind: subsolar $m_{\rm min}$, precessing / higher-mode /
  eccentric banks, early warning — all outside this SETTING.

- **2026-09-14 — independent-trials FAP vs. Poisson approximation.** The qDEF objective
  called $1-\exp[-N_{\rm eff}p]$ exact. For $N_{\rm eff}$ independent trials the exact
  combination is $1-(1-p)^{N_{\rm eff}}$; the exponential is its rare-tail Poisson
  approximation. qDEF now calibrates $N_{\rm eff}$ from simulated maxima, checks its stability
  with segment length and threshold, and reports the approximation error. The separate relation
  $1-\exp(-\mathrm{FAR}\,T_{\rm obs})$ is conditional on the stated Poisson false-alarm-process
  convention.
- **2026-09-14 — "Owen's metric is near-constant in $(\tau_0,\tau_3)$".** This file said so, and
  on 2026-09-13 qualified it only to the main region. Wrong there too: job q12's analytic 3.5PN
  metric over $M=10$–35 has template density $\sqrt{\det g}$ varying by a factor 3.0, the small
  eigenvalue by 4.5 and the large by 2.0 (factors 12, 28 and 5 over the extended region); only
  the orientation is stable (4.7°). Owen 1996 found a constant matrix because he worked at 1PN
  with a cutoff that does not move with mass. Consequence: bank placement uses the local metric
  (Cokelaer 2007). Found while checking a second Codex review of the objective.
- **2026-09-14 — FAP and observation time, contradictory instructions.** The job objective
  asked the team to choose headline values while [[todo]] deferred the choice to the paper.
  Both now fixed as pre-registered inputs above.
- **2026-09-14 — the square-lattice claim overcorrected.** On 2026-09-13 claim
  `covering-at-mm097` was rewritten to assert that both lattices cover with a below-target
  fraction of zero. That is the ideal constant-metric geometry, which is exactly what the Monte
  Carlo has to test under a varying metric, a moving cutoff and boundaries. Reworded as a
  measurement with attribution.
- **2026-09-13 — square lattice "dips below target at cell corners".** Claim
  `covering-at-mm097` (reworded 2026-09-05) called this an expected result. Wrong: with Owen's
  spacing the square cell's worst point, its centre, has mismatch exactly $1-\mathrm{MM}$, so
  a correctly spaced square lattice covers; it only needs ≈30 % more templates than a
  hexagonal one. Found by an independent Codex review of the objective; checked against Owen
  1996 Eq. 3.16. The claim now compares lattices at equal MM.
- **2026-09-13 — "fractional SNR loss equals the mismatch to leading order".** Claim
  `mismatch-snr-loss` had it backwards: in noise-free data the loss *is* the mismatch,
  exactly; what is leading order is $\mu\approx g_{ij}\Delta\theta^i\Delta\theta^j$. In noise
  the observed statistic is a random variable, which the claim now states separately.
- **2026-09-13 — "where the metric varies fastest".** Job q12 answered it with a Frobenius
  norm of $g_{ij}$ changes in $(\tau_0,\tau_3)$, which depends on the coordinates. Replaced by
  the quadratic-validity criterion above.
- **2026-09-13 — mismatch symbol.** The table used $\mathcal{M}$ for the mismatch while job
  q12 used $M$ for the match; the job's figure legend read "$\rho_{\rm rec}/\rho_{\rm opt} =
  1-\mathcal{M}$". Mismatch is now $\mu$.
