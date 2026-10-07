from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
component_path = root / "components" / "TargetJobTailor.tsx"
component_path.parent.mkdir(parents=True, exist_ok=True)

component_path.write_text(r''' 'use client';

import { useEffect, useMemo, useState } from 'react';

type Language = 'en' | 'ar';

type KeywordResult = {
  term: string;
  score: number;
  matched: boolean;
};

const STOPWORDS = new Set([
  'and','the','for','with','that','this','from','your','you','our','are','will','have','has','into','who','job','role',
  'work','working','using','within','about','their','they','them','but','not','all','any','can','may','must','should',
  'required','preferred','including','include','responsible','responsibilities','requirements','qualification','qualifications',
  'years','year','experience','skills','skill','ability','strong','excellent','good','team','teams','position','candidate',
  'في','من','على','إلى','الى','عن','مع','هذا','هذه','ذلك','تلك','التي','الذي','الذين','و','أو','او','أن','ان','كما',
  'يجب','يفضل','مطلوب','المطلوب','خبرة','سنوات','سنة','مهارات','مهارة','القدرة','العمل','فريق','ضمن','مسؤول','مسؤوليات',
  'الوظيفة','الدور','المتطلبات','المؤهلات','جيد','ممتاز','قوي','لدى','لديه','لديها'
]);

const COMMON_PHRASES = [
  'patient safety','clinical documentation','quality improvement','infection control','critical care','emergency nursing',
  'patient care','care coordination','medication administration','team leadership','project management','data analysis',
  'customer service','problem solving','time management','risk management','quality assurance','healthcare quality',
  'electronic medical records','registered nurse','multidisciplinary team','communication skills','continuous improvement',
  'سلامة المرضى','التوثيق السريري','تحسين الجودة','مكافحة العدوى','الرعاية الحرجة','تمريض الطوارئ','رعاية المرضى',
  'تنسيق الرعاية','إعطاء الأدوية','قيادة الفريق','إدارة المشاريع','تحليل البيانات','خدمة العملاء','حل المشكلات',
  'إدارة الوقت','إدارة المخاطر','ضمان الجودة','جودة الرعاية الصحية','السجلات الطبية الإلكترونية','فريق متعدد التخصصات'
];

function normalize(value: string) {
  return value
    .toLowerCase()
    .replace(/[\u064B-\u065F\u0670]/g, '')
    .replace(/[إأآ]/g, 'ا')
    .replace(/ى/g, 'ي')
    .replace(/ة/g, 'ه')
    .replace(/[^a-z0-9\u0600-\u06FF+#./-]+/gi, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function detectLanguage(): Language {
  const cv = document.querySelector<HTMLElement>('.cv-sheet');
  if (cv?.getAttribute('dir') === 'rtl') return 'ar';
  if (document.documentElement.getAttribute('dir') === 'rtl') return 'ar';
  return 'en';
}

function collectCvText() {
  const preview = document.querySelector<HTMLElement>('.cv-sheet')?.innerText || '';
  const controls = Array.from(document.querySelectorAll<HTMLInputElement | HTMLTextAreaElement>('input, textarea'))
    .filter((item) => !item.closest('.job-tailor'))
    .map((item) => item.value)
    .filter(Boolean)
    .join(' ');
  return normalize(preview + ' ' + controls);
}

function extractKeywords(title: string, description: string): Array<{ term: string; score: number }> {
  const normalizedTitle = normalize(title);
  const normalizedDescription = normalize(description);
  const weights = new Map<string, number>();

  const add = (term: string, score: number) => {
    const clean = normalize(term);
    if (!clean || clean.length < 2 || STOPWORDS.has(clean)) return;
    weights.set(clean, (weights.get(clean) || 0) + score);
  };

  if (normalizedTitle) {
    add(normalizedTitle, 8);
    normalizedTitle.split(' ').forEach((token) => {
      if (token.length >= 3 && !STOPWORDS.has(token)) add(token, 4);
    });
  }

  const tokens = normalizedDescription.split(' ').filter(Boolean);
  tokens.forEach((token) => {
    if (token.length < 3 || STOPWORDS.has(token) || /^\d+$/.test(token)) return;
    add(token, 1);
  });

  COMMON_PHRASES.forEach((phrase) => {
    const clean = normalize(phrase);
    if (clean && normalizedDescription.includes(clean)) add(clean, 5);
  });

  return Array.from(weights.entries())
    .map(([term, score]) => ({ term, score }))
    .sort((a, b) => b.score - a.score || b.term.length - a.term.length)
    .slice(0, 12);
}

export default function TargetJobTailor() {
  const [enabled, setEnabled] = useState(false);
  const [open, setOpen] = useState(false);
  const [language, setLanguage] = useState<Language>('en');
  const [targetRole, setTargetRole] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [cvText, setCvText] = useState('');

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const onBuilder = window.location.pathname.includes('/builder');
    setEnabled(onBuilder);
    if (!onBuilder) return;

    const scan = () => {
      setLanguage(detectLanguage());
      setCvText(collectCvText());
    };

    scan();
    const timer = window.setInterval(scan, 900);
    document.addEventListener('input', scan, true);
    document.addEventListener('change', scan, true);

    return () => {
      window.clearInterval(timer);
      document.removeEventListener('input', scan, true);
      document.removeEventListener('change', scan, true);
    };
  }, []);

  const analysisReady = normalize(jobDescription).length >= 40;

  const results = useMemo<KeywordResult[]>(() => {
    if (!analysisReady) return [];
    return extractKeywords(targetRole, jobDescription).map((item) => ({
      ...item,
      matched: cvText.includes(item.term),
    }));
  }, [targetRole, jobDescription, cvText, analysisReady]);

  const coverage = useMemo(() => {
    const total = results.reduce((sum, item) => sum + item.score, 0);
    if (!total) return 0;
    const matched = results.reduce((sum, item) => sum + (item.matched ? item.score : 0), 0);
    return Math.round((matched / total) * 100);
  }, [results]);

  const matched = results.filter((item) => item.matched);
  const missing = results.filter((item) => !item.matched);

  if (!enabled) return null;

  const copy = language === 'ar'
    ? {
        trigger: 'خصّص للوظيفة',
        eyebrow: 'تخصيص حسب الوظيفة المستهدفة',
        title: 'قارن سيرتك بإعلان الوظيفة',
        role: 'المسمى الوظيفي المستهدف',
        rolePlaceholder: 'مثال: ممرض طوارئ',
        jd: 'وصف الوظيفة',
        jdPlaceholder: 'الصق وصف أو إعلان الوظيفة هنا...',
        helper: 'الصق وصف الوظيفة للحصول على مقارنة محلية بدون AI أو تكلفة.',
        coverage: 'تغطية الكلمات المهمة',
        found: 'موجود في سيرتك',
        review: 'راجعها إذا كانت صحيحة لديك',
        noneMatched: 'لم يتم العثور على كلمات مطابقة بعد.',
        noneMissing: 'كل الكلمات المهمة المختارة موجودة في سيرتك.',
        clear: 'مسح',
        safety: 'أضف أي كلمة ناقصة فقط إذا كانت تعكس خبرتك ومهاراتك الحقيقية. Sirati لا يضيف معلومات تلقائيًا.',
        disclaimer: 'هذه مقارنة كلمات مفتاحية وليست درجة ATS أو ضمانًا للقبول.',
      }
    : {
        trigger: 'Tailor to job',
        eyebrow: 'TARGET JOB TAILORING',
        title: 'Compare your CV with the job ad',
        role: 'Target job title',
        rolePlaceholder: 'e.g. Emergency Nurse',
        jd: 'Job description',
        jdPlaceholder: 'Paste the job description here...',
        helper: 'Paste the job description for a local, zero-cost comparison without AI.',
        coverage: 'Keyword coverage',
        found: 'Already in your CV',
        review: 'Review if true for you',
        noneMatched: 'No selected keywords are matched yet.',
        noneMissing: 'All selected keywords are already represented in your CV.',
        clear: 'Clear',
        safety: 'Only add a missing term if it truthfully reflects your real experience or skills. Sirati never adds facts automatically.',
        disclaimer: 'This is keyword coverage, not an ATS score or hiring guarantee.',
      };

  return (
    <aside className="job-tailor" dir={language === 'ar' ? 'rtl' : 'ltr'} aria-label={copy.trigger}>
      <button
        type="button"
        className="job-tailor__trigger"
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
      >
        <span>{copy.trigger}</span>
        <strong aria-hidden="true">◎</strong>
      </button>

      {open && (
        <div className="job-tailor__panel">
          <div className="job-tailor__heading">
            <div>
              <small>{copy.eyebrow}</small>
              <h3>{copy.title}</h3>
            </div>
            {(targetRole || jobDescription) && (
              <button
                type="button"
                className="job-tailor__clear"
                onClick={() => {
                  setTargetRole('');
                  setJobDescription('');
                }}
              >
                {copy.clear}
              </button>
            )}
          </div>

          <label className="job-tailor__field">
            <span>{copy.role}</span>
            <input
              type="text"
              value={targetRole}
              onChange={(event) => setTargetRole(event.target.value)}
              placeholder={copy.rolePlaceholder}
              autoComplete="off"
            />
          </label>

          <label className="job-tailor__field">
            <span>{copy.jd}</span>
            <textarea
              value={jobDescription}
              onChange={(event) => setJobDescription(event.target.value)}
              placeholder={copy.jdPlaceholder}
              rows={6}
            />
          </label>

          {!analysisReady ? (
            <p className="job-tailor__helper">{copy.helper}</p>
          ) : (
            <>
              <div className="job-tailor__score">
                <div>
                  <small>{copy.coverage}</small>
                  <strong>{coverage}%</strong>
                </div>
                <div className="job-tailor__bar" aria-hidden="true">
                  <span style={{ width: `${coverage}%` }} />
                </div>
              </div>

              <section className="job-tailor__group">
                <h4>{copy.found}</h4>
                {matched.length ? (
                  <div className="job-tailor__chips">
                    {matched.map((item) => <span className="is-match" key={item.term}>✓ {item.term}</span>)}
                  </div>
                ) : <p>{copy.noneMatched}</p>}
              </section>

              <section className="job-tailor__group">
                <h4>{copy.review}</h4>
                {missing.length ? (
                  <div className="job-tailor__chips">
                    {missing.map((item) => <span key={item.term}>{item.term}</span>)}
                  </div>
                ) : <p>{copy.noneMissing}</p>}
              </section>

              <p className="job-tailor__safety">{copy.safety}</p>
              <p className="job-tailor__disclaimer">{copy.disclaimer}</p>
            </>
          )}
        </div>
      )}
    </aside>
  );
}
'''.lstrip(), encoding="utf-8")

