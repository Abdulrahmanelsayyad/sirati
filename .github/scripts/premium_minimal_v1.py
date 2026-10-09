"""Sirati Premium Minimal V1: presentation only, no auth/save/PDF changes."""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
page = root / "app" / "page.tsx"
css_path = root / "app" / "globals.css"
home = page.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")
marker = "/* Sirati Premium Minimal V1 */"

if marker in css:
    raise RuntimeError("Premium Minimal V1 already applied")
for required in ('className="marketing-page"', 'className="container hero marketing-hero"',
                 'className="wizard-builder-page"'):
    if required not in home and required != 'className="wizard-builder-page"':
        raise RuntimeError("Expected homepage markup missing: " + required)
if home.count("A clearer CV.") != 1 or home.count("A stronger first impression.") != 1:
    raise RuntimeError("Unexpected homepage headline; refusing blind replacement")

home = home.replace("A clearer CV.", "Your experience.", 1)
home = home.replace("A stronger first impression.", "Beautifully presented.", 1)
home = home.replace(
    "Turn your experience into a polished, structured CV with live preview, flexible sections and clean templates — all in one focused workspace.",
    "Create a CV that is clear, confident, and ready to share. Choose a professional template, tell your story, and see each change instantly.",
    1
)
page.write_text(home, encoding="utf-8")

