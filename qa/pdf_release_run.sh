#!/usr/bin/env bash
# Run from workspace parent containing baseline/ and candidate/ repo checkouts.
# Baseline is approved Staging, NOT main's image-only PDF.
set -euo pipefail
node candidate/qa/pdf_boundary_check.mjs candidate/site-src/sirati-cv-source/lib/siratiPdfExport.ts
export QA_PDF_FIXED_BASELINE=1
export GITHUB_STEP_SUMMARY="${GITHUB_STEP_SUMMARY:-/tmp/sirati-pdf-release-summary.md}"
for variant in baseline candidate; do
  src="$PWD/$variant/site-src/sirati-cv-source"
  port=4174
  [[ "$variant" == candidate ]] && port=4175
  for suite in sections photo longform metadata; do
    suffix=""
    [[ "$suite" == photo ]] && suffix="-photo"
    [[ "$suite" == longform ]] && suffix="-long"
    [[ "$suite" == metadata ]] && suffix="-metadata"
    script="pdf_${suite}_check.mjs"
    [[ "$suite" == metadata ]] && script=pdf_metadata_download.mjs
    cp "candidate/qa/$script" "$src/qa-release-$suite.mjs"
    (cd "$src"; QA_PDF_BASE_URL="http://127.0.0.1:$port/sirati" \
      QA_PDF_RESULTS_DIR="/tmp/sirati-pdf$suffix-$variant" node "qa-release-$suite.mjs")
  done
done
src="$PWD/candidate/site-src/sirati-cv-source"
cp candidate/qa/pdf_rtl_list_style_check.mjs "$src/qa-release-rtl.mjs"
(cd "$src"; QA_PDF_BASE_URL=http://127.0.0.1:4175/sirati node qa-release-rtl.mjs)
for test in metadata quality word_boundaries rtl_numerals_bullets; do
  python3 "candidate/qa/pdf_${test}_check.py"
done
# Extra mobile width: all 9 families in both languages. No claim of physical Android.
(cd "$src"; QA_PDF_ALL_WIDTHS=1 QA_PDF_BASE_URL=http://127.0.0.1:4175/sirati \
  QA_PDF_RESULTS_DIR=/tmp/sirati-pdf-candidate-widths node qa-release-sections.mjs)
python3 - <<'PY'
import json, statistics
from pathlib import Path
b=json.loads(Path('/tmp/sirati-pdf-baseline/results.json').read_text())
c=json.loads(Path('/tmp/sirati-pdf-candidate/results.json').read_text())
assert len(b)==len(c)==36
assert {r['id'] for r in b} == {r['id'] for r in c}
result={'comparison':'approved Staging vs main-derived PDF candidate',
  'baseline_bytes':sum(r['sizeBytes'] for r in b), 'candidate_bytes':sum(r['sizeBytes'] for r in c),
  'baseline_median_ms':statistics.median(r['elapsedMs'] for r in b),
  'candidate_median_ms':statistics.median(r['elapsedMs'] for r in c)}
Path('candidate/pdf-perf-visual/performance.json').write_text(json.dumps(result,indent=2))
print(result)
assert result['candidate_bytes'] <= result['baseline_bytes'] * 1.01
PY

cp candidate/qa/pdf_template_longform_check.mjs "$src/qa-release-template-long.mjs"
long_status=0
(cd "$src"; QA_PDF_BASE_URL=http://127.0.0.1:4175/sirati node qa-release-template-long.mjs) || long_status=$?
native_status=0
python3 candidate/qa/pdf_template_native_check.py || native_status=$?
[[ "$long_status" == 0 && "$native_status" == 0 ]]

# V17: explicit bilingual download/text coverage for all 24 extra variants.
(cd "$src"; QA_PDF_EXTRA_TEMPLATES=1 QA_PDF_ALL_WIDTHS=1 QA_PDF_BASE_URL=http://127.0.0.1:4175/sirati \
  QA_PDF_RESULTS_DIR=/tmp/sirati-pdf-extra-candidate node qa-release-sections.mjs)
python3 candidate/qa/pdf_extra_templates_check.py

python3 candidate/qa/pdf_rtl_raster_check.py
