#!/usr/bin/env python
"""The ONLY source of figures that ship (figure rule F5).

Reads nothing but data/ -- which is tracked -- so a clean clone regenerates every
figure. Rebuild data/ first with scripts/export_figure_data.py.

Each figure below carries its F4 sentence: what it would look like if the result
were wrong. A figure for which that cannot be written does not ship.

Palette: the four categorical slots blue/orange/aqua/yellow, validated for
colour-vision deficiency (worst adjacent pair dE 9.1 protan, 22.9 normal) before use.
Every series is also distinguished by dash pattern or marker, so identity never rests
on colour alone.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
from matplotlib.colors import TwoSlopeNorm  # noqa: E402
import numpy as np                       # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FIGURES = ROOT / "figures"
MM_GRID = (0.95, 0.96, 0.97, 0.98, 0.99)
VALIDATED_FROM = 0.97

BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#d8d7d2"
STYLE = {
    "main_hexagonal": (BLUE, "-", "o"), "main_square": (ORANGE, "--", "s"),
    "extended_hexagonal": (AQUA, "-.", "^"), "extended_square": (YELLOW, ":", "D"),
}
LABEL = {"main_hexagonal": "main, hexagonal", "main_square": "main, square",
         "extended_hexagonal": "extended, hexagonal",
         "extended_square": "extended, square"}


def setup():
    plt.rcParams.update({
        "figure.dpi": 140, "savefig.dpi": 140, "font.size": 9,
        "axes.edgecolor": MUTED, "axes.labelcolor": INK, "text.color": INK,
        "xtick.color": MUTED, "ytick.color": MUTED, "axes.linewidth": 0.8,
        "grid.color": GRID, "grid.linewidth": 0.6, "legend.frameon": False,
        "axes.spines.top": False, "axes.spines.right": False, "figure.autolayout": False,
        # Keep text searchable and avoid Type-3 bitmap fonts in the paper PDF.
        "pdf.fonttype": 42, "ps.fonttype": 42,
    })
    FIGURES.mkdir(exist_ok=True)


def save(fig, stem, caption):
    for suffix in ("pdf", "png"):
        fig.savefig(FIGURES / f"{stem}.{suffix}", bbox_inches="tight")
    (FIGURES / f"{stem}.caption.txt").write_text(caption.strip() + "\n")
    plt.close(fig)
    print(f"  wrote figures/{stem}.pdf (+png, +caption)")


# --------------------------------------------------------------------------- D
def figure_covering():
    """Cumulative fraction of injections below a given match, in the manner of
    Roulet et al. 2019 Fig. 5. MEASURED matches, not a formula (rule F1)."""
    blob = np.load(DATA / "fig_covering.npz")
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.1), sharey=True)
    for ax, region in zip(axes, ("main", "extended")):
        border = blob[f"{region}_border"]
        # Colour follows the LATTICE, which is the entity being compared; the region is
        # the facet. Using a different hue per panel for the same lattice would make the
        # reader learn two mappings for one comparison.
        for lattice, colour, dash in (("hexagonal", BLUE, "-"), ("square", ORANGE, "--")):
            key = f"{region}_{lattice}"
            match = blob[f"{key}_match"]
            for mask, alpha, width, tag in ((~border, 0.45, 1.2, "interior"),
                                            (border, 1.0, 1.8, "border")):
                if mask.sum() == 0:
                    continue
                values = np.sort(match[mask])
                ax.plot(values, np.arange(1, len(values) + 1) / len(values),
                        color=colour, linestyle=dash, lw=width, alpha=alpha,
                        label=f"{lattice}, {tag}")
        ax.axvline(0.97, color=INK, lw=0.8)
        ax.annotate("MM = 0.97", (0.97, 1.2e-3), xytext=(-4, 0),
                    textcoords="offset points", ha="right", va="center", fontsize=8,
                    color=MUTED, rotation=90)
        ax.set_yscale("log"); ax.set_ylim(2e-4, 1.4)
        ax.set_xlim(0.955, 1.0)
        ax.grid(True, alpha=0.5)
        ax.set_xlabel("quadratic-metric predicted best match")
        ax.set_title(f"{region} region", fontsize=9, color=INK, loc="left")
    axes[0].set_ylabel("conditional cumulative fraction within subset")
    axes[1].legend(fontsize=7.5, loc="lower right")
    save(fig, "d_covering_cumulative", """
