"""Generate a local-only document facts review route from shared extraction code."""
from pathlib import Path
import shutil
import sys

root = Path(sys.argv[1]).resolve()
repo = Path(__file__).resolve().parents[2]
target = root / "lib"
target.mkdir(parents=True, exist_ok=True)
for name in ("documentCvExtraction.ts", "documentCvFileImport.ts"):
    source = repo / "lib" / name
    dest = target / name
    if dest.exists() and dest.read_bytes() != source.read_bytes():
        raise RuntimeError(f"Refusing to overwrite existing generated library: {name}")
    shutil.copyfile(source, dest)

page = root / "app" / "import-documents" / "page.tsx"
page.parent.mkdir(parents=True, exist_ok=True)
page.write_text(r"""'use client';
import { useMemo, useState } from 'react';
import { importTextDocuments } from '@/lib/documentCvFileImport';
import type { ExtractedCvFact } from '@/lib/documentCvExtraction';

type ReviewFact = ExtractedCvFact & { accepted: boolean };
const labels: Record<ExtractedCvFact['field'], string> = {
  email: 'Email / البريد الإلكتروني',
  phone: 'Phone / الهاتف',
  education: 'Education / التعليم',
  date: 'Date / التاريخ',
  url: 'Website / رابط',
};

export default function DocumentImportPage() {
  const [facts, setFacts] = useState<ReviewFact[]>([]);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [copyNotice, setCopyNotice] = useState('');
  const approved = useMemo(() => facts.filter(f => f.accepted), [facts]);
  const approvedText = useMemo(() => approved.map(f => labels[f.field] + ': ' + f.value).join('\n'), [approved]);

  async function handleFiles(files: FileList | null) {
    if (!files) return;
    setBusy(true);
    setFacts([]);
    setCopyNotice('');
    setWarnings([]);
    try {
      const selected = Array.from(files).slice(0, 10);
      const results = await importTextDocuments(selected);
      const notices = results.flatMap(result => result.warning ? [result.fileName + ': ' + result.warning] : []);
      if (files.length > 10) notices.unshift('Only the first 10 files were reviewed. / تمت مراجعة أول 10 ملفات فقط.');
      const extracted = results.flatMap(result => result.facts.map(f => ({ ...f, accepted: false })));
      setFacts(extracted);
      if (!extracted.length) notices.push('No supported facts found. / لم يتم العثور على بيانات قابلة للاستخراج.');
      setWarnings(notices);
    } catch {
      setWarnings(['Files could not be processed locally. / تعذرت قراءة الملفات محليًا.']);
    } finally {
      setBusy(false);
    }
  }

  async function copyFacts() {
    if (!approvedText) return;
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(approvedText);
      setCopyNotice('Approved facts copied. / تم نسخ البيانات المعتمدة.');
    } catch {
      setCopyNotice('Select and copy the approved text below manually. / انسخ النص أدناه يدويًا.');
    }
  }

  return <main style={{ maxWidth: 780, margin: '40px auto', padding: 24, fontFamily: 'system-ui', lineHeight: 1.6 }}>
    <h1>Import CV documents / استيراد مستندات السيرة الذاتية</h1>
    <p>Private, local-first review. Files stay in this browser session and are not uploaded.
      Check each fact before using it. / تتم مراجعة الملفات محليًا، ويجب التأكد من كل معلومة.</p>
    <label htmlFor="cv-files">TXT or Markdown only / ملفات نصية فقط (10 max, 5 MB each)</label>
    <input id="cv-files" type="file" multiple accept=".txt,.md,text/plain,text/markdown"
      disabled={busy} onChange={e => void handleFiles(e.target.files)}
      style={{ display: 'block', margin: '12px 0 20px', maxWidth: '100%' }} />
    {busy && <p role="status">Reading locally… / جارٍ القراءة محليًا…</p>}
    {warnings.map((warning, i) => <p role="status" key={i}>{warning}</p>)}
    <h2>Review extracted facts / راجع البيانات المستخرجة</h2>
    {facts.map((fact, i) => <div key={i} style={{ padding: 12, border: '1px solid #ccc', borderRadius: 8, marginBottom: 8 }}>
      <label style={{ display: 'flex', gap: 10, alignItems: 'flex-start', cursor: 'pointer' }}>
        <input type="checkbox" checked={fact.accepted} disabled={busy}
          onChange={e => setFacts(old => old.map((f, j) => j === i ? { ...f, accepted: e.target.checked } : f))}
          style={{ marginTop: 7 }} />
        <span><strong>{labels[fact.field]}</strong>: <span dir="auto">{fact.value}</span></span>
      </label>
      <small style={{ display: 'block', marginTop: 6 }} dir="auto">Source / المصدر: {fact.evidence.fileName}</small>
      <small style={{ display: 'block', overflowWrap: 'anywhere' }} dir="auto">Evidence / الدليل: {fact.evidence.snippet}</small>
    </div>)}
    <h2>Approved facts / البيانات المعتمدة ({approved.length})</h2>
    <button type="button" disabled={!approved.length || busy} onClick={() => void copyFacts()}
      style={{ minHeight: 44, padding: '8px 18px', cursor: approved.length ? 'pointer' : 'not-allowed' }}>
      Copy reviewed facts / نسخ البيانات المعتمدة
    </button>
    {copyNotice && <p role="status">{copyNotice}</p>}
    {approved.length > 0 && <textarea readOnly aria-label="Approved CV facts" dir="auto"
      value={approvedText} rows={Math.min(12, Math.max(3, approved.length * 2))}
      style={{ display: 'block', width: '100%', boxSizing: 'border-box', marginTop: 14, padding: 10 }} />}
    <p>Paste approved facts into the Builder. Automatic field population and PDF/DOCX/image import are
      not yet supported. / الإضافة التلقائية للحقول واستيراد PDF وWord والصور غير متاحين بعد.</p>
    <a href="/sirati/builder/">Open CV Builder / فتح محرر السيرة الذاتية</a>
  </main>;
}
""", encoding="utf-8")
