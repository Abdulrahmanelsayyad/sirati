from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
component = root / "components" / "DuplicateCvAction.tsx"
component.parent.mkdir(parents=True, exist_ok=True)

component.write_text(r''' 'use client';

import { createClient } from '@supabase/supabase-js';
import { useEffect, useMemo, useState } from 'react';

type Lang = 'en' | 'ar';
type CvDoc = { id: string; title: string | null; language: string | null; template: string | null; data: unknown };

function langNow(): Lang {
  const cv = document.querySelector<HTMLElement>('.cv-sheet');
  return cv?.getAttribute('dir') === 'rtl' || document.documentElement.getAttribute('dir') === 'rtl' ? 'ar' : 'en';
}

function nextBuilderUrl(id: string) {
  const marker = '/builder';
  const i = window.location.pathname.indexOf(marker);
  const base = i >= 0 ? window.location.pathname.slice(0, i) : '';
  return `${base}/builder/?doc=${encodeURIComponent(id)}`;
}

function cleanTitle(value: string) {
  return value.replace(/\s+/g, ' ').trim().slice(0, 120);
}

export default function DuplicateCvAction() {
  const [enabled, setEnabled] = useState(false);
  const [language, setLanguage] = useState<Lang>('en');
  const [open, setOpen] = useState(false);
  const [source, setSource] = useState<CvDoc | null>(null);
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [message, setMessage] = useState('');

  const supabase = useMemo(() => {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
    return url && key ? createClient(url, key) : null;
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const params = new URLSearchParams(window.location.search);
    setEnabled(window.location.pathname.includes('/builder') && Boolean(params.get('doc')) && Boolean(supabase));
    const scan = () => setLanguage(langNow());
    scan();
    const timer = window.setInterval(scan, 1000);
    return () => window.clearInterval(timer);
  }, [supabase]);

  useEffect(() => {
    if (!open) return;
    const previous = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && !creating) setOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => {
      document.body.style.overflow = previous;
      window.removeEventListener('keydown', onKey);
    };
  }, [open, creating]);

  if (!enabled || !supabase) return null;

  const c = language === 'ar' ? {
    trigger: 'إنشاء نسخة من CV',
    heading: 'أنشئ نسخة مستقلة',
    sub: 'استخدم نفس محتوى السيرة لوظيفة أخرى بدون تعديل النسخة الأصلية.',
    label: 'اسم النسخة الجديدة',
    placeholder: 'مثال: ممرض طوارئ - دبي',
    loading: 'جارٍ قراءة السيرة...',
    create: 'إنشاء النسخة',
    creating: 'جارٍ الإنشاء...',
    cancel: 'إلغاء',
    readError: 'تعذر قراءة هذه السيرة. تأكد من تسجيل الدخول وأن السيرة تخص حسابك.',
    createError: 'تعذر إنشاء النسخة. لم يتم تعديل السيرة الأصلية.',
    empty: 'اكتب اسمًا واضحًا للنسخة الجديدة.',
    safety: 'يتم نسخ بيانات السيرة والقالب واللغة فقط. لا يتم نسخ طلبات الدفع أو سجل الطلبات.',
  } : {
    trigger: 'Duplicate CV',
    heading: 'Create an independent CV copy',
    sub: 'Use this CV for another job without changing the original.',
    label: 'New CV name',
    placeholder: 'e.g. Emergency Nurse — Dubai',
    loading: 'Reading this CV...',
    create: 'Create copy',
    creating: 'Creating...',
    cancel: 'Cancel',
    readError: 'Could not read this CV. Make sure you are signed in and the CV belongs to your account.',
    createError: 'Could not create the copy. The original CV was not changed.',
    empty: 'Enter a clear name for the new CV.',
    safety: 'Only CV data, template and language are copied. Payment orders and order history are not copied.',
  };

  const begin = async () => {
    const id = new URLSearchParams(window.location.search).get('doc');
    if (!id) return;
    setOpen(true);
    setLoading(true);
    setMessage('');
    setSource(null);

    const { data: auth } = await supabase.auth.getUser();
    if (!auth.user) {
      setLoading(false);
      setMessage(c.readError);
      return;
    }

    const { data, error } = await supabase
      .from('cv_documents')
      .select('id,title,language,template,data')
      .eq('id', id)
      .eq('user_id', auth.user.id)
      .single();

    if (error || !data) {
      setLoading(false);
      setMessage(c.readError);
      return;
    }

    const doc = data as CvDoc;
    setSource(doc);
    const base = cleanTitle(doc.title || (language === 'ar' ? 'سيرتي' : 'My CV'));
    setTitle(cleanTitle(language === 'ar' ? `${base} - نسخة` : `${base} — Copy`));
    setLoading(false);
  };

  const duplicate = async () => {
    const newTitle = cleanTitle(title);
    if (!source || !newTitle) {
      setMessage(c.empty);
      return;
    }

    setCreating(true);
    setMessage('');

    try {
      const { data: auth } = await supabase.auth.getUser();
      if (!auth.user) {
        setMessage(c.createError);
        return;
      }

      const id = crypto.randomUUID();
      const { data, error } = await supabase
        .from('cv_documents')
        .insert({
          id,
          user_id: auth.user.id,
          title: newTitle,
          language: source.language || 'en',
          template: source.template || 'modern',
          data: source.data,
        })
        .select('id')
        .single();

      if (error || !data?.id) {
        setMessage(c.createError);
        return;
      }

      window.location.href = nextBuilderUrl(data.id);
    } catch {
      setMessage(c.createError);
    } finally {
      setCreating(false);
    }
  };

  return (
    <aside className="duplicate-cv" dir={language === 'ar' ? 'rtl' : 'ltr'} aria-label={c.trigger}>
      <button type="button" className="duplicate-cv__trigger" onClick={begin}>
        <span aria-hidden="true">⧉</span><span>{c.trigger}</span>
      </button>

      {open && (
        <div className="duplicate-cv__backdrop" onMouseDown={(e) => {
          if (e.currentTarget === e.target && !creating) setOpen(false);
        }}>
          <div className="duplicate-cv__dialog" role="dialog" aria-modal="true" aria-label={c.heading}>
            <header className="duplicate-cv__heading">
              <div><small>SIRATI MULTI-CV</small><h3>{c.heading}</h3><p>{c.sub}</p></div>
              <button type="button" className="duplicate-cv__close" onClick={() => setOpen(false)} disabled={creating} aria-label={c.cancel}>×</button>
            </header>

            {loading ? <p className="duplicate-cv__notice">{c.loading}</p> : (
              <>
                <label className="duplicate-cv__field">
                  <span>{c.label}</span>
                  <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder={c.placeholder} maxLength={120} disabled={!source || creating} />
                </label>
                <p className="duplicate-cv__notice">{c.safety}</p>
                {message && <p className="duplicate-cv__error" role="alert">{message}</p>}
                <div className="duplicate-cv__actions">
                  <button type="button" className="duplicate-cv__secondary" onClick={() => setOpen(false)} disabled={creating}>{c.cancel}</button>
                  <button type="button" className="duplicate-cv__primary" onClick={duplicate} disabled={!source || creating || !cleanTitle(title)}>
                    {creating ? c.creating : c.create}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </aside>
  );
}
'''.lstrip(), encoding="utf-8")

