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

print("Applied mobile builder containment fix.")
