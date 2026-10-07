from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()

data_file = root / "lib" / "nursingLibrary.ts"
data_file.write_text(r'''export type LibraryLanguage = 'en' | 'ar';
export type NursingLevel = 'beginner' | 'experienced' | 'senior' | 'supervisor';
export type TargetMarket = 'ats' | 'egypt' | 'gulf';

export type LocalText = {
  en: string;
  ar: string;
};

export type NursingSpecialty = {
  id: string;
  label: LocalText;
  coreSummary: LocalText;
  skills: LocalText[];
  bullets: LocalText[];
  keywords: LocalText[];
  certifications: LocalText[];
};

export const nursingLevels: Array<{ id: NursingLevel; label: LocalText; intro: LocalText }> = [
  {
    id: 'beginner',
    label: { en: 'Beginner / Early career', ar: 'مبتدئ / بداية المسار المهني' },
    intro: {
      en: 'Early-career nursing professional with a strong foundation in safe patient care and clinical teamwork.',
      ar: 'ممرض/ة في بداية المسار المهني يمتلك أساسًا قويًا في رعاية المرضى الآمنة والعمل السريري ضمن الفريق.'
    }
  },
  {
    id: 'experienced',
    label: { en: 'Experienced', ar: 'ذو خبرة' },
    intro: {
      en: 'Nursing professional with hands-on clinical experience, dependable prioritization and consistent patient-centered care.',
      ar: 'ممرض/ة ذو خبرة عملية سريرية مع قدرة موثوقة على ترتيب الأولويات وتقديم رعاية تتمحور حول المريض.'
    }
  },
  {
    id: 'senior',
    label: { en: 'Senior', ar: 'خبير / Senior' },
    intro: {
      en: 'Senior nursing professional with strong clinical judgment, escalation skills and support for safe team performance.',
      ar: 'ممرض/ة خبير يمتلك حكمًا سريريًا قويًا وقدرة على التصعيد المناسب ودعم أداء الفريق بصورة آمنة.'
    }
  },
  {
    id: 'supervisor',
    label: { en: 'Supervisor', ar: 'مشرف تمريض' },
    intro: {
      en: 'Nursing professional with supervisory focus, shift coordination experience and a strong emphasis on quality and patient safety.',
      ar: 'ممرض/ة ذو تركيز إشرافي وخبرة في تنسيق الوردية مع اهتمام قوي بالجودة وسلامة المرضى.'
    }
  }
];

export const targetMarkets: Array<{ id: TargetMarket; label: LocalText; emphasis: LocalText; keywords: LocalText[] }> = [
  {
    id: 'ats',
    label: { en: 'General ATS', ar: 'ATS عام' },
    emphasis: {
      en: 'Focused on patient safety, accurate documentation and multidisciplinary collaboration.',
      ar: 'مع التركيز على سلامة المرضى ودقة التوثيق والتعاون مع الفريق متعدد التخصصات.'
    },
    keywords: [
      { en: 'Patient Safety', ar: 'سلامة المرضى' },
      { en: 'Clinical Documentation', ar: 'التوثيق السريري' },
      { en: 'Multidisciplinary Collaboration', ar: 'التعاون متعدد التخصصات' }
    ]
  },
  {
    id: 'egypt',
    label: { en: 'Egypt', ar: 'مصر' },
    emphasis: {
      en: 'Comfortable with practical, high-volume clinical workflows and clear escalation of changing patient needs.',
      ar: 'قادر على العمل ضمن تدفقات سريرية عملية وعالية الكثافة مع تصعيد واضح عند تغير حالة المريض.'
    },
    keywords: [
      { en: 'High-volume Clinical Care', ar: 'الرعاية السريرية عالية الكثافة' },
      { en: 'Care Coordination', ar: 'تنسيق الرعاية' },
      { en: 'Patient Education', ar: 'تثقيف المرضى' }
    ]
  },
  {
    id: 'gulf',
    label: { en: 'Gulf', ar: 'الخليج' },
    emphasis: {
      en: 'Focused on policy-based care, patient safety, clear documentation and teamwork in multicultural clinical environments.',
      ar: 'مع التركيز على الرعاية المبنية على السياسات وسلامة المرضى والتوثيق الواضح والعمل ضمن بيئات سريرية متعددة الثقافات.'
    },
    keywords: [
      { en: 'Policy-based Care', ar: 'الرعاية المبنية على السياسات' },
      { en: 'Quality Improvement', ar: 'تحسين الجودة' },
      { en: 'Multicultural Teamwork', ar: 'العمل ضمن فريق متعدد الثقافات' }
    ]
  }
];

export const nursingSpecialties: NursingSpecialty[] = [
  {
    id: 'emergency',
    label: { en: 'Emergency Nurse', ar: 'تمريض الطوارئ' },
    coreSummary: {
      en: 'Focused on rapid assessment, triage, stabilization and safe emergency care in time-critical situations.',
      ar: 'يركز على التقييم السريع والفرز والاستقرار الأولي وتقديم رعاية طارئة آمنة في الحالات الحرجة زمنيًا.'
    },
    skills: [
      { en: 'Triage', ar: 'الفرز' },
      { en: 'Emergency Assessment', ar: 'التقييم الطارئ' },
      { en: 'Resuscitation Support', ar: 'دعم الإنعاش' },
      { en: 'ECG Monitoring', ar: 'مراقبة تخطيط القلب' },
      { en: 'Trauma Care', ar: 'رعاية الإصابات' },
      { en: 'Medication Administration', ar: 'إعطاء الأدوية' },
      { en: 'Wound Care', ar: 'العناية بالجروح' },
      { en: 'Clinical Handover', ar: 'التسليم والاستلام السريري' }
    ],
    bullets: [
      { en: 'Perform rapid patient assessments and prioritize care using triage principles.', ar: 'إجراء تقييم سريع للمرضى وترتيب أولوية الرعاية وفق مبادئ الفرز.' },
      { en: 'Monitor vital signs and clinical changes and escalate deterioration promptly.', ar: 'مراقبة العلامات الحيوية والتغيرات السريرية وتصعيد حالات التدهور بسرعة.' },
      { en: 'Support resuscitation and emergency interventions within scope and facility policy.', ar: 'دعم الإنعاش والتدخلات الطارئة ضمن نطاق الممارسة وسياسات المنشأة.' },
      { en: 'Administer prescribed medications and treatments safely and document patient response.', ar: 'إعطاء الأدوية والعلاجات الموصوفة بأمان وتوثيق استجابة المريض.' },
      { en: 'Document assessments, interventions and handovers accurately.', ar: 'توثيق التقييمات والتدخلات والتسليم والاستلام بدقة.' },
      { en: 'Coordinate with physicians and multidisciplinary teams during time-critical care.', ar: 'التنسيق مع الأطباء والفريق متعدد التخصصات أثناء الرعاية الحرجة زمنيًا.' }
    ],
    keywords: [
      { en: 'Emergency Nursing', ar: 'تمريض الطوارئ' },
      { en: 'Patient Prioritization', ar: 'ترتيب أولوية المرضى' },
      { en: 'Deterioration Recognition', ar: 'اكتشاف تدهور الحالة' }
    ],
    certifications: [
      { en: 'Basic Life Support (BLS)', ar: 'دعم الحياة الأساسي (BLS)' },
      { en: 'Advanced Cardiovascular Life Support (ACLS)', ar: 'دعم الحياة القلبي المتقدم (ACLS)' },
      { en: 'Pediatric Advanced Life Support (PALS)', ar: 'دعم الحياة المتقدم للأطفال (PALS)' }
    ]
  },
  {
    id: 'icu',
    label: { en: 'ICU Nurse', ar: 'تمريض العناية المركزة' },
    coreSummary: {
      en: 'Focused on close monitoring, early recognition of deterioration and safe care for critically ill patients.',
      ar: 'يركز على المراقبة الدقيقة والاكتشاف المبكر للتدهور وتقديم رعاية آمنة للمرضى ذوي الحالات الحرجة.'
    },
    skills: [
      { en: 'Critical Care Nursing', ar: 'تمريض الحالات الحرجة' },
      { en: 'Hemodynamic Monitoring', ar: 'المراقبة الديناميكية الدموية' },
      { en: 'Ventilator Care', ar: 'رعاية مرضى أجهزة التنفس الصناعي' },
      { en: 'Infusion Pump Management', ar: 'التعامل مع مضخات المحاليل والأدوية' },
      { en: 'Neurological Assessment', ar: 'التقييم العصبي' },
      { en: 'Central Line Care', ar: 'العناية بالقسطرة المركزية' },
      { en: 'Pressure Injury Prevention', ar: 'الوقاية من إصابات الضغط' },
      { en: 'Critical Care Handover', ar: 'التسليم والاستلام في العناية المركزة' }
    ],
    bullets: [
      { en: 'Monitor critically ill patients closely and recognize significant clinical changes early.', ar: 'مراقبة المرضى ذوي الحالات الحرجة عن قرب واكتشاف التغيرات السريرية المهمة مبكرًا.' },
      { en: 'Provide safe nursing care for patients receiving mechanical ventilation and continuous monitoring.', ar: 'تقديم رعاية تمريضية آمنة للمرضى على أجهزة التنفس الصناعي والمراقبة المستمرة.' },
      { en: 'Manage prescribed infusions and medications using infusion devices according to policy.', ar: 'التعامل مع المحاليل والأدوية الموصوفة باستخدام مضخات الحقن وفق السياسات.' },
      { en: 'Apply infection-prevention practices for invasive devices and high-risk care.', ar: 'تطبيق ممارسات منع العدوى مع الأجهزة التدخلية والرعاية عالية الخطورة.' },
      { en: 'Communicate changes in patient condition promptly and participate in structured handover.', ar: 'إبلاغ الفريق سريعًا بتغيرات حالة المريض والمشاركة في تسليم واستلام منظم.' },
      { en: 'Document assessments, monitoring data, interventions and responses accurately.', ar: 'توثيق التقييمات وبيانات المراقبة والتدخلات والاستجابات بدقة.' }
    ],
    keywords: [
      { en: 'Critical Care', ar: 'الرعاية الحرجة' },
      { en: 'Early Deterioration Recognition', ar: 'الاكتشاف المبكر للتدهور' },
      { en: 'Invasive Device Care', ar: 'العناية بالأجهزة التدخلية' }
    ],
    certifications: [
      { en: 'Basic Life Support (BLS)', ar: 'دعم الحياة الأساسي (BLS)' },
      { en: 'Advanced Cardiovascular Life Support (ACLS)', ar: 'دعم الحياة القلبي المتقدم (ACLS)' },
      { en: 'Critical Care Nursing Training', ar: 'تدريب تمريض العناية المركزة' }
    ]
  },
  {
    id: 'or',
    label: { en: 'Operating Room Nurse', ar: 'تمريض العمليات' },
    coreSummary: {
      en: 'Focused on perioperative safety, aseptic practice, surgical preparation and coordinated operating-room care.',
      ar: 'يركز على السلامة حول الجراحة والممارسة المعقمة والتحضير الجراحي وتنسيق الرعاية داخل غرفة العمليات.'
    },
    skills: [
      { en: 'Perioperative Nursing', ar: 'التمريض حول الجراحة' },
      { en: 'Aseptic Technique', ar: 'التقنية المعقمة' },
      { en: 'Surgical Safety Checklist', ar: 'قائمة التحقق من السلامة الجراحية' },
      { en: 'Instrument and Sponge Counts', ar: 'عد الأدوات والشاش' },
      { en: 'Patient Positioning', ar: 'وضعية المريض الجراحية' },
      { en: 'Specimen Handling', ar: 'التعامل مع العينات' },
      { en: 'Sterile Field Support', ar: 'دعم الحقل المعقم' },
      { en: 'Perioperative Handover', ar: 'التسليم والاستلام حول الجراحة' }
    ],
    bullets: [
      { en: 'Prepare the operating room and required supplies according to the planned procedure and policy.', ar: 'تجهيز غرفة العمليات والمستلزمات المطلوبة وفق الإجراء المخطط وسياسة المنشأة.' },
      { en: 'Support surgical safety checks, patient identification and procedure verification.', ar: 'دعم فحوص السلامة الجراحية والتحقق من هوية المريض والإجراء.' },
      { en: 'Maintain aseptic technique and monitor the integrity of the sterile field.', ar: 'الحفاظ على التقنية المعقمة ومتابعة سلامة الحقل المعقم.' },
      { en: 'Participate in instrument, needle and sponge counts according to facility policy.', ar: 'المشاركة في عد الأدوات والإبر والشاش وفق سياسة المنشأة.' },
      { en: 'Assist with safe positioning, specimen handling and perioperative documentation.', ar: 'المساعدة في الوضع الآمن للمريض والتعامل مع العينات والتوثيق حول الجراحة.' },
      { en: 'Provide structured handover to the receiving recovery or critical-care team.', ar: 'تقديم تسليم واستلام منظم لفريق الإفاقة أو العناية المستلم.' }
    ],
    keywords: [
      { en: 'Surgical Safety', ar: 'السلامة الجراحية' },
      { en: 'Sterile Technique', ar: 'التقنية المعقمة' },
      { en: 'Perioperative Documentation', ar: 'التوثيق حول الجراحة' }
    ],
    certifications: [
      { en: 'Basic Life Support (BLS)', ar: 'دعم الحياة الأساسي (BLS)' },
      { en: 'Perioperative Nursing Training', ar: 'تدريب تمريض العمليات' },
      { en: 'Infection Prevention and Control Training', ar: 'تدريب مكافحة العدوى' }
    ]
  },
  {
    id: 'medsurg',
    label: { en: 'Ward / Medical-Surgical Nurse', ar: 'تمريض الأقسام / الباطنة والجراحة' },
    coreSummary: {
      en: 'Focused on comprehensive bedside assessment, medication safety, care planning and continuity of inpatient care.',
      ar: 'يركز على التقييم الشامل بجانب السرير وسلامة الدواء وتخطيط الرعاية واستمرارية رعاية المرضى الداخليين.'
    },
    skills: [
      { en: 'Patient Assessment', ar: 'تقييم المريض' },
      { en: 'Medication Safety', ar: 'سلامة الدواء' },
      { en: 'IV Therapy', ar: 'العلاج الوريدي' },
      { en: 'Care Planning', ar: 'تخطيط الرعاية' },
      { en: 'Wound Care', ar: 'العناية بالجروح' },
      { en: 'Fall Prevention', ar: 'الوقاية من السقوط' },
      { en: 'Discharge Education', ar: 'تثقيف المريض عند الخروج' },
      { en: 'Clinical Documentation', ar: 'التوثيق السريري' }
    ],
    bullets: [
      { en: 'Perform ongoing nursing assessments and identify changes requiring escalation.', ar: 'إجراء تقييمات تمريضية مستمرة وتحديد التغيرات التي تتطلب التصعيد.' },
      { en: 'Administer prescribed medications and treatments safely and monitor patient response.', ar: 'إعطاء الأدوية والعلاجات الموصوفة بأمان ومراقبة استجابة المريض.' },
      { en: 'Develop and update nursing care priorities according to patient needs.', ar: 'تحديد وتحديث أولويات الرعاية التمريضية وفق احتياجات المريض.' },
      { en: 'Apply fall-prevention, pressure-injury prevention and infection-prevention measures.', ar: 'تطبيق إجراءات الوقاية من السقوط وإصابات الضغط والعدوى.' },
      { en: 'Educate patients and families about care plans, medications and discharge instructions.', ar: 'تثقيف المرضى وأسرهم حول خطة الرعاية والأدوية وتعليمات الخروج.' },
      { en: 'Document care and communicate relevant information during handover.', ar: 'توثيق الرعاية ونقل المعلومات المهمة أثناء التسليم والاستلام.' }
    ],
    keywords: [
      { en: 'Inpatient Nursing', ar: 'تمريض المرضى الداخليين' },
      { en: 'Continuity of Care', ar: 'استمرارية الرعاية' },
      { en: 'Discharge Planning', ar: 'تخطيط الخروج' }
    ],
    certifications: [
      { en: 'Basic Life Support (BLS)', ar: 'دعم الحياة الأساسي (BLS)' },
      { en: 'Medication Safety Training', ar: 'تدريب سلامة الدواء' },
      { en: 'Infection Prevention and Control Training', ar: 'تدريب مكافحة العدوى' }
    ]
  },
  {
    id: 'infection-control',
    label: { en: 'Infection Control Nurse', ar: 'تمريض مكافحة العدوى' },
    coreSummary: {
      en: 'Focused on infection-prevention practices, surveillance support, audits, staff education and safe clinical processes.',
      ar: 'يركز على ممارسات منع العدوى ودعم الترصد والتدقيق وتثقيف العاملين وتعزيز العمليات السريرية الآمنة.'
    },
    skills: [
      { en: 'Infection Prevention and Control', ar: 'مكافحة العدوى' },
      { en: 'Hand Hygiene Auditing', ar: 'تدقيق نظافة اليدين' },
      { en: 'Standard Precautions', ar: 'الاحتياطات القياسية' },
      { en: 'Transmission-based Precautions', ar: 'احتياطات طرق الانتقال' },
      { en: 'HAI Surveillance', ar: 'ترصد العدوى المرتبطة بالرعاية الصحية' },
      { en: 'Environmental Rounds', ar: 'الجولات البيئية' },
      { en: 'Reprocessing Awareness', ar: 'مبادئ إعادة معالجة الأدوات' },
      { en: 'Staff Education', ar: 'تثقيف العاملين' }
    ],
    bullets: [
      { en: 'Support surveillance activities for healthcare-associated infections using defined criteria.', ar: 'دعم أنشطة ترصد العدوى المرتبطة بالرعاية الصحية باستخدام معايير محددة.' },
      { en: 'Conduct hand-hygiene and infection-prevention observations and communicate findings.', ar: 'إجراء ملاحظات نظافة اليدين ومكافحة العدوى وإبلاغ النتائج.' },
      { en: 'Review adherence to standard and transmission-based precautions during clinical rounds.', ar: 'مراجعة الالتزام بالاحتياطات القياسية واحتياطات طرق الانتقال أثناء الجولات السريرية.' },
      { en: 'Provide practical infection-prevention education to healthcare workers.', ar: 'تقديم تثقيف عملي للعاملين الصحيين حول ممارسات منع العدوى.' },
      { en: 'Support investigation and follow-up of infection-control incidents and clusters.', ar: 'دعم تقصي ومتابعة حوادث وتجمعات العدوى.' },
      { en: 'Document audit results, action items and follow-up findings clearly.', ar: 'توثيق نتائج التدقيق والإجراءات المطلوبة ونتائج المتابعة بوضوح.' }
    ],
    keywords: [
      { en: 'IPC Audits', ar: 'تدقيق مكافحة العدوى' },
      { en: 'Healthcare-associated Infection Surveillance', ar: 'ترصد العدوى المرتبطة بالرعاية الصحية' },
      { en: 'Outbreak Investigation Support', ar: 'دعم تقصي التفشيات' }
    ],
    certifications: [
      { en: 'Infection Prevention and Control Diploma / Course', ar: 'دبلومة / دورة مكافحة العدوى' },
      { en: 'Hand Hygiene Observer Training', ar: 'تدريب ملاحظ نظافة اليدين' },
      { en: 'Sterilization and Reprocessing Training', ar: 'تدريب التعقيم وإعادة المعالجة' }
    ]
  },
  {
    id: 'dialysis',
    label: { en: 'Dialysis Nurse', ar: 'تمريض الغسيل الكلوي' },
    coreSummary: {
      en: 'Focused on safe hemodialysis preparation, vascular-access care, close monitoring and prevention of treatment-related complications.',
      ar: 'يركز على التحضير الآمن للغسيل الدموي والعناية بمدخل الأوعية والمراقبة الدقيقة والوقاية من مضاعفات العلاج.'
    },
    skills: [
      { en: 'Hemodialysis Nursing', ar: 'تمريض الغسيل الدموي' },
      { en: 'Vascular Access Care', ar: 'العناية بمدخل الأوعية' },
      { en: 'Pre/Post Dialysis Assessment', ar: 'التقييم قبل وبعد الغسيل' },
      { en: 'Fluid Balance Monitoring', ar: 'مراقبة توازن السوائل' },
      { en: 'Dialysis Safety Checks', ar: 'فحوص سلامة الغسيل' },
      { en: 'Complication Recognition', ar: 'اكتشاف المضاعفات' },
      { en: 'Infection Prevention', ar: 'منع العدوى' },
      { en: 'Patient Education', ar: 'تثقيف المريض' }
    ],
    bullets: [
      { en: 'Complete pre- and post-dialysis nursing assessments and document relevant findings.', ar: 'إجراء تقييمات تمريضية قبل وبعد الغسيل وتوثيق النتائج المهمة.' },
      { en: 'Assess and protect vascular access and report signs of dysfunction or infection.', ar: 'تقييم وحماية مدخل الأوعية والإبلاغ عن علامات الخلل أو العدوى.' },
      { en: 'Monitor patients throughout treatment and respond promptly to changes or complications.', ar: 'مراقبة المرضى أثناء الجلسة والاستجابة السريعة للتغيرات أو المضاعفات.' },
      { en: 'Follow dialysis safety checks and infection-prevention procedures according to policy.', ar: 'اتباع فحوص سلامة الغسيل وإجراءات منع العدوى وفق السياسة.' },
      { en: 'Track fluid balance and prescribed treatment parameters accurately.', ar: 'متابعة توازن السوائل ومعايير العلاج الموصوفة بدقة.' },
      { en: 'Educate patients about vascular-access protection and treatment-related self-care.', ar: 'تثقيف المرضى حول حماية مدخل الأوعية والعناية الذاتية المرتبطة بالعلاج.' }
    ],
    keywords: [
      { en: 'Renal Nursing', ar: 'تمريض الكلى' },
      { en: 'Dialysis Safety', ar: 'سلامة الغسيل الكلوي' },
      { en: 'Vascular Access Monitoring', ar: 'مراقبة مدخل الأوعية' }
    ],
    certifications: [
      { en: 'Basic Life Support (BLS)', ar: 'دعم الحياة الأساسي (BLS)' },
      { en: 'Hemodialysis Nursing Training', ar: 'تدريب تمريض الغسيل الكلوي' },
      { en: 'Infection Prevention and Control Training', ar: 'تدريب مكافحة العدوى' }
    ]
  },
  {
    id: 'pediatric',
    label: { en: 'Pediatric Nurse', ar: 'تمريض الأطفال' },
    coreSummary: {
      en: 'Focused on age-appropriate assessment, medication safety, family-centered care and early recognition of pediatric deterioration.',
      ar: 'يركز على التقييم المناسب للعمر وسلامة الدواء والرعاية المتمحورة حول الأسرة والاكتشاف المبكر لتدهور حالة الطفل.'
    },
    skills: [
      { en: 'Pediatric Assessment', ar: 'تقييم الأطفال' },
      { en: 'Weight-based Medication Safety', ar: 'سلامة الأدوية المحسوبة حسب الوزن' },
      { en: 'Family-centered Care', ar: 'الرعاية المتمحورة حول الأسرة' },
      { en: 'Pediatric Vital Signs', ar: 'العلامات الحيوية للأطفال' },
      { en: 'Fluid Balance', ar: 'توازن السوائل' },
      { en: 'Growth and Development Awareness', ar: 'مبادئ النمو والتطور' },
      { en: 'Pediatric Deterioration Recognition', ar: 'اكتشاف تدهور حالة الطفل' },
      { en: 'Parent Education', ar: 'تثقيف الوالدين' }
    ],
    bullets: [
      { en: 'Perform age-appropriate nursing assessments and recognize signs of pediatric deterioration.', ar: 'إجراء تقييمات تمريضية مناسبة للعمر واكتشاف علامات تدهور حالة الطفل.' },
      { en: 'Administer prescribed medications safely with attention to weight-based dosing and verification.', ar: 'إعطاء الأدوية الموصوفة بأمان مع الاهتمام بالجرعات المرتبطة بالوزن والتحقق منها.' },
      { en: 'Monitor hydration, intake and output and relevant pediatric vital signs.', ar: 'مراقبة الترطيب والمدخلات والمخرجات والعلامات الحيوية المناسبة للأطفال.' },
      { en: 'Provide family-centered care and explain procedures in age-appropriate language.', ar: 'تقديم رعاية متمحورة حول الأسرة وشرح الإجراءات بلغة مناسبة للعمر.' },
      { en: 'Apply infection-prevention and safety measures appropriate to pediatric care.', ar: 'تطبيق إجراءات منع العدوى والسلامة المناسبة لرعاية الأطفال.' },
      { en: 'Document assessments, interventions, responses and family education accurately.', ar: 'توثيق التقييمات والتدخلات والاستجابات وتثقيف الأسرة بدقة.' }
    ],
    keywords: [
      { en: 'Pediatric Nursing', ar: 'تمريض الأطفال' },
      { en: 'Family-centered Care', ar: 'الرعاية المتمحورة حول الأسرة' },
      { en: 'Medication Verification', ar: 'التحقق من الدواء' }
    ],
    certifications: [
      { en: 'Basic Life Support (BLS)', ar: 'دعم الحياة الأساسي (BLS)' },
      { en: 'Pediatric Advanced Life Support (PALS)', ar: 'دعم الحياة المتقدم للأطفال (PALS)' },
      { en: 'Pediatric Nursing Training', ar: 'تدريب تمريض الأطفال' }
    ]
  },
  {
    id: 'supervisor',
    label: { en: 'Nursing Supervisor', ar: 'مشرف تمريض' },
    coreSummary: {
      en: 'Focused on shift coordination, safe staffing, escalation, patient flow, documentation quality and support for frontline nursing teams.',
      ar: 'يركز على تنسيق الوردية والتوزيع الآمن للتمريض والتصعيد وتدفق المرضى وجودة التوثيق ودعم فرق التمريض المباشرة.'
    },
    skills: [
      { en: 'Shift Coordination', ar: 'تنسيق الوردية' },
      { en: 'Staff Allocation', ar: 'توزيع أفراد التمريض' },
      { en: 'Clinical Escalation', ar: 'التصعيد السريري' },
      { en: 'Patient Flow', ar: 'تدفق المرضى' },
      { en: 'Documentation Oversight', ar: 'الإشراف على التوثيق' },
      { en: 'Incident Follow-up', ar: 'متابعة الحوادث' },
      { en: 'Team Coaching', ar: 'توجيه الفريق' },
      { en: 'Quality and Patient Safety', ar: 'الجودة وسلامة المرضى' }
    ],
    bullets: [
      { en: 'Coordinate nursing assignments according to patient acuity, workload and available staff.', ar: 'تنسيق توزيع التمريض وفق حدة الحالات وحجم العمل والكوادر المتاحة.' },
      { en: 'Prioritize operational and clinical issues and escalate risks to the appropriate leadership level.', ar: 'ترتيب أولوية المشكلات التشغيلية والسريرية وتصعيد المخاطر للمستوى القيادي المناسب.' },
      { en: 'Support patient flow and redistribute nursing resources when workload changes.', ar: 'دعم تدفق المرضى وإعادة توزيع الموارد التمريضية عند تغير ضغط العمل.' },
      { en: 'Review key documentation and follow up gaps affecting quality, safety or continuity of care.', ar: 'مراجعة عناصر التوثيق المهمة ومتابعة النواقص المؤثرة على الجودة أو السلامة أو استمرارية الرعاية.' },
      { en: 'Coach staff, address workflow barriers and support consistent adherence to policies.', ar: 'توجيه العاملين ومعالجة معوقات سير العمل ودعم الالتزام المستمر بالسياسات.' },
      { en: 'Communicate incidents, staffing concerns and unresolved risks clearly to nursing leadership.', ar: 'إبلاغ قيادة التمريض بوضوح بالحوادث ومشكلات التغطية والمخاطر غير المحلولة.' }
    ],
    keywords: [
      { en: 'Nursing Leadership', ar: 'القيادة التمريضية' },
      { en: 'Workload Prioritization', ar: 'ترتيب أولويات عبء العمل' },
      { en: 'Quality Oversight', ar: 'الإشراف على الجودة' }
    ],
    certifications: [
      { en: 'Basic Life Support (BLS)', ar: 'دعم الحياة الأساسي (BLS)' },
      { en: 'Leadership / Nursing Management Training', ar: 'تدريب القيادة / إدارة التمريض' },
      { en: 'Patient Safety or Quality Training', ar: 'تدريب سلامة المرضى أو الجودة' }
    ]
  }
];

export function getSpecialty(id: string): NursingSpecialty {
  return nursingSpecialties.find(item => item.id === id) || nursingSpecialties[0];
}

export function buildNursingSummary(
  specialty: NursingSpecialty,
  level: NursingLevel,
  market: TargetMarket,
  language: LibraryLanguage
): string {
  const levelItem = nursingLevels.find(item => item.id === level) || nursingLevels[1];
  const marketItem = targetMarkets.find(item => item.id === market) || targetMarkets[0];
  return [levelItem.intro[language], specialty.coreSummary[language], marketItem.emphasis[language]].join(' ');
}

export function getMarketKeywords(market: TargetMarket): LocalText[] {
  return (targetMarkets.find(item => item.id === market) || targetMarkets[0]).keywords;
}
''', encoding='utf-8')

