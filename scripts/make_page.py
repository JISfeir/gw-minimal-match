#!/usr/bin/env python3
"""Build the offline human-facing HTML page.

The HTML and paper state the same scientific claims and cite the same project-number
keys.  The HTML may include supplementary diagnostics that do not fit in the paper.
Both formats use the formatter and registry in data/project_numbers.json; literature
reference values used only in prose come from provenance/numbers.json.

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
from make_numbers_tex import fmt

DATA = ROOT / "data"
FIGURES = ROOT / "figures"
OUT = ROOT / "page" / "index.html"
REGISTRY = json.loads((DATA / "project_numbers.json").read_text())
PROVENANCE_NUMBERS = json.loads((ROOT / "provenance" / "numbers.json").read_text())


def num(key):
    """Render a project result with the same formatter used by the paper."""
    record = REGISTRY[key]
    text = fmt(record["value"], record["unit"], html=True)
    caveat = html_module.escape(record.get("caveat", ""), quote=True)
    return f'<span class="num" title="{caveat}">{text}</span>'


def prov_num(key, places=4):
    """Render a literature or document number from the provenance registry."""
    record = PROVENANCE_NUMBERS[key]
    text = f"{record['value']:.{places}f}"
    caveat = html_module.escape(" ".join(record["choices"]), quote=True)
    return f'<span class="num" title="{caveat}">{text}</span>'


def figure(stem, width="100%"):
    """Embed a generated figure and its registered explanatory caption."""
    png = base64.b64encode((FIGURES / f"{stem}.png").read_bytes()).decode()
    caption = html_module.escape((FIGURES / f"{stem}.caption.txt").read_text().strip())
    parts = re.split(
        r"(HOW THIS COULD FAIL \(F4\):|THE RESULT IS|WHY:|WHAT IT DOES NOT SHOW:|"
        r"WHAT THIS FIGURE DOES NOT SHOW:|THIS FIGURE REPLACES|NOT MONOTONIC,|"
        r"CONDITIONAL ON THE TRIALS MODEL,)",
        caption,
    )
    body = parts[0].strip().replace("\n", " ")
    rest = "".join(parts[1:]).strip()
    extra = ""
    if rest:
        rest_html = re.sub(
            r"(HOW THIS COULD FAIL \(F4\):|THE RESULT IS|WHY:|"
            r"WHAT IT DOES NOT SHOW:|WHAT THIS FIGURE DOES NOT SHOW:|"
            r"THIS FIGURE REPLACES|NOT MONOTONIC,|CONDITIONAL ON THE TRIALS MODEL,)",
            r"<strong>\1</strong>",
            rest,
        ).replace("\n", " ")
        extra = f'<p class="fail">{rest_html}</p>'
    return f'''<figure>
  <img src="data:image/png;base64,{png}" alt="{stem}" style="width:{width}">
  <figcaption>{body}{extra}</figcaption>
</figure>'''


def check_shared_number_keys():
    """Fail the build if HTML and LaTeX stop citing the same project results."""
    source = Path(__file__).read_text()
    html_keys = set(re.findall(r"(?<![A-Za-z_])num\('([^']+)'\)", source))
    tex = (ROOT / "paper" / "main.tex").read_text()
    paper_keys = {key.replace("-", "_") for key in re.findall(r"\\dataref\{([^}]+)\}", tex)}
    if html_keys != paper_keys:
        only_html = sorted(html_keys - paper_keys)
        only_paper = sorted(paper_keys - html_keys)
        raise RuntimeError(
            "HTML/PDF project-number keys differ: "
            f"HTML only={only_html}; paper only={only_paper}"
        )


HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Minimal match and SNR loss from imperfect templates</title>
<meta name="description" content="Minimal match, template-bank placement and SNR loss
in a controlled two-parameter gravitational-wave study.">
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
  main {{ max-width:49rem; margin:0 auto; padding:3rem 16px 6rem; }}
  h1 {{ font-size:2rem; line-height:1.2; margin:0 0 .4rem; }}
  h2 {{ font-size:1.3rem; margin:2.6rem 0 .7rem; padding-top:.7rem;
    border-top:1px solid var(--line); }}
  h3 {{ font-size:1.03rem; margin:1.6rem 0 .4rem; color:var(--muted);
    font-family:system-ui,sans-serif; letter-spacing:.02em; }}
  .sub {{ color:var(--muted); font-size:1.02rem; margin:0 0 2rem; }}
  .lead {{ font-size:1.06rem; }}
  .answers {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(18rem,1fr));
    gap:1rem; margin:1.2rem 0; }}
  .answer {{ background:var(--soft); padding:.25rem 1rem .8rem; border-radius:4px;
    border-top:3px solid var(--blue); }}
  .answer h3 {{ color:var(--ink); margin-top:.8rem; }}
  .num {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:.93em;
    background:var(--soft); padding:.05em .3em; border-radius:3px;
    border-bottom:1px dotted var(--muted); cursor:help; }}
  .eq {{ text-align:center; margin:1rem 0; font-size:1.05rem; }}
  .note {{ font-size:.9rem; color:var(--muted); font-family:system-ui,sans-serif; }}
  .method {{ background:var(--soft); padding:.8rem 1rem; border-radius:4px; }}
  figure {{ margin:2rem 0; }}
  figure img {{ display:block; margin:auto; border:1px solid var(--line); border-radius:4px;
    background:#fff; max-width:100%; height:auto; }}
  figcaption {{ font-size:.87rem; color:var(--muted); margin-top:.6rem;
    font-family:system-ui,sans-serif; line-height:1.55; }}
  .fail {{ background:var(--warn); border-left:3px solid var(--orange);
    padding:.6rem .8rem; margin:.6rem 0 0; border-radius:0 3px 3px 0; }}
  table {{ border-collapse:collapse; width:100%; margin:1.2rem 0; font-size:.9rem;
    font-family:system-ui,sans-serif; }}
  th,td {{ text-align:right; padding:.4rem .45rem; border-bottom:1px solid var(--line); }}
  th:first-child,td:first-child {{ text-align:left; }}
  thead th {{ border-bottom:2px solid var(--muted); font-weight:600; }}
  ul,ol {{ padding-left:1.25rem; }} li {{ margin:.4rem 0; }}
  details {{ margin:1.2rem 0; padding:.5rem .8rem; border:1px solid var(--line);
    border-radius:4px; }}
  summary {{ cursor:pointer; font-family:system-ui,sans-serif; font-weight:600; }}
  a {{ color:var(--blue); }}
  code {{ font-family:ui-monospace,Menlo,monospace; font-size:.9em;
    background:var(--soft); padding:.08em .3em; border-radius:3px; }}
</style>
</head>
<body><main>

<h1>Minimal match and SNR loss from imperfect templates</h1>
<p class="sub">The web companion to the paper. The scientific claims and headline
project values are shared with the PDF; this page adds supplementary diagnostics that do
not fit within its page limit. Hover a highlighted value to see its caveat.</p>

<p class="lead">We quantify the SNR and volume loss caused by an imperfect
gravitational-wave template in a deliberately restricted setting. Owen supplies the
matched-filter geometry. The bank growth is inspired by Cokelaer, but our implementation
replaces his explicit connector graph and adds its own boundary repair; it is therefore
not a faithful reproduction of his placement algorithm.</p>

<h2>1. Scope and definitions</h2>
<p>This is a controlled bank study, not a reproduction of an observational search. It
uses one detector, stationary Gaussian noise, the
<code>aLIGOZeroDetHighPower</code> PSD from 20 to 1024&nbsp;Hz, and non-spinning
TaylorF2 waveforms terminated at <i>f</i><sub>ISCO</sub>. Component masses run from
5 to 50 solar masses. Results are separated into a main region with total mass at most
35 solar masses and an extended region above it, where an inspiral-only model visibly
fails. Real searches additionally include spin dimensions, coincidence and rejection of
non-Gaussian transients.</p>

<p>For normalized waveforms, the match maximizes the overlap over coalescence time and
phase, and the mismatch is</p>
<p class="eq">&mu; = 1 &minus; &#8499;.</p>
<p>In noise-free data the recovered SNR fraction is exactly &#8499;. A nominal minimal
match MM bounds the design mismatch only if the bank actually covers the region. For
sources uniform in Euclidean volume, the exact nominal worst-case loss at
MM&nbsp;=&nbsp;{num('minimal_match_headline')} is
1&nbsp;&minus;&nbsp;MM<sup>3</sup>&nbsp;=&nbsp;{num('worst_case_volume_loss_mm097')}.
The population averages below instead use injections uniform in component mass. They are
<strong>not</strong> an astrophysical population model.</p>

<p>The symmetric mass ratio is</p>
<p class="eq">&eta; = m<sub>1</sub>m<sub>2</sub>/(m<sub>1</sub>+m<sub>2</sub>)<sup>2</sup>
&le; 1/4.</p>
<p>The upper bound follows from (m<sub>1</sub>&minus;m<sub>2</sub>)<sup>2</sup>&nbsp;&ge;&nbsp;0;
equality holds only for equal masses. Thus &eta;&nbsp;=&nbsp;1/4 is the physical
equal-mass boundary, whereas &mu; denotes mismatch.</p>

<h2>2. Method: Owen baseline and our placement</h2>
<h3>The metric we use</h3>
<div class="method">
<p>Following Owen, mismatch is expanded locally as
&mu;&nbsp;&asymp;&nbsp;g<sub>ij</sub>&Delta;&lambda;<sup>i</sup>&Delta;&lambda;<sup>j</sup>.
The implementation uses the analytic non-spinning 3.5PN TaylorF2 projected-phase metric
in chirp-time coordinates (&tau;<sub>0</sub>,&tau;<sub>3</sub>) at 20&nbsp;Hz. Constant
phase and time are projected out; the frequency weight is proportional to
|h(f)|<sup>2</sup>/S<sub>n</sub>(f). PyCBC supplies the waveform and PSD. Derivatives use
the base waveform's fixed TaylorF2 support ending at its <i>f</i><sub>ISCO</sub>.</p>
</div>
<p>A finite-difference calculation tests the quadratic predictor against a pre-registered
relative-error limit of {num('metric_validation_relative_error_limit')}. It passes at
mismatch 0.03 but not at 0.05; only those discrete radii were tested. Results below
MM&nbsp;=&nbsp;0.97 are therefore metric extrapolations.</p>

<h3>What comes from Cokelaer, and what we changed</h3>
<p>Owen supplies the metric and target spacing, but not the complete finite-region growth
rule used here. Square and hexagonal banks are grown generation by generation, with the
local metric recomputed at each parent, following the idea of Cokelaer's cell-by-cell
two-dimensional inspiral placement. Cells that cross &eta;&nbsp;=&nbsp;1/4 are projected
back only after reproduction, also following Cokelaer's prescription.</p>
<p>Two rules are ours:</p>
<ul>
<li><strong>No explicit connectors.</strong> Cokelaer's mother&ndash;daughter and
adjacent-daughter connector graph was replaced by a lattice-independent collision rule:
a proposal is rejected if it lies within one half of the local spacing of an existing
template, measured with the parent's metric. This makes both lattice implementations use
the same duplicate rule, but does not preserve Cokelaer's topology and has not been shown
equivalent to it.</li>
<li><strong>Boundary repair.</strong> After growth, a strip within one covering radius of
the region boundary is repaired greedily because the uncorrected banks left boundary
holes.</li>
</ul>
<p>Consequently, both the lattice-only and repaired template counts are properties of
this implementation. They must not be described as Cokelaer counts.</p>

<h2>3. Results</h2>
<h3>Waveform and discretisation losses</h3>
<p>In the declared interpolation model, the TaylorF2 family plus bank loses
{num('imrphenomd_volume_loss_main')} of the volume in the main region, compared with
{num('imrphenomd_family_only_main')} for the interpolated family-only estimate. In the extended
region the corresponding values are {num('imrphenomd_volume_loss_extended')} and
{num('imrphenomd_family_only_extended')}. The exact continuous-family loss would bound the
discrete-bank loss from below, but the 28-point interpolation has no demonstrated one-sided
error. Within this model, waveform-family error dominates bank discretisation at high mass.</p>

<table>
<thead><tr><th>nominal MM = 0.97</th><th>main hex.</th><th>main square</th>
<th>ext. hex.</th><th>ext. square</th></tr></thead>
<tbody>
<tr><td>templates</td><td>{num('n_templates_main_hexagonal_mm097')}</td>
<td>{num('n_templates_main_square_mm097')}</td>
<td>{num('n_templates_extended_hexagonal_mm097')}</td>
<td>{num('n_templates_extended_square_mm097')}</td></tr>
<tr><td>sampled covering fraction</td>
<td>{num('covering_fraction_main_hexagonal_mm097')}</td>
<td>{num('covering_fraction_main_square_mm097')}</td>
<td>{num('covering_fraction_extended_hexagonal_mm097')}</td>
<td>{num('covering_fraction_extended_square_mm097')}</td></tr>
<tr><td>population volume loss</td>
<td>{num('population_volume_loss_main_hexagonal_mm097')}</td>
<td>{num('population_volume_loss_main_square_mm097')}</td>
<td>{num('population_volume_loss_extended_hexagonal_mm097')}</td>
<td>{num('population_volume_loss_extended_square_mm097')}</td></tr>
</tbody></table>

<p>Uniform injections do not certify strict covering. Adaptive optimisation reaches
mismatch {num('adaptive_worst_mismatch_main_hexagonal')} in the main hexagonal bank and
{num('adaptive_worst_mismatch_extended_hexagonal')} in the extended hexagonal bank,
both above the target. These are counterexamples to strict covering, not certified global
maxima. The square banks survive the same search.</p>

{figure('d_counts_and_ratio', '78%')}

<p>The measured hexagonal-to-square ratios at the headline minimal match are
{num('hex_square_ratio_main_mm097')} in the main region and
{num('hex_square_ratio_extended_mm097')} in the extended region. The constant-metric,
boundary-free value is {prov_num('ideal_hex_square_ratio')}. Across the comparable banks
in Cokelaer's Tables I&ndash;II, the recomputed range is
{prov_num('cokelaer_hex_square_ratio_min')}&ndash;{prov_num('cokelaer_hex_square_ratio_max')}
and the mean is {prov_num('cokelaer_hex_square_ratio_mean')}. That range is descriptive,
not an uncertainty interval. Because our collision and boundary rules differ, this
comparison neither validates nor refutes Cokelaer's implementation.</p>

<p>Boundary sensitivity is expected: {num('border_fraction_main')} of main-region
injections and {num('border_fraction_extended')} of extended-region injections lie
within one covering radius of an edge. The count ratio consequently varies with region,
minimal match and boundary treatment; it is not a universal lattice constant here.</p>

{figure('f_volume_losses', '76%')}

<p>The population-average losses lie below the exact nominal worst case because typical
injections do not occupy a cell's worst point. This comparison applies only to the stated
uniform component-mass measure.</p>

<details>
<summary>Supplementary covering diagnostics</summary>
<p class="note">These figures are retained online but omitted from the page-limited PDF.
In the cumulative plot, every interior/border curve is normalized within its own subset;
the ordinate is conditional and is not a fraction of all injections.</p>
{figure('d_covering_cumulative')}
{figure('d_mismatch_map_main_hex', '76%')}
</details>

<h3>Threshold and effective volume</h3>
<p>Counting every template and time sample as independent is a conservative upper bound
for the finite correlated Gaussian grid, but it is loose. Fitting simulated-noise maxima
gives {num('nu_eff_main_hexagonal_mm097')} equivalent independent trials per second for
the main hexagonal MM&nbsp;=&nbsp;0.97 bank.</p>
<p>Within each fixed region and lattice, fits of
N<sub>eff</sub>&nbsp;&prop;&nbsp;N<sub>templates</sub><sup>&alpha;</sup> give
&alpha;&nbsp;=&nbsp;{num('trials_exponent_main_hexagonal')},
{num('trials_exponent_main_square')},
{num('trials_exponent_extended_hexagonal')} and
{num('trials_exponent_extended_square')}. Pooling unlike families gives
{num('trials_exponent_pooled')} instead, demonstrating that bank size by itself does not
define the trials factor.</p>

{figure('e_trials_measured_vs_naive')}

<p class="fail"><strong>Calibration limit.</strong> The fitted effective count varies
across the observed tail and is calibrated where the simulated maxima occur, then
extrapolated to a substantially higher detection threshold. It is an empirical model,
not a measured false-alarm rate at the operating point.</p>

<p>For the relative sensitivity proxy
V<sub>eff</sub>&nbsp;=&nbsp;&lang;&#8499;<sup>3</sup>&rang;/&rho;<sup>*3</sup>, the main
hexagonal value changes by {num('veff_change_naive_main_hexagonal')}&nbsp;% under naive
counting and by {num('veff_change_calibrated_main_hexagonal')}&nbsp;% under the fitted
trials model. Even the sign therefore depends on the trials model.</p>

{figure('f_veff_vs_mm')}

<p>The calibrated curves are nearly flat and do not resolve a robust optimum. They are
shown without precision-style uncertainty bars because uncertainty in the effective-trials
calibration and its tail extrapolation has not been quantified; an injection-only bar would
be misleadingly incomplete.</p>

<h2>4. Limitations</h2>
<ul>
<li>The delivered banks were not rechecked template by template with waveform overlaps;
covering is evaluated with the quadratic metric.</li>
<li>The connector implementation, globally anchored metric sensitivity,
discard-versus-project sensitivity and SVD cross-check were not completed.</li>
<li>The IMRPhenomD comparison approximately composes continuous-family and discretisation
effects.</li>
<li>The effective-trials calibration does not reach the detection tail.</li>
</ul>

<h2>5. Conclusion: answers to the two questions</h2>
<div class="answers">
<section class="answer">
<h3>How much SNR is lost?</h3>
<p>If the nearest template has match &#8499;, then in noise-free data the recovered SNR is
&rho;<sub>rec</sub>&nbsp;=&nbsp;&#8499;&rho;<sub>opt</sub>. The fractional SNR loss is
therefore exactly the mismatch, &mu;&nbsp;=&nbsp;1&nbsp;&minus;&nbsp;&#8499;. In the banks we
actually built at nominal MM&nbsp;=&nbsp;0.97, adaptive searches found losses of at least
{num('adaptive_worst_mismatch_main_hexagonal')} in the main hexagonal bank and
{num('adaptive_worst_mismatch_extended_hexagonal')} in the extended hexagonal bank,
both worse than the nominal 0.03. The square banks survived the same search, although
that is not a proof of strict covering.</p>
<p>The metric-predicted population-average <em>volume</em> losses were
{num('population_volume_loss_main_hexagonal_mm097')} (hexagonal) versus
{num('population_volume_loss_main_square_mm097')} (square) in the main region, and
{num('population_volume_loss_extended_hexagonal_mm097')} versus
{num('population_volume_loss_extended_square_mm097')} in the extended region. Against
IMRPhenomD signals, the approximate total loss for the hexagonal bank instead rises from
{num('imrphenomd_volume_loss_main')} in main to
{num('imrphenomd_volume_loss_extended')} in extended; most of that is already present in
the continuous TaylorF2 family
({num('imrphenomd_family_only_main')} and {num('imrphenomd_family_only_extended')}). Thus
the main/extended contrast is mainly a waveform-model result, not a bank-spacing result.</p>
</section>
<section class="answer">
<h3>How dense must the bank be?</h3>
<p>At MM&nbsp;=&nbsp;0.97, our main bank contains
{num('n_templates_main_hexagonal_mm097')} hexagonal templates versus
{num('n_templates_main_square_mm097')} square templates; the extended bank contains
{num('n_templates_extended_hexagonal_mm097')} versus
{num('n_templates_extended_square_mm097')}. The corresponding hexagonal-to-square count
ratios are {num('hex_square_ratio_main_mm097')} and
{num('hex_square_ratio_extended_mm097')}: hexagonal placement uses fewer templates in both
regions, but by different amounts.</p>
<p>That saving is not a free improvement. The denser square banks have the smaller
population-average losses above and survived the adaptive covering search, whereas both
hexagonal banks have counterexamples. Moreover, {num('border_fraction_main')} of main and
{num('border_fraction_extended')} of extended injections lie within one covering radius
of an edge. These narrow finite regions are boundary dominated, so neither the ideal
lattice ratio nor one universal density describes the delivered banks. We also find no
robust optimal minimal match: the small V<sub>eff</sub> trend changes sign with the trials
model.</p>
</section>
</div>

<h2 id="repro">Reproducibility</h2>
<p class="note">Every highlighted project result is read from
<code>data/project_numbers.json</code> through the same formatter used by the PDF.
<code>scripts/make_page.py</code> refuses to build if the HTML and LaTeX cite different
sets of project-number keys. Literature comparison values are read from
<code>provenance/numbers.json</code>. All figures are generated by
<code>scripts/make_figures.py</code>.</p>

<h2>References</h2>
<ol class="note">
<li><a href="../papers/gr-qc-9511032/owen1995.pdf">B. J. Owen, <i>Search templates for
gravitational waves from inspiraling binaries: choice of template spacing</i></a>.</li>
<li><a href="../papers/gr-qc-9808076/owen-sathyaprakash-1999.pdf">B. J. Owen and
B. S. Sathyaprakash, <i>Matched filtering of gravitational waves from inspiraling compact
binaries</i></a>.</li>
<li><a href="../papers/0706.4437/cokelaer-2007.pdf">T. Cokelaer, <i>Gravitational waves
from inspiralling compact binaries: hexagonal template placement</i></a>.</li>
<li><a href="../papers/gr-qc-0509116/allen-findchirp.pdf">B. Allen et al.,
<i>FINDCHIRP</i></a>.</li>
<li><a href="../papers/1508.02357/usman-2016.pdf">S. A. Usman et al., <i>The PyCBC
search for gravitational waves from compact binary coalescence</i></a>.</li>
<li><a href="../papers/1904.01683/roulet-2019.pdf">J. Roulet et al., <i>A general
geometric placement algorithm</i></a>.</li>
<li><a href="../papers/gr-qc-0404096/croce-2004.pdf">R. P. Croce et al., <i>The
minimal-match issue revisited</i></a>.</li>
<li><a href="../papers/1303.2005/keppel-2013.pdf">D. Keppel, <i>The balancing act of
template bank construction</i></a>.</li>
<li><a href="../papers/2211.16674/sakon-2023.pdf">S. Sakon et al., <i>Template bank for
the fourth observing run</i></a>.</li>
<li><a href="https://arxiv.org/abs/1512.08776">R. Lata&#322;a and D. Matlak,
<i>Royen's proof of the Gaussian correlation inequality</i></a>.</li>
</ol>

<p class="note">Companion note: <a href="owen.html">a guide to Owen's metric paper</a>.
PDF version: <a href="../paper/main.pdf">paper/main.pdf</a>.</p>

</main></body></html>
"""


