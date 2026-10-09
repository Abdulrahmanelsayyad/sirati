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

// Advanced optional experience examples; users must select only factual duties.
const ADVANCED_CAREER_BULLETS: Record<string, CareerText[]> = {
  "accounting": [
    { en: "Analyzed ledger reconciliations, investigated posting exceptions and documented adjustments to support reliable month-end reporting.", ar: "تحليل تسويات دفاتر الأستاذ وفحص استثناءات القيود وتوثيق التسويات لدعم تقارير نهاية الشهر بصورة موثوقة." },
    { en: "Reviewed accounts payable and receivable records against supporting evidence and flagged variances for timely resolution.", ar: "مراجعة سجلات الحسابات الدائنة والمدينة مقابل المستندات الداعمة وتحديد الفروقات لمعالجتها في الوقت المناسب." },
    { en: "Prepared audit-ready schedules and explained expense or budget variances in collaboration with relevant departments.", ar: "إعداد جداول قابلة للمراجعة وتوضيح انحرافات المصروفات أو الميزانيات بالتعاون مع الإدارات المعنية." }
  ],
  "software": [
    { en: "Translated documented requirements into maintainable features with defined acceptance criteria and focused regression coverage.", ar: "تحويل المتطلبات الموثقة إلى خصائص برمجية قابلة للصيانة بمعايير قبول محددة واختبارات موجهة لمنع تكرار الأخطاء." },
    { en: "Diagnosed application defects using reproducible cases, logging and root-cause analysis before validating fixes.", ar: "تشخيص الأعطال البرمجية باستخدام خطوات إعادة إنتاج واضحة والسجلات وتحليل الأسباب الجذرية قبل التحقق من الإصلاحات." },
    { en: "Reviewed code for edge cases, accessibility and compatibility while communicating technical trade-offs to stakeholders.", ar: "مراجعة الشفرة للحالات الطرفية وسهولة الوصول والتوافق مع توضيح المفاضلات التقنية لأصحاب المصلحة." }
  ],
  "engineering": [
    { en: "Reviewed drawings, specifications and interface constraints to identify constructability questions and technical dependencies.", ar: "مراجعة الرسومات والمواصفات والقيود الفنية لتحديد استفسارات قابلية التنفيذ والاعتماديات التقنية." },
    { en: "Coordinated technical submittals, inspections and clarification requests with project stakeholders against approved requirements.", ar: "تنسيق الاعتمادات الفنية والفحوص وطلبات التوضيح مع أطراف المشروع وفق المتطلبات المعتمدة." },
    { en: "Documented nonconformities, tracked corrective actions and supported structured technical handovers.", ar: "توثيق حالات عدم المطابقة ومتابعة الإجراءات التصحيحية ودعم عمليات التسليم الفني المنظمة." }
  ],
  "teaching": [
    { en: "Designed differentiated lesson sequences aligned with learning objectives and measurable assessment checkpoints.", ar: "تصميم خطط دروس متمايزة ترتبط بنواتج التعلم ونقاط تقييم قابلة للملاحظة." },
    { en: "Used formative assessment evidence to identify learning gaps and adapt instruction or targeted practice.", ar: "استخدام أدلة التقييم البنائي لتحديد فجوات التعلم وتكييف الشرح أو التدريبات الموجهة." },
    { en: "Provided actionable feedback on learner progress and coordinated suitable support with academic colleagues.", ar: "تقديم تغذية راجعة عملية حول تقدم المتعلمين والتنسيق مع الزملاء الأكاديميين بشأن الدعم المناسب." }
  ],
  "sales": [
    { en: "Qualified opportunities through structured discovery of customer needs, buying constraints and decision criteria.", ar: "تأهيل فرص البيع من خلال استكشاف منظم لاحتياجات العملاء وقيود الشراء ومعايير اتخاذ القرار." },
    { en: "Maintained CRM pipeline records with stakeholder context, next actions and documented follow-up commitments.", ar: "إدارة سجلات الفرص البيعية بنظام CRM مع توثيق أصحاب القرار والخطوات التالية والتزامات المتابعة." },
    { en: "Aligned product recommendations with customer use cases and coordinated accurate handovers to service teams.", ar: "مواءمة توصيات المنتجات مع حالات استخدام العملاء والتنسيق لتسليمات دقيقة لفرق الخدمة." }
  ],
  "marketing": [
    { en: "Created audience-specific campaign briefs linking positioning, channel choices and testable business objectives.", ar: "إعداد موجزات حملات موجهة لشرائح الجمهور تربط الرسائل التسويقية بالقنوات والأهداف القابلة للاختبار." },
    { en: "Evaluated engagement and conversion patterns to propose actionable content and targeting experiments.", ar: "تقييم أنماط التفاعل والتحويل لاقتراح تجارب عملية لتحسين المحتوى والاستهداف." },
    { en: "Coordinated editorial calendars and creative approvals while recording key campaign learnings.", ar: "تنسيق جداول النشر واعتماد المواد الإبداعية مع توثيق الدروس المستفادة من الحملات." }
  ],
  "hr": [
    { en: "Screened candidate evidence against role-specific criteria and organized structured interview handovers.", ar: "فرز مؤهلات المرشحين وفق معايير كل وظيفة وتنظيم تسليمات المقابلات المهيكلة." },
    { en: "Coordinated onboarding milestones, document verification and departmental handoffs under approved HR procedures.", ar: "تنسيق مراحل انضمام الموظفين والتحقق من المستندات والتسليمات بين الإدارات وفق إجراءات الموارد البشرية." },
    { en: "Maintained confidential personnel records and escalated sensitive exceptions through authorized channels.", ar: "إدارة سجلات العاملين السرية وتصعيد الحالات الحساسة عبر القنوات المخولة." }
  ],
  "customer-service": [
    { en: "Managed multi-step customer cases by documenting root concerns, actions taken and clear follow-up ownership.", ar: "إدارة حالات العملاء متعددة المراحل بتوثيق أصل المشكلة والإجراءات المتخذة ومسؤولية المتابعة بوضوح." },
    { en: "Triaged complex service requests, provided context-rich escalations and monitored outstanding resolution actions.", ar: "تصنيف طلبات الخدمة المعقدة وإحالتها بسياق مكتمل ومتابعة إجراءات الحل المعلقة." },
    { en: "Identified recurring support themes and communicated service improvement opportunities to relevant teams.", ar: "تحديد أنماط طلبات الدعم المتكررة وإبلاغ الفرق المعنية بفرص تحسين الخدمة." }
  ],
  "administration": [
    { en: "Coordinated cross-functional schedules, approvals and action trackers across competing operational priorities.", ar: "تنسيق الجداول والموافقات وسجلات المهام بين الفرق مع مراعاة الأولويات التشغيلية المتزامنة." },
    { en: "Prepared decision-focused meeting records with assigned owners, deadlines and follow-up requirements.", ar: "إعداد محاضر اجتماعات تركز على القرارات وتوضح المسؤوليات والمواعيد ومتطلبات المتابعة." },
    { en: "Maintained document version control and confidential records according to approved access procedures.", ar: "ضبط إصدارات المستندات وإدارة السجلات السرية وفق إجراءات الصلاحيات المعتمدة." }
  ],
  "logistics": [
    { en: "Reconciled physical inventory movements with system records and investigated traceable stock variances.", ar: "مطابقة حركة المخزون الفعلية بسجلات النظام وفحص الفروقات التي يمكن تتبعها." },
    { en: "Coordinated inbound receiving, outbound dispatch and exception handling against shipment documents.", ar: "تنسيق الاستلامات والشحنات الصادرة ومعالجة الاستثناءات وفق مستندات الشحن." },
    { en: "Monitored replenishment signals and escalated potential availability risks to planning stakeholders.", ar: "متابعة مؤشرات إعادة التوريد وتصعيد مخاطر التوافر المحتملة لفرق التخطيط المعنية." }
  ],
  "design": [
    { en: "Translated user needs and project briefs into structured flows, interface concepts and reusable visual patterns.", ar: "تحويل احتياجات المستخدمين وموجزات المشاريع إلى تدفقات استخدام وأفكار واجهات وأنماط بصرية قابلة لإعادة الاستخدام." },
    { en: "Reviewed prototypes for visual hierarchy, accessibility and responsive behavior before developer handover.", ar: "مراجعة النماذج الأولية من حيث التدرج البصري وسهولة الوصول والاستجابة للشاشات قبل التسليم للمطورين." },
    { en: "Documented component states, interaction details and usability findings for iterative refinement.", ar: "توثيق حالات المكونات وتفاصيل التفاعل وملاحظات قابلية الاستخدام لدعم التحسين التدريجي." }
  ],
  "physician": [
    { en: "Documented focused clinical assessments, differential considerations and escalation decisions within authorized practice.", ar: "توثيق التقييمات السريرية الموجهة والاحتمالات التشخيصية وقرارات التصعيد ضمن نطاق الممارسة المخول." },
    { en: "Coordinated time-sensitive clinical priorities and structured patient handovers across multidisciplinary teams.", ar: "تنسيق الأولويات السريرية العاجلة وتسليم حالات المرضى بشكل منظم بين فرق التخصصات المختلفة." },
    { en: "Interpreted investigation findings in patient context and recorded appropriate follow-up plans under local protocols.", ar: "تفسير نتائج الفحوص في سياق حالة المريض وتوثيق خطط المتابعة الملائمة وفق البروتوكولات المحلية." }
  ],
  "pharmacy": [
    { en: "Reviewed medication orders for completeness and relevant safety checks within the permitted scope of practice.", ar: "مراجعة أوامر الأدوية من حيث الاكتمال وفحوص السلامة ذات الصلة ضمن نطاق الممارسة المسموح." },
    { en: "Clarified prescription discrepancies with authorized clinicians and documented approved follow-up actions.", ar: "توضيح اختلافات الوصفات مع الممارسين المخولين وتوثيق إجراءات المتابعة المعتمدة." },
    { en: "Monitored storage conditions, expiry risks and inventory exceptions to support safe medication workflows.", ar: "متابعة ظروف تخزين الأدوية ومخاطر الصلاحية واستثناءات المخزون لدعم عمليات دوائية آمنة." }
  ],
  "laboratory": [
    { en: "Verified specimen identity and traceability across receipt, processing and pre-analytical quality checkpoints.", ar: "التحقق من هوية العينات وإمكانية تتبعها خلال الاستلام والتجهيز ومراحل جودة ما قبل التحليل." },
    { en: "Reviewed quality-control anomalies and documented corrective steps under laboratory standard procedures.", ar: "مراجعة حالات ضبط الجودة غير المعتادة وتوثيق الإجراءات التصحيحية وفق إجراءات المختبر." },
    { en: "Communicated critical or flagged findings through approved reporting pathways while maintaining accurate analytical records.", ar: "إبلاغ النتائج الحرجة أو التي تستدعي الانتباه عبر مسارات الإبلاغ المعتمدة مع الحفاظ على دقة السجلات التحليلية." }
  ],
  "hospitality": [
    { en: "Coordinated guest requests across reception, housekeeping and service teams with clear handover accountability.", ar: "تنسيق طلبات النزلاء بين الاستقبال وخدمات الغرف وفرق الخدمة مع وضوح مسؤولية التسليم." },
    { en: "Managed service-recovery requests within delegated authority and documented escalations for complex concerns.", ar: "معالجة طلبات استعادة رضا النزلاء ضمن الصلاحيات وتوثيق تصعيد الحالات المعقدة." },
    { en: "Maintained shift handovers covering pending requests, priority changes and service-readiness risks.", ar: "تنظيم تسليمات الورديات بما يشمل الطلبات المعلقة وتغير الأولويات ومخاطر جاهزية الخدمة." }
  ],
  "legal": [
    { en: "Organized case records into structured chronologies to support issue analysis and evidence review.", ar: "تنظيم سجلات القضايا في تسلسل زمني منظم لدعم تحليل المسائل ومراجعة الأدلة." },
    { en: "Reviewed legal correspondence and supporting documents for consistency, procedural requirements and open actions.", ar: "مراجعة المراسلات القانونية والمستندات الداعمة من حيث الاتساق والمتطلبات الإجرائية والإجراءات المعلقة." },
    { en: "Tracked filing deadlines and maintained confidential document versions for authorized case review.", ar: "متابعة المواعيد الإجرائية وضبط نسخ الوثائق السرية للمراجعة المصرح بها." }
  ]
};
const ADVANCED_NURSING_BULLETS: Record<string, CareerText[]> = {
  "emergency": [
    { en: "Triaged patients using presenting acuity, recognized red-flag deterioration and escalated time-critical findings through the emergency response pathway.", ar: "فرز المرضى وفق حدة العرض، والتعرف على مؤشرات التدهور الخطرة وتصعيد النتائج العاجلة عبر مسار الاستجابة بالطوارئ." },
    { en: "Coordinated resuscitation-area readiness, prioritized clinical handovers and documented key reassessment findings during high-acuity care.", ar: "تنسيق جاهزية منطقة الإنعاش وترتيب أولويات تسليم الحالات وتوثيق نتائج إعادة التقييم المهمة أثناء رعاية الحالات الحرجة." }
  ],
  "icu": [
    { en: "Monitored trends in vital signs and organ-support observations, escalating clinically significant changes through the critical-care pathway.", ar: "متابعة اتجاهات العلامات الحيوية وملاحظات دعم الوظائف الحيوية مع تصعيد التغيرات السريرية المهمة عبر مسار الرعاية الحرجة." },
    { en: "Delivered structured handovers covering device safety, treatment priorities and outstanding clinical concerns.", ar: "تنفيذ تسليمات منظمة تتناول سلامة الأجهزة وأولويات العلاج والمخاوف السريرية المعلقة." }
  ],
  "or": [
    { en: "Applied perioperative verification and aseptic-practice checks across preparation, intraoperative care and handover.", ar: "تطبيق فحوص التحقق قبل الجراحة وإجراءات التعقيم خلال التحضير والرعاية أثناء العملية والتسليم." },
    { en: "Coordinated instrument and count documentation and escalated discrepancies according to theatre safety policy.", ar: "تنسيق توثيق الأدوات والعد الجراحي وتصعيد الفروقات وفق سياسة سلامة غرفة العمليات." }
  ],
  "infection-control": [
    { en: "Conducted infection-prevention observations and documented compliance gaps against approved transmission-based precautions.", ar: "إجراء ملاحظات مكافحة العدوى وتوثيق فجوات الالتزام وفق الاحتياطات المعتمدة المبنية على طرق الانتقال." },
    { en: "Communicated audit findings and follow-up actions for hand hygiene, device care and environmental practices.", ar: "إبلاغ نتائج التدقيق وإجراءات المتابعة المتعلقة بنظافة اليدين ورعاية الأجهزة والممارسات البيئية." }
  ],
  "dialysis": [
    { en: "Verified dialysis access and treatment-preparation checks, documenting changes requiring timely escalation.", ar: "التحقق من وصلة الغسيل الكلوي وفحوص التحضير للجلسة وتوثيق التغيرات التي تتطلب التصعيد في الوقت المناسب." },
    { en: "Monitored treatment tolerance and communicated relevant observations during multidisciplinary renal-care handovers.", ar: "متابعة تحمل المريض للجلسة وإبلاغ الملاحظات المهمة أثناء تسليمات فريق رعاية الكلى." }
  ],
  "pediatric": [
    { en: "Used age-appropriate observation and family communication to recognize and escalate changes in pediatric condition.", ar: "استخدام الملاحظة الملائمة للعمر والتواصل مع الأسرة للتعرف على تغيرات حالة الأطفال وتصعيدها." },
    { en: "Verified weight-sensitive care information and documented safety checks according to pediatric protocols.", ar: "التحقق من بيانات الرعاية المرتبطة بالوزن وتوثيق فحوص السلامة وفق بروتوكولات الأطفال." }
  ],
  "medsurg": [
    { en: "Prioritized ward care based on clinical acuity, medication timing and pending investigations, escalating deterioration.", ar: "ترتيب رعاية الأقسام وفق حدة الحالة ومواعيد الأدوية والفحوص المعلقة مع تصعيد علامات التدهور." },
    { en: "Maintained structured shift handovers and reconciled outstanding care needs with the multidisciplinary team.", ar: "الالتزام بتسليمات منظمة للورديات ومراجعة احتياجات الرعاية المعلقة مع الفريق متعدد التخصصات." }
  ],
  "supervisor": [
    { en: "Balanced staffing assignments against patient acuity, workload and available competencies while escalating coverage gaps.", ar: "موازنة توزيع الكوادر مع حدة الحالات وحجم العمل والكفاءات المتاحة وتصعيد فجوات التغطية." },
    { en: "Reviewed documentation and safety incidents to coordinate follow-up actions and practical team coaching.", ar: "مراجعة التوثيق وحوادث السلامة لتنسيق إجراءات المتابعة والتوجيه العملي للفريق." }
  ]
};


