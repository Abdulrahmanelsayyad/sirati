"""V11: simplify the CV template picker after sitewide navigation is generated.

The shared navbar already supplies Sirati branding and a desktop Documents
shortcut; the existing accessible drawer supplies Documents and Career Tools
on mobile. This patch changes layout/copy only, not navigation targets or data.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
page_path = root / "app/templates/page.tsx"
menu_path = root / "components/SiratiSiteMenu.tsx"
css_path = root / "app/globals.css"

page = page_path.read_text(encoding="utf-8")
old_header = """      <header className="container nav flow-nav">
        <Link href="/" className="brand">Sirati</Link>
        <Link href="/documents" className="btn btn-secondary">My documents</Link>
      </header>

"""
if page.count(old_header) != 1:
    raise RuntimeError("V11: expected exactly one redundant template-page header")
page = page.replace(old_header, "", 1)

copy_changes = [
    ("<h1>Choose the look of your CV.</h1>",
     "<h1>Choose your CV template</h1>"),
    ("<p>You can change the template later without losing any information.</p>",
     "<p>Find a layout that fits your career. Change it anytime without losing information.</p>"),
]
for old, new in copy_changes:
    if page.count(old) != 1:
        raise RuntimeError(f"V11: missing or ambiguous template intro: {old}")
    page = page.replace(old, new, 1)
page_path.write_text(page, encoding="utf-8")

# Move the Tools shortcut into the existing mobile drawer; keep it in desktop nav.
menu = menu_path.read_text(encoding="utf-8")
before = """<a className="sirati-topbar-link" href={withBasePath('/career-tools/')}"""
after = """<a className="sirati-topbar-link sirati-topbar-tools" href={withBasePath('/career-tools/')}"""
if menu.count(before) != 1:
    raise RuntimeError("V11: expected one global Tools shortcut")
menu_path.write_text(menu.replace(before, after, 1), encoding="utf-8")

css = css_path.read_text(encoding="utf-8")
marker = "/* Sirati V11: compact CV template selection */"
if marker in css:
    raise RuntimeError("V11: layout patch already applied")
css += r"""
/* Sirati V11: compact CV template selection — scoped to screen UI. */
@media screen {
  .flow-page .flow-heading h1 { text-wrap: balance; }
  .flow-page .flow-heading p { max-width: 56ch; }
}
@media screen and (max-width: 760px) {
  .sirati-site-topbar .sirati-topbar-tools { display: none; }
  .flow-page .flow-shell { padding-top: 12px; }
  .flow-page .journey-steps { margin-bottom: 18px; }
  .flow-page .flow-heading { margin-top: 17px; margin-bottom: 18px; }
  .flow-page .flow-heading .eyebrow { font-size: 12px; }
  .flow-page .flow-heading h1 {
    font-size: clamp(29px, 8vw, 39px);
    line-height: 1.09;
    letter-spacing: -.035em;
    margin-block: 9px 10px;
  }
  .flow-page .flow-heading p {
    font-size: 14px;
    line-height: 1.52;
    margin-block: 0 14px;
  }
  .flow-page .template-library-entrance { margin-block: 8px 10px; }
}
@media print {
  .flow-page .flow-heading { display: none !important; }
}
"""
css_path.write_text(css, encoding="utf-8")
print("PASS: V11 single Sirati brand, Documents in existing navigation, compact template header.")
