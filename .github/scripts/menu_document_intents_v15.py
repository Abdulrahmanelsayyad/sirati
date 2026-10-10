"""#91/#92: connect real saved CVs to existing Smart CV and CV Quality.
Generated Next.js source is reconstructed in CI. UI-only, fail closed on drift.
"""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
menu_path = root / 'components/SiratiSiteMenu.tsx'
docs_path = root / 'app/documents/page.tsx'
summary_path = root / 'components/PersonalSummaryPicker.tsx'
quality_path = root / 'components/CvReadinessCheck.tsx'
css_path = root / 'app/globals.css'

def once(source, needle, replacement, label):
    n = source.count(needle)
    if n != 1:
        raise RuntimeError(f'#91/#92 {label}: expected 1 occurrence; got {n}')
    return source.replace(needle, replacement, 1)

menu = menu_path.read_text(encoding='utf-8')
menu = once(menu,
    "{ title: 'مساعد الكتابة الذكي', detail: 'Smart CV — inside the builder', route: '/auth?next=/templates', icon: '✦' },",
    "{ title: 'مساعد الكتابة الذكي', detail: 'اختيار CV محفوظ ثم Smart CV', route: '/documents?tool=smart', icon: '✦' },",
    'Smart CV destination')
menu = once(menu,
    "{ title: 'مراجعة جودة السيرة', detail: 'CV Quality — inside the builder', route: '/auth?next=/templates', icon: '◉' },",
    "{ title: 'مراجعة جودة السيرة', detail: 'اختيار CV محفوظ ثم فحص الجودة', route: '/documents?tool=quality', icon: '◉' },",
    'Quality destination')
menu_path.write_text(menu, encoding='utf-8')

docs = docs_path.read_text(encoding='utf-8')
# Existing unauthenticated redirect, retain desired route (do not redirect into templates).
docs = once(docs,
    "window.location.href = withBasePath('/auth');",
    "window.location.href = withBasePath('/auth?next=' + encodeURIComponent('/documents' + window.location.search));",
    'auth return to document action')
import_line = "import SiratiDocumentIntent from '@/components/SiratiDocumentIntent';\n"
if import_line in docs:
    raise RuntimeError('#91/#92: intent component already imported')
first_import = re.search(r'^import ', docs, re.MULTILINE)
if not first_import: raise RuntimeError('#91/#92: docs import anchor missing')
docs = docs[:first_import.start()] + import_line + docs[first_import.start():]
# The intent chooser only appears on the signed-in document workspace, where
# documents were already loaded by the existing RLS-constrained Supabase query.
target = '<div className="document-grid">'
docs = once(docs,target,'<SiratiDocumentIntent documents={documents} />\n        '+target,'signed-in document grid')
docs_path.write_text(docs, encoding='utf-8')

component = root / 'components/SiratiDocumentIntent.tsx'
if component.exists(): raise RuntimeError('#91/#92 component already exists')
component.write_text(r"""'use client';

import { useEffect, useState } from 'react';
import { withBasePath } from '@/lib/basePath';

type SavedCv = { id: string; title?: string | null; template?: string | null; language?: string | null };
type Intent = 'smart' | 'quality' | null;

export default function SiratiDocumentIntent({ documents }: { documents: SavedCv[] }) {
  const [intent, setIntent] = useState<Intent>(null);
  useEffect(() => {
    // Never reflect an arbitrary query into page markup or a fetch.
    const tool = new URLSearchParams(window.location.search).get('tool');
    setIntent(tool === 'smart' || tool === 'quality' ? tool : null);
  }, []);
  if (!intent) return null;
  const isSmart = intent === 'smart';
  const title = isSmart ? 'مساعد الكتابة الذكي · Smart CV' : 'مراجعة جودة السيرة · CV Quality';
  const subtitle = isSmart
    ? 'اختر سيرة ذاتية محفوظة لفتح اقتراحات الملخص المهني داخل المحرر.'
    : 'اختر سيرة محفوظة لفتح تقرير الجودة داخل المحرر.';
  const destination = (doc: SavedCv) => withBasePath(
    '/builder?doc=' + encodeURIComponent(doc.id) + '&focus=' + (isSmart ? 'smart' : 'quality')
  );
  return (
    <section className="sirati-document-intent no-print" aria-label={title} dir="rtl"
      data-testid="sirati-document-intent">
      <div className="sirati-document-intent-head">
        <div><h2>{title}</h2><p>{subtitle}</p></div>
        <a href={withBasePath('/documents')}>عرض جميع مستنداتي · My Documents</a>
      </div>
      {documents.length ? (
        <div className="sirati-document-intent-list">
          {documents.map((doc) => (
            <article key={doc.id} className="sirati-document-intent-row">
              <div><strong dir="auto">{doc.title?.trim() || 'Untitled CV'}</strong>
                <small>{doc.language === 'ar' ? 'العربية' : 'English'}</small></div>
              <a className="btn btn-primary" href={destination(doc)}>
                {isSmart ? 'فتح Smart CV' : 'مراجعة الجودة'} <span aria-hidden="true">←</span>
              </a>
            </article>
          ))}
        </div>
      ) : (
        <div className="sirati-document-intent-empty">
          <p>ليس لديك سيرة ذاتية محفوظة بعد. ابدأ بإنشاء سيرة ثم احفظها في مستنداتي.</p>
          <a className="btn btn-primary" href={withBasePath('/templates')}>إنشاء CV · Create CV</a>
        </div>
      )}
    </section>
  );
}
""", encoding='utf-8')

