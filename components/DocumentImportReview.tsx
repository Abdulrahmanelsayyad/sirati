'use client';
import { useMemo, useRef, useState } from 'react';
import { importTextDocuments } from '@/lib/documentCvFileImport';
import type { ExtractedCvFact } from '@/lib/documentCvExtraction';
import type { CvData } from '@/lib/types';

type ReviewFact = ExtractedCvFact & { accepted: boolean };
const labels = { name: ['Name','الاسم'], title: ['Job title','المسمى الوظيفي'], experience: ['Experience notes','ملاحظات الخبرة'], certification: ['Certification','الشهادة'], email: ['Email','البريد الإلكتروني'], phone: ['Phone','الهاتف'], education: ['Education','التعليم'], date: ['Date (review only)','التاريخ (للمراجعة فقط)'], url: ['Website (review only)','الرابط (للمراجعة فقط)'] };

// Never replace populated fields, infer date associations, or change unrelated CV content.
export function applyReviewedFacts(data: CvData, facts: readonly ExtractedCvFact[]): CvData {
  const next = { ...data, education: [...data.education], experience: [...data.experience], certifications: [...data.certifications] };
  for (const fact of facts) {
    const value = fact.value.trim();
    if (!value) continue;
    if (fact.field === 'name' && !next.fullName.trim()) next.fullName = value;
    if (fact.field === 'title' && !next.title.trim()) next.title = value;
    if (fact.field === 'experience' && !next.experience.some(e => e.details.trim().toLocaleLowerCase() === value.toLocaleLowerCase()))
      next.experience.push({ id: crypto.randomUUID(), role: '', company: '', location: '', period: '', details: value });
    if (fact.field === 'certification' && !next.certifications.some(e => e.name.trim().toLocaleLowerCase() === value.toLocaleLowerCase()))
      next.certifications.push({ id: crypto.randomUUID(), name: value, issuer: '', date: '' });
    if (fact.field === 'email' && !next.email.trim()) next.email = value;
    if (fact.field === 'phone' && !next.phone.trim()) next.phone = value;
    if (fact.field === 'education' && !next.education.some(e => [e.degree,e.school,e.details].some(v => v.trim().toLocaleLowerCase() === value.toLocaleLowerCase()))) {
      next.education.push({ id: crypto.randomUUID(), degree: '', school: '', location: '', period: '', details: value });
    }
  }
  return next;
}

