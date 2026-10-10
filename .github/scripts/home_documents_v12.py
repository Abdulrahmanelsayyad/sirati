"""V12: remove duplicated navigation and put documents ahead of career promotion.

Generated UI only: preserve all authenticated document actions and routes, the
original sign-out handler, and all free Career Tools. Fail closed on drift.
"""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
home_path = root / "app/page.tsx"
docs_path = root / "app/documents/page.tsx"
css_path = root / "app/globals.css"

def once(source: str, before: str, after: str, label: str) -> str:
    count = source.count(before)
    if count != 1:
        raise RuntimeError(f"V12 {label}: expected one anchor, found {count}")
    return source.replace(before, after, 1)

# The global SiratiSiteMenu is now the sole page header, including keyboard
# navigation and desktop shortcuts. Keep the homepage hero CTAs unchanged.
home = home_path.read_text(encoding="utf-8")
header = re.search(
    r'^[ \t]*<header className="marketing-header">[\s\S]*?^[ \t]*</header>\s*\n',
    home, flags=re.MULTILINE,
)
if not header or home.count('<header className="marketing-header">') != 1:
    raise RuntimeError("V12 homepage: duplicated marketing header not unique")
if 'marketing-nav' not in header.group(0) or '<AccountNav />' not in header.group(0):
    raise RuntimeError("V12 homepage: original header changed; refusing to remove")
home = home[:header.start()] + home[header.end():]
home_path.write_text(home, encoding="utf-8")

docs = docs_path.read_text(encoding="utf-8")
# The no-cloud informational branch has a second redundant Sirati link.
docs = once(
    docs,
    '        <header className="container nav"><Link href="/" className="brand">Sirati</Link></header>\n',
    '',
    'unconfigured branch brand',
)
docs = once(
    docs,
    '  return (\n    <main>\n',
    '  return (\n    <main className="sirati-documents-page">\n',
    'configured documents main',
)
old_header = """      <header className="container nav">
        <Link href="/" className="brand">Sirati</Link>
        <div className="account-actions">
          <span className="account-chip muted">{email}</span>
          <button className="account-chip account-button" onClick={signOut}>Sign out</button>
        </div>
      </header>

"""
docs = once(docs, old_header, '', 'configured documents header')
docs = once(docs, '<h1>My documents</h1>', '<h1>My Documents</h1>', 'configured document heading') if docs.count('<h1>My documents</h1>') == 1 else docs.replace('<h1>My documents</h1>', '<h1>My Documents</h1>')
if docs.count('<h1>My Documents</h1>') != 2:
    raise RuntimeError("V12 documents: expected both configured and fallback headings")

# The large career banner was injected immediately inside the configured main.
# Keep its single existing route and test-id; move it beneath CV documents.
card_match = re.search(
    r'\n[ \t]*<section className="sirati-career-shortcut no-print"'
    r'[\s\S]*?</section>\n',
    docs,
)
if not card_match or docs.count('data-testid="career-tools-entry"') != 1:
    raise RuntimeError("V12 documents: Career Tools entry missing or duplicated")
card = card_match.group(0).strip("\n")
card = once(
    card, 'className="sirati-career-shortcut no-print"',
    'className="container sirati-career-shortcut no-print"',
    'career banner container',
)
docs = docs[:card_match.start()] + docs[card_match.end():]

# Retain the ORIGINAL account-controls markup and signOut() callback, tucked
# inside an accessible optional disclosure after the actual saved CV list.
account = """      <section className="container sirati-documents-account-controls no-print"
        aria-label="Account settings">
        <details className="sirati-documents-account-disclosure">
          <summary>Account details · تفاصيل الحساب</summary>
          <div className="account-actions">
            <span className="account-chip muted">{email}</span>
            <button className="account-chip account-button" onClick={signOut}>Sign out</button>
          </div>
        </details>
      </section>
"""
footer = "\n    </main>\n  );\n}\n"
if docs.count(footer) != 1:
    raise RuntimeError("V12 documents: final authenticated page boundary changed")
docs = docs.replace(footer, "\n" + account + "\n" + card + "\n" + footer, 1)
if not (docs.index('className="documents-head"') <
        docs.index('className="document-grid"') <
        docs.index('data-testid="career-tools-entry"')):
    raise RuntimeError("V12 documents: saved CV list must precede career promotion")
docs_path.write_text(docs, encoding="utf-8")

css = css_path.read_text(encoding="utf-8")
marker = "/* Sirati V12: home and documents visual hierarchy */"
if marker in css:
    raise RuntimeError("V12 stylesheet already applied")
