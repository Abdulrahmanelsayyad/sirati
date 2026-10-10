#!/usr/bin/env python3
"""Fail-closed free-access check and test-only banner for Netlify Staging."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("Usage: render_staging_patch.py SOURCE_ROOT")

root = Path(sys.argv[1])
builder_path = root / "app" / "builder" / "page.tsx"
css_path = root / "app" / "globals.css"
builder = builder_path.read_text(encoding="utf-8")
# The active Sirati builder became free in PR #64; do not reintroduce a
# historical paid-order UI in Staging. Fail closed on incompatible builds.
for required in (
    "Everything in Sirati is free",
    "Download your PDF file directly to your device. No print dialog, payment or approval required.",
):
    if required not in builder:
        raise SystemExit("FAIL: expected free-access Builder proof is missing: " + required)

for forbidden in (
    "pdfOrderStatus", "requestCleanPdf", "refreshPdfOrder",
    "paymentReference", "manual-payment-card", "from('pdf_orders')",
    "Pay EGP 50 by InstaPay or Vodafone Cash",
):
    if forbidden in builder:
        raise SystemExit("FAIL: paid-order Builder path detected in Staging: " + forbidden)
print("PASS: current free-only Builder verified; no real payment actions")

css = css_path.read_text(encoding="utf-8")
css += """
/* TEST-ONLY rendered banner, added exclusively by Render staging build script. */
@media screen {
  body { padding-top: 46px !important; }
  body::before {
    content: "SIRATI STAGING — TEST ONLY — DO NOT PAY";
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 2147483640;
    display: block;
    min-height: 38px;
    padding: 10px 12px;
    background: #7f1d1d;
    color: #fff;
    font: 700 12px/1.5 system-ui, sans-serif;
    letter-spacing: .025em;
    text-align: center;
    pointer-events: none;
    box-sizing: border-box;
  }
}
@media print {
  body::before { display: none !important; }
}
"""
css_path.write_text(css, encoding="utf-8")
print("PASS: Staging free-only payment guard and direct PDF message verified")
print("PASS: visible test-only banner installed, no real payments")