Cumulative distribution of the best match each injection finds in the bank, at
nominal MM = 0.97, interior and border injections apart. Each curve is normalised
within its own subset, so its ordinate is conditional rather than a fraction of all
injections. 3000 injections per region,
uniform in component mass, seed 20260925; the match is the quadratic form evaluated
with the injection's own metric.
HOW THIS COULD FAIL (F4): any nonzero CDF ordinate left of the MM = 0.97 line refutes
sampled covering. The extended hexagonal curve does cross it -- 2
injections in 3000 -- and that is the measured covering failure, not a plotting
artefact. A sampled bank that covered would have no step left of the line. The log
ordinate is what makes a 1-in-1000 failure visible at
all; on a linear scale all four curves would look identical.
""")


def figure_counts():
    """N(MM) and the measured hexagonal/square ratio against its two references.
    Rule F2: the ratio is the claim, so it gets its own panel on a scale where the
    difference between 0.7698 and 0.717 is visible."""
    opt = json.loads((DATA / "part_f_optimum.json").read_text())
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(5.0, 5.0), sharex=True,
                                      gridspec_kw={"height_ratios": [2, 1.4]})
    for region in ("main", "extended"):
        for lattice in ("hexagonal", "square"):
            key = f"{region}_{lattice}"
            colour, dash, marker = STYLE[key]
            xs, ys = [], []
            for mm in MM_GRID:
                entry = opt.get(region, {}).get(f"{lattice}_mm{round(mm * 100):03d}")
                if entry:
                    xs.append(mm); ys.append(entry["n_templates"])
            if xs:
                top.plot(xs, ys, color=colour, linestyle=dash, marker=marker,
                         ms=4.5, lw=1.6, label=LABEL[key])
    top.set_yscale("log"); top.set_ylabel("templates in the bank")
    top.grid(True, alpha=0.5); top.legend(fontsize=7.5)

    for region, colour, dash, marker in (("main", BLUE, "-", "o"),
                                         ("extended", AQUA, "-.", "^")):
        xs, ys = [], []
        for mm in MM_GRID:
            h = opt.get(region, {}).get(f"hexagonal_mm{round(mm * 100):03d}")
            s = opt.get(region, {}).get(f"square_mm{round(mm * 100):03d}")
            if h and s:
                xs.append(mm); ys.append(h["n_templates"] / s["n_templates"])
        if xs:
            bottom.plot(xs, ys, color=colour, linestyle=dash, marker=marker,
                        ms=4.5, lw=1.6, label=f"{region}, measured")
    # The two references go in the legend, not as annotations: at this ordinate range
    # any in-plot label crosses one of the measured series.
    bottom.axhline(0.7698, color=INK, lw=1.0, label="0.7698  ideal, constant metric")
    bottom.axhspan(0.6605, 0.7866, color=ORANGE, alpha=0.15, lw=0,
                   label="0.6605–0.7866  Cokelaer banks")
    bottom.axhline(0.7191, color=ORANGE, lw=1.0, ls=(0, (5, 2)),
                   label="0.7191  Cokelaer mean")
    bottom.set_ylim(0.60, 0.90)
    bottom.set_xlabel("nominal minimal match MM")
    bottom.set_ylabel("$N_{\\rm hex}/N_{\\rm square}$")
    bottom.grid(True, alpha=0.5)
    bottom.legend(fontsize=7, loc="upper left", ncol=2, columnspacing=1.0)
    save(fig, "d_counts_and_ratio", """
Top: bank size against nominal minimal match, both regions and both lattices.
Bottom: the measured hexagonal/square count ratio against the ideal constant-metric
value 0.7698 and all ratios recomputed from the banks in Cokelaer 2007 Tables I-II:
range 0.6605-0.7866, mean 0.7191. The band is the full published spread, not an
uncertainty interval.
HOW THIS COULD FAIL (F4): if lattice efficiency alone set the ratio, both regions would
sit on one horizontal line near 0.77. They do not: main stays at or above the ideal
(0.7744-0.8090) while extended reaches 0.639. The changes with region, minimal match and
boundary treatment show that the ratio is not universal here. The counts include this
project's boundary repair; the comparison therefore does not test a faithful
implementation of Cokelaer's algorithm.
""")


def figure_mismatch_map():
    """Rule F3: the metric depends on (m1, m2), so at least one figure must show
    both and not collapse them."""
    blob = np.load(DATA / "fig_mismatch_map.npz")
    witness = json.loads((DATA / "fig_witnesses.json").read_text())["main_hexagonal"]
    fig, ax = plt.subplots(figsize=(4.6, 3.8))
    field = blob["mismatch"]
    residual = field - 0.03
    mesh = ax.pcolormesh(
        blob["grid_m1"], blob["grid_m2"], residual, cmap="coolwarm",
        norm=TwoSlopeNorm(vmin=-0.03, vcenter=0.0, vmax=0.01), shading="nearest")
    ax.plot(witness["m1"], witness["m2"], marker="x", ms=9, mew=2.0, color=ORANGE,
            linestyle="none",
            label=f"adaptive witness, $\\mu$ = {witness['mismatch']:.5f}")
    bar = fig.colorbar(mesh, ax=ax, pad=0.02)
    bar.set_label("quadratic-metric mismatch $\\mu-0.03$")
    bar.ax.axhline(0.0, color=INK, lw=1.0)
    ax.set_xlabel("$m_1\\ [M_\\odot]$"); ax.set_ylabel("$m_2\\ [M_\\odot]$")
    ax.set_title("main region, hexagonal bank", fontsize=9, color=INK, loc="left")
    ax.legend(fontsize=7.5, loc="upper left")
    save(fig, "d_mismatch_map_main_hex", """
