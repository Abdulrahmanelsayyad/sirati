"""Sitewide Navigation UX: a non-overlapping sticky top bar and usable drawer.

Applies after generated career and feature-finder UI. No auth/database/CV/paid
features changed; all destinations are existing routes via withBasePath.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
path=root/"components/SiratiSiteMenu.tsx"
csspath=root/"app/globals.css"
s=path.read_text(encoding="utf-8")
def swap(old,new,label):
    global s
    if s.count(old)!=1: raise RuntimeError(f"Navigation UX {label}: {s.count(old)} anchors")
    s=s.replace(old,new,1)

swap("import { useEffect, useRef, useState } from 'react';",
"""import { useEffect, useRef, useState } from 'react';
import { usePathname } from 'next/navigation';""","route-aware navigation")
swap("  const [open, setOpen] = useState(false);",
"""  const [open, setOpen] = useState(false);
  const pathname = usePathname() || '/';
  const onHome = pathname === '/';
  const onCv = /\\/builder|\\/templates/.test(pathname);
  const onTools = pathname.includes('/career-tools');
  const onDocuments = pathname.includes('/documents');
  const pageName = onHome ? 'Home · الرئيسية' : onCv
    ? (pathname.includes('/builder') ? 'CV Editor · محرر السيرة' : 'CV Templates · القوالب')
    : onTools ? 'Career Tools · أدوات المهنة'
    : onDocuments ? 'My Documents · مستنداتي'
    : pathname.includes('/profile') ? 'My Profile · الملف الشخصي'
    : pathname.includes('/auth') ? 'Account · الحساب'
    : 'Sirati · سيرتي';""","current section")
swap("const focusable = menu?.querySelectorAll<HTMLElement>('a[href],button:not([disabled])');",
"const focusable = menu?.querySelectorAll<HTMLElement>('a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled])');",
"keyboard focus trap handles input")
swap("""  return <>
    <button ref={opener} type="button" className="sirati-menu-trigger no-print" """.rstrip(),
"""  return <>
    <nav className="sirati-site-topbar no-print" aria-label="Primary site navigation · التنقل الرئيسي">
      <a className="sirati-topbar-brand" href={withBasePath('/')} aria-label="Sirati — Home">
        <span className="sirati-topbar-brand-icon" aria-hidden="true">S</span><strong>Sirati</strong>
      </a>
      <span className="sirati-topbar-location" aria-label="Current section">{pageName}</span>
      <div className="sirati-topbar-shortcuts">
        <a className="sirati-topbar-link" href={withBasePath('/templates')}
          aria-current={onCv ? 'page' : undefined}><span aria-hidden="true">▤</span> <span>CV</span></a>
        <a className="sirati-topbar-link" href={withBasePath('/career-tools/')}
          aria-current={onTools ? 'page' : undefined}><span aria-hidden="true">✦</span> <span>Tools</span></a>
        <a className="sirati-topbar-link sirati-topbar-docs"
          href={withBasePath(user ? '/documents' : '/auth?next=/documents')}
          aria-current={onDocuments ? 'page' : undefined}><span aria-hidden="true">▣</span> <span>Documents</span></a>
      </div>
    <button ref={opener} type="button" className="sirati-menu-trigger no-print" """.rstrip(),
"topbar shortcuts")
swap("""      <span className="sirati-menu-trigger-text">القائمة</span>
    </button>
    {open &&""",
"""      <span className="sirati-menu-trigger-text">Menu · القائمة</span>
    </button>
    </nav>
    {open &&""","close topbar and bilingual menu")
path.write_text(s,encoding="utf-8")

css=csspath.read_text(encoding="utf-8")
if "/* Sirati sitewide navigation UX */" in css: raise RuntimeError("UX already applied")
css+=r"""
/* Sirati sitewide navigation UX */
@media screen {
  html {scroll-padding-top:82px}
  .sirati-site-topbar {
    position:sticky;top:0;inset-inline:0;z-index:1050;
    display:flex;align-items:center;gap:12px;
    width:100%;min-width:0;min-height:64px;box-sizing:border-box;
    padding:8px clamp(14px,3vw,36px);
    border-bottom:1px solid rgba(28,75,51,.12);
    background:rgba(252,253,249,.96);backdrop-filter:blur(14px);
    box-shadow:0 3px 18px rgba(18,56,36,.045);color:#193f30;
    direction:ltr;
  }
  .sirati-topbar-brand {display:flex;align-items:center;gap:9px;text-decoration:none;
    flex:0 0 auto;color:#183f2e;font-weight:850}
  .sirati-topbar-brand strong {font-size:20px;letter-spacing:-.045em}
  .sirati-topbar-brand-icon {display:grid;place-items:center;width:35px;height:35px;
    color:#fbeaca;background:#184f3b;border-radius:11px;font-size:18px}
  .sirati-topbar-location {min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
    color:#607467;font-size:12px;font-weight:650;margin-inline-end:auto}
  .sirati-topbar-shortcuts {display:flex;align-items:center;gap:6px;min-width:0}
  .sirati-topbar-link {display:inline-flex;align-items:center;gap:6px;justify-content:center;
    text-decoration:none;color:#234d3a;background:transparent;white-space:nowrap;
    padding:9px 12px;border:1px solid transparent;border-radius:10px;
    font-size:13px;font-weight:750;min-height:42px;box-sizing:border-box}
  .sirati-topbar-link:hover,.sirati-topbar-link[aria-current="page"] {background:#e7f1e8;
    border-color:#cfe3d3;color:#154531}
  .sirati-site-topbar .sirati-menu-trigger {position:static;inset:auto;top:auto;right:auto;
    flex:0 0 auto;min-height:44px;padding:9px 11px;margin:0;
    box-shadow:none;border-radius:10px;font-size:12px}
  .sirati-site-topbar :is(a,button):focus-visible {outline:3px solid #d2b16e;outline-offset:2px}
  .sirati-menu-feature-search {position:sticky;top:0;z-index:3;background:#fffefa;
    box-shadow:0 6px 12px rgba(16,62,40,.035)}
  .sirati-menu-panel {max-height:100dvh}
  .sirati-menu-scroll {overscroll-behavior:contain}
  .marketing-page .marketing-nav {padding-right:clamp(12px,2.5vw,32px)}
  main :is(h1,h2,h3),.wizard-panel,.wizard-section-card {scroll-margin-top:86px}
}
@media screen and (max-width:760px) {
  .sirati-site-topbar {min-height:58px;padding:6px 11px;gap:8px}
  .sirati-topbar-location {display:none}
  .sirati-topbar-shortcuts {margin-inline-start:auto}
  .sirati-topbar-link {padding:7px 9px;min-height:42px}
  .sirati-topbar-docs {display:none}
  .sirati-site-topbar .sirati-menu-trigger {padding:9px;min-height:43px}
  .sirati-site-topbar .sirati-menu-trigger-text {display:none}
  .sirati-topbar-brand strong {font-size:18px}
  .sirati-topbar-brand-icon {width:30px;height:30px}
}
@media screen and (max-width:350px) {
  .sirati-site-topbar {gap:5px;padding-inline:7px}
  .sirati-topbar-brand {gap:5px}
  .sirati-topbar-link {padding:6px 7px;font-size:12px}
  .sirati-topbar-shortcuts {gap:2px}
  .sirati-site-topbar .sirati-menu-trigger {padding:8px}
}
@media print {
  .sirati-site-topbar {display:none!important}
}
@media (prefers-reduced-motion:reduce) {
  .sirati-site-topbar {scroll-behavior:auto}
}
"""
csspath.write_text(css,encoding="utf-8")
print("PASS: sitewide navigation stays in layout flow; direct shortcuts and keyboard access.")
