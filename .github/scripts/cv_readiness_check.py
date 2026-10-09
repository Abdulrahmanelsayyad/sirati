from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
component_path = root / "components" / "CvReadinessCheck.tsx"
component_path.parent.mkdir(parents=True, exist_ok=True)

component_path.write_text(r''' 'use client';

import { useMemo, useState } from 'react';

type Check = {
  id: string;
  labelEn: string;
  labelAr: string;
  weight: number;
  passed: boolean;
};

type CVRecord = Record<string, unknown>;
function isRecord(value: unknown): value is CVRecord {
  return !!value && typeof value === 'object' && !Array.isArray(value);
}
function record(value: unknown): CVRecord {
  return isRecord(value) ? value : {};
}
function textValue(value: unknown): string {
  if (typeof value === 'string') return value.trim();
  if (typeof value === 'number' && Number.isFinite(value)) return String(value);
  return '';
}
function firstValue(source: CVRecord, keys: string[]): string {
  for (const key of keys) {
    const value = textValue(source[key]);
    if (value) return value;
  }
  return '';
}
function sectionRows(value: unknown): CVRecord[] {
  if (Array.isArray(value)) {
    return value.map((item) => typeof item === 'string' ? { text: item } : record(item));
  }
  if (typeof value === 'string') return value.trim() ? [{ text: value }] : [];
  return isRecord(value) ? [value] : [];
}
function sectionText(value: unknown, keys: string[]): string {
  return sectionRows(value)
    .map((item) => keys.map((key) => textValue(item[key])).filter(Boolean).join(' '))
    .filter(Boolean).join('\n');
}
function countUniqueItems(value: unknown): number {
  const raw = Array.isArray(value) ? value.map((v) =>
    typeof v === 'string' ? v : firstValue(record(v), ['name', 'skill', 'text'])
  ).join('\n') : textValue(value);
  const items = raw.split(/[\n,;•|]+/)
    .map((item) => item.toLocaleLowerCase().trim().replace(/\s+/g, ' '))
    .filter((item) => item.length >= 2);
  return new Set(items).size;
}
function hasActionLanguage(value: string): boolean {
  return /(managed|led|supervised|coordinated|implemented|improved|reduced|increased|developed|performed|administered|assessed|monitored|trained|maintained|documented|أدرت|ادرت|قدت|أشرفت|اشرفت|نسقت|نفذت|حسنت|راقبت|دربت|وثقت)/i.test(value);
}
function hasMeasuredImpact(value: string): boolean {
  return /[0-9٠-٩]{1,3}\s*%/.test(value)
    || /[0-9٠-٩]+\+?\s+(patients?|cases?|staff|employees?|projects?|beds?|calls?|clients?|مريض|مرضى|حالة|حالات|موظف|موظفين|مشروع|مشاريع|سرير|أسرة|اسرة)/i.test(value);
}

/**
 * Pure, read-only CV quality guide, not an ATS vendor score.
 * Uses the current Builder's authoritative data object instead of DOM labels.
 * No factual content is inferred, created or saved by this function.
 */
export function evaluateCvQuality(input: unknown): Check[] {
  const data = record(input);
  const contact = record(data.contact);
  const person = record(data.personal);
  const name = firstValue(data, ['fullName', 'name']) ||
    firstValue(person, ['fullName', 'name']) ||
    [firstValue(data, ['firstName']), firstValue(data, ['lastName'])].filter(Boolean).join(' ');
  const email = firstValue(data, ['email']) || firstValue(contact, ['email']) || firstValue(person, ['email']);
  const phone = firstValue(data, ['phone', 'mobile']) ||
    firstValue(contact, ['phone', 'mobile']) || firstValue(person, ['phone', 'mobile']);
  const summary = firstValue(data, ['profile', 'summary', 'personalSummary']);
  const skillsValue = data.skills;
  const work = sectionRows(data.experience);
  const workText = sectionText(data.experience, ['details', 'description', 'responsibilities', 'achievements', 'text']);
  const education = sectionText(data.education, ['degree', 'institution', 'school', 'university', 'qualification', 'text']);
  const workPresent = work.some((item) =>
    !!firstValue(item, ['role', 'title', 'position', 'jobTitle', 'company', 'employer', 'details', 'description', 'text'])
  );
  const hasSkills = countUniqueItems(skillsValue) > 0;
  const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email);
  return [
    { id: 'name', labelEn: 'Full name', labelAr: 'الاسم الكامل', weight: 10, passed: name.length >= 2 },
    { id: 'contact', labelEn: 'Contact details', labelAr: 'بيانات التواصل', weight: 10, passed: !!(emailValid || phone.length >= 6) },
    { id: 'summary', labelEn: 'Professional summary', labelAr: 'الملخص المهني', weight: 10, passed: summary.length >= 60 },
    { id: 'experience', labelEn: 'Work experience', labelAr: 'الخبرة العملية', weight: 10, passed: workPresent },
    { id: 'education', labelEn: 'Education', labelAr: 'التعليم', weight: 10, passed: education.length >= 2 },
    { id: 'skills', labelEn: 'Skills', labelAr: 'المهارات', weight: 10, passed: hasSkills },
    { id: 'email-quality', labelEn: 'Valid professional email', labelAr: 'بريد إلكتروني صحيح', weight: 8, passed: emailValid },
    { id: 'summary-focus', labelEn: 'Focused summary (60–350 chars)', labelAr: 'ملخص مركز (60–350 حرف)', weight: 8, passed: summary.length >= 60 && summary.length <= 350 },
    { id: 'skills-depth', labelEn: '5+ relevant skills', labelAr: '5 مهارات مناسبة أو أكثر', weight: 8, passed: countUniqueItems(skillsValue) >= 5 },
    { id: 'action-language', labelEn: 'Action-oriented experience wording', labelAr: 'صياغة خبرة بأفعال قوية', weight: 8, passed: workText.length >= 20 && hasActionLanguage(workText) },
    { id: 'impact', labelEn: 'Measurable impact when available', labelAr: 'أثر قابل للقياس عند توفره', weight: 8, passed: hasMeasuredImpact(workText) },
  ];
}

export default function CvReadinessCheck({ data, language: requestedLanguage }: { data: unknown; language: string }) {
  const [open, setOpen] = useState(false);
  const language: 'en' | 'ar' = requestedLanguage === 'ar' ? 'ar' : 'en';
  const checks = useMemo(() => evaluateCvQuality(data), [data]);

  const score = useMemo(
    () => checks.reduce((sum, item) => sum + (item.passed ? item.weight : 0), 0),
    [checks]
  );
  const passedCount = checks.filter((item) => item.passed).length;
  const status =
    score >= 85
      ? (language === 'ar' ? 'قوي وجاهز للمراجعة' : 'Strong and ready to review')
      : score >= 55
        ? (language === 'ar' ? 'جيد ويحتاج بعض التحسين' : 'Good, with a few improvements')
        : (language === 'ar' ? 'يحتاج تحسين قبل الإرسال' : 'Needs improvement before sending');

  return (
    <aside className="cv-readiness" dir={language === 'ar' ? 'rtl' : 'ltr'} aria-label={language === 'ar' ? 'مركز جودة السيرة الذاتية' : 'CV Quality Center'}>
      <button
        type="button"
        className="cv-readiness__trigger"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
      >
        <span>{language === 'ar' ? 'جودة CV' : 'CV quality'}</span>
        <strong>{score}%</strong>
      </button>

      {open && (
        <div className="cv-readiness__panel">
          <div className="cv-readiness__heading">
            <div>
              <small>{language === 'ar' ? 'SIRATI QUALITY CENTER' : 'SIRATI QUALITY CENTER'}</small>
              <h3>{status}</h3>
            </div>
            <strong>{score}%</strong>
          </div>

          <div className="cv-readiness__bar" aria-hidden="true">
            <span style={{ width: `${score}%` }} />
          </div>

          <p className="cv-readiness__summary">
            {language === 'ar'
              ? `${passedCount} من ${checks.length} فحص جودة مكتمل`
              : `${passedCount} of ${checks.length} quality checks complete`}
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
              ? 'هذه نسبة جودة عملية مبنية على فحوص واضحة داخل Sirati؛ ليست ATS Score ولا ضمانًا للمقابلة أو القبول.'
              : 'This is a transparent Sirati quality guide, not an ATS score or a hiring guarantee.'}
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
