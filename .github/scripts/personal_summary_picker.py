"""Add opt-in role-based summary suggestions without touching CV persistence or payment."""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
component = root / "components" / "PersonalSummaryPicker.tsx"
component.write_text(r''' 'use client';
import { useEffect, useMemo, useRef, useState } from 'react';
import { createPortal } from 'react-dom';

type Local = { en: string; ar: string };
type Lang = 'en' | 'ar';
type Career = { match: RegExp; name: Local; focus: Local; outcome: Local };
const careers: Career[] = [
  {match:/\bicu\b|intensive care|عناية مركزة|رعاية حرجة/i,name:{en:'critical care nursing',ar:'تمريض الرعاية الحرجة'},focus:{en:'patient observation and clinical coordination',ar:'مراقبة المرضى والتنسيق السريري'},outcome:{en:'safe coordinated care',ar:'الرعاية الآمنة والمنسقة'}},
  {match:/emergency nurs|\ber nurse\b|trauma nurse|تمريض طوارئ|ممرض طوارئ/i,name:{en:'emergency nursing',ar:'تمريض الطوارئ'},focus:{en:'timely assessment and appropriate escalation',ar:'التقييم السريع والتصعيد المناسب'},outcome:{en:'safe emergency team performance',ar:'أداء فريق الطوارئ بشكل آمن'}},
  {match:/nurs|تمريض|ممرض|ممرضة/i,name:{en:'nursing',ar:'التمريض'},focus:{en:'patient-centered care and precise documentation',ar:'رعاية المرضى والتوثيق الدقيق'},outcome:{en:'patient safety and teamwork',ar:'سلامة المرضى والعمل الجماعي'}},
  {match:/accountant|accounting|bookkeep|محاسب|محاسبة|حسابات/i,name:{en:'accounting',ar:'المحاسبة'},focus:{en:'accurate financial records and reporting',ar:'دقة السجلات والتقارير المالية'},outcome:{en:'reliable financial workflows',ar:'موثوقية العمليات المالية'}},
  {match:/developer|software|programmer|full.stack|frontend|backend|مبرمج|برمجيات|مطو.?ر برمج/i,name:{en:'software development',ar:'تطوير البرمجيات'},focus:{en:'maintainable software and practical problem solving',ar:'البرمجيات القابلة للصيانة وحل المشكلات'},outcome:{en:'useful reliable digital experiences',ar:'تجارب رقمية مفيدة وموثوقة'}},
  {match:/engineer|مهندس|هندسة/i,name:{en:'engineering',ar:'الهندسة'},focus:{en:'technical planning and quality-centered execution',ar:'التخطيط الفني والتنفيذ عالي الجودة'},outcome:{en:'practical project results',ar:'نتائج عملية للمشروعات'}},
  {match:/teacher|educator|instructor|مدرس|معلم|معلمة|تدريس/i,name:{en:'education',ar:'التعليم'},focus:{en:'learner-centered teaching and clear instruction',ar:'التدريس المتمحور حول المتعلم والشرح الواضح'},outcome:{en:'supportive learning experiences',ar:'تجارب تعليمية داعمة'}},
  {match:/sales|account executive|مبيعات|مندوب بيع/i,name:{en:'sales',ar:'المبيعات'},focus:{en:'customer needs and clear product communication',ar:'احتياجات العملاء والتواصل الواضح'},outcome:{en:'positive customer relationships',ar:'علاقات إيجابية مع العملاء'}},
  {match:/marketing|marketer|seo|تسويق|مسوق/i,name:{en:'marketing',ar:'التسويق'},focus:{en:'audience needs and relevant content',ar:'احتياجات الجمهور والمحتوى الملائم'},outcome:{en:'clear brand communication',ar:'التواصل الواضح للعلامة التجارية'}},
  {match:/human resources|recruiter|recruitment|موارد بشرية|موارد بشريه|توظيف/i,name:{en:'human resources',ar:'الموارد البشرية'},focus:{en:'organized people processes and communication',ar:'تنظيم شؤون الموظفين والتواصل'},outcome:{en:'supportive employee experiences',ar:'تجارب إيجابية للموظفين'}},
  {match:/customer service|customer support|call center|help desk|خدمة عملاء|خدمه عملاء|كول سنتر/i,name:{en:'customer service',ar:'خدمة العملاء'},focus:{en:'clear communication and careful issue resolution',ar:'التواصل الواضح وحل المشكلات بعناية'},outcome:{en:'consistent customer support',ar:'خدمة عملاء متسقة'}},
  {match:/administrator|administrative|secretary|office manager|إداري|اداري|سكرتير|مساعد اداري/i,name:{en:'administration',ar:'الإدارة'},focus:{en:'efficient coordination and accurate records',ar:'التنسيق الفعال ودقة السجلات'},outcome:{en:'organized daily operations',ar:'تنظيم سير العمل اليومي'}},
  {match:/logistics|warehouse|supply chain|inventory|procurement|مخازن|مستودع|لوجست|مشتريات/i,name:{en:'logistics',ar:'اللوجستيات'},focus:{en:'inventory accuracy and order coordination',ar:'دقة المخزون وتنسيق الطلبات'},outcome:{en:'dependable supply operations',ar:'موثوقية عمليات الإمداد'}},
  {match:/graphic design|designer|ui.?ux|تصميم|مصمم/i,name:{en:'design',ar:'التصميم'},focus:{en:'clear visual communication and accessible design',ar:'التواصل البصري والتصميم سهل الاستخدام'},outcome:{en:'thoughtful visual experiences',ar:'تجارب بصرية مدروسة'}},
  {match:/physician|medical doctor|doctor|طبيب|طبيبة/i,name:{en:'medicine',ar:'الطب'},focus:{en:'patient assessment and clinical communication',ar:'تقييم المرضى والتواصل السريري'},outcome:{en:'safe coordinated healthcare',ar:'رعاية صحية آمنة ومنسقة'}},
  {match:/pharmacist|pharmacy|صيدلي|صيدلة/i,name:{en:'pharmacy',ar:'الصيدلة'},focus:{en:'medication safety and reliable information',ar:'سلامة الأدوية ودقة المعلومات الدوائية'},outcome:{en:'responsible pharmaceutical services',ar:'خدمات دوائية مسؤولة'}},
  {match:/laboratory|lab technician|تحاليل|مختبر|معمل/i,name:{en:'laboratory services',ar:'المختبرات'},focus:{en:'specimen processes and precise documentation',ar:'إجراءات العينات والتوثيق الدقيق'},outcome:{en:'reliable laboratory work',ar:'العمل المخبري الموثوق'}},
  {match:/hotel|hospitality|receptionist|chef|cook|restaurant|فندق|شيف|طباخ|مطعم/i,name:{en:'hospitality',ar:'الضيافة'},focus:{en:'attentive guest service and organization',ar:'خدمة الضيوف باهتمام والتنظيم'},outcome:{en:'positive guest experiences',ar:'تجارب إيجابية للضيوف'}},
  {match:/lawyer|attorney|legal counsel|paralegal|محام|قانوني/i,name:{en:'legal services',ar:'الخدمات القانونية'},focus:{en:'careful research and document review',ar:'البحث الدقيق ومراجعة المستندات'},outcome:{en:'responsible legal support',ar:'الدعم القانوني المسؤول'}}
];
const general: Career = {match:/.*/,name:{en:'professional work',ar:'العمل المهني'},focus:{en:'organized work and clear communication',ar:'تنظيم العمل والتواصل الواضح'},outcome:{en:'teamwork and practical results',ar:'العمل الجماعي والنتائج العملية'}};

function cvLanguage(): Lang {
  return document.querySelector('.cv-sheet')?.getAttribute('dir') === 'rtl' || document.documentElement.dir === 'rtl' ? 'ar' : 'en';
}
function isSummary(target: EventTarget | null): target is HTMLTextAreaElement {
  if (!(target instanceof HTMLTextAreaElement) || target.closest('.sirati-summary-assistant')) return false;
  const field = target.closest('.field, label');
  const label = field?.querySelector('label')?.textContent || field?.textContent || '';
  const text = [label, target.id, target.name, target.placeholder, target.getAttribute('aria-label')].join(' ').toLowerCase();
  return /personal summary|professional summary|\bsummary\b|\bprofile\b|\babout me\b|ملخص|نبذة|نبذه/i.test(text)
    && !/description|responsibilit|achievement|المسؤوليات|الإنجازات|الوصف الوظيفي/i.test(text);
}
function storedRole() {
  for (const field of Array.from(document.querySelectorAll<HTMLElement>('.field'))) {
    const label = field.querySelector('label')?.textContent?.toLowerCase().trim() || '';
    if (!/^(role|job title|professional title|position|المسمى الوظيفي|الوظيفة|المهنة|المسمى)$/.test(label)) continue;
    const input = field.querySelector<HTMLInputElement>('input');
    if (input?.value.trim()) return input.value.trim().slice(0, 90);
  }
  return '';
}
function putSummary(field: HTMLTextAreaElement, value: string) {
  Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value')?.set?.call(field, value);
  field.dispatchEvent(new Event('input', {bubbles:true}));
  field.dispatchEvent(new Event('change', {bubbles:true}));
}
function makeSuggestions(job: string, lang: Lang) {
  const career = careers.find(item => item.match.test(job)) || general;
  const name = career === general && lang === 'en' ? job.slice(0,80) : career.name[lang];
  const focus = career.focus[lang], outcome = career.outcome[lang];
  if (lang === 'ar') return [
    'متخصص في مجال ' + name + ' يركز على ' + focus + '، مع الاهتمام بـ' + outcome + ' من خلال العمل المنظم والتواصل الواضح.',
    'مهتم بمجال ' + name + ' ويسعى إلى الإسهام في ' + outcome + '، مع تطوير المعرفة في ' + focus + '.',
    'محترف في مجال ' + name + ' يهتم بـ' + focus + ' ويقدّر العمل الجماعي والتعلم المستمر لتعزيز ' + outcome + '.'
  ];
  const capital = name.charAt(0).toUpperCase() + name.slice(1);
  return [
    capital + ' professional focused on ' + focus + ', emphasizing ' + outcome + ' through clear communication and organized work.',
    'Motivated professional in ' + name + ' interested in ' + focus + ' and committed to contributing to ' + outcome + '.',
    'Detail-oriented professional in ' + name + ' who values collaboration and learning, with a focus on ' + focus + ' to support ' + outcome + '.'
  ];
}
export default function PersonalSummaryPicker() {
  const [enabled,setEnabled] = useState(false);
  const [mount,setMount] = useState<HTMLElement | null>(null);
  const [open,setOpen] = useState(false);
  const [role,setRole] = useState('');
  const [lang,setLang] = useState<Lang>('en');
  const [chosen,setChosen] = useState(0);
  const target = useRef<HTMLTextAreaElement | null>(null);
  useEffect(() => {
    if (!window.location.pathname.includes('/builder')) return;
    setEnabled(true);
    const onFocus = (event: FocusEvent) => {
      if ((event.target as HTMLElement | null)?.closest?.('.sirati-summary-assistant')) return;
      if (!isSummary(event.target)) return;
      const field = event.target.closest('.field') || event.target.parentElement;
      if (!field) return;
      let host = field.querySelector<HTMLElement>(':scope > .sirati-summary-assistant');
      if (!host) { host = document.createElement('div'); host.className = 'sirati-summary-assistant'; field.appendChild(host); }
      if (target.current !== event.target) setOpen(false);
      target.current = event.target;
      setMount(host);
      setLang(cvLanguage());
      const detected = storedRole();
      if (detected) setRole(detected);
    };
    document.addEventListener('focusin',onFocus,true);
    return () => document.removeEventListener('focusin',onFocus,true);
  },[]);
  const options = useMemo(() => role.trim() ? makeSuggestions(role.trim(),lang) : [],[role,lang]);
  if (!enabled || !mount || !target.current) return null;
  const t = lang === 'ar' ? {trigger:'اختيار ملخص مهني جاهز',title:'ملخص مهني حسب الوظيفة',role:'المسمى الوظيفي',placeholder:'مثال: محاسب أو ممرض طوارئ أو مهندس',help:'اختَر الملخص الأنسب وعدّله ليناسب خبرتك الفعلية.',empty:'اكتب المسمى الوظيفي لإظهار 3 ملخصات مقترحة.',use:'استخدم هذا الملخص',close:'إغلاق',confirm:'يوجد ملخص مكتوب بالفعل. هل تريد استبداله بالملخص المختار؟',safety:'هذه نماذج قابلة للتعديل، ولا تُعد إثباتًا لخبرة أو شهادة.'}
  : {trigger:'Choose a ready-made personal summary',title:'Personal summary for your job',role:'Job title',placeholder:'e.g. Accountant, Nurse or Engineer',help:'Select a starting point, then edit it to reflect your real experience.',empty:'Enter a job title to view 3 suggested summaries.',use:'Use this summary',close:'Close',confirm:'Replace the personal summary you have already written?',safety:'These are editable examples, not verified skills, credentials or achievements.'};
  const apply = () => {
    if (!target.current || !options[chosen]) return;
    const current = target.current.value.trim();
    if (current === options[chosen]) {setOpen(false); return;}
    if (current && !window.confirm(t.confirm)) return;
    putSummary(target.current,options[chosen]);
    setOpen(false);
  };
  return createPortal(!open
    ? <button type="button" className="sirati-summary-trigger" onClick={() => {setLang(cvLanguage());setOpen(true);}}>{t.trigger}</button>
    : <section className="sirati-summary-panel" dir={lang === 'ar' ? 'rtl' : 'ltr'} aria-label={t.title}>
        <div className="sirati-summary-head"><strong>{t.title}</strong><button type="button" aria-label={t.close} onClick={() => setOpen(false)}>×</button></div>
        <p>{t.help}</p>
        <label className="sirati-summary-role">{t.role}
          <input value={role} maxLength={90} onChange={e => {setRole(e.target.value);setChosen(0);}} placeholder={t.placeholder}/>
        </label>
        {options.length ? <div className="sirati-summary-choices">{options.map((text,i) =>
          <label key={i} className={chosen===i ? 'is-selected' : ''}>
            <input type="radio" name="sirati-summary-choice" checked={chosen===i} onChange={() => setChosen(i)}/>
            <span>{text}</span>
          </label>
        )}</div> : <p role="status">{t.empty}</p>}
        <div className="sirati-summary-actions">
          <button type="button" disabled={!options.length} onClick={apply}>{t.use}</button>
          <button type="button" onClick={() => setOpen(false)}>{t.close}</button>
        </div>
        <small>{t.safety}</small>
      </section>, mount);
}
'''.lstrip(),encoding="utf-8")
layout = root / "app" / "layout.tsx"
text = layout.read_text(encoding="utf-8")
imp = "import PersonalSummaryPicker from '@/components/PersonalSummaryPicker';\n"
if imp not in text:
    idx = text.find("import ")
    if idx < 0: raise RuntimeError("Layout import anchor missing")
    text = text[:idx] + imp + text[idx:]