layout = root / "app" / "layout.tsx"
text = layout.read_text(encoding="utf-8")
imp = "import TargetJobTailor from '@/components/TargetJobTailor';\n"
if imp not in text:
    lines = text.splitlines(True)
    insert_at = 0
    while insert_at < len(lines) and (lines[insert_at].startswith("import ") or not lines[insert_at].strip()):
        insert_at += 1
    lines.insert(insert_at, imp)
    text = "".join(lines)

if "<TargetJobTailor />" not in text:
    if "</body>" not in text:
        raise SystemExit("Could not find </body> in app/layout.tsx")
    text = text.replace("</body>", "        <TargetJobTailor />\n      </body>", 1)

layout.write_text(text, encoding="utf-8")

css_path = root / "app" / "globals.css"
css = css_path.read_text(encoding="utf-8")
marker = "/* Sirati target job tailoring */"
if marker not in css:
    css += r'''

/* Sirati target job tailoring */
.job-tailor {
  position: fixed;
  top: 88px;
  left: 16px;
  z-index: 87;
  width: min(390px, calc(100vw - 32px));
  font-size: 14px;
}
.job-tailor__trigger {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  min-height: 42px;
  padding: 8px 12px;
  border: 1px solid rgba(15, 23, 42, .12);
  border-radius: 999px;
  background: rgba(255, 255, 255, .97);
  box-shadow: 0 12px 30px rgba(15, 23, 42, .12);
  color: #0f172a;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
}
.job-tailor__trigger strong {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 999px;
  background: #0f172a;
  color: #fff;
}
.job-tailor__panel {
  margin-top: 8px;
  max-height: calc(100vh - 150px);
  overflow: auto;
  padding: 17px;
  border: 1px solid rgba(15, 23, 42, .10);
  border-radius: 18px;
  background: rgba(255, 255, 255, .985);
  box-shadow: 0 18px 48px rgba(15, 23, 42, .16);
  backdrop-filter: blur(12px);
}
.job-tailor__heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}
.job-tailor__heading small {
  display: block;
  margin-bottom: 4px;
  color: #64748b;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .08em;
}
.job-tailor__heading h3 {
  margin: 0;
  font-size: 20px;
  line-height: 1.25;
}
.job-tailor__clear {
  border: 0;
  background: transparent;
  color: #64748b;
  font: inherit;
  font-size: 12px;
  text-decoration: underline;
  cursor: pointer;
}
.job-tailor__field {
  display: grid;
  gap: 6px;
  margin-top: 12px;
  color: #334155;
  font-weight: 700;
}
.job-tailor__field input,
.job-tailor__field textarea {
  width: 100%;
  box-sizing: border-box;
  border: 1px solid #cbd5e1;
  border-radius: 11px;
  background: #fff;
  color: #0f172a;
  font: inherit;
  font-weight: 400;
  line-height: 1.5;
}
.job-tailor__field input {
  min-height: 42px;
  padding: 8px 10px;
}
.job-tailor__field textarea {
  padding: 10px;
  resize: vertical;
}
.job-tailor__helper,
.job-tailor__group p {
  margin: 12px 0 0;
  color: #64748b;
  line-height: 1.5;
}
.job-tailor__score {
  margin-top: 16px;
  padding: 12px;
  border-radius: 13px;
  background: #f8fafc;
}
.job-tailor__score > div:first-child {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 14px;
}
.job-tailor__score small {
  color: #64748b;
}
.job-tailor__score strong {
  font-size: 24px;
}
.job-tailor__bar {
  height: 7px;
  margin-top: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: #e2e8f0;
}
.job-tailor__bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: #0f172a;
  transition: width .2s ease;
}
.job-tailor__group {
  margin-top: 15px;
}
.job-tailor__group h4 {
  margin: 0 0 8px;
  font-size: 13px;
}
.job-tailor__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}
.job-tailor__chips span {
  max-width: 100%;
  padding: 6px 9px;
  border: 1px solid #dbe3ee;
  border-radius: 999px;
  background: #fff;
  color: #475569;
  font-size: 12px;
  overflow-wrap: anywhere;
}
.job-tailor__chips span.is-match {
  border-color: #cbd5e1;
  background: #f1f5f9;
  color: #0f172a;
  font-weight: 700;
}
.job-tailor__safety {
  margin: 16px 0 0;
  padding: 11px 12px;
  border-radius: 11px;
  background: #f8fafc;
  color: #334155;
  font-size: 12px;
  line-height: 1.55;
}
.job-tailor__disclaimer {
  margin: 9px 0 0;
  color: #64748b;
  font-size: 11px;
  line-height: 1.5;
}
[dir="rtl"].job-tailor {
  left: auto;
  right: 16px;
}
@media (max-width: 760px) {
  .job-tailor,
  [dir="rtl"].job-tailor {
    top: 126px;
    left: 8px;
    right: auto;
    width: min(374px, calc(100vw - 16px));
  }
  [dir="rtl"].job-tailor {
    left: auto;
    right: 8px;
  }
  .job-tailor__panel {
    max-height: calc(100vh - 190px);
    padding: 14px;
  }
  .job-tailor__trigger {
    min-height: 40px;
    padding: 6px 10px;
  }
}
'''
    css_path.write_text(css, encoding="utf-8")

print("Applied target job tailoring.")
