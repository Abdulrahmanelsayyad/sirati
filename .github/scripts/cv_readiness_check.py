from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
component_path = root / "components" / "CvReadinessCheck.tsx"
component_path.parent.mkdir(parents=True, exist_ok=True)

component_path.write_text(r''' 'use client';

import { useEffect, useMemo, useState } from 'react';

type Check = {
  id: string;
  labelEn: string;
  labelAr: string;
  weight: number;
  passed: boolean;
};

function fieldValue(pattern: RegExp): string {
  const fields = Array.from(document.querySelectorAll<HTMLElement>('.field, label, .wizard-section-card'));
  for (const field of fields) {
    const text = (field.innerText || field.textContent || '').replace(/\s+/g, ' ').trim();
    if (!pattern.test(text)) continue;
    const control = field.querySelector<HTMLInputElement | HTMLTextAreaElement>('input, textarea');
    if (control?.value?.trim()) return control.value.trim();
  }
  return '';
}

function anyTextArea(minLength = 1): string {
  const areas = Array.from(document.querySelectorAll<HTMLTextAreaElement>('textarea'));
  const match = areas.find((item) => item.value.trim().length >= minLength);
  return match?.value.trim() || '';
}

function anyControlByType(type: string): string {
  const control = document.querySelector<HTMLInputElement>(`input[type="${type}"]`);
  return control?.value?.trim() || '';
}

function detectLanguage(): 'en' | 'ar' {
  const cv = document.querySelector<HTMLElement>('.cv-sheet');
  if (cv?.getAttribute('dir') === 'rtl') return 'ar';
  if (document.documentElement.getAttribute('dir') === 'rtl') return 'ar';
  return 'en';
}

function scanChecks(): Check[] {
  const fullName = fieldValue(/full name|الاسم الكامل|الاسم/i);
  const email = anyControlByType('email') || fieldValue(/email|البريد/i);
  const phone = anyControlByType('tel') || fieldValue(/phone|mobile|هاتف|موبايل|جوال/i);
  const summary = fieldValue(/professional summary|summary|profile|نبذة|ملخص/i) || anyTextArea(80);
  const experience = fieldValue(/job title|position|company|employer|experience|المسمى|الوظيفة|الشركة|جهة العمل|الخبرة/i);
  const education = fieldValue(/education|degree|university|school|التعليم|المؤهل|الجامعة|الكلية/i);
  const skills = fieldValue(/skills|مهارات/i);

  return [
    { id: 'name', labelEn: 'Full name', labelAr: 'الاسم الكامل', weight: 15, passed: fullName.length >= 2 },
    { id: 'contact', labelEn: 'Contact details', labelAr: 'بيانات التواصل', weight: 15, passed: email.length >= 5 || phone.length >= 6 },
    { id: 'summary', labelEn: 'Professional summary', labelAr: 'الملخص المهني', weight: 20, passed: summary.length >= 60 },
    { id: 'experience', labelEn: 'Work experience', labelAr: 'الخبرة العملية', weight: 20, passed: experience.length >= 2 },
    { id: 'education', labelEn: 'Education', labelAr: 'التعليم', weight: 15, passed: education.length >= 2 },
    { id: 'skills', labelEn: 'Skills', labelAr: 'المهارات', weight: 15, passed: skills.length >= 2 },
  ];
}

export default function CvReadinessCheck() {
  const [enabled, setEnabled] = useState(false);
  const [open, setOpen] = useState(false);
  const [language, setLanguage] = useState<'en' | 'ar'>('en');
  const [checks, setChecks] = useState<Check[]>([]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const onBuilder = window.location.pathname.includes('/builder');
    setEnabled(onBuilder);
    if (!onBuilder) return;

    const scan = () => {
      setLanguage(detectLanguage());
      setChecks(scanChecks());
    };

    scan();
    const timer = window.setInterval(scan, 700);
    document.addEventListener('input', scan, true);
    document.addEventListener('change', scan, true);

    return () => {
      window.clearInterval(timer);
      document.removeEventListener('input', scan, true);
      document.removeEventListener('change', scan, true);
    };
  }, []);

  const score = useMemo(
    () => checks.reduce((sum, item) => sum + (item.passed ? item.weight : 0), 0),
    [checks]
  );
  const passedCount = checks.filter((item) => item.passed).length;
  const status =
    score >= 85
      ? (language === 'ar' ? 'جاهز للمراجعة' : 'Ready to review')
      : score >= 55
        ? (language === 'ar' ? 'قريب من الاكتمال' : 'Almost there')
        : (language === 'ar' ? 'يحتاج استكمال' : 'Needs work');

  if (!enabled) return null;

  return (
    <aside className="cv-readiness" dir={language === 'ar' ? 'rtl' : 'ltr'} aria-label={language === 'ar' ? 'فحص جاهزية السيرة الذاتية' : 'CV readiness check'}>
      <button
        type="button"
        className="cv-readiness__trigger"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
      >
        <span>{language === 'ar' ? 'جاهزية CV' : 'CV readiness'}</span>
        <strong>{score}%</strong>
      </button>

      {open && (
        <div className="cv-readiness__panel">
          <div className="cv-readiness__heading">
            <div>
              <small>{language === 'ar' ? 'فحص سريع أثناء الكتابة' : 'Live completion check'}</small>
              <h3>{status}</h3>
            </div>
            <strong>{score}%</strong>
          </div>

          <div className="cv-readiness__bar" aria-hidden="true">
            <span style={{ width: `${score}%` }} />
          </div>

          <p className="cv-readiness__summary">
            {language === 'ar'
              ? `${passedCount} من ${checks.length} عناصر أساسية مكتملة`
              : `${passedCount} of ${checks.length} essentials complete`}
          </p>

          <ul className="cv-readiness__list">
            {checks.map((item) => (
              <li key={item.id} className={item.passed ? 'is-complete' : ''}>
                <span aria-hidden="true">{item.passed ? '✓' : '○'}</span>
                <span>{language === 'ar' ? item.labelAr : item.labelEn}</span>
              </li>
            ))}
          </ul>

          <p className="cv-readiness__note">
            {language === 'ar'
              ? 'هذا مؤشر جاهزية عملي وليس ضمانًا لنتيجة أي نظام ATS.'
              : 'This is a practical readiness guide, not an ATS-score guarantee.'}
          </p>
        </div>
      )}
    </aside>
  );
}
'''.lstrip(), encoding="utf-8")