Quadratic-metric mismatch residual mu - 0.03 to the nearest template over the mass plane
for the main-region hexagonal bank at MM = 0.97, on a 90x90 grid restricted to the region.
Shown against both masses
rather than against total mass, because the metric depends on both (rule F3).
HOW THIS COULD FAIL (F4): a sampled bank that covered would have no positive residual.
On this grid none appears -- the grid's worst cell is 0.02893
-- yet the cross marks a point an adaptive search found at 0.03222, reproduced
independently by the dverify r03 audit. That is the figure's real content: a regular
grid of test points does not find the holes, and a figure built only from grid sampling
would wrongly show a covering bank.
""")


# --------------------------------------------------------------------------- E
def figure_trials():
    """REPLACES the earlier threshold figure, which plotted rho* against MM.

    That figure violated this project's own rule F1: rho* is a closed function of the
    template count through FAP = 1-(1-p)^N, so its y-values were computed from its
    x-values by the formula under test. A blind reviewer reconstructed every plotted
    point from N alone to within 1e-13 and called it decoration. It was.

    What part E actually measures is this: the effective number of independent trials,
    filtered out of simulated noise, against the naive bound that counts every template
    and every sample. Measurement against prediction, which is what F1 asks for."""
    nu = json.loads((DATA / "part_e_nu_eff.json").read_text())
    fig, (left, right) = plt.subplots(1, 2, figsize=(7.6, 3.3))
    for region, lattice, colour, marker in (("main", "hexagonal", BLUE, "o"),
                                            ("main", "square", ORANGE, "s"),
                                            ("extended", "hexagonal", AQUA, "^"),
                                            ("extended", "square", YELLOW, "D")):
        xs, measured, errors, naive = [], [], [], []
        for mm in MM_GRID:
            entry = nu["banks"].get(f"{region}_{lattice}_mm{round(mm * 100):03d}")
            if not entry:
                continue
            xs.append(entry["n_templates"])
            measured.append(entry["n_eff_per_segment"])
            errors.append(entry["n_eff_per_segment_error"])
            naive.append(entry["naive_trials_per_segment"])
        if not xs:
            continue
        fit = nu["alpha_fit"][f"{region}_{lattice}"]
        lo, hi = fit["alpha_ci95"]
        label = f"{region}, {lattice}; $\\alpha$={fit['alpha']:.2f} [{lo:.2f}, {hi:.2f}]"
        left.plot(xs, naive, color=MUTED, lw=1.0, ls=(0, (5, 2)), zorder=1)
        left.errorbar(xs, measured, yerr=errors, color=colour, marker=marker, ms=5,
                      lw=1.6, capsize=2.5, label=label)
        ratio = np.asarray(naive) / np.asarray(measured)
        ratio_error = ratio * np.asarray(errors) / np.asarray(measured)
        right.errorbar(xs, ratio, yerr=ratio_error, color=colour, marker=marker, ms=5,
                       lw=1.6, capsize=2.5, label=label)
    left.plot([], [], color=MUTED, lw=1.0, ls=(0, (5, 2)),
              label="naive bound $N_{\\rm tmpl}\\,f_s\\,T$")
    for ax in (left, right):
        ax.set_xscale("log"); ax.grid(True, alpha=0.5)
        ax.set_xlabel("templates in the bank")
        # explicit ticks: the default log minor labels collide at this aspect ratio
        ax.set_xticks([200, 500, 1000, 2000, 5000])
        ax.set_xticklabels(["200", "500", "1000", "2000", "5000"])
        ax.set_xticks([], minor=True)
        ax.set_xlim(180, 6000)
    left.set_yscale("log")
    left.set_ylabel("independent trials per 32 s segment")
    right.set_ylabel("naive bound / measured")
    left.legend(fontsize=6.2, loc="upper left")
    save(fig, "e_trials_measured_vs_naive", """
