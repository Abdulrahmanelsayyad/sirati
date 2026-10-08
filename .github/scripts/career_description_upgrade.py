"""Move Sirati suggestions into the experience field and support non-nursing roles.

Runs after experience_description_picker.py. No paid API, database or auth changes.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
builder = root / "app" / "builder" / "page.tsx"
source = builder.read_text(encoding="utf-8")
source = source.replace("import NursingSmartLibrary from '@/components/NursingSmartLibrary';\n", "")
import re
source, removed = re.subn(
    r'^[ \t]*<NursingSmartLibrary data=\{data\} setData=\{setData\} language=\{language\} />\s*\n',
    "", source, flags=re.MULTILINE
)
if removed != 1:
    raise RuntimeError("Expected one standalone Smart Nursing widget in Builder")
builder.write_text(source, encoding="utf-8")

component = root / "components" / "ExperienceDescriptionPicker.tsx"
text = component.read_text(encoding="utf-8")

def replace(old, new):
    global text
    if text.count(old) != 1:
        raise RuntimeError("Experience assistant patch anchor changed: " + old[:90])
    text = text.replace(old, new, 1)

replace("import { useEffect, useMemo, useRef, useState } from 'react';",
        "import { useEffect, useMemo, useRef, useState } from 'react';\nimport { createPortal } from 'react-dom';")

# A conservative offline content library: user confirms each factual statement.
# Match explicit job words only; unknown jobs get neutral editable suggestions.
careers = r'''
type CareerText = { en: string; ar: string };
type Career = { id: string; pattern: RegExp; label: CareerText; bullets: CareerText[] };
const CAREERS: Career[] = [
  { id: 'accounting', pattern: /accountant|accounting|bookkeep|محاسب|محاسبه|حسابات/i,
    label: { en: 'Accounting', ar: 'المحاسبة' }, bullets: [
      { en: 'Prepared and reconciled financial records and transaction reports.', ar: 'إعداد ومطابقة السجلات المالية وتقارير المعاملات.' },
      { en: 'Reviewed invoices and supporting documents for accuracy.', ar: 'مراجعة الفواتير والمستندات الداعمة للتحقق من دقتها.' },
      { en: 'Maintained organized records to support month-end reporting.', ar: 'تنظيم السجلات لدعم إعداد التقارير المالية الدورية.' }] },
  { id: 'software', pattern: /developer|programmer|software|full.stack|frontend|backend|مبرمج|مطو.?ر برمج|برمجيات/i,
    label: { en: 'Software development', ar: 'تطوير البرمجيات' }, bullets: [
      { en: 'Developed and maintained application features based on documented requirements.', ar: 'تطوير وصيانة خصائص التطبيقات وفق المتطلبات الموثقة.' },
      { en: 'Investigated defects and tested fixes before release.', ar: 'فحص أخطاء البرمجيات واختبار الإصلاحات قبل الإصدار.' },
      { en: 'Collaborated with colleagues on code reviews and technical documentation.', ar: 'التعاون في مراجعة الشفرة البرمجية والتوثيق التقني.' }] },
  { id: 'engineering', pattern: /engineer|هندس|مهندس/i,
    label: { en: 'Engineering', ar: 'الهندسة' }, bullets: [
      { en: 'Reviewed technical specifications and documented project requirements.', ar: 'مراجعة المواصفات الفنية وتوثيق متطلبات المشاريع.' },
      { en: 'Coordinated project tasks with technical and operational teams.', ar: 'تنسيق مهام المشروع مع الفرق الفنية والتشغيلية.' },
      { en: 'Monitored work quality and reported technical issues for resolution.', ar: 'متابعة جودة التنفيذ والإبلاغ عن المشكلات الفنية لمعالجتها.' }] },
  { id: 'teaching', pattern: /teacher|educator|instructor|مدرس|معلم|معلمه|معلمة|تدريس/i,
    label: { en: 'Education', ar: 'التعليم' }, bullets: [
      { en: 'Planned lessons aligned with learning objectives and student needs.', ar: 'تخطيط الدروس وفق أهداف التعلم واحتياجات الطلاب.' },
      { en: 'Assessed learner progress and provided constructive feedback.', ar: 'تقييم تقدم المتعلمين وتقديم تغذية راجعة بنّاءة.' },
      { en: 'Maintained organized instructional records and classroom materials.', ar: 'تنظيم سجلات التدريس والمواد التعليمية.' }] },
  { id: 'sales', pattern: /sales|salesperson|account executive|مبيعات|مندوب بيع|مندوب مبيعات/i,
    label: { en: 'Sales', ar: 'المبيعات' }, bullets: [
      { en: 'Identified customer requirements and presented suitable product options.', ar: 'تحديد احتياجات العملاء وعرض خيارات المنتجات المناسبة.' },
      { en: 'Followed up on customer inquiries and maintained sales records.', ar: 'متابعة استفسارات العملاء وتنظيم سجلات المبيعات.' },
      { en: 'Collaborated with the team to improve the customer buying experience.', ar: 'التعاون مع الفريق لتحسين تجربة الشراء.' }] },
  { id: 'marketing', pattern: /marketing|seo|content creator|marketer|تسويق|مسوق|محتوى تسويقي/i,
    label: { en: 'Marketing', ar: 'التسويق' }, bullets: [
      { en: 'Coordinated marketing content across relevant communication channels.', ar: 'تنسيق المحتوى التسويقي عبر قنوات التواصل المناسبة.' },
      { en: 'Reviewed campaign performance and documented improvement ideas.', ar: 'مراجعة أداء الحملات وتوثيق أفكار التحسين.' },
      { en: 'Collaborated on audience research and campaign planning.', ar: 'المشاركة في دراسة الجمهور وتخطيط الحملات.' }] },
  { id: 'hr', pattern: /human resources|recruiter|recruitment|people operations|موارد بشريه|موارد بشرية|توظيف/i,
    label: { en: 'Human resources', ar: 'الموارد البشرية' }, bullets: [
      { en: 'Coordinated recruitment and candidate communication activities.', ar: 'تنسيق أنشطة التوظيف والتواصل مع المرشحين.' },
      { en: 'Maintained confidential personnel records in accordance with policy.', ar: 'حفظ ملفات الموظفين بسرية وفق السياسات.' },
      { en: 'Supported onboarding and internal employee queries.', ar: 'دعم استقبال الموظفين الجدد والرد على استفساراتهم.' }] },
  { id: 'customer-service', pattern: /customer service|customer support|call center|help desk|خدمه عملاء|خدمة عملاء|كول سنتر|دعم فني/i,
    label: { en: 'Customer service', ar: 'خدمة العملاء' }, bullets: [
      { en: 'Responded to customer inquiries and documented service requests.', ar: 'الرد على استفسارات العملاء وتوثيق طلبات الخدمة.' },
      { en: 'Resolved routine concerns or escalated them through approved channels.', ar: 'حل المشكلات المعتادة أو تصعيدها عبر القنوات المعتمدة.' },
      { en: 'Communicated clearly with customers and relevant internal teams.', ar: 'التواصل بوضوح مع العملاء والفرق الداخلية المعنية.' }] },
  { id: 'administration', pattern: /administrator|administrative|office manager|secretary|executive assistant|اداري|إداري|سكرتير|مساعد اداري/i,
    label: { en: 'Administration', ar: 'الإدارة' }, bullets: [
      { en: 'Organized schedules, correspondence and office documentation.', ar: 'تنظيم المواعيد والمراسلات والمستندات المكتبية.' },
      { en: 'Coordinated administrative requests with relevant departments.', ar: 'تنسيق الطلبات الإدارية مع الأقسام المعنية.' },
      { en: 'Maintained accurate records and followed established workflows.', ar: 'الاحتفاظ بسجلات دقيقة واتباع إجراءات العمل المعتمدة.' }] },
  { id: 'logistics', pattern: /logistics|warehouse|supply chain|inventory|procurement|لوجست|مخازن|مستودع|مشتريات|سلسلة امداد/i,
    label: { en: 'Logistics and supply', ar: 'اللوجستيات والإمداد' }, bullets: [
      { en: 'Tracked inventory movements and maintained stock records.', ar: 'متابعة حركة المخزون والحفاظ على سجلاته.' },
      { en: 'Coordinated incoming and outgoing orders with relevant teams.', ar: 'تنسيق الطلبات الواردة والصادرة مع الفرق المعنية.' },
      { en: 'Reported discrepancies and supported timely issue resolution.', ar: 'الإبلاغ عن فروقات المخزون والمساعدة في معالجتها.' }] },
  { id: 'design', pattern: /graphic design|visual designer|ui.?ux|product designer|مصمم|تصميم جرافيك|تصميم واجهات/i,
    label: { en: 'Design', ar: 'التصميم' }, bullets: [
      { en: 'Created design materials based on project briefs and feedback.', ar: 'إعداد مواد تصميمية وفق متطلبات المشروع والملاحظات.' },
      { en: 'Prepared and revised visual assets for appropriate delivery formats.', ar: 'تجهيز وتعديل العناصر البصرية بصيغ مناسبة للتسليم.' },
      { en: 'Collaborated with stakeholders to refine design requirements.', ar: 'التعاون مع أصحاب المصلحة لتحسين متطلبات التصميم.' }] },
  { id: 'physician', pattern: /doctor|physician|medical officer|طبيب|دكتور|طبيبه|طبيبة/i,
    label: { en: 'Medicine', ar: 'الطب' }, bullets: [
      { en: 'Assessed patients and documented findings within professional scope.', ar: 'تقييم المرضى وتوثيق النتائج في حدود نطاق الممارسة المهنية.' },
      { en: 'Coordinated care plans with the multidisciplinary healthcare team.', ar: 'تنسيق خطط الرعاية مع الفريق الصحي متعدد التخصصات.' },
      { en: 'Communicated clinical updates and escalated concerns appropriately.', ar: 'نقل المستجدات السريرية وتصعيد المخاوف بالشكل المناسب.' }] },
  { id: 'pharmacy', pattern: /pharmacist|pharmacy|صيدلي|صيدلة/i,
    label: { en: 'Pharmacy', ar: 'الصيدلة' }, bullets: [
      { en: 'Reviewed medication orders within assigned professional responsibilities.', ar: 'مراجعة طلبات الأدوية في حدود المسؤوليات المهنية.' },
      { en: 'Provided medication-related information according to approved procedures.', ar: 'تقديم المعلومات المتعلقة بالأدوية وفق الإجراءات المعتمدة.' },
      { en: 'Maintained accurate medication or inventory documentation.', ar: 'الاحتفاظ بتوثيق دقيق للأدوية أو المخزون.' }] },
  { id: 'laboratory', pattern: /laboratory|lab technician|lab technologist|تحاليل|مختبر|معمل/i,
    label: { en: 'Laboratory', ar: 'المختبرات' }, bullets: [
      { en: 'Processed laboratory specimens following established procedures.', ar: 'التعامل مع عينات المختبر وفق الإجراءات المعتمدة.' },
      { en: 'Recorded results and reported irregularities through approved channels.', ar: 'تسجيل النتائج والإبلاغ عن الحالات غير المعتادة عبر القنوات المعتمدة.' },
      { en: 'Maintained equipment and work-area readiness within assigned duties.', ar: 'المحافظة على جاهزية الأجهزة ومكان العمل ضمن المهام المحددة.' }] },
  { id: 'hospitality', pattern: /hotel|hospitality|receptionist|chef|cook|restaurant|فندق|استقبال فندقي|شيف|طباخ|مطعم/i,
    label: { en: 'Hospitality', ar: 'الضيافة' }, bullets: [
      { en: 'Responded to guest requests and coordinated service delivery.', ar: 'الاستجابة لطلبات الضيوف وتنسيق تقديم الخدمة.' },
      { en: 'Followed workplace hygiene, quality and safety procedures.', ar: 'اتباع إجراءات النظافة والجودة والسلامة في العمل.' },
      { en: 'Supported team operations during busy service periods.', ar: 'دعم عمليات الفريق خلال فترات ضغط العمل.' }] },
  { id: 'legal', pattern: /lawyer|legal counsel|paralegal|attorney|محام|قانوني|قانونية/i,
    label: { en: 'Legal services', ar: 'الخدمات القانونية' }, bullets: [
      { en: 'Reviewed case documents and organized relevant records.', ar: 'مراجعة مستندات القضايا وتنظيم السجلات ذات الصلة.' },
      { en: 'Prepared correspondence and documents under applicable procedures.', ar: 'إعداد المراسلات والمستندات وفق الإجراءات المطبقة.' },
      { en: 'Coordinated updates and deadlines with relevant parties.', ar: 'تنسيق المستجدات والمواعيد مع الأطراف المعنية.' }] },
];
const FALLBACK: Career = {
  id: 'general', pattern: /./, label: { en: 'General work experience', ar: 'خبرة عمل عامة' },
  bullets: [
    { en: 'Organized assigned tasks and followed applicable workplace procedures.', ar: 'تنظيم المهام الموكلة واتباع إجراءات العمل المعتمدة.' },
    { en: 'Communicated progress and relevant updates to colleagues or supervisors.', ar: 'إبلاغ الزملاء أو المشرفين بتقدم العمل والمستجدات ذات الصلة.' },
    { en: 'Maintained accurate documentation related to assigned responsibilities.', ar: 'الحفاظ على توثيق دقيق للمسؤوليات الموكلة.' }
  ]
};
function isNursingJob(role: string) {
  return /nurs|ممرض|ممرضة|تمريض|(?:\ber\b|\bicu\b|\bor\b)\s+supervisor/i.test(role);
}
function careerFor(role: string) {
  return CAREERS.find((career) => career.pattern.test(role)) || FALLBACK;
}
'''
replace("const SPECIALTY_PATTERNS:", careers + "\nconst SPECIALTY_PATTERNS:")

replace("  const [autoOpen, setAutoOpen] = useState(true);\n", "  const [slot, setSlot] = useState<HTMLElement | null>(null);\n")
replace("    const savedAutoOpen = sessionStorage.getItem('sirati.experiencePicker.autoOpen');\n", "")
replace("    if (savedAutoOpen === '0') setAutoOpen(false);\n", "")
replace("      targetRef.current = target;\n      const role = nearbyRole(target);",
        """      const isNewTarget = targetRef.current !== target;
      targetRef.current = target;
      const role = nearbyRole(target);
      const field = target.closest('.field') || target.parentElement || target;
      let anchor = field.querySelector<HTMLElement>(':scope > .sirati-description-assistant-slot');
      if (!anchor) {
        anchor = document.createElement('div');
        anchor.className = 'sirati-description-assistant-slot';
        field.appendChild(anchor);
      }
      setSlot(anchor);
      if (isNewTarget) setOpen(false);""")
replace("if (element?.closest('.experience-picker')) return;",
        "if (element?.closest('.experience-picker, .experience-picker-trigger')) return;")
replace("      if (autoOpen) setOpen(true);\n", "")
replace("  }, [autoOpen]);", "  }, []);")
replace("  const specialty = useMemo(() => getSpecialty(specialtyId), [specialtyId]);",
        """  const specialty = useMemo(() => getSpecialty(specialtyId), [specialtyId]);
  const nursingRole = isNursingJob(detectedRole);
  const career = useMemo(() => careerFor(detectedRole), [detectedRole]);""")
replace("    const specialtyItems: Suggestion[] = specialty.bullets.map((item, index) => ({",
        "    const specialtyItems: Suggestion[] = (nursingRole ? specialty.bullets : career.bullets).map((item, index) => ({")
replace("      id: 'specialty-' + specialty.id + '-' + index,",
        "      id: 'career-' + (nursingRole ? specialty.id : career.id) + '-' + index,")
replace("    const levelItems: Suggestion[] = LEVEL_EXTRAS[level].map((item, index) => ({",
        "    const levelItems: Suggestion[] = (nursingRole ? LEVEL_EXTRAS[level] : []).map((item, index) => ({")
replace("  }, [specialty, level, language]);",
        "  }, [specialty, career, nursingRole, level, language]);")
replace("  if (!enabled || !targetRef.current) return null;",
        "  if (!enabled || !targetRef.current || !detectedRole.trim() || !slot) return null;")
replace("        trigger: 'اقتراحات Description',\n        title: 'Experience Description Pro',",
        "        trigger: 'اقتراحات Description',\n        title: 'اقتراحات للوصف الوظيفي',")
replace("        trigger: 'Description suggestions',\n        title: 'Experience Description Pro',",
        "        trigger: 'Description suggestions',\n        title: 'Job description suggestions',")
replace("        trigger: 'اقتراحات Description',", "        trigger: 'اختيار وصف جاهز لهذه الوظيفة',")
replace("        trigger: 'Description suggestions',", "        trigger: 'Choose job description examples',")
replace("    return (\n      <button\n        type=\"button\"\n        className={'experience-picker-trigger experience-picker-trigger--' + side}",
        "    return createPortal(\n      <button\n        type=\"button\"\n        className={'experience-picker-trigger experience-picker-trigger--' + side}")
replace("      </button>\n    );\n  }\n\n  const selectedItems = ",
        "      </button>, slot\n    );\n  }\n\n  const selectedItems = ")
replace("  return (\n    <aside className={'experience-picker experience-picker--' + side}",
        "  return createPortal(\n    <aside className={'experience-picker experience-picker--' + side}")
replace("          <small>SIRATI EXPERIENCE PRO</small>", "          <small>SIRATI SMART CV</small>")
replace("      <div className=\"experience-picker__selectors\">",
        "      {nursingRole && <div className=\"experience-picker__selectors\">")
replace("      </div>\n\n      <label className=\"experience-picker__search\">",
        "      </div>}\n\n      <label className=\"experience-picker__search\">")
replace("      <label className=\"experience-picker__auto-open\">", "      {/* Auto-open is intentionally removed: show suggestions only on request. */}\n      {false && <label className=\"experience-picker__auto-open\">")
replace("            setAutoOpen(event.target.checked);\n            sessionStorage.setItem('sirati.experiencePicker.autoOpen', event.target.checked ? '1' : '0');",
        "            /* no automatic panel opening */")
replace("          checked={autoOpen}", "          checked={false}")
replace("      </label>\n\n      <p className=\"experience-picker__manual\">",
        "      </label>}\n\n      <p className=\"experience-picker__manual\">")
replace("    </aside>\n  );\n}", "    </aside>, slot\n  );\n}")
replace("    clinical: { en: 'Clinical care', ar: 'الرعاية السريرية' },",
        "    clinical: { en: 'Job duties', ar: 'المهام الوظيفية' },")
component.write_text(text, encoding="utf-8")

css_path = root / "app" / "globals.css"
css = css_path.read_text(encoding="utf-8")
css += r'''
/* Contextual career descriptions: no floating overlays. */
.sirati-description-assistant-slot { margin: 8px 0 18px; min-width: 0; }
.sirati-description-assistant-slot .experience-picker-trigger {
  position: static; inset: auto; display: inline-flex; align-items: center;
  min-height: 40px; box-shadow: none; max-width: 100%; white-space: normal;
}
.sirati-description-assistant-slot .experience-picker {
  position: static; inset: auto; width: 100%; max-height: min(520px, 75vh);
  margin: 0; box-shadow: none; border-radius: 14px; z-index: auto;
}
@media(max-width: 760px) {
  .sirati-description-assistant-slot .experience-picker,
  .sirati-description-assistant-slot .experience-picker-trigger {
    position: static; inset: auto; width: 100%; max-width: 100%;
  }
}
'''
css_path.write_text(css, encoding="utf-8")
print("Applied contextual career descriptions and hid standalone Nursing library")
