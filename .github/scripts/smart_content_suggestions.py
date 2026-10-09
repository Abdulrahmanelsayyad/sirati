"""Opt-in role-based skills & verifiable achievement prompts beside the Skills field.

Reuses Experience Description Pro V3 for duties, does not clone or replace it.
Builds a single read-only recommendation component that only mutates CvData after
a deliberate user click and confirmation. No AI spend, customer data uploads,
browser storage, authorization or payment changes.
"""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
component = root / "components" / "SmartContentSuggestions.tsx"
component.write_text(r''' 'use client';
import { useEffect, useMemo, useState, type Dispatch, type SetStateAction } from 'react';
import { createPortal } from 'react-dom';
import type { CvData, CvLanguage } from '@/lib/types';

type Local = { en: string; ar: string };
type Pack = { match: RegExp; label: Local; skills: Local[]; achievements: Local[] };
const pair = (en: string, ar: string): Local => ({ en, ar });
const PACKS: Pack[] = [
  {match:/\b(icu|intensive care|critical care)\b|عناية مركزة|رعاية حرجة/i, label:pair('Critical care nursing','تمريض الرعاية الحرجة'),
   skills:[pair('Patient assessment','تقييم المرضى'),pair('Critical care monitoring','مراقبة الحالات الحرجة'),pair('Structured handovers','تسليم الحالات المنظم'),pair('Clinical documentation','التوثيق السريري'),pair('Safety escalation','تصعيد مخاطر السلامة')],
   achievements:[pair('Improved [actual care workflow] through [action you performed], supported by [verifiable evidence].','تحسين [إجراء رعاية حقيقي] من خلال [الإجراء الذي نفذته] وفق [دليل يمكن التحقق منه].'),pair('Contributed to [verified safety initiative] by [your specific role] with [observed outcome].','المساهمة في [مبادرة سلامة مثبتة] عبر [دورك المحدد] بنتيجة [نتيجة ملحوظة].')]},
  {match:/\b(nurse|nursing|er nurse|ed nurse)\b|تمريض|ممرض|ممرضة|طوارئ/i,label:pair('Nursing','التمريض'),
   skills:[pair('Patient triage','فرز المرضى'),pair('Patient safety','سلامة المرضى'),pair('Clinical handover','تسليم الحالات'),pair('Vital signs monitoring','متابعة العلامات الحيوية'),pair('Clinical documentation','التوثيق السريري')],
   achievements:[pair('Supported [documented clinical improvement] by [actual action] with [verified outcome].','المساهمة في [تحسين سريري موثق] بواسطة [إجراء حقيقي] بنتيجة [نتيجة مثبتة].'),pair('Contributed to [real team initiative] by [your own contribution]; evidence: [source].','المساهمة في [مبادرة فريق حقيقية] عبر [مساهمتك الفعلية]؛ الدليل: [المصدر].')]},
  {match:/software|developer|programmer|مبرمج|مطو.?ر برمج|تطوير برمج/i,label:pair('Software development','تطوير البرمجيات'),
   skills:[pair('Debugging','تصحيح الأخطاء'),pair('Software testing','اختبار البرمجيات'),pair('Version control','إدارة نسخ الشفرة'),pair('Technical documentation','التوثيق التقني'),pair('Code review','مراجعة الشفرة')],
   achievements:[pair('Improved [real application feature] through [tested change], verified using [test evidence].','تحسين [ميزة برمجية حقيقية] عبر [تعديل مختبر] مع التحقق بواسطة [دليل اختبار].'),pair('Resolved [documented defect] by [specific fix] with [observed result].','معالجة [خطأ موثق] باستخدام [الإصلاح المحدد] مع [نتيجة ملحوظة].')]},
  {match:/accountant|accounting|bookkeep|محاسب|حسابات/i,label:pair('Accounting','المحاسبة'),
   skills:[pair('Financial reconciliation','التسويات المالية'),pair('Record accuracy','دقة السجلات'),pair('Invoice review','مراجعة الفواتير'),pair('Financial reporting','التقارير المالية'),pair('Spreadsheet analysis','تحليل الجداول')],
   achievements:[pair('Improved accuracy of [actual report or reconciliation] using [specific verification method]; evidence: [source].','تحسين دقة [تقرير أو تسوية فعلية] باستخدام [طريقة تحقق محددة]؛ الدليل: [المصدر].'),pair('Reduced [verified reporting issue] through [actual corrective action] with [documented result].','تقليل [مشكلة تقارير مثبتة] عبر [إجراء تصحيحي حقيقي] بنتيجة [موثقة].')]},
  {match:/sales|مبيعات|مندوب بيع/i,label:pair('Sales','المبيعات'),
   skills:[pair('Customer needs assessment','تحديد احتياجات العملاء'),pair('Sales follow-up','متابعة المبيعات'),pair('CRM records','سجلات إدارة العملاء'),pair('Product presentation','عرض المنتجات'),pair('Client communication','التواصل مع العملاء')],
   achievements:[pair('Improved [verified customer process] by [real follow-up approach], with [documented result].','تحسين [عملية عملاء موثقة] عبر [أسلوب متابعة حقيقي] بنتيجة [موثقة].'),pair('Helped achieve [verified sales outcome] through [your actual contribution]; evidence: [source].','المساهمة في [نتيجة مبيعات مثبتة] عبر [مساهمتك الفعلية]؛ الدليل: [المصدر].')]},
  {match:/teacher|instructor|educator|مدرس|معلم|معلمة|تدريس/i,label:pair('Education','التعليم'),
   skills:[pair('Lesson planning','تخطيط الدروس'),pair('Learner assessment','تقييم المتعلمين'),pair('Classroom organization','تنظيم الفصل'),pair('Constructive feedback','التغذية الراجعة'),pair('Student communication','التواصل مع الطلاب')],
   achievements:[pair('Improved [observed learning activity] through [teaching method], supported by [assessment evidence].','تحسين [نشاط تعليمي ملحوظ] باستخدام [أسلوب تدريس] وفق [دليل تقييم].'),pair('Supported [verified classroom initiative] by [your contribution] with [observed outcome].','دعم [مبادرة صفية موثقة] عبر [مساهمتك] بنتيجة [ملحوظة].')]},
  {match:/engineer|engineering|مهندس|هندسة/i,label:pair('Engineering','الهندسة'),
   skills:[pair('Technical documentation','التوثيق الفني'),pair('Quality inspections','فحوص الجودة'),pair('Project coordination','تنسيق المشاريع'),pair('Specification review','مراجعة المواصفات'),pair('Risk identification','تحديد المخاطر')],
   achievements:[pair('Resolved [real technical issue] through [documented method] with [verifiable result].','حل [مشكلة فنية حقيقية] بواسطة [طريقة موثقة] بنتيجة [قابلة للتحقق].'),pair('Improved [verified project workflow] by [actual coordination action]; evidence: [source].','تحسين [سير مشروع مثبت] عبر [تنسيق فعلي]؛ الدليل: [المصدر].')]},
  {match:/marketing|seo|تسويق|مسوق/i,label:pair('Marketing','التسويق'),
   skills:[pair('Campaign planning','تخطيط الحملات'),pair('Audience research','دراسة الجمهور'),pair('Performance reporting','تقارير الأداء'),pair('Content coordination','تنسيق المحتوى'),pair('Marketing analytics','تحليل التسويق')],
   achievements:[pair('Improved [actual campaign metric] through [verified change], supported by [analytics evidence].','تحسين [مؤشر حملة حقيقي] عبر [تعديل مثبت] وفق [دليل تحليلي].'),pair('Contributed to [documented campaign outcome] by [your role]; evidence: [source].','المساهمة في [نتيجة حملة موثقة] عبر [دورك]؛ الدليل: [المصدر].')]},
  {match:/human resources|recruit|موارد بشرية|توظيف/i,label:pair('Human resources','الموارد البشرية'),
   skills:[pair('Recruitment coordination','تنسيق التوظيف'),pair('Candidate screening','فرز المرشحين'),pair('Personnel records','سجلات الموظفين'),pair('Onboarding','تهيئة الموظفين'),pair('Confidentiality','السرية')],
   achievements:[pair('Improved [real HR process] through [verified procedural change], supported by [evidence].','تحسين [عملية موارد بشرية حقيقية] عبر [تغيير إجرائي مثبت] وفق [دليل].'),pair('Supported [documented recruitment outcome] by [your actual role] with [verified result].','دعم [نتيجة توظيف موثقة] عبر [دورك الفعلي] بنتيجة [مثبتة].')]},
  {match:/customer service|call center|support agent|خدمة عملاء|كول سنتر/i,label:pair('Customer service','خدمة العملاء'),
   skills:[pair('Case documentation','توثيق الحالات'),pair('Issue resolution','حل المشكلات'),pair('Customer communication','التواصل مع العملاء'),pair('Escalation','تصعيد الطلبات'),pair('Follow-up','المتابعة')],
   achievements:[pair('Improved [verified customer issue process] through [action taken] with [observed outcome].','تحسين [عملية طلبات عملاء مثبتة] عبر [إجراء منفذ] بنتيجة [ملحوظة].'),pair('Helped resolve [documented recurring issue] by [specific intervention]; evidence: [source].','المساهمة في معالجة [مشكلة متكررة موثقة] عبر [تدخل محدد]؛ الدليل: [المصدر].')]},
  {match:/designer|design|ui.?ux|مصمم|تصميم/i,label:pair('Design','التصميم'),
   skills:[pair('Visual hierarchy','التدرج البصري'),pair('Wireframing','تصميم المخططات الأولية'),pair('Accessibility review','مراجعة سهولة الوصول'),pair('Prototyping','إنشاء النماذج'),pair('Design handoff','تسليم التصاميم')],
   achievements:[pair('Improved [tested user journey] using [design change], supported by [research findings].','تحسين [رحلة مستخدم مختبرة] عبر [تغيير تصميم] وفق [نتائج بحث].'),pair('Delivered [verified design outcome] through [your specific contribution]; evidence: [source].','تحقيق [نتيجة تصميم مثبتة] عبر [مساهمتك المحددة]؛ الدليل: [المصدر].')]},
  {match:/logistics|supply chain|warehouse|inventory|مخازن|مستودع|لوجست|مشتريات/i,label:pair('Logistics','اللوجستيات'),
   skills:[pair('Inventory tracking','تتبع المخزون'),pair('Shipment coordination','تنسيق الشحنات'),pair('Record reconciliation','مطابقة السجلات'),pair('Supplier communication','التواصل مع الموردين'),pair('Exception handling','معالجة الاستثناءات')],
   achievements:[pair('Improved [verified inventory process] through [specific action] with [documented outcome].','تحسين [عملية مخزون مثبتة] عبر [إجراء محدد] بنتيجة [موثقة].'),pair('Reduced [documented delivery issue] by [actual coordination change]; evidence: [source].','تقليل [مشكلة تسليم موثقة] عبر [تغيير تنسيقي حقيقي]؛ الدليل: [المصدر].')]},
];
const GENERIC: Pack = {
  match: /./, label:pair('General professional','مهني عام'),
  skills:[pair('Team communication','التواصل مع الفريق'),pair('Task coordination','تنسيق المهام'),pair('Documentation','التوثيق'),pair('Problem solving','حل المشكلات'),pair('Time management','إدارة الوقت')],
  achievements:[pair('Improved [actual work process] through [your specific action], supported by [verifiable result].','تحسين [إجراء عمل حقيقي] عبر [مساهمتك المحددة] مع [نتيجة قابلة للتحقق].'),pair('Contributed to [real documented initiative] by [action you performed]; evidence: [source].','المساهمة في [مبادرة موثقة] عبر [إجراء نفذته]؛ الدليل: [المصدر].')]
};
type Props = { data: CvData; setData: Dispatch<SetStateAction<CvData>>; language: CvLanguage };
export default function SmartContentSuggestions({ data, setData, language }: Props) {
  const [slot, setSlot] = useState<HTMLElement | null>(null);
  const [open, setOpen] = useState(false);
  const [tab, setTab] = useState<'skills'|'achievement'>('skills');
  const [selected, setSelected] = useState<number[]>([]);
  const [draft, setDraft] = useState('');
  const [entry, setEntry] = useState(0);
  const [confirmed, setConfirmed] = useState(false);
  const ar = language === 'ar';
  const role = (data.title || '').trim();
  const pack = useMemo(() => PACKS.find(p => p.match.test(role)) || GENERIC, [role]);
  const suggestions = pack.skills.map(s => s[ar ? 'ar' : 'en']);
  useEffect(() => { setSelected([]); setDraft(''); setConfirmed(false); }, [role, language]);
  useEffect(() => {
    if (typeof window === 'undefined' || !window.location.pathname.includes('/builder')) return;
    const scan = () => {
      const field = Array.from(document.querySelectorAll<HTMLElement>('.wizard-panel .field, .field'))
        .find(el => {
          const label = el.querySelector('label');
          return !!el.querySelector('textarea') && !!label && /^(skills|المهارات)\b|^المهارات/u.test((label.textContent || '').trim());
        });
      if (!field) { setSlot(current => current ? null : current); return; }
      let host = field.querySelector<HTMLElement>(':scope > .sirati-content-slot');
      if (!host) {
        host = document.createElement('div');
        host.className = 'sirati-content-slot';
        field.appendChild(host);
      }
      setSlot(current => current === host ? current : host);
    };
    scan();
    const observer = new MutationObserver(scan);
    observer.observe(document.body, {childList:true, subtree:true});
    return () => observer.disconnect();
  }, []);
  if (!slot) return null;
  const chooseAchievement = (index:number) => {setDraft(pack.achievements[index][ar ? 'ar':'en']);setConfirmed(false);};
  const insertSkills = () => {
    if (!confirmed || !selected.length || !role) return;
    const chosen = selected.map(i => suggestions[i]);
    setData(prev => {
      const existing = prev.skills.split(/[\n,،;]+/).map(x=>x.trim()).filter(Boolean);
      const unique = new Set(existing.map(x=>x.toLocaleLowerCase()));
      const additions = chosen.filter(x => {
        const key=x.toLocaleLowerCase();
        if (unique.has(key)) return false;
        unique.add(key);return true;
      });
      return {...prev, skills:[...existing,...additions].join(prev.skills.includes('\n') ? '\n' : ', ')};
    });
    setSelected([]);setConfirmed(false);setOpen(false);
  };
  const insertAchievement = () => {
    const value = draft.trim();
    if (!role || !confirmed || !data.experience.length || !value || /\[[^\]]+\]/.test(value)) return;
    setData(prev => ({...prev,experience:prev.experience.map((item,i) => {
      if (i !== Math.min(entry,prev.experience.length-1)) return item;
      const existing = item.details.split('\n').map(x=>x.trim());
      if (existing.some(x=>x.toLocaleLowerCase()===value.toLocaleLowerCase())) return item;
      return {...item,details:[item.details.trim(),value].filter(Boolean).join('\n')};
    })}));
    setDraft('');setConfirmed(false);setOpen(false);
  };
  return createPortal(<div className="sirati-content" dir={ar?'rtl':'ltr'}>
    <button type="button" className="sirati-content-trigger" aria-expanded={open}
      onClick={()=>setOpen(v=>!v)}>
      {ar?'✨ اقتراحات محتوى ذكية':'✨ Smart Content Suggestions'}
    </button>
    {open && <section className="sirati-content-panel" aria-label="Smart Content Suggestions">
      <div className="sirati-content-head"><strong>{ar?'محتوى يناسب مسماك الوظيفي':'Suggestions matched to your job title'}</strong>
        <button type="button" aria-label="Close content suggestions" onClick={()=>setOpen(false)}>×</button></div>
      {role ? <p className="sirati-content-role">{role} · {pack.label[ar?'ar':'en']}</p>
        : <p role="status">{ar?'اكتب المسمى الوظيفي أولًا في البيانات الشخصية.':'Enter your Professional Title in Personal Information first.'}</p>}
      {role && <>
        <div className="sirati-content-tabs" role="group" aria-label="Suggestion type">
          <button type="button" aria-pressed={tab==='skills'} onClick={()=>{setTab('skills');setConfirmed(false);}}>{ar?'المهارات':'Skills'}</button>
          <button type="button" aria-pressed={tab==='achievement'} onClick={()=>{setTab('achievement');setConfirmed(false);}}>{ar?'الإنجازات':'Achievements'}</button>
        </div>
        {tab==='skills' ? <div className="sirati-content-options">
          {suggestions.map((skill,i)=><label key={i}><input type="checkbox"
            checked={selected.includes(i)} onChange={()=>{setSelected(v=>v.includes(i)?v.filter(n=>n!==i):[...v,i]);setConfirmed(false);}}/>
            <span>{skill}</span></label>)}
        </div> : <div className="sirati-content-achievements">
          <p>{ar?'اختر مثالًا ثم استبدل كل الخانات بإنجازاتك الفعلية:':'Choose a prompt, then replace every placeholder with your own evidence:'}</p>
          {pack.achievements.map((item,i)=><button type="button" key={i} onClick={()=>chooseAchievement(i)}>
            {item[ar?'ar':'en']}</button>)}
          <label>{ar?'عدّل الإنجاز بنفسك':'Edit your achievement'}
            <textarea aria-label="Edit achievement" value={draft} onChange={e=>{setDraft(e.target.value);setConfirmed(false);}} rows={3}/>
          </label>
          {data.experience.length ? <label>{ar?'إضافة إلى خبرة':'Add to experience'}
            <select aria-label="Achievement target experience" value={Math.min(entry,data.experience.length-1)}
              onChange={e=>setEntry(Number(e.target.value))}>
              {data.experience.map((exp,i)=><option key={exp.id || i} value={i}>{exp.role||exp.company||(ar?'خبرة':'Experience')} #{i+1}</option>)}
            </select></label> : <p role="status">{ar?'أضف خبرة عمل أولًا، ثم أدرج الإنجاز.':'Add a work experience entry before inserting an achievement.'}</p>}
          {draft && /\[[^\]]+\]/.test(draft) && <p className="sirati-content-warning">{ar?'استبدل جميع الخانات بين الأقواس بمعلومات حقيقية أولًا.':'Replace every bracketed placeholder with true details before inserting.'}</p>}
        </div>}
        <p className="sirati-content-advice">{ar?'لوصف الخبرة استخدم «اختيار وصف جاهز لهذه الوظيفة» بجوار خانة Description. لا نُنشئ أرقامًا أو خبرات أو مهارات نيابة عنك.':'For job description examples use the existing Experience Pro beside Description. Never add unverified achievements, skills or metrics.'}</p>
        <label className="sirati-content-confirm"><input type="checkbox" checked={confirmed} onChange={e=>setConfirmed(e.target.checked)}/>
          {ar?'أؤكد أن المحتوى الذي اخترته صحيح ويخص خبرتي.':'I confirm this content truthfully reflects my work.'}</label>
        <button type="button" className="sirati-content-add"
          disabled={!confirmed || (tab==='skills' ? !selected.length : !data.experience.length || !draft.trim() || /\[[^\]]+\]/.test(draft))}
          onClick={tab==='skills'?insertSkills:insertAchievement}>
          {tab==='skills' ? (ar?'إضافة المهارات المختارة':'Add selected skills'):(ar?'إضافة الإنجاز المعدّل':'Add edited achievement')}
        </button>
      </>}
    </section>}
  </div>,slot);
}
''', encoding='utf-8')

