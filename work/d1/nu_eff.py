"""Part E.2: calibrate the effective independent-trials rate from simulated noise.

This replaces the naive bound N_templates * f_sample * T_obs, which counts every
template and every sample as independent. It is what part F's conclusion turns on:
the efverify r01 audit showed that with N_eff growing as N^alpha the V_eff maximum
leaves MM = 0.95 at alpha between 0.46 and 0.85, so the exponent decides whether the
optimum sits at the coarse edge or inside the grid.

METHOD. Colour Gaussian noise with the analytic PSD, filter it through every template
of a bank, and take the maximum of |z| over templates and over time in each segment.
For N_eff independent samples of a statistic with P(|z| > r) = exp(-r^2/2) -- q1bC part
A, verified there and reproduced here as a control -- the maximum M obeys
    P(M <= r) = (1 - exp(-r^2/2))^{N_eff},
whose maximum-likelihood estimate from S observed maxima is closed form:
    N_eff = -S / sum_i log(1 - exp(-M_i^2 / 2)),      SE ~ N_eff / sqrt(S).
Threshold-wise estimates from exceedance fractions are reported beside it, because the
objective asks whether N_eff is stable across the tail rather than assuming it is.

WHAT THIS DOES NOT DO. It does not simulate a year; nu_eff is a rate per second and
N_eff = nu_eff * T_obs extrapolates it, which assumes segments are independent and
stationary. It uses one detector and the analytic PSD, so it measures the correlation
structure of the bank, not any real detector's noise.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(os.environ.get("GWMM_PROJECT", "/home/juan/gw-minimal-match"))
sys.path.insert(0, str(ROOT / "jobs/2026-09-14_041516_derive-q1bc/out"))
from lib.filtering import kernel                    # noqa: E402
from lib.noise import coloured_noise                # noqa: E402
from lib.waveforms import psd_grid, taylorf2        # noqa: E402

RESULTS = ROOT / "results" / "d1"
DF = 1 / 32
T_SEG = 1.0 / DF
CHUNK = 64
MM_GRID = (0.95, 0.96, 0.97, 0.98, 0.99)


def mle_n_eff(maxima):
    """Closed-form MLE and its asymptotic standard error."""
    m = np.asarray(maxima, dtype=float)
    logs = np.log1p(-np.exp(-0.5 * m * m))
    n_eff = -len(m) / float(np.sum(logs))
    return n_eff, n_eff / np.sqrt(len(m))


def threshold_estimates(maxima, thresholds):
    """N_eff read off the exceedance fraction at each threshold, for the stability
    check the objective asks for."""
    m = np.asarray(maxima, dtype=float)
    out = {}
    for r in thresholds:
        frac = float(np.mean(m > r))
        if 0.0 < frac < 1.0:
            out[f"{r:.2f}"] = float(np.log1p(-frac) / np.log1p(-np.exp(-0.5 * r * r)))
    return out


def bank_maxima(bank_path, noise, psd, verbose=True):
    """Maximum of |z| over templates and time, per segment; also over the first half
    of each segment, which tests whether nu_eff is a rate."""
    raw = np.loadtxt(bank_path)
    n_templates, n_seg = len(raw), len(noise)
    n_time = 2 * (len(psd) - 1)
    best = np.zeros(n_seg)
    best_half = np.zeros(n_seg)
    started = time.time()
    used = 0
    for start in range(0, n_templates, CHUNK):
        rows = raw[start:start + CHUNK]
        kernels = []
        for m1, m2 in rows[:, :2]:
            try:
                kernels.append(kernel(taylorf2(float(m1), float(m2), DF), psd, DF))
            except Exception:
                continue
        if not kernels:
            continue
        block = np.asarray(kernels)
        used += len(block)
        for s in range(n_seg):
            amplitude = np.abs(np.fft.ifft(noise[s] * block, n=n_time, axis=1) * n_time)
            best[s] = max(best[s], float(amplitude.max()))
            best_half[s] = max(best_half[s], float(amplitude[:, :n_time // 2].max()))
        if verbose and (start // CHUNK) % 8 == 0:
            print(f"    {start + len(block)}/{n_templates} templates, "
                  f"{time.time() - started:.0f}s", flush=True)
    return best, best_half, used


def main():
    n_seg = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20260926
    combos = [("main", "hexagonal"), ("main", "square"),
              ("extended", "hexagonal"), ("extended", "square")]

    psd = psd_grid(DF)
    rng = np.random.default_rng(seed)
    # one noise set, shared by every bank, so the comparison across MM is paired
    noise = coloured_noise(psd, DF, rng, count=n_seg)
    print(f"{n_seg} segments of {T_SEG:g} s, seed {seed}, shared across banks\n")

    out = {"n_segments": n_seg, "seed": seed, "t_seg_s": T_SEG,
           "f_sample_hz": 2 * (len(psd) - 1) * DF, "banks": {}}
    maxima_store = {}
    for region, lattice in combos:
      for mm in MM_GRID:
        path = RESULTS / "banks" / f"bank_{region}_{lattice}_mm{round(mm * 100):03d}.txt"
        if not path.exists():
            continue
        print(f"  {region} {lattice} MM = {mm}")
        maxima, maxima_half, used = bank_maxima(path, noise, psd)
        n_eff, err = mle_n_eff(maxima)
        n_eff_half, _ = mle_n_eff(maxima_half)
        naive = used * out["f_sample_hz"] * T_SEG
        entry = {
            "n_templates": int(used),
            "n_eff_per_segment": n_eff, "n_eff_per_segment_error": err,
            "n_eff_half_segment": n_eff_half,
            "half_over_full": n_eff_half / n_eff,
            "nu_eff_per_second": n_eff / T_SEG,
            "naive_trials_per_segment": naive,
            "ratio_to_naive": n_eff / naive,
            "threshold_estimates": threshold_estimates(
                maxima, np.arange(4.6, 6.61, 0.2)),
            "max_statistics": {"min": float(np.min(maxima)),
                               "median": float(np.median(maxima)),
                               "max": float(np.max(maxima))},
        }
        key = f"{region}_{lattice}_mm{round(mm * 100):03d}"
        entry["region"], entry["lattice"], entry["minimal_match"] = region, lattice, mm
        out["banks"][key] = entry
        maxima_store[key] = maxima
        maxima_store[key + "_half"] = maxima_half
        print(f"    N={used}  max median {np.median(maxima):.3f}  "
              f"N_eff/segment = {n_eff:.4g} +- {err:.2g}  "
              f"naive = {naive:.4g}  ratio = {n_eff / naive:.3e}")

    # the exponent alpha in N_eff ~ N_templates^alpha, per region/lattice and overall,
    # with a PAIRED bootstrap over segments -- the same noise drives every bank, so the
    # per-bank estimates are correlated and an unpaired error bar would be far too wide
    out["alpha_fit"] = {}
    rng_boot = np.random.default_rng(seed + 7)
    draws = rng_boot.integers(0, n_seg, size=(600, n_seg))
    for label, keys in ([(f"{r}_{l}", [k for k in out["banks"]
                                       if out["banks"][k]["region"] == r
                                       and out["banks"][k]["lattice"] == l])
                         for r, l in combos] + [("all", list(out["banks"]))]):
        if len(keys) < 2:
            continue
        n_t = np.array([out["banks"][k]["n_templates"] for k in keys], float)
        n_e = np.array([out["banks"][k]["n_eff_per_segment"] for k in keys], float)
        alpha, intercept = np.polyfit(np.log(n_t), np.log(n_e), 1)
        boot = []
        for idx in draws:
            resampled = [mle_n_eff(maxima_store[k][idx])[0] for k in keys]
            boot.append(np.polyfit(np.log(n_t), np.log(resampled), 1)[0])
        residual = np.log(n_e) - (alpha * np.log(n_t) + intercept)
        out["alpha_fit"][label] = {
            "alpha": float(alpha), "alpha_bootstrap_sd": float(np.std(boot, ddof=1)),
            "alpha_ci95": [float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))],
            "max_abs_log_residual": float(np.abs(residual).max()), "n_points": len(keys)}
        a = out["alpha_fit"][label]
        print(f"  alpha[{label:22s}] = {alpha:7.4f} +- {a['alpha_bootstrap_sd']:.4f}  "
              f"95% [{a['alpha_ci95'][0]:.4f}, {a['alpha_ci95'][1]:.4f}]  "
              f"(naive assumes 1.0)")

    np.savez_compressed(RESULTS / "part_e_nu_eff_maxima.npz", **maxima_store)
    path = RESULTS / "part_e_nu_eff.json"
    path.write_text(json.dumps(out, indent=2, default=float) + "\n")
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
