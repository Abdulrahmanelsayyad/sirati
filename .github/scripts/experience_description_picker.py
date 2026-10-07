from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
component = root / "components" / "ExperienceDescriptionPicker.tsx"
component.parent.mkdir(parents=True, exist_ok=True)

component.write_text(r''' 'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { getSpecialty, nursingSpecialties, type LibraryLanguage } from '@/lib/nursingLibrary';

function detectLanguage(): LibraryLanguage {
  const cv = document.querySelector<HTMLElement>('.cv-sheet');
  if (cv?.getAttribute('dir') === 'rtl') return 'ar';
  if (document.documentElement.getAttribute('dir') === 'rtl') return 'ar';
  return 'en';
}

function normalize(value: string) {
  return value
    .toLowerCase()
    .replace(/^[-•]\s*/, '')
    .replace(/\s+/g, ' ')
    .trim();
}

function isExperienceDescription(target: EventTarget | null): target is HTMLTextAreaElement {
  if (!(target instanceof HTMLTextAreaElement)) return false;

  // Never treat textareas from other Sirati tools as work-experience descriptions.
  // "Job description" in Job Match Center was the important false positive here.
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

  // When broader section context is available, prefer explicit work-experience context.
  // Fall back to the description label itself for the current Builder markup.
  const hasExperienceContext = /work experience|experience|employment|الخبره|الخبرة|العمل السابق|الخبرات/.test(context);
  return hasExperienceContext || !context || context === fieldText.toLowerCase();
}

function setTextareaValue(target: HTMLTextAreaElement, value: string) {
  const descriptor = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value');
  descriptor?.set?.call(target, value);
  target.dispatchEvent(new Event('input', { bubbles: true }));
  target.dispatchEvent(new Event('change', { bubbles: true }));
}

export default function ExperienceDescriptionPicker() {
  const [enabled, setEnabled] = useState(false);
  const [open, setOpen] = useState(false);
  const [language, setLanguage] = useState<LibraryLanguage>('en');
  const [specialtyId, setSpecialtyId] = useState('emergency');
  const [version, setVersion] = useState(0);
  const targetRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const onBuilder = window.location.pathname.includes('/builder');
    setEnabled(onBuilder);
    if (!onBuilder) return;

    const saved = sessionStorage.getItem('sirati.experiencePicker.specialty');
    if (saved && nursingSpecialties.some((item) => item.id === saved)) {
      setSpecialtyId(saved);
    }

    const scanLanguage = () => setLanguage(detectLanguage());
    scanLanguage();

    const onFocus = (event: FocusEvent) => {
      const element = event.target instanceof HTMLElement ? event.target : null;
      if (element?.closest('.experience-picker')) return;

      if (!isExperienceDescription(event.target)) {
        setOpen(false);
        return;
      }

      targetRef.current = event.target;
      setVersion((value) => value + 1);
      setOpen(true);
      setLanguage(detectLanguage());
    };

    const onInput = (event: Event) => {
      if (event.target === targetRef.current) {
        setVersion((value) => value + 1);
      }
    };

    document.addEventListener('focusin', onFocus, true);
    document.addEventListener('input', onInput, true);
    const timer = window.setInterval(scanLanguage, 1200);

    return () => {
      document.removeEventListener('focusin', onFocus, true);
      document.removeEventListener('input', onInput, true);
      window.clearInterval(timer);
    };
  }, []);

  const specialty = useMemo(() => getSpecialty(specialtyId), [specialtyId]);
  const targetValue = targetRef.current?.value || '';
  const existing = useMemo(() => {
    return new Set(
      targetValue
        .split(/\n|•/)
        .map((line) => normalize(line))
        .filter(Boolean)
    );
  }, [targetValue, version]);

  if (!enabled || !open || !targetRef.current) return null;

  const copy = language === 'ar'
    ? {
        title: 'اختيارات وصف الخبرة',
        subtitle: 'اختر فقط الجمل التي تصف عملك فعلًا، أو اكتب وصفك يدويًا في الخانة كالمعتاد.',
        specialty: 'التخصص',
        add: 'إضافة',
        added: 'مضاف',
        close: 'إغلاق',
        manual: 'يمكنك التعديل أو الكتابة يدويًا في خانة Description في أي وقت.',
        safety: 'Sirati لا يضيف أي مسؤولية تلقائيًا. أنت تختار كل جملة بنفسك.',
      }
    : {
        title: 'Experience description options',
        subtitle: 'Choose only statements that genuinely describe your work, or keep typing manually in the field.',
        specialty: 'Specialty',
        add: 'Add',
        added: 'Added',
        close: 'Close',
        manual: 'You can edit or type manually in the Description field at any time.',
        safety: 'Sirati never adds responsibilities automatically. You choose every statement yourself.',
      };

  const addBullet = (value: string) => {
    const target = targetRef.current;
    if (!target) return;

    const key = normalize(value);
    const currentLines = target.value
      .split(/\n|•/)
      .map((line) => line.trim())
      .filter(Boolean);

    if (currentLines.some((line) => normalize(line) === key)) {
      target.focus();
      return;
    }

    const next = [...currentLines, value].join('\n');
    setTextareaValue(target, next);
    target.focus();
    setVersion((value) => value + 1);
  };

  return (
    <aside className="experience-picker" dir={language === 'ar' ? 'rtl' : 'ltr'} aria-label={copy.title}>
      <div className="experience-picker__heading">
        <div>
          <small>SIRATI EXPERIENCE HELPER</small>
          <strong>{copy.title}</strong>
          <p>{copy.subtitle}</p>
        </div>
        <button type="button" onClick={() => setOpen(false)} aria-label={copy.close}>×</button>
      </div>

      <label className="experience-picker__specialty">
        <span>{copy.specialty}</span>
        <select
          value={specialtyId}
          onChange={(event) => {
            setSpecialtyId(event.target.value);
            sessionStorage.setItem('sirati.experiencePicker.specialty', event.target.value);
          }}
        >
          {nursingSpecialties.map((item) => (
            <option key={item.id} value={item.id}>{item.label[language]}</option>
          ))}
        </select>
      </label>

      <div className="experience-picker__options">
        {specialty.bullets.map((item, index) => {
          const value = item[language];
          const alreadyAdded = existing.has(normalize(value));
          return (
            <article key={value + '-' + index} className={alreadyAdded ? 'is-added' : ''}>
              <p>{value}</p>
              <button type="button" onClick={() => addBullet(value)} disabled={alreadyAdded}>
                {alreadyAdded ? copy.added : '+ ' + copy.add}
              </button>
            </article>
          );
        })}
      </div>

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
if "/* Sirati experience description picker */" not in css:
    css += r'''

/* Sirati experience description picker */
.experience-picker {
  position: fixed;
  left: 16px;
  bottom: 96px;
  z-index: 105;
  width: min(430px, calc(100vw - 32px));
  max-height: min(640px, calc(100vh - 150px));
  overflow: auto;
  padding: 16px;
  border: 1px solid rgba(15, 23, 42, .12);
  border-radius: 18px;
  background: rgba(255, 255, 255, .99);
  box-shadow: 0 22px 64px rgba(15, 23, 42, .20);
  backdrop-filter: blur(12px);
  font-size: 14px;
}
[dir="rtl"].experience-picker {
  left: auto;
  right: 16px;
}
.experience-picker__heading {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 36px;
  gap: 12px;
  align-items: start;
}
.experience-picker__heading small {
  display: block;
  margin-bottom: 4px;
  color: #2563eb;
  font-size: 10px;
  font-weight: 850;
  letter-spacing: .08em;
}
.experience-picker__heading strong {
  display: block;
  color: #0f172a;
  font-size: 18px;
}
.experience-picker__heading p {
  margin: 6px 0 0;
  color: #64748b;
  font-size: 12px;
  line-height: 1.5;
}
.experience-picker__heading button {
  width: 36px;
  height: 36px;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  background: #f8fafc;
  color: #0f172a;
  font-size: 20px;
  cursor: pointer;
}
.experience-picker__specialty {
  display: grid;
  gap: 5px;
  margin-top: 13px;
}
.experience-picker__specialty > span {
  color: #475569;
  font-size: 11px;
  font-weight: 800;
}
.experience-picker__specialty select {
  width: 100%;
  min-height: 42px;
  padding: 0 10px;
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  background: #fff;
  color: #0f172a;
  font: inherit;
}
.experience-picker__options {
  display: grid;
  gap: 8px;
  margin-top: 12px;
}
.experience-picker__options article {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 11px;
  background: #fff;
}
.experience-picker__options article.is-added {
  background: #f8fafc;
}
.experience-picker__options p {
  margin: 0;
  color: #334155;
  font-size: 12px;
  line-height: 1.45;
}
.experience-picker__options button {
  min-height: 34px;
  padding: 0 10px;
  border: 1px solid #0f172a;
  border-radius: 9px;
  background: #0f172a;
  color: #fff;
  font: inherit;
  font-size: 11px;
  font-weight: 800;
  cursor: pointer;
}
.experience-picker__options button:disabled {
  border-color: #cbd5e1;
  background: #e2e8f0;
  color: #475569;
  cursor: default;
}
.experience-picker__manual,
.experience-picker__safety {
  margin: 11px 0 0;
  color: #64748b;
  font-size: 11px;
  line-height: 1.5;
}
.experience-picker__safety {
  padding-top: 9px;
  border-top: 1px solid #e2e8f0;
}
@media (max-width: 760px) {
  .experience-picker,
  [dir="rtl"].experience-picker {
    left: 8px;
    right: 8px;
    bottom: 88px;
    width: auto;
    max-height: min(520px, calc(100vh - 140px));
  }
  .experience-picker__options article {
    grid-template-columns: 1fr;
  }
  .experience-picker__options button {
    width: 100%;
  }
}
'''
    css_path.write_text(css, encoding="utf-8")

print("Applied contextual experience description picker.")
