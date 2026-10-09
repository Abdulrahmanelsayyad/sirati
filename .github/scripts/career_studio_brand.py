"""Sirati Career Studio: replace CV-only homepage kicker with a distinctive career path mark.

Applied after all existing source generation and design layers. This only changes
marketing copy and appearance, not the actual CV Builder, templates, accounts or PDF.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
homepage = root / "app/page.tsx"
css_path = root / "app/globals.css"
source = homepage.read_text(encoding="utf-8")
old = """          <div className="hero-kicker">
            <span className="kicker-dot" />
            Professional CV builder for Arabic & English
          </div>"""
new = """          <div className="hero-kicker sirati-career-studio-mark" aria-label="Sirati Career Studio: CV, cover letters, LinkedIn and interview preparation">
            <span className="career-studio-symbol" aria-hidden="true">
              <svg viewBox="0 0 64 64" width="38" height="38" fill="none" focusable="false">
                <path d="M17 43L28 32L36 38L48 21" stroke="#E8C993" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M39 21H48V30" stroke="#E8C993" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M17 21V30M17 21H26" stroke="#F6F8F4" strokeWidth="3.5" strokeLinecap="round" />
                <circle cx="17" cy="43" r="3" fill="#F6F8F4" />
              </svg>
            </span>
            <span className="career-studio-label">
              <strong>Career Studio</strong>
              <small>CV · Cover Letter · LinkedIn · Interview</small>
            </span>
          </div>"""
old_intro = "Choose a polished template, add your real experience, and build a clear CV in Arabic or English. Preview your work before you decide to export."
new_intro = "Build your CV, write cover letters, improve your LinkedIn profile and prepare for interviews — all free, in Arabic and English."
for label, previous, replacement in (
    ("hero brand", old, new),
    ("career-wide hero introduction", old_intro, new_intro),
):
    count = source.count(previous)
    if count != 1:
        raise RuntimeError(f"{label}: expected a single exact anchor; found {count}. No modification made.")
    source = source.replace(previous, replacement, 1)
homepage.write_text(source, encoding="utf-8")

styles = css_path.read_text(encoding="utf-8")
if "/* Sirati Career Studio identity */" in styles:
    raise RuntimeError("Career Studio identity already applied")
styles += r"""
/* Sirati Career Studio identity */
@media screen {
  .marketing-page .hero-kicker.sirati-career-studio-mark {
    display: inline-flex;
    flex-wrap: nowrap;
    align-items: center;
    gap: 11px;
    max-width: 100%;
    width: fit-content;
    padding: 8px 16px 8px 8px;
    border: 1px solid rgba(232,201,147,.45);
    border-radius: 15px;
    background: rgba(255,255,255,.09);
    letter-spacing: normal;
  }
  .marketing-page .career-studio-symbol {
    flex: 0 0 48px;
    width: 48px;
    height: 48px;
    display: grid;
    place-items: center;
    border-radius: 12px;
    background: #143b31;
    box-shadow: inset 0 0 0 1px rgba(232,201,147,.20);
  }
  .marketing-page .career-studio-label {
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 2px;
    line-height: 1.25;
  }
  .marketing-page .career-studio-label strong {
    color: #f6e2bb;
    font-size: 15px;
    font-weight: 800;
    letter-spacing: .02em;
  }
  .marketing-page .career-studio-label small {
    color: #e7eee8;
    font-size: 11px;
    letter-spacing: 0;
    white-space: normal;
    overflow-wrap: break-word;
  }
}
@media screen and (max-width: 390px) {
  .marketing-page .hero-kicker.sirati-career-studio-mark {
    gap: 8px;
    padding: 7px 10px 7px 7px;
  }
  .marketing-page .career-studio-symbol {
    flex-basis: 42px; width: 42px; height: 42px;
  }
  .marketing-page .career-studio-label strong { font-size: 14px; }
  .marketing-page .career-studio-label small { font-size: 10px; }
}
@media print {
  .sirati-career-studio-mark { display: none !important; }
}
"""
css_path.write_text(styles, encoding="utf-8")
print("PASS: Sirati Career Studio mark and career-wide homepage introduction installed.")
