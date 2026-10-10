"""#93: direct, client-side PDF generation from the actual CV preview.
No print dialog, no payment, no file uploads; requires independent A4/RTL/ATS QA.
"""
from pathlib import Path
import json
import re
import sys

root = Path(sys.argv[1]).resolve()
menu_path = root / 'components/SiratiSiteMenu.tsx'
docs_path = root / 'app/documents/page.tsx'
intents_path = root / 'components/SiratiDocumentIntent.tsx'
builder_path = root / 'app/builder/page.tsx'
package_path = root / 'package.json'
css_path = root / 'app/globals.css'

def once(text, old, new, name):
    hits = text.count(old)
    if hits != 1: raise RuntimeError(f'Direct PDF {name}: expected 1 occurrence; got {hits}')
    return text.replace(old,new,1)

menu = menu_path.read_text(encoding='utf-8')
menu = once(menu,
    "{ title: 'طباعة السيرة PDF', detail: 'Free export — inside the builder', route: '/auth?next=/templates', icon: '⇩' },",
    "{ title: 'تنزيل السيرة PDF', detail: 'Download PDF · ملف على جهازك', route: '/documents?tool=pdf', icon: '⇩' },",
    'menu route')
menu_path.write_text(menu,encoding='utf-8')

intents = intents_path.read_text(encoding='utf-8')
intents = once(intents,
    "import { withBasePath } from '@/lib/basePath';",
    "import { withBasePath } from '@/lib/basePath';\nimport SiratiPdfDownload from '@/components/SiratiPdfDownload';",
    'intent import')
intents = once(intents,
    "type Intent = 'smart' | 'quality' | null;",
    "type Intent = 'smart' | 'quality' | 'pdf' | null;",
    'PDF intent type')
intents = once(intents,
    "tool === 'smart' || tool === 'quality' ? tool : null",
    "tool === 'smart' || tool === 'quality' || tool === 'pdf' ? tool : null",
    'PDF intent allowlist')
intents = once(intents,
    "const title = isSmart ? 'مساعد الكتابة الذكي · Smart CV' : 'مراجعة جودة السيرة · CV Quality';",
    "const title = isSmart ? 'مساعد الكتابة الذكي · Smart CV' : intent === 'quality' ? 'مراجعة جودة السيرة · CV Quality' : 'تنزيل السيرة PDF · Download PDF';",
    'PDF intent title')
intents = once(intents,
    """: 'اختر سيرة محفوظة لفتح تقرير الجودة داخل المحرر.';""",
    """: intent === 'quality' ? 'اختر سيرة محفوظة لفتح تقرير الجودة داخل المحرر.' : 'اختر السيرة المراد تنزيلها مباشرة كملف PDF دون فتح نافذة الطباعة.';""",
    'PDF intent summary')
intents = once(intents,
    """              <a className="btn btn-primary" href={destination(doc)}>
                {isSmart ? 'فتح Smart CV' : 'مراجعة الجودة'} <span aria-hidden="true">←</span>
              </a>""",
    """              {intent === 'pdf'
                ? <SiratiPdfDownload documentId={doc.id} title={doc.title || 'Sirati CV'} />
                : <a className="btn btn-primary" href={destination(doc)}>
                    {isSmart ? 'فتح Smart CV' : 'مراجعة الجودة'} <span aria-hidden="true">←</span>
                  </a>}""",
    'PDF in chooser')
intents_path.write_text(intents,encoding='utf-8')

docs = docs_path.read_text(encoding='utf-8')
docs = once(docs,
    "import SiratiDocumentIntent from '@/components/SiratiDocumentIntent';",
    "import SiratiDocumentIntent from '@/components/SiratiDocumentIntent';\nimport SiratiPdfDownload from '@/components/SiratiPdfDownload';",
    'documents import')
anchor = "onClick={() => removeDocument(doc.id)}"
if docs.count(anchor) != 1: raise RuntimeError(f'Direct PDF: unexpected delete buttons ({docs.count(anchor)})')
at = docs.index(anchor)
start = docs.rfind('<button', 0, at)
end = docs.find('</button>',at)
if start < 0 or end < 0 or at-start>300 or end-at>400:
    raise RuntimeError('Direct PDF: original delete button structure changed')
# Add a direct PDF download control in the same existing card action row; do
# not alter the account-owned open/edit/delete behavior or user session.
docs = docs[:start] + '<SiratiPdfDownload documentId={doc.id} title={doc.title || "Sirati CV"} />\n              ' + docs[start:]
docs_path.write_text(docs,encoding='utf-8')

