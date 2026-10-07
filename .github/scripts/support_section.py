from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
page = root / "app" / "page.tsx"
text = page.read_text(encoding="utf-8")

if '<a href="#support">Support</a>' not in text:
    text = text.replace(
        '            <a href="#faq">FAQ</a>\n',
        '            <a href="#faq">FAQ</a>\n            <a href="#support">Support</a>\n',
        1
    )

support_section = r'''
      <section className="section support-section" id="support">
        <div className="container support-card">
          <div className="support-copy">
            <div className="eyebrow">SIRATI SUPPORT</div>
            <h2>Need help with your CV or the website?</h2>
            <p>
              Contact Sirati Support for CV-builder questions, document guidance, or technical help.
              Routine support is handled by our support assistant, and important account, payment,
              privacy, or security matters are escalated to the site owner.
            </p>
          </div>
          <div className="support-actions">
            <a className="btn btn-primary btn-lg" href="mailto:sirati-support@agentmail.to?subject=Sirati%20Support">
              Email Sirati Support
            </a>
            <span className="support-email">sirati-support@agentmail.to</span>
          </div>
        </div>
      </section>

'''

anchor = '      <section className="container final-cta">'
if 'id="support"' not in text:
    if anchor not in text:
        raise SystemExit("Could not find final CTA anchor")
    text = text.replace(anchor, support_section + anchor, 1)

footer_faq = '            <a href="#faq">FAQ</a>\n'
if text.count('<a href="#support">Support</a>') < 2:
    idx = text.rfind(footer_faq)
    if idx != -1:
        insert_at = idx + len(footer_faq)
        text = text[:insert_at] + '            <a href="#support">Support</a>\n' + text[insert_at:]

page.write_text(text, encoding="utf-8")

css_path = root / "app" / "globals.css"
css = css_path.read_text(encoding="utf-8")
marker = "/* Sirati support section */"
if marker not in css:
    css += r'''

/* Sirati support section */
.support-section {
  padding-top: 18px;
}
.support-card {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(260px, .6fr);
  gap: 32px;
  align-items: center;
  padding: 36px;
  border: 1px solid rgba(15, 23, 42, .08);
  border-radius: 22px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  box-shadow: 0 18px 45px rgba(15, 23, 42, .07);
}
.support-copy h2 {
  margin: 8px 0 12px;
}
.support-copy p {
  margin: 0;
  max-width: 760px;
  color: var(--muted);
}
.support-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
}
.support-email {
  font-size: 13px;
  color: var(--muted);
  word-break: break-all;
}
@media (max-width: 760px) {
  .support-card {
    grid-template-columns: 1fr;
    padding: 24px;
  }
}
'''
    css_path.write_text(css, encoding="utf-8")

print("Applied Sirati support section.")
