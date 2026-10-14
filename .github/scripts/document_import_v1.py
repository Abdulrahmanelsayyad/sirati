"""Add a standalone, local-only CV document review page after source reconstruction."""
from pathlib import Path
import sys
root = Path(sys.argv[1]).resolve()
page = root / "app" / "import-documents" / "page.tsx"
page.parent.mkdir(parents=True, exist_ok=True)
page.write_text(r"""'use client';
import { useState } from 'react';
type Fact = { type: string; value: string; source: string; accepted: boolean };
export default function DocumentImportPage() {
  const [facts, setFacts] = useState<Fact[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  async function handleFiles(files: FileList | null) {
    if (!files) return;
    setBusy(true);
    const next: Fact[] = [], warnings: string[] = [];
    for (const file of Array.from(files).slice(0, 10)) {
      if (file.size > 5_000_000) { warnings.push(file.name + ': exceeds 5 MB'); continue; }
      if (!/\\.(txt|md)$/i.test(file.name)) {
        warnings.push(file.name + ': PDF/image extraction is not available yet; no data was imported.');
        continue;
      }
      try {
        const text = (await file.text()).slice(0, 200_000);
        const lines = text.split(/\\r?\\n/).map(x => x.trim()).filter(Boolean);
        const email = /\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}\\b/gi;
        const edu = /bachelor|master|diploma|university|college|بكالوريوس|ماجستير|دبلوم|جامعة|كلية/i;
        for (const line of lines) {
          for (const match of line.match(email) || []) next.push({type:'Email',value:match,source:file.name,accepted:false});
          if (edu.test(line)) next.push({type:'Education (verify)',value:line.slice(0,180),source:file.name,accepted:false});
        }
      } catch { warnings.push(file.name + ': could not read file'); }
    }
    setFacts(next.filter((f,i,a)=>a.findIndex(x=>x.type===f.type&&x.value===f.value)===i));
    setErrors(warnings); setBusy(false);
  }
  const accepted = facts.filter(f=>f.accepted);
  return <main style={{maxWidth:760,margin:'40px auto',padding:24,fontFamily:'system-ui'}}>
    <h1>Import CV documents</h1>
    <p>Free, local-first document review. No files are uploaded or saved. Only approve facts that you have verified.</p>
    <label htmlFor="cv-files">Choose TXT or Markdown files (up to 10, 5 MB each)</label>
    <input id="cv-files" type="file" multiple accept=".txt,.md,text/plain,text/markdown" disabled={busy}
      onChange={e=>void handleFiles(e.target.files)} style={{display:'block',margin:'16px 0'}}/>
    {busy && <p>Reading files…</p>}
    {errors.map((e,i)=><p role="status" key={i}>{e}</p>)}
    <h2>Review extracted facts</h2>
    {facts.map((f,i)=><div key={i} style={{padding:12,border:'1px solid #ccc',marginBottom:8}}>
      <label><input type="checkbox" checked={f.accepted} onChange={e=>setFacts(old=>old.map((x,j)=>j===i?{...x,accepted:e.target.checked}:x))}/>
      {' '}<strong>{f.type}:</strong> {f.value}</label><small style={{display:'block'}}>Source: {f.source}</small>
    </div>)}
    <button disabled={!accepted.length} onClick={()=>navigator.clipboard?.writeText(accepted.map(f=>f.type+': '+f.value).join('\\n'))}>
      Copy approved facts
    </button>
    <p>Paste reviewed facts into the existing CV Builder. Automatic PDF/image extraction and field mapping are not implemented yet.</p>
    <a href="/sirati/builder/">Open CV Builder</a>
  </main>;
}
""", encoding="utf-8")