component = root / "components" / "NursingSmartLibrary.tsx"
component.write_text(r'''"use client";

import { useMemo, useState } from "react";
import {
  buildNursingSummary,
  getMarketKeywords,
  getSpecialty,
  nursingLevels,
  nursingSpecialties,
  targetMarkets,
  type LibraryLanguage,
  type NursingLevel,
  type TargetMarket
} from "@/lib/nursingLibrary";

type Props = {
  data: any;
  setData: any;
  language: string;
};

function normalize(value: string) {
  return value.trim().replace(/^[-•]\s*/, "").toLowerCase();
}

function mergeLines(existing: string, additions: string[], splitCommas = false) {
  const source = splitCommas ? existing.split(/[\n,]+/) : existing.split("\n");
  const output = source.map(item => item.trim()).filter(Boolean);
  const seen = new Set(output.map(normalize));
  additions.forEach(item => {
    const clean = item.trim();
    const key = normalize(clean);
    if (clean && !seen.has(key)) {
      seen.add(key);
      output.push(clean);
    }
  });
  return output.join("\n");
}

function createId(prefix: string) {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return prefix + "-" + crypto.randomUUID();
  }
  return prefix + "-" + Date.now() + "-" + Math.random().toString(36).slice(2, 8);
}

export default function NursingSmartLibrary({ data, setData, language }: Props) {
  const lang: LibraryLanguage = language === "ar" ? "ar" : "en";
  const [specialtyId, setSpecialtyId] = useState("emergency");
  const [level, setLevel] = useState<NursingLevel>("experienced");
  const [market, setMarket] = useState<TargetMarket>("ats");
  const [useSummary, setUseSummary] = useState(false);
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [selectedBullets, setSelectedBullets] = useState<string[]>([]);
  const [selectedCerts, setSelectedCerts] = useState<string[]>([]);
  const [experienceIndex, setExperienceIndex] = useState(0);
  const [confirmed, setConfirmed] = useState(false);
  const [message, setMessage] = useState("");

  const specialty = useMemo(() => getSpecialty(specialtyId), [specialtyId]);
  const summary = useMemo(
    () => buildNursingSummary(specialty, level, market, lang),
    [specialty, level, market, lang]
  );
  const marketKeywords = useMemo(() => getMarketKeywords(market), [market]);
  const skillOptions = useMemo(
    () => [...specialty.skills, ...specialty.keywords, ...marketKeywords],
    [specialty, marketKeywords]
  );

  function toggle(list: string[], setter: (value: string[]) => void, value: string) {
    setter(list.includes(value) ? list.filter(item => item !== value) : [...list, value]);
    setMessage("");
  }

  function resetSelections() {
    setUseSummary(false);
    setSelectedSkills([]);
    setSelectedBullets([]);
    setSelectedCerts([]);
    setConfirmed(false);
    setMessage("");
  }

  function selectEssentials() {
    setUseSummary(true);
    setSelectedSkills(skillOptions.slice(0, 6).map(item => item[lang]));
    setSelectedBullets(specialty.bullets.slice(0, 4).map(item => item[lang]));
    setSelectedCerts([]);
    setMessage("");
  }

  function applySelections() {
    const hasAny = useSummary || selectedSkills.length || selectedBullets.length || selectedCerts.length;
    if (!hasAny || !confirmed) return;

    if (useSummary && data.profile && data.profile.trim() && data.profile.trim() !== summary.trim()) {
      const replace = window.confirm(
        lang === "ar"
          ? "يوجد ملخص مهني حالي. هل تريد استبداله بالملخص الذي اخترته؟"
          : "You already have a professional summary. Replace it with the selected summary?"
      );
      if (!replace) return;
    }

    setData((prev: any) => {
      const next = { ...prev };

      if (useSummary) {
        next.profile = summary;
      }

      if (selectedSkills.length) {
        next.skills = mergeLines(prev.skills || "", selectedSkills, true);
      }

      if (selectedBullets.length && Array.isArray(prev.experience) && prev.experience.length) {
        const safeIndex = Math.min(Math.max(experienceIndex, 0), prev.experience.length - 1);
        next.experience = prev.experience.map((item: any, index: number) =>
          index === safeIndex
            ? { ...item, details: mergeLines(item.details || "", selectedBullets) }
            : item
        );
      }

      if (selectedCerts.length) {
        const existing = Array.isArray(prev.certifications) ? prev.certifications : [];
        const known = new Set(existing.map((item: any) => normalize(item.name || "")));
        const additions = selectedCerts
          .filter(name => !known.has(normalize(name)))
          .map(name => ({ id: createId("cert-library"), name, issuer: "", date: "" }));
        next.certifications = [...existing, ...additions];
      }

      return next;
    });

    setMessage(
      lang === "ar"
        ? "تمت إضافة العناصر المختارة. راجعها وعدّلها قبل الحفظ."
        : "Selected items were added. Review and edit them before saving."
    );
    setConfirmed(false);
  }

  const copy = lang === "ar"
    ? {
        eyebrow: "مكتبة Sirati الذكية للتمريض",
        title: "ابدأ من محتوى مهني جاهز بدل الصفحة الفارغة",
        intro: "اختر تخصصك ومستوى الخبرة والسوق المستهدف، ثم اختر فقط العبارات التي تصف خبرتك فعلًا.",
        specialty: "التخصص",
        level: "مستوى الخبرة",
        market: "السوق المستهدف",
        marketNote: "اختيار السوق يغيّر تركيز الصياغة فقط ولا يعني الأهلية أو الترخيص للعمل.",
        summary: "الملخص المهني المقترح",
        useSummary: "استخدم هذا الملخص",
        skills: "المهارات والكلمات المفتاحية",
        bullets: "نقاط خبرة مقترحة",
        experience: "أضف النقاط إلى",
        certifications: "شهادات مقترحة",
        certWarning: "اختر الشهادة فقط إذا كنت حاصلًا عليها فعلًا. لن تضيف Sirati جهة إصدار أو تاريخًا من عندها.",
        achievement: "فكرة إنجاز",
        achievementText: "اكتب إنجازًا فقط إذا كان لديك دليل عليه، مثل تحسن نسبة التزام أو زمن انتظار أو نتيجة تدقيق يمكنك إثباتها.",
        selectEssentials: "اختيار الأساسيات",
        clear: "مسح الاختيارات",
        confirm: "أؤكد أن العناصر التي اخترتها تصف خبرتي أو مهاراتي أو شهاداتي بشكل صحيح.",
        add: "إضافة العناصر المختارة إلى السيرة",
        noRole: "خبرة",
        empty: "اختر عنصرًا واحدًا على الأقل ثم أكد صحته.",
        zero: "بدون تكلفة أو API"
      }
    : {
        eyebrow: "SIRATI SMART NURSING LIBRARY",
        title: "Start with curated professional content instead of a blank page",
        intro: "Choose your specialty, experience level and target market, then select only statements that genuinely describe you.",
        specialty: "Specialty",
        level: "Experience level",
        market: "Target market",
        marketNote: "Target market changes wording emphasis only. It does not imply licensing or eligibility.",
        summary: "Suggested professional summary",
        useSummary: "Use this summary",
        skills: "Skills & ATS keywords",
        bullets: "Suggested experience bullets",
        experience: "Add bullets to",
        certifications: "Suggested certifications",
        certWarning: "Select a certification only if you actually hold it. Sirati will not invent an issuer or date.",
        achievement: "Achievement prompt",
        achievementText: "Add an achievement only when you can verify it, such as a measurable compliance improvement, wait-time reduction or audit result.",
        selectEssentials: "Select essentials",
        clear: "Clear selections",
        confirm: "I confirm the selected items accurately describe my experience, skills or certifications.",
        add: "Add selected items to my CV",
        noRole: "Experience",
        empty: "Select at least one item and confirm it before adding.",
        zero: "Zero-cost · no AI API"
      };

  const hasAny = useSummary || selectedSkills.length > 0 || selectedBullets.length > 0 || selectedCerts.length > 0;

  return (
    <details className="smart-nursing-library">
      <summary className="smart-nursing-summary">
        <div>
          <span className="smart-nursing-eyebrow">{copy.eyebrow}</span>
          <strong>{copy.title}</strong>
        </div>
        <span className="smart-nursing-zero">{copy.zero}</span>
      </summary>

      <div className="smart-nursing-body" dir={lang === "ar" ? "rtl" : "ltr"}>
        <p className="smart-nursing-intro">{copy.intro}</p>

        <div className="smart-nursing-selectors">
          <label>
            <span>{copy.specialty}</span>
            <select value={specialtyId} onChange={event => { setSpecialtyId(event.target.value); resetSelections(); }}>
              {nursingSpecialties.map(item => (
                <option key={item.id} value={item.id}>{item.label[lang]}</option>
              ))}
            </select>
          </label>

          <label>
            <span>{copy.level}</span>
            <select value={level} onChange={event => { setLevel(event.target.value as NursingLevel); resetSelections(); }}>
              {nursingLevels.map(item => (
                <option key={item.id} value={item.id}>{item.label[lang]}</option>
              ))}
            </select>
          </label>

          <label>
            <span>{copy.market}</span>
            <select value={market} onChange={event => { setMarket(event.target.value as TargetMarket); resetSelections(); }}>
              {targetMarkets.map(item => (
                <option key={item.id} value={item.id}>{item.label[lang]}</option>
              ))}
            </select>
          </label>
        </div>

        <p className="smart-nursing-note">{copy.marketNote}</p>

        <section className="smart-library-section">
          <div className="smart-library-heading">
            <h4>{copy.summary}</h4>
            <label className="smart-library-inline-check">
              <input type="checkbox" checked={useSummary} onChange={event => setUseSummary(event.target.checked)} />
              <span>{copy.useSummary}</span>
            </label>
          </div>
          <p className="smart-summary-preview">{summary}</p>
        </section>

        <section className="smart-library-section">
          <h4>{copy.skills}</h4>
          <div className="smart-library-choice-grid">
            {skillOptions.map((item, index) => {
              const value = item[lang];
              return (
                <label className="smart-library-choice" key={value + "-" + index}>
                  <input
                    type="checkbox"
                    checked={selectedSkills.includes(value)}
                    onChange={() => toggle(selectedSkills, setSelectedSkills, value)}
                  />
                  <span>{value}</span>
                </label>
              );
            })}
          </div>
        </section>

        <section className="smart-library-section">
          <div className="smart-library-heading smart-library-heading-stack-mobile">
            <h4>{copy.bullets}</h4>
            <label className="smart-library-target">
              <span>{copy.experience}</span>
              <select
                value={experienceIndex}
                onChange={event => setExperienceIndex(Number(event.target.value))}
                disabled={!data.experience || !data.experience.length}
              >
                {(data.experience || []).map((item: any, index: number) => (
                  <option key={item.id || index} value={index}>
                    {(item.role || item.company || copy.noRole) + " " + (index + 1)}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="smart-library-choice-list">
            {specialty.bullets.map((item, index) => {
              const value = item[lang];
              return (
                <label className="smart-library-choice smart-library-choice-wide" key={value + "-" + index}>
                  <input
                    type="checkbox"
                    checked={selectedBullets.includes(value)}
                    onChange={() => toggle(selectedBullets, setSelectedBullets, value)}
                  />
                  <span>{value}</span>
                </label>
              );
            })}
          </div>
        </section>

        <section className="smart-library-section">
          <h4>{copy.certifications}</h4>
          <p className="smart-nursing-note warning-note">{copy.certWarning}</p>
          <div className="smart-library-choice-grid">
            {specialty.certifications.map((item, index) => {
              const value = item[lang];
              return (
                <label className="smart-library-choice" key={value + "-" + index}>
                  <input
                    type="checkbox"
                    checked={selectedCerts.includes(value)}
                    onChange={() => toggle(selectedCerts, setSelectedCerts, value)}
                  />
                  <span>{value}</span>
                </label>
              );
            })}
          </div>
        </section>

        <section className="smart-achievement-prompt">
          <strong>{copy.achievement}</strong>
          <span>{copy.achievementText}</span>
        </section>

        <div className="smart-library-quick-actions">
          <button type="button" className="text-btn" onClick={selectEssentials}>{copy.selectEssentials}</button>
          <button type="button" className="text-btn" onClick={resetSelections}>{copy.clear}</button>
        </div>

        <label className="smart-library-confirm">
          <input type="checkbox" checked={confirmed} onChange={event => setConfirmed(event.target.checked)} />
          <span>{copy.confirm}</span>
        </label>

        <div className="smart-library-submit-row">
          <button
            type="button"
            className="btn btn-primary"
            disabled={!hasAny || !confirmed}
            onClick={applySelections}
          >
            {copy.add}
          </button>
          {!hasAny && <span className="small">{copy.empty}</span>}
        </div>

        {message && <div className="smart-library-success" role="status">{message}</div>}
      </div>
    </details>
  );
}
''', encoding='utf-8')