builder = root / "app" / "builder" / "page.tsx"
source = builder.read_text(encoding="utf-8")
imp = "import SmartContentSuggestions from '@/components/SmartContentSuggestions';\n"
if imp in source or '<SmartContentSuggestions ' in source:
    raise RuntimeError("Smart Content component already mounted")
if "import CvReadinessCheck from '@/components/CvReadinessCheck';\n" not in source:
    raise RuntimeError("Expected data-driven Builder CV Quality import is missing")
source = source.replace("import CvReadinessCheck from '@/components/CvReadinessCheck';\n",
    "import CvReadinessCheck from '@/components/CvReadinessCheck';\n" + imp, 1)
# Mount in Builder's React tree, but portal only into the active Skills field.
anchor = "<CvReadinessCheck data={data} language={language} />"
if source.count(anchor) != 1:
    raise RuntimeError("Expected single preview Quality widget anchor")
source = source.replace(anchor, anchor + "\n          <SmartContentSuggestions data={data} setData={setData} language={language} />", 1)
builder.write_text(source, encoding="utf-8")

css_path = root / "app" / "globals.css"
css = css_path.read_text(encoding="utf-8")
css += r'''
/* Smart Content: inline, opt-in, keyboard-accessible, mobile-friendly. */
.sirati-content-slot {margin:8px 0 14px;min-width:0;}
.sirati-content {width:100%;max-width:100%;box-sizing:border-box;}
.sirati-content * {box-sizing:border-box;}
.sirati-content button {cursor:pointer;font:inherit;}
.sirati-content button:focus-visible,.sirati-content input:focus-visible,.sirati-content textarea:focus-visible,.sirati-content select:focus-visible {outline:2px solid #146e6a;outline-offset:2px;}
.sirati-content-trigger {min-height:42px;padding:9px 13px;background:#e9f5f1;color:#145a50;border:1px solid #b9dbcf;border-radius:11px;font-weight:700;}
.sirati-content-panel {display:grid;gap:11px;padding:13px;margin-top:9px;border:1px solid #c8d8d4;border-radius:13px;background:#fff;color:#18304a;max-width:100%;font-size:13px;}
.sirati-content-head {display:flex;justify-content:space-between;align-items:center;gap:8px;}
.sirati-content-head button {border:1px solid #cbd5e1;background:#f8fafc;border-radius:8px;min-height:34px;min-width:34px;font-size:20px;}
.sirati-content-role {font-size:12px;color:#285a64;font-weight:650;overflow-wrap:anywhere;}
.sirati-content-tabs {display:flex;flex-wrap:wrap;gap:8px;}
.sirati-content-tabs button {padding:8px 14px;min-height:40px;border:1px solid #cbd5e1;background:white;border-radius:9px;}
.sirati-content-tabs button[aria-pressed="true"] {background:#e1f3ec;color:#145a50;border-color:#639c85;font-weight:700;}
.sirati-content-options {display:grid;grid-template-columns:repeat(auto-fit,minmax(165px,1fr));gap:8px;}
.sirati-content-options label {display:flex;gap:9px;align-items:center;border:1px solid #e0e6e8;border-radius:9px;padding:9px;overflow-wrap:anywhere;cursor:pointer;}
.sirati-content-options input {flex:none;accent-color:#187461;}
.sirati-content-achievements {display:grid;gap:9px;min-width:0;}
.sirati-content-achievements > button {text-align:start;padding:10px;border:1px solid #d7e3df;background:#f6f9f8;border-radius:9px;overflow-wrap:anywhere;}
.sirati-content-achievements label {display:grid;gap:5px;font-weight:650;}
.sirati-content-achievements textarea,.sirati-content-achievements select {min-height:43px;width:100%;padding:9px;border-radius:8px;border:1px solid #cbd5e1;background:white;color:#182d42;font:inherit;overflow-wrap:anywhere;}
.sirati-content-advice {font-size:11px;line-height:1.5;color:#587070;}
.sirati-content-warning {color:#935514;font-size:12px;}
.sirati-content-confirm {display:flex;align-items:start;gap:9px;font-size:12px;}
.sirati-content-confirm input {flex:none;}
.sirati-content-add {min-height:44px;padding:9px 14px;color:white;background:#17564d;border:1px solid #17564d;border-radius:10px;font-weight:700;}
.sirati-content-add:disabled {opacity:.48;cursor:not-allowed;}
@media(max-width:390px){.sirati-content-options {grid-template-columns:1fr;}.sirati-content-panel {padding:10px;}}
@media print {.sirati-content-slot {display:none!important;}}
'''
css_path.write_text(css, encoding="utf-8")
print("Installed role-specific editable skills and achievement prompts into Skills; preserved Experience Pro V3.")
