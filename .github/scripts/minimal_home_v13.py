"""Sirati V13: short, accessible, five-part mobile-first landing page.

Runs after V12. Marketing presentation only; keeps all actual CV and career
features, FAQ anchors, support destination, and existing sitewide navigation.
"""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
page = root / "app/page.tsx"
cssfile = root / "app/globals.css"
home = page.read_text(encoding="utf-8")

def replace_once(old, new, label):
    global home
    count = home.count(old)
    if count != 1:
        raise RuntimeError(f"V13 {label}: expected one anchor, got {count}")
    home = home.replace(old, new, 1)

def section(start, label):
    if home.count(start) != 1:
        raise RuntimeError(f"V13 {label}: expected exactly one section")
    a = home.index(start)
    b = home.find("\n      </section>", a)
    if b < 0:
        raise RuntimeError(f"V13 {label}: closing tag missing")
    b += len("\n      </section>")
    return a, b, home[a:b]

# Retain the sitewide logo/navigation introduced in V12.
if '<header className="marketing-header">' in home:
    raise RuntimeError("V13 expects V12's unified navigation")

old = """          <h1>
            Your career.
            <span>Beautifully presented.</span>
          </h1>"""
new = """          <h1>
            Build a CV
            <span>that gets noticed.</span>
          </h1>"""
replace_once(old, new, "short heading")
replace_once(
    "Build your CV, write cover letters, improve your LinkedIn profile and prepare for interviews — all free, in Arabic and English.",
    "Build your CV for free with professional templates and PDF export. Get help with cover letters, LinkedIn and interviews too.",
    "clear hero introduction",
)
replace_once(
    """            <Link className="btn btn-primary btn-lg" href="/career-tools/">
              Explore Career Studio <span aria-hidden="true">→</span>
            </Link>
            <Link className="btn btn-quiet btn-lg" href="/templates">
              Create my CV
            </Link>""",
    """            <Link className="btn btn-primary btn-lg" href="/templates">
              Create My CV <span aria-hidden="true">→</span>
            </Link>
            <Link className="btn btn-quiet btn-lg" href="/career-tools/">
              Explore Career Tools
            </Link>""",
    "CV-first call to action",
)

# The 33-template library already provides authentic, full-size previews.
# Three existing lightweight homepage previews suffice for discovery.
start = '        <div className="product-stage sirati-v2-product-stage"'
a, b, _ = section(start, "hero sample")
# section() finds the hero close; remove only the sample and preserve it.
home = home[:a] + home[b - len("\n      </section>"):]
# Remove redundant proof/feature strip; their claims remain in the concise lead.
m = re.search(r'\n          <div className="hero-proof">[\s\S]*?\n          </div>\n', home)
if not m or home.count('className="hero-proof"') != 1:
    raise RuntimeError("V13 hero-proof anchor changed")
home = home[:m.start()] + home[m.end():]
a, b, _ = section('      <section className="feature-strip"', "feature strip")
home = home[:a] + home[b:]

# Reuse exactly the current three template cards; show them before short steps.
step_key = '      <section className="section section-soft" id="how-it-works">'
template_key = '      <section className="section" id="templates">'
sa, sb, steps_section = section(step_key, "steps")
ta, tb, template_section = section(template_key, "templates")
if not (sa < sb < ta < tb):
    raise RuntimeError("V13 expected steps preceding template showcase")
home = home[:sa] + template_section + "\n\n" + steps_section + home[tb:]

replace_once(
    '<Link className="text-link" href="/auth?next=/templates">Try them in the builder →</Link>',
    '<Link className="text-link" href="/templates">View all 33 templates →</Link>',
    "template-library link",
)
replace_once('Clean layouts. Your content stays the focus.',
             'Choose your style', "template section title")
replace_once('From blank page to application-ready.',
             'Create in 3 easy steps', "steps section title")

# Keep the existing three accessible process cards and id anchor; shorten copy.
home, stepcount = re.subn(
    r'const steps = \[[\s\S]*?\n\];',
    """const steps = [
  { number: '01', title: 'Choose', text: 'Pick a professional CV template.' },
  { number: '02', title: 'Write', text: 'Add and refine your real experience.' },
  { number: '03', title: 'Download', text: 'Save your finished CV as a free PDF.' }
];""",
    home, count=1,
)
if stepcount != 1:
    raise RuntimeError("V13 steps data anchor missing")