layout = root / "app" / "layout.tsx"
text = layout.read_text(encoding="utf-8")
imp = "import DuplicateCvAction from '@/components/DuplicateCvAction';\n"
if imp not in text:
    lines = text.splitlines(True)
    i = 0
    while i < len(lines) and (lines[i].startswith("import ") or not lines[i].strip()):
        i += 1
    lines.insert(i, imp)
    text = "".join(lines)
if "<DuplicateCvAction />" not in text:
    text = text.replace("</body>", "        <DuplicateCvAction />\n      </body>", 1)
layout.write_text(text, encoding="utf-8")

css_path = root / "app" / "globals.css"
css = css_path.read_text(encoding="utf-8")
if "/* Sirati duplicate CV */" not in css:
    css += r'''

/* Sirati duplicate CV */
.duplicate-cv { position: fixed; top: 142px; right: 16px; z-index: 120; font-size: 14px; }
[dir="rtl"].duplicate-cv { right: auto; left: 16px; }
.duplicate-cv__trigger { display: inline-flex; align-items: center; gap: 8px; min-height: 40px; padding: 7px 11px; border: 1px solid rgba(15,23,42,.12); border-radius: 999px; background: rgba(255,255,255,.97); box-shadow: 0 12px 30px rgba(15,23,42,.10); color: #0f172a; font: inherit; font-weight: 750; cursor: pointer; }
.duplicate-cv__trigger > span:first-child { display: grid; place-items: center; width: 26px; height: 26px; border-radius: 999px; background: #f1f5f9; font-size: 16px; }
.duplicate-cv__backdrop { position: fixed; inset: 0; z-index: 121; display: grid; place-items: center; padding: 18px; background: rgba(15,23,42,.38); backdrop-filter: blur(3px); }
.duplicate-cv__dialog { width: min(520px,100%); max-height: calc(100vh - 36px); overflow: auto; padding: 20px; border: 1px solid rgba(15,23,42,.10); border-radius: 20px; background: #fff; box-shadow: 0 28px 80px rgba(15,23,42,.26); }
.duplicate-cv__heading { display: grid; grid-template-columns: minmax(0,1fr) 40px; gap: 14px; align-items: start; }
.duplicate-cv__heading small { display: block; margin-bottom: 5px; color: #64748b; font-size: 10px; font-weight: 850; letter-spacing: .09em; }
.duplicate-cv__heading h3 { margin: 0; font-size: 24px; line-height: 1.2; }
.duplicate-cv__heading p { margin: 7px 0 0; color: #64748b; line-height: 1.5; }
.duplicate-cv__close { width: 40px; height: 40px; border: 1px solid #e2e8f0; border-radius: 999px; background: #f8fafc; color: #0f172a; font-size: 22px; cursor: pointer; }
.duplicate-cv__field { display: grid; gap: 7px; margin-top: 18px; font-weight: 750; color: #334155; }
.duplicate-cv__field input { width: 100%; box-sizing: border-box; min-height: 46px; padding: 0 12px; border: 1px solid #cbd5e1; border-radius: 11px; background: #fff; color: #0f172a; font: inherit; }
.duplicate-cv__notice,.duplicate-cv__error { margin: 14px 0 0; padding: 11px 12px; border-radius: 11px; background: #f8fafc; color: #475569; line-height: 1.5; }
.duplicate-cv__error { background: #fff7ed; color: #9a3412; }
.duplicate-cv__actions { display: flex; justify-content: flex-end; gap: 9px; margin-top: 18px; }
.duplicate-cv__actions button { min-height: 42px; padding: 0 15px; border-radius: 11px; font: inherit; font-weight: 800; cursor: pointer; }
.duplicate-cv__secondary { border: 1px solid #cbd5e1; background: #fff; color: #334155; }
.duplicate-cv__primary { border: 1px solid #0f172a; background: #0f172a; color: #fff; }
.duplicate-cv__actions button:disabled,.duplicate-cv__close:disabled { opacity: .55; cursor: default; }
@media (max-width: 760px) {
  .duplicate-cv,[dir="rtl"].duplicate-cv { top: 180px; right: 8px; left: auto; }
  [dir="rtl"].duplicate-cv { right: auto; left: 8px; }
  .duplicate-cv__backdrop { padding: 10px; }
  .duplicate-cv__dialog { width: 100%; max-height: calc(100vh - 20px); padding: 16px; }
  .duplicate-cv__actions { flex-direction: column-reverse; }
  .duplicate-cv__actions button { width: 100%; }
}
'''
    css_path.write_text(css, encoding="utf-8")

print("Applied duplicate CV action.")