Left: the effective number of independent trials per segment, measured by filtering
simulated Gaussian noise through each bank and fitting the distribution of the maximum
of |z| over templates and time (100 segments of 32 s, seed 20260926, the same noise for
every bank), against the naive bound that counts every template and every sample as
independent. Right: their ratio. Error bars show the stored per-bank fit uncertainty;
legend intervals are paired-bootstrap 95 % intervals for each within-family exponent.
THIS FIGURE REPLACES an earlier one that plotted the threshold against minimal match.
That figure broke rule F1 -- rho* is a closed function of the template count, so its
y-values were computed from its x-values by the formula under test, and a blind reviewer
reconstructed every plotted point from N alone to within 1e-13. It was decoration.
HOW THIS COULD FAIL (F4): if the templates of a bank were independent, the coloured
points would lie on the dashed line and the right-hand ratio would be 1. They do not and
it is not: the ratio runs from about 7 to 58. If instead the measured trials grew in
proportion to the template count, each family would run parallel to the dashed line;
they are far flatter, which is the exponent the text reports.
WHAT IT DOES NOT SHOW: the calibration is done where the maxima fall, around |z| = 5.3
to 5.8, and is applied at thresholds near 8.0 to 8.6. That extrapolation of about two in
|z| is not tested here, and the trials count is not constant across the probed tail.
""")


# --------------------------------------------------------------------------- F
def figure_volume_losses():
    """Three losses that must never be merged, plotted against MM. Two are
    predictions and one is measured, which is the comparison rule F1 asks for."""
    opt = json.loads((DATA / "part_f_optimum.json").read_text())
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    fine = np.linspace(0.945, 0.995, 200)
    ax.plot(fine, 1 - fine ** 3, color=INK, lw=1.4, label="$1-\\mathrm{MM}^3$ (exact worst case)")
    ax.plot(fine, 3 * (1 - fine), color=MUTED, lw=1.2, ls=(0, (5, 2)),
            label="$3(1-\\mathrm{MM})$ (linear expansion)")
    for region in ("main", "extended"):
        for lattice in ("hexagonal", "square"):
            key = f"{region}_{lattice}"
            colour, dash, marker = STYLE[key]
            xs, ys, es = [], [], []
            for mm in MM_GRID:
                entry = opt.get(region, {}).get(f"{lattice}_mm{round(mm * 100):03d}")
                if entry:
                    xs.append(mm); ys.append(entry["losses"]["population_taylorf2"])
                    rho = entry["rho_star"]["far_1_per_100yr"]
                    es.append(entry["v_eff_error"]["far_1_per_100yr"]["taylorf2"] * rho ** 3)
            if xs:
                ax.errorbar(xs, ys, yerr=es, color=colour, linestyle=dash, marker=marker,
                            ms=4.5, lw=1.6, capsize=2.5,
                            label=f"metric-predicted population, {LABEL[key]}")
    ax.set_yscale("log")
    ax.set_xlabel("nominal minimal match MM")
    ax.set_ylabel("fractional detection-volume loss")
    ax.grid(True, alpha=0.5)
    # Outside the data area: with six series every in-plot corner crosses one of them.
    ax.legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.02, 1.0),
              borderaxespad=0.0)
    inset = ax.inset_axes([0.10, 0.12, 0.38, 0.28])
    exact = 1 - fine ** 3
    inset.plot(fine, 100 * (3 * (1 - fine) / exact - 1), color=MUTED, lw=1.2)
    inset.axvline(0.97, color=INK, lw=0.7)
    inset.set_ylabel("linear excess [%]", fontsize=6.5)
    inset.set_xlabel("MM", fontsize=6.5)
    inset.tick_params(labelsize=6)
    inset.grid(True, alpha=0.4)
    save(fig, "f_volume_losses", """
