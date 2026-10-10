#!/usr/bin/env bash
# Rebuild the same generated application used by the GitHub Pages pipeline.
# Run from the repository root with Node.js 22 and Python 3.
set -euo pipefail

cd "$(dirname "$0")"

parts=(
  source.part1 source.part2 source.part3
  source.part4a source.part4b source.part4c
  source.part5 source.part6 source.part7
)
for part in "${parts[@]}"; do
  if [[ ! -f "$part" ]]; then
    echo "Missing source archive part: $part" >&2
    exit 1
  fi
done

for tool in base64 unzip python3 node npm; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Required tool not found: $tool" >&2
    exit 1
  fi
done

# Do not silently overwrite an existing generated tree or edits inside it.
build_dir="${SIRATI_BUILD_DIR:-site-src}"
if [[ -e "$build_dir" ]]; then
  echo "Build destination already exists: $build_dir" >&2
  echo "Choose a fresh SIRATI_BUILD_DIR or move the existing directory." >&2
  exit 1
fi

archive="$(mktemp "${TMPDIR:-/tmp}/sirati-source.XXXXXX.zip")"
trap 'rm -f "$archive"' EXIT

cat "${parts[@]}" | base64 -d > "$archive"
mkdir -p "$build_dir"
unzip -q "$archive" -d "$build_dir"

source_dir="$build_dir/sirati-cv-source"
if [[ ! -d "$source_dir" ]]; then
  echo "Archive did not contain sirati-cv-source" >&2
  exit 1
fi

# These generator hooks are required for parity with the deployed app.
python3 .github/scripts/prepare_pages.py "$source_dir"
python3 qa/print_isolation_fix.py "$source_dir"

(
  cd "$source_dir"
  npm install
  npm run build
)
echo "Static site built at: $source_dir/out"
