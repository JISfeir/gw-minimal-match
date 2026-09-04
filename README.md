# Minimal match and SNR loss from imperfect templates

**Claim.** How imperfect a template must be to lose a signal (recovered SNR below the
detection threshold), and how dense a bank must be so that never happens — derived from
the match metric and verified with injections.

**Scope (v1).** Non-spinning 2D bank in (m1, m2), single detector, ~5-50 Msun.
Detection threshold from an analytic Gaussian false-alarm rate. Numeric match metric
checked against the analytic Owen metric (TaylorF2). Monte-Carlo covering check at
minimal match 0.97. Output: volume loss and template count vs. minimal match.

Final project for *Gravitational Waves and AI-Assisted Research*.

## Environment

```
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