check_shared_number_keys()
ROOT_INDEX = ROOT / "index.html"
ROOT_INDEX_TEXT = (
    '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">\n'
    '<title>Minimal match and SNR loss from imperfect templates</title>\n'
    '<meta http-equiv="refresh" content="0; url=page/index.html">\n'
    '<link rel="canonical" href="page/index.html">\n'
    '<!-- Generated by scripts/make_page.py. -->\n'
    '</head><body>\n'
    '<p>Redirecting to <a href="page/index.html">the project page</a>.</p>\n'
    '<p>Also here: <a href="paper/main.pdf">the paper (PDF)</a> and\n'
    '<a href="page/owen.html">a guide to Owen (1995)</a>.</p>\n'
    '</body></html>\n'
)

if "--check" in sys.argv:
    stale = []
    if not OUT.exists() or OUT.read_text(encoding="utf-8") != HTML:
        stale.append(str(OUT.relative_to(ROOT)))
    if not ROOT_INDEX.exists() or ROOT_INDEX.read_text(encoding="utf-8") != ROOT_INDEX_TEXT:
        stale.append(str(ROOT_INDEX.relative_to(ROOT)))
    if stale:
        raise SystemExit("stale generated page artifact(s): " + ", ".join(stale))
    print("generated page artifacts: current")
else:
    OUT.write_text(HTML, encoding="utf-8")
    size = OUT.stat().st_size
    print(f"wrote {OUT.relative_to(ROOT)}  ({size / 1024:.0f} kB, figures embedded)")
    # GitHub Pages is served from the repository root; keep the redirect with the page.
    ROOT_INDEX.write_text(ROOT_INDEX_TEXT, encoding="utf-8")
    (ROOT / ".nojekyll").write_text("")
    print("wrote index.html (Pages redirect) and .nojekyll")