library = root / 'lib/siratiPdfExport.ts'
if library.exists(): raise RuntimeError('Direct PDF library already present')
library.write_text(r"""'use client';

import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';

/**
 * Capture the existing CV preview (not app chrome) as a PDF file.
 * Note: visually faithful raster PDF, NOT searchable text/ATS-certified.
 * QA must verify Arabic and pagination before release.
 */
export async function downloadCvSheet(sheet: HTMLElement, name: string): Promise<void> {
  await document.fonts.ready;
  const bounds = sheet.getBoundingClientRect();
  if (bounds.width < 200 || sheet.scrollHeight < 100) {
    throw new Error('CV preview is not ready yet.');
  }
  const canvas = await html2canvas(sheet, {
    backgroundColor: '#ffffff',
    scale: 2,
    useCORS: true,
    allowTaint: false,
    logging: false,
    scrollX: 0,
    scrollY: -window.scrollY,
    windowWidth: Math.max(window.innerWidth, Math.ceil(bounds.width)),
  });
  if (!canvas.width || !canvas.height) throw new Error('Could not render the CV.');
  const pdf = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4', compress: true });
  const pageHeight = Math.floor(canvas.width * 297 / 210);
  if (pageHeight <= 0) throw new Error('Invalid rendered page size.');
  let pageNo = 0;
  for (let top = 0; top < canvas.height; top += pageHeight) {
    const actualHeight = Math.min(pageHeight, canvas.height - top);
    const pageCanvas = document.createElement('canvas');
    pageCanvas.width = canvas.width;
    pageCanvas.height = actualHeight;
    const ctx = pageCanvas.getContext('2d');
    if (!ctx) throw new Error('Could not render PDF page.');
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, pageCanvas.width, pageCanvas.height);
    ctx.drawImage(canvas, 0, top, canvas.width, actualHeight,
      0, 0, canvas.width, actualHeight);
    if (pageNo) pdf.addPage('a4', 'portrait');
    pdf.addImage(pageCanvas.toDataURL('image/png'), 'PNG',
      0, 0, 210, actualHeight * 210 / canvas.width, undefined, 'FAST');
    pageCanvas.width = 0; pageCanvas.height = 0;
    pageNo++;
  }
  if (!pageNo) throw new Error('CV PDF is empty.');
  const blob = pdf.output('blob');
  if (!blob || blob.size < 800 || blob.type !== 'application/pdf')
    throw new Error('Generated PDF is invalid.');
  const safeName = (name || 'Sirati-CV').replace(/[^\p{L}\p{N}_. -]/gu, '').trim().slice(0,80) || 'Sirati-CV';
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = safeName + '.pdf';
  link.style.display = 'none';
  document.body.appendChild(link);
  try { link.click(); }
  finally {
    link.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 20000);
  }
}
""",encoding='utf-8')

widget = root / 'components/SiratiPdfDownload.tsx'
if widget.exists(): raise RuntimeError('Direct PDF component already present')
widget.write_text(r"""'use client';

import { useEffect, useRef, useState } from 'react';
import { createClient } from '@/lib/supabase/client';
import type { CvData, CvLanguage, TemplateName } from '@/lib/types';
import CvPreview from '@/components/CvPreview';
import { downloadCvSheet } from '@/lib/siratiPdfExport';

type Saved = { title?: string | null; data: unknown; template?: string | null;
               language?: string | null };
type Choice = { row: Saved; name: string };

export default function SiratiPdfDownload({ documentId, title }: {
  documentId: string; title: string;
}) {
  const [selected, setSelected] = useState<Choice | null>(null);
  const [busy, setBusy] = useState(false);
  const [errorText, setErrorText] = useState('');
  const stage = useRef<HTMLDivElement>(null);
  const request = useRef(false);

  async function begin() {
    if (request.current) return;
    request.current = true;
    setBusy(true); setErrorText('');
    try {
      const client = createClient();
      if (!client) throw new Error('Please sign in first.');
      const { data: auth, error: authError } = await client.auth.getUser();
      if (authError || !auth.user) throw new Error('Sign in required.');
      // Defense-in-depth: require both the selected ID and the current user.
      // Supabase row-level security remains the authoritative protection.
      const { data, error } = await client.from('cv_documents')
        .select('title,data,template,language')
        .eq('id',documentId).eq('user_id',auth.user.id).single();
      if (error || !data) throw new Error('Saved CV not available for this account.');
      if (!data.data || typeof data.data !== 'object')
        throw new Error('Saved CV content is missing.');
      setSelected({row: data as Saved, name: title || data.title || 'Sirati-CV'});
    } catch (e: unknown) {
      setErrorText(e instanceof Error ? e.message : 'Cannot prepare your PDF.');
      setBusy(false); request.current = false;
    }
  }
  useEffect(() => {
    if (!selected) return;
    let cancelled = false;
    (async () => {
      try {
        // Wait for React's CvPreview and its layout to be painted.
        await new Promise<void>(resolve =>
          requestAnimationFrame(() => requestAnimationFrame(() => resolve())));
        if (cancelled) return;
        const sheet = stage.current?.querySelector<HTMLElement>('.cv-sheet');
        if (!sheet) throw new Error('CV preview not available.');
        await downloadCvSheet(sheet, selected.name);
      } catch (e: unknown) {
        if (!cancelled) setErrorText(e instanceof Error ? e.message : 'PDF export failed.');
      } finally {
        if (!cancelled) { setSelected(null); setBusy(false); request.current = false; }
      }
    })();
    return () => { cancelled = true; };
  }, [selected]);
  return <>
    <span className="sirati-direct-pdf-action">
      <button type="button" className="btn btn-secondary" disabled={busy}
        onClick={begin} aria-label={'Download PDF · ' + title}>
        {busy ? 'Preparing PDF…' : 'Download PDF · تنزيل PDF'}
      </button>
      {errorText && <span className="sirati-pdf-error" role="alert">{errorText}</span>}
    </span>
    {selected && <div className="sirati-pdf-offscreen" ref={stage} aria-hidden="true">
      <CvPreview
        data={selected.row.data as CvData}
        template={(selected.row.template || 'modern') as TemplateName}
        language={(selected.row.language === 'ar' ? 'ar' : 'en') as CvLanguage}
        watermarked={false}
      />
    </div>}
  </>;
}
""",encoding='utf-8')