builder = root / "app" / "builder" / "page.tsx"
text = builder.read_text(encoding="utf-8")
import_line = "import NursingSmartLibrary from '@/components/NursingSmartLibrary';\n"
if import_line not in text:
    lines = text.splitlines(True)
    first_import = next((i for i, line in enumerate(lines) if line.startswith("import ")), 0)
    lines.insert(first_import, import_line)
    text = "".join(lines)

if "<NursingSmartLibrary" not in text:
    match = re.search(r"(?m)^(\s*)\{step\s*===\s*0\s*&&\s*\(", text)
    if not match:
        raise SystemExit("Could not locate step 0 insertion point in builder")
    indent = match.group(1)
    widget = (
        indent + "<NursingSmartLibrary data={data} setData={setData} language={language} />\n"
    )
    text = text[:match.start()] + widget + text[match.start():]

builder.write_text(text, encoding="utf-8")

css_path = root / "app" / "globals.css"
css = css_path.read_text(encoding="utf-8")
marker = "/* Smart Nursing CV Library */"
if marker not in css:
    css += r'''

/* Smart Nursing CV Library */
.smart-nursing-library {
  margin: 0 0 18px;
  border: 1px solid rgba(37, 99, 235, .18);
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(239, 246, 255, .86), #fff 34%);
  box-shadow: 0 14px 34px rgba(15, 23, 42, .06);
  overflow: hidden;
}
.smart-nursing-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 17px 18px;
  cursor: pointer;
  list-style: none;
}
.smart-nursing-summary::-webkit-details-marker { display: none; }
.smart-nursing-summary > div { display: grid; gap: 3px; min-width: 0; }
.smart-nursing-summary strong { font-size: 15px; line-height: 1.3; }
.smart-nursing-eyebrow {
  color: #2563eb;
  font-size: 10px;
  font-weight: 850;
  letter-spacing: .1em;
}
.smart-nursing-zero {
  flex: 0 0 auto;
  padding: 7px 10px;
  border: 1px solid rgba(37, 99, 235, .18);
  border-radius: 999px;
  background: #fff;
  color: #1d4ed8;
  font-size: 11px;
  font-weight: 750;
}
.smart-nursing-body {
  padding: 0 18px 18px;
  border-top: 1px solid rgba(37, 99, 235, .10);
}
.smart-nursing-intro {
  margin: 15px 0 14px;
  color: #475569;
  font-size: 13px;
  line-height: 1.5;
}
.smart-nursing-selectors {
  display: grid;
  grid-template-columns: 1.25fr 1fr 1fr;
  gap: 10px;
}
.smart-nursing-selectors label,
.smart-library-target {
  display: grid;
  gap: 5px;
}
.smart-nursing-selectors label > span,
.smart-library-target > span {
  color: #475569;
  font-size: 11px;
  font-weight: 750;
}
.smart-nursing-selectors select,
.smart-library-target select {
  width: 100%;
  min-height: 42px;
  padding: 0 10px;
  border: 1px solid #dbe3ee;
  border-radius: 10px;
  background: #fff;
  color: #0f172a;
  font: inherit;
}
.smart-nursing-note {
  margin: 9px 0 0;
  color: #64748b;
  font-size: 11.5px;
  line-height: 1.45;
}
.warning-note {
  margin: -1px 0 9px;
  color: #92400e;
}
.smart-library-section {
  margin-top: 15px;
  padding-top: 14px;
  border-top: 1px solid #e2e8f0;
}
.smart-library-section h4 {
  margin: 0;
  font-size: 13px;
}
.smart-library-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 9px;
}
.smart-library-inline-check,
.smart-library-confirm {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: #334155;
  font-size: 12px;
  line-height: 1.4;
}
.smart-library-inline-check input,
.smart-library-confirm input,
.smart-library-choice input {
  flex: 0 0 auto;
  margin-top: 2px;
  accent-color: #2563eb;
}
.smart-summary-preview {
  margin: 0;
  padding: 12px 13px;
  border: 1px solid #dbeafe;
  border-radius: 11px;
  background: #f8fbff;
  color: #1e293b;
  font-size: 12.5px;
  line-height: 1.5;
}
.smart-library-choice-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 7px;
  margin-top: 9px;
}
.smart-library-choice-list {
  display: grid;
  gap: 7px;
  margin-top: 9px;
}
.smart-library-choice {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  min-height: 38px;
  padding: 9px 10px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
  color: #334155;
  font-size: 11.8px;
  line-height: 1.35;
}
.smart-library-choice:has(input:checked) {
  border-color: #93c5fd;
  background: #eff6ff;
  color: #1e3a8a;
}
.smart-library-choice-wide { min-height: 0; }
.smart-library-target {
  width: min(280px, 100%);
}
.smart-achievement-prompt {
  display: grid;
  gap: 4px;
  margin-top: 15px;
  padding: 11px 12px;
  border: 1px dashed #cbd5e1;
  border-radius: 10px;
  background: #f8fafc;
}
.smart-achievement-prompt strong {
  color: #334155;
  font-size: 12px;
}
.smart-achievement-prompt span {
  color: #64748b;
  font-size: 11.5px;
  line-height: 1.45;
}
.smart-library-quick-actions {
  display: flex;
  gap: 12px;
  margin: 14px 0 10px;
}
.smart-library-confirm {
  padding: 11px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: #fff;
}
.smart-library-submit-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 11px;
  flex-wrap: wrap;
}
.smart-library-submit-row .btn:disabled {
  opacity: .45;
  cursor: not-allowed;
}
.smart-library-success {
  margin-top: 10px;
  padding: 9px 11px;
  border: 1px solid #bbf7d0;
  border-radius: 10px;
  background: #f0fdf4;
  color: #166534;
  font-size: 12px;
  font-weight: 650;
}

@media (max-width: 760px) {
  .smart-nursing-summary {
    align-items: flex-start;
    padding: 14px;
  }
  .smart-nursing-zero {
    max-width: 120px;
    white-space: normal;
    text-align: center;
  }
  .smart-nursing-body { padding: 0 14px 15px; }
  .smart-nursing-selectors { grid-template-columns: 1fr; }
  .smart-library-choice-grid { grid-template-columns: 1fr; }
  .smart-library-heading-stack-mobile {
    align-items: stretch;
    flex-direction: column;
  }
  .smart-library-target { width: 100%; }
  .smart-library-submit-row .btn { width: 100%; justify-content: center; }
}
'''
    css_path.write_text(css, encoding='utf-8')

print("Applied Smart Nursing CV Library.")
