"""Add a zero-cost, client-side Career Toolkit without touching paid order/auth flows."""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
target = root / "app/career-tools/page.tsx"
target.parent.mkdir(parents=True, exist_ok=True)
if target.exists():
    raise RuntimeError("Career tools route already exists: refusing overwrite")
target.write_text(r"""'use client';

import Link from 'next/link';
import { useState } from 'react';

type Mode = 'letter' | 'linkedin' | 'interview';
type Language = 'en' | 'ar';
type Fields = { name: string; role: string; company: string; facts: string; skills: string };

function draftFor(mode: Mode, lang: Language, f: Fields): string {
  const name = f.name.trim();
  const role = f.role.trim();
  const company = f.company.trim();
  const facts = f.facts.trim();
  const skills = f.skills.trim();
  if (mode === 'letter') {
    return lang === 'ar'
      ? ['السادة فريق التوظيف في ' + company + '،', '', 'أتقدم لشغل وظيفة ' + role + '.',
          'من خبراتي الفعلية: ' + facts + '.', skills ? 'ومن المهارات التي أمتلكها: ' + skills + '.' : '',
          'أتطلع إلى فرصة لمناقشة مدى ملاءمة خبراتي لمتطلبات الوظيفة.', '',
          'مع خالص التحية،', name].filter(x => x !== '').join('\n')
      : ['Dear Hiring Team at ' + company + ',', '', 'I am applying for the ' + role + ' position.',
          'My relevant experience includes: ' + facts + '.', skills ? 'Skills I can bring include: ' + skills + '.' : '',
          'I would welcome the opportunity to discuss how my experience relates to this role.', '',
          'Sincerely,', name].filter(x => x !== '').join('\n');
  }
  if (mode === 'linkedin') {
    return lang === 'ar'
      ? 'العنوان المهني:\n' + role + (skills ? ' | ' + skills.split(/[،,\n]/)[0].trim().slice(0, 75) : '')
        + '\n\nنبذة عني:\nأعمل في مجال ' + role + '. من خبراتي: ' + facts + '.'
        + (skills ? '\nمهارات أمتلكها: ' + skills + '.' : '')
      : 'HEADLINE:\n' + role + (skills ? ' | ' + skills.split(/[,\n]/)[0].trim().slice(0, 75) : '')
        + '\n\nABOUT:\nMy background as a ' + role + ' includes: ' + facts + '.'
        + (skills ? '\nMy skills include: ' + skills + '.' : '');
  }
  const questions = lang === 'ar'
    ? ['حدثنا عن نفسك وخبرتك المناسبة لدور ' + role + '؟',
       'ما الذي جذبك إلى وظيفة ' + role + '؟',
       'صف موقفًا استخدمت فيه مهاراتك لحل مشكلة فعلية.',
       'كيف تحدد الأولويات عند التعامل مع عدة مهام؟',
       'احكِ عن تحدٍ واجهته، وكيف تعاملت معه وما النتيجة الحقيقية؟',
       'ما الأسئلة التي ترغب في طرحها على جهة العمل؟']
    : ['Tell us about your background related to the ' + role + ' role.',
       'Why are you interested in this ' + role + ' position?',
       'Describe a real problem you solved using your skills.',
       'How do you prioritize competing responsibilities?',
       'Share an actual challenge, your actions and the outcome.',
       'What would you like to ask the interviewer?'];
  return (lang === 'ar'
    ? 'تدريب مقابلة لوظيفة: ' + role + '\nأجب باستخدام أمثلة حقيقية. استخدم: الموقف، المهمة، الإجراء، النتيجة.\n\n'
    : 'Interview practice for: ' + role + '\nUse real examples. Structure answers as Situation, Task, Action, Result.\n\n')
    + questions.map((q, i) => (i + 1) + '. ' + q).join('\n\n')
    + (facts ? (lang === 'ar' ? '\n\nخبرات ذكرتها للتدرب عليها: ' : '\n\nYour stated background to practice with: ') + facts : '');
}

export default function CareerToolsPage() {
  const [lang, setLang] = useState<Language>('en');
  const [mode, setMode] = useState<Mode>('letter');
  const [fields, setFields] = useState<Fields>({ name: '', role: '', company: '', facts: '', skills: '' });
  const [draft, setDraft] = useState('');
  const [notice, setNotice] = useState('');
  const ar = lang === 'ar';
  const t = (en: string, arabic: string) => ar ? arabic : en;
  const valid = Boolean(fields.role.trim()) &&
    (mode === 'interview' || Boolean(fields.facts.trim())) &&
    (mode !== 'letter' || Boolean(fields.name.trim() && fields.company.trim()));
  function changeMode(next: Mode) { setMode(next); setDraft(''); setNotice(''); }
  function update(field: keyof Fields, value: string) {
    setFields(previous => ({ ...previous, [field]: value }));
    setNotice('');
  }
  async function copyDraft() {
    if (!draft) return;
    try {
      await navigator.clipboard.writeText(draft);
      setNotice(t('Copied to clipboard.', 'تم نسخ النص.'));
    } catch {
      setNotice(t('Copy unavailable: select the text below to copy.', 'النسخ غير متاح: حدد النص أدناه لنسخه.'));
    }
  }
  function downloadDraft() {
    if (!draft) return;
    const url = URL.createObjectURL(new Blob(['\uFEFF' + draft], { type: 'text/plain;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = 'sirati-' + mode + '-' + lang + '.txt';
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }
  return <main className="career-page" dir={ar ? 'rtl' : 'ltr'}>
    <header className="career-top"><Link href="/" className="brand">Sirati · سيرتي</Link>
      <div><Link className="btn btn-secondary" href="/templates">{t('CV templates', 'قوالب السيرة')}</Link>
        <button type="button" className="btn btn-secondary" onClick={() => { setLang(ar ? 'en' : 'ar'); setDraft(''); }} aria-label="Switch language">{ar ? 'English' : 'العربية'}</button>
      </div>
    </header>
    <div className="career-wrap">
      <div className="career-hero"><span className="eyebrow">{t('FREE CAREER TOOLKIT', 'أدوات مهنية مجانية')}</span>
        <h1>{t('A stronger application, made simpler.', 'قدّم على الوظائف بثقة وبخطوات بسيطة.')}</h1>
        <p>{t('Write a cover letter, refresh your LinkedIn text or prepare for interviews. No fees, sign-in, or external AI required.', 'اكتب خطاب التقديم، وحسّن وصف لينكدإن، وتدرّب على المقابلات دون رسوم أو تسجيل دخول أو خدمة ذكاء اصطناعي خارجية.')}</p>
      </div>
      <div className="career-tabs" role="group" aria-label="Career tool">
        {([['letter', 'Cover letter', 'خطاب تقديم'], ['linkedin', 'LinkedIn profile', 'الملف المهني'], ['interview', 'Interview prep', 'التدرب للمقابلة']] as const).map(([id, en, arabic]) =>
          <button key={id} type="button" aria-pressed={mode === id} className={mode === id ? 'career-tab selected' : 'career-tab'} onClick={() => changeMode(id)}>
            {t(en, arabic)}
          </button>)}
      </div>
      <div className="career-grid">
        <section className="career-card career-form" aria-label={t('Your real information', 'بياناتك الحقيقية')}>
          <h2>{t('Your information', 'بياناتك')}</h2>
          <p>{t('Only enter facts you can verify. Nothing is submitted to Sirati or saved by this tool.', 'أدخل معلومات حقيقية يمكنك تأكيدها. هذه الأداة لا ترسل البيانات أو تحفظها.')}</p>
          {mode === 'letter' && <label>{t('Full name', 'الاسم بالكامل')} *
            <input data-field="name" maxLength={120} value={fields.name} onChange={e => update('name', e.target.value)} /></label>}
          <label>{t('Professional title / target role', 'المسمى الوظيفي')} *
            <input data-field="role" maxLength={120} value={fields.role} onChange={e => update('role', e.target.value)} /></label>
          {mode === 'letter' && <label>{t('Company you are applying to', 'جهة العمل المستهدفة')} *
            <input data-field="company" maxLength={120} value={fields.company} onChange={e => update('company', e.target.value)} /></label>}
          {mode !== 'interview' && <label>{t('Your real experience / achievements', 'خبراتك أو إنجازاتك الحقيقية')} *
            <textarea data-field="facts" rows={5} maxLength={1600} value={fields.facts} onChange={e => update('facts', e.target.value)} placeholder={t('Describe work you actually did', 'اكتب ما قمت به فعلاً')} /></label>}
          <label>{t(mode === 'interview' ? 'Background to practice with (optional)' : 'Verified skills (optional)', mode === 'interview' ? 'خبرات تريد التدريب عليها (اختياري)' : 'مهارات حقيقية (اختياري)')}
            <textarea data-field="skills" rows={3} maxLength={600} value={fields.skills} onChange={e => update('skills', e.target.value)} /></label>
          <button type="button" className="btn btn-primary" disabled={!valid} onClick={() => { setDraft(draftFor(mode, lang, { ...fields, facts: mode === 'interview' ? fields.skills : fields.facts })); setNotice(''); }}>
            {t('Generate editable draft', 'إنشاء مسودة قابلة للتعديل')}</button>
        </section>
        <section className="career-card career-result" aria-label={t('Editable result', 'النتيجة')}>
          <h2>{t('Your editable draft', 'مسودتك القابلة للتعديل')}</h2>
          <p>{t('Review the wording and accuracy before using it. This is structured drafting, not a hiring guarantee.', 'راجع الصياغة والدقة قبل الاستخدام. هذه مسودة منظمة وليست ضمانًا للتوظيف.')}</p>
          <textarea data-testid="career-output" aria-label={t('Editable draft', 'مسودة قابلة للتعديل')} rows={19} value={draft} onChange={e => setDraft(e.target.value)}
            placeholder={t('Enter the required details, then select Generate.', 'أدخل المعلومات المطلوبة ثم اضغط إنشاء.')} />
          <div className="career-actions">
            <button type="button" className="btn btn-secondary" disabled={!draft} onClick={copyDraft}>{t('Copy text', 'نسخ النص')}</button>
            <button type="button" className="btn btn-secondary" disabled={!draft} onClick={downloadDraft}>{t('Download TXT', 'تنزيل ملف نصي')}</button>
          </div>
          <p role="status" aria-live="polite" className="career-feedback">{notice}</p>
        </section>
      </div>
    </div>
  </main>;
}
""", encoding="utf-8")

