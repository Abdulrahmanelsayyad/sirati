'use client';

import { useEffect, useId, useMemo, useRef, useState } from 'react';

// Curated titles, not qualifications or claims; selection is always optional.
const JOB_TITLE_GROUPS = `
Developer|Software Developer|Software Engineer|Frontend Developer|Backend Developer|Full Stack Developer|Web Developer|Mobile Developer|Android Developer|iOS Developer|React Developer|JavaScript Developer|TypeScript Developer|Python Developer|Java Developer|PHP Developer|WordPress Developer|.NET Developer|C++ Developer|Game Developer|Embedded Software Engineer|DevOps Engineer|Site Reliability Engineer|Cloud Engineer|Solutions Architect|Software Architect|QA Engineer|Software Tester|Test Automation Engineer|IT Support Specialist|Help Desk Technician|Systems Administrator|Network Engineer|Database Administrator|IT Manager|Technical Support Engineer
Data Analyst|Data Scientist|Data Engineer|Analytics Engineer|Business Intelligence Analyst|Business Intelligence Developer|Machine Learning Engineer|AI Engineer|Research Scientist|Statistician|Cybersecurity Analyst|Security Engineer|Information Security Analyst|Penetration Tester|SOC Analyst|IT Auditor|Cloud Architect|Product Analyst
Registered Nurse|Staff Nurse|Emergency Department Nurse|ICU Nurse|Critical Care Nurse|Operating Room Nurse|Pediatric Nurse|Neonatal Nurse|NICU Nurse|Dialysis Nurse|Oncology Nurse|Mental Health Nurse|Community Health Nurse|Home Health Nurse|School Nurse|Occupational Health Nurse|Infection Control Nurse|Charge Nurse|Nurse Supervisor|Nurse Manager|Nurse Educator|Clinical Nurse Specialist|Nurse Practitioner|Nursing Assistant|Healthcare Assistant|Midwife|Paramedic|Emergency Medical Technician
Physician|General Practitioner|Family Physician|Emergency Physician|Pediatrician|Cardiologist|Neurologist|Psychiatrist|Surgeon|Anesthesiologist|Radiologist|Dermatologist|Dentist|Dental Assistant|Dental Hygienist|Pharmacist|Clinical Pharmacist|Pharmacy Technician|Physiotherapist|Occupational Therapist|Speech Therapist|Respiratory Therapist|Dietitian|Nutritionist|Medical Laboratory Technologist|Laboratory Technician|Radiographer|Sonographer|Optometrist|Psychologist|Social Worker|Infection Prevention Specialist|Patient Safety Specialist|Healthcare Quality Specialist|Medical Coder|Medical Receptionist|Hospital Administrator
Educator|Teacher|Primary School Teacher|Secondary School Teacher|English Teacher|Mathematics Teacher|Science Teacher|Physics Teacher|Chemistry Teacher|Biology Teacher|Arabic Teacher|Special Education Teacher|Early Childhood Educator|Teaching Assistant|University Lecturer|Assistant Professor|Professor|Research Assistant|Academic Advisor|School Counselor|School Principal|Instructional Designer|Corporate Trainer|Learning and Development Specialist|Education Coordinator|ESL Teacher|Tutor|Librarian
Accountant|Senior Accountant|Junior Accountant|General Ledger Accountant|Accounts Payable Accountant|Accounts Receivable Accountant|Cost Accountant|Tax Accountant|Financial Accountant|Management Accountant|Bookkeeper|Auditor|Internal Auditor|External Auditor|Financial Analyst|Finance Manager|Financial Controller|Chief Financial Officer|Treasury Analyst|Credit Analyst|Risk Analyst|Investment Analyst|Bank Teller|Banking Advisor|Payroll Specialist|Tax Consultant|Compliance Officer|Insurance Agent|Actuary
Civil Engineer|Structural Engineer|Mechanical Engineer|Electrical Engineer|Electronics Engineer|Industrial Engineer|Chemical Engineer|Biomedical Engineer|Environmental Engineer|Petroleum Engineer|Process Engineer|Production Engineer|Manufacturing Engineer|Maintenance Engineer|Quality Engineer|Quality Assurance Specialist|Quality Control Inspector|Automation Engineer|Control Systems Engineer|Mechatronics Engineer|HVAC Engineer|Project Engineer|Site Engineer|Planning Engineer|Quantity Surveyor|Land Surveyor|Architect|Interior Designer|BIM Engineer|CAD Technician|Safety Engineer|Health and Safety Officer|Construction Manager
Marketing Specialist|Digital Marketing Specialist|Marketing Manager|SEO Specialist|SEM Specialist|Social Media Manager|Social Media Specialist|Content Creator|Content Writer|Copywriter|Technical Writer|Content Strategist|Brand Manager|Product Marketing Manager|Performance Marketing Specialist|Email Marketing Specialist|Public Relations Specialist|Communications Manager|Market Research Analyst|Growth Manager|Graphic Designer|UI Designer|UX Designer|UI/UX Designer|Product Designer|UX Researcher|Art Director|Creative Director|Motion Designer|Animator|Illustrator|Video Editor|Photographer|Videographer
Sales Representative|Sales Executive|Sales Manager|Sales Engineer|Account Executive|Account Manager|Key Account Manager|Business Development Representative|Business Development Manager|Retail Sales Associate|Store Manager|Cashier|Customer Service Representative|Customer Support Specialist|Customer Success Manager|Call Center Agent|Contact Center Supervisor|Client Relations Specialist|Technical Account Manager|Real Estate Agent|Property Manager|Merchandiser|E-commerce Specialist
Human Resources Specialist|HR Coordinator|HR Manager|HR Business Partner|Recruiter|Technical Recruiter|Talent Acquisition Specialist|Employee Relations Specialist|Compensation and Benefits Specialist|Administrative Assistant|Executive Assistant|Office Manager|Receptionist|Data Entry Clerk|Document Controller|Operations Coordinator|Operations Manager|Business Analyst|Management Consultant|Project Coordinator|Project Manager|Program Manager|Product Manager|Product Owner|Scrum Master|Chief Executive Officer|Chief Operating Officer|General Manager
Supply Chain Analyst|Supply Chain Manager|Logistics Coordinator|Logistics Manager|Procurement Specialist|Procurement Manager|Purchasing Officer|Warehouse Associate|Warehouse Supervisor|Warehouse Manager|Inventory Controller|Demand Planner|Supply Planner|Shipping Coordinator|Customs Clearance Specialist|Fleet Manager|Delivery Driver|Truck Driver|Dispatcher|Forklift Operator
Hotel Manager|Front Desk Agent|Guest Relations Officer|Reservation Agent|Concierge|Housekeeping Supervisor|Housekeeper|Restaurant Manager|Chef|Sous Chef|Pastry Chef|Cook|Barista|Waiter|Bartender|Food and Beverage Manager|Travel Consultant|Tour Guide|Event Coordinator|Event Manager|Flight Attendant|Pilot|Ground Services Agent
Lawyer|Legal Counsel|Paralegal|Legal Assistant|Contract Specialist|Policy Analyst|Translator|Interpreter|Journalist|Editor|Proofreader|Researcher|Community Manager|Program Officer|Fundraising Officer|Monitoring and Evaluation Specialist|Sustainability Specialist|Environmental Scientist|Agronomist|Veterinarian|Veterinary Technician
Electrician|Plumber|Carpenter|Welder|Mechanic|Automotive Technician|HVAC Technician|Maintenance Technician|Machine Operator|Production Operator|Assembly Technician|Painter|Security Guard|Security Supervisor|Fitness Trainer|Personal Trainer|Sports Coach|Beauty Therapist|Hair Stylist|Tailor|Cleaner
ممرض مسجل|أخصائي تمريض|ممرض طوارئ|ممرض عناية مركزة|مشرف تمريض|مدير تمريض|أخصائي مكافحة عدوى
طبيب عام|صيدلي|أخصائي علاج طبيعي
معلم
محاسب|محاسب تكاليف|محلل مالي
مطور برمجيات|مهندس برمجيات|مطور واجهات أمامية|مطور مواقع|محلل بيانات|مهندس بيانات
مصمم جرافيك|مصمم تجربة المستخدم
مهندس مدني|مهندس كهرباء|مهندس ميكانيكا
مدير مشروع
أخصائي موارد بشرية|أخصائي تسويق|ممثل خدمة عملاء|مندوب مبيعات|مساعد إداري
مدير عمليات
أمين مخزن
محامي
مترجم
`.trim().split('\n').map(line => line.split('|').filter(Boolean));
export const JOB_TITLES = Array.from(new Set(JOB_TITLE_GROUPS.flat()));
const normalize = (value: string) => value.normalize('NFKD').replace(/[\u0300-\u036f\u064b-\u065f]/g, '').toLowerCase().replace(/[أإآ]/g, 'ا').replace(/[^\p{L}\p{N}+#]+/gu, ' ').trim();
type TitleChoice = { title: string; kind: 'match' | 'related' };
const INDEX = JOB_TITLE_GROUPS.flatMap((titles, group) => titles.map(title => ({ title, text: normalize(title), group })));
const PAGE_SIZE = 6;
const MAX_CHOICES = 48;

function rankedMatches(value: string) {
  const query = normalize(value);
  if (query.length < 3) return [];
  const terms = query.split(/\s+/);
  return INDEX.filter(({text}) => terms.every(term => text.split(' ').some(word => word.startsWith(term))))
    .sort((a, b) => {
      const score = (text: string) => text === query ? 0 : text.startsWith(query) ? 1 : 2;
      return score(a.text) - score(b.text);
    });
}

// Keep a ranked strict-match shortlist for existing clients.
export function suggestJobTitles(value: string): string[] {
  return rankedMatches(value).slice(0, 12).map(item => item.title);
}

// Supplement narrow searches with curated titles only from the same job family.
export function browseJobTitles(value: string): TitleChoice[] {
  const matches = rankedMatches(value);
  if (!matches.length) return [];
  const choices: TitleChoice[] = matches.slice(0, MAX_CHOICES).map(item => ({title: item.title, kind: 'match'}));
  if (matches.length >= 12) return choices;
  const seen = new Set(choices.map(item => item.title));
  for (const item of INDEX) {
    if (item.group !== matches[0].group || seen.has(item.title)) continue;
    choices.push({title: item.title, kind: 'related'});
    seen.add(item.title);
    if (choices.length >= MAX_CHOICES) break;
  }
  return choices;
}

type Props = { value: string; onChange: (value: string) => void; label: string; placeholder?: string };
export default function JobTitleInput({ value, onChange, label, placeholder }: Props) {
  const id = useId();
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(-1);
  const [page, setPage] = useState(0);
  const [composing, setComposing] = useState(false);
  const list = useRef<HTMLUListElement>(null);
  const options = useMemo(() => browseJobTitles(value), [value]);
  const pages = Math.ceil(options.length / PAGE_SIZE);
  const visibleOptions = options.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);
  const arabicUi = /[\u0600-\u06ff]/.test(label);
  const visible = open && !composing && normalize(value).length >= 3;
  useEffect(() => { setActive(-1); setPage(0); }, [value]);
  useEffect(() => { list.current?.children[active]?.scrollIntoView({ block: 'nearest' }); }, [active]);
  const choose = (title: string) => { onChange(title); setOpen(false); setActive(-1); };
  return <div className="field" style={{position:'relative', minWidth:0}}>
    <label htmlFor={id}>{label}</label>
    <input id={id} value={value} placeholder={placeholder} autoComplete="off" role="combobox"
      aria-autocomplete="list" aria-expanded={visible && options.length > 0} aria-controls={visible && options.length ? `${id}-list` : undefined}
      aria-activedescendant={visible && visibleOptions[active] ? `${id}-${active}` : undefined} aria-describedby={`${id}-help`}
      onChange={e => { onChange(e.target.value); setPage(0); setActive(-1); setOpen(true); }}
      onFocus={() => setOpen(true)} onBlur={e => { if (e?.relatedTarget && e.currentTarget.parentElement?.contains(e.relatedTarget as Node)) return; setOpen(false); setActive(-1); }}
      onCompositionStart={() => setComposing(true)} onCompositionEnd={() => setComposing(false)}
      onKeyDown={e => {
        if (e.nativeEvent.isComposing || composing) return;
        if (e.key === 'Escape') { setOpen(false); setActive(-1); return; }
        if (e.key === 'Tab') { setOpen(false); return; }
        if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && visibleOptions.length) {
          e.preventDefault(); setOpen(true);
          setActive(current => e.key === 'ArrowDown' ? (current + 1) % visibleOptions.length : (current <= 0 ? visibleOptions.length - 1 : current - 1));
        } else if (e.key === 'Enter' && visible && visibleOptions[active]) { e.preventDefault(); choose(visibleOptions[active].title); }
      }} />
    <span className="field-help" id={`${id}-help`}>{arabicUi ? 'اكتب 3 أحرف أو أكثر، ويمكنك كتابة أي مسمى بنفسك.' : 'Type 3+ letters for job titles, or write your own.'}</span>
    {visible && <div style={{position:'absolute',top:'100%',insetInline:0,zIndex:40,background:'#fff',color:'#172b4d',border:'1px solid #cbd5e1',borderRadius:12,boxShadow:'0 12px 28px #0f172a26',overflow:'hidden'}}>
      {options.length ? <>
        <ul ref={list} id={`${id}-list`} role="listbox" aria-label={`${label} suggestions`} style={{listStyle:'none',margin:0,padding:4,maxHeight:300,overflowY:'auto',overscrollBehavior:'contain'}}>
          {visibleOptions.map(({title,kind}, i) => <li key={title} id={`${id}-${i}`} role="option" aria-selected={i === active}
            onMouseDown={e => e.preventDefault()} onClick={() => choose(title)}
            style={{padding:'11px 12px',minHeight:44,boxSizing:'border-box',borderRadius:8,cursor:'pointer',overflowWrap:'anywhere',background:i === active ? '#e0f2fe' : 'transparent',fontWeight:i === active ? 600 : 400}}>
            {title}{kind === 'related' && <span style={{fontSize:11,marginInlineStart:8,color:'#52657b'}}>{arabicUi ? 'مرتبط بالمجال' : 'Related role'}</span>}
          </li>)}
        </ul>
        {pages > 1 && <div style={{display:'flex',gap:8,alignItems:'center',justifyContent:'space-between',borderTop:'1px solid #e2e8f0',padding:'8px 12px'}}>
          <span style={{fontSize:12,color:'#52657b'}}>{page * PAGE_SIZE + 1}–{Math.min((page + 1) * PAGE_SIZE, options.length)} / {options.length}</span>
          <button type="button" data-job-title-more="true"
            onMouseDown={e => e.preventDefault()} onBlur={() => { setOpen(false); setActive(-1); }}
            onClick={() => { setPage(current => (current + 1) % pages); setActive(-1); if (list.current) list.current.scrollTop = 0; }}
            style={{minHeight:40,padding:'7px 12px',border:'1px solid #cbd5e1',borderRadius:8,background:'#f8fafc',color:'#172b4d',fontWeight:600,cursor:'pointer'}}>
            {arabicUi ? '↻ اقتراحات أخرى' : '↻ More suggestions'}
          </button>
        </div>}
      </> : <p style={{padding:12,margin:0}}>{arabicUi ? 'لا توجد نتائج مطابقة. يمكنك الاحتفاظ بالمسمى الذي كتبته.' : 'No matching titles. You can keep your own wording.'}</p>}
    </div>}
    <span role="status" aria-live="polite" style={{position:'absolute',width:1,height:1,overflow:'hidden',clipPath:'inset(50%)'}}>
      {visible ? (arabicUi ? `${visibleOptions.length} اقتراحات ظاهرة من أصل ${options.length}. استخدم الأسهم ثم Enter للاختيار.` : `${visibleOptions.length} of ${options.length} suggestions shown. Use arrow keys and Enter, or request more suggestions.`) : ''}
    </span>
  </div>;
}
