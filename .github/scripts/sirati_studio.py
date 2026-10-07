from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
page = root / "app" / "page.tsx"
text = page.read_text(encoding="utf-8")

# Fix the free GitHub Pages path-safe homepage CTA if an earlier patch added a root-relative link.
text = text.replace('href="/templates"', 'href="./templates/"')

studio = r'''
      <section className="section sirati-studio" id="studio">
        <div className="container">
          <div className="studio-heading">
            <div>
              <div className="eyebrow">SIRATI STUDIO</div>
              <h2>A simpler way to build a professional CV</h2>
              <p>Choose a professional template, complete your information in short guided steps, and see your CV take shape as you work.</p>
            </div>
            <a className="btn btn-primary" href="./templates/">Create your CV</a>
          </div>

          <div className="studio-grid">
            <article className="studio-card studio-card--primary">
              <span className="studio-number">01</span>
              <h3>Choose your look</h3>
              <p>Start with a clean ATS-friendly template instead of a blank page.</p>
              <div className="studio-template-mini" aria-hidden="true">
                <span className="mini-title"></span>
                <span></span><span></span><span></span>
                <b></b>
                <span></span><span></span>
              </div>
            </article>

            <article className="studio-card">
              <span className="studio-number">02</span>
              <h3>Build step by step</h3>
              <p>Personal info, summary, experience, education, and skills — one clear section at a time.</p>
              <div className="studio-progress-demo" aria-hidden="true">
                <span className="done">✓</span><i></i>
                <span className="active">2</span><i></i>
                <span>3</span><i></i>
                <span>4</span>
              </div>
            </article>

            <article className="studio-card">
              <span className="studio-number">03</span>
              <h3>Polish without clutter</h3>
              <p>Keep the design professional with simple choices for layout, spacing, and presentation.</p>
              <div className="studio-controls-demo" aria-hidden="true">
                <span>Professional</span>
                <span>Clean</span>
                <span>ATS</span>
              </div>
            </article>

            <article className="studio-card">
              <span className="studio-number">04</span>
              <h3>Review with confidence</h3>
              <p>Check the final CV, save your document, and return to edit it whenever you need.</p>
              <div className="studio-review-demo" aria-hidden="true">
                <strong>Ready to review</strong>
                <span>✓ Contact details</span>
                <span>✓ Experience</span>
                <span>✓ Skills</span>
              </div>
            </article>
          </div>
        </div>
      </section>

'''

if 'className="section sirati-studio"' not in text:
    anchor = '      <section className="section support-section" id="support">'
    if anchor in text:
        text = text.replace(anchor, studio + anchor, 1)
    else:
        anchor = '      <section className="container final-cta">'
        if anchor in text:
            text = text.replace(anchor, studio + anchor, 1)

page.write_text(text, encoding="utf-8")

css_path = root / "app" / "globals.css"
css = css_path.read_text(encoding="utf-8")
marker = "/* Sirati Studio product experience */"
if marker not in css:
    css += r'''

/* Sirati Studio product experience */
.sirati-studio {
  position: relative;
  overflow: hidden;
}
.sirati-studio::before {
  content: "";
  position: absolute;
  inset: 10% auto auto 50%;
  width: min(760px, 80vw);
  height: 360px;
  transform: translateX(-50%);
  border-radius: 999px;
  background: radial-gradient(circle, rgba(99, 102, 241, .10), transparent 70%);
  pointer-events: none;
}
.studio-heading {
  position: relative;
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 28px;
  margin-bottom: 28px;
}
.studio-heading > div {
  max-width: 720px;
}
.studio-heading h2 {
  margin: 8px 0 10px;
  font-size: clamp(32px, 5vw, 54px);
  max-width: 760px;
}
.studio-heading p {
  margin: 0;
  max-width: 650px;
  color: #64748b;
  font-size: 17px;
}
.studio-grid {
  position: relative;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}
.studio-card {
  min-height: 270px;
  padding: 26px;
  border: 1px solid rgba(15, 23, 42, .08);
  border-radius: 22px;
  background: rgba(255, 255, 255, .96);
  box-shadow: 0 16px 45px rgba(15, 23, 42, .06);
}
.studio-card--primary {
  background: linear-gradient(145deg, #111827 0%, #1e293b 100%);
  color: #fff;
}
.studio-number {
  display: inline-flex;
  margin-bottom: 30px;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: .14em;
  color: #94a3b8;
}
.studio-card h3 {
  margin: 0 0 8px;
  font-size: 23px;
}
.studio-card p {
  margin: 0;
  max-width: 520px;
  color: #64748b;
}
.studio-card--primary p {
  color: #cbd5e1;
}
.studio-template-mini {
  width: min(250px, 80%);
  margin: 24px 0 0 auto;
  padding: 16px;
  border-radius: 12px 12px 4px 4px;
  background: #fff;
  box-shadow: 0 12px 26px rgba(0, 0, 0, .24);
}
.studio-template-mini span,
.studio-template-mini b {
  display: block;
  height: 5px;
  margin: 6px 0;
  border-radius: 999px;
  background: #dbe3ee;
}
.studio-template-mini .mini-title {
  width: 58%;
  height: 10px;
  background: #0f172a;
}
.studio-template-mini b {
  width: 32%;
  margin-top: 14px;
  background: #64748b;
}
.studio-progress-demo {
  display: flex;
  align-items: center;
  margin-top: 34px;
}
.studio-progress-demo span {
  display: grid;
  place-items: center;
  flex: 0 0 34px;
  width: 34px;
  height: 34px;
  border: 1px solid #cbd5e1;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  background: #fff;
}
.studio-progress-demo span.done,
.studio-progress-demo span.active {
  border-color: #111827;
  background: #111827;
  color: #fff;
}
.studio-progress-demo i {
  width: 38px;
  height: 2px;
  background: #e2e8f0;
}
.studio-controls-demo {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 36px;
}
.studio-controls-demo span {
  padding: 10px 14px;
  border: 1px solid #dbe3ee;
  border-radius: 999px;
  background: #f8fafc;
  font-size: 13px;
  font-weight: 700;
}
.studio-review-demo {
  display: grid;
  gap: 8px;
  margin-top: 28px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  background: #f8fafc;
}
.studio-review-demo strong {
  margin-bottom: 3px;
}
.studio-review-demo span {
  font-size: 13px;
  color: #475569;
}

@media (max-width: 760px) {
  .studio-heading {
    align-items: stretch;
    flex-direction: column;
  }
  .studio-heading > .btn {
    width: 100%;
    justify-content: center;
  }
  .studio-grid {
    grid-template-columns: 1fr;
  }
  .studio-card {
    min-height: auto;
    padding: 22px;
  }
}
'''
    css_path.write_text(css, encoding="utf-8")

print("Applied Sirati Studio product experience.")
