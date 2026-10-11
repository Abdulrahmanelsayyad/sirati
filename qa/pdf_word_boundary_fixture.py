#!/usr/bin/env python3
"""Augment both baseline and candidate synthetic QA fixture with original bug strings.

NEVER applied outside explicitly opted-in CI, never touches Production source.
"""
import os,sys
from pathlib import Path
if os.environ.get("SIRATI_PDF_QA_FIXTURE") != "1":
    raise SystemExit("FAIL: issue #120 fixture is CI-only")
root=Path(sys.argv[1])
p=root/"app"/"qa-pdf-ats"/"page.tsx"
text=p.read_text(encoding="utf-8")
target="""      {mode !== 'short' && <>
      <h1 style={{fontSize:27,margin:'0 0 10px'}}>"""
assert text.count(target)==1, "Incompatible synthetic QA fixture; fail closed"
expanded="""      {mode !== 'short' && <>
      {mode === 'en1' && <section>
        <p>Healthcare professional with a focus on clear communication, accurate documentation, service quality and teamwork.</p>
        <p>Communication, Documentation, Teamwork, Quality, Patient Support</p>
        <p>Example Organization</p>
      </section>}
      <h1 style={{fontSize:27,margin:'0 0 10px'}}>"""
p.write_text(text.replace(target,expanded),encoding="utf-8")
print("PASS: identical synthetic missing-space strings injected for #120")