The three volume losses kept apart, against nominal minimal match: the exact worst case
1 - MM^3, its linear expansion 3(1 - MM), and the metric-predicted population average
1 - <M^3> from injections, evaluated with the quadratic metric. TaylorF2 injections, so
this is modelled discretisation loss alone. Error bars show the injection bootstrap; the
inset resolves the relative excess of the linear expansion over the exact curve.
HOW THIS COULD FAIL (F4): if the worst case described what this bank model predicts for
the population, the population points would lie on the black curve. They lie a factor 4
to 9 below it, and
the gap widens with MM. If sampling error were large enough to explain their separation,
the bootstrap intervals would overlap accordingly; they do not. The linear expansion sits
3.060909 % above the
exact curve at MM = 0.97 -- where the exact value is 0.087327, not the 0.08733 quoted
earlier -- which is why the two are never merged.
""")


def figure_veff():
    """The claim is the SIGN and the ~2 % size of the trend, so the ordinate is the
    relative change from the coarse end. Both trials models are drawn, because the
    difference between them is the result."""
    opt = json.loads((DATA / "part_f_optimum.json").read_text())
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.4), sharey=True)
    for ax, region in zip(axes, ("main", "extended")):
        for lattice, colour, marker in (("hexagonal", BLUE, "o"), ("square", ORANGE, "s")):
            for field, dash, fill, tag in (("v_eff", (0, (5, 2)), "none", "naive trials"),
                                           ("v_eff_calibrated", "-", colour,
                                            "calibrated $\\nu_{\\rm eff}$")):
                xs, ys = [], []
                base = None
                for mm in MM_GRID:
                    e = opt.get(region, {}).get(f"{lattice}_mm{round(mm * 100):03d}")
                    if not e or not e.get(field):
                        continue
                    v = e[field]["far_1_per_100yr"]["taylorf2"]
                    base = base or v
                    xs.append(mm); ys.append(100 * (v / base - 1))
                if xs:
                    ax.plot(xs, ys, color=colour, linestyle=dash, marker=marker, ms=5,
                            lw=1.6, markerfacecolor=fill, markeredgecolor=colour,
                            label=f"{lattice}, {tag}")
        ax.axhline(0.0, color=MUTED, lw=0.8)
        ax.axvspan(0.945, VALIDATED_FROM, color=MUTED, alpha=0.12, lw=0)
        ax.grid(True, alpha=0.5)
        ax.set_xlabel("nominal minimal match MM")
        ax.set_title(f"{region} region", fontsize=9, color=INK, loc="left")
    axes[0].set_ylabel("derived sensitivity-proxy change from MM = 0.95  [%]")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.subplots_adjust(bottom=0.30)
    fig.legend(handles, labels, fontsize=7.5, ncol=2, loc="lower center",
               bbox_to_anchor=(0.5, -0.06))
    save(fig, "f_veff_vs_mm", """
Change in the derived relative sensitivity proxy from the coarse end of the grid, under
two scenarios for the trials factor. Dashed with open markers: the naive bound
N_templates x f_sample x T_obs. Solid with filled markers: nu_eff calibrated on
simulated Gaussian noise (100 segments of 32 s, seed 20260926, the same noise for every
bank). Curves are shown without precision-style uncertainty bars because uncertainty and
tail extrapolation in nu_eff have not been propagated; the stored injection-bootstrap
error alone would be misleadingly incomplete. Shaded: below MM = 0.97 the quadratic
predictor is outside the range q1bC validated.
THE RESULT IS THE DIFFERENCE BETWEEN THE TWO MODELS. The naive bound makes V_eff fall
by 1.9-3.7 % across the grid; the calibrated one makes it rise by 0.2-1.8 %. The sign of
the trend therefore depends on how the trials factor is modelled. This comparison does
not establish that the fitted model is valid at the detection threshold.
WHAT IT DOES NOT SHOW: nu_eff is calibrated near the simulated maxima and extrapolated
to a higher detection threshold. It varies across the observed tail, and that calibration
uncertainty is unquantified here; the curves are model scenarios, not a measurement of the
trend at the operating threshold.
HOW THIS COULD FAIL (F4): if the two models agreed, the dashed and solid curves would
lie on top of each other and the choice would not matter. They do not. If instead the
calibrated curves showed a clear interior peak, the pre-registered hypothesis would be
supported; they are flat to within about 2 % and NOT monotonic -- extended hexagonal
wobbles inside the grid -- so no robust optimum is resolved
inside the grid.
""")


def main():
    if "SOURCE_DATE_EPOCH" not in os.environ:
        os.environ["SOURCE_DATE_EPOCH"] = "1758844800"
    setup()
    print("figures")
    figure_covering()
    figure_counts()
    figure_mismatch_map()
    figure_trials()
    figure_volume_losses()
    figure_veff()


if __name__ == "__main__":
    main()
