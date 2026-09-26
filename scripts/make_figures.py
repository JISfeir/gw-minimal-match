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
        ax.set_xlabel("best match in the bank")
        ax.set_title(f"{region} region", fontsize=9, color=INK, loc="left")
    axes[0].set_ylabel("cumulative fraction of injections")
    axes[1].legend(fontsize=7.5, loc="lower right")
    save(fig, "d_covering_cumulative", """
Cumulative distribution of the best match each injection finds in the bank, at
nominal MM = 0.97, interior and border injections apart. 3000 injections per region,
uniform in component mass, seed 20260925; the match is the quadratic form evaluated
with the injection's own metric.
HOW THIS COULD FAIL (F4): if the banks did not cover, a visible fraction of each curve
would lie left of the MM = 0.97 line. The extended hexagonal curve does cross it -- 2
injections in 3000 -- and that is the measured covering failure, not a plotting
artefact. A bank that covered perfectly would show every curve reaching 1 strictly to
the right of the line. The log ordinate is what makes a 1-in-1000 failure visible at
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
    bottom.axhspan(0.7165, 0.7195, color=ORANGE, alpha=0.45, lw=0,
                   label="0.717–0.719  Cokelaer 2007, measured")
    bottom.set_ylim(0.60, 0.90)
    bottom.set_xlabel("nominal minimal match MM")
    bottom.set_ylabel("$N_{\\rm hex}/N_{\\rm square}$")
    bottom.grid(True, alpha=0.5)
    bottom.legend(fontsize=7, loc="upper left", ncol=2, columnspacing=1.0)
    save(fig, "d_counts_and_ratio", """
Top: bank size against nominal minimal match, both regions and both lattices.
Bottom: the measured hexagonal/square count ratio against its two references -- the
ideal constant-metric value 0.7698 and the 0.717-0.719 Cokelaer 2007 measures once the
metric varies. The ordinate spans 0.60-0.86 so that the 5-point gap between those two
references is legible (rule F2).
HOW THIS COULD FAIL (F4): if lattice efficiency alone set the ratio, both regions would
sit on one horizontal line near 0.77. They do not: main stays at or above the ideal
(0.7744-0.8090) while extended falls through Cokelaer's band to 0.639 -- not
monotonically, since it first rises from 0.7122 to 0.7275, an earlier wording that said
otherwise was wrong and the efverify r01 audit caught it. The ratio is
therefore not a property of the two lattices here. The counts include the boundary
repair, which is 50.7 % of the main hexagonal bank and 17.0 % of the extended square
one, and that asymmetry is the candidate explanation this figure does not itself prove.
""")


def figure_mismatch_map():
    """Rule F3: the metric depends on (m1, m2), so at least one figure must show
    both and not collapse them."""
    blob = np.load(DATA / "fig_mismatch_map.npz")
    witness = json.loads((DATA / "fig_witnesses.json").read_text())["main_hexagonal"]
    fig, ax = plt.subplots(figsize=(4.6, 3.8))
    field = blob["mismatch"]
    mesh = ax.pcolormesh(blob["grid_m1"], blob["grid_m2"], field,
                         cmap="Blues", vmin=0.0, vmax=0.03, shading="nearest")
    over = np.ma.masked_where(~(field > 0.03), field)
    ax.pcolormesh(blob["grid_m1"], blob["grid_m2"], over, cmap="autumn_r",
                  vmin=0.03, vmax=0.04, shading="nearest")
    ax.plot(witness["m1"], witness["m2"], marker="x", ms=9, mew=2.0, color=ORANGE,
            linestyle="none",
            label=f"adaptive witness, $\\mu$ = {witness['mismatch']:.5f}")
    bar = fig.colorbar(mesh, ax=ax, pad=0.02)
    bar.set_label("mismatch $\\mu$ to the nearest template")
    bar.ax.axhline(0.03, color=INK, lw=1.0)
    ax.set_xlabel("$m_1\\ [M_\\odot]$"); ax.set_ylabel("$m_2\\ [M_\\odot]$")
    ax.set_title("main region, hexagonal bank", fontsize=9, color=INK, loc="left")
    ax.legend(fontsize=7.5, loc="upper left")
    save(fig, "d_mismatch_map_main_hex", """
Mismatch to the nearest template over the mass plane for the main-region hexagonal
bank at MM = 0.97, on a 90x90 grid restricted to the region. Shown against both masses
rather than against total mass, because the metric depends on both (rule F3).
HOW THIS COULD FAIL (F4): a bank that covered would be uniformly below 0.03 with no
cell in the warm overlay. On this grid none appears -- the grid's worst cell is 0.02893
-- yet the cross marks a point an adaptive search found at 0.03222, reproduced
independently by the dverify r03 audit. That is the figure's real content: a regular
grid of test points does not find the holes, and a figure built only from grid sampling
would wrongly show a covering bank.
""")


# --------------------------------------------------------------------------- E
def figure_threshold():
    opt = json.loads((DATA / "part_f_optimum.json").read_text())
    names = {"far_1_per_100yr": ("FAR = 1/(100 yr)", "-", "o"),
             "far_1_per_yr": ("FAR = 1/yr", "--", "s"),
             "five_sigma": ("5$\\sigma$ global", ":", "D")}
    fig, ax = plt.subplots(figsize=(5.0, 3.4))
    for (op, (label, dash, marker)), colour in zip(names.items(), (BLUE, AQUA, YELLOW)):
        xs, ys = [], []
        for mm in MM_GRID:
            entry = opt["main"].get(f"hexagonal_mm{round(mm * 100):03d}")
            if entry:
                xs.append(mm); ys.append(entry["rho_star"][op])
        ax.plot(xs, ys, color=colour, linestyle=dash, marker=marker, ms=4.5, lw=1.6,
                label=label)
    ax.axvspan(0.945, VALIDATED_FROM, color=MUTED, alpha=0.12, lw=0)
    ax.annotate("outside the range where q1bC\nvalidated the quadratic predictor",
                (0.9525, 9.35), fontsize=7, color=MUTED)
    ax.set_xlabel("nominal minimal match MM")
    ax.set_ylabel("threshold $\\rho^*$")
    ax.grid(True, alpha=0.5); ax.legend(fontsize=7.5, loc="center right")
    ax.set_title("main region, hexagonal bank", fontsize=9, color=INK, loc="left")
    save(fig, "e_threshold_vs_mm", """
Detection threshold against nominal minimal match, at the pre-registered operating
point and its two sensitivities, solving FAP = 1 - (1 - p)^N exactly with
p = exp(-rho^2/2) from q1bC part A.
HOW THIS COULD FAIL (F4): rho* depends on the trials count only logarithmically, so
tripling the bank between MM = 0.95 and 0.99 should move it by of order 1 %. It moves
1.46 %. A curve that rose steeply would mean the trials model or the tail was wrong.
The naive trials count is now known to be a genuine UPPER bound, not merely a plausible
one: for a finite bank-and-time grid in centred Gaussian noise with fixed templates, the
Gaussian correlation inequality (Latala and Matlak, arXiv:1512.08776, Thm 1) gives
FAP(rho) <= 1 - (1 - exp(-rho^2/2))^N, proved by the efverify r01 verifier. It still does
not calibrate the effective trials, nor cover a continuous-time search.
WHAT THIS FIGURE DOES NOT SHOW: the trials count is the naive bound
N_templates x f_sample x T_obs, not a calibrated nu_eff estimated from simulated noise.
It over-counts trials, so every rho* here is an upper bound, and the pre-registered
figure -- a measured false-alarm rate on simulated noise against the nu_eff prediction
-- was not produced.
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
            xs, ys = [], []
            for mm in MM_GRID:
                entry = opt.get(region, {}).get(f"{lattice}_mm{round(mm * 100):03d}")
                if entry:
                    xs.append(mm); ys.append(entry["losses"]["population_taylorf2"])
            if xs:
                ax.plot(xs, ys, color=colour, linestyle=dash, marker=marker, ms=4.5,
                        lw=1.6, label=f"measured, {LABEL[key]}")
    ax.set_yscale("log")
    ax.set_xlabel("nominal minimal match MM")
    ax.set_ylabel("fractional detection-volume loss")
    ax.grid(True, alpha=0.5)
    # Outside the data area: with six series every in-plot corner crosses one of them.
    ax.legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.02, 1.0),
              borderaxespad=0.0)
    save(fig, "f_volume_losses", """
The three volume losses kept apart, against nominal minimal match: the exact worst case
1 - MM^3, its linear expansion 3(1 - MM), and the measured population average
1 - <M^3> from injections. TaylorF2 injections, so this is discretisation loss alone.
HOW THIS COULD FAIL (F4): if the worst case described what a bank actually costs, the
measured points would lie on the black curve. They lie a factor 4 to 9 below it, and
the gap widens with MM. If instead the population loss were an artefact of too few
injections, the four measured series would scatter rather than order themselves cleanly
by lattice and region. The linear expansion sits 3.060909 % above the
exact curve at MM = 0.97 -- where the exact value is 0.087327, not the 0.08733 quoted
earlier -- which is why the two are never merged.
""")


