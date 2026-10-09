"""Sirati UX phase 2: CV form/preview jump actions and predictable touch-sized forms.

Runs after sitewide_navigation_ux.py and uses only generated UI/CSS.
No new routes, secrets, stored data, workflow, auth or PDF logic changes.
"""
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve()
menu_path=root/"components/SiratiSiteMenu.tsx"
css_path=root/"app/globals.css"
menu=menu_path.read_text(encoding="utf-8")

def once(before,after,reason):
    global menu
    if menu.count(before)!=1:
        raise RuntimeError("Sirati UX phase2 "+reason+": expected one anchor, got "+str(menu.count(before)))
    menu=menu.replace(before,after,1)

once("""  const name = accountName(user);
  const query = search.trim().toLocaleLowerCase();""",
"""  const jumpTo = (selector: string) => {
    const el = document.querySelector<HTMLElement>(selector);
    if (!el) return;
    el.style.scrollMarginTop = '86px';
    el.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',block:'start'});
  };
  const onBuilder = pathname.includes('/builder');
  const name = accountName(user);
  const query = search.trim().toLocaleLowerCase();""","manual form/preview buttons")

once("""      <div className="sirati-topbar-shortcuts">
        <a className="sirati-topbar-link" href={withBasePath('/templates')}
          aria-current={onCv ? 'page' : undefined}><span aria-hidden="true">▤</span> <span>CV</span></a>
        <a className="sirati-topbar-link" href={withBasePath('/career-tools/')}
          aria-current={onTools ? 'page' : undefined}><span aria-hidden="true">✦</span> <span>Tools</span></a>
        <a className="sirati-topbar-link sirati-topbar-docs"
          href={withBasePath(user ? '/documents' : '/auth?next=/documents')}
          aria-current={onDocuments ? 'page' : undefined}><span aria-hidden="true">▣</span> <span>Documents</span></a>
      </div>""",
"""      {onBuilder
        ? <div className="sirati-topbar-workflow" role="group" aria-label="CV editing navigation">
            <button type="button" className="sirati-topbar-link"
              aria-label="Jump to CV form" onClick={() => jumpTo('.wizard-panel')}>✎ <span>Edit · تعديل</span></button>
            <button type="button" className="sirati-topbar-link"
              aria-label="Jump to CV preview" onClick={() => jumpTo('.wizard-preview-wrap')}>▤ <span>Preview · معاينة</span></button>
          </div>
        : <div className="sirati-topbar-shortcuts">
            <a className="sirati-topbar-link" href={withBasePath('/templates')}
              aria-current={onCv ? 'page' : undefined}><span aria-hidden="true">▤</span> <span>CV</span></a>
            <a className="sirati-topbar-link" href={withBasePath('/career-tools/')}
              aria-current={onTools ? 'page' : undefined}><span aria-hidden="true">✦</span> <span>Tools</span></a>
            <a className="sirati-topbar-link sirati-topbar-docs"
              href={withBasePath(user ? '/documents' : '/auth?next=/documents')}
              aria-current={onDocuments ? 'page' : undefined}><span aria-hidden="true">▣</span> <span>Documents</span></a>
          </div>}""","two explicit non-mutating Builder jump actions")
menu_path.write_text(menu,encoding="utf-8")

css=css_path.read_text(encoding="utf-8")
if "/* Sirati UX phase 2: inputs and wizard travel */" in css:
    raise RuntimeError("UX phase2 CSS duplicate")
css+=r"""
/* Sirati UX phase 2: inputs and wizard travel */
@media screen {
  .sirati-topbar-workflow {display:flex;align-items:center;gap:5px;margin-inline-start:auto;min-width:0}
  .sirati-topbar-workflow button {font:inherit;font-size:12px;font-weight:750;cursor:pointer;min-height:44px}
  .sirati-topbar-workflow button:hover {background:#e7f1e8;border-color:#cfe3d3}
  .wizard-builder-page .wizard-section-card,.wizard-builder-page .wizard-panel-top {min-width:0}
  .wizard-builder-page .wizard-section-card .field {min-width:0;max-width:100%}
  .wizard-builder-page .wizard-section-card .field :is(
    input:not([type="radio"]):not([type="checkbox"]):not([type="file"]):not([type="hidden"]),
    select,textarea
  ) {box-sizing:border-box;max-width:100%;min-width:0;min-height:44px;scroll-margin-top:95px}
  .wizard-builder-page .wizard-section-card .field textarea {resize:vertical;line-height:1.55}
  .wizard-builder-page .wizard-section-card .field label {line-height:1.55}
  .wizard-builder-page :is(.wizard-footer-nav .btn,.cv-substeps button) {min-height:44px}
  .wizard-builder-page :is(.wizard-panel,.wizard-preview-wrap) {scroll-margin-top:86px}
  .wizard-builder-page .wizard-section-card .field :is(input,textarea,select):focus-visible {
    outline:3px solid #5c9d77;outline-offset:2px;
  }
  .career-page :is(.career-form,.career-result,.career-card),
  .sirati-profile-page :is(.sirati-profile-card,.sirati-profile-shell) {
    min-width:0;max-width:100%;box-sizing:border-box;
  }
  .career-page .career-form :is(input,select,textarea),
  .career-page .career-result textarea,
  .sirati-profile-page .sirati-profile-card input {
    box-sizing:border-box;width:100%;max-width:100%;min-width:0;min-height:44px;
  }
  .career-page :is(.career-tab,.career-actions button,.career-form .btn),
  .sirati-profile-page .sirati-profile-card button {min-height:44px}
  .career-page .career-form label {line-height:1.55}
  .sirati-profile-page .sirati-profile-card :is(input,button):focus-visible {
    outline:3px solid #5c9d77;outline-offset:2px;
  }
}
@media screen and (max-width:760px) {
  .sirati-topbar-workflow .sirati-topbar-link {font-size:12px;padding:7px 8px;gap:3px}
  .wizard-builder-page .wizard-section-card .field :is(
    input:not([type="radio"]):not([type="checkbox"]):not([type="file"]):not([type="hidden"]),
    select,textarea
  ),.career-page :is(.career-form input,.career-form textarea,.career-form select,.career-result textarea) {
    font-size:16px;
  }
  .career-page .career-actions button {flex:1 1 142px;min-width:0}
  .wizard-builder-page .wizard-panel-top :is(h1,h2,h3) {line-height:1.25}
}
@media screen and (max-width:350px) {
  .sirati-topbar-workflow {gap:1px}
  .sirati-topbar-workflow .sirati-topbar-link {padding:7px 5px;font-size:11px}
}
"""
css_path.write_text(css,encoding="utf-8")
print("PASS: non-mutating jump-to-form/preview; consistent responsive form inputs and buttons.")
