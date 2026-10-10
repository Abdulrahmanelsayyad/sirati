from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
css_path = root / "app" / "globals.css"
css = css_path.read_text(encoding="utf-8")

marker = "/* Sirati mobile builder containment fix */"
if marker not in css:
    css += r'''

/* Sirati mobile builder containment fix */
@media (max-width: 980px) {
  .wizard-builder-shell {
    grid-template-columns: minmax(0, 1fr);
    width: min(100%, calc(100vw - 32px));
    max-width: 100%;
    min-width: 0;
  }

  .wizard-panel,
  .wizard-preview-wrap,
  .preview-stage {
    width: 100%;
    max-width: 100%;
    min-width: 0;
  }

  .wizard-panel > *,
  .wizard-preview-wrap > *,
  .preview-stage > * {
    min-width: 0;
    max-width: 100%;
  }

  .wizard-preview-wrap .cv-sheet {
    box-sizing: border-box;
    width: 100%;
    max-width: 100%;
    min-width: 0;
  }

  .wizard-preview-wrap .preview-label {
    box-sizing: border-box;
    max-width: 100%;
    min-width: 0;
  }

  .wizard-preview-wrap .preview-label strong,
  .wizard-preview-wrap .preview-label span {
    min-width: 0;
    overflow-wrap: anywhere;
  }

  .wizard-footer-nav {
    box-sizing: border-box;
    width: auto;
    max-width: calc(100% + 20px);
    min-width: 0;
  }

  .cv-substeps {
    max-width: 100%;
    min-width: 0;
  }
}

@media (max-width: 720px) {
  .wizard-builder-page {
    overflow-x: clip;
  }

  .wizard-builder-shell {
    width: calc(100vw - 24px);
    padding-inline: 0;
  }

  .wizard-panel {
    box-sizing: border-box;
    padding: 16px;
  }

  .wizard-section-card,
  .wizard-panel-top,
  .wizard-progress-block,
  .wizard-document-settings,
  .wizard-footer-nav {
    max-width: 100%;
    min-width: 0;
  }

  .wizard-footer-nav {
    margin-inline: 0;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  }

  .wizard-footer-nav .btn {
    width: 100%;
    min-width: 0;
    white-space: normal;
  }

  .wizard-preview-wrap .preview-stage {
    overflow: hidden;
  }

  .wizard-preview-wrap .cv-sheet {
    min-height: auto;
    padding: 22px 18px;
  }

  .wizard-preview-wrap .cv-watermark {
    max-width: 100%;
  }
}

@media (max-width: 500px) {
  .wizard-builder-shell {
    width: calc(100vw - 20px);
  }

  .wizard-panel {
    padding: 14px;
  }

  .wizard-footer-nav {
    gap: 8px;
    padding: 9px;
  }

  .wizard-preview-wrap .cv-sheet {
    padding: 20px 16px;
  }
}
'''
    css_path.write_text(css, encoding="utf-8")


layer_marker = "/* Keep Builder feedback above the sticky CV preview */"
if layer_marker not in css:
    css += r'''

/* Keep Builder feedback above the sticky CV preview */
.wizard-panel {
  position: relative;
  z-index: 2;
}
.wizard-preview-wrap {
  z-index: 1;
}
'''
    css_path.write_text(css, encoding="utf-8")

print("Applied mobile builder containment fix.")


# Keep the user's active field unobstructed on narrow screens.
# The CV builder already has its own 'Section X of 9' progress, so its
# earlier onboarding ribbon is redundant once editing has started.
focus_marker = "/* Sirati mobile editor focus mode */"
if focus_marker not in css:
    css += r'''

/* Sirati mobile editor focus mode */
@media (max-width: 640px) {
  .wizard-builder-page .wizard-journey-wrap {
    display: none;
  }
  .wizard-builder-page .wizard-builder-shell {
    padding-top: 8px;
  }
  .wizard-builder-page .wizard-panel-top > div > p {
    display: none;
  }
  .builder-guide {
    bottom: max(8px, env(safe-area-inset-bottom));
  }
  .builder-guide__content {
    grid-template-columns: 44px minmax(0, 1fr) 44px;
    gap: 7px;
    padding: 6px 8px;
  }
  .builder-guide__nav {
    min-width: 44px;
    min-height: 44px;
  }
  /* The CV editor already has its own section navigator.
     Do not show the unrelated three-heading guide over it. */
  body:has(.wizard-builder-page) .builder-guide {
    display: none;
  }
  /* Compact manual navigation on the PHYSICAL RIGHT edge of the form.
     Never float/stick over editable content or the on-screen keyboard:
     deliberate Continue/Back taps only (Auto-Advance is retired). */
  .wizard-builder-page .wizard-footer-nav {
    position: static;
    inset: auto;
    transform: none;
    box-sizing: border-box;
    width: min(236px, 100%);
    max-width: 100%;
    min-width: 0;
    margin: 18px 0 0 auto;
    justify-self: end;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
    padding: 4px;
    border: 0;
    border-radius: 10px;
    background: transparent;
    box-shadow: none;
    direction: ltr;
  }
  .wizard-builder-page .wizard-footer-nav .btn {
    box-sizing: border-box;
    width: 100%;
    min-width: 0;
    min-height: 44px;
    padding: 8px 6px;
    font-size: 12px;
    line-height: 1.25;
    font-weight: 650;
    border-radius: 9px;
    white-space: normal;
    touch-action: manipulation;
  }
}
'''
    css_path.write_text(css, encoding="utf-8")

print("Applied mobile Builder focus-mode spacing and keyboard-safe navigation.")
