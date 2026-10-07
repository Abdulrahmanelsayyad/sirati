from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
builder_path = root / "app" / "builder" / "page.tsx"
css_path = root / "app" / "globals.css"

text = builder_path.read_text(encoding="utf-8")

replacements = [
    (
        "Enter the payment transaction reference first.",
        "Enter your payment transaction reference before submitting."
    ),
    (
        "Request received. Your clean PDF will unlock after the payment reference is approved.",
        "Payment reference submitted. Status: Pending review. Use “Check approval status” later; the clean PDF unlocks after approval."
    ),
    (
        "Payment approved. Clean PDF is unlocked for this CV.",
        "Payment approved. Your clean PDF is unlocked — use “Save clean PDF” below."
    ),
    (
        "Payment reference received and waiting for manual approval. The preview remains watermarked.",
        "Payment reference received. Status: Pending review. Keep this page or return later and use “Check approval status”."
    ),
    (
        "The previous payment reference was not approved. Check it and submit a new request.",
        "Payment reference was not approved. Confirm the reference with Sirati Support, then submit a corrected reference."
    ),
    (
        "Preview and print are free with a Sirati watermark. Clean PDF costs EGP 50 and is approved manually — no payment gateway fees.",
        "Preview and watermarked printing are free. Clean PDF: EGP 50, unlocked after manual payment verification."
    ),
    (
        "Request clean PDF · EGP 50",
        "Clean PDF · EGP 50"
    ),
    (
        "Get the payment details from Sirati on WhatsApp, pay using InstaPay or Vodafone Cash, then enter the transaction reference below. Do not enter card details.",
        "1. Get payment details from Sirati Support. 2. Pay EGP 50 by InstaPay or Vodafone Cash. 3. Enter the payment transaction reference below and submit it for manual review. Never enter card details."
    ),
    (
        "Get payment details on WhatsApp →",
        "Get payment details from Sirati Support →"
    ),
    (
        "Transaction reference",
        "Payment transaction reference"
    ),
    (
        "Reference / transaction ID",
        "Paste the reference or transaction ID"
    ),
    (
        "Request clean PDF",
        "Submit payment reference"
    ),
    (
        "Refresh approval status",
        "Check approval status"
    ),
]

for old, new in replacements:
    if old not in text:
        raise SystemExit(f"Could not locate payment copy: {old}")
    text = text.replace(old, new)

whatsapp_old = "href={process.env.NEXT_PUBLIC_WHATSAPP_URL || '#'}"
whatsapp_new = "href={process.env.NEXT_PUBLIC_WHATSAPP_URL || 'mailto:sirati-support@agentmail.to?subject=Sirati%20PDF%20Payment'}"
if whatsapp_old not in text:
    raise SystemExit("Could not locate payment support link fallback")
text = text.replace(whatsapp_old, whatsapp_new, 1)

builder_path.write_text(text, encoding="utf-8")

css = css_path.read_text(encoding="utf-8")
marker = "/* Sirati payment clarity */"
if marker not in css:
    css += r'''

/* Sirati payment clarity */
.manual-payment-card {
  border-color: #d9d3c7;
  background: #fff;
  box-shadow: 0 10px 30px rgba(20, 24, 32, 0.05);
}

.manual-payment-card > div:first-child {
  border-bottom: 1px solid var(--line);
  padding-bottom: 12px;
}

.manual-payment-card > div:first-child strong {
  display: block;
  font-size: 16px;
  line-height: 1.3;
}

.manual-payment-card > div:first-child .small {
  color: #4b5563;
  line-height: 1.65;
  max-width: 70ch;
}

.manual-payment-card .text-link {
  display: inline-flex;
  align-items: center;
  min-height: 36px;
  font-weight: 700;
}

.manual-payment-card .grid-2 {
  margin-top: 14px;
}

.manual-payment-card .review-actions {
  margin-top: 12px;
  align-items: center;
}

.manual-payment-card .auth-message {
  margin-top: 10px;
  line-height: 1.5;
}

@media (max-width: 720px) {
  .manual-payment-card {
    padding: 14px;
  }

  .manual-payment-card .grid-2 {
    grid-template-columns: 1fr;
  }

  .manual-payment-card .review-actions {
    display: grid;
    grid-template-columns: 1fr;
  }

  .manual-payment-card .review-actions .btn {
    width: 100%;
  }
}
'''
    css_path.write_text(css, encoding="utf-8")

print("Applied PDF order/payment clarity improvements.")