builderComponent = root / 'components/SiratiBuilderPdfButton.tsx'
builderComponent.write_text(r"""'use client';

import { useState } from 'react';
import { downloadCvSheet } from '@/lib/siratiPdfExport';

export default function SiratiBuilderPdfButton({ language }: {language: string}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  async function handle() {
    if (busy) return;
    setBusy(true); setError('');
    try {
      const sheet = document.querySelector<HTMLElement>(
        '.wizard-preview-wrap .preview-stage > .cv-sheet'
      );
      if (!sheet) throw new Error('CV preview is not available.');
      const name = sheet.querySelector('h1')?.textContent?.trim() || 'Sirati-CV';
      await downloadCvSheet(sheet,name);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'PDF export failed.');
    } finally { setBusy(false); }
  }
  return <span className="sirati-builder-pdf-action">
    <button type="button" className="btn btn-secondary btn-lg" disabled={busy}
      onClick={handle}>
      {busy ? (language === 'ar' ? 'جارٍ إعداد PDF…' : 'Preparing PDF…')
        : (language === 'ar' ? 'تنزيل PDF مجانًا' : 'Download free PDF')}
    </button>
    {error && <small role="alert" className="sirati-pdf-error">{error}</small>}
  </span>;
}
""",encoding='utf-8')

builder = builder_path.read_text(encoding='utf-8')
builder = once(builder,
    "import CvReadinessCheck from '@/components/CvReadinessCheck';",
    "import CvReadinessCheck from '@/components/CvReadinessCheck';\nimport SiratiBuilderPdfButton from '@/components/SiratiBuilderPdfButton';",
    'builder import')
button = """<button type="button" className="btn btn-secondary btn-lg" onClick={() => window.print()}>{language === 'ar' ? 'طباعة / حفظ PDF مجانًا' : 'Print / Save free PDF'}</button>"""
builder = once(builder,button,"<SiratiBuilderPdfButton language={language} />",'replace print CTA')
builder = builder.replace(
    "استخدم الطباعة ثم اختر حفظ كملف PDF من متصفحك، دون دفع أو طلب موافقة.",
    "نزّل ملف PDF مباشرة إلى جهازك دون طباعة أو دفع أو طلب موافقة.")
builder = builder.replace(
    "Use your browser print dialog and choose Save as PDF. No payment or approval required.",
    "Download your PDF file directly to your device. No print dialog, payment or approval required.")
builder_path.write_text(builder,encoding='utf-8')

pkg = json.loads(package_path.read_text(encoding='utf-8'))
dependencies = pkg.setdefault('dependencies', {})
dependencies.setdefault('html2canvas', '1.4.1')
dependencies.setdefault('jspdf', '2.5.2')
package_path.write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+"\n",encoding='utf-8')

css = css_path.read_text(encoding='utf-8')
if '/* Sirati #93 direct PDF export */' in css: raise RuntimeError('Direct PDF CSS already present')
css += r"""
/* Sirati #93 direct PDF export; only the existing CV sheet is captured. */
@media screen {
  .sirati-direct-pdf-action, .sirati-builder-pdf-action {
    display: inline-flex; flex-direction: column; gap: 6px; max-width: 100%; }
  .sirati-direct-pdf-action button, .sirati-builder-pdf-action button { min-height: 44px; }
  .sirati-pdf-error { color: #9a2f27; font-size: 12px; max-width: 36ch; overflow-wrap: anywhere; }
  .sirati-pdf-offscreen {
    position: fixed !important; top: 0 !important; left: -20000px !important;
    pointer-events: none; z-index: -200 !important;
    width: 210mm !important; background: #fff;
  }
  .sirati-pdf-offscreen .cv-sheet { width: 210mm !important; max-width: none !important;
    transform: none !important; margin: 0 !important; box-shadow: none !important; }
}
@media print { .sirati-pdf-offscreen, .sirati-direct-pdf-action,
 .sirati-builder-pdf-action { display: none !important; } }
"""
css_path.write_text(css,encoding='utf-8')
print('PASS: direct device PDF controls from Documents and Builder; no CV print dialog.')
