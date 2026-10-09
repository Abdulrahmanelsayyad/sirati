#!/usr/bin/env python3
"""Safety patch applied to the Render staging build ONLY, after prepare_pages.py."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("Usage: render_staging_patch.py SOURCE_ROOT")

root = Path(sys.argv[1])
builder_path = root / "app" / "builder" / "page.tsx"
css_path = root / "app" / "globals.css"
builder = builder_path.read_text(encoding="utf-8")
payment_phrase = (
    "1. Get payment details from Sirati Support. "
    "2. Pay EGP 50 by InstaPay or Vodafone Cash. "
    "3. Enter the payment transaction reference below and submit it for manual review. "
    "Never enter card details."
)
fake_payment_phrase = (
    "STAGING TEST ONLY — DO NOT TRANSFER REAL MONEY. "
    "Enter a fictional transaction reference (for example QA-TEST-002) to request "
    "a simulated EGP 50 clean PDF order for manual QA approval."
)
if payment_phrase not in builder:
    raise SystemExit("FAIL: payment text marker changed; staging guard cannot disable real-payment instructions")
builder = builder.replace(payment_phrase, fake_payment_phrase)

support_link = "href={process.env.NEXT_PUBLIC_WHATSAPP_URL || 'mailto:sirati-support@agentmail.to?subject=Sirati%20PDF%20Payment'}"
if support_link not in builder:
    raise SystemExit("FAIL: customer payment support marker changed; do not deploy unsafe staging preview")
builder = builder.replace(
    support_link, 'href="mailto:qa-only@example.invalid?subject=Sirati%20Staging%20No%20Real%20Payments"'
)
builder = builder.replace("Get payment details from Sirati Support →", "TEST ONLY: No real payment details →")
builder_path.write_text(builder, encoding="utf-8")

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
print("PASS: staging-only payment and support instructions are non-transactional")
print("PASS: visible test-only banner installed, no real payments")