def figure_veff():
    opt = json.loads((DATA / "part_f_optimum.json").read_text())
    fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.2), sharex=True)
    for ax, leg, title in zip(axes, ("taylorf2", "imrphenomd_approx"),
                              ("TaylorF2 — discretisation only",
                               "IMRPhenomD — declared approximation")):
        for region in ("main", "extended"):
            for lattice in ("hexagonal", "square"):
                key = f"{region}_{lattice}"
                colour, dash, marker = STYLE[key]
                xs, ys, es = [], [], []
                for mm in MM_GRID:
                    e = opt.get(region, {}).get(f"{lattice}_mm{round(mm * 100):03d}")
                    if e:
                        xs.append(mm)
                        ys.append(e["v_eff"]["far_1_per_100yr"][leg])
                        es.append(e["v_eff_error"]["far_1_per_100yr"][leg])
                if xs:
                    ax.errorbar(xs, np.asarray(ys) * 1e3, yerr=np.asarray(es) * 1e3,
                                color=colour, linestyle=dash, marker=marker, ms=4.5,
                                lw=1.6, capsize=2.5, label=LABEL[key])
        ax.axvspan(0.945, VALIDATED_FROM, color=MUTED, alpha=0.12, lw=0)
        ax.grid(True, alpha=0.5)
        ax.set_xlabel("nominal minimal match MM")
        ax.set_title(title, fontsize=8.5, color=INK, loc="left")
    axes[0].set_ylabel("$V_{\\rm eff}$  [arb. units $\\times 10^{3}$]")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.subplots_adjust(bottom=0.26)
    fig.legend(handles, labels, fontsize=7.5, ncol=4, loc="lower center",
               bbox_to_anchor=(0.5, -0.02))
    save(fig, "f_veff_vs_mm", """
Effective detection volume V_eff = <M^3>/rho*^3 against nominal minimal match, with
bootstrap uncertainties (400 resamples of 2000 injections). Shaded: below MM = 0.97 the
quadratic predictor is outside the range q1bC validated, so points there are
provisional.
HOW THIS COULD FAIL (F4): the pre-registered hypothesis was that the threshold rise and
the finer bank roughly balance between MM = 0.97 and 0.99, producing an interior maximum
there. That would appear as a peak inside the plotted range. None appears: every grid
maximum sits at the coarse edge, so the hypothesis is refuted as stated.
NOT MONOTONIC, and the earlier wording that said so was wrong: main hexagonal RISES from
MM = 0.95 to 0.96 by 1.088e-6 before falling. The efverify r01 audit caught it, and its
larger samples (8000 injections per region) do not reproduce that 0.96 maximum -- every
one of its maxima is at 0.95. Treat the 0.96 point as within sampling noise.
Note the ordinate range: the whole variation is 1.9 % (main hexagonal) to 3.7 % (extended
square) across a threefold change in bank size, so the honest reading is that MM barely
moves V_eff, not that one should place coarse.
CONDITIONAL ON THE TRIALS MODEL, which the error bars do not cover. With N_eff growing as
N^alpha rather than N, the maximum leaves MM = 0.95 at alpha = 0.85 / 0.68 / 0.46 / 0.66
in the order plotted, and at alpha = 0.5 the preferred values are MM = 0.98 / 0.97 / 0.95
/ 0.96. A calibrated nu_eff would therefore be likely to move the optimum to finer banks,
and the curve above is what the naive bound gives, not what the search would do.
""")


def main():
    if "SOURCE_DATE_EPOCH" not in os.environ:
        os.environ["SOURCE_DATE_EPOCH"] = "1758844800"
    setup()
    print("figures")
    figure_covering()
    figure_counts()
    figure_mismatch_map()
    figure_threshold()
    figure_volume_losses()
    figure_veff()


if __name__ == "__main__":
    main()