css += r'''

/* Sirati Premium Minimal V1 */
:root {
  --pm-ink: #152923;
  --pm-green: #184237;
  --pm-green-hover: #235b4b;
  --pm-soft: #f7f8f5;
  --pm-surface: #fffefa;
  --pm-border: #dce5df;
  --pm-muted: #64736b;
  --pm-gold: #ae8d5a;
  --pm-shadow: 0 16px 48px rgba(16, 45, 35, .065);
}
.marketing-page,
.wizard-builder-page {
  --bg: var(--pm-soft);
  --card: var(--pm-surface);
  --text: var(--pm-ink);
  --muted: var(--pm-muted);
  --line: var(--pm-border);
  --accent: var(--pm-green);
  --accent-2: var(--pm-gold);
  color: var(--pm-ink);
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
}
.marketing-page :is(button, a, input, select, textarea):focus-visible,
.wizard-builder-page :is(button, a, input, select, textarea):focus-visible {
  outline: 3px solid #6c9e89;
  outline-offset: 3px;
}
.marketing-page :is(.btn, .template-card, .studio-card) {
  transition: border-color .18s ease, box-shadow .18s ease, transform .18s ease, background-color .18s ease;
}
.marketing-page .btn-primary,
.wizard-builder-page .btn-primary {
  background: var(--pm-green);
  color: #fff;
  box-shadow: 0 10px 24px rgba(24, 66, 55, .18);
  font-weight: 750;
}
.marketing-page .btn-primary:hover,
.wizard-builder-page .btn-primary:hover {
  background: var(--pm-green-hover);
}
.marketing-page .btn-secondary,
.wizard-builder-page .btn-secondary {
  border-color: var(--pm-border);
  background: rgba(255, 254, 250, .92);
  color: var(--pm-ink);
}
.marketing-page {
  background: radial-gradient(ellipse at 80% -5%, rgba(170, 202, 181, .23), transparent 38%), var(--pm-soft);
}
.marketing-page .marketing-header {
  background: rgba(255, 254, 250, .82);
  border-bottom: 1px solid var(--pm-border);
}
.marketing-page .marketing-nav { min-height: 82px; }
.marketing-page .brand-mark {
  background: var(--pm-green);
  color: #fff;
  box-shadow: 0 5px 18px rgba(24, 66, 55, .13);
}
.marketing-page .brand-lockup strong { letter-spacing: -.045em; }
.marketing-page .marketing-hero {
  padding-block: clamp(48px, 6vw, 94px) clamp(52px, 6vw, 94px);
  gap: clamp(26px, 4vw, 60px);
}
.marketing-page .hero-kicker {
  color: var(--pm-green);
  border-color: rgba(24, 66, 55, .13);
}
.marketing-page .kicker-dot { background: var(--pm-green); }
.marketing-page .marketing-hero h1 {
  max-width: 720px;
  margin-block: 20px 26px;
  font-size: clamp(45px, 5.7vw, 78px);
  line-height: 1.035;
  letter-spacing: -.055em;
}
.marketing-page .marketing-hero h1 span {
  display: block;
  color: var(--pm-green);
}
.marketing-page .hero-lead {
  color: var(--pm-muted);
  max-width: 585px;
  font-size: clamp(16px, 1.7vw, 19px);
  line-height: 1.7;
}
.marketing-page .hero-actions { gap: 12px; margin-top: 28px; }
.marketing-page .hero-actions .btn { min-height: 52px; padding-inline: 23px; }
.marketing-page .hero-proof { color: var(--pm-muted); }
.marketing-page .proof-icon { color: var(--pm-green); }
.marketing-page :is(.builder-mockup, .template-card, .studio-card, .faq-item) {
  border-color: var(--pm-border);
  box-shadow: var(--pm-shadow);
}
.marketing-page .builder-mockup { background: #fff; border-radius: 23px; }
.marketing-page .product-stage .stage-glow { opacity: .6; }
.marketing-page .feature-strip { background: #ecf2ed; border-block: 1px solid var(--pm-border); }
.marketing-page .feature-strip .strip-item > span { color: var(--pm-green); }
.marketing-page .home-quickstart__inner {
  border-color: var(--pm-border);
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(24, 66, 55, .05);
}
.marketing-page .home-quickstart__inner strong { background: var(--pm-green); }
.marketing-page .sirati-studio::before {
  background: radial-gradient(circle, rgba(142, 183, 159, .18), transparent 70%);
}
.marketing-page .studio-card--primary {
  background: linear-gradient(145deg, #163c32, #245346);
}
.marketing-page .studio-number { color: #b7cabc; }
.marketing-page .studio-progress-demo span.done,
.marketing-page .studio-progress-demo span.active { background: var(--pm-green); border-color: var(--pm-green); }
.marketing-page .studio-template-mini .mini-title { background: var(--pm-green); }
.marketing-page .template-card:hover,
.marketing-page .studio-card:not(.studio-card--primary):hover {
  border-color: #b4cbbd;
  box-shadow: 0 22px 50px rgba(16, 45, 35, .095);
  transform: translateY(-2px);
}
.marketing-page .final-cta { background: var(--pm-green); }
.wizard-builder-page {
  background: radial-gradient(ellipse at 12% 0%, rgba(180, 201, 181, .16), transparent 40%), var(--pm-soft);
}
.wizard-builder-page .wizard-builder-nav {
  border-bottom: 1px solid rgba(24, 66, 55, .08);
}
.wizard-builder-page .wizard-panel,
.wizard-builder-page .wizard-section-card {
  background: var(--pm-surface);
  border: 1px solid var(--pm-border);
  border-radius: 20px;
  box-shadow: 0 8px 30px rgba(24, 66, 55, .045);
}
.wizard-builder-page .wizard-panel-top h2 {
  color: var(--pm-ink);
  letter-spacing: -.035em;
}
.wizard-builder-page :is(.field input, .field textarea, .field select) {
  border-color: #d4dfd7;
  border-radius: 12px;
  background: #fff;
  min-height: 46px;
}
.wizard-builder-page :is(.field input, .field textarea, .field select):focus {
  border-color: #679a80;
  box-shadow: 0 0 0 3px rgba(76, 132, 103, .10);
}
.wizard-builder-page :is(.save-status, .step-badge) {
  color: var(--pm-green);
  background: #eaf3ed;
}
.wizard-builder-page .wizard-progress-block { color: var(--pm-ink); }
.wizard-builder-page .sirati-builder-action { font-weight: 700; }
@media (max-width: 760px) {
  .marketing-page .marketing-nav { min-height: 68px; }
  .marketing-page .marketing-hero {
    padding-top: 38px;
    padding-bottom: 50px;
    gap: 28px;
  }
  .marketing-page .marketing-hero h1 {
    font-size: clamp(40px, 9vw, 56px);
    margin-block: 16px 20px;
  }
  .marketing-page .hero-actions { gap: 9px; }
  .marketing-page .hero-actions .btn { min-height: 48px; }
  .marketing-page .studio-card { border-radius: 17px; }
}
@media (max-width: 640px) {
  .marketing-page .marketing-hero h1 { font-size: clamp(36px, 10vw, 48px); }
  .marketing-page .hero-actions { display: grid; grid-template-columns: 1fr; }
  .marketing-page .hero-actions .btn { width: 100%; }
  .marketing-page .home-quickstart__inner {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 8px;
  }
  .marketing-page .home-quickstart__inner > div {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    font-size: 11px;
    gap: 5px;
    line-height: 1.35;
  }
  .marketing-page .home-quickstart__inner span { white-space: normal; }
  .marketing-page .home-quickstart__inner > a {
    grid-column: 1 / -1;
    grid-row: auto;
  }
  .wizard-builder-page .wizard-panel,
  .wizard-builder-page .wizard-section-card { border-radius: 16px; }
}
@media (prefers-reduced-motion: reduce) {
  .marketing-page :is(.btn, .template-card, .studio-card) { transition: none; }
  .marketing-page .template-card:hover,
  .marketing-page .studio-card:hover { transform: none; }
}
@media print {
  .wizard-builder-page,
  .marketing-page { background: #fff !important; }
  .wizard-builder-page .wizard-panel,
  .wizard-builder-page .wizard-section-card { box-shadow: none !important; }
}
'''
css_path.write_text(css, encoding="utf-8")
print("Applied Premium Minimal V1: home copy, unified visual tokens, landing and Builder polish.")
