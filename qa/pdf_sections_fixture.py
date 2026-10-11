"""Local/CI synthetic fixture: real CvPreview and shared exporter; never customer data."""
import os
import sys
from pathlib import Path
p=Path(sys.argv[1])/'app/qa-pdf-sections/page.tsx'
if os.environ.get('SIRATI_PDF_QA_FIXTURE') != '1':
    p.unlink(missing_ok=True)
    raise SystemExit(0)
p.parent.mkdir(parents=True,exist_ok=True)
p.write_text(''' 'use client';
import { useRef, useState } from 'react';
import CvPreview from '@/components/CvPreview';
import { downloadCvSheet } from '@/lib/siratiPdfExport';
import type { CvData, TemplateName, CvLanguage } from '@/lib/types';
export default function Fixture(){
const [template,setTemplate]=useState<TemplateName>('modern');
const [language,setLanguage]=useState<CvLanguage>('en');
const [offscreen,setOffscreen]=useState(false);
const [error,setError]=useState(''); const stage=useRef<HTMLDivElement>(null);
const ar=language==='ar';
const data:CvData={fullName:ar?'مرشح تجريبي':'Synthetic Candidate',title:ar?'مهندس برمجيات':'Software Engineer',email:'test@example.com',phone:'01000000000',location:'Cairo',linkedin:'https://example.com',photoDataUrl:'',
profile:ar?'ملخص مهني للاختبار':'SummaryMarker professional summary',skills:ar?'مهارات البرمجة':'SkillsMarker programming',languages:ar?'اللغة العربية':'LanguagesMarker English',
experience:[{id:'1',role:ar?'خبرة عملية':'ExperienceMarker',company:'CompanyMarker',location:'Cairo',period:'2022',details:ar?'تطوير التطبيقات':'ExperienceDetailsMarker'}],
education:[{id:'2',degree:ar?'درجة جامعية':'EducationMarker',school:'SchoolMarker',location:'Cairo',period:'2020',details:ar?'دراسة جامعية':'EducationDetailsMarker'}],
certifications:[{id:'3',name:ar?'شهادة مهنية':'CertificationMarker',issuer:'IssuerMarker',date:'2025'}],
courses:[{id:'4',name:ar?'دورة تدريبية':'CourseMarker',provider:'ProviderMarker',date:'2024'}],
projects:[{id:'5',name:ar?'مشروع تطبيقي':'ProjectMarker',organization:'OrganizationMarker',period:'2023',details:ar?'تفاصيل المشروع':'ProjectDetailsMarker'}]};
return <main><select aria-label="Template" value={template} onChange={e=>setTemplate(e.target.value as TemplateName)}>{['modern','classic','compact','compact-ats','healthcare-pro','executive-ats','profile-sidebar','gold-sidebar','executive-letterhead'].map(t=><option key={t}>{t}</option>)}</select>
<select aria-label="Language" value={language} onChange={e=>setLanguage(e.target.value as CvLanguage)}><option>en</option><option>ar</option></select>
<label><input type="checkbox" checked={offscreen} onChange={e=>setOffscreen(e.target.checked)}/>Documents rendering</label>
<button onClick={async()=>{setError('');try{await downloadCvSheet(stage.current!.querySelector<HTMLElement>('.cv-sheet')!,'sections');}catch(e){setError(String(e));}}}>Download fixture</button><p role="alert">{error}</p>
<div className={offscreen?'sirati-pdf-offscreen':'wizard-preview-wrap'} aria-hidden={offscreen||undefined} ref={stage}><div className="preview-stage"><CvPreview data={data} template={template} language={language} watermarked={false}/></div></div></main>;
}''')
