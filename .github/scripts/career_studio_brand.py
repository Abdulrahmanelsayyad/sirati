"""Replace CV-only homepage product label with the wider Sirati Career Studio mark.
Temporary source discovery stage: print sanitized public homepage markup anchors.
"""
from pathlib import Path
import re
import sys
root=Path(sys.argv[1]).resolve()
home=(root/"app/page.tsx").read_text(encoding="utf-8")
print("CAREER_BRAND_DIAGNOSTIC start length",len(home),flush=True)
for token in ("Building CV","Building a CV","Build your CV","Build CV","CV Builder","building","Career Studio","hero-kicker","brand-mark","sirati-v2-preview-symbol"):
    matches=list(re.finditer(re.escape(token),home,re.I))
    print("CAREER_BRAND_FIND",repr(token),"count",len(matches),flush=True)
    for m in matches[:3]:
        print("CAREER_BRAND_EXCERPT",repr(home[max(0,m.start()-300):min(len(home),m.end()+360)]),flush=True)
print("CAREER_BRAND_DIAGNOSTIC end",flush=True)
