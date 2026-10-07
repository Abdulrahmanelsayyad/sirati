from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
component = root / "components" / "ExperienceDescriptionPicker.tsx"
component.parent.mkdir(parents=True, exist_ok=True)

component.write_text(r''' 'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import {
  getSpecialty,
  nursingLevels,
  nursingSpecialties,
  type LibraryLanguage,
  type NursingLevel
} from '@/lib/nursingLibrary';

type Category = 'all' | 'clinical' | 'safety' | 'documentation' | 'teamwork' | 'leadership';
type Side = 'left' | 'right';

type Suggestion = {
  id: string;
  text: string;
  category: Exclude<Category, 'all'>;
  recommended: boolean;
  source: 'specialty' | 'level';
};

const SPECIALTY_PATTERNS: Array<{ id: string; pattern: RegExp }> = [
  { id: 'supervisor', pattern: /supervisor|charge nurse|head nurse|team leader|nursing lead|مشرف|رئيس تمريض|مسؤول تمريض/i },
  { id: 'emergency', pattern: /emergency|\ber\b|ed nurse|trauma|طوارئ|استقبال/i },
  { id: 'icu', pattern: /\bicu\b|critical care|intensive care|عناية مركزة|رعاية حرجة/i },
  { id: 'or', pattern: /operating room|theatre|perioperative|surgical nurse|\bor\b|عمليات|جراحة/i },
  { id: 'infection-control', pattern: /infection control|infection prevention|\bipc\b|مكافحة العدوى|منع العدوى/i },
  { id: 'dialysis', pattern: /dialysis|hemodialysis|renal|غسيل كلوي|غسيل الكلى/i },
  { id: 'pediatric', pattern: /pediatric|paediatric|children|child|أطفال|اطفال/i },
  { id: 'medsurg', pattern: /medical.?surgical|med.?surg|ward nurse|inpatient|باطنة|جراحة عامة|أقسام|عنابر/i },
];

const LEVEL_PATTERNS: Array<{ id: NursingLevel; pattern: RegExp }> = [
  { id: 'supervisor', pattern: /supervisor|head nurse|nursing lead|manager|مشرف|رئيس تمريض|مدير تمريض/i },
  { id: 'senior', pattern: /senior|charge nurse|team leader|خبير|سينيور|مسؤول وردية/i },
  { id: 'beginner', pattern: /intern|trainee|new grad|graduate nurse|متدرب|امتياز|حديث التخرج/i },
];

const LEVEL_EXTRAS: Record<NursingLevel, Array<{ en: string; ar: string; category: Exclude<Category, 'all'> }>> = {
  beginner: [
    {
      en: 'Carry out assigned nursing care under applicable policies and escalate concerns to the responsible clinician.',
      ar: 'تنفيذ الرعاية التمريضية المكلّف بها وفق السياسات المعمول بها وتصعيد المخاوف للممارس المسؤول.',
      category: 'clinical'
    },
    {
      en: 'Maintain accurate documentation of assigned observations, care and patient responses.',
      ar: 'الحفاظ على توثيق دقيق للملاحظات والرعاية واستجابات المرضى ضمن نطاق العمل.',
      category: 'documentation'
    },
    {
      en: 'Follow patient-identification, medication-safety and infection-prevention requirements consistently.',
      ar: 'الالتزام المستمر بمتطلبات تعريف المريض وسلامة الدواء ومكافحة العدوى.',
      category: 'safety'
    }
  ],
  experienced: [
    {
      en: 'Prioritize assigned patient care according to acuity, changing clinical needs and time-sensitive tasks.',
      ar: 'ترتيب أولويات رعاية المرضى وفق حدة الحالة والتغيرات السريرية والمهام الحساسة للوقت.',
      category: 'clinical'
    },
    {
      en: 'Coordinate care with the multidisciplinary team and communicate clinically significant changes promptly.',
      ar: 'تنسيق الرعاية مع الفريق متعدد التخصصات وإبلاغ التغيرات السريرية المهمة بسرعة.',
      category: 'teamwork'
    },
    {
      en: 'Apply patient-safety checks and escalate risks or deterioration through the appropriate pathway.',
      ar: 'تطبيق فحوص سلامة المرضى وتصعيد المخاطر أو التدهور عبر المسار المناسب.',
      category: 'safety'
    }
  ],
  senior: [
    {
      en: 'Support junior staff with clinical guidance, prioritization and safe escalation during the shift.',
      ar: 'دعم أفراد التمريض الأقل خبرة بالتوجيه السريري وترتيب الأولويات والتصعيد الآمن أثناء الوردية.',
      category: 'leadership'
    },
    {
      en: 'Contribute to complex-care coordination and help resolve workflow barriers affecting patient safety.',
      ar: 'المساهمة في تنسيق الرعاية المعقدة والمساعدة في حل معوقات سير العمل المؤثرة على سلامة المرضى.',
      category: 'teamwork'
    },
    {
      en: 'Review key clinical documentation and reinforce complete handover of high-risk patient information.',
      ar: 'مراجعة عناصر التوثيق السريري المهمة وتعزيز التسليم الكامل لمعلومات المرضى عالية الخطورة.',
      category: 'documentation'
    }
  ],
  supervisor: [
    {
      en: 'Coordinate nursing assignments according to patient acuity, workload and available staffing.',
      ar: 'تنسيق توزيع التمريض وفق حدة الحالات وحجم العمل والكوادر المتاحة.',
      category: 'leadership'
    },
    {
      en: 'Monitor patient flow, redistribute nursing resources when priorities change and escalate unresolved risks.',
      ar: 'متابعة تدفق المرضى وإعادة توزيع الموارد التمريضية عند تغير الأولويات وتصعيد المخاطر غير المحلولة.',
      category: 'leadership'
    },
    {
      en: 'Review documentation, safety concerns and operational gaps and follow up required corrective actions.',
      ar: 'مراجعة التوثيق ومخاوف السلامة والفجوات التشغيلية ومتابعة الإجراءات التصحيحية المطلوبة.',
      category: 'documentation'
    },
    {
      en: 'Coach staff on workflow, policy adherence and safe clinical communication during the shift.',
      ar: 'توجيه العاملين بشأن سير العمل والالتزام بالسياسات والتواصل السريري الآمن أثناء الوردية.',
      category: 'leadership'
    }
  ]
};

function detectLanguage(): LibraryLanguage {
  const cv = document.querySelector<HTMLElement>('.cv-sheet');
  if (cv?.getAttribute('dir') === 'rtl') return 'ar';
  if (document.documentElement.getAttribute('dir') === 'rtl') return 'ar';
  return 'en';
}

function normalize(value: string) {
  return value
    .toLowerCase()
    .replace(/[\u064B-\u065F\u0670]/g, '')
    .replace(/[إأآ]/g, 'ا')
    .replace(/ى/g, 'ي')
    .replace(/ة/g, 'ه')
    .replace(/^[-•]\s*/, '')
    .replace(/[^a-z0-9\u0600-\u06ff%+ ]/gi, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function words(value: string) {
  return new Set(normalize(value).split(' ').filter((item) => item.length > 2));
}

function similarity(a: string, b: string) {
  const left = words(a);
  const right = words(b);
  if (!left.size || !right.size) return 0;
  let common = 0;
  left.forEach((word) => {
    if (right.has(word)) common += 1;
  });
  return common / Math.max(left.size, right.size);
}

function isExperienceDescription(target: EventTarget | null): target is HTMLTextAreaElement {
  if (!(target instanceof HTMLTextAreaElement)) return false;
  if (target.closest('.job-tailor, .smart-nursing-library, .cv-readiness, .duplicate-cv, .experience-picker')) {
    return false;
  }

  const own = [
    target.name,
    target.id,
    target.placeholder,
    target.getAttribute('aria-label') || '',
  ].join(' ');

  const field = target.closest<HTMLElement>('.field, label, .wizard-section-card, fieldset');
  const fieldText = field ? (field.innerText || field.textContent || '') : '';
  const section = target.closest<HTMLElement>('.wizard-section-card, fieldset, section');
  const sectionText = section ? (section.innerText || section.textContent || '') : '';

  const text = (own + ' ' + fieldText).replace(/\s+/g, ' ').toLowerCase();
  const context = sectionText.replace(/\s+/g, ' ').toLowerCase();

  const descriptionLike = /description|details|responsibilit|duties|الوصف|التفاصيل|المسؤوليات|المهام/.test(text);
  if (!descriptionLike) return false;

  const hasExperienceContext = /work experience|experience|employment|الخبره|الخبرة|العمل السابق|الخبرات/.test(context);
  return hasExperienceContext || !context || context === fieldText.toLowerCase();
}

function fieldLabel(control: HTMLInputElement) {
  const field = control.closest<HTMLElement>('.field, label, .wizard-section-card, fieldset');
  return (field?.innerText || field?.textContent || control.placeholder || control.name || '').replace(/\s+/g, ' ').trim();
}

function nearbyRole(target: HTMLTextAreaElement) {
  const targetTop = target.getBoundingClientRect().top;
  let best = '';
  let bestDistance = Number.POSITIVE_INFINITY;

  for (const input of Array.from(document.querySelectorAll<HTMLInputElement>('input[type="text"], input:not([type])'))) {
    if (!input.value.trim()) continue;
    if (input.closest('.job-tailor, .smart-nursing-library, .cv-readiness, .duplicate-cv, .experience-picker')) continue;

    const label = fieldLabel(input);
    if (!/job title|role|position|designation|المسمى|الوظيفه|الوظيفة|الدور|المسمى الوظيفي/i.test(label)) continue;

    const distance = Math.abs(input.getBoundingClientRect().top - targetTop);
    if (distance < bestDistance && distance < 900) {
      bestDistance = distance;
      best = input.value.trim();
    }
  }

  return best;
}

function inferSpecialty(role: string) {
  const match = SPECIALTY_PATTERNS.find((item) => item.pattern.test(role));
  return match?.id || '';
}

function inferLevel(role: string): NursingLevel {
  return LEVEL_PATTERNS.find((item) => item.pattern.test(role))?.id || 'experienced';
}

function classify(text: string): Exclude<Category, 'all'> {
  const value = normalize(text);
  if (/lead|supervis|assign|staff|coach|mentor|قياد|اشراف|اشراف|توزيع|توجيه/.test(value)) return 'leadership';
  if (/document|record|handover|communicat|توثيق|تسليم|استلام|ابلاغ/.test(value)) return 'documentation';
  if (/safe|infection|prevent|risk|aseptic|identif|سلام|عدوي|وقاي|خطر/.test(value)) return 'safety';
  if (/coordinat|team|physician|multidisciplin|collaborat|تنسيق|فريق|اطباء/.test(value)) return 'teamwork';
  return 'clinical';
}

function setTextareaValue(target: HTMLTextAreaElement, value: string) {
  const descriptor = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value');
  descriptor?.set?.call(target, value);
  target.dispatchEvent(new Event('input', { bubbles: true }));
  target.dispatchEvent(new Event('change', { bubbles: true }));
}

function currentLines(target: HTMLTextAreaElement | null) {
  if (!target) return [];
  return target.value
    .split(/\n|•/)
    .map((line) => line.trim())
    .filter(Boolean);
}

function isAlreadyPresent(text: string, lines: string[]) {
  const exact = normalize(text);
  return lines.some((line) => normalize(line) === exact || similarity(line, text) >= 0.84);
}

function categoryLabel(category: Category, language: LibraryLanguage) {
  const labels: Record<Category, { en: string; ar: string }> = {
    all: { en: 'All', ar: 'الكل' },
    clinical: { en: 'Clinical care', ar: 'الرعاية السريرية' },
    safety: { en: 'Safety', ar: 'السلامة' },
    documentation: { en: 'Documentation', ar: 'التوثيق' },
    teamwork: { en: 'Teamwork', ar: 'العمل الجماعي' },
    leadership: { en: 'Leadership', ar: 'القيادة' },
  };
  return labels[category][language];
}

export default function ExperienceDescriptionPicker() {
  const [enabled, setEnabled] = useState(false);
  const [open, setOpen] = useState(false);
  const [language, setLanguage] = useState<LibraryLanguage>('en');
  const [specialtyId, setSpecialtyId] = useState('emergency');
  const [level, setLevel] = useState<NursingLevel>('experienced');
  const [category, setCategory] = useState<Category>('all');
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState<string[]>([]);
  const [detectedRole, setDetectedRole] = useState('');
  const [autoDetected, setAutoDetected] = useState(false);
  const [autoOpen, setAutoOpen] = useState(true);
  const [side, setSide] = useState<Side>('left');
  const [version, setVersion] = useState(0);
  const targetRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const onBuilder = window.location.pathname.includes('/builder');
    setEnabled(onBuilder);
    if (!onBuilder) return;

    const savedSpecialty = sessionStorage.getItem('sirati.experiencePicker.specialty');
    const savedLevel = sessionStorage.getItem('sirati.experiencePicker.level') as NursingLevel | null;
    const savedAutoOpen = sessionStorage.getItem('sirati.experiencePicker.autoOpen');

    if (savedSpecialty && nursingSpecialties.some((item) => item.id === savedSpecialty)) setSpecialtyId(savedSpecialty);
    if (savedLevel && nursingLevels.some((item) => item.id === savedLevel)) setLevel(savedLevel);
    if (savedAutoOpen === '0') setAutoOpen(false);

    const scanLanguage = () => setLanguage(detectLanguage());
    scanLanguage();

    const activate = (target: HTMLTextAreaElement) => {
      targetRef.current = target;
      const role = nearbyRole(target);
      setDetectedRole(role);

      const specialtyGuess = inferSpecialty(role);
      if (specialtyGuess) {
        setSpecialtyId(specialtyGuess);
        setAutoDetected(true);
      } else {
        setAutoDetected(false);
      }

      const levelGuess = inferLevel(role);
      setLevel(levelGuess);

      const rect = target.getBoundingClientRect();
      setSide(rect.left + rect.width / 2 < window.innerWidth / 2 ? 'right' : 'left');
      setSelected([]);
      setCategory('all');
      setQuery('');
      setVersion((value) => value + 1);
      setLanguage(detectLanguage());
      if (autoOpen) setOpen(true);
    };

    const onFocus = (event: FocusEvent) => {
      const element = event.target instanceof HTMLElement ? event.target : null;
      if (element?.closest('.experience-picker')) return;
      if (!isExperienceDescription(event.target)) {
        setOpen(false);
        return;
      }
      activate(event.target);
    };

    const onInput = (event: Event) => {
      if (event.target === targetRef.current) setVersion((value) => value + 1);
    };

    document.addEventListener('focusin', onFocus, true);
    document.addEventListener('input', onInput, true);
    const timer = window.setInterval(scanLanguage, 1200);

    return () => {
      document.removeEventListener('focusin', onFocus, true);
      document.removeEventListener('input', onInput, true);
      window.clearInterval(timer);
    };
  }, [autoOpen]);

  const specialty = useMemo(() => getSpecialty(specialtyId), [specialtyId]);
  const lines = useMemo(() => currentLines(targetRef.current), [version, targetRef.current?.value]);

  const suggestions = useMemo<Suggestion[]>(() => {
    const specialtyItems: Suggestion[] = specialty.bullets.map((item, index) => ({
      id: 'specialty-' + specialty.id + '-' + index,
      text: item[language],
      category: classify(item[language]),
      recommended: index < 4,
      source: 'specialty',
    }));

    const levelItems: Suggestion[] = LEVEL_EXTRAS[level].map((item, index) => ({
      id: 'level-' + level + '-' + index,
      text: item[language],
      category: item.category,
      recommended: level !== 'beginner' || index < 2,
      source: 'level',
    }));

    const unique = new Map<string, Suggestion>();
    [...specialtyItems, ...levelItems].forEach((item) => {
      const key = normalize(item.text);
      if (!unique.has(key)) unique.set(key, item);
    });

    return Array.from(unique.values());
  }, [specialty, level, language]);

  const filtered = useMemo(() => {
    const needle = normalize(query);
    return suggestions.filter((item) => {
      if (category !== 'all' && item.category !== category) return false;
      if (needle && !normalize(item.text).includes(needle)) return false;
      return true;
    });
  }, [suggestions, category, query]);

  if (!enabled || !targetRef.current) return null;

  const copy = language === 'ar'
    ? {
        trigger: 'اقتراحات Description',
        title: 'Experience Description Pro',
        subtitle: 'اختيارات ذكية حسب المسمى الوظيفي ومستوى الخبرة، مع بقاء الكتابة اليدوية متاحة بالكامل.',
        specialty: 'التخصص',
        level: 'المستوى',
        detected: 'تم التعرف من المسمى',
        role: 'المسمى الحالي',
        search: 'ابحث داخل الاقتراحات...',
        recommended: 'اختيار المقترح',
        clear: 'مسح الاختيار',
        addSelected: 'إضافة المختار',
        selected: 'محدد',
        add: 'إضافة',
        added: 'موجود بالفعل',
        similar: 'مشابه لمحتوى موجود',
        empty: 'لا توجد اقتراحات مطابقة للبحث الحالي.',
        close: 'إغلاق',
        manual: 'يمكنك الكتابة أو تعديل أي جملة يدويًا داخل Description في أي وقت.',
        safety: 'أضف فقط ما يصف خبرتك الحقيقية. Sirati لا يضيف مهام أو إنجازات أو أرقامًا تلقائيًا.',
        autoOpen: 'فتح الاقتراحات تلقائيًا عند دخول Description',
        sourceSpecialty: 'التخصص',
        sourceLevel: 'مستوى الخبرة',
      }
    : {
        trigger: 'Description suggestions',
        title: 'Experience Description Pro',
        subtitle: 'Smart options based on job title and experience level, while manual writing stays fully available.',
        specialty: 'Specialty',
        level: 'Experience level',
        detected: 'Auto-detected from role',
        role: 'Current role',
        search: 'Search suggestions...',
        recommended: 'Select recommended',
        clear: 'Clear selection',
        addSelected: 'Add selected',
        selected: 'selected',
        add: 'Add',
        added: 'Already added',
        similar: 'Similar content exists',
        empty: 'No suggestions match the current filters.',
        close: 'Close',
        manual: 'You can type or edit any sentence manually in the Description field at any time.',
        safety: 'Only add statements that are factually true for you. Sirati never invents duties, achievements or metrics.',
        autoOpen: 'Open suggestions automatically when Description is focused',
        sourceSpecialty: 'Specialty',
        sourceLevel: 'Experience level',
      };

  const toggleSelected = (id: string) => {
    setSelected((current) => current.includes(id) ? current.filter((item) => item !== id) : [...current, id]);
  };

  const selectRecommended = () => {
    const ids = filtered
      .filter((item) => item.recommended && !isAlreadyPresent(item.text, lines))
      .slice(0, 5)
      .map((item) => item.id);
    setSelected(ids);
  };

  const insertSuggestions = (items: Suggestion[]) => {
    const target = targetRef.current;
    if (!target) return;

    const current = currentLines(target);
    const additions = items
      .map((item) => item.text)
      .filter((text) => !isAlreadyPresent(text, current));

    if (!additions.length) {
      target.focus();
      return;
    }

    setTextareaValue(target, [...current, ...additions].join('\n'));
    setSelected([]);
    setVersion((value) => value + 1);
    target.focus();
  };

  const setSpecialtyManually = (value: string) => {
    setSpecialtyId(value);
    setAutoDetected(false);
    setSelected([]);
    sessionStorage.setItem('sirati.experiencePicker.specialty', value);
  };

  const setLevelManually = (value: NursingLevel) => {
    setLevel(value);
    setSelected([]);
    sessionStorage.setItem('sirati.experiencePicker.level', value);
  };

  if (!open) {
    return (
      <button
        type="button"
        className={'experience-picker-trigger experience-picker-trigger--' + side}
        onClick={() => setOpen(true)}
      >
        ✨ {copy.trigger}
      </button>
    );
  }

  const selectedItems = suggestions.filter((item) => selected.includes(item.id));

  return (
    <aside className={'experience-picker experience-picker--' + side} dir={language === 'ar' ? 'rtl' : 'ltr'} aria-label={copy.title}>
      <div className="experience-picker__heading">
        <div>
          <small>SIRATI EXPERIENCE PRO</small>
          <strong>{copy.title}</strong>
          <p>{copy.subtitle}</p>
        </div>
        <button type="button" onClick={() => setOpen(false)} aria-label={copy.close}>×</button>
      </div>

      {detectedRole && (
        <div className="experience-picker__detected">
          <span>{copy.role}</span>
          <strong>{detectedRole}</strong>
          {autoDetected && <em>✓ {copy.detected}</em>}
        </div>
      )}

      <div className="experience-picker__selectors">
        <label>
          <span>{copy.specialty}</span>
          <select value={specialtyId} onChange={(event) => setSpecialtyManually(event.target.value)}>
            {nursingSpecialties.map((item) => (
              <option key={item.id} value={item.id}>{item.label[language]}</option>
            ))}
          </select>
        </label>

        <label>
          <span>{copy.level}</span>
          <select value={level} onChange={(event) => setLevelManually(event.target.value as NursingLevel)}>
            {nursingLevels.map((item) => (
              <option key={item.id} value={item.id}>{item.label[language]}</option>
            ))}
          </select>
        </label>
      </div>

      <label className="experience-picker__search">
        <span aria-hidden="true">⌕</span>
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder={copy.search}
          type="search"
        />
      </label>

      <div className="experience-picker__categories" role="tablist" aria-label="Suggestion categories">
        {(['all', 'clinical', 'safety', 'documentation', 'teamwork', 'leadership'] as Category[]).map((item) => (
          <button
            type="button"
            key={item}
            className={category === item ? 'is-active' : ''}
            onClick={() => setCategory(item)}
          >
            {categoryLabel(item, language)}
          </button>
        ))}
      </div>

      <div className="experience-picker__quick">
        <button type="button" onClick={selectRecommended}>{copy.recommended}</button>
        <button type="button" onClick={() => setSelected([])} disabled={!selected.length}>{copy.clear}</button>
        <span>{selected.length} {copy.selected}</span>
      </div>

      <div className="experience-picker__options">
        {filtered.map((item) => {
          const exact = lines.some((line) => normalize(line) === normalize(item.text));
          const similar = !exact && lines.some((line) => similarity(line, item.text) >= 0.84);
          const unavailable = exact || similar;
          return (
            <article key={item.id} className={unavailable ? 'is-added' : selected.includes(item.id) ? 'is-selected' : ''}>
              <label>
                <input
                  type="checkbox"
                  checked={selected.includes(item.id)}
                  onChange={() => toggleSelected(item.id)}
                  disabled={unavailable}
                />
                <span>{item.text}</span>
              </label>
              <div className="experience-picker__meta">
                <span>{item.source === 'specialty' ? copy.sourceSpecialty : copy.sourceLevel}</span>
                <span>{categoryLabel(item.category, language)}</span>
                <button type="button" onClick={() => insertSuggestions([item])} disabled={unavailable}>
                  {exact ? copy.added : similar ? copy.similar : '+ ' + copy.add}
                </button>
              </div>
            </article>
          );
        })}
        {!filtered.length && <p className="experience-picker__empty">{copy.empty}</p>}
      </div>

      <div className="experience-picker__sticky-actions">
        <div>
          <strong>{selected.length}</strong>
          <span>{copy.selected}</span>
        </div>
        <button
          type="button"
          onClick={() => insertSuggestions(selectedItems)}
          disabled={!selectedItems.length}
        >
          {copy.addSelected}
        </button>
      </div>

      <label className="experience-picker__auto-open">
        <input
          type="checkbox"
          checked={autoOpen}
          onChange={(event) => {
            setAutoOpen(event.target.checked);
            sessionStorage.setItem('sirati.experiencePicker.autoOpen', event.target.checked ? '1' : '0');
          }}
        />
        <span>{copy.autoOpen}</span>
      </label>

      <p className="experience-picker__manual">{copy.manual}</p>
      <p className="experience-picker__safety">{copy.safety}</p>
    </aside>
  );
}
'''.lstrip(), encoding="utf-8")