type CareerTrack = { id: string; career: string; pattern: RegExp; label: CareerText; bullets: CareerText[] };
const CAREER_TRACKS: CareerTrack[] = [
  { id: "financial-accounting", career: "accounting", pattern: /financial accountant|general ledger|\bgl accountant\b|محاسب مالي|محاسب عام/i, label: { en: "Financial accounting", ar: "المحاسبة المالية" }, bullets: [
    { en: "Investigated general-ledger variances, reconciled supporting schedules and documented correction requests for month-end close.", ar: "فحص فروقات دفتر الأستاذ العام ومطابقة الجداول الداعمة وتوثيق طلبات التصحيح ضمن إقفال الشهر." },
    { en: "Prepared account reconciliations and traceable supporting schedules to support financial statement review.", ar: "إعداد تسويات الحسابات والجداول الداعمة القابلة للتتبع لدعم مراجعة القوائم المالية." }
  ] },
  { id: "tax-accounting", career: "accounting", pattern: /tax accountant|tax specialist|محاسب ضرائب|أخصائي ضرائب|ضرايب/i, label: { en: "Tax accounting", ar: "المحاسبة الضريبية" }, bullets: [
    { en: "Reconciled tax-related ledger balances with source transactions and documented reporting discrepancies.", ar: "مطابقة أرصدة الحسابات الضريبية مع المعاملات الأصلية وتوثيق فروقات التقارير." },
    { en: "Organized supporting tax schedules and monitored submission requirements under applicable procedures.", ar: "تنظيم الجداول الضريبية الداعمة ومتابعة متطلبات تقديم الإقرارات وفق الإجراءات المعمول بها." }
  ] },
  { id: "audit", career: "accounting", pattern: /auditor|internal audit|external audit|مراجع مالي|مدقق|مراجع حسابات/i, label: { en: "Audit and controls", ar: "التدقيق والرقابة" }, bullets: [
    { en: "Mapped control procedures to supporting evidence and recorded findings for risk-based follow-up.", ar: "ربط إجراءات الرقابة بالمستندات الداعمة وتوثيق الملاحظات للمتابعة المبنية على المخاطر." },
    { en: "Reviewed transaction samples and documented exceptions, control owners and corrective-action follow-up.", ar: "مراجعة عينات المعاملات وتوثيق الاستثناءات ومسؤولي الرقابة ومتابعة الإجراءات التصحيحية." }
  ] },
  { id: "frontend", career: "software", pattern: /front.?end|react developer|angular developer|vue developer|مطور واجهات|واجهات أمامية|فرونت اند/i, label: { en: "Frontend development", ar: "تطوير الواجهات" }, bullets: [
    { en: "Translated accessible interface specifications into reusable frontend components with responsive-state checks.", ar: "تحويل مواصفات الواجهات الداعمة لإمكانية الوصول إلى مكونات قابلة لإعادة الاستخدام مع فحص تجاوب الشاشات." },
    { en: "Validated form behavior, loading and error states, and keyboard interactions through targeted browser tests.", ar: "التحقق من سلوك النماذج وحالات التحميل والأخطاء والتفاعل عبر لوحة المفاتيح باختبارات المتصفح الموجهة." }
  ] },
  { id: "backend", career: "software", pattern: /back.?end|api developer|server.?side|مطور باك اند|تطوير خلفي|برمجيات خلفية/i, label: { en: "Backend development", ar: "تطوير الأنظمة الخلفية" }, bullets: [
    { en: "Designed API contracts with input validation, clear error handling and documented access boundaries.", ar: "تصميم عقود واجهات البرمجة مع التحقق من المدخلات ومعالجة واضحة للأخطاء وتوثيق حدود الوصول." },
    { en: "Investigated service failures using structured logs and repeatable tests before validating regression fixes.", ar: "فحص أعطال الخدمات باستخدام السجلات المنظمة والاختبارات القابلة للإعادة قبل التحقق من إصلاحات منع تكرار الخطأ." }
  ] },
  { id: "fullstack", career: "software", pattern: /full.?stack|فول ستاك|تطوير متكامل/i, label: { en: "Full-stack development", ar: "التطوير المتكامل" }, bullets: [
    { en: "Coordinated frontend workflows with backend API contracts and verified end-to-end failure handling.", ar: "ربط مسارات الواجهة بعقود واجهات البرمجة والتحقق من معالجة الإخفاقات عبر رحلة المستخدم كاملة." },
    { en: "Implemented and reviewed application changes across UI, service and data boundaries with targeted regression checks.", ar: "تنفيذ ومراجعة تغييرات التطبيق عبر الواجهة والخدمات والبيانات مع فحوص منع تكرار الأخطاء." }
  ] },
  { id: "civil", career: "engineering", pattern: /civil engineer|site engineer|structural engineer|مهندس مدني|مهندس موقع|مهندس إنشائي/i, label: { en: "Civil and site engineering", ar: "الهندسة المدنية والمواقع" }, bullets: [
    { en: "Reviewed site drawings and material submittals against approved specifications and raised technical clarifications.", ar: "مراجعة رسومات الموقع واعتمادات المواد مقابل المواصفات المعتمدة ورفع الاستفسارات الفنية." },
    { en: "Tracked inspection findings and coordinated corrective actions for construction nonconformities.", ar: "متابعة نتائج الفحوص وتنسيق الإجراءات التصحيحية لحالات عدم المطابقة في أعمال الإنشاء." }
  ] },
  { id: "electrical", career: "engineering", pattern: /electrical engineer|power engineer|مهندس كهرباء|مهندس كهربائي/i, label: { en: "Electrical engineering", ar: "الهندسة الكهربائية" }, bullets: [
    { en: "Reviewed electrical schematics, equipment schedules and interface requirements for implementation readiness.", ar: "مراجعة المخططات الكهربائية وجداول المعدات ومتطلبات الربط للتحقق من جاهزية التنفيذ." },
    { en: "Documented inspection and test observations against approved electrical safety procedures.", ar: "توثيق ملاحظات الفحص والاختبار وفق إجراءات السلامة الكهربائية المعتمدة." }
  ] },
  { id: "mechanical", career: "engineering", pattern: /mechanical engineer|hvac engineer|مهندس ميكانيكا|مهندس تكييف|مهندس ميكانيكي/i, label: { en: "Mechanical engineering", ar: "الهندسة الميكانيكية" }, bullets: [
    { en: "Reviewed mechanical equipment specifications and installation interfaces against project requirements.", ar: "مراجعة مواصفات المعدات الميكانيكية وواجهات التركيب وفق متطلبات المشروع." },
    { en: "Recorded commissioning observations, technical deviations and outstanding corrective items for handover.", ar: "توثيق ملاحظات التشغيل التجريبي والانحرافات الفنية والبنود التصحيحية المعلقة للتسليم." }
  ] },
  { id: "math-teaching", career: "teaching", pattern: /math teacher|mathematics teacher|مدرس رياضيات|معلم رياضيات/i, label: { en: "Mathematics teaching", ar: "تدريس الرياضيات" }, bullets: [
    { en: "Designed scaffolded mathematics tasks that connect problem-solving strategies with curriculum outcomes.", ar: "إعداد مهام رياضية متدرجة تربط استراتيجيات حل المسائل بمخرجات المنهج." },
    { en: "Analyzed formative assessment errors to tailor follow-up practice for specific mathematical misconceptions.", ar: "تحليل أخطاء التقييم البنائي لتكييف التدريبات اللاحقة وفق المفاهيم الرياضية غير المكتملة." }
  ] },
  { id: "b2b-sales", career: "sales", pattern: /\bb2b\b|business development|enterprise sales|مبيعات شركات|تطوير أعمال/i, label: { en: "B2B and enterprise sales", ar: "مبيعات الشركات" }, bullets: [
    { en: "Qualified B2B opportunities by documenting stakeholder priorities, decision criteria and procurement dependencies.", ar: "تأهيل فرص مبيعات الشركات بتوثيق أولويات أصحاب القرار ومعايير الشراء والاعتماديات التعاقدية." },
    { en: "Maintained opportunity plans with customer use cases, follow-up actions and structured proposal handovers.", ar: "إدارة خطط الفرص وفق حالات استخدام العملاء وخطوات المتابعة وتسليمات العروض المنظمة." }
  ] },
  { id: "retail-sales", career: "sales", pattern: /retail sales|sales representative|store sales|مندوب مبيعات|بائع تجزئة|مبيعات تجزئة/i, label: { en: "Retail and field sales", ar: "مبيعات التجزئة والميدان" }, bullets: [
    { en: "Matched product recommendations to customer requirements while documenting objections and agreed next steps.", ar: "مواءمة توصيات المنتجات مع احتياجات العملاء وتوثيق الاعتراضات والخطوات المتفق عليها." },
    { en: "Coordinated order follow-ups and communicated stock or delivery constraints with service teams.", ar: "تنسيق متابعة الطلبات وإبلاغ فرق الخدمة بقيود المخزون أو التسليم." }
  ] },
  { id: "seo", career: "marketing", pattern: /\bseo\b|search engine optim|تحسين محركات البحث|أخصائي سيو|سيو/i, label: { en: "Search engine optimization", ar: "تحسين محركات البحث" }, bullets: [
    { en: "Mapped search intent to content topics and documented on-page optimization priorities for relevant pages.", ar: "ربط نوايا البحث بموضوعات المحتوى وتوثيق أولويات تحسين الصفحات ذات الصلة." },
    { en: "Reviewed indexing, metadata and internal-linking issues and proposed testable technical SEO improvements.", ar: "مراجعة مشكلات الفهرسة والبيانات الوصفية والربط الداخلي واقتراح تحسينات تقنية قابلة للاختبار." }
  ] },
  { id: "paid-media", career: "marketing", pattern: /performance market|paid media|ppc specialist|media buyer|إعلانات ممولة|مشتري إعلانات/i, label: { en: "Paid media", ar: "الإعلانات الرقمية المدفوعة" }, bullets: [
    { en: "Organized campaign structures around audience segments, creative variations and clearly defined conversion events.", ar: "تنظيم الحملات حول شرائح الجمهور وتنوع المواد الإبداعية وأحداث التحويل المحددة بوضوح." },
    { en: "Reviewed funnel metrics and documented hypotheses for campaign targeting and landing-page improvements.", ar: "مراجعة مؤشرات مسار التحويل وتوثيق فرضيات تحسين الاستهداف وصفحات الهبوط." }
  ] },
  { id: "recruitment", career: "hr", pattern: /recruiter|talent acquisition|recruitment specialist|أخصائي توظيف|مسؤول توظيف/i, label: { en: "Recruitment", ar: "الاستقطاب والتوظيف" }, bullets: [
    { en: "Prepared structured candidate-screening notes against role requirements and maintained traceable interview handovers.", ar: "إعداد ملاحظات فرز منظمة للمرشحين مقابل متطلبات الوظيفة والحفاظ على تسليمات مقابلات قابلة للتتبع." },
    { en: "Coordinated candidate communication, interview scheduling and recruitment-stage documentation.", ar: "تنسيق التواصل مع المرشحين ومواعيد المقابلات وتوثيق مراحل التوظيف." }
  ] },
  { id: "tech-support", career: "customer-service", pattern: /technical support|it support|help desk|دعم فني|مساعدة تقنية/i, label: { en: "Technical support", ar: "الدعم الفني" }, bullets: [
    { en: "Triaged support requests using impact, reproducibility and affected services to prioritize escalation.", ar: "تصنيف طلبات الدعم حسب التأثير وقابلية تكرار العطل والخدمات المتأثرة لتحديد أولوية التصعيد." },
    { en: "Documented troubleshooting steps, evidence and resolution handovers in the service ticket record.", ar: "توثيق خطوات استكشاف الأخطاء والأدلة وتسليمات الحل في سجل طلب الخدمة." }
  ] },
  { id: "procurement", career: "logistics", pattern: /procurement|purchasing officer|buyer|مشتريات|أخصائي توريد/i, label: { en: "Procurement", ar: "المشتريات" }, bullets: [
    { en: "Compared supplier quotations against technical requirements, delivery constraints and approval criteria.", ar: "مقارنة عروض الموردين وفق المتطلبات الفنية وقيود التسليم ومعايير الاعتماد." },
    { en: "Tracked purchase-order exceptions and coordinated document-complete handovers with receiving teams.", ar: "متابعة استثناءات أوامر الشراء وتنسيق التسليم بالمستندات المكتملة مع فرق الاستلام." }
  ] },
  { id: "warehouse", career: "logistics", pattern: /warehouse|inventory control|stock controller|مخازن|مستودع|مراقب مخزون/i, label: { en: "Warehouse and inventory", ar: "المستودعات والمخزون" }, bullets: [
    { en: "Reconciled receipt and dispatch records with inventory movements and documented stock discrepancies.", ar: "مطابقة سجلات الاستلام والصرف مع حركة المخزون وتوثيق الفروقات." },
    { en: "Reviewed storage locations and picking records to support traceability and timely exception escalation.", ar: "مراجعة مواقع التخزين وسجلات التجهيز لدعم التتبع والتصعيد المبكر للاستثناءات." }
  ] },
  { id: "product-design", career: "design", pattern: /\bui.?ux\b|ux designer|product designer|مصمم تجربة مستخدم|مصمم واجهات/i, label: { en: "Product and UX design", ar: "تصميم تجربة المستخدم" }, bullets: [
    { en: "Converted user-journey findings into prioritized interaction flows, annotated wireframes and prototype requirements.", ar: "تحويل نتائج رحلات المستخدم إلى تدفقات تفاعل ذات أولوية ورسومات أولية مشروحة ومتطلبات للنماذج التفاعلية." },
    { en: "Evaluated accessible interaction patterns and responsive component states during design-to-development handover.", ar: "تقييم أنماط التفاعل الداعمة لإمكانية الوصول وحالات المكونات المتجاوبة أثناء التسليم للتطوير." }
  ] },
  { id: "clinical-pharmacy", career: "pharmacy", pattern: /clinical pharmacist|صيدلي إكلينيكي|صيدلي سريري/i, label: { en: "Clinical pharmacy", ar: "الصيدلة الإكلينيكية" }, bullets: [
    { en: "Reviewed medication histories and potential therapy discrepancies within authorized clinical pharmacy responsibilities.", ar: "مراجعة التاريخ الدوائي والفروقات العلاجية المحتملة ضمن المسؤوليات المصرح بها للصيدلة الإكلينيكية." },
    { en: "Documented medication-related recommendations and follow-up communications through the appropriate care team.", ar: "توثيق التوصيات الدوائية واتصالات المتابعة عبر فريق الرعاية المختص." }
  ] },
  { id: "laboratory-quality", career: "laboratory", pattern: /lab quality|quality control analyst|laboratory qc|جودة مختبر|ضبط جودة معمل/i, label: { en: "Laboratory quality assurance", ar: "جودة المختبرات" }, bullets: [
    { en: "Reviewed laboratory control results against acceptance criteria and documented out-of-range investigations.", ar: "مراجعة نتائج ضبط الجودة بالمختبر مقابل معايير القبول وتوثيق فحص النتائج الخارجة عن النطاق." },
    { en: "Maintained traceable corrective-action records and verified procedural follow-up for analytical exceptions.", ar: "الاحتفاظ بسجلات قابلة للتتبع للإجراءات التصحيحية والتحقق من المتابعة الإجرائية للاستثناءات التحليلية." }
  ] },
  { id: "contracts", career: "legal", pattern: /contract lawyer|contract specialist|contracts counsel|محامي عقود|أخصائي عقود/i, label: { en: "Contract review", ar: "مراجعة العقود" }, bullets: [
    { en: "Reviewed contractual clauses for consistency with agreed terms and documented issues requiring legal clarification.", ar: "مراجعة بنود العقود للتحقق من الاتساق مع الشروط المتفق عليها وتوثيق المسائل التي تتطلب توضيحًا قانونيًا." },
    { en: "Maintained structured clause comparisons and version-controlled negotiation records for authorized review.", ar: "إدارة مقارنات منظمة للبنود وسجلات تفاوض مضبوطة الإصدارات للمراجعة المصرح بها." }
  ] }
];
const PROFESSIONAL_LEVEL_OPTIONS: Array<{ id: NursingLevel; label: CareerText }> = [
  { id: 'beginner', label: { en: 'Early career', ar: 'بداية المسار المهني' } },
  { id: 'experienced', label: { en: 'Professional', ar: 'مستوى مهني' } },
  { id: 'senior', label: { en: 'Senior / Specialist', ar: 'أقدم / متخصص' } },
  { id: 'supervisor', label: { en: 'Manager / Lead', ar: 'إدارة / قيادة' } }
];
const PROFESSIONAL_LEVEL_BULLETS: Record<NursingLevel, Array<CareerText & { category: Exclude<Category, 'all'> }>> = {
  beginner: [
    { en: 'Applied documented procedures to assigned tasks and escalated exceptions for timely review.', ar: 'تطبيق الإجراءات الموثقة على المهام المكلف بها وتصعيد الاستثناءات للمراجعة في الوقت المناسب.', category: 'clinical' },
    { en: 'Maintained clear task records and followed up on assigned actions with the relevant team.', ar: 'الاحتفاظ بسجلات واضحة للمهام ومتابعة الإجراءات المكلف بها مع الفريق المعني.', category: 'documentation' }
  ],
  experienced: [
    { en: 'Prioritized concurrent responsibilities against agreed requirements and communicated emerging delivery risks.', ar: 'ترتيب المسؤوليات المتزامنة وفق المتطلبات المتفق عليها وإبلاغ مخاطر التنفيذ المستجدة.', category: 'clinical' },
    { en: 'Investigated work exceptions and coordinated documented follow-up with relevant stakeholders.', ar: 'فحص استثناءات العمل وتنسيق المتابعة الموثقة مع الجهات المعنية.', category: 'teamwork' }
  ],
  senior: [
    { en: 'Reviewed complex work outputs for quality and provided actionable feedback to colleagues.', ar: 'مراجعة مخرجات العمل المعقدة من حيث الجودة وتقديم ملاحظات عملية للزملاء.', category: 'leadership' },
    { en: 'Identified process dependencies and coordinated cross-team solutions for recurring operational issues.', ar: 'تحديد اعتماديات العمليات وتنسيق الحلول بين الفرق للمشكلات التشغيلية المتكررة.', category: 'teamwork' }
  ],
  supervisor: [
    { en: 'Coordinated workload assignments against team capacity, delivery deadlines and operational priorities.', ar: 'تنسيق توزيع أعباء العمل وفق طاقة الفريق ومواعيد التسليم والأولويات التشغيلية.', category: 'leadership' },
    { en: 'Reviewed escalations, assigned corrective-action owners and monitored outstanding operational risks.', ar: 'مراجعة حالات التصعيد وتحديد المسؤولين عن الإجراءات التصحيحية ومتابعة المخاطر التشغيلية المعلقة.', category: 'leadership' }
  ]
};
function inferProfessionalLevel(role: string): NursingLevel {
  if (/\b(manager|director|head|supervisor|team lead)\b|مدير|مشرف|رئيس قسم|قائد فريق/i.test(role)) return 'supervisor';
  if (/\b(senior|principal|lead specialist)\b|كبير|أول|خبير|سينيور/i.test(role)) return 'senior';
  if (/\b(junior|intern|trainee|graduate|entry.level)\b|متدرب|حديث التخرج|مبتدئ|مساعد/i.test(role)) return 'beginner';
  return 'experienced';
}
function detectCareerTrack(role: string, careerId: string) {
  return CAREER_TRACKS.find((track) => track.career === careerId && track.pattern.test(role));
}

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
        "    const specialtyItems: Suggestion[] = (nursingRole ? [...(ADVANCED_NURSING_BULLETS[specialty.id] || []), ...specialty.bullets] : [...(ADVANCED_CAREER_BULLETS[career.id] || []), ...career.bullets]).map((item, index) => ({")
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
replace("    setVersion((value) => value + 1);\n    target.focus();\n  };",
        "    setVersion((value) => value + 1);\n    setOpen(false); // Close Smart CV only after selected examples are inserted.\n    target.focus();\n  };")


