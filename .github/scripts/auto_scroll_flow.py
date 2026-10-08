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

import { useEffect } from 'react';

const continued = /continue|next step|متابعة|التالي|استمرار|أكمل/i;
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
  useEffect(() => {
    const onClick = (event: MouseEvent) => {
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
      const progress = panel.querySelector('.wizard-progress-meta')?.textContent || '';
      const match = progress.match(/Section\s+(\d+)\s+of\s+(\d+)/i);
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
      const target = event.target;
      if ((target instanceof HTMLInputElement ||
           target instanceof HTMLTextAreaElement ||
           target instanceof HTMLSelectElement) &&
          target.closest('.wizard-section-card')) {
        startingValues.set(target, target.value);
      }
    };

    const onFinishedField = (event: FocusEvent) => {
      if (!/\/builder\/?$/.test(window.location.pathname)) return;
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
      window.setTimeout(() => {
        if (!document.contains(card) || activeSection(panel) !== step ||
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
    document.addEventListener('focusin', onFocusField);
    document.addEventListener('focusout', onFinishedField);
    return () => {
      document.removeEventListener('click', onClick);
      document.removeEventListener('focusin', onFocusField);
      document.removeEventListener('focusout', onFinishedField);
    };
  }, []);

  return null;
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
print("Installed non-submitting auto-scroll for template selection and guided Builder navigation.")