layout = root / "app" / "layout.tsx"
text = layout.read_text(encoding="utf-8")
imp = "import ExperienceDescriptionPicker from '@/components/ExperienceDescriptionPicker';\n"
if imp not in text:
    lines = text.splitlines(True)
    i = 0
    while i < len(lines) and (lines[i].startswith("import ") or not lines[i].strip()):
        i += 1
    lines.insert(i, imp)
    text = "".join(lines)

if "<ExperienceDescriptionPicker />" not in text:
    if "</body>" not in text:
        raise SystemExit("Could not find </body> in app/layout.tsx")
    text = text.replace("</body>", "        <ExperienceDescriptionPicker />\n      </body>", 1)

layout.write_text(text, encoding="utf-8")

css_path = root / "app" / "globals.css"
css = css_path.read_text(encoding="utf-8")
marker = "/* Sirati experience description picker */"
if marker in css:
    css = css[:css.index(marker)].rstrip() + "\n"

css += r'''

/* Sirati experience description picker */
.experience-picker,
.experience-picker * {
  box-sizing: border-box;
}
.experience-picker {
  position: fixed;
  bottom: 92px;
  z-index: 105;
  width: min(520px, calc(100vw - 32px));
  max-height: min(760px, calc(100vh - 126px));
  overflow: auto;
  padding: 16px;
  border: 1px solid rgba(15, 23, 42, .12);
  border-radius: 20px;
  background: rgba(255, 255, 255, .99);
  box-shadow: 0 24px 72px rgba(15, 23, 42, .22);
  backdrop-filter: blur(14px);
  font-size: 14px;
}
.experience-picker--left { left: 16px; }
.experience-picker--right { right: 16px; }
[dir="rtl"].experience-picker--left { left: auto; right: 16px; }
[dir="rtl"].experience-picker--right { right: auto; left: 16px; }

.experience-picker-trigger {
  position: fixed;
  bottom: 98px;
  z-index: 104;
  min-height: 40px;
  padding: 8px 12px;
  border: 1px solid rgba(37, 99, 235, .22);
  border-radius: 999px;
  background: #eff6ff;
  box-shadow: 0 12px 30px rgba(15, 23, 42, .12);
  color: #1d4ed8;
  font: inherit;
  font-size: 12px;
  font-weight: 800;
  cursor: pointer;
}
.experience-picker-trigger--left { left: 16px; }
.experience-picker-trigger--right { right: 16px; }

.experience-picker__heading {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 38px;
  gap: 12px;
  align-items: start;
}
.experience-picker__heading small {
  display: block;
  margin-bottom: 4px;
  color: #2563eb;
  font-size: 10px;
  font-weight: 900;
  letter-spacing: .1em;
}
.experience-picker__heading strong {
  display: block;
  color: #0f172a;
  font-size: 20px;
}
.experience-picker__heading p {
  margin: 6px 0 0;
  color: #64748b;
  font-size: 12px;
  line-height: 1.5;
}
.experience-picker__heading button {
  width: 38px;
  height: 38px;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  background: #f8fafc;
  color: #0f172a;
  font-size: 21px;
  cursor: pointer;
}

.experience-picker__detected {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 7px;
  align-items: center;
  margin-top: 13px;
  padding: 9px 10px;
  border: 1px solid #dbeafe;
  border-radius: 11px;
  background: #eff6ff;
}
.experience-picker__detected span {
  color: #64748b;
  font-size: 10px;
  font-weight: 800;
}
.experience-picker__detected strong {
  min-width: 0;
  overflow: hidden;
  color: #1e3a8a;
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.experience-picker__detected em {
  padding: 4px 7px;
  border-radius: 999px;
  background: #dbeafe;
  color: #1d4ed8;
  font-size: 9px;
  font-style: normal;
  font-weight: 850;
  white-space: nowrap;
}

.experience-picker__selectors {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 9px;
  margin-top: 12px;
}
.experience-picker__selectors label {
  display: grid;
  gap: 5px;
}
.experience-picker__selectors span {
  color: #475569;
  font-size: 10px;
  font-weight: 800;
}
.experience-picker__selectors select {
  width: 100%;
  min-height: 42px;
  padding: 0 9px;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  background: #fff;
  color: #0f172a;
  font: inherit;
  font-size: 12px;
}

.experience-picker__search {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr);
  align-items: center;
  margin-top: 10px;
  border: 1px solid #cbd5e1;
  border-radius: 11px;
  background: #fff;
}
.experience-picker__search > span {
  text-align: center;
  color: #64748b;
}
.experience-picker__search input {
  min-width: 0;
  min-height: 42px;
  border: 0;
  outline: 0;
  background: transparent;
  color: #0f172a;
  font: inherit;
  font-size: 12px;
}

.experience-picker__categories {
  display: flex;
  gap: 6px;
  margin-top: 10px;
  padding-bottom: 2px;
  overflow-x: auto;
  scrollbar-width: thin;
}
.experience-picker__categories button {
  flex: 0 0 auto;
  min-height: 32px;
  padding: 0 9px;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  background: #fff;
  color: #475569;
  font: inherit;
  font-size: 10px;
  font-weight: 750;
  cursor: pointer;
}
.experience-picker__categories button.is-active {
  border-color: #0f172a;
  background: #0f172a;
  color: #fff;
}

.experience-picker__quick {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
}
.experience-picker__quick button {
  min-height: 32px;
  padding: 0 9px;
  border: 1px solid #cbd5e1;
  border-radius: 9px;
  background: #fff;
  color: #334155;
  font: inherit;
  font-size: 10px;
  font-weight: 800;
  cursor: pointer;
}
.experience-picker__quick button:disabled {
  opacity: .45;
  cursor: default;
}
.experience-picker__quick span {
  margin-inline-start: auto;
  color: #64748b;
  font-size: 10px;
  font-weight: 750;
}

.experience-picker__options {
  display: grid;
  gap: 8px;
  margin-top: 10px;
}
.experience-picker__options article {
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  background: #fff;
}
.experience-picker__options article.is-selected {
  border-color: #93c5fd;
  background: #eff6ff;
}
.experience-picker__options article.is-added {
  background: #f8fafc;
}
.experience-picker__options article > label {
  display: grid;
  grid-template-columns: 20px minmax(0, 1fr);
  gap: 8px;
  align-items: start;
}
.experience-picker__options article input {
  margin-top: 2px;
  accent-color: #2563eb;
}
.experience-picker__options article label span {
  color: #334155;
  font-size: 11.7px;
  line-height: 1.45;
}
.experience-picker__meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding-inline-start: 28px;
}
.experience-picker__meta > span {
  padding: 4px 6px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #64748b;
  font-size: 9px;
  font-weight: 750;
}
.experience-picker__meta button {
  margin-inline-start: auto;
  min-height: 30px;
  padding: 0 9px;
  border: 1px solid #0f172a;
  border-radius: 8px;
  background: #0f172a;
  color: #fff;
  font: inherit;
  font-size: 9px;
  font-weight: 850;
  cursor: pointer;
}
.experience-picker__meta button:disabled {
  border-color: #cbd5e1;
  background: #e2e8f0;
  color: #64748b;
  cursor: default;
}
.experience-picker__empty {
  margin: 0;
  padding: 15px;
  border: 1px dashed #cbd5e1;
  border-radius: 11px;
  color: #64748b;
  text-align: center;
  font-size: 11px;
}

.experience-picker__sticky-actions {
  position: sticky;
  bottom: -16px;
  display: grid;
  grid-template-columns: auto minmax(150px, .65fr);
  gap: 10px;
  align-items: center;
  margin: 12px -16px 0;
  padding: 10px 16px 12px;
  border-top: 1px solid #e2e8f0;
  background: rgba(255, 255, 255, .98);
}
.experience-picker__sticky-actions > div {
  display: flex;
  align-items: baseline;
  gap: 5px;
}
.experience-picker__sticky-actions strong {
  font-size: 18px;
}
.experience-picker__sticky-actions span {
  color: #64748b;
  font-size: 10px;
}
.experience-picker__sticky-actions button {
  min-height: 40px;
  border: 1px solid #0f172a;
  border-radius: 10px;
  background: #0f172a;
  color: #fff;
  font: inherit;
  font-size: 11px;
  font-weight: 850;
  cursor: pointer;
}
.experience-picker__sticky-actions button:disabled {
  opacity: .45;
  cursor: default;
}

.experience-picker__auto-open {
  display: flex;
  gap: 7px;
  align-items: flex-start;
  margin-top: 10px;
  color: #475569;
  font-size: 10px;
  line-height: 1.4;
}
.experience-picker__auto-open input {
  margin-top: 1px;
  accent-color: #2563eb;
}
.experience-picker__manual,
.experience-picker__safety {
  margin: 9px 0 0;
  color: #64748b;
  font-size: 10px;
  line-height: 1.5;
}
.experience-picker__safety {
  padding-top: 8px;
  border-top: 1px solid #e2e8f0;
}

@media (max-width: 760px) {
  .experience-picker,
  .experience-picker--left,
  .experience-picker--right,
  [dir="rtl"].experience-picker--left,
  [dir="rtl"].experience-picker--right {
    left: 8px;
    right: 8px;
    bottom: 84px;
    width: auto;
    max-height: min(640px, calc(100vh - 112px));
    border-radius: 16px;
  }
  .experience-picker-trigger,
  .experience-picker-trigger--left,
  .experience-picker-trigger--right {
    left: 8px;
    right: auto;
    bottom: 88px;
  }
  .experience-picker__selectors {
    grid-template-columns: 1fr;
  }
  .experience-picker__detected {
    grid-template-columns: 1fr;
  }
  .experience-picker__detected strong {
    white-space: normal;
  }
  .experience-picker__meta {
    align-items: flex-start;
    flex-wrap: wrap;
  }
  .experience-picker__meta button {
    width: 100%;
    margin-inline-start: 0;
  }
  .experience-picker__sticky-actions {
    grid-template-columns: 1fr 1.4fr;
  }
}
'''
css_path.write_text(css, encoding="utf-8")

print("Applied Experience Description Pro V2.")
