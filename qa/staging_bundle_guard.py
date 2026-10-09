#!/usr/bin/env python3
"""Check that the downloadable (not deployed) Sirati build targets staging only.

This is a static build inspection, NOT proof of Auth, RLS or paid PDF unlock.
No Supabase keys beyond the public browser key are needed.
"""
from pathlib import Path
import sys

STAGING_URL = "https://ykfxcxhozqqsvhtdyxho.supabase.co"
PRODUCTION_URL = "https://hzzojoiqzbeivxesjlyf.supabase.co"

def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: staging_bundle_guard.py PATH_TO_NEXT_OUT")
    root = Path(sys.argv[1])
    if not root.is_dir() or not (root / "index.html").exists():
        raise SystemExit("FAIL: exported staging site is missing its index.html")

    seen_staging = False
    seen_production = []
    checked = 0
    for file in root.rglob("*"):
        if not file.is_file() or file.suffix not in (".js", ".html", ".json", ".txt"):
            continue
        checked += 1
        body = file.read_text(encoding="utf-8", errors="replace")
        if STAGING_URL in body:
            seen_staging = True
        if PRODUCTION_URL in body:
            seen_production.append(str(file.relative_to(root)))

    if not checked:
        raise SystemExit("FAIL: no searchable output files")
    if not seen_staging:
        raise SystemExit("FAIL: staging Supabase URL is missing from browser bundle")
    if seen_production:
        raise SystemExit("FAIL: production Supabase URL detected in build: " + ", ".join(seen_production[:5]))

    print("PASS: exported browser bundle references the staging Supabase URL")
    print("PASS: production Supabase URL absent from exported browser bundle")
    print("NOTE: only a static connectivity guard; no paid-PDF authorization claim")

if __name__ == "__main__":
    main()
