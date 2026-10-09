"""Make each intentional Sirati step lead visually to the next action.

User-initiated field completion may move between CV editing sections. Never
trigger checkout, save, print or payment actions. No persistence/auth changes.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
target = root / "components" / "FlowAutoScroll.tsx"
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text("""'use client';

import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';

const continued = /continue|next step|متابعة|التالي|استمرار|أكمل/i;
const PREF_KEY = 'sirati.autoAdvance.enabled.v1';
function asWesternDigits(value: string): string {
  return value.replace(/[٠-٩۰-۹]/g, digit => {
    const code = digit.charCodeAt(0);
    return String(code >= 0x6f0 ? code - 0x6f0 : code - 0x660);
  });
}
const stepNavigation = /^(?:continue|next step|←?\\s*back|previous|متابعة|التالي|رجوع|السابق|عودة)/i;

function visible(element: HTMLElement): boolean {
  return element.getClientRects().length > 0 &&
    getComputedStyle(element).visibility !== 'hidden';
}

function findContinue(root: ParentNode): HTMLButtonElement | undefined {
  return Array.from(root.querySelectorAll<HTMLButtonElement>('button'))
    .find(button => !button.disabled && visible(button) &&
      continued.test((button.textContent || '').trim()));
}

function reveal(element: HTMLElement, focus = false): void {
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  element.style.scrollMarginTop = '94px';
  element.scrollIntoView({ behavior: reduced ? 'auto' : 'smooth', block: 'start' });
  if (focus) element.focus({ preventScroll: true });
}

function afterRender(callback: () => void): void {
  window.setTimeout(() => window.requestAnimationFrame(() =>
    window.requestAnimationFrame(callback)), 90);
}

/**
 * Only progress after an intentional blur of a suitable *completed* field;
 * never on page load, typing, draft restoration, save, or payment.
 * Manual Continue and Back remain available.
 */
