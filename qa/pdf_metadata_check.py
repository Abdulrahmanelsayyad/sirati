#!/usr/bin/env python3
"""Fail on overlapping invisible PDF metadata text, verified by PyMuPDF.

Uses *synthetic* test CV only. Compares exact Staging baseline to patch.
Visible CV screenshot is checked by existing Poppler image regression suite.
"""
import json
import re
import os
import subprocess
from pathlib import Path
import fitz

root = Path(os.environ.get("SIRATI_QA_ARTIFACT_DIR", "qa-artifacts")).resolve()
baseline = root/"sirati-pdf-metadata-baseline"/"metadata.pdf"
candidate = root/"sirati-pdf-metadata-candidate"/"metadata.pdf"
assert baseline.is_file() and candidate.is_file(), "Missing downloaded metadata QA PDFs"

def inspect(pdf_path, strict=False):
    doc=fitz.open(str(pdf_path))
    assert len(doc)==1, "Synthetic metadata unexpectedly paginated"
    page=doc[0]
    assert abs(page.rect.width-595.28)<2 and abs(page.rect.height-841.89)<2
    lines=[]
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines",[]):
            for span in line["spans"]:
                t=span["text"].strip()
                if t:
                    bounds=span["bbox"]
                    lines.append({"text":t,"x0":bounds[0],"x1":bounds[2],
                                  "y":(bounds[1]+bounds[3])/2})
    rows={}
    for label,needle in {
        "degree":"بكالوريوس",
        "institution":"كلية",
        "languages":"العربية",
        "english":"Example",
    }.items():
        hits=[s for s in lines if needle in s["text"]]
        assert hits, label + ": synthetic field missing in PDF extracted spans"
        y=hits[0]["y"]
        companions=[s for s in lines if abs(s["y"]-y)<2.5 and s["text"]!=""]
        # Include only spans from the matching row. Fixture has no more
        # than one metadata row at a given vertical coordinate.
        assert len(companions)>=1, f"{label}: metadata row was absent"
        # PyMuPDF may merge several physically separated text objects into
        # one span if it recognizes an inline line. That's fine only if
        # the field separator stays present in the extracted text.
        assert "|" in "".join(item["text"] for item in companions), (
            f"{label}: metadata delimiter lost: {companions}")
        overlaps=[]
        for i,a in enumerate(companions):
            for b in companions[i+1:]:
                intersect=max(0,min(a["x1"],b["x1"])-max(a["x0"],b["x0"]))
                if intersect>0:
                    overlaps.append(round(intersect,2))
        rows[label]={"spans":[(s["text"],round(s["x0"],2),round(s["x1"],2)) for s in companions],
                     "worst_overlap_pt":max(overlaps,default=0)}
    raw=subprocess.run(["pdftotext","-raw","-enc","UTF-8",str(pdf_path),"-"],
                        check=True,capture_output=True,text=True).stdout
    actual=page.get_text(sort=True)
    norm=lambda x: re.sub(r"\s+"," ",re.sub("[\u200e\u200f\u202a-\u202e]","",x)).strip()
    actual=norm(actual);raw=norm(raw)
    # Candidate-only Arabic-Indic date ranges are checked using independent
    # native readers: no OCR, whitespace reconstruction or numeric guesswork.
    # The visible raster must retain Arabic-Indic glyphs (shared visual QA).
    date_results={}
    if strict:
        for date in ("2020-2026", "10/2026", "3.2026"):
            date_results[date]={"poppler_raw":date in raw,
                                "pymupdf_sorted":date in actual}
            assert date in raw, f"Poppler omitted normalized date {date!r}: {raw[-500:]}"
            assert date in actual, f"PyMuPDF omitted normalized date {date!r}: {actual[-500:]}"
    phrase_results={}
    for phrase in ["كلية التمريض","جامعة الزقازيق","اللغة العربية",
                   "اللغة الإنجليزية","بكالوريوس تمريض",
                   "Example Organization","Your City",
                   "التركيز", "المهني", "التنسيق الآمن", "أساليب العمل",
                   "تقييم تجريبي", "التوثيق الآمن", "ICU"]:
        phrase_results[phrase]={"poppler_raw":phrase in raw,
                                "pymupdf_sorted":phrase in actual}
        if strict:
            assert phrase in raw, f"Poppler raw omitted {phrase!r}: {raw[:250]}"
            assert phrase in actual, f"PyMuPDF sorted omitted {phrase!r}: {actual[:250]}"
    return {"rows":rows,"phrases":phrase_results,"dates":date_results}

old=inspect(baseline,strict=False)
new=inspect(candidate,strict=True)
for label in new["rows"]:
    v=new["rows"][label]["worst_overlap_pt"]
    b=old["rows"][label]["worst_overlap_pt"]
    print(f"{label}: baseline max overlap {b:.2f}pt, candidate {v:.2f}pt")
    if v>1.0:
        print("DIAGNOSTIC",label,json.dumps(new["rows"][label],ensure_ascii=False))
        raise SystemExit(f"FAIL: PDF invisible {label} metadata remains overlapped by {v:.2f}pt")
    assert v<=max(b,1.0), f"{label}: overlap worsened"
out=Path("candidate/pdf-perf-visual")
out.mkdir(parents=True,exist_ok=True)
(out/"metadata-spacing-results.json").write_text(
    json.dumps({"baseline":old,"candidate":new},indent=2,ensure_ascii=False))
with open(os.environ["GITHUB_STEP_SUMMARY"],"a") as file:
    file.write("\n## Synthetic PDF adjacent metadata regression\n")
    file.write("- PyMuPDF extracted Arabic/English metadata field phrases; Poppler raw agreed\n")
    file.write("- No overlapping PDF text glyph bounds across 4 mixed metadata rows\n")
print("PASS metadata text separate, extractable and non-overlapping")
