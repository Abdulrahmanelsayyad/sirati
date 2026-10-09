"""Scoped post-generation UX enhancement: searchable Sirati feature drawer.

No Supabase, account records, auth, print, CV editing or payment changes.
Patch exact output anchors so incompatible future interfaces fail safely.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
menu_path = root / "components/SiratiSiteMenu.tsx"
style_path = root / "app/globals.css"
menu = menu_path.read_text(encoding="utf-8")

def replace_one(before, after, label):
    global menu
    matches = menu.count(before)
    if matches != 1:
        raise RuntimeError(f"{label}: expected 1 anchor, found {matches}")
    menu = menu.replace(before, after, 1)

replace_one(
    "  const [open, setOpen] = useState(false);",
    """  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');""",
    "client-only feature search state",
)
replace_one(
    """  const name = accountName(user);
  const close = () => setOpen(false);""",
    """  const name = accountName(user);
  const query = search.trim().toLocaleLowerCase();
  const matches = (item: Item) => (item.title + ' ' + item.detail).toLocaleLowerCase().includes(query);
  const matchingCv = cvFeatures.filter(matches);
  const matchingCareer = careerFeatures.filter(matches);
  const matchingCount = matchingCv.length + matchingCareer.length;
  const close = () => { setOpen(false); setSearch(''); };""",
    "normalized bilingual filtering",
)
replace_one(
    """onClick={() => setOpen(true)}>
      <span aria-hidden="true" className="sirati-menu-bars">""",
    """onClick={() => { setSearch(''); setOpen(true); }}>
      <span aria-hidden="true" className="sirati-menu-bars">""",
    "reset on opening",
)
replace_one(
    """          </section>
          <section className="sirati-menu-group">
            <h3>مساحة العمل</h3>""",
    """          </section>
          <div className="sirati-menu-feature-search">
            <label htmlFor="sirati-feature-search">البحث عن أداة · Search features</label>
            <input id="sirati-feature-search" type="search" dir="auto"
              autoComplete="off" value={search}
              onChange={event => setSearch(event.target.value)}
              placeholder="مثال: LinkedIn أو CV أو خطاب" />
            <p role="status" aria-live="polite">
              {query ? String(matchingCount) + ' نتائج · matches'
                : 'ابحث بالعربي أو الإنجليزي للوصول للأداة بسرعة'}
            </p>
          </div>
          {!query && <section className="sirati-menu-group">
            <h3>مساحة العمل</h3>""",
    "search UI and workspace conditional",
)
replace_one(
    """          </section>
          <NavGroup title="السيرة الذاتية" items={cvFeatures} close={close} />
          <NavGroup title="أدوات التطوير المهني" items={careerFeatures} close={close} />
          <section className="sirati-menu-group">
            <h3>المساعدة</h3>""",
    """          </section>}
          {matchingCv.length > 0 && <NavGroup title="السيرة الذاتية" items={matchingCv} close={close} />}
          {matchingCareer.length > 0 && <NavGroup title="أدوات التطوير المهني" items={matchingCareer} close={close} />}
          {query && matchingCount === 0 &&
            <div className="sirati-menu-empty" role="status">
              <strong>لا توجد أدوات مطابقة</strong>
              <span>No matching tools. Try CV, LinkedIn or Interview.</span>
              <button type="button" onClick={() => setSearch('')}>إظهار كل الأدوات · Show all</button>
            </div>}
          {!query && <section className="sirati-menu-group">
            <h3>المساعدة</h3>""",
    "filtered feature groups and empty state",
)
replace_one(
    """          </section>
          <div className="sirati-menu-footer">كل الأدوات مجانية · All tools are free</div>""",
    """          </section>}
          <div className="sirati-menu-footer">كل الأدوات مجانية · All tools are free</div>""",
    "support conditional",
)

menu_path.write_text(menu, encoding="utf-8")
css = style_path.read_text(encoding="utf-8")
marker = "/* Sidebar feature finder V2 */"
if marker in css:
    raise RuntimeError("Feature finder V2 already installed")
css += r"""
/* Sidebar feature finder V2 */
@media screen {
  .sirati-menu-feature-search {
    margin-top: 17px;
    padding: 14px;
    border: 1px solid #d9e5dc;
    border-radius: 15px;
    background: #fffefa;
  }
  .sirati-menu-feature-search label {
    display: block;
    margin-bottom: 8px;
    color: #244a3b;
    font-size: 13px;
    font-weight: 750;
  }
  .sirati-menu-feature-search input {
    display: block;
    box-sizing: border-box;
    width: 100%;
    min-width: 0;
    min-height: 44px;
    padding: 10px 12px;
    border: 1px solid #b6cdbd;
    border-radius: 11px;
    background: #f8faf7;
    color: #153e31;
    font: inherit;
    font-size: 14px;
  }
  .sirati-menu-feature-search input:focus-visible,
  .sirati-menu-empty button:focus-visible {
    outline: 3px solid #d6b67e;
    outline-offset: 2px;
  }
  .sirati-menu-feature-search p {
    margin: 9px 0 0;
    color: #607469;
    font-size: 12px;
    line-height: 1.5;
  }
  .sirati-menu-empty {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    padding: 22px 12px;
    color: #345743;
    line-height: 1.5;
  }
  .sirati-menu-empty strong { font-size: 16px; }
  .sirati-menu-empty span { font-size: 13px; color: #536d5d; }
  .sirati-menu-empty button {
    min-height: 42px;
    padding: 9px 13px;
    border: 1px solid #bdd2c2;
    border-radius: 10px;
    background: #f0f6f0;
    color: #1c563f;
    font-weight: 700;
    cursor: pointer;
  }
}
"""
style_path.write_text(css, encoding="utf-8")
print("PASS: sidebar feature search handles Arabic/English, zero results, reset and screen readers.")