export default function FlowAutoScroll() {
  const [enabled, setEnabled] = useState(true);
  const enabledRef = useRef(true);
  const [host, setHost] = useState<HTMLElement | null>(null);
  const [arabic, setArabic] = useState(false);

  useEffect(() => {
    try {
      const stored = window.sessionStorage.getItem(PREF_KEY);
      if (stored === 'off') {
        enabledRef.current = false;
        setEnabled(false);
      }
    } catch { /* Private browsing: keep the in-memory preference. */ }
    const scan = () => {
      if (!/\/builder\/?$/.test(window.location.pathname)) {
        setHost(null);
        return;
      }
      const el = document.querySelector<HTMLElement>('.wizard-progress-block');
      setHost(current => current === el ? current : el);
      const dir = document.querySelector('.cv-sheet')?.getAttribute('dir');
      setArabic(dir === 'rtl' || document.documentElement.dir === 'rtl');
    };
    const observer = new MutationObserver(scan);
    observer.observe(document.body, {childList:true, subtree:true});
    scan();
    return () => observer.disconnect();
  }, []);

  const changePreference = (checked: boolean) => {
    enabledRef.current = checked;
    setEnabled(checked);
    try { window.sessionStorage.setItem(PREF_KEY, checked ? 'on' : 'off'); } catch {}
  };

  useEffect(() => {
    let pending: number | null = null;
    const cancelPending = () => {
      if (pending !== null) window.clearTimeout(pending);
      pending = null;
    };
    const onClick = (event: MouseEvent) => {
      cancelPending();
      if (!(event.target instanceof Element)) return;
      const path = window.location.pathname;
      if (/\\/templates\\/?$/.test(path) &&
          event.target.closest('.template-choice')) {
        afterRender(() => {
          const cta = findContinue(document.querySelector('main') || document);
          if (cta) reveal(cta, true);
        });
        return;
      }
      if (!/\\/builder\\/?$/.test(path)) return;
      const button = event.target.closest('button');
      if (!button || !stepNavigation.test((button.textContent || '').trim())) return;
      afterRender(() => {
        const panel = document.querySelector<HTMLElement>('.wizard-panel');
        if (panel && visible(panel)) reveal(panel);
      });
    };

    // The active CV section is numbered 1–9 in Builder's own progress line.
    function activeSection(panel: HTMLElement): number {
      const progress = asWesternDigits(panel.querySelector('.wizard-progress-meta > span')?.textContent || '');
      const match = progress.match(/(?:Section|القسم|الخطوة|مرحلة)\s+(\d+)\s+(?:of|من|\/)\s+(\d+)/i);
      return match && Number(match[2]) === 9 ? Number(match[1]) - 1 : -1;
    }

    function formValues(card: HTMLElement, label: string): Array<{ value: string; valid: boolean }> {
      return Array.from(card.querySelectorAll<HTMLElement>('.field'))
        .filter(field => field.querySelector('label')?.textContent?.trim() === label)
        .map(field => {
          const input = field.querySelector<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>(
            'input:not([type="file"]):not([type="hidden"]),textarea,select'
          );
          return { value: input?.value.trim() || '', valid: input?.checkValidity() ?? false };
        });
    }

    function filled(card: HTMLElement, label: string): boolean {
      const items = formValues(card, label);
      return items.length > 0 && items.every(item => Boolean(item.value) && item.valid);
    }

    function eligible(card: HTMLElement, step: number): boolean {
      switch (step) {
        case 0: {
          const email = formValues(card, 'Email')[0];
          const phone = formValues(card, 'Phone')[0];
          return filled(card, 'Full name') && filled(card, 'Professional title') &&
            filled(card, 'City & country') &&
            (!email?.value || email.valid) &&
            (Boolean(email?.value && email.valid) || Boolean(phone?.value));
        }
        case 1: {
          const summary = card.querySelector<HTMLTextAreaElement>('textarea');
          return Boolean(summary?.value.trim() && summary.value.trim().length >= 20 &&
            summary.checkValidity());
        }
        case 2:
          return ['Role', 'Company / hospital', 'Period', 'Achievements / responsibilities']
            .every(label => filled(card, label));
        case 3:
          return ['Degree / qualification', 'School / university', 'Period / graduation year']
            .every(label => filled(card, label));
        case 4:
          return ['Certification / license', 'Issuer'].every(label => filled(card, label));
        case 5:
          return ['Course / training', 'Provider'].every(label => filled(card, label));
        case 6:
          return ['Project name', 'Organization / context', 'Highlights']
            .every(label => filled(card, label));
        case 7:
          return filled(card, 'Skills');
        default:
          return false; // Never auto-finish Review, PDF, orders or payment.
      }
    }

    function finalField(step: number, field: string, card: HTMLElement): boolean {
      switch (step) {
        case 0:
          return field === 'LinkedIn / professional link' ||
            (field === 'City & country' && !formValues(card, 'LinkedIn / professional link')[0]?.value);
        case 1: return field === 'Professional summary' || field === 'Professional profile' || 
          Boolean(card.querySelector('textarea')?.closest('.field')?.querySelector('label')?.textContent?.trim() === field);
        case 2: return field === 'Achievements / responsibilities';
        case 3: return field === 'Details (optional)' || field === 'Period / graduation year';
        case 4: return field === 'Date / status';
        case 5: return field === 'Date';
        case 6: return field === 'Highlights';
        case 7: return field === 'Languages' ||
          (field === 'Skills' && Boolean(formValues(card, 'Languages')[0]?.value));
        default: return false;
      }
    }

    // A focus/blur without an edit must never cause the user to lose a step.
    const startingValues = new WeakMap<HTMLElement, string>();
    const onFocusField = (event: FocusEvent) => {
      cancelPending(); // A new interaction invalidates an older blur's scheduled step.
      const target = event.target;
      if ((target instanceof HTMLInputElement ||
           target instanceof HTMLTextAreaElement ||
           target instanceof HTMLSelectElement) &&
          target.closest('.wizard-section-card')) {
        startingValues.set(target, target.value);
      }
    };

    const onFinishedField = (event: FocusEvent) => {
      if (!enabledRef.current || !/\/builder\/?$/.test(window.location.pathname)) return;
      const target = event.target;
      if (!(target instanceof HTMLInputElement ||
            target instanceof HTMLTextAreaElement ||
            target instanceof HTMLSelectElement)) return;
      if (target instanceof HTMLInputElement &&
          ['hidden', 'file', 'checkbox', 'radio'].includes(target.type)) return;
      if (startingValues.get(target) === undefined ||
          startingValues.get(target) === target.value) return;
      const card = target.closest<HTMLElement>('.wizard-section-card');
      const panel = card?.closest<HTMLElement>('.wizard-panel');
      if (!card || !panel) return;
      const step = activeSection(panel);
      if (step < 0 || step >= 8) return;
      const field = target.closest('.field')?.querySelector('label')?.textContent?.trim() || '';
      if (!finalField(step, field, card)) return;

      // React controlled fields update on input/change. Delay until settled,
      // and never navigate away from new work the user has already focused.
      cancelPending();
      pending = window.setTimeout(() => {
        pending = null;
        if (!enabledRef.current || !document.contains(card) || activeSection(panel) !== step ||
            document.hidden || !eligible(card, step)) return;
        const active = document.activeElement;
        if (active instanceof HTMLElement && card.contains(active) &&
            active !== target) return;
        const next = findContinue(panel);
        if (!next || !next.closest('.wizard-footer-nav')) return;
        next.click(); // Existing Builder goNext owns the actual section change.
      }, 420);
    };

    document.addEventListener('click', onClick);
    document.addEventListener('pointerdown', cancelPending, true);
    document.addEventListener('input', cancelPending, true);
    document.addEventListener('focusin', onFocusField);
    document.addEventListener('focusout', onFinishedField);
    return () => {
      cancelPending();
      document.removeEventListener('click', onClick);
      document.removeEventListener('pointerdown', cancelPending, true);
      document.removeEventListener('input', cancelPending, true);
      document.removeEventListener('focusin', onFocusField);
      document.removeEventListener('focusout', onFinishedField);
    };
  }, []);

  // A tiny opt-out by the existing progress, not another floating overlay.
  if (!host) return null;
  return createPortal(
    <label className="sirati-auto-advance-control">
      <input type="checkbox" aria-label="Auto-advance completed CV sections" checked={enabled}
        onChange={event => changePreference(event.target.checked)} />
      <span>{arabic ? 'الانتقال التلقائي بعد إكمال الخطوة' : 'Auto-advance completed steps'}</span>
    </label>,
    host
  );
}
""", encoding="utf-8")

layout_path = root / "app" / "layout.tsx"
layout = layout_path.read_text(encoding="utf-8")
imp = "import FlowAutoScroll from '@/components/FlowAutoScroll';\n"
if imp not in layout:
    layout = imp + layout
if "<FlowAutoScroll />" not in layout:
    if "</body>" not in layout:
        raise RuntimeError("Missing layout body for FlowAutoScroll")
    layout = layout.replace("</body>", "        <FlowAutoScroll />\n      </body>", 1)
layout_path.write_text(layout, encoding="utf-8")
with (root / "app" / "globals.css").open("a", encoding="utf-8") as css:
    css.write("""
/* Visible, opt-out navigation preference next to existing Builder progress. */
.sirati-auto-advance-control {
  display: inline-flex; align-items: center; flex-wrap: wrap; gap: 7px;
  max-width: 100%; min-height: 32px; margin-top: 7px;
  font-size: 12px; font-weight: 650; line-height: 1.35; color: #475569;
  cursor: pointer;
}
.sirati-auto-advance-control input { width: 17px; height: 17px; margin: 0; accent-color: #1d4ed8; }
.sirati-auto-advance-control:focus-within { outline: 2px solid #2563eb; outline-offset: 3px; border-radius: 4px; }
@media(max-width: 500px) { .sirati-auto-advance-control { font-size: 11px; } }
@media print { .sirati-auto-advance-control { display: none; } }
""")
print("Hardened auto-advance timing, localized step detection and visible opt-out.")

