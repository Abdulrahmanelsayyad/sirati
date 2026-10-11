#!/usr/bin/env python3
"""Synthetic Arabic/LTR adjacent field fixture, only in opted-in CI builds."""
import os
import sys
from pathlib import Path

if os.environ.get("SIRATI_PDF_QA_FIXTURE") != "1":
    raise SystemExit("FAIL: metadata fixture must be explicitly CI-only")

root = Path(sys.argv[1])
page = root / "app/qa-pdf-metadata/page.tsx"
page.parent.mkdir(parents=True,exist_ok=True)
page.write_text(r"""'use client';
import { useRef, useState } from 'react';
import { downloadCvSheet } from '@/lib/siratiPdfExport';
export default function PdfMetadataFixture(){
  const sheet=useRef<HTMLDivElement>(null);
  const [error,setError]=useState('');
  return <main style={{padding:20}}>
    <button onClick={async()=>{setError('');
      try{await downloadCvSheet(sheet.current!,'synthetic-metadata');}
      catch(e){setError(String(e));}
    }}>Download metadata fixture</button>
    <p role="alert">{error}</p>
    <div className="cv-sheet" ref={sheet} dir="rtl"
      style={{boxSizing:'border-box',width:794,minHeight:1123,
       background:'#fff',padding:30,lineHeight:1.8,color:'#13243d',
       fontSize:18,fontFamily:'Arial, sans-serif',textAlign:'right'}}>
      <h1>سيرة ذاتية اختبارية</h1>
      <h2>التعليم</h2>
      <div className="metadata-degree">
        <span>بكالوريوس تمريض</span><span> | </span><span>٢٠١٩</span>
      </div>
      <div className="metadata-institution">
        <span>كلية التمريض</span><span> | </span><span>جامعة الزقازيق</span>
      </div>
      <h2>اللغات ومعلومات إضافية</h2>
      <div className="metadata-languages">
        <span>اللغة العربية</span><span> | </span><span>اللغة الإنجليزية</span>
      </div>
      <h2>الملخص المهني</h2>
      <p>خبرة مهنية في خدمة المرضى وتنسيق المهام وتطوير الجودة وسلامة الرعاية.</p>
      <h2>English control</h2>
      <div dir="ltr" className="metadata-english" style={{textAlign:'left'}}>
        <span>Example Organization</span><span> | </span><span>Your City</span>
      </div>
    </div>
  </main>;
}
""",encoding="utf-8")
print("PASS: synthetic PDF metadata QA page installed only for isolated CI")
