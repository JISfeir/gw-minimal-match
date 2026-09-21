#!/usr/bin/env python
"""Acceptance gate for job qDEF.

Hash-pinned with --acceptance-guard: the team can make this pass, but cannot edit it,
and the job may not report DONE while it fails.

It asserts two things the job's own checks cannot:

  A. q1bC's frozen package is still exactly what was frozen. qDEF imports its library and
     reads its data; if that input drifts, every qDEF number is built on sand. This is the
     same GATE the objective asks the team to run -- asserted here so passing it is not
     left to the team's word.

  B. qDEF's own deliverable exists, is offline, and its spine is green: checks.py exits 0,
     and every \\src{key} in notes.tex resolves in provenance.json.

Usage: python tests/test_qdef_acceptance.py <job-dir>
Exits 0 only if every check passes. Prints one line per check.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Q1BC = os.path.join(PROJECT, "jobs", "2026-09-14_041516_derive-q1bc")
fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (": " + detail if detail else ""))
    if not ok:
        fails.append(name)
    return ok


def sha_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# ---- A. the frozen input -----------------------------------------------------------
def gate_q1bc():
    spec = os.path.join(Q1BC, "spec.json")
    if not check("q1bC present", os.path.isdir(Q1BC), Q1BC):
        return
    status = json.load(open(spec)).get("status")
    check("q1bC frozen", status == "frozen", "status=%r" % status)

    mpath = os.path.join(Q1BC, "out", "manifest.json")
    if not check("q1bC manifest exists", os.path.exists(mpath)):
        return
    m = json.load(open(mpath))

    files = m["files"]
    items = list(files.items()) if isinstance(files, dict) else [(f["path"], f) for f in files]
    bad = miss = 0
    for path, meta in items:
        full = os.path.join(Q1BC, path)
        rec = meta.get("sha256") if isinstance(meta, dict) else meta
        if not os.path.exists(full):
            miss += 1
        elif rec and sha_file(full) != rec:
            bad += 1
    check("q1bC manifest hashes", bad == 0 and miss == 0,
          "%d files, %d differ, %d missing" % (len(items), bad, miss))

    # The manifest declares how its output was captured; honour it or the hash cannot match.
    merged = "merged" in (m.get("check_output_capture") or "").lower()
    r = subprocess.run(m["check_command"], shell=True, cwd=Q1BC, text=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT if merged else subprocess.PIPE)
    check("q1bC check re-runs clean", r.returncode == m["check_exit_code"],
          "exit %s, manifest says %s" % (r.returncode, m["check_exit_code"]))
    got = hashlib.sha256(r.stdout.encode()).hexdigest()
    check("q1bC check output hash", got == m["check_output_sha256"], got[:16])


# ---- B. qDEF's own deliverable -----------------------------------------------------
NETWORK = re.compile(r"""(?:src|href)\s*=\s*["']https?://|<link[^>]+https?://|fetch\s*\(|"""
                     r"""cdn\.|googleapis\.com|jsdelivr|unpkg""", re.I)


def gate_qdef(job):
    out = os.path.join(job, "out")
    if not check("qDEF out/ exists", os.path.isdir(out), out):
        return

    rep = os.path.join(out, "report.html")
    if check("qDEF report.html exists", os.path.exists(rep)):
        html = open(rep, encoding="utf-8", errors="replace").read()
        check("qDEF report is substantial", len(html) > 20000, "%d bytes" % len(html))
        hits = sorted(set(NETWORK.findall(html)))
        check("qDEF report is offline", not hits, "remote refs: %s" % hits[:5])

    prov_path = os.path.join(out, "provenance.json")
    notes = os.path.join(out, "notes.tex")
    if check("qDEF provenance.json exists", os.path.exists(prov_path)) and os.path.exists(notes):
        prov = json.load(open(prov_path))
        keys = set(prov) if isinstance(prov, dict) else set()
        used = set(re.findall(r"\\src\{([^}]+)\}", open(notes, encoding="utf-8").read()))
        missing = sorted(used - keys)
        check("qDEF every src key resolves", not missing,
              "%d used, missing: %s" % (len(used), missing[:5]))

    checks = os.path.join(out, "checks.py")
    if check("qDEF checks.py exists", os.path.exists(checks)):
        py = os.path.join(PROJECT, ".venv", "bin", "python")
        r = subprocess.run([py, "-B", checks], cwd=job, text=True,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        nfail = len(re.findall(r"^FAIL", r.stdout, re.M))
        check("qDEF checks.py exits 0", r.returncode == 0,
              "exit %s, %d FAIL line(s)" % (r.returncode, nfail))


def main():
    if len(sys.argv) < 2:
        print("usage: test_qdef_acceptance.py <job-dir>")
        return 2
    job = os.path.abspath(sys.argv[1])
    print("== A. frozen input: job q1bC ==")
    gate_q1bc()
    print("== B. deliverable: %s ==" % os.path.basename(job))
    gate_qdef(job)
    print("SUMMARY failed=%d" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