layout = root / "app" / "layout.tsx"
text = layout.read_text(encoding="utf-8")
imp = "import CvReadinessCheck from '@/components/CvReadinessCheck';\n"
if imp not in text:
    lines = text.splitlines(True)
    insert_at = 0
    while insert_at < len(lines) and (lines[insert_at].startswith("import ") or not lines[insert_at].strip()):
        insert_at += 1
    lines.insert(insert_at, imp)
    text = "".join(lines)

if "<CvReadinessCheck />" not in text:
    if "</body>" not in text:
        raise SystemExit("Could not find </body> in app/layout.tsx")
    text = text.replace("</body>", "        <CvReadinessCheck />\n      </body>", 1)

layout.write_text(text, encoding="utf-8")

css_path = root / "app" / "globals.css"
css = css_path.read_text(encoding="utf-8")
marker = "/* Sirati CV readiness check */"
if marker not in css:
    css += r'''

/* Sirati CV readiness check */
.cv-readiness {
  position: fixed;
  top: 88px;
  right: 16px;
  z-index: 88;
  width: min(340px, calc(100vw - 32px));
  font-size: 14px;
}
.cv-readiness__trigger {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 42px;
  padding: 8px 12px;
  border: 1px solid rgba(15, 23, 42, .12);
  border-radius: 999px;
  background: rgba(255, 255, 255, .97);
  box-shadow: 0 12px 30px rgba(15, 23, 42, .12);
  color: #0f172a;
  font: inherit;
  cursor: pointer;
}
.cv-readiness__trigger strong {
  display: grid;
  place-items: center;
  min-width: 50px;
  min-height: 28px;
  padding: 0 8px;
  border-radius: 999px;
  background: #0f172a;
  color: #fff;
}
.cv-readiness__panel {
  margin-top: 8px;
  padding: 16px;
  border: 1px solid rgba(15, 23, 42, .10);
  border-radius: 18px;
  background: rgba(255, 255, 255, .98);
  box-shadow: 0 18px 48px rgba(15, 23, 42, .16);
  backdrop-filter: blur(12px);
}
.cv-readiness__heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}
.cv-readiness__heading small {
  display: block;
  margin-bottom: 4px;
  color: #64748b;
}
.cv-readiness__heading h3 {
  margin: 0;
  font-size: 20px;
}
.cv-readiness__heading > strong {
  font-size: 22px;
}
.cv-readiness__bar {
  height: 7px;
  margin: 14px 0 10px;
  overflow: hidden;
  border-radius: 999px;
  background: #e2e8f0;
}
.cv-readiness__bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: #0f172a;
  transition: width .2s ease;
}
.cv-readiness__summary {
  margin: 0 0 12px;
  color: #475569;
}
.cv-readiness__list {
  display: grid;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}
.cv-readiness__list li {
  display: flex;
  align-items: center;
  gap: 9px;
  min-height: 34px;
  padding: 6px 9px;
  border-radius: 10px;
  background: #f8fafc;
  color: #475569;
}
.cv-readiness__list li.is-complete {
  color: #0f172a;
  font-weight: 650;
}
.cv-readiness__list li > span:first-child {
  display: grid;
  place-items: center;
  flex: 0 0 24px;
  width: 24px;
  height: 24px;
  border-radius: 999px;
  background: #e2e8f0;
}
.cv-readiness__list li.is-complete > span:first-child {
  background: #0f172a;
  color: #fff;
}
.cv-readiness__note {
  margin: 12px 0 0;
  padding-top: 10px;
  border-top: 1px solid #e2e8f0;
  color: #64748b;
  font-size: 12px;
  line-height: 1.5;
}
[dir="rtl"] .cv-readiness__trigger {
  margin-left: 0;
  margin-right: auto;
}
@media (max-width: 760px) {
  .cv-readiness {
    top: 72px;
    right: 8px;
    width: min(330px, calc(100vw - 16px));
  }
  .cv-readiness__panel {
    max-height: min(520px, calc(100vh - 180px));
    overflow: auto;
  }
}
'''
    css_path.write_text(css, encoding="utf-8")

print("Applied CV readiness check.")
