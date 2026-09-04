#!/usr/bin/env python3
"""The provenance gate, run by hand and in CI.

A stricter, repository-wide version of the Stop hook in
`.claude/hooks/provenance_gate.py`. That hook stops an agent from *finishing* work
without a record; this script is what a reviewer runs against the whole tree.

Checks
------
1. Every figure in `figures/` has an entry under `figures:` in `provenance/claims.yaml`.
2. Every number entry in `provenance/numbers.json` has all six required fields.
3. Every `numbers:` slug named by a claim in both `provenance/claims.yaml` and
   `structure/claims.yaml` exists in `provenance/numbers.json`.
4. Every claim in `structure/claims.yaml` has a statement, a section and evidence.
5. Every non-empty `results/` file is listed in `wiki/reproducibility.md`.

Exit 0 if all pass, 1 otherwise. Prints one line per problem.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIGURE_EXT = (".png", ".pdf", ".svg", ".jpg", ".jpeg")
NUMBER_FIELDS = ("value", "statement", "produced_by",
                 "from_scratch", "from_library", "choices")


def load_json(path: Path):
    if not path.exists():
        return None, f"{path.relative_to(ROOT)} is missing"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # noqa: BLE001
        return None, f"{path.relative_to(ROOT)} does not parse: {exc}"


def load_yaml(path: Path):
    try:
        import yaml
    except ImportError:
        return None, "PyYAML is not installed (pip install pyyaml)"
    if not path.exists():
        return None, f"{path.relative_to(ROOT)} is missing"
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}, None
    except Exception as exc:  # noqa: BLE001
        return None, f"{path.relative_to(ROOT)} does not parse: {exc}"


def main() -> int:
    problems: list[str] = []

    numbers, err = load_json(ROOT / "provenance" / "numbers.json")
    if err and "missing" not in err:
        problems.append(err)
    numbers = numbers or {}
    for key, entry in numbers.items():
        if not isinstance(entry, dict):
            problems.append(f"numbers.json[{key}] is not an object")
            continue
        missing = [f for f in NUMBER_FIELDS if f not in entry]
        if missing:
            problems.append(f"numbers.json[{key}] missing: {', '.join(missing)}")

    prov, err = load_yaml(ROOT / "provenance" / "claims.yaml")
    if err and "missing" not in err:
        problems.append(err)
    prov = prov or {}

    recorded_figs = {f.get("file") for f in (prov.get("figures") or [])}
    recorded_figs |= {Path(f).name for f in recorded_figs if f}
    for fig in sorted((ROOT / "figures").glob("**/*")):
        if fig.suffix.lower() in FIGURE_EXT:
            rel = str(fig.relative_to(ROOT / "figures"))
            if rel not in recorded_figs and fig.name not in recorded_figs:
                problems.append(f"figure figures/{rel} has no entry in provenance/claims.yaml")

    struct, err = load_yaml(ROOT / "structure" / "claims.yaml")
    if err:
        problems.append(err)
    struct = struct or {}

    for src, doc in (("provenance/claims.yaml", prov), ("structure/claims.yaml", struct)):
        for c in doc.get("claims") or []:
            cid = c.get("id", "<no id>")
            if not c.get("statement"):
                problems.append(f"{src}: claim {cid} has no statement")
            if src == "structure/claims.yaml" and not c.get("section"):
                problems.append(f"{src}: claim {cid} has no section")
            if not c.get("evidence"):
                problems.append(f"{src}: claim {cid} has no evidence")
            for slug in c.get("numbers") or []:
                if slug not in numbers:
                    problems.append(f"{src}: claim {cid} names number '{slug}' not in numbers.json")

    repro = (ROOT / "wiki" / "reproducibility.md")
    repro_text = repro.read_text(encoding="utf-8") if repro.exists() else ""
    for f in sorted((ROOT / "results").glob("**/*")):
        if f.is_file() and f.name != ".gitkeep" and f.stat().st_size > 0:
            if f.name not in repro_text:
                problems.append(f"results/{f.relative_to(ROOT / 'results')} not listed in wiki/reproducibility.md")

    if problems:
        print(f"provenance gate: {len(problems)} problem(s)")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("provenance gate: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