# Replace obsolete long-form sales pitch with one honest, smaller tools section.
a, b, _ = section('      <section className="section section-dark" id="services">', "services")
tools = """      <section className="section sirati-v13-tools" id="services" aria-labelledby="sirati-v13-tools-title">
        <div className="container sirati-v13-tools-inner">
          <div>
            <span className="eyebrow">FREE CAREER TOOLS</span>
            <h2 id="sirati-v13-tools-title">More than a CV</h2>
            <p>Cover letters · LinkedIn · Interview preparation</p>
          </div>
          <Link className="btn btn-secondary" href="/career-tools/">Explore free tools →</Link>
        </div>
      </section>"""
home = home[:a] + tools + home[b:]

# Three truthful and concise answers, still using the existing FAQ accordion.
home, faqcount = re.subn(
    r'const faqItems = \[[\s\S]*?\n\];',
    """const faqItems = [
  { question: 'Is Sirati free?',
    answer: 'Yes. CV templates, smart writing tools and browser PDF export are free.' },
  { question: 'Can I download my CV as PDF?',
    answer: 'Yes. Choose Print / Save free PDF, then Save as PDF in your browser.' },
  { question: 'Can I create a CV in Arabic?',
    answer: 'Yes. You can use Arabic with right-to-left layout or English.' }
];""",
    home, count=1,
)
if faqcount != 1:
    raise RuntimeError("V13 FAQ data anchor missing")

# Preserve the #support deep link and real email, without a whole promo card.
a, b, support = section('      <section className="section support-section" id="support">', "support")
match = re.search(r'href="(mailto:[^"]+)"', support)
if not match:
    raise RuntimeError("V13 existing support email link missing")
home = home[:a] + (
    '      <div className="container sirati-v13-support" id="support">'
    '<span>Need help?</span> <a href="' + match.group(1) +
    '">Contact Support</a></div>'
) + home[b:]

a, b, _ = section('      <section className="container final-cta">', "extra closing pitch")
home = home[:a] + home[b:]
replace_once('Questions before you start?', 'Frequently asked questions', "FAQ title")
home = home.replace('Here are the essentials about language, saving, export and assisted services.',
                    'The essentials, before you begin.')

# Guard all major destinations in the final page.
for anchor in ['id="templates"', 'id="how-it-works"', 'id="services"',
               'id="faq"', 'id="support"', 'href="/templates"',
               'href="/career-tools/"']:
    if anchor not in home:
        raise RuntimeError("V13 required journey anchor absent: " + anchor)
page.write_text(home, encoding="utf-8")

css = cssfile.read_text(encoding="utf-8")
if '/* Sirati V13 minimalist landing */' in css:
    raise RuntimeError("V13 already applied")
