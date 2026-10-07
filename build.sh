#!/usr/bin/env bash
set -euo pipefail

python3 - <<'PY'
import base64
from pathlib import Path
import zipfile

parts = []
for i in range(1, 8):
    parts.append(Path(f"source.part{i}").read_text().strip())

Path("source.zip").write_bytes(base64.b64decode("".join(parts)))

with zipfile.ZipFile("source.zip") as z:
    z.extractall(".")
PY

cd sirati-cv-source
npm install
npm run build
