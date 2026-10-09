"""Read-only diagnostic of generated interface before navigation changes."""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
for rel, limit in [
 ("app/layout.tsx",6500),("components/AccountNav.tsx",6000),
 ("app/documents/page.tsx",14000),("app/page.tsx",10000),
 ("lib/supabase.ts",2500),("lib/supabaseClient.ts",2500),
 ("app/auth/page.tsx",5500),("app/career-tools/page.tsx",1600)]:
  p=root/rel
  print("\nNAV_AUDIT_START",rel,"exists",p.exists(),flush=True)
  if p.exists():
    s=p.read_text(encoding="utf-8")
    if rel=="app/page.tsx":
      for term in ('<header className="marketing-header">','<section className="container hero marketing-hero">','<h1>','<div className="hero-actions">','<nav className="nav-links'):
        ix=s.find(term)
        print("NAV_AUDIT_SEGMENT",term,repr(s[max(0,ix-110):ix+850]) if ix>=0 else 'NOT FOUND',flush=True)
    elif rel=="app/documents/page.tsx":
      print("NAV_AUDIT_CODE",repr(s[:min(len(s),limit)]),flush=True)
    else:
      print("NAV_AUDIT_CODE",repr(s[:limit]),flush=True)
print("NAV_AUDIT_ROUTES",[(p.parent.name) for p in (root/"app").glob("*/page.tsx")],flush=True)