if "<PersonalSummaryPicker />" not in text:
    if "</body>" not in text: raise RuntimeError("Layout body anchor missing")
    text = text.replace("</body>","        <PersonalSummaryPicker />\n      </body>",1)
layout.write_text(text,encoding="utf-8")
with (root / "app" / "globals.css").open("a",encoding="utf-8") as f:
    f.write(r'''
/* Inline role-based Personal Summary templates */
.sirati-summary-assistant {margin:8px 0 16px;min-width:0}
.sirati-summary-trigger {display:inline-flex;max-width:100%;padding:9px 13px;min-height:42px;border:1px solid #93c5fd;border-radius:10px;background:#eff6ff;color:#1d4ed8;font:inherit;font-size:13px;font-weight:700;cursor:pointer}
.sirati-summary-panel {display:grid;gap:12px;width:100%;max-width:100%;padding:15px;border:1px solid #dbeafe;border-radius:14px;background:#fff;font-size:13px;color:#0f172a;box-sizing:border-box}
.sirati-summary-panel * {box-sizing:border-box}
.sirati-summary-head,.sirati-summary-actions {display:flex;align-items:center;justify-content:space-between;gap:8px}
.sirati-summary-head strong {font-size:16px}
.sirati-summary-head button {min-width:35px;min-height:35px;border:1px solid #e2e8f0;border-radius:8px;background:#f8fafc;font-size:22px;cursor:pointer}
.sirati-summary-panel p {margin:0;color:#475569;line-height:1.55}
.sirati-summary-role {display:grid;gap:6px;font-weight:650}
.sirati-summary-role input {width:100%;min-height:42px;padding:8px 10px;border:1px solid #cbd5e1;border-radius:8px;background:#fff;color:#0f172a;font:inherit}
.sirati-summary-choices {display:grid;gap:9px}
.sirati-summary-choices label {display:flex;align-items:flex-start;gap:9px;padding:12px;border:1px solid #e2e8f0;border-radius:10px;cursor:pointer}
.sirati-summary-choices label.is-selected {background:#eff6ff;border-color:#93c5fd}
.sirati-summary-choices input {margin-top:3px;flex:0 0 auto;accent-color:#2563eb}
.sirati-summary-choices span {line-height:1.55;min-width:0;overflow-wrap:anywhere}
.sirati-summary-actions {justify-content:flex-start;flex-wrap:wrap}
.sirati-summary-actions button {min-height:40px;padding:8px 12px;border:1px solid #cbd5e1;border-radius:9px;background:#fff;color:#0f172a;font:inherit;font-weight:650;cursor:pointer}
.sirati-summary-actions button:first-child {background:#1d4ed8;border-color:#1d4ed8;color:#fff}
.sirati-summary-actions button:disabled {opacity:.5;cursor:not-allowed}
.sirati-summary-panel small {color:#64748b;line-height:1.5}
@media(max-width:760px) {.sirati-summary-trigger {width:100%;justify-content:center}.sirati-summary-panel {padding:12px}}
''')
print("Applied optional role-aware personal summaries.")
