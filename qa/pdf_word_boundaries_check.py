#!/usr/bin/env python3
"""Issue #120: independent word-boundary regression. Synthetic local PDFs only.

The earlier QA suite inserted spaces between extracted PDF.js items and hence
masked actual merged words. Require real separators from Poppler and PyMuPDF,
without repairing source text or inventing whitespace in the assertions.
"""
import json
import os
import re
import subprocess
import unicodedata
from pathlib import Path
import fitz

root = Path("/tmp")
samples = {
    "long-en1": [
        "Healthcare professional with a focus on clear communication",
        "accurate documentation, service quality and teamwork",
        "Communication, Documentation, Teamwork, Quality, Patient Support",
        "Example Organization",
        "Professional experience, Emergency Nursing, Patient Safety, and Infection Control",
    ],
    "long-short": [
        "Technology professional focused on practical problem-solving",
        "reliable software delivery, testing and clear technical documentation",
        "Software Development, Debugging, Testing, Collaboration, Documentation",
    ],
    "modern-en-1440": ["SummaryMarker professional summary", "SkillsMarker programming"],
    "gold-sidebar-en-390": ["SummaryMarker professional summary", "SkillsMarker programming"],
    "photo-profile-sidebar-en-1440": ["SummaryMarker professional summary"],
}
arabic_phrases = {
    "long-ar3": ["الخبرة المهنية", "تمريض الطوارئ", "سلامة المرضى"],
    "modern-ar-390": ["ملخص مهني", "مهارات البرمجة"],
}
directory = lambda prefix, name: root / ("sirati-pdf-" + prefix) / (name + ".pdf")
paths = {
    "long-en1": ("long-baseline", "long-candidate"),
    "long-short": ("long-baseline", "long-candidate"),
    "long-ar3": ("long-baseline", "long-candidate"),
    "modern-en-1440": ("baseline", "candidate"),
    "gold-sidebar-en-390": ("baseline", "candidate"),
    "modern-ar-390": ("baseline", "candidate"),
    "photo-profile-sidebar-en-1440": ("photo-baseline", "photo-candidate"),
}
def squash(s):
    # Remove directional formatting controls, not word-boundary whitespace.
    clean = "".join(ch for ch in unicodedata.normalize("NFC",s)
                    if unicodedata.category(ch) != "Cf")
    return re.sub(r"\\s+", " ", clean).strip()

def extract(pdf, mode):
    if mode.startswith("poppler"):
        flag = "-raw" if mode == "poppler-raw" else "-layout"
        return squash(subprocess.run(
            ["pdftotext",flag,"-enc","UTF-8",str(pdf),"-"],
            check=True,capture_output=True,text=True).stdout)
    with fitz.open(str(pdf)) as document:
        return squash(" ".join(page.get_text(sort=True) for page in document))

modes = ["poppler-raw","poppler-layout","pymupdf"]
reports = []
errors = []
baselineFailures = 0
for name in [*samples, *arabic_phrases]:
    beforeKey, afterKey = paths[name]
    before, after = directory(beforeKey,name),directory(afterKey,name)
    assert before.is_file() and after.is_file(), "Missing PDF for "+name
    phrases = samples.get(name, arabic_phrases.get(name, []))
    for mode in modes:
        actual = extract(after,mode)
        old = extract(before,mode)
        for phrase in phrases:
            phrase = squash(phrase)
            ok = phrase in actual
            before_ok = phrase in old
            baselineFailures += int(not before_ok)
            reports.append({"id":name,"tool":mode,"phrase":phrase,"pass":ok,"baseline_pass":before_ok})
            if not ok:
                errors.append(f"{name} / {mode}: missing [{phrase}]; after excerpt: {actual[:350]}")
        print(f"{name} {mode}: {sum(phrase in actual for phrase in phrases)}/{len(phrases)} required boundaries")
output=Path("candidate/pdf-perf-visual")
output.mkdir(parents=True,exist_ok=True)
(output/"word-boundary-results.json").write_text(json.dumps(reports,indent=2,ensure_ascii=False))
if errors:
    for err in errors: print("FAIL",err)
    raise SystemExit(f"Word-boundary regression failed: {len(errors)} missing phrase observations")
print(f"PASS: {len(reports)} exact phrase x tool checks; historical baseline missing {baselineFailures} expected observations")
with open(os.environ["GITHUB_STEP_SUMMARY"],"a") as f:
    f.write(f"\n## Issue #120 native word-boundary regression\n- {len(reports)} multiword phrase/tool checks passed across Poppler raw/layout and PyMuPDF\n- Baseline missing {baselineFailures} phrase observations\n- No OCR or artificial word separators added by test\n")