quality = quality_path.read_text(encoding='utf-8')
quality = once(quality,
    "import { useMemo, useState } from 'react';",
    "import { useEffect, useMemo, useState } from 'react';",
    'quality effect import')
quality = once(quality,
    "  const [open, setOpen] = useState(false);",
    """  const [open, setOpen] = useState(false);
  useEffect(() => {
    if (typeof window === 'undefined') return;
    if (new URLSearchParams(window.location.search).get('focus') !== 'quality') return;
    setOpen(true);
    const frame = window.requestAnimationFrame(() => {
      document.querySelector('.wizard-preview-wrap .cv-readiness')?.scrollIntoView({
        behavior: 'smooth', block: 'start'
      });
    });
    return () => window.cancelAnimationFrame(frame);
  }, []);""",
    'Quality open on explicit focus')
quality_path.write_text(quality, encoding='utf-8')

summary = summary_path.read_text(encoding='utf-8')
summary = once(summary,
    "export default function PersonalSummaryPicker() {",
    """export default function PersonalSummaryPicker() {
  // Only a deliberate per-document Smart CV link activates this navigation.
  // Preserve all current opt-in suggestions for normal Builder users.
  useEffect(() => {
    if (!window.location.pathname.includes('/builder') ||
        new URLSearchParams(window.location.search).get('focus') !== 'smart') return;
    let moved = false;
    let ticks = 0;
    const timer = window.setInterval(() => {
      ticks++;
      if (!moved) {
        const steps = document.querySelectorAll<HTMLButtonElement>('.cv-substep');
        if (steps.length >= 2) { steps[1].click(); moved = true; }
      }
      const trigger = document.querySelector<HTMLButtonElement>(
        '.wizard-section-card .sirati-summary-trigger'
      );
      if (moved && trigger && !document.querySelector('.wizard-section-card .sirati-summary-panel')) {
        trigger.click();
      }
      if (document.querySelector('.wizard-section-card .sirati-summary-panel') || ticks >= 50) {
        window.clearInterval(timer);
        if (trigger) trigger.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 250);
    return () => window.clearInterval(timer);
  }, []);""",
    'Smart CV one-time wizard focus')
summary_path.write_text(summary, encoding='utf-8')

css = css_path.read_text(encoding='utf-8')
if '/* Sirati #91/#92 saved document intents */' in css:
    raise RuntimeError('#91/#92 CSS already exists')
css += r"""
/* Sirati #91/#92 saved document intents (existing private Documents view only). */
@media screen {
  .sirati-document-intent { padding: 20px; margin: 16px auto 24px; border: 1px solid #d7e5da;
    border-radius: 18px; background: #f8fbf8; color: #184237; }
  .sirati-document-intent-head { display: flex; flex-wrap: wrap; gap: 10px;
    align-items: start; justify-content: space-between; margin-bottom: 16px; }
  .sirati-document-intent-head h2 { font-size: clamp(20px, 3vw, 27px); margin: 0 0 6px; }
  .sirati-document-intent-head p { color: #52675a; margin: 0; line-height: 1.6; }
  .sirati-document-intent-head > a { padding: 8px; min-height: 44px; }
  .sirati-document-intent-list { display: grid; gap: 10px; }
  .sirati-document-intent-row { display: flex; gap: 12px; flex-wrap: wrap;
    align-items: center; justify-content: space-between; background: white;
    padding: 14px; border-radius: 12px; border: 1px solid #dce8dd; }
  .sirati-document-intent-row > div { display: grid; gap: 5px; min-width: 0; }
  .sirati-document-intent-row strong { overflow-wrap: anywhere; }
  .sirati-document-intent-row small { color: #65796c; }
  .sirati-document-intent-row a { min-height: 44px; text-align: center; }
  .sirati-document-intent-empty { display: grid; gap: 12px; justify-items: start; }
}
@media screen and (max-width: 390px) {
  .sirati-document-intent { padding: 14px; }
  .sirati-document-intent-row > a { width: 100%; }
}
"""
css_path.write_text(css, encoding='utf-8')
print('PASS: dedicated Smart CV / Quality document selection and focused Builder paths.')
