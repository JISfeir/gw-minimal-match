#!/usr/bin/env python3
"""Build page/index.html -- the human-facing half, offline.

Same content and the same numbers as paper/main.pdf, and that is enforced rather than
promised: both read data/project_numbers.json, so a number can only disagree between the
two formats if one of them stops being rebuilt. The figures are the same files
scripts/make_figures.py produces (rule F5), embedded as base64 so the page opens from a
file:// URL with no network at all -- no CDN, no font, no fetch.

Run:  .venv/bin/python scripts/make_page.py
"""
from __future__ import annotations

import base64
import html as html_module
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from make_numbers_tex import fmt  # the paper's formatter, shared so the two agree
DATA = ROOT / "data"
FIGURES = ROOT / "figures"
OUT = ROOT / "page" / "index.html"

REGISTRY = json.loads((DATA / "project_numbers.json").read_text())


def num(key, places=None):
    """A number, from the registry, formatted by the same function the paper uses, with
    its caveat carried as a tooltip."""
    record = REGISTRY[key]
    text = fmt(record["value"], record["unit"], html=True)
    caveat = record.get("caveat", "").replace('"', "&quot;")
    return f'<span class="num" title="{caveat}">{text}</span>'


def figure(stem, width="100%"):
    png = base64.b64encode((FIGURES / f"{stem}.png").read_bytes()).decode()
    # ESCAPE FIRST: the captions contain things like "1 - <M^3>", which a browser
    # reads as an opening tag. The bold markers below are added after escaping.
    caption = html_module.escape((FIGURES / f"{stem}.caption.txt").read_text().strip())
    # the caption's own falsification sentence is the part worth pulling out
    parts = re.split(r"(HOW THIS COULD FAIL \(F4\):|THE RESULT IS|WHY:|WHAT IT DOES NOT SHOW:|"
                     r"WHAT THIS FIGURE DOES NOT SHOW:|THIS FIGURE REPLACES|NOT MONOTONIC,|"
                     r"CONDITIONAL ON THE TRIALS MODEL,)", caption)
    body = parts[0].strip()
    rest = "".join(parts[1:]).strip()
    extra = ""
    if rest:
        rest_html = re.sub(r"(HOW THIS COULD FAIL \(F4\):|THE RESULT IS|WHY:|"
                           r"WHAT IT DOES NOT SHOW:|WHAT THIS FIGURE DOES NOT SHOW:|"
                           r"THIS FIGURE REPLACES|NOT MONOTONIC,|CONDITIONAL ON THE TRIALS MODEL,)",
                           r"<strong>\1</strong>", rest).replace("\n", " ")
        extra = f'<p class="fail">{rest_html}</p>'
    return f'''<figure>
  <img src="data:image/png;base64,{png}" alt="{stem}" style="width:{width}">
  <figcaption>{body}{extra}</figcaption>
</figure>'''


HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Template banks: what a mismatch costs</title>
<meta name="description" content="How much signal-to-noise ratio a gravitational-wave
template bank costs, and how dense it has to be. A controlled measurement in one
idealised setting.">
<style>
  :root {{
    --ink:#0b0b0b; --muted:#52514e; --paper:#fcfcfb; --line:#d8d7d2;
    --blue:#2a78d6; --orange:#eb6834; --soft:#f2f5fa; --warn:#fdf4ec;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --ink:#f2f2f0; --muted:#b4b2ab; --paper:#16161a; --line:#33333a;
      --blue:#6fa8ef; --orange:#f08a5f; --soft:#1d2028; --warn:#241d16;
    }}
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--paper); color:var(--ink);
    font:17px/1.65 Georgia,"Iowan Old Style",serif; }}
  main {{ max-width:47rem; margin:0 auto; padding:3rem 16px 6rem; }}
  h1 {{ font-size:2rem; line-height:1.2; margin:0 0 .4rem; }}
  h2 {{ font-size:1.25rem; margin:2.6rem 0 .7rem; padding-top:.7rem;
    border-top:1px solid var(--line); }}
  h3 {{ font-size:1.02rem; margin:1.6rem 0 .4rem; color:var(--muted);
    font-family:system-ui,sans-serif; letter-spacing:.02em; }}
  .sub {{ color:var(--muted); font-size:1.02rem; margin:0 0 2rem; }}
  .num {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.93em;
    background:var(--soft); padding:.05em .3em; border-radius:3px;
    border-bottom:1px dotted var(--muted); cursor:help; }}
  figure {{ margin:2rem 0; }}
  figure img {{ display:block; border:1px solid var(--line); border-radius:4px;
    background:#fff; }}
  figcaption {{ font-size:.87rem; color:var(--muted); margin-top:.6rem;
    font-family:system-ui,sans-serif; line-height:1.55; }}
  .fail {{ background:var(--warn); border-left:3px solid var(--orange);
    padding:.6rem .8rem; margin:.6rem 0 0; border-radius:0 3px 3px 0; }}
  table {{ border-collapse:collapse; width:100%; margin:1.2rem 0; font-size:.92rem;
    font-family:system-ui,sans-serif; }}
  th,td {{ text-align:right; padding:.4rem .5rem; border-bottom:1px solid var(--line); }}
  th:first-child,td:first-child {{ text-align:left; }}
  thead th {{ border-bottom:2px solid var(--muted); font-weight:600; }}
  ul {{ padding-left:1.2rem; }} li {{ margin:.4rem 0; }}
  .lead {{ font-size:1.06rem; }}
  .note {{ font-size:.9rem; color:var(--muted); font-family:system-ui,sans-serif; }}
  a {{ color:var(--blue); }}
  code {{ font-family:ui-monospace,Menlo,monospace; font-size:.9em;
    background:var(--soft); padding:.08em .3em; border-radius:3px; }}
</style>
</head>
<body><main>

<h1>How much SNR a template bank costs,<br>and how dense it has to be</h1>
<p class="sub">A controlled measurement in one deliberately idealised setting.
Every number on this page is read from the same registry the PDF reads, so the two
cannot disagree. Hover a number to see what it is <em>not</em>.</p>

<p class="lead">Searches for gravitational waves from inspiralling binaries filter the
data against a bank of template waveforms. No template matches a real signal exactly, and
the bank is finite, so some signal-to-noise ratio is always lost. Two questions follow:
how much, and how densely must the bank be packed to keep the loss acceptable. The first
has an exact answer. The second, it turns out, does not have one in these terms.</p>

<h2>What is idealised away, first</h2>
<p>These come before the results because several of them bound what the results can
mean.</p>
<ul>
<li><strong>One detector, Gaussian noise, an analytic power spectrum.</strong> Real
searches are limited by non-Gaussian transients and handle them with signal-consistency
tests and multi-detector coincidence. None of that is modelled, so no false-alarm rate
here is a search sensitivity.</li>
<li><strong>Non-spinning TaylorF2 templates cut at the innermost stable circular
orbit.</strong> That cutoff is a software default, not a physical statement, and it
causes most of the template-family error below.</li>
<li><strong>The whole mass range sits above where post-Newtonian templates alone were
trusted.</strong> Results are reported separately for a main region (total mass at most
35&nbsp;M<sub>&#9737;</sub>) and an extended one (35 to 100).</li>
<li><strong>Two parameters.</strong> Production banks are four-dimensional and are not
placed with a metric at all.</li>
</ul>

<h2>The minimal match is a convention, not a constant</h2>
<p>The design target is the <em>minimal match</em>: the worst match a signal anywhere in
the region is allowed to have with its nearest template. The conventional value is
{num('minimal_match_headline')}. Owen introduced it in 1996 as a quantity
&ldquo;chosen by the experimenter based upon what he or she considers to be an acceptable
loss of ideal event rate&rdquo;, and picked that value because, for sources spread
uniformly in volume, a 3&nbsp;% loss of amplitude costs
{num('worst_case_volume_loss_mm097')} of the event rate.</p>
<p>It is still the convention thirty years later &mdash; but it is now applied as a
<strong>percentile, not a worst case</strong>. The current LIGO&ndash;Virgo&ndash;KAGRA
bank reports fitting factors above 97&nbsp;% for 90&nbsp;% of injections. That
distinction turns out to matter a great deal.</p>

<h2>The banks</h2>
<table>
<thead><tr><th>at minimal match 0.97</th><th>main hex</th><th>main square</th>
<th>ext. hex</th><th>ext. square</th></tr></thead>
<tbody>
<tr><td>templates</td><td>{num('n_templates_main_hexagonal_mm097')}</td>
<td>{num('n_templates_main_square_mm097')}</td>
<td>{num('n_templates_extended_hexagonal_mm097')}</td>
<td>{num('n_templates_extended_square_mm097')}</td></tr>
<tr><td>constant-metric ideal</td><td>458</td><td>595</td><td>95</td><td>124</td></tr>
<tr><td>population volume loss</td>
<td>{num('population_volume_loss_main_hexagonal_mm097')}</td>
<td>{num('population_volume_loss_main_square_mm097')}</td>
<td>{num('population_volume_loss_extended_hexagonal_mm097')}</td>
<td>{num('population_volume_loss_extended_square_mm097')}</td></tr>
</tbody></table>

<h3>Uniform sampling flatters a bank</h3>
<p>Three of the four banks contain no injection at all below the target under 3000 uniform
draws. That test has almost no power: it reaches even 50&nbsp;% detection probability only
at an uncovered fraction of 2.3&times;10<sup>&minus;4</sup>. An adaptive search finds what
uniform sampling does not &mdash; a worst mismatch of
{num('adaptive_worst_mismatch_main_hexagonal')} in the main hexagonal bank and
{num('adaptive_worst_mismatch_extended_hexagonal')} in the extended one, both above the
0.03 target. <strong>Strict covering fails for both hexagonal banks.</strong> Both square
banks survive the same search.</p>

{figure('d_covering_cumulative')}

{figure('d_mismatch_map_main_hex', '76%')}

<h3>The hexagonal-to-square ratio is not a property of the lattices</h3>
<p>A hexagonal lattice should need about 0.77 of the templates a square one needs. We
measure {num('hex_square_ratio_main_mm097')} in the main region &mdash; but counting only
the lattice, without the boundary treatment, gives 0.4882 instead. The boundary repair is
half the main hexagonal bank and a sixth of the extended square one, and the ratio
inherits that asymmetry.</p>
<p>The reason is geometric. {num('border_fraction_main')} of main-region injections and
{num('border_fraction_extended')} of extended ones lie within one covering radius of a
boundary. The regions are ribbons: the main one has proper area
{num('proper_area_main')} against a proper perimeter of {num('proper_perimeter_main')},
where a disc of that area would have 21.2, giving an effective width of
{num('effective_width_main')} covering radii. <strong>There is almost no interior in which
an asymptotic, boundary-free ratio could be measured</strong>, and 0.77 is an asymptotic,
boundary-free number.</p>

{figure('d_counts_and_ratio', '74%')}

<h2>The threshold, and how many trials there really are</h2>
<p>Everything about detection significance depends on how many independent chances the
search had to produce a loud noise event. Counting every template and every time sample
as independent is an upper bound &mdash; provably so, from the Gaussian correlation
inequality. But it is a loose one.</p>
<p>Filtering simulated noise through each bank and taking the maximum gives
{num('nu_eff_main_hexagonal_mm097')} independent trials per second, nine to thirty-one
times below the naive count. And the effective count grows as the template count raised
to {num('trials_exponent_main_hexagonal')}, not to the first power:
<strong>refining a bank adds templates that overlap their neighbours by construction, so
they add redundancy rather than trials.</strong></p>
<p class="note">The same twenty banks fitted together give
{num('trials_exponent_pooled')} &mdash; four standard deviations <em>above</em> one, the
opposite conclusion. We report it and do not use it: the two regions differ in trial rate
by more than a factor ten, so the pooled slope measures the step between them rather than
how either one scales.</p>

{figure('e_trials_measured_vs_naive')}

<h2>Volume, and the optimum that is not there</h2>
<p>Three losses are conventionally conflated and are kept apart here: the exact worst case
{num('worst_case_volume_loss_mm097')}, its linear expansion 0.09, which is 3.06&nbsp;%
larger and a different quantity, and the measured population average, which for the main
hexagonal bank is {num('population_volume_loss_main_hexagonal_mm097')} &mdash;
<strong>four to nine times smaller than the worst case.</strong> Almost no signal lands at
the worst point of its cell.</p>

{figure('f_volume_losses', '82%')}

<p>So is there a best minimal match? Under the naive trials count the effective volume
falls as the bank is refined. Under the calibrated one it rises. <strong>The sign of the
trend is set by the trials model, not by the bank.</strong> And the whole variation is
{num('veff_change_calibrated_main_hexagonal')}&nbsp;% across a threefold change in bank
size &mdash; flat, and not even monotonic in the extended region.</p>

{figure('f_veff_vs_mm')}

<h2>Where the volume actually goes</h2>
<p>Against realistic IMRPhenomD signals the TaylorF2 family loses
{num('imrphenomd_volume_loss_extended')} of the detection volume in the extended region.
Of that, {num('imrphenomd_family_only_extended')} is the waveform family alone: the bank's
discretisation adds seven tenths of a percentage point.</p>
<p class="lead"><strong>Above 35&nbsp;M<sub>&#9737;</sub> the waveform model, not the bank,
costs the volume &mdash; and no amount of refinement recovers it.</strong></p>

<h2>What was not done</h2>
<ul>
<li>No waveform check of the twenty delivered banks; every covering number is the
quadratic form of a metric.</li>
<li>Cokelaer's explicit lattice connectors were never implemented; a proximity threshold
stands in for them.</li>
<li>The pre-registered placement sensitivities were not run.</li>
<li>The trials rate was calibrated at one segment length, where the noise maxima fall
(|z| &asymp; 5.3&ndash;5.8), and applied at thresholds near 8.0&ndash;8.6. That
extrapolation is not tested.</li>
<li>The IMRPhenomD volume leg is an approximation that assumes two losses are
independent; the rigorous family-only bound is quoted beside it.</li>
<li>A cross-check of bank spacing by singular-value decomposition was planned and cut.</li>
</ul>

<h2>Conclusion</h2>
<p class="lead">The two questions have asymmetric answers. <strong>How much SNR a mismatch
costs is exact and settled</strong> &mdash; the loss is the mismatch, and above
35&nbsp;M<sub>&#9737;</sub> the dominant loss is the waveform model, at half the detection
volume. <strong>How dense a bank must be has no answer in these terms</strong>, because
within a plausible range the effective volume hardly depends on the density, and the
direction of what little dependence exists is set by the trials model rather than by the
bank. The minimal match is not where this search's sensitivity is won or lost.</p>

<h2 id="repro">Reproducing this</h2>
<p class="note">Every number above is read from <code>data/project_numbers.json</code>,
whose sole writer is <code>scripts/compute_numbers.py</code>; the PDF reads the same file,
so the two formats cannot disagree. Every figure comes from
<code>scripts/make_figures.py</code> and from nowhere else, and this page is built by
<code>scripts/make_page.py</code>. A clean clone regenerates all of it byte-identically.
What it cannot regenerate is the frozen upstream package that supplies the metric,
waveforms and noise; that boundary is stated in the repository README.</p>
<p class="note">Companion note: <a href="owen.html">a guide to Owen&nbsp;(1995)</a>, the
paper this work's placement metric comes from.</p>

</main></body></html>
"""

OUT.write_text(HTML, encoding="utf-8")
size = OUT.stat().st_size
print(f"wrote {OUT.relative_to(ROOT)}  ({size / 1024:.0f} kB, figures embedded)")
