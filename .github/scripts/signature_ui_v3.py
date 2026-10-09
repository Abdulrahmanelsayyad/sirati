"""Sirati Signature UI V3 — presentation-only polish across public and signed-in journeys.

No changes to CV, payment, authentication, save/restore, link targets,
browser PDF or customer data. Scoped selectors and print-safe overrides.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
css_path = root / 'app/globals.css'
css = css_path.read_text(encoding='utf-8')
marker = '/* Sirati Signature UI V3 */'
if marker in css:
    raise RuntimeError('Signature V3 is already installed')
for anchor in ('.marketing-page .marketing-hero', '.career-card', '.sirati-career-shortcut', '.wizard-builder-page'):
    if anchor not in css:
        raise RuntimeError(f'Expected baseline design missing: {anchor}')
if not (root / 'app/career-tools/page.tsx').exists():
    raise RuntimeError('Career Tools route must exist before design layer is added')
css += r"""
/* Sirati Signature UI V3 — brand system; never affect printed CVs. */
@media screen {
  .marketing-page, .career-page, .wizard-builder-page {
    --s3-forest: #143b31;
    --s3-forest-strong: #102f28;
    --s3-gold: #dfc58e;
    --s3-paper: #fffefa;
    --s3-ink: #172e27;
    --s3-border: #dbe6de;
    --s3-radius: 18px;
  }
  .marketing-page {
    background: linear-gradient(180deg, #f4f7f2 0, #f8f9f6 720px, #fffefa 100%);
  }
  .marketing-page .marketing-header {
    background: rgba(255,254,250,.96);
    box-shadow: 0 8px 26px rgba(16,47,40,.055);
    border-bottom-color: #e0e9e1;
  }
  .marketing-page .marketing-nav { min-height: 76px; gap: 16px; }
  .marketing-page .brand-mark { background: #173f33; box-shadow: 0 6px 14px rgba(16,47,40,.14); }
  .marketing-page .marketing-hero {
    position: relative;
    isolation: isolate;
    overflow: hidden;
    min-height: 610px;
    margin-top: 22px;
    margin-bottom: 36px;
    padding: clamp(28px,5vw,64px) clamp(24px,5vw,62px);
    border-radius: 28px;
    border: 1px solid #245446;
    background: linear-gradient(123deg, #102c26 0%, #173c32 54%, #245342 100%);
    box-shadow: 0 30px 78px rgba(17,50,40,.18);
  }
  .marketing-page .marketing-hero::before {
    content: '';
    position: absolute;
    z-index: -1;
    width: 600px;
    aspect-ratio: 1;
    border: 1px solid rgba(224,240,220,.15);
    border-radius: 50%;
    top: -390px;
    right: -230px;
    box-shadow: 0 0 0 80px rgba(224,240,220,.022), 0 0 0 180px rgba(224,240,220,.016);
    pointer-events: none;
  }
  .marketing-page .marketing-hero .hero-copy { min-width: 0; }
  .marketing-page .marketing-hero h1 {
    color: #fffefa;
    font-weight: 780;
    letter-spacing: -.055em;
    text-wrap: balance;
  }
  .marketing-page .marketing-hero h1 span { color: #e5d2aa; }
  .marketing-page .marketing-hero .hero-lead { color: #dcebe1; line-height: 1.68; }
  .marketing-page .hero-kicker {
    display: inline-flex;
    align-items: center;
    max-width: 100%;
    color: #f0deb8;
    background: rgba(255,255,255,.07);
    border: 1px solid rgba(231,211,173,.31);
    border-radius: 999px;
  }
  .marketing-page .kicker-dot { background: #e0c68f; }
  .marketing-page .hero-proof, .marketing-page .hero-proof span { color: #e0e9e2; }
  .marketing-page .proof-icon { color: #f2d8a0; }
  .marketing-page .marketing-hero .hero-actions { gap: 12px; flex-wrap: wrap; }
  .marketing-page .marketing-hero .hero-actions .btn {
    min-height: 54px;
    border-radius: 12px;
    font-weight: 740;
    transition: transform .16s ease, background .16s ease, box-shadow .16s ease;
  }
  .marketing-page .marketing-hero .hero-actions .btn-primary {
    background: #e6c993;
    border-color: #e6c993;
    color: #183b31;
    box-shadow: 0 8px 22px rgba(3,18,12,.17);
  }
  .marketing-page .marketing-hero .hero-actions .btn-primary:hover {
    background: #f0d9ac;
    color: #14372c;
    transform: translateY(-2px);
  }
  .marketing-page .marketing-hero .hero-actions :is(.btn-quiet,.btn-secondary,.btn-light) {
    background: rgba(255,255,255,.085);
    border: 1px solid rgba(238,246,238,.48);
    color: #fffefa;
    box-shadow: none;
  }
  .marketing-page .marketing-hero .hero-actions :is(.btn-quiet,.btn-secondary,.btn-light):hover {
    background: rgba(255,255,255,.17);
  }
  .marketing-page .sirati-v2-preview-frame {
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,.7);
    box-shadow: 0 36px 65px rgba(0,15,9,.3), 0 3px 0 rgba(255,255,255,.09);
  }
  .marketing-page .sirati-v2-product-stage::before { opacity: .4; }
  .marketing-page .feature-strip {
    background: #f1f5f0;
    border-color: #e0e9e0;
  }
  .marketing-page :is(.template-card, .faq-item, .feature-card) {
    border-radius: 18px;
    border-color: var(--s3-border);
    background-color: var(--s3-paper);
    box-shadow: 0 10px 26px rgba(17,50,40,.048);
  }
  .marketing-page :is(.template-card, .feature-card):hover {
    box-shadow: 0 18px 36px rgba(17,50,40,.10);
  }
  .career-page {
    background: linear-gradient(180deg,#f2f6f1 0,#fbfcfa 620px,#f8faf7 100%);
  }
  .career-page .career-top {
    min-height: 76px;
    max-width: 1160px;
    border-bottom: 1px solid #dae6db;
  }
  .career-page .career-hero {
    position: relative;
    overflow: hidden;
    box-sizing: border-box;
    max-width: none;
    padding: clamp(28px,4vw,52px);
    margin: 16px 0 26px;
    border-radius: 22px;
    background: linear-gradient(115deg,#13392f,#235a46);
    color: #fffefa;
    box-shadow: 0 18px 45px rgba(17,50,40,.14);
  }
  .career-page .career-hero h1 { max-width: 720px; letter-spacing: -.042em; color: #fffefa; text-wrap: balance; }
  .career-page .career-hero p { color: #dcece0; max-width: 690px; }
  .career-page .career-hero .eyebrow { color: #efd7a6; }
  .career-page .career-tabs { margin-block: 28px 22px; gap: 9px; }
  .career-page .career-tab {
    border-radius: 12px;
    min-height: 46px;
    padding: 11px 18px;
    font-weight: 730;
    transition: background .15s ease, box-shadow .15s ease;
  }
  .career-page .career-tab.selected { background: #143b31; border-color: #143b31; box-shadow: 0 5px 18px rgba(20,59,49,.18); }
  .career-page .career-card {
    border-color: var(--s3-border);
    border-radius: 20px;
    box-shadow: 0 14px 38px rgba(23,55,40,.065);
  }
  .career-page .career-card h2 { color: #173f33; letter-spacing: -.026em; }
  .career-page .career-form :is(input,textarea,select),
  .career-page .career-result textarea {
    border-color: #cad9cf;
    border-radius: 12px;
    background: #fdfefd;
    transition: border-color .15s ease, box-shadow .15s ease;
  }
  .career-page .career-form :is(input,textarea,select):focus,
  .career-page .career-result textarea:focus {
    outline: none;
    border-color: #257456;
    box-shadow: 0 0 0 3px rgba(37,116,86,.12);
  }
  .career-page .career-result textarea { min-height: 325px; }
  .career-page .career-actions .btn { min-height: 44px; }
  .sirati-career-shortcut {
    border-color: #235444;
    background: linear-gradient(110deg,#14382f,#235a47);
    box-shadow: 0 16px 35px rgba(19,57,47,.14);
  }
  .sirati-career-shortcut-eyebrow { color: #efdbb2; }
  .sirati-career-shortcut h2 { color: #fffefa; }
  .sirati-career-shortcut p { color: #e0eee4; }
  .sirati-career-shortcut .sirati-career-shortcut-link {
    background: #e6ca97;
    color: #14372c;
    border-color: #e6ca97;
    font-weight: 750;
  }
  .wizard-builder-page .wizard-panel,
  .wizard-builder-page .wizard-section-card {
    border-color: #dbe6dd;
    background: #fffefa;
    box-shadow: 0 10px 27px rgba(22,62,42,.052);
  }
  .wizard-builder-page :is(.field input,.field textarea,.field select):focus {
    border-color: #327a5d;
    box-shadow: 0 0 0 3px rgba(50,122,93,.14);
  }
}
@media screen and (max-width:920px) {
  .marketing-page .marketing-hero { min-height: 0; padding: 35px 28px; gap: 28px; }
}
@media screen and (max-width:640px) {
  .marketing-page .marketing-nav { min-height: 65px; }
  .marketing-page .marketing-hero {
    margin-top: 12px;
    margin-bottom: 18px;
    padding: 29px 21px;
    border-radius: 19px;
  }
  .marketing-page .marketing-hero h1 { font-size: clamp(33px,8.9vw,46px); }
  .marketing-page .marketing-hero .hero-actions .btn { min-height: 50px; }
  .marketing-page .sirati-v2-preview-frame { border-radius: 13px; }
  .career-page .career-hero { padding: 25px 20px; border-radius: 18px; margin-top: 10px; }
  .career-page .career-tabs { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap: 8px; }
  .career-page .career-tab { min-width: 0; padding-inline: 9px; font-size: 13px; }
  .career-page .career-card { padding: 19px; border-radius: 16px; }
  .career-page .career-actions { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); }
  .career-page .career-actions .btn { white-space: normal; text-align: center; }
}
@media (prefers-reduced-motion: reduce) {
  .marketing-page .marketing-hero .hero-actions .btn,
  .career-page .career-tab { transition: none; transform: none; }
}
"""
css_path.write_text(css, encoding='utf-8')
print('PASS: Signature UI V3 styles applied to landing, Career Tools, My Documents, and builder.')
