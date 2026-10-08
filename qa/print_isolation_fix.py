#!/usr/bin/env python3
"""P1 #39 — isolate printable CV from mobile wizard and avoid a trailing A4 page.

The actual source is reconstructed by prepare_pages.py. Keep this patch after
all generated theme CSS; fail closed if its DOM anchors change.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1])
builder = (root / "app/builder/page.tsx").read_text(encoding="utf-8")
required = (
    'wizard-builder-shell',
    'preview-wrap wizard-preview-wrap',
    'preview-stage',
    '<CvPreview data={data}',
    'wizard-footer-nav',
)
for marker in required:
    if marker not in builder:
        raise SystemExit(f"FAIL: expected printable Builder DOM marker missing: {marker}")

css_path = root / "app/globals.css"
css = css_path.read_text(encoding="utf-8")
marker = "/* P1 #39: print only the CV sheet */"
if marker in css:
    raise SystemExit("FAIL: print isolation patch already applied")

css += r"""

/* P1 #39: print only the CV sheet */
@media print {
  @page { size: A4; margin: 0; }

  html, body {
    width: 210mm !important;
    height: auto !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: visible !important;
    background: #fff !important;
  }

  /* Excludes page chrome (including injected site toolbars) while leaving
     any Next.js layout wrapper that contains the printable Builder intact. */
  body:has(.wizard-builder-page) > :not(.wizard-builder-page):not(:has(.wizard-builder-page)) {
    display: none !important;
  }

  /* The print DOM path is:
     .wizard-builder-page > .wizard-builder-shell >
     .wizard-preview-wrap > .preview-stage > .cv-sheet
     Removing side panels from FLOW avoids ghost pages; visibility:hidden
     would still reserve their height and is deliberately not used. */
  .wizard-builder-page > :not(.wizard-builder-shell),
  .wizard-builder-shell > :not(.wizard-preview-wrap),
  .wizard-preview-wrap > :not(.preview-stage),
  .wizard-preview-wrap .preview-stage > :not(.cv-sheet) {
    display: none !important;
  }

  .wizard-builder-page,
  .wizard-builder-shell,
  .wizard-preview-wrap,
  .wizard-preview-wrap .preview-stage {
    display: block !important;
    position: static !important;
    inset: auto !important;
    float: none !important;
    flex: none !important;
    grid-template-columns: none !important;
    width: 210mm !important;
    max-width: none !important;
    min-width: 0 !important;
    height: auto !important;
    min-height: 0 !important;
    max-height: none !important;
    margin: 0 !important;
    padding: 0 !important;
    border: 0 !important;
    box-shadow: none !important;
    transform: none !important;
    overflow: visible !important;
    break-before: auto !important;
    break-after: auto !important;
  }

  .wizard-preview-wrap .preview-stage > .cv-sheet {
    display: block !important;
    position: relative !important;
    width: 210mm !important;
    max-width: 210mm !important;
    min-width: 0 !important;
    min-height: 0 !important;
    height: auto !important;
    margin: 0 !important;
    border: 0 !important;
    box-shadow: none !important;
    box-sizing: border-box !important;
    overflow: visible !important;
    break-before: auto !important;
    break-after: auto !important;
  }
}
"""
css_path.write_text(css, encoding="utf-8")
print("Applied P1 #39 CV-only A4 print-flow isolation")
