"""Temporary source-shape probe to diagnose guest template loader; source only."""
from pathlib import Path
import re
import sys

root=Path(sys.argv[1]).resolve()
s=(root/"app/templates/page.tsx").read_text(encoding="utf-8")
lines=s.splitlines()
anchors=re.compile(r"checking|setChecking|auth\.|getUser|getSession|signIn|window\.location|template|return \(|useEffect|onClick",re.I)
select=set(range(min(len(lines),95)))
for i,line in enumerate(lines):
    if (re.search(r"Checking your account|setChecking|auth\.getUser|auth\.getSession|if \(checking\)|window\.location|function choose|handleChoose|function select|function handle|return \(",line,re.I)):
        select.update(range(max(0,i-7),min(len(lines),i+15)))
# Log static UI source, never account data, credentials, or runtime env.
print("SIRATI_TEMPLATE_SHAPE_BEGIN")
print("Source lines:",len(lines))
for i in sorted(select):
    if i>=500: break
    line=lines[i].rstrip()[:230]
    if re.search(r"secret|password|service.role|bearer|token",line,re.I):
        line="<redacted static source>"
    print(f"{i+1:04d} {line}")
print("SIRATI_TEMPLATE_SHAPE_END")
