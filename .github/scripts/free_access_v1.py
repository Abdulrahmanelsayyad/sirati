"""Sirati free-access launch: remove checkout from the active CV journey.

Applied LAST to the reconstructed static source. No database writes, migrations,
payment approvals, secrets, authentication or historic order records are touched.
This offers the browser's own Print / Save as PDF dialog, not a server-issued PDF.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
builder_path = root / "app/builder/page.tsx"
home_path = root / "app/page.tsx"

def once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one source anchor, found {count}")
    return source.replace(old, new, 1)

builder = builder_path.read_text(encoding="utf-8")
for line in (
    "  const [paymentMethod, setPaymentMethod] = useState<'instapay' | 'vodafone_cash' | 'other'>('instapay');\n",
    "  const [paymentReference, setPaymentReference] = useState('');\n",
    "  const [pdfOrderStatus, setPdfOrderStatus] = useState<'none' | 'pending' | 'approved' | 'rejected'>('none');\n",
    "  const [orderMessage, setOrderMessage] = useState('');\n",
):
    builder = once(builder, line, "", "retire client payment state")
builder = once(builder, "        await refreshPdfOrder(doc.id);\n", "", "retire payment lookup")
start = builder.find("  async function refreshPdfOrder(id: string) {")
end = builder.find("  async function saveToAccount(", start)
if start < 0 or end < 0 or end <= start:
    raise RuntimeError("Expected legacy payment lookup/order function boundaries not found")
builder = builder[:start] + builder[end:]

start = builder.find('              <div className={`notice review-notice ')
end_anchor = '              <div className="review-actions">\n                <button type="button" className="btn btn-primary btn-lg" onClick={() => saveToAccount(true)}'
end = builder.find(end_anchor, start)
if start < 0 or end < 0:
    raise RuntimeError("Expected legacy review payment card not found; refusing partial free conversion")
free_notice = """              <div className="notice review-notice free-pdf-notice" role="status">
                <strong>{language === 'ar' ? 'كل أدوات Sirati مجانية' : 'Everything in Sirati is free'}</strong>
                <p>{language === 'ar'
                  ? 'القوالب والمساعدة في الكتابة ومراجعة الجودة وحفظ السيرة متاحة مجانًا. استخدم الطباعة ثم اختر حفظ كملف PDF من متصفحك، دون دفع أو طلب موافقة.'
                  : 'Templates, writing suggestions, CV quality checks and saving are free. Use your browser print dialog and choose Save as PDF. No payment or approval required.'}</p>
              </div>

"""
builder = builder[:start] + free_notice + builder[end:]
builder = once(builder,
    '<button type="button" className="btn btn-secondary btn-lg" onClick={() => window.print()}>{pdfOrderStatus === \'approved\' ? \'Save clean PDF\' : \'Print watermarked preview\'}</button>',
    '<button type="button" className="btn btn-secondary btn-lg" onClick={() => window.print()}>{language === \'ar\' ? \'طباعة / حفظ PDF مجانًا\' : \'Print / Save free PDF\'}</button>',
    "free PDF export CTA")
builder = once(builder, 'watermarked={pdfOrderStatus !== \'approved\'}', 'watermarked={false}', "remove watermark from CV")
for forbidden in ('pdfOrderStatus', 'setPdfOrderStatus', 'requestCleanPdf', 'refreshPdfOrder',
                  'paymentMethod', 'paymentReference', 'manual-payment-card', "from('pdf_orders')"):
    if forbidden in builder:
        raise RuntimeError(f"Legacy payment reference remains in generated Builder: {forbidden}")
builder_path.write_text(builder, encoding="utf-8")

home = home_path.read_text(encoding="utf-8")
replacements = (
    ("Free preview before payment", "Free templates and PDF export"),
    ("Yes. Preview and watermarked printing are free. A clean PDF can be requested for EGP 50 using manual payment verification, so Sirati does not need a paid payment gateway yet.",
     "Yes. All CV templates, live previews and browser-based PDF saving are free. Select Print / Save free PDF in the builder, then choose Save as PDF in your browser."),
    ("Yes. CV writing and CV review are available as separate assisted services for EGP 50 per service.",
     "Sirati provides free, editable writing suggestions and automated CV quality guidance. Human-written or human-reviewed services are not currently offered."),
    ("Build it yourself — or let Sirati help shape the story.",
     "Build and improve your CV for free."),
    ("You can use the builder independently, or request help writing and refining your CV.",
     "Use the templates, role-based content suggestions and CV quality checks at no cost."),
    ("<div className=\"service-copy\"><h3>CV Writing</h3><p>We organize your real experience, education and skills into clear professional language.</p></div>",
     "<div className=\"service-copy\"><h3>Smart writing suggestions</h3><p>Choose and edit suggested content tailored to your professional title. Always verify your own details.</p></div>"),
    ("<div className=\"service-copy\"><h3>Review & Refine</h3><p>Improve wording, structure and readability while keeping your experience accurate.</p></div>",
     "<div className=\"service-copy\"><h3>CV Quality Center</h3><p>Get clear, actionable checks for your CV content. This is not an ATS score or a hiring guarantee.</p></div>"),
)
for old, new in replacements:
    home = once(home, old, new, "homepage free-access copy")
price = '<div className="service-price"><strong>EGP 50</strong><small>per service</small></div>'
if home.count(price) != 2:
    raise RuntimeError("Expected exactly two homepage paid service badges")
home = home.replace(price, '<div className="service-price"><strong>FREE</strong><small>for everyone</small></div>')
for forbidden in ('EGP 50', 'before payment', 'per service', 'manual payment verification'):
    if forbidden in home:
        raise RuntimeError(f"Legacy paid promise remains on homepage: {forbidden}")
home_path.write_text(home, encoding="utf-8")
print("PASS: Sirati home and CV journey are free; no payment UI or database order submission.")
