"""Premium Editorial V2 — structural landing page redesign.

Only touches app/page.tsx and scoped homepage CSS. No business logic.
Runs after Premium Minimal V1 in the existing build reconstruction pipeline.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
page = root / "app" / "page.tsx"
css_file = root / "app" / "globals.css"
home = page.read_text(encoding="utf-8")
css = css_file.read_text(encoding="utf-8")

marker = "/* Sirati Premium Editorial V2 */"
if marker in css:
    raise RuntimeError("V2 design already applied")

expected = [
    'className="container hero marketing-hero"',
    'className="product-stage"',
    'className="home-quickstart"',
    'className="section sirati-studio"',
    'className="template-showcase"',
    'className="marketing-header"',
]
for token in expected:
    if token not in home:
        raise RuntimeError("Unexpected landing page structure: missing " + token)

# Replace generic marketing copy with a more confident, specific explanation.
old_title = "Your experience.\n            <span>Beautifully presented.</span>"
new_title = "A CV that looks\n            <span>as professional as you are.</span>"
if home.count(old_title) != 1:
    raise RuntimeError("Expected Premium Minimal V1 homepage headline")
home = home.replace(old_title, new_title, 1)

old_lead = "Create a CV that is clear, confident, and ready to share. Choose a professional template, tell your story, and see each change instantly."
new_lead = "Choose a polished template, add your real experience, and build a clear CV in Arabic or English. Preview your work before you decide to export."
if home.count(old_lead) != 1:
    raise RuntimeError("Expected homepage introduction text")
home = home.replace(old_lead, new_lead, 1)

# A believable document example, not blank gray placeholder lines.
# Deliberately label it as synthetic illustrative content, not the actual CV renderer.
start = '        <div className="product-stage" aria-label="Sirati CV builder preview">'
end = '\n      </section>'
if home.count(start) != 1:
    raise RuntimeError("Expected exactly one hero product mockup")
a = home.index(start)
b = home.index(end, a)
hero_preview = '''        <div className="product-stage sirati-v2-product-stage" aria-label="Illustrative sample CV preview">
          <div className="sirati-v2-preview-frame">
            <div className="sirati-v2-preview-topbar">
              <div className="sirati-v2-preview-brand"><span className="sirati-v2-preview-symbol">S</span> Sirati <span className="sirati-v2-preview-separator">/</span> Preview</div>
              <span className="sirati-v2-preview-state"><span aria-hidden="true" /> Sample layout</span>
            </div>
            <div className="sirati-v2-preview-body">
              <div className="sirati-v2-preview-sidebar" aria-hidden="true">
                <span className="sirati-v2-sidebar-title">CV EDITOR</span>
                <span className="sirati-v2-sidebar-item active"><b>01</b> Personal details</span>
                <span className="sirati-v2-sidebar-item"><b>02</b> Profile</span>
                <span className="sirati-v2-sidebar-item"><b>03</b> Experience</span>
                <span className="sirati-v2-sidebar-item"><b>04</b> Education</span>
                <span className="sirati-v2-sidebar-separator" />
                <span className="sirati-v2-sidebar-note">Your story. Your style.</span>
              </div>
              <div className="sirati-v2-paper-area">
                <article className="sirati-v2-paper" aria-label="Illustrative example resume for Alex Morgan">
                  <div className="sirati-v2-paper-topline"><span>EXAMPLE CV</span><span>MODERN</span></div>
                  <header className="sirati-v2-paper-heading">
                    <h2>Alex Morgan</h2>
                    <p>Product Designer</p>
                    <small>alex@example.com · London, UK · linkedin.com/in/example</small>
                  </header>
                  <div className="sirati-v2-paper-section">
                    <h3>PROFILE</h3>
                    <p>Designer focused on simplifying complex products through thoughtful research, clear interfaces and cross-team collaboration.</p>
                  </div>
                  <div className="sirati-v2-paper-section">
                    <h3>EXPERIENCE</h3>
                    <div className="sirati-v2-paper-role"><strong>Product Designer</strong><span>2022 – Present</span></div>
                    <small>Example Studio · London</small>
                    <p>Partner with product and engineering teams to design accessible, intuitive digital experiences.</p>
                  </div>
                  <div className="sirati-v2-paper-section sirati-v2-paper-columns">
                    <div><h3>EDUCATION</h3><strong>BA Design</strong><small>Example University</small></div>
                    <div><h3>SKILLS</h3><p>UX Research · UI Design · Prototyping</p></div>
                  </div>
                </article>
              </div>
            </div>
            <div className="sirati-v2-preview-footer">
              <span>Beautifully structured. Easy to update.</span>
              <span className="sirati-v2-preview-footer-step">01 / 09</span>
            </div>
          </div>
          <p className="sirati-v2-illustration-note">Illustrative sample content · Your final CV depends on your selected template</p>
        </div>'''
home = home[:a] + hero_preview + home[b:]

# The page already has a 3-step "How it works" section, so remove the
# additional three-step band and the four repeated workflow panels.
for section in (
    '      <section className="home-quickstart"',
    '      <section className="section sirati-studio"',
):
    if home.count(section) != 1:
        raise RuntimeError("Expected exactly one repeated steps section: " + section)
    p = home.index(section)
    q = home.find('\n      </section>', p)
    if q < 0:
        raise RuntimeError("Missing repeated section end for " + section)
    home = home[:p] + home[q + len('\n      </section>'):]

# The actual template showcase remains. Use it as the primary secondary CTA.
home = home.replace('Explore templates\n            </a>', 'View CV templates\n            </a>', 1)
page.write_text(home, encoding="utf-8")

css += r'''

/* Sirati Premium Editorial V2 */
.marketing-page .marketing-hero.sirati-v2-hero,
.marketing-page .marketing-hero {
  align-items: center;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, .95fr);
  gap: clamp(24px, 4.8vw, 68px);
  min-height: 630px;
}
.marketing-page .marketing-hero .hero-copy {
  position: relative;
  z-index: 2;
}
.marketing-page .marketing-hero h1 {
  font-size: clamp(44px, 5.3vw, 76px);
  line-height: 1.035;
  letter-spacing: -.055em;
  max-width: 670px;
}
.marketing-page .marketing-hero .hero-lead {
  max-width: 545px;
}
.marketing-page .sirati-v2-product-stage {
  position: relative;
  width: 100%;
  min-width: 0;
  min-height: auto;
  display: block;
  isolation: isolate;
}
.marketing-page .sirati-v2-product-stage::before {
  content: "";
  position: absolute;
  z-index: -1;
  inset: 7% -4% 0;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(112, 167, 132, .22), transparent 69%);
  filter: blur(16px);
  pointer-events: none;
}
.marketing-page .sirati-v2-preview-frame {
  overflow: hidden;
  border: 1px solid #d4ded7;
  border-radius: 21px;
  background: #f7f9f6;
  box-shadow: 0 26px 70px rgba(25, 58, 44, .14), 0 4px 14px rgba(20, 55, 41, .05);
}
.marketing-page .sirati-v2-preview-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 51px;
  padding: 10px 16px;
  border-bottom: 1px solid #dce5de;
  color: #1c352a;
  background: #fff;
  font-size: 12px;
}
.marketing-page .sirati-v2-preview-brand {
  display: flex;
  align-items: center;
  gap: 9px;
  font-weight: 750;
}
.marketing-page .sirati-v2-preview-symbol {
  display: grid;
  place-items: center;
  width: 25px;
  height: 25px;
  border-radius: 8px;
  color: #fff;
  background: #184237;
}
.marketing-page .sirati-v2-preview-separator { color: #b1beb3; }
.marketing-page .sirati-v2-preview-state {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: #496b58;
  font-size: 11px;
  white-space: nowrap;
}
.marketing-page .sirati-v2-preview-state span {
  width: 7px;
  height: 7px;
  background: #70a184;
  border-radius: 50%;
}
.marketing-page .sirati-v2-preview-body {
  display: grid;
  grid-template-columns: 130px minmax(0, 1fr);
  min-width: 0;
}
.marketing-page .sirati-v2-preview-sidebar {
  min-width: 0;
  padding: 20px 11px;
  background: #eaf0e9;
  border-right: 1px solid #dbe6db;
  display: flex;
  flex-direction: column;
  gap: 7px;
}
.marketing-page .sirati-v2-sidebar-title {
  margin: 0 8px 12px;
  color: #758479;
  font-size: 9px;
  letter-spacing: .12em;
  font-weight: 800;
}
.marketing-page .sirati-v2-sidebar-item {
  display: flex;
  align-items: center;
  gap: 7px;
  min-width: 0;
  padding: 11px 8px;
  border-radius: 9px;
  color: #617469;
  font-size: 10px;
  font-weight: 650;
  white-space: nowrap;
}
.marketing-page .sirati-v2-sidebar-item b {
  color: #799483;
  font-size: 9px;
}
.marketing-page .sirati-v2-sidebar-item.active {
  color: #164637;
  background: #fff;
  box-shadow: 0 3px 10px rgba(20, 60, 41, .05);
}
.marketing-page .sirati-v2-sidebar-separator {
  margin: 11px 7px 6px;
  border-top: 1px solid #d3e0d2;
}
.marketing-page .sirati-v2-sidebar-note {
  padding: 0 7px;
  color: #758b79;
  font-size: 9px;
  line-height: 1.4;
}
.marketing-page .sirati-v2-paper-area {
  display: grid;
  min-width: 0;
  padding: 22px 19px;
  align-items: center;
}
.marketing-page .sirati-v2-paper {
  position: relative;
  min-width: 0;
  padding: 24px 22px 27px;
  background: white;
  border: 1px solid #e9ebe7;
  box-shadow: 0 7px 28px rgba(36, 60, 45, .08);
  color: #23332a;
  font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
}
.marketing-page .sirati-v2-paper-topline {
  display: flex;
  justify-content: space-between;
  margin-bottom: 17px;
  color: #9aaa9d;
  font-size: 8px;
  letter-spacing: .12em;
  font-weight: 800;
}
.marketing-page .sirati-v2-paper-heading {
  border-bottom: 2px solid #184237;
  padding-bottom: 15px;
}
.marketing-page .sirati-v2-paper-heading h2 {
  font-size: clamp(23px, 2.8vw, 33px);
  letter-spacing: -.045em;
  line-height: 1.08;
  margin: 0;
  color: #163b30;
}
.marketing-page .sirati-v2-paper-heading p {
  margin: 6px 0 11px;
  color: #55695c;
  font-size: 12px;
  font-weight: 700;
  line-height: 1.4;
}
.marketing-page .sirati-v2-paper small {
  display: block;
  color: #708177;
  font-size: 9px;
  line-height: 1.6;
  overflow-wrap: anywhere;
}
.marketing-page .sirati-v2-paper-section {
  margin-top: 19px;
}
.marketing-page .sirati-v2-paper-section h3 {
  margin: 0 0 9px;
  color: #184237;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: .105em;
}
.marketing-page .sirati-v2-paper-section p {
  margin: 0;
  color: #53665a;
  font-size: 10px;
  line-height: 1.55;
}
.marketing-page .sirati-v2-paper-role {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 7px;
  font-size: 10px;
}
.marketing-page .sirati-v2-paper-role strong { font-weight: 780; }
.marketing-page .sirati-v2-paper-role span {
  color: #7e9084;
  white-space: nowrap;
  font-size: 8px;
}
.marketing-page .sirati-v2-paper-section > small { margin-bottom: 7px; }
.marketing-page .sirati-v2-paper-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  border-top: 1px solid #e8ece7;
  padding-top: 15px;
}
.marketing-page .sirati-v2-paper-columns strong { display: block; font-size: 10px; }
.marketing-page .sirati-v2-preview-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 11px 17px;
  color: #557064;
  border-top: 1px solid #dce5de;
  background: #fff;
  font-size: 11px;
}
.marketing-page .sirati-v2-preview-footer-step { font-weight: 800; letter-spacing: .12em; }
.marketing-page .sirati-v2-illustration-note {
  margin: 12px 0 0;
  text-align: center;
  color: #78877e;
  font-size: 11px;
}
.marketing-page .feature-strip { margin-top: 4px; }
.marketing-page .marketing-hero .hero-actions .btn {
  border-radius: 13px;
}
.marketing-page .marketing-hero .hero-actions .btn-quiet {
  border: 1px solid #bfd0c3;
  background: #fffefa;
  color: #285244;
}
@media (max-width: 1080px) {
  .marketing-page .sirati-v2-preview-body { grid-template-columns: 108px minmax(0, 1fr); }
  .marketing-page .sirati-v2-preview-sidebar { padding: 17px 7px; }
  .marketing-page .sirati-v2-sidebar-item { font-size: 9px; padding: 9px 5px; }
  .marketing-page .sirati-v2-paper-area { padding: 14px 11px; }
  .marketing-page .sirati-v2-paper { padding: 18px 15px; }
}
@media (max-width: 920px) {
  .marketing-page .marketing-hero {
    grid-template-columns: 1fr;
    min-height: 0;
    gap: 35px;
  }
  .marketing-page .sirati-v2-product-stage {
    max-width: 620px;
    margin-inline: auto;
  }
}
@media (max-width: 520px) {
  .marketing-page .marketing-hero { padding-top: 32px; gap: 27px; }
  .marketing-page .marketing-hero h1 {
    font-size: clamp(37px, 9.8vw, 47px);
    line-height: 1.07;
  }
  .marketing-page .sirati-v2-preview-body { grid-template-columns: minmax(0, 1fr); }
  .marketing-page .sirati-v2-preview-sidebar { display: none; }
  .marketing-page .sirati-v2-paper-area { padding: 13px; }
  .marketing-page .sirati-v2-paper { padding: 21px 17px 25px; }
  .marketing-page .sirati-v2-paper-heading h2 { font-size: 28px; }
  .marketing-page .sirati-v2-paper-heading p { font-size: 11px; }
  .marketing-page .sirati-v2-illustration-note { font-size: 10px; }
}
@media (prefers-reduced-motion: reduce) {
  .marketing-page .sirati-v2-preview-frame { animation: none; }
}
'''
css_file.write_text(css, encoding="utf-8")

# Build-time invariants: guard against accidental loss of key CTAs and content.
assert home.count('className="template-showcase"') == 1
assert home.count('className="product-stage sirati-v2-product-stage"') == 1
assert home.count('className="home-quickstart"') == 0
assert home.count('className="section sirati-studio"') == 0
assert home.count('className="manual-payment-card"') == 0
print("Applied Premium Editorial V2: readable synthetic CV hero and reduced duplicated process sections.")