css += r"""
/* Sirati V12: home and documents visual hierarchy (non-print presentation). */
@media screen {
  .marketing-page .marketing-hero {
    min-height: 0;
    margin-top: 12px;
    margin-bottom: 22px;
    gap: 24px;
  }
  .marketing-page .marketing-hero .hero-actions { gap: 9px; }
  .sirati-documents-page .documents-section {
    padding-top: clamp(20px, 3.5vw, 40px);
    padding-bottom: 12px;
  }
  .sirati-documents-page .documents-head {
    gap: 12px;
    align-items: flex-start;
  }
  .sirati-documents-page .documents-head h1 {
    font-size: clamp(33px, 5vw, 49px);
    letter-spacing: -.045em;
    line-height: 1.12;
  }
  .sirati-documents-page .documents-head p {
    max-width: 60ch;
    line-height: 1.55;
  }
  .sirati-documents-account-controls { margin: 8px auto 0; }
  .sirati-documents-account-disclosure {
    padding: 12px 0;
    border-top: 1px solid #d9e4db;
    color: #3b5849;
  }
  .sirati-documents-account-disclosure summary {
    display: list-item;
    width: fit-content;
    min-height: 44px;
    padding: 11px 7px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 650;
  }
  .sirati-documents-account-disclosure summary:focus-visible {
    outline: 3px solid #d4b776;
    outline-offset: 2px;
  }
  .sirati-documents-account-disclosure .account-actions {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 9px;
    padding: 8px 0 6px;
  }
  .sirati-documents-account-disclosure .account-chip {
    max-width: 100%;
    overflow-wrap: anywhere;
  }
  .sirati-documents-page .sirati-career-shortcut {
    margin: 16px auto 28px;
    padding: 17px 20px;
    gap: 12px;
    border-radius: 16px;
  }
  .sirati-documents-page .sirati-career-shortcut h2 {
    margin: 5px 0;
    font-size: clamp(18px, 2vw, 21px);
  }
  .sirati-documents-page .sirati-career-shortcut p {
    font-size: 13px;
    line-height: 1.45;
  }
  .sirati-documents-page .sirati-career-shortcut-link {
    min-height: 44px;
    padding: 10px 16px;
    font-size: 13px;
  }
}
@media screen and (max-width: 640px) {
  .marketing-page .marketing-hero {
    padding: 19px 17px 22px;
    margin-top: 9px;
    margin-bottom: 14px;
    border-radius: 18px;
    gap: 16px;
  }
  .marketing-page .marketing-hero h1 {
    font-size: clamp(31px, 8.2vw, 39px);
    line-height: 1.1;
    margin-block: 12px;
  }
  .marketing-page .marketing-hero .hero-lead {
    font-size: 15px;
    line-height: 1.48;
    margin-block: 0 16px;
  }
  .marketing-page .marketing-hero .hero-actions {
    gap: 8px;
    margin-block: 0 12px;
  }
  .marketing-page .marketing-hero .hero-actions .btn {
    min-height: 44px;
    padding: 10px 14px;
    border-radius: 11px;
    font-size: 14px;
  }
  .marketing-page .hero-kicker.sirati-career-studio-mark {
    padding: 5px 9px 5px 5px;
    gap: 8px;
  }
  .marketing-page .career-studio-symbol {
    flex-basis: 36px;
    width: 36px;
    height: 36px;
  }
  .marketing-page .career-studio-symbol svg { width: 29px; height: 29px; }
  .marketing-page .hero-proof { margin-top: 10px; gap: 7px; }
  .marketing-page .hero-proof .proof-item { font-size: 12px; }
  .sirati-documents-page .documents-section {
    padding-top: 20px;
    padding-bottom: 10px;
  }
  .sirati-documents-page .documents-head {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  .sirati-documents-page .documents-head .btn { min-height: 44px; }
  .sirati-documents-page .sirati-career-shortcut {
    margin-block: 12px 24px;
    padding: 15px;
    gap: 10px;
  }
  .sirati-documents-page .sirati-career-shortcut-copy { flex-basis: 100%; }
  .sirati-documents-page .sirati-career-shortcut-link { width: 100%; }
}
@media print {
  .sirati-documents-account-controls,
  .sirati-documents-page .sirati-career-shortcut { display: none !important; }
}
"""
css_path.write_text(css, encoding="utf-8")
print("PASS: V12 homepage nav unified; documents prioritized; account actions and Career Tools preserved.")