# Pro V3: context-aware career tracks and experience levels for non-nursing roles.
replace("  const [slot, setSlot] = useState<HTMLElement | null>(null);",
        """  const [slot, setSlot] = useState<HTMLElement | null>(null);
  const [professionalLevel, setProfessionalLevel] = useState<NursingLevel>('experienced');
  const [careerTrackId, setCareerTrackId] = useState('');
  const trackRoleRef = useRef<string | null>(null);
  const levelOverrideRoleRef = useRef<string | null>(null);""")

replace("      setDetectedRole(role);",
        """      setDetectedRole(role);
      if (trackRoleRef.current !== role) {
        trackRoleRef.current = role;
        const roleCareer = careerFor(role);
        setCareerTrackId(detectCareerTrack(role, roleCareer.id)?.id || '');
      }
      if (levelOverrideRoleRef.current !== role) {
        levelOverrideRoleRef.current = null;
        setProfessionalLevel(inferProfessionalLevel(role));
      }""")

replace("  const career = useMemo(() => careerFor(detectedRole), [detectedRole]);",
        """  const career = useMemo(() => careerFor(detectedRole), [detectedRole]);
  const careerTrack = useMemo(() => CAREER_TRACKS.find((track) => track.career === career.id && track.id === careerTrackId), [career, careerTrackId]);
  const careerTrackChoices = useMemo(() => CAREER_TRACKS.filter((track) => track.career === career.id), [career]);""")