css += r"""
/* Sirati V13 minimalist landing — only Home; printing CVs is untouched. */
@media screen {
 .marketing-page .marketing-hero {
    display:block; min-height:0; max-width:1010px;
    padding:clamp(28px,4vw,48px) clamp(20px,5vw,66px);
    margin:12px auto 16px; border-radius:23px;
 }
 .marketing-page .marketing-hero .hero-copy {
    max-width:720px; margin:0 auto; text-align:center;
 }
 .marketing-page .marketing-hero h1 {
    max-width:720px; font-size:clamp(36px,5vw,58px);
    line-height:1.08; margin:18px auto 13px;
 }
 .marketing-page .marketing-hero .hero-lead {
    max-width:560px; margin:0 auto 20px;
    line-height:1.48; font-size:16px;
 }
 .marketing-page .marketing-hero .hero-actions { justify-content:center; margin:0 auto; }
 .marketing-page .marketing-hero .hero-kicker { margin-inline:auto; }
 .marketing-page > .section { padding-block:clamp(28px,4vw,48px); }
 .marketing-page .section-heading-marketing { margin-bottom:18px; }
 .marketing-page .section-heading-marketing h2 { font-size:clamp(25px,3vw,34px); }
 .marketing-page #templates .template-card-copy p { font-size:12px; line-height:1.45; }
 .marketing-page .process-grid { gap:12px; }
 .marketing-page .process-card { padding:18px; }
 .marketing-page .sirati-v13-tools { background:#f0f6f0; }
 .marketing-page .sirati-v13-tools-inner {
    display:flex; justify-content:space-between; align-items:center;
    gap:20px; flex-wrap:wrap;
 }
 .marketing-page .sirati-v13-tools h2 { font-size:clamp(24px,3vw,34px); margin:4px 0; }
 .marketing-page .sirati-v13-tools p { margin:3px 0; color:#53675b; }
 .marketing-page .sirati-v13-support {
    display:flex; align-items:center; justify-content:center; gap:8px;
    padding:16px 12px 25px; font-size:13px; color:#4f6255;
 }
 .marketing-page .sirati-v13-support a { color:#195744; text-underline-offset:3px; font-weight:700; }
 .marketing-page .sirati-v13-support a:focus-visible { outline:3px solid #d7b87c; }
 .marketing-page .faq-layout { gap:20px; }
 .marketing-page .faq-item { margin-bottom:7px; }
}
@media screen and (max-width:640px) {
 .marketing-page .marketing-hero {
    padding:24px 17px; margin:9px 10px 12px;
    border-radius:18px;
 }
 .marketing-page .marketing-hero h1 {
    font-size:clamp(30px,8vw,38px); margin:14px auto 10px;
 }
 .marketing-page .marketing-hero .hero-lead {
    font-size:14px; line-height:1.48; margin-bottom:16px;
 }
 .marketing-page .marketing-hero .hero-actions { display:grid; gap:9px; }
 .marketing-page .marketing-hero .hero-actions .btn { width:100%; min-height:46px; }
 .marketing-page > .section { padding-block:26px; }
 .marketing-page .section-heading-marketing { gap:9px; margin-bottom:12px; }
 .marketing-page .section-heading-marketing p { font-size:13px; line-height:1.45; }
 .marketing-page #templates .template-showcase {
    display:grid; grid-template-columns:repeat(3,minmax(0,1fr));
    gap:7px; align-items:stretch;
 }
 .marketing-page #templates .template-card {
    grid-column:auto; min-width:0; width:auto; padding:7px;
    border-radius:12px;
 }
 .marketing-page #templates .template-preview {
    min-height:0; height:104px; max-height:104px;
    border-radius:8px; margin:0 0 7px;
 }
 .marketing-page #templates .template-card-copy h3 { font-size:12px; }
 .marketing-page #templates .template-card-copy p { display:none; }
 .marketing-page #templates .template-badge { font-size:9px; }
 .marketing-page .process-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:8px; }
 .marketing-page .process-card { padding:12px 9px; min-width:0; }
 .marketing-page .process-card h3 { font-size:13px; }
 .marketing-page .process-card p { font-size:11px; line-height:1.4; }
 .marketing-page .sirati-v13-tools-inner { display:block; }
 .marketing-page .sirati-v13-tools .btn { width:100%; margin-top:14px; }
 .marketing-page .faq-layout { gap:12px; }
 .marketing-page .faq-intro p { font-size:13px; }
 .marketing-page .marketing-footer { padding-top:26px; }
}
@media (prefers-reduced-motion: reduce) {
 .marketing-page .sirati-v13-tools .btn { transition:none; }
}
"""
# Visual QA refinement: prevent featured badge/title collision at 320/390px,
# remove inherited 210px process-card minimum and reduce FAQ headline scale.
css += r"""
@media screen {
 .marketing-page #how-it-works .process-card {
    min-height:0;
    height:auto;
 }
 .marketing-page #how-it-works .process-card h3 {
    margin:22px 0 6px;
 }
 .marketing-page #faq .faq-intro h2 {
    font-size:clamp(27px,3vw,36px);
    line-height:1.13;
 }
}
@media screen and (max-width:640px) {
 .marketing-page #templates .template-card-copy,
 .marketing-page #templates .template-card-featured .template-card-copy {
    padding:4px 1px 5px;
    min-width:0;
 }
 .marketing-page #templates .template-card-copy > div {
    display:flex;
    flex-direction:column;
    align-items:flex-start;
    gap:3px;
    min-width:0;
 }
 .marketing-page #templates .template-card-copy h3 {
    margin:0;
    max-width:100%;
    font-size:12px;
    line-height:1.2;
    overflow-wrap:anywhere;
 }
 .marketing-page #templates .template-badge {
    font-size:8px;
    letter-spacing:0;
    padding:3px 5px;
    line-height:1.1;
    white-space:normal;
 }
 .marketing-page #how-it-works .process-card {
    min-height:0;
    padding:11px 9px;
 }
 .marketing-page #how-it-works .process-card h3 {
    margin:15px 0 5px;
 }
 .marketing-page #faq .faq-intro h2 {
    font-size:clamp(26px,7vw,31px);
    line-height:1.12;
 }
}
"""
cssfile.write_text(css, encoding="utf-8")
print("PASS: Sirati V13 minimal CV-first homepage, 3 template examples, 3 steps, tools, FAQ and support.")
