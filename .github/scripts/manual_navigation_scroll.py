"""Scroll to the next visible action after EXPLICIT customer navigation clicks.

This is not Auto-Advance. It never changes a CV Builder step, never listens
to form input/focus/blur, and never triggers save, print, order or payment.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
component = root / "components" / "ManualNavigationScroll.tsx"
component.parent.mkdir(parents=True, exist_ok=True)
component.write_text(r"""'use client';

import { useEffect } from 'react';

const continueLabel = /continue|next step|متابعة|التالي|استمرار|أكمل/i;
const manualNavigation = /^(?:continue|next step|←?\s*back|previous|متابعة|التالي|رجوع|السابق|عودة)/i;

function isVisible(element: HTMLElement): boolean {
  return element.getClientRects().length > 0 &&
    getComputedStyle(element).visibility !== 'hidden';
}

function afterRender(action: () => void) {
  window.setTimeout(() => window.requestAnimationFrame(() =>
    window.requestAnimationFrame(action)), 90);
}

function reveal(element: HTMLElement, focus = false) {
  element.style.scrollMarginTop = '94px';
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  element.scrollIntoView({behavior: reduced ? 'auto' : 'smooth', block: 'start'});
  if (focus) element.focus({preventScroll: true});
}

export default function ManualNavigationScroll() {
  useEffect(() => {
    const onClick = (event: MouseEvent) => {
      if (!(event.target instanceof Element)) return;
      const path = window.location.pathname;

      // Keep the separately requested template-selection -> Continue scroll.
      if (/\/templates\/?$/.test(path) && event.target.closest('.template-choice')) {
        afterRender(() => {
          const root = document.querySelector('main') || document;
          const button = Array.from(root.querySelectorAll<HTMLButtonElement>('button'))
            .find(candidate => !candidate.disabled && isVisible(candidate) &&
              continueLabel.test((candidate.textContent || '').trim()));
          if (button) reveal(button, true);
        });
        return;
      }

      // After a MANUAL Continue/Back click, reveal the step already selected
      // by the Builder itself. This NEVER invokes Continue/Back on its own.
      if (!/\/builder\/?$/.test(path)) return;
      const button = event.target.closest('button');
      if (!button || !manualNavigation.test((button.textContent || '').trim())) return;
      afterRender(() => {
        const panel = document.querySelector<HTMLElement>('.wizard-panel');
        if (panel && isVisible(panel)) reveal(panel);
      });
    };

    document.addEventListener('click', onClick);
    return () => document.removeEventListener('click', onClick);
  }, []);

  return null;
}
""", encoding="utf-8")

layout_path = root / "app" / "layout.tsx"
layout = layout_path.read_text(encoding="utf-8")
imp = "import ManualNavigationScroll from '@/components/ManualNavigationScroll';\n"
if imp not in layout:
    layout = imp + layout
if "<ManualNavigationScroll />" not in layout:
    if "</body>" not in layout:
        raise RuntimeError("Missing layout body for ManualNavigationScroll")
    layout = layout.replace("</body>", "        <ManualNavigationScroll />\n      </body>", 1)
layout_path.write_text(layout, encoding="utf-8")
print("Installed manual-only navigation scroll; no automatic CV step transitions.")