replace("    const specialtyItems: Suggestion[] = (nursingRole ? [...(ADVANCED_NURSING_BULLETS[specialty.id] || []), ...specialty.bullets] : [...(ADVANCED_CAREER_BULLETS[career.id] || []), ...career.bullets]).map((item, index) => ({",
        "    const specialtyItems: Suggestion[] = (nursingRole ? [...(ADVANCED_NURSING_BULLETS[specialty.id] || []), ...specialty.bullets] : [...(careerTrack?.bullets || []), ...(ADVANCED_CAREER_BULLETS[career.id] || []), ...career.bullets]).map((item, index) => ({")

replace("      id: 'career-' + (nursingRole ? specialty.id : career.id) + '-' + index,",
        "      id: 'career-' + (nursingRole ? specialty.id : careerTrack?.id || career.id) + '-' + index,")

replace("    const levelItems: Suggestion[] = (nursingRole ? LEVEL_EXTRAS[level] : []).map((item, index) => ({",
        "    const levelItems: Suggestion[] = (nursingRole ? LEVEL_EXTRAS[level] : PROFESSIONAL_LEVEL_BULLETS[professionalLevel]).map((item, index) => ({")

replace("      id: 'level-' + level + '-' + index,",
        "      id: 'level-' + (nursingRole ? level : professionalLevel) + '-' + index,")

