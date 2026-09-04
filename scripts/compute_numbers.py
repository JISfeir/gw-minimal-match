#!/usr/bin/env python3
"""The sole writer of `data/project_numbers.json` — the number registry.

Every number that appears in `page/` or `paper/` is computed here and nowhere else, so
that regenerating this one file reproduces every quoted value. Nothing else writes to
`data/project_numbers.json`.

Run:
    python scripts/compute_numbers.py

Determinism: no wall-clock, no unseeded RNG. Any Monte-Carlo quantity takes a fixed seed
passed explicitly and records it alongside the value.

STATUS: scaffold. No numbers computed yet — see wiki/todo.md for the spec that has to be
fixed first.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "project_numbers.json"


def compute() -> dict:
    """Return the full registry. One key per reported number."""
    registry: dict = {}
    # registry["owen_metric_max_rel_err"] = { ... }   # e.g. stage 2
    # registry["mm097_worst_match"]       = { ... }   # e.g. stage 4
    # registry["volume_loss_rule_max_dev"] = { ... }  # e.g. stage 5
    return registry


def main() -> None:
    registry = compute()
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(registry)} numbers)")


if __name__ == "__main__":
    main()