export default function DocumentImportReview({ language = 'en', onApply }: {
  language?: 'en' | 'ar'; onApply?: (facts: ExtractedCvFact[]) => void;
}) {
  const [lang, setLang] = useState(language);
  const [facts, setFacts] = useState<ReviewFact[]>([]);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');
  const run = useRef(0);
  const ar = lang === 'ar';
  const t = (en: string, arabic: string) => ar ? arabic : en;
  const approved = useMemo(() => facts.filter(f => f.accepted && f.value.trim()), [facts]);
  const approvedText = approved.map(f => labels[f.field][ar ? 1 : 0] + ': ' + f.value).join('\n');
  const usable = approved.filter(f => ['email','phone','education','name','title','experience','certification'].includes(f.field));
  async function handleFiles(files: FileList | null) {
    if (!files?.length) return;
    const request = ++run.current;
    setBusy(true); setFacts([]); setWarnings([]); setNotice('');
    try {
      const results = await importTextDocuments(Array.from(files));
      if (request !== run.current) return;
      const extracted = results.flatMap(result => result.facts.map(f => ({ ...f, accepted: false })));
      setFacts(extracted);
      const notices = results.flatMap(result => result.warning ? [result.fileName + ': ' + result.warning] : []);
      if (files.length > 10) notices.unshift(t('Only the first 10 files were reviewed.','تمت مراجعة أول 10 ملفات فقط.'));
      if (!extracted.length) notices.push(t('No supported facts found. Enter missing information manually.','لم يتم العثور على بيانات مدعومة. أدخل المعلومات الناقصة يدويًا.'));
      setWarnings(notices);
    } catch { if (request === run.current) setWarnings([t('Could not read these files locally.','تعذرت قراءة الملفات محليًا.')]); }
    finally { if (request === run.current) setBusy(false); }
  }
  async function copyFacts() {
    try { await navigator.clipboard.writeText(approvedText); setNotice(t('Approved facts copied.','تم نسخ البيانات المعتمدة.')); }
    catch { setNotice(t('Select and copy the approved text below manually.','انسخ النص المعتمد أدناه يدويًا.')); }
  }
  return <section dir={ar ? 'rtl' : 'ltr'} style={{maxWidth:780,padding:16,lineHeight:1.6,overflowWrap:'anywhere'}}>
    <button type="button" onClick={() => setLang(ar ? 'en' : 'ar')} style={{minHeight:44}}>{ar ? 'English' : 'العربية'}</button>
    <h1>{t('Import CV documents','استيراد مستندات السيرة الذاتية')}</h1>
    <p>{t('Files are read in this browser, without uploads or paid services. Review and edit each fact before approving it.','تُقرأ الملفات محليًا دون رفعها أو استخدام خدمات مدفوعة. راجع وعدّل كل معلومة قبل اعتمادها.')}</p>
    <p>{t('Text PDF, TXT or Markdown: up to 10 files, 5 MB each, 30 PDF pages. Images and scanned pages need OCR and are not supported yet. Reading order and extraction may be imperfect.','PDF نصي أو TXT أو Markdown: حتى 10 ملفات، 5 ميجابايت للملف و30 صفحة PDF. الصور والصفحات الممسوحة ضوئيًا غير مدعومة بعد. قد تحتاج البيانات وترتيبها إلى تصحيح.')}</p>
    <label>{t('Choose documents','اختر المستندات')}<input aria-label="CV documents" type="file" multiple accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown" disabled={busy}
      onChange={e => { void handleFiles(e.target.files); e.target.value = ''; }} style={{display:'block',maxWidth:'100%',margin:'12px 0'}} /></label>
    <button type="button" onClick={() => { run.current++; setFacts([]);setWarnings([]);setNotice('');setBusy(false); }}>{t('Clear imported data','مسح البيانات المستوردة')}</button>
    {busy && <p role="status">{t('Reading locally…','جارٍ القراءة محليًا…')}</p>}
    {warnings.map((warning,i) => <p role="status" key={i}>{warning}</p>)}
    {facts.map((fact,i) => <div key={i} style={{padding:12,border:'1px solid #ccc',borderRadius:8,marginTop:8}}>
      <label><input type="checkbox" aria-label={`Approve fact ${i+1}`} checked={fact.accepted} disabled={busy || !fact.value.trim()}
        onChange={e => { const checked=e.target.checked;setNotice('');setFacts(old=>old.map((f,j)=>j===i?{...f,accepted:checked}:f)); }} /> {labels[fact.field][ar?1:0]}</label>
      <input aria-label={`Edit fact ${i+1}`} dir="auto" value={fact.value} maxLength={500} style={{display:'block',width:'100%',boxSizing:'border-box'}}
        onChange={e=>{const value=e.target.value;setNotice('');setFacts(old=>old.map((f,j)=>j===i?{...f,value,accepted:false}:f));}} />
      <small style={{display:'block'}} dir="auto">{t('Source: ','المصدر: ')}{fact.evidence.fileName}</small>
      <small dir="auto">{t('Evidence: ','الدليل: ')}{fact.evidence.snippet}</small>
    </div>)}
    <h2>{t('Approved facts','البيانات المعتمدة')} ({approved.length})</h2>
    <button type="button" disabled={!approved.length || busy} onClick={() => void copyFacts()} style={{minHeight:44}}>{t('Copy reviewed facts','نسخ البيانات المعتمدة')}</button>
    {onApply && <><p>{t('Add fills empty contact/name/title fields and appends education, experience notes and certifications. Explicitly labeled facts are recognized; missing details stay blank. Existing text is preserved. Dates and websites are review-only; place them manually. Check the Education section to organize degree and school.','تُضاف البيانات إلى حقول الاسم والمسمى والتواصل الفارغة، وإلى التعليم والخبرة والشهادات دون استبدال بياناتك. تُقرأ المعلومات المعلّمة بوضوح فقط وتظل التفاصيل الناقصة فارغة. ضع التواريخ والروابط يدويًا، ونظّم المؤهل والجامعة في قسم التعليم.')}</p>
      <button type="button" disabled={!usable.length || busy} style={{minHeight:44}} onClick={()=>{onApply(usable);setFacts(old=>old.map(f=>({...f,accepted:false})));setNotice(t('Reviewed facts applied where fields were empty; reviewed entries added. Check your CV before saving.','أُضيفت البيانات إلى الحقول الفارغة وملاحظات التعليم. راجع سيرتك قبل الحفظ.'));}}>{t('Add approved facts to CV','إضافة البيانات المعتمدة للسيرة')}</button></>}
    {notice && <p role="status">{notice}</p>}
    {approved.length > 0 && <textarea readOnly aria-label="Approved CV facts" dir="auto" value={approvedText} rows={5} style={{display:'block',width:'100%',boxSizing:'border-box',marginTop:12}} />}
  </section>;
}
