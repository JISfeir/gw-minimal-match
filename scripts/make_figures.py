#!/usr/bin/env python3
"""Regenerates every file in `figures/`. One function per panel.

Run:
    SOURCE_DATE_EPOCH=1704067200 python scripts/make_figures.py

Setting SOURCE_DATE_EPOCH to a fixed value makes the PDFs byte-identical under a pinned
matplotlib (matplotlib otherwise stamps /CreationDate and /Producer).

Each figure drawn here must have an entry under `figures:` in `provenance/claims.yaml`
(format: .claude/provenance/figures.md). `scripts/check_provenance.py` enforces it.

STATUS: scaffold. No figures yet — see wiki/todo.md.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIGDIR = ROOT / "figures"


def main() -> None:
    FIGDIR.mkdir(exist_ok=True)
    drawn: list[str] = []
    # drawn.append(fig_mismatch_map())
    # drawn.append(fig_metric_vs_owen())
    # drawn.append(fig_covering_histogram())
    # drawn.append(fig_volume_loss_vs_mm())
    print(f"drew {len(drawn)} figure(s): {', '.join(drawn) or '(none)'}")


if __name__ == "__main__":
    main()
