"""Make each intentional Sirati step lead visually to the next action.

Presentation-only enhancement: no form submission, data persistence, auth,
PDF or payment behavior is changed. Run after generated layout is ready.
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
 * Never programmatically click Continue: a customer's partially edited
 * or optional CV fields must not be bypassed. Only the viewport moves.
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

    const onFinishedField = (event: FocusEvent) => {
      if (!/\\/builder\\/?$/.test(window.location.pathname)) return;
      const target = event.target;
      if (!(target instanceof HTMLInputElement ||
            target instanceof HTMLTextAreaElement ||
            target instanceof HTMLSelectElement)) return;
      if (target instanceof HTMLInputElement &&
          ['hidden', 'file', 'checkbox', 'radio'].includes(target.type)) return;
      const panel = target.closest('.wizard-panel');
      if (!panel) return;
      const editors = Array.from(panel.querySelectorAll<
        HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
      >('input:not([type="hidden"]):not([type="file"]), textarea, select'))
        .filter(field => !field.disabled && visible(field) &&
          !(field instanceof HTMLInputElement &&
            ['checkbox', 'radio'].includes(field.type)));
      if (editors.at(-1) !== target || !target.value.trim() ||
          !target.checkValidity()) return;
      afterRender(() => {
        const cta = findContinue(panel);
        if (cta) reveal(cta);
      });
    };

    document.addEventListener('click', onClick);
    document.addEventListener('focusout', onFinishedField);
    return () => {
      document.removeEventListener('click', onClick);
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


# TEMP: inspect Builder step structure; remove before final review.
builder_lines = (root / "app" / "builder" / "page.tsx").read_text(encoding="utf-8").splitlines()
print("SIRATI_BUILDER_DIAG_V2_START")
for i, line in enumerate(builder_lines):
    if i >= 960: break
    if (i < 210 or i >= 630) and (i < 210 or any(word in line for word in ('currentSection', 'cvSections', 'goNext', 'goBack', 'field', 'input', 'select', 'textarea', 'button', 'onChange', 'wizard-', 'details', 'isLastSection'))):
        print(f"BUILDER_LINE {i+1}: {line[:260]}")
print("SIRATI_BUILDER_DIAG_V2_END")
