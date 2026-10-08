"""Place CV Quality inline above the live CV preview instead of floating over forms.

Runs after cv_readiness_check.py and all other generated Builder patches.
Never change a CV document or any PDF/print content.
"""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
layout = root / "app/layout.tsx"
builder = root / "app/builder/page.tsx"
quality = root / "components/CvReadinessCheck.tsx"
css_path = root / "app/globals.css"

layout_text = layout.read_text(encoding="utf-8")
quality_import = "import CvReadinessCheck from '@/components/CvReadinessCheck';\n"
quality_mount = "<CvReadinessCheck />"
if quality_import not in layout_text or quality_mount not in layout_text:
    raise RuntimeError("Expected old global CV Quality mount missing")
layout.write_text(layout_text.replace(quality_import, "").replace(quality_mount, ""), encoding="utf-8")

builder_text = builder.read_text(encoding="utf-8")
# The generated Builder owns the preview; keep quality in the same panel, before
# the printable CV sheet. It must not mount in the print-only .cv-sheet.
preview = re.search(
    r'<div className="preview-stage">',
    builder_text,
)
if not preview:
    raise RuntimeError("Cannot locate live preview stage; refuse floating fallback")
if quality_mount in builder_text:
    raise RuntimeError("Unexpected duplicate CV Quality mount in Builder")
if quality_import not in builder_text:
    first_import = re.search(r'^import ', builder_text, flags=re.MULTILINE)
    if not first_import:
        raise RuntimeError("Cannot locate Builder import section")
    builder_text = builder_text[:first_import.start()] + quality_import + builder_text[first_import.start():]
    preview = re.search(
        r'<div className="preview-stage">',
        builder_text,
    )
assert preview
builder_text = (
    builder_text[:preview.end()]
    + "\n          <CvReadinessCheck />"
    + builder_text[preview.end():]
)
builder.write_text(builder_text, encoding="utf-8")

quality_text = quality.read_text(encoding="utf-8")
needle = "      {open && (\n        <div className=\"cv-readiness__panel\">"
if needle not in quality_text:
    raise RuntimeError("Cannot locate CV Quality details panel")
quality_text = quality_text.replace(needle, """      <div
        className="cv-readiness__bar cv-readiness__bar--inline"
        role="progressbar"
        aria-label={language === 'ar' ? 'نسبة جودة السيرة الذاتية' : 'CV quality completion'}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={score}
      >
        <span style={{ width: `${score}%` }} />
      </div>

""" + needle, 1)
quality.write_text(quality_text, encoding="utf-8")

css_path.write_text(css_path.read_text(encoding="utf-8") + r'''

/* CV Quality lives inside the preview column; never float above Builder inputs. */
.wizard-preview-wrap .preview-stage > .cv-readiness {
  position: relative;
  inset: auto;
  z-index: auto;
  box-sizing: border-box;
  order: -1;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  margin: 0 0 12px;
}
.wizard-preview-wrap .cv-readiness__trigger {
  width: 100%;
  min-height: 48px;
  margin: 0;
  padding: 10px 12px;
  justify-content: space-between;
  border-radius: 12px;
  box-shadow: none;
  background: #fff;
}
.wizard-preview-wrap .cv-readiness__bar--inline {
  height: 7px;
  margin: 8px 0 0;
}
.wizard-preview-wrap .cv-readiness__panel {
  position: relative;
  inset: auto;
  z-index: auto;
  max-height: min(360px, 44vh);
  overflow-y: auto;
  margin-top: 10px;
  box-shadow: none;
}
@media (max-width: 760px) {
  .wizard-preview-wrap .preview-stage > .cv-readiness {
    top: auto;
    right: auto;
    left: auto;
    width: 100%;
  }
}
@media print {
  .cv-readiness { display: none !important; }
}
''', encoding="utf-8")
print("Anchored CV Quality above the CV preview (no floating overlay).")
