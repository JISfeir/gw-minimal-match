#!/usr/bin/env python3
"""Generate a job's per-round BRIEFING.md: what a worker actually needs, and nothing else.

Why this exists. `roles/worker.md` tells every worker "every file below is small" and to read
spec.json, state.json, inbox.jsonl and reports/ at the start of every round. In this project
those are ~50k tokens (job qDEF) to ~83k (job q1bC). An agentic session re-sends its whole
context on every step, so front-loading 50-83k tokens before any work multiplies through every
subsequent step: a measured q1bC worker call cost 5.4M tokens. The fix is not to ask the worker
to read less -- that is a judgement call it will get wrong in one direction or the other -- but
to hand it a deterministic digest and an explicit whitelist.

The digest is mechanical, not a summary: claims are filtered by `status in {refuted, unclear}`,
so nothing live can be silently dropped. That is more reliable than a worker skimming 19k tokens
of JSON and deciding what matters.

Usage:  python scripts/make_job_briefing.py <job-dir> [--facts <file>] [--round N]
Writes <job-dir>/work/BRIEFING.md and prints its size.
"""
import argparse
import json
import os
import sys


def human(n):
    return "%s bytes (~%d tokens)" % (format(n, ","), n // 4)


def inventory(root, sub, limit=60):
    base = os.path.join(root, sub)
    if not os.path.isdir(base):
        return ["  (nothing yet)"]
    rows = []
    for dirpath, _dirs, files in os.walk(base):
        if "__pycache__" in dirpath:
            continue
        for name in sorted(files):
            p = os.path.join(dirpath, name)
            rows.append("  %-58s %9d B" % (os.path.relpath(p, root), os.path.getsize(p)))
    if not rows:
        return ["  (empty)"]
    if len(rows) > limit:
        return rows[:limit] + ["  ... and %d more" % (len(rows) - limit)]
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("job")
    ap.add_argument("--facts", help="file whose contents become the 'Facts for this round' section")
    ap.add_argument("--round", type=int, default=None)
    a = ap.parse_args()

    job = os.path.abspath(a.job)
    state = json.load(open(os.path.join(job, "state.json"), encoding="utf-8"))
    spec = json.load(open(os.path.join(job, "spec.json"), encoding="utf-8"))
    rnd = a.round if a.round is not None else (state.get("round") or 0) + 1

    claims = [c for c in (state.get("claims") or []) if isinstance(c, dict)]
    live = [c for c in claims if c.get("status") in ("refuted", "unclear")]

    out = []
    w = out.append
    w("# BRIEFING — round %d of job %s" % (rnd, spec.get("id", os.path.basename(job))))
    w("")
    w("GENERATED FILE. It is rebuilt before every round, so it is never stale.")
    w("")
    w("**It replaces reading `state.json` and the rest of `reports/`.** Those total roughly")
    w("%d tokens in this job; everything in them that is still open is reproduced below by a" % (
        (os.path.getsize(os.path.join(job, 'state.json'))
         + sum(os.path.getsize(os.path.join(job, 'reports', f))
               for f in os.listdir(os.path.join(job, 'reports'))) ) // 4
        if os.path.isdir(os.path.join(job, "reports")) else 0))
    w("mechanical filter (`status in {refuted, unclear}`), not by a summary, so nothing live")
    w("can have been dropped. Read this instead. The cost of reading everything is not paid")
    w("once: an agentic session re-sends its whole context on every step, so what you load")
    w("before starting is charged again at every step afterwards.")
    w("")

    w("## Live claims — %d open (%d of %d total are settled and are NOT your problem)"
      % (len(live), len(claims) - len(live), len(claims)))
    w("")
    w("The filter is deliberately conservative: it shows everything not marked settled, so a")
    w("claim someone already fixed but never closed still appears here. Check cheaply before")
    w("working one. Resolve it, or say in your report why it stands -- do not silently skip it.")
    w("")
    if not live:
        w("(none — nothing is open)")
    for c in live:
        w("- **[%s]** (round %s) %s" % (c.get("status", "?"), c.get("round", "?"),
                                        (c.get("text") or c.get("claim") or "").strip()))
    w("")

    w("## What already exists on disk — do not rebuild it")
    w("")
    w("`out/` — the deliverable so far:")
    out.extend(inventory(job, "out"))
    w("")
    w("`work/` — sandbox (yours; `papers/` are the sources, `verifier/` is not yours):")
    out.extend(inventory(job, "work", limit=25))
    w("")

    if a.facts and os.path.exists(a.facts):
        w("## Facts for this round")
        w("")
        w(open(a.facts, encoding="utf-8").read().rstrip())
        w("")

    text = "\n".join(out) + "\n"
    dest = os.path.join(job, "work", "BRIEFING.md")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("wrote %s" % dest)
    print("  %s" % human(len(text)))
    print("  live claims: %d of %d" % (len(live), len(claims)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
