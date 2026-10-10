"""Keep menu feature search fixed below the brand header, outside the scrolling links.

The search input remains interactive and searchable in both RTL and LTR.
No authentication, document, PDF, backend, or payment behavior is modified.
"""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
menu_path = root / "components/SiratiSiteMenu.tsx"
css_path = root / "app/globals.css"
menu = menu_path.read_text(encoding="utf-8")

# Move exactly the existing search UI; do not recreate search state or handlers.
matches = list(re.finditer(
    r'(?ms)^          <div className="sirati-menu-feature-search">\n.*?^          </div>\n',
    menu,
))
if len(matches) != 1:
    raise RuntimeError(f"Fixed search: expected one search UI block, found {len(matches)}")
search_markup = matches[0].group()
menu = menu.replace(search_markup, "", 1)
boundary = '        </header>\n        <div className="sirati-menu-scroll">'
if menu.count(boundary) != 1:
    raise RuntimeError("Fixed search: brand header / scroll boundary changed")
menu = menu.replace(
    boundary,
    '        </header>\n' + search_markup +
    '        <div className="sirati-menu-scroll">',
    1,
)
if not (menu.index("sirati-menu-header") < menu.index("sirati-menu-feature-search") <
        menu.index('className="sirati-menu-scroll"')):
    raise RuntimeError("Fixed search: unexpected menu child ordering")
menu_path.write_text(menu, encoding="utf-8")

css = css_path.read_text(encoding="utf-8")
marker = "/* Sirati fixed menu search under drawer header */"
if marker in css:
    raise RuntimeError("Fixed search already applied")
css += r"""
/* Sirati fixed menu search under drawer header */
@media screen {
  .sirati-menu-panel > .sirati-menu-header {
    flex: 0 0 auto;
  }
  .sirati-menu-panel > .sirati-menu-feature-search {
    position: static;
    inset: auto;
    z-index: auto;
    flex: 0 0 auto;
    margin: 0;
    padding: 12px clamp(14px, 3vw, 20px);
    border-radius: 0;
    border-top: 0;
    border-left: 0;
    border-right: 0;
    background: #fffefa;
    box-shadow: none;
  }
  .sirati-menu-panel > .sirati-menu-scroll {
    flex: 1 1 auto;
    min-height: 0;
    overflow-y: auto;
    overflow-x: hidden;
  }
}
"""
css_path.write_text(css, encoding="utf-8")
print("PASS: feature search stays directly below the fixed menu header; only links scroll.")