replace("  }, [specialty, career, nursingRole, level, language]);",
        "  }, [specialty, career, nursingRole, careerTrack, professionalLevel, level, language]);")

replace("  const selectedItems = suggestions.filter((item) => selected.includes(item.id));",
        """  const selectedItems = suggestions.filter((item) => selected.includes(item.id));""")

replace("      <label className=\"experience-picker__search\">",
        """      {!nursingRole && <div className="experience-picker__selectors experience-picker__career-selectors">
        <label>
          <span>{copy.specialty}</span>
          <select aria-label="Career specialization" value={careerTrackId}
            onChange={(event) => {
              setCareerTrackId(event.target.value);
              setSelected([]);
              setCategory('all');
              setQuery('');
            }}>
            <option value="">{career.label[language]} — {language === 'ar' ? 'عام' : 'general'}</option>
            {careerTrackChoices.map((track) => (
              <option key={track.id} value={track.id}>{track.label[language]}</option>
            ))}
          </select>
        </label>
        <label>
          <span>{copy.level}</span>
          <select aria-label="Professional experience level" value={professionalLevel}
            onChange={(event) => {
              const choice = event.target.value as NursingLevel;
              setProfessionalLevel(choice);
              levelOverrideRoleRef.current = detectedRole;
              setSelected([]);
            }}>
            {PROFESSIONAL_LEVEL_OPTIONS.map((item) => (
              <option key={item.id} value={item.id}>{item.label[language]}</option>
            ))}
          </select>
        </label>
      </div>}

      <label className="experience-picker__search">""")

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
