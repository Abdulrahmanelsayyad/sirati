"""Surface the existing free Career Toolkit where signed-in users land.

Presentation only: generated My Documents page and isolated CSS. Does not
change authentication, user data, CV Builder, payment or PDF business logic.
"""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
page = root / "app/documents/page.tsx"
css_file = root / "app/globals.css"
source = page.read_text(encoding="utf-8")

if 'data-testid="career-tools-entry"' in source:
    raise RuntimeError("Career tools account shortcut already installed")
if "withBasePath" not in source:
    raise RuntimeError("Expected prepared documents base-path helper was not found")

# Prefer the final main view: no change to auth redirects or save functions.
main_openings = list(re.finditer(r"<main\b[^>]*>", source))
if not main_openings:
    raise RuntimeError("No My Documents main element found; no safe insertion")
last = main_openings[-1]
card = r'''
        <section className="sirati-career-shortcut no-print" data-testid="career-tools-entry"
          aria-label="Free cover letter, LinkedIn and interview tools">
          <div className="sirati-career-shortcut-copy">
            <span className="sirati-career-shortcut-eyebrow">FREE CAREER TOOLS · أدوات مهنية مجانية</span>
            <h2>Cover Letter &amp; LinkedIn Tools</h2>
            <p>Write a cover letter, improve your LinkedIn headline and About section,
              or prepare for interviews — free in English and Arabic.</p>
          </div>
          <a className="btn btn-primary sirati-career-shortcut-link"
            href={withBasePath('/career-tools/')}>
            Open Career Tools / افتح الأدوات
          </a>
        </section>
'''
source = source[:last.end()] + '\n' + card + source[last.end():]
page.write_text(source, encoding="utf-8")

styles = css_file.read_text(encoding="utf-8")
style_marker = "/* Sirati signed-in Career Tools entry */"
if style_marker in styles:
    raise RuntimeError("Career Tools shortcut stylesheet already applied")
styles += r"""
/* Sirati signed-in Career Tools entry */
.sirati-career-shortcut {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 22px;
  flex-wrap: wrap;
  margin: 16px 0 26px;
  padding: clamp(18px, 3vw, 28px);
  border: 1px solid #cfdfd4;
  border-radius: 18px;
  background: linear-gradient(115deg, #f0f8f0, #fffefa);
  box-shadow: 0 10px 26px rgba(25, 60, 43, .06);
}
.sirati-career-shortcut-copy { min-width: 0; flex: 1 1 250px; }
.sirati-career-shortcut-eyebrow {
  color: #235b4b; font-size: 11px; font-weight: 800; letter-spacing: .08em;
}
.sirati-career-shortcut h2 {
  margin: 8px 0; color: #184237; font-size: clamp(20px, 3vw, 28px);
}
.sirati-career-shortcut p { margin: 0; color: #4d6358; line-height: 1.55; max-width: 640px; }
.sirati-career-shortcut-link { flex: 0 1 auto; text-align: center; }
@media (max-width: 640px) {
  .sirati-career-shortcut { margin-block: 12px 22px; gap: 14px; }
  .sirati-career-shortcut-copy { flex-basis: 100%; }
  .sirati-career-shortcut-link { width: 100%; }
}
@media print { .sirati-career-shortcut { display: none !important; } }
"""
css_file.write_text(styles, encoding="utf-8")
print("PASS: My Documents includes a prominent, no-cost Career Tools shortcut.")
