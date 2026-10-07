from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
component_path = root / "components" / "TargetJobTailor.tsx"
component_path.parent.mkdir(parents=True, exist_ok=True)

component_path.write_text(r''' 'use client';

import { useEffect, useMemo, useState } from 'react';

type Language = 'en' | 'ar';
type Category = 'skills' | 'experience' | 'certifications' | 'education' | 'languages';
type Priority = 'required' | 'preferred' | 'general';

type Requirement = {
  term: string;
  category: Category;
  priority: Priority;
  weight: number;
  variants: string[];
  matched: boolean;
};

type SynonymGroup = {
  label: string;
  category: Category;
  variants: string[];
};

const STOPWORDS = new Set([
  'and','the','for','with','that','this','from','your','you','our','are','will','have','has','into','who','job','role',
  'work','working','using','within','about','their','they','them','but','not','all','any','can','may','must','should',
  'required','preferred','including','include','responsible','responsibilities','requirements','requirement','qualification',
  'qualifications','years','year','experience','skills','skill','ability','strong','excellent','good','team','teams',
  'position','candidate','minimum','plus','knowledge','understanding','demonstrated','proven','support','supports','supporting',
  'basic','patient','patients','nursing','nurse','emergency','department','hospital','healthcare','clinical','medical','license','licence','licensed','certification','certified',
  'في','من','على','إلى','الى','عن','مع','هذا','هذه','ذلك','تلك','التي','الذي','الذين','و','أو','او','أن','ان','كما',
  'يجب','يفضل','مطلوب','المطلوب','خبرة','سنوات','سنة','مهارات','مهارة','القدرة','العمل','فريق','ضمن','مسؤول','مسؤوليات',
  'الوظيفة','الدور','المتطلبات','المؤهلات','جيد','ممتاز','قوي','لدى','لديه','لديها','معرفة','فهم','دعم','خبرات'
]);

const SYNONYM_GROUPS: SynonymGroup[] = [
  { label: 'Emergency Department', category: 'experience', variants: ['emergency department','emergency room','er','ed','قسم الطوارئ','الطوارئ'] },
  { label: 'Critical Care / ICU', category: 'experience', variants: ['critical care','intensive care','icu','العناية المركزة','الرعاية الحرجة'] },
  { label: 'Triage', category: 'skills', variants: ['triage','patient prioritization','فرز','الفرز','ترتيب اولوية المرضى','ترتيب أولوية المرضى'] },
  { label: 'Patient Safety', category: 'skills', variants: ['patient safety','سلامة المرضى'] },
  { label: 'Clinical Documentation', category: 'skills', variants: ['clinical documentation','medical documentation','documentation','التوثيق السريري','التوثيق الطبي'] },
  { label: 'Infection Prevention and Control', category: 'skills', variants: ['infection prevention and control','infection control','ipc','مكافحة العدوى','منع العدوى'] },
  { label: 'Quality Improvement', category: 'skills', variants: ['quality improvement','continuous improvement','qi','تحسين الجودة','التحسين المستمر'] },
  { label: 'Medication Administration', category: 'skills', variants: ['medication administration','medication safety','administer medications','إعطاء الأدوية','سلامة الدواء'] },
  { label: 'ECG Monitoring', category: 'skills', variants: ['ecg monitoring','ecg','ekg','cardiac monitoring','مراقبة تخطيط القلب','تخطيط القلب'] },
  { label: 'Ventilator Care', category: 'skills', variants: ['ventilator care','mechanical ventilation','ventilation','جهاز التنفس الصناعي','التنفس الصناعي'] },
  { label: 'Hemodynamic Monitoring', category: 'skills', variants: ['hemodynamic monitoring','haemodynamic monitoring','المراقبة الديناميكية الدموية'] },
  { label: 'Wound Care', category: 'skills', variants: ['wound care','wound management','العناية بالجروح'] },
  { label: 'Care Coordination', category: 'skills', variants: ['care coordination','clinical coordination','تنسيق الرعاية'] },
  { label: 'Multidisciplinary Collaboration', category: 'skills', variants: ['multidisciplinary collaboration','multidisciplinary team','interdisciplinary team','multidisciplinary teamwork','فريق متعدد التخصصات','التعاون متعدد التخصصات'] },
  { label: 'Leadership', category: 'skills', variants: ['leadership','team leadership','staff leadership','قيادة الفريق','القيادة'] },
  { label: 'Supervision', category: 'experience', variants: ['supervision','supervisory','shift supervision','staff supervision','الإشراف','مشرف','إشراف الوردية'] },
  { label: 'Project Management', category: 'skills', variants: ['project management','project coordination','إدارة المشاريع','تنسيق المشاريع'] },
  { label: 'Data Analysis', category: 'skills', variants: ['data analysis','analytics','تحليل البيانات'] },
  { label: 'Risk Management', category: 'skills', variants: ['risk management','clinical risk','إدارة المخاطر'] },
  { label: 'Customer Service', category: 'skills', variants: ['customer service','client service','خدمة العملاء'] },
  { label: 'Problem Solving', category: 'skills', variants: ['problem solving','problem-solving','حل المشكلات'] },
  { label: 'Microsoft Excel', category: 'skills', variants: ['microsoft excel','excel','اكسل','إكسل'] },
  { label: 'Electronic Medical Records', category: 'skills', variants: ['electronic medical records','electronic health records','emr','ehr','السجلات الطبية الإلكترونية','السجل الطبي الإلكتروني'] },
  { label: 'Basic Life Support (BLS)', category: 'certifications', variants: ['basic life support','bls','دعم الحياة الأساسي'] },
  { label: 'Advanced Cardiovascular Life Support (ACLS)', category: 'certifications', variants: ['advanced cardiovascular life support','advanced cardiac life support','acls','دعم الحياة القلبي المتقدم'] },
  { label: 'Pediatric Advanced Life Support (PALS)', category: 'certifications', variants: ['pediatric advanced life support','paediatric advanced life support','pals','دعم الحياة المتقدم للأطفال'] },
  { label: 'Registered Nurse / RN License', category: 'certifications', variants: ['registered nurse','rn license','nursing license','licensure','ترخيص التمريض','ترخيص مزاولة المهنة','ممرض مسجل'] },
  { label: 'Bachelor Degree', category: 'education', variants: ['bachelor degree','bachelor\'s degree','bsc','bsn','bachelor of science','درجة البكالوريوس','بكالوريوس'] },
  { label: 'Master Degree', category: 'education', variants: ['master degree','master\'s degree','msc','master of science','درجة الماجستير','ماجستير'] },
  { label: 'Diploma', category: 'education', variants: ['diploma','postgraduate diploma','دبلومة','دبلوم'] },
  { label: 'Dubai Health Authority (DHA) License', category: 'certifications', variants: ['dha license','dha licence','dha eligibility','dha eligible','dubai health authority','ترخيص dha','اهلية dha','أهلية dha'] },
  { label: 'Department of Health Abu Dhabi (DOH/HAAD) License', category: 'certifications', variants: ['doh license','doh licence','doh eligibility','haad license','haad licence','department of health abu dhabi','ترخيص doh','ترخيص haad'] },
  { label: 'MOHAP License', category: 'certifications', variants: ['mohap license','mohap licence','moh license','ministry of health uae license','ترخيص mohap','ترخيص وزارة الصحة الامارات'] },
  { label: 'SCFHS Registration', category: 'certifications', variants: ['scfhs','saudi commission for health specialties','saudi council license','saudi nursing license','تصنيف الهيئة السعودية','تسجيل الهيئة السعودية','الهيئة السعودية للتخصصات الصحية'] },
  { label: 'Trauma Nursing Core Course (TNCC)', category: 'certifications', variants: ['tncc','trauma nursing core course','دورة تمريض الإصابات','تمريض الاصابات'] },
  { label: 'Vital Signs Monitoring', category: 'skills', variants: ['vital signs','vital signs monitoring','monitor vital signs','العلامات الحيوية','مراقبة العلامات الحيوية'] },
  { label: 'Communication Skills', category: 'skills', variants: ['communication skills','effective communication','interpersonal communication','مهارات التواصل','التواصل الفعال'] },
  { label: 'Computer Skills', category: 'skills', variants: ['computer skills','computer proficiency','basic computer skills','it skills','مهارات الحاسب','مهارات الكمبيوتر','مهارات الحاسب الآلي'] },
  { label: 'English Language', category: 'languages', variants: ['english language','english proficiency','fluent english','english speaking','english','اللغة الإنجليزية','اللغه الانجليزيه','الإنجليزية','انجليزي'] },
  { label: 'Arabic Language', category: 'languages', variants: ['arabic language','arabic proficiency','fluent arabic','arabic speaking','arabic','اللغة العربية','اللغه العربيه','العربية'] },
];

const CATEGORY_ORDER: Category[] = ['skills', 'experience', 'certifications', 'education', 'languages'];

const REQUIRED_MARKERS = [
  'required','must','essential','mandatory','minimum','need to','needs to','shall',
  'مطلوب','يجب','شرط','اساسي','أساسي','ضروري','حد ادنى','حد أدنى'
];

const PREFERRED_MARKERS = [
  'preferred','desirable','nice to have','a plus','advantage','ideally',
  'يفضل','مفضل','ميزة اضافية','ميزة إضافية','افضلية','أفضلية'
];

const CATEGORY_MARKERS: Record<Category, string[]> = {
  skills: [
    'skill','skills','proficiency','competency','competencies','knowledge','ability','abilities',
    'مهارة','مهارات','إجادة','اجادة','كفاءة','كفاءات','معرفة','قدرة'
  ],
  experience: [
    'experience','responsibility','responsibilities','duties','responsible for','manage','monitor','assess','administer',
    'coordinate','perform','provide','lead','supervise','maintain','document','خبرة','مسؤوليات','مهام','إدارة','ادارة',
    'مراقبة','تقييم','تنسيق','تنفيذ','تقديم','قيادة','إشراف','اشراف','توثيق'
  ],
  certifications: [
    'certification','certifications','certified','license','licence','licensure','registration','credential',
    'شهادة','شهادات','معتمد','ترخيص','تسجيل مهني','اعتماد مهني'
  ],
  education: [
    'education','degree','bachelor','master','diploma','university','college','academic',
    'تعليم','مؤهل','بكالوريوس','ماجستير','دبلوم','دبلومة','جامعة','كلية','اكاديمي','أكاديمي'
  ],
  languages: [
    'language','languages','english','arabic','fluent','proficiency',
    'لغة','لغات','انجليزي','إنجليزي','عربي','العربية','الإنجليزية'
  ],
};

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

function containsNormalized(haystack: string, needle: string) {
  const cleanNeedle = normalize(needle);
  if (!cleanNeedle) return false;
  if (cleanNeedle.length <= 3 && !cleanNeedle.includes(' ')) {
    return (` ${haystack} `).includes(` ${cleanNeedle} `);
  }
  return haystack.includes(cleanNeedle);
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

function getPriority(text: string): Priority {
  const clean = normalize(text);
  if (REQUIRED_MARKERS.some((marker) => containsNormalized(clean, marker))) return 'required';
  if (PREFERRED_MARKERS.some((marker) => containsNormalized(clean, marker))) return 'preferred';
  return 'general';
}

function getCategory(text: string): Category {
  const clean = normalize(text);
  const scores = CATEGORY_ORDER.map((category) => ({
    category,
    score: CATEGORY_MARKERS[category].reduce(
      (sum, marker) => sum + (containsNormalized(clean, marker) ? 1 : 0),
      0
    ),
  })).sort((a, b) => b.score - a.score);

  if (scores[0].score > 0) return scores[0].category;
  return 'skills';
}

function requirementWeight(priority: Priority, known: boolean) {
  const priorityWeight = priority === 'required' ? 5 : priority === 'preferred' ? 3 : 2;
  return priorityWeight + (known ? 2 : 0);
}

function extractMinimumExperience(segments: string[]) {
  const found: Array<{ years: number; priority: Priority; source: string }> = [];
  const patterns = [
    /(\d{1,2})\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:relevant\s+|clinical\s+|professional\s+)?experience/i,
    /(?:minimum|min\.?|at least)\s*(\d{1,2})\s*\+?\s*(?:years?|yrs?)/i,
    /(?:خبرة|خبره)\s*(?:لا تقل عن\s*)?(\d{1,2})\s*(?:سنوات|سنين|سنة|سنه)/i,
    /(?:حد ادنى|حد أدنى)\s*(\d{1,2})\s*(?:سنوات|سنين|سنة|سنه)/i,
  ];

  for (const segment of segments) {
    for (const pattern of patterns) {
      const match = segment.match(pattern);
      if (!match) continue;
      const years = Number(match[1]);
      if (!Number.isFinite(years) || years < 1 || years > 30) continue;
      found.push({ years, priority: getPriority(segment), source: segment });
      break;
    }
  }

  if (!found.length) return null;
  return found.sort((a, b) => b.years - a.years)[0];
}

function conceptFallbacks(segments: string[]) {
  const candidates: Array<{ term: string; category: Category; priority: Priority; score: number }> = [];

  for (const segment of segments) {
    const priority = getPriority(segment);
    const category = getCategory(segment);
    const clean = normalize(segment)
      .replace(/\b(required|preferred|essential|mandatory|minimum|responsible for|requirements?|qualifications?)\b/g, ' ')
      .replace(/\b(مطلوب|يفضل|اساسي|أساسي|ضروري|المتطلبات|المؤهلات|المسؤوليات|المهام)\b/g, ' ')
      .replace(/\s+/g, ' ')
      .trim();

    const chunks = clean
      .split(/,|\band\b|\bor\b|\bwith\b|\bplus\b|،| و | أو /)
      .map((chunk) => chunk.trim())
      .filter(Boolean);

    for (const chunk of chunks) {
      const words = chunk.split(' ').filter((word) =>
        word.length >= 3 &&
        !STOPWORDS.has(word) &&
        !/^\d+$/.test(word)
      );
      if (words.length < 2 || words.length > 5) continue;
      const term = words.join(' ');
      if (term.length < 7) continue;
      if (SYNONYM_GROUPS.some((group) =>
        group.variants.some((variant) => containsNormalized(term, variant) || containsNormalized(normalize(variant), term))
      )) continue;
      candidates.push({
        term,
        category,
        priority,
        score: (priority === 'required' ? 5 : priority === 'preferred' ? 3 : 1) + Math.min(words.length, 3),
      });
    }
  }

  const unique = new Map<string, { term: string; category: Category; priority: Priority; score: number }>();
  for (const candidate of candidates) {
    const key = normalize(candidate.term);
    const existing = unique.get(key);
    if (!existing || candidate.score > existing.score) unique.set(key, candidate);
  }

  return Array.from(unique.values())
    .sort((a, b) => b.score - a.score || b.term.length - a.term.length)
    .slice(0, 5);
}

function extractRequirements(title: string, description: string) {
  const cleanDescription = normalize(description);
  const found = new Map<string, Omit<Requirement, 'matched'>>();
  const segments = description
    .split(/\n|[.!?;•]+/)
    .map((segment) => segment.trim())
    .filter(Boolean);

  const add = (
    term: string,
    category: Category,
    priority: Priority,
    variants: string[],
    weight: number
  ) => {
    const key = normalize(term);
    if (!key || key.length < 2 || STOPWORDS.has(key)) return;
    const existing = found.get(key);
    if (!existing || weight > existing.weight) {
      found.set(key, {
        term,
        category,
        priority,
        variants: Array.from(new Set(variants.map((variant) => normalize(variant)).filter(Boolean))),
        weight,
      });
    }
  };

  for (const group of SYNONYM_GROUPS) {
    const sourceSegment = segments.find((segment) =>
      group.variants.some((variant) => containsNormalized(normalize(segment), variant))
    );
    if (!sourceSegment) continue;
    const priority = getPriority(sourceSegment);
    add(group.label, group.category, priority, group.variants, requirementWeight(priority, true));
  }

  const minimumExperience = extractMinimumExperience(segments);
  if (minimumExperience) {
    const y = minimumExperience.years;
    add(
      `Minimum ${y} years experience`,
      'experience',
      minimumExperience.priority === 'general' ? 'required' : minimumExperience.priority,
      [`${y} years experience`, `${y}+ years experience`, `${y} yrs experience`, `${y}+ yrs`],
      requirementWeight(minimumExperience.priority === 'general' ? 'required' : minimumExperience.priority, true) + 1
    );
  }

  for (const fallback of conceptFallbacks(segments)) {
    add(
      fallback.term,
      fallback.category,
      fallback.priority,
      [fallback.term],
      requirementWeight(fallback.priority, false)
    );
  }

  return Array.from(found.values())
    .sort((a, b) => {
      const priorityRank = { required: 3, preferred: 2, general: 1 };
      return priorityRank[b.priority] - priorityRank[a.priority] || b.weight - a.weight;
    })
    .slice(0, 22);
}

function matchRequirement(cvText: string, requirement: Omit<Requirement, 'matched'>) {
  const yearsMatch = requirement.term.match(/^Minimum (\d{1,2}) years experience$/i);
  if (yearsMatch) {
    const requiredYears = Number(yearsMatch[1]);
    const explicitYears = Array.from(cvText.matchAll(/(\d{1,2})\s*\+?\s*(?:years?|yrs?)\s+(?:of\s+)?experience/gi))
      .map((match) => Number(match[1]))
      .filter((value) => Number.isFinite(value));
    if (explicitYears.some((value) => value >= requiredYears)) return true;
  }
  return requirement.variants.some((variant) => containsNormalized(cvText, variant));
}

function coverageFor(items: Requirement[]) {
  const total = items.reduce((sum, item) => sum + item.weight, 0);
  if (!total) return 0;
  const matched = items.reduce((sum, item) => sum + (item.matched ? item.weight : 0), 0);
  return Math.round((matched / total) * 100);
}

function currentStorageScope() {
  if (typeof window === 'undefined') return { key: '', persistent: false };
  const docId = new URLSearchParams(window.location.search).get('doc');
  return docId
    ? { key: `sirati.jobTailor.v2.doc.${docId}`, persistent: true }
    : { key: 'sirati.jobTailor.v2.draft', persistent: false };
}

function readSavedTarget(scope: { key: string; persistent: boolean }) {
  if (!scope.key || typeof window === 'undefined') return null;
  try {
    const raw = scope.persistent ? localStorage.getItem(scope.key) : sessionStorage.getItem(scope.key);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    return {
      targetRole: typeof parsed.targetRole === 'string' ? parsed.targetRole : '',
      jobDescription: typeof parsed.jobDescription === 'string' ? parsed.jobDescription : '',
    };
  } catch {
    return null;
  }
}

function writeSavedTarget(scope: { key: string; persistent: boolean }, targetRole: string, jobDescription: string) {
  if (!scope.key || typeof window === 'undefined') return;
  const store = scope.persistent ? localStorage : sessionStorage;
  if (!targetRole.trim() && !jobDescription.trim()) {
    store.removeItem(scope.key);
    return;
  }
  store.setItem(scope.key, JSON.stringify({ version: 2, targetRole, jobDescription }));
}

function findBuilderSection(category: Category) {
  const patterns: Record<Category, RegExp> = {
    skills: /skills|competencies|مهارات|الكفاءات/i,
    experience: /experience|employment|work history|الخبرة|العمل/i,
    certifications: /certifications|licenses|credentials|الشهادات|التراخيص/i,
    education: /education|degree|academic|التعليم|المؤهل/i,
    languages: /languages|language|اللغات|اللغة/i,
  };
  const headings = Array.from(
    document.querySelectorAll<HTMLElement>('main h2, main h3, main legend, .wizard-panel h2, .wizard-panel h3')
  );
  return headings.find((heading) => patterns[category].test((heading.innerText || heading.textContent || '').trim()));
}

export default function TargetJobTailor() {
  const [enabled, setEnabled] = useState(false);
  const [open, setOpen] = useState(false);
  const [language, setLanguage] = useState<Language>('en');
  const [targetRole, setTargetRole] = useState('');
  const [jobDescription, setJobDescription] = useState('');
  const [cvText, setCvText] = useState('');
  const [storageScope, setStorageScope] = useState<{ key: string; persistent: boolean }>({ key: '', persistent: false });
  const [storageReady, setStorageReady] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const onBuilder = window.location.pathname.includes('/builder');
    setEnabled(onBuilder);
    if (!onBuilder) return;

    const initialScope = currentStorageScope();
    setStorageScope(initialScope);
    const saved = readSavedTarget(initialScope);
    if (saved) {
      setTargetRole(saved.targetRole);
      setJobDescription(saved.jobDescription);
    }
    // Do not persist until the initial storage read has finished.
    // Otherwise the first empty render can erase a valid saved Job Match draft.
    setStorageReady(true);

    const scan = () => {
      setLanguage(detectLanguage());
      setCvText(collectCvText());
      const nextScope = currentStorageScope();
      setStorageScope((previous) =>
        previous.key === nextScope.key && previous.persistent === nextScope.persistent
          ? previous
          : nextScope
      );
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

  useEffect(() => {
    if (!enabled || !storageReady || !storageScope.key) return;
    writeSavedTarget(storageScope, targetRole, jobDescription);
  }, [enabled, storageReady, storageScope, targetRole, jobDescription]);

  useEffect(() => {
    if (!open) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener('keydown', onKey);
    };
  }, [open]);

  const analysisReady = normalize(jobDescription).length >= 40;

  const requirements = useMemo<Requirement[]>(() => {
    if (!analysisReady) return [];
    return extractRequirements(targetRole, jobDescription).map((item) => ({
      ...item,
      matched: matchRequirement(cvText, item),
    }));
  }, [targetRole, jobDescription, cvText, analysisReady]);

  const coverage = coverageFor(requirements);
  const requiredItems = requirements.filter((item) => item.priority === 'required');
  const requiredCoverage = requiredItems.length ? coverageFor(requiredItems) : null;
  const missing = requirements.filter((item) => !item.matched);
  const missingRequired = missing.filter((item) => item.priority === 'required');

  const breakdowns = CATEGORY_ORDER.map((category) => {
    const items = requirements.filter((item) => item.category === category);
    return {
      category,
      items,
      coverage: coverageFor(items),
      matched: items.filter((item) => item.matched).length,
      total: items.length,
    };
  }).filter((item) => item.total > 0);

  if (!enabled) return null;

  const copy = language === 'ar'
    ? {
        trigger: 'مركز مطابقة الوظيفة',
        eyebrow: 'SIRATI JOB MATCH',
        title: 'خصّص سيرتك للوظيفة المستهدفة',
        subtitle: 'حلّل المتطلبات المهمة واعرف أين تحتاج سيرتك إلى مراجعة — بدون إضافة معلومات من تلقاء نفسها.',
        role: 'المسمى الوظيفي المستهدف',
        rolePlaceholder: 'مثال: ممرض طوارئ',
        jd: 'إعلان / وصف الوظيفة',
        jdPlaceholder: 'الصق إعلان الوظيفة هنا...',
        helper: 'الصق وصفًا لا يقل عن عدة أسطر لبدء تحليل المتطلبات.',
        overall: 'التغطية الإجمالية',
        mustHave: 'المتطلبات الأساسية',
        requiredMissing: 'متطلبات أساسية تحتاج مراجعة',
        breakdown: 'تفصيل المطابقة',
        matched: 'مطابق',
        review: 'يحتاج مراجعة',
        requirementAnalysis: 'تحليل المتطلبات',
        required: 'أساسي',
        preferred: 'مفضل',
        general: 'عام',
        skills: 'المهارات',
        experience: 'الخبرة والمسؤوليات',
        certifications: 'الشهادات والتراخيص',
        education: 'التعليم',
        languages: 'اللغات',
        alreadyThere: 'موجود',
        missingLabel: 'راجع',
        reviewSection: 'راجع هذا القسم',
        noRequirements: 'لم يتم استخراج متطلبات كافية بعد.',
        noRequiredMissing: 'لا توجد متطلبات أساسية ناقصة ضمن العناصر المستخرجة.',
        clear: 'مسح',
        close: 'إغلاق',
        storagePersistent: 'محفوظ على هذا الجهاز لهذه السيرة.',
        storageDraft: 'محفوظ مؤقتًا في هذا التبويب حتى تصبح للسيرة نسخة محفوظة.',
        safety: 'لا تضف أي مهارة أو خبرة أو شهادة إلا إذا كانت صحيحة لديك بالفعل. Sirati لا ينسخ ادعاءات إعلان الوظيفة إلى سيرتك تلقائيًا.',
        disclaimer: 'النسب هنا لقياس تغطية المتطلبات والكلمات المهمة فقط؛ ليست ATS Score ولا ضمانًا للمقابلة أو القبول.',
      }
    : {
        trigger: 'Job Match Center',
        eyebrow: 'SIRATI JOB MATCH',
        title: 'Tailor your CV to the target job',
        subtitle: 'Break down the important requirements and see exactly where your CV needs review — without inventing facts.',
        role: 'Target job title',
        rolePlaceholder: 'e.g. Emergency Nurse',
        jd: 'Job ad / description',
        jdPlaceholder: 'Paste the job description here...',
        helper: 'Paste a few lines of the job description to start the requirements analysis.',
        overall: 'Overall coverage',
        mustHave: 'Must-have coverage',
        requiredMissing: 'Must-have items to review',
        breakdown: 'Match breakdown',
        matched: 'Matched',
        review: 'Needs review',
        requirementAnalysis: 'Requirements analysis',
        required: 'Required',
        preferred: 'Preferred',
        general: 'General',
        skills: 'Skills',
        experience: 'Experience & responsibilities',
        certifications: 'Certifications & licenses',
        education: 'Education',
        languages: 'Languages',
        alreadyThere: 'Found',
        missingLabel: 'Review',
        reviewSection: 'Review this section',
        noRequirements: 'Not enough requirements were extracted yet.',
        noRequiredMissing: 'No missing must-have items were found in the extracted requirements.',
        clear: 'Clear',
        close: 'Close',
        storagePersistent: 'Saved on this device for this CV.',
        storageDraft: 'Kept in this tab until the CV has a saved document ID.',
        safety: 'Only add a skill, responsibility, certification, or qualification when it is genuinely true for you. Sirati never copies job-ad claims into your CV automatically.',
        disclaimer: 'These percentages measure requirement and keyword coverage only. They are not an ATS score or a hiring guarantee.',
      };

  const categoryLabel = (category: Category) => copy[category];
  const priorityLabel = (priority: Priority) =>
    priority === 'required' ? copy.required : priority === 'preferred' ? copy.preferred : copy.general;

  const goToSection = (category: Category) => {
    const section = findBuilderSection(category) || (category === 'languages' ? findBuilderSection('skills') : undefined);
    setOpen(false);
    if (section) {
      window.setTimeout(() => section.scrollIntoView({ behavior: 'smooth', block: 'start' }), 80);
    }
  };

  return (
    <aside className="job-tailor" dir={language === 'ar' ? 'rtl' : 'ltr'} aria-label={copy.trigger}>
      <button
        type="button"
        className="job-tailor__trigger"
        onClick={() => setOpen(true)}
        aria-expanded={open}
      >
        <span>{copy.trigger}</span>
        <strong aria-hidden="true">◎</strong>
      </button>

      {open && (
        <div
          className="job-tailor__backdrop"
          onMouseDown={(event) => {
            if (event.currentTarget === event.target) setOpen(false);
          }}
        >
          <div className="job-tailor__panel" role="dialog" aria-modal="true" aria-label={copy.title}>
            <header className="job-tailor__heading">
              <div>
                <small>{copy.eyebrow}</small>
                <h3>{copy.title}</h3>
                <p>{copy.subtitle}</p>
              </div>
              <button type="button" className="job-tailor__close" onClick={() => setOpen(false)} aria-label={copy.close}>×</button>
            </header>

            <div className="job-tailor__inputs">
              <label className="job-tailor__field">
                <span>{copy.role}</span>
                <input
                  type="text"
                  value={targetRole}
                  onChange={(event) => {
                    const nextRole = event.target.value;
                    setTargetRole(nextRole);
                    writeSavedTarget(currentStorageScope(), nextRole, jobDescription);
                  }}
                  placeholder={copy.rolePlaceholder}
                  autoComplete="off"
                />
              </label>

              <label className="job-tailor__field">
                <span>{copy.jd}</span>
                <textarea
                  value={jobDescription}
                  onChange={(event) => {
                    const nextDescription = event.target.value;
                    setJobDescription(nextDescription);
                    writeSavedTarget(currentStorageScope(), targetRole, nextDescription);
                  }}
                  placeholder={copy.jdPlaceholder}
                  rows={7}
                />
              </label>

              <div className="job-tailor__input-meta">
                <small>{storageScope.persistent ? copy.storagePersistent : copy.storageDraft}</small>
                {(targetRole || jobDescription) && (
                  <button
                    type="button"
                    className="job-tailor__clear"
                    onClick={() => {
                      setTargetRole('');
                      setJobDescription('');
                      writeSavedTarget(currentStorageScope(), '', '');
                    }}
                  >
                    {copy.clear}
                  </button>
                )}
              </div>
            </div>

            {!analysisReady ? (
              <div className="job-tailor__empty">
                <strong>◎</strong>
                <p>{copy.helper}</p>
              </div>
            ) : requirements.length === 0 ? (
              <div className="job-tailor__empty">
                <strong>○</strong>
                <p>{copy.noRequirements}</p>
              </div>
            ) : (
              <div className="job-tailor__analysis">
                <section className="job-tailor__score-grid">
                  <article className="job-tailor__score">
                    <small>{copy.overall}</small>
                    <strong>{coverage}%</strong>
                    <div className="job-tailor__bar" aria-hidden="true"><span style={{ width: `${coverage}%` }} /></div>
                  </article>
                  <article className="job-tailor__score">
                    <small>{copy.mustHave}</small>
                    <strong>{requiredCoverage === null ? '—' : `${requiredCoverage}%`}</strong>
                    <div className="job-tailor__bar" aria-hidden="true">
                      <span style={{ width: `${requiredCoverage ?? 0}%` }} />
                    </div>
                  </article>
                </section>

                <section className="job-tailor__section">
                  <div className="job-tailor__section-title">
                    <h4>{copy.requiredMissing}</h4>
                    <span>{missingRequired.length}</span>
                  </div>
                  {missingRequired.length ? (
                    <div className="job-tailor__priority-list">
                      {missingRequired.slice(0, 6).map((item) => (
                        <article key={`${item.category}-${item.term}`}>
                          <div>
                            <span className="job-tailor__status job-tailor__status--review">!</span>
                            <div>
                              <strong>{item.term}</strong>
                              <small>{categoryLabel(item.category)}</small>
                            </div>
                          </div>
                          <button type="button" onClick={() => goToSection(item.category)}>{copy.reviewSection}</button>
                        </article>
                      ))}
                    </div>
                  ) : <p className="job-tailor__muted">{copy.noRequiredMissing}</p>}
                </section>

                <section className="job-tailor__section">
                  <div className="job-tailor__section-title">
                    <h4>{copy.breakdown}</h4>
                  </div>
                  <div className="job-tailor__breakdown">
                    {breakdowns.map((item) => (
                      <article key={item.category}>
                        <div className="job-tailor__breakdown-head">
                          <strong>{categoryLabel(item.category)}</strong>
                          <span>{item.coverage}%</span>
                        </div>
                        <div className="job-tailor__mini-bar" aria-hidden="true"><span style={{ width: `${item.coverage}%` }} /></div>
                        <small>{item.matched}/{item.total} {copy.matched.toLowerCase()}</small>
                        <button type="button" onClick={() => goToSection(item.category)}>{copy.reviewSection}</button>
                      </article>
                    ))}
                  </div>
                </section>

                <section className="job-tailor__section">
                  <div className="job-tailor__section-title">
                    <h4>{copy.requirementAnalysis}</h4>
                    <span>{requirements.length}</span>
                  </div>
                  <div className="job-tailor__requirements">
                    {requirements.map((item) => (
                      <article className={item.matched ? 'is-match' : 'is-review'} key={`${item.category}-${item.term}`}>
                        <span className={`job-tailor__status ${item.matched ? 'job-tailor__status--match' : 'job-tailor__status--review'}`}>
                          {item.matched ? '✓' : '!'}
                        </span>
                        <div>
                          <strong>{item.term}</strong>
                          <div className="job-tailor__tags">
                            <span>{categoryLabel(item.category)}</span>
                            <span className={`priority-${item.priority}`}>{priorityLabel(item.priority)}</span>
                            <span>{item.matched ? copy.alreadyThere : copy.missingLabel}</span>
                          </div>
                        </div>
                      </article>
                    ))}
                  </div>
                </section>

                <p className="job-tailor__safety">{copy.safety}</p>
                <p className="job-tailor__disclaimer">{copy.disclaimer}</p>
              </div>
            )}
          </div>
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
  font-size: 14px;
}
[dir="rtl"].job-tailor {
  left: auto;
  right: 16px;
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
  font-weight: 750;
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
.job-tailor__backdrop {
  position: fixed;
  inset: 0;
  z-index: 115;
  display: flex;
  justify-content: flex-end;
  padding: 14px;
  background: rgba(15, 23, 42, .32);
  backdrop-filter: blur(3px);
}
[dir="rtl"] .job-tailor__backdrop {
  justify-content: flex-start;
}
.job-tailor__panel {
  width: min(680px, calc(100vw - 28px));
  height: calc(100vh - 28px);
  overflow: auto;
  padding: 22px;
  border: 1px solid rgba(15, 23, 42, .10);
  border-radius: 22px;
  background: #fff;
  box-shadow: 0 28px 80px rgba(15, 23, 42, .28);
}
.job-tailor__heading {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 42px;
  gap: 16px;
  align-items: start;
  padding-bottom: 18px;
  border-bottom: 1px solid #e2e8f0;
}
.job-tailor__heading small {
  display: block;
  margin-bottom: 5px;
  color: #64748b;
  font-size: 11px;
  font-weight: 850;
  letter-spacing: .10em;
}
.job-tailor__heading h3 {
  margin: 0;
  font-size: clamp(24px, 4vw, 34px);
  line-height: 1.15;
}
.job-tailor__heading p {
  max-width: 560px;
  margin: 8px 0 0;
  color: #64748b;
  line-height: 1.55;
}
.job-tailor__close {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  background: #f8fafc;
  color: #0f172a;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
}
.job-tailor__inputs {
  display: grid;
  gap: 13px;
  margin-top: 18px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: #f8fafc;
}
.job-tailor__field {
  display: grid;
  gap: 6px;
  color: #334155;
  font-weight: 750;
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
  min-height: 44px;
  padding: 9px 11px;
}
.job-tailor__field textarea {
  padding: 11px;
  resize: vertical;
}
.job-tailor__input-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.job-tailor__input-meta small {
  color: #64748b;
  line-height: 1.4;
}
.job-tailor__clear {
  flex: 0 0 auto;
  border: 0;
  background: transparent;
  color: #475569;
  font: inherit;
  font-size: 12px;
  text-decoration: underline;
  cursor: pointer;
}
.job-tailor__empty {
  display: grid;
  place-items: center;
  min-height: 180px;
  margin-top: 18px;
  padding: 24px;
  border: 1px dashed #cbd5e1;
  border-radius: 16px;
  text-align: center;
  color: #64748b;
}
.job-tailor__empty strong {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #0f172a;
  font-size: 24px;
}
.job-tailor__empty p {
  max-width: 430px;
  margin: 12px 0 0;
}
.job-tailor__analysis {
  display: grid;
  gap: 16px;
  margin-top: 18px;
}
.job-tailor__score-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
.job-tailor__score {
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 15px;
  background: #fff;
}
.job-tailor__score small {
  display: block;
  color: #64748b;
}
.job-tailor__score strong {
  display: block;
  margin-top: 4px;
  font-size: 32px;
}
.job-tailor__bar,
.job-tailor__mini-bar {
  height: 7px;
  margin-top: 10px;
  overflow: hidden;
  border-radius: 999px;
  background: #e2e8f0;
}
.job-tailor__bar span,
.job-tailor__mini-bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: #0f172a;
  transition: width .2s ease;
}
.job-tailor__section {
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: #fff;
}
.job-tailor__section-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}
.job-tailor__section-title h4 {
  margin: 0;
  font-size: 16px;
}
.job-tailor__section-title > span {
  display: grid;
  place-items: center;
  min-width: 28px;
  height: 28px;
  padding: 0 7px;
  border-radius: 999px;
  background: #f1f5f9;
  font-size: 12px;
  font-weight: 800;
}
.job-tailor__priority-list {
  display: grid;
  gap: 9px;
}
.job-tailor__priority-list article {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #f8fafc;
}
.job-tailor__priority-list article > div {
  display: flex;
  align-items: center;
  gap: 9px;
  min-width: 0;
}
.job-tailor__priority-list strong,
.job-tailor__requirements strong {
  overflow-wrap: anywhere;
}
.job-tailor__priority-list small {
  display: block;
  margin-top: 2px;
  color: #64748b;
}
.job-tailor__priority-list button,
.job-tailor__breakdown button {
  flex: 0 0 auto;
  border: 0;
  background: transparent;
  color: #0f172a;
  font: inherit;
  font-size: 12px;
  font-weight: 800;
  text-decoration: underline;
  cursor: pointer;
}
.job-tailor__status {
  display: grid;
  place-items: center;
  flex: 0 0 28px;
  width: 28px;
  height: 28px;
  border-radius: 999px;
  font-weight: 900;
}
.job-tailor__status--match {
  background: #0f172a;
  color: #fff;
}
.job-tailor__status--review {
  background: #f1f5f9;
  color: #334155;
}
.job-tailor__breakdown {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.job-tailor__breakdown article {
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #f8fafc;
}
.job-tailor__breakdown-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.job-tailor__breakdown article > small {
  display: block;
  margin-top: 7px;
  color: #64748b;
}
.job-tailor__breakdown button {
  margin-top: 8px;
  padding: 0;
}
.job-tailor__requirements {
  display: grid;
  gap: 8px;
}
.job-tailor__requirements article {
  display: grid;
  grid-template-columns: 30px minmax(0, 1fr);
  gap: 10px;
  align-items: start;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
}
.job-tailor__requirements article.is-match {
  background: #f8fafc;
}
.job-tailor__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
}
.job-tailor__tags span {
  padding: 4px 7px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #475569;
  font-size: 11px;
}
.job-tailor__tags .priority-required {
  background: #e2e8f0;
  color: #0f172a;
  font-weight: 800;
}
.job-tailor__muted {
  margin: 0;
  color: #64748b;
  line-height: 1.5;
}
.job-tailor__safety {
  margin: 0;
  padding: 13px 14px;
  border-radius: 12px;
  background: #f8fafc;
  color: #334155;
  font-size: 12px;
  line-height: 1.55;
}
.job-tailor__disclaimer {
  margin: 0;
  color: #64748b;
  font-size: 11px;
  line-height: 1.5;
}
@media (max-width: 760px) {
  .job-tailor,
  [dir="rtl"].job-tailor {
    top: 126px;
    left: 8px;
    right: auto;
  }
  [dir="rtl"].job-tailor {
    left: auto;
    right: 8px;
  }
  .job-tailor__trigger {
    min-height: 40px;
    padding: 6px 10px;
  }
  .job-tailor__backdrop,
  [dir="rtl"] .job-tailor__backdrop {
    justify-content: stretch;
    padding: 0;
  }
  .job-tailor__panel {
    width: 100vw;
    height: 100vh;
    padding: 16px;
    border: 0;
    border-radius: 0;
  }
  .job-tailor__heading {
    grid-template-columns: minmax(0, 1fr) 40px;
  }
  .job-tailor__heading h3 {
    font-size: 26px;
  }
  .job-tailor__score-grid,
  .job-tailor__breakdown {
    grid-template-columns: 1fr;
  }
  .job-tailor__priority-list article {
    align-items: flex-start;
    flex-direction: column;
  }
  .job-tailor__priority-list button {
    margin-inline-start: 37px;
  }
}
'''
    css_path.write_text(css, encoding="utf-8")

print("Applied target job tailoring V2.")
