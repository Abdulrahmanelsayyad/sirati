#!/usr/bin/env bash
# Render static-site build: isolated Sirati Staging ONLY.
set -euo pipefail

: "${NEXT_PUBLIC_SUPABASE_URL:?Missing staging Supabase URL}"
test "$NEXT_PUBLIC_SUPABASE_URL" = "https://ykfxcxhozqqsvhtdyxho.supabase.co" || {
  echo "FAIL: refusing a build against a non-staging Supabase project" >&2
  exit 1
}
test "${NEXT_PUBLIC_BASE_PATH:-}" = "" || {
  echo "FAIL: Render staging must use an empty basePath" >&2
  exit 1
}

python3 - <<'PY'
import base64
from pathlib import Path
from zipfile import ZipFile

chunks = [
    Path(f"source.part{i}").read_text().strip()
    for i in (1, 2, 3)
]
chunks.extend(Path(f"source.part4{x}").read_text().strip() for x in ("a", "b", "c"))
chunks.extend(Path(f"source.part{i}").read_text().strip() for i in (5, 6, 7))
Path("/tmp/sirati-render-staging.zip").write_bytes(base64.b64decode("".join(chunks)))
Path("site-src").mkdir(exist_ok=True)
with ZipFile("/tmp/sirati-render-staging.zip") as archive:
    archive.extractall("site-src")
PY

python3 .github/scripts/prepare_pages.py site-src/sirati-cv-source
python3 qa/render_staging_patch.py site-src/sirati-cv-source

(
  cd site-src/sirati-cv-source
  npm install --no-audit --no-fund
  npm run build
)

python3 qa/staging_bundle_guard.py site-src/sirati-cv-source/out
echo "PASS: Render staging-only static output ready"