home_path = root / "app/page.tsx"
home = home_path.read_text(encoding="utf-8")
nav = '<a href="#services">Services</a>'
cta = '<p>Use the templates, role-based content suggestions and CV quality checks at no cost.</p>'
if home.count(nav) < 1 or home.count(cta) != 1:
    raise RuntimeError("Homepage navigation/service anchors changed")
home = home.replace(nav, nav + '\n            <a href="./career-tools/">Career tools</a>', 1)
home = home.replace(cta, cta + '\n            <a className="btn btn-light btn-lg" href="./career-tools/">Explore free career tools</a>', 1)
home_path.write_text(home, encoding="utf-8")

css_path = root / "app/globals.css"
css_path.write_text(css_path.read_text(encoding="utf-8") + r"""
/* Free career toolkit: isolated from CV template/print styles. */
.career-page{min-height:100vh;background:#f7f8f5;color:#152923;font-family:Inter,Arial,sans-serif}
.career-top{max-width:1160px;margin:auto;padding:24px;display:flex;align-items:center;justify-content:space-between;gap:12px}
.career-top>div{display:flex;gap:8px;flex-wrap:wrap}.career-wrap{max-width:1160px;margin:auto;padding:18px 24px 72px}
.career-hero{max-width:780px}.career-hero h1{font-size:clamp(32px,5vw,56px);line-height:1.15;margin:14px 0}
.career-hero p,.career-card>p{color:#52655e;line-height:1.7}.career-tabs{display:flex;flex-wrap:wrap;gap:10px;margin:30px 0 20px}
.career-tab{border:1px solid #cbd9d0;background:#fff;border-radius:999px;padding:12px 18px;color:#152923;cursor:pointer}
.career-tab.selected{color:#fff;background:#184237;border-color:#184237}.career-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start}
.career-card{min-width:0;padding:24px;border:1px solid #dce5df;background:#fff;border-radius:18px;box-shadow:0 12px 30px rgba(16,45,35,.05)}
.career-card h2{font-size:23px;margin:0 0 8px}.career-form label{display:block;font-weight:650;margin:18px 0 0}
.career-form input,.career-form textarea,.career-result textarea{width:100%;box-sizing:border-box;min-width:0;border:1px solid #b8c9c1;background:#fff;border-radius:10px;padding:12px;margin-top:7px;font:inherit;font-weight:400;line-height:1.55;color:#152923}
.career-form textarea,.career-result textarea{resize:vertical}.career-form>.btn{margin-top:18px;min-height:46px}
.career-form>.btn:disabled,.career-actions button:disabled{opacity:.45;cursor:not-allowed}
.career-result textarea{white-space:pre-wrap;direction:inherit;min-height:290px}.career-actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
.career-feedback{min-height:1.5em;color:#184237}.career-page :is(button,input,textarea,a):focus-visible{outline:3px solid #439b75;outline-offset:3px}
@media(max-width:760px){.career-top{padding:14px 16px;flex-wrap:wrap}.career-wrap{padding:18px 16px 52px}.career-grid{grid-template-columns:minmax(0,1fr)}.career-card{padding:18px}.career-tab{flex:1 1 auto}}
""", encoding="utf-8")
print("PASS: generated free bilingual Career Toolkit, nav and responsive styles.")
