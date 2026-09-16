#!/usr/bin/env bash
# Rebuild papers/ — the local reading copies of the arXiv sources this project cites.
#
# papers/ is git-ignored (PDFs are not ours to redistribute), so a fresh clone has none
# of this. This script is the reproducibility entry for that directory, per the rule in
# wiki/reproducibility.md. The canonical list of what belongs here is
# wiki/sources/papers.md; keep the two in step.
#
# Usage:  bash scripts/fetch_papers.sh          # fetch what is missing
#         bash scripts/fetch_papers.sh --check  # verify checksums, fetch nothing
#
# Needs network. Nothing else in this repository does.

set -euo pipefail
cd "$(dirname "$0")/.."

UA="gw-minimal-match (course project; contact via the repository)"
DELAY=3          # be polite to arXiv between requests

# dir|filename|arxiv-pdf-id
PAPERS=(
  "gr-qc-9511032|owen1995.pdf|gr-qc/9511032"
  "gr-qc-9808076|owen-sathyaprakash-1999.pdf|gr-qc/9808076"
  "gr-qc-0404096|croce-2004.pdf|gr-qc/0404096"
  "gr-qc-0509116|allen-findchirp.pdf|gr-qc/0509116"
  "0706.4437|cokelaer-2007.pdf|0706.4437"
  "1303.2005|keppel-2013.pdf|1303.2005"
  "1508.02357|usman-2016.pdf|1508.02357"
  "1904.01683|roulet-2019.pdf|1904.01683"
  "2211.16674|sakon-2023.pdf|2211.16674"
)

check_only=0
[ "${1:-}" = "--check" ] && check_only=1

fetched=0
for entry in "${PAPERS[@]}"; do
  IFS='|' read -r dir name id <<< "$entry"
  target="papers/$dir/$name"
  if [ -f "$target" ]; then
    echo "have    $target"
    continue
  fi
  if [ "$check_only" = 1 ]; then
    echo "MISSING $target"
    continue
  fi
  mkdir -p "papers/$dir"
  echo "fetch   $target  <- arXiv:$id"
  curl -fsS -L --max-time 180 -A "$UA" -o "$target" "https://arxiv.org/pdf/$id"
  fetched=1
  sleep "$DELAY"
done

# Owen 1996 also ships its arXiv LaTeX source; the equation numbering in
# wiki/sources/owen1995_template_metric.md and in structure/claims.yaml is v1's,
# which is readable only in the source, not in the rendered PDF.
if [ ! -f papers/gr-qc-9511032/9511032.tex ]; then
  if [ "$check_only" = 1 ]; then
    echo "MISSING papers/gr-qc-9511032/9511032.tex (arXiv e-print source)"
  else
    echo "fetch   papers/gr-qc-9511032/ e-print source <- arXiv:gr-qc/9511032"
    [ "$fetched" = 1 ] && sleep "$DELAY"
    tmp="$(mktemp -d)"
    curl -fsS -L --max-time 180 -A "$UA" -o "$tmp/src" "https://arxiv.org/e-print/gr-qc/9511032"
    tar -xzf "$tmp/src" -C papers/gr-qc-9511032/ 2>/dev/null \
      || gunzip -c "$tmp/src" > papers/gr-qc-9511032/9511032.tex
    rm -rf "$tmp"
  fi
fi

echo
echo "sha256 (first 16 hex) of what is present — compare with wiki/sources/papers.md:"
find papers -type f \( -name '*.pdf' -o -name '*.tex' -o -name '*.ps' \) | sort | while read -r f; do
  printf "  %s  %s\n" "$(sha256sum "$f" | cut -c1-16)" "${f#papers/}"
done
