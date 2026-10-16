'use client';

import { useEffect, useId, useMemo, useRef, useState } from 'react';

// Curated titles, not qualifications or claims; selection is always optional.
export const JOB_TITLES = Array.from(new Set(`
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
ممرض مسجل|أخصائي تمريض|ممرض طوارئ|ممرض عناية مركزة|مشرف تمريض|مدير تمريض|أخصائي مكافحة عدوى|طبيب عام|صيدلي|أخصائي علاج طبيعي|معلم|محاسب|محاسب تكاليف|محلل مالي|مطور برمجيات|مهندس برمجيات|مطور واجهات أمامية|مطور مواقع|محلل بيانات|مهندس بيانات|مصمم جرافيك|مصمم تجربة المستخدم|مهندس مدني|مهندس كهرباء|مهندس ميكانيكا|مدير مشروع|أخصائي موارد بشرية|أخصائي تسويق|ممثل خدمة عملاء|مندوب مبيعات|مساعد إداري|مدير عمليات|أمين مخزن|محامي|مترجم
`.trim().split(/[|\n]/).filter(Boolean)));
const normalize = (value: string) => value.normalize('NFKD').replace(/[\u0300-\u036f\u064b-\u065f]/g, '').toLowerCase().replace(/[أإآ]/g, 'ا').replace(/[^\p{L}\p{N}+#]+/gu, ' ').trim();
const INDEX = JOB_TITLES.map(title => ({ title, text: normalize(title) }));
export function suggestJobTitles(value: string): string[] {
  const query = normalize(value);
  if (query.length < 3) return [];
  const terms = query.split(/\s+/);
  return INDEX.filter(({text}) => terms.every(term => text.split(' ').some(word => word.startsWith(term))))
    .sort((a, b) => {
      const score = (text: string) => text === query ? 0 : text.startsWith(query) ? 1 : 2;
      return score(a.text) - score(b.text);
    }).slice(0, 12).map(item => item.title);
}

type Props = { value: string; onChange: (value: string) => void; label: string; placeholder?: string };
export default function JobTitleInput({ value, onChange, label, placeholder }: Props) {
  const id = useId();
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(-1);
  const [composing, setComposing] = useState(false);
  const list = useRef<HTMLUListElement>(null);
  const options = useMemo(() => suggestJobTitles(value), [value]);
  const visible = open && !composing && normalize(value).length >= 3;
  useEffect(() => { setActive(-1); }, [value]);
  useEffect(() => { list.current?.children[active]?.scrollIntoView({ block: 'nearest' }); }, [active]);
  const choose = (title: string) => { onChange(title); setOpen(false); setActive(-1); };
  return <div className="field" style={{position:'relative', minWidth:0}}>
    <label htmlFor={id}>{label}</label>
    <input id={id} value={value} placeholder={placeholder} autoComplete="off" role="combobox"
      aria-autocomplete="list" aria-expanded={visible && options.length > 0} aria-controls={visible && options.length ? `${id}-list` : undefined}
      aria-activedescendant={visible && options[active] ? `${id}-${active}` : undefined} aria-describedby={`${id}-help`}
      onChange={e => { onChange(e.target.value); setActive(-1); setOpen(true); }}
      onFocus={() => setOpen(true)} onBlur={() => { setOpen(false); setActive(-1); }}
      onCompositionStart={() => setComposing(true)} onCompositionEnd={() => setComposing(false)}
      onKeyDown={e => {
        if (e.nativeEvent.isComposing || composing) return;
        if (e.key === 'Escape') { setOpen(false); setActive(-1); return; }
        if (e.key === 'Tab') { setOpen(false); return; }
        if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && options.length) {
          e.preventDefault(); setOpen(true);
          setActive(current => e.key === 'ArrowDown' ? (current + 1) % options.length : (current <= 0 ? options.length - 1 : current - 1));
        } else if (e.key === 'Enter' && visible && options[active]) { e.preventDefault(); choose(options[active]); }
      }} />
    <span className="field-help" id={`${id}-help`}>Type 3+ letters for job titles, or write your own.</span>
    {visible && <div style={{position:'absolute',top:'100%',insetInline:0,zIndex:40,background:'#fff',color:'#172b4d',border:'1px solid #cbd5e1',borderRadius:12,boxShadow:'0 12px 28px #0f172a26',overflow:'hidden'}}>
      {options.length ? <ul ref={list} id={`${id}-list`} role="listbox" aria-label={`${label} suggestions`} style={{listStyle:'none',margin:0,padding:4,maxHeight:260,overflowY:'auto',overscrollBehavior:'contain'}}>
        {options.map((title, i) => <li key={title} id={`${id}-${i}`} role="option" aria-selected={i === active}
          onMouseDown={e => e.preventDefault()} onClick={() => choose(title)}
          style={{padding:'11px 12px',minHeight:44,boxSizing:'border-box',borderRadius:8,cursor:'pointer',overflowWrap:'anywhere',background:i === active ? '#e0f2fe' : 'transparent',fontWeight:i === active ? 600 : 400}}>{title}</li>)}
      </ul> : <p style={{padding:12,margin:0}}>No matching titles. You can keep your own wording.</p>}
    </div>}
    <span role="status" aria-live="polite" style={{position:'absolute',width:1,height:1,overflow:'hidden',clipPath:'inset(50%)'}}>
      {visible ? `${options.length} suggestions. Use arrow keys and Enter to select, or keep typing.` : ''}
    </span>
  </div>;
}
