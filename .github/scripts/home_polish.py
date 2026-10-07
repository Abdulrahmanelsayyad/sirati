from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
page = root / "app" / "page.tsx"
text = page.read_text(encoding="utf-8")

# Add a compact trust/value strip directly before the first major content section after the hero.
quick = r'''
      <section className="home-quickstart" aria-label="How Sirati works">
        <div className="container home-quickstart__inner">
          <div><strong>1</strong><span>Choose a template</span></div>
          <div><strong>2</strong><span>Fill your CV step by step</span></div>
          <div><strong>3</strong><span>Review and save</span></div>
          <a className="btn btn-primary" href="/templates">Start your CV</a>
        </div>
      </section>

'''

if 'className="home-quickstart"' not in text:
    candidates = [
        '      <section className="section"',
        '      <section className="container section"',
        '      <section id="'
    ]
    inserted = False
    for anchor in candidates:
        pos = text.find(anchor)
        if pos != -1:
            text = text[:pos] + quick + text[pos:]
            inserted = True
            break
    if not inserted:
        marker = '</header>'
        if marker in text:
            text = text.replace(marker, marker + '\n' + quick, 1)

# Make template journey link work with GitHub Pages base path by using the existing /templates link;
# prepare_pages handles internal builder routing separately.
page.write_text(text, encoding="utf-8")

css_path = root / "app" / "globals.css"
css = css_path.read_text(encoding="utf-8")
marker = "/* Sirati professional simple homepage */"
if marker not in css:
    css += r'''

/* Sirati professional simple homepage */
:root {
  --sirati-content: 1120px;
}

.container {
  max-width: var(--sirati-content);
}

.home-quickstart {
  padding: 14px 0 4px;
}
.home-quickstart__inner {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr)) auto;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border: 1px solid rgba(15, 23, 42, .08);
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 10px 30px rgba(15, 23, 42, .05);
}
.home-quickstart__inner > div {
  display: flex;
  align-items: center;
  gap: 9px;
  min-width: 0;
  color: #334155;
  font-size: 14px;
}
.home-quickstart__inner strong {
  display: inline-grid;
  place-items: center;
  flex: 0 0 28px;
  width: 28px;
  height: 28px;
  border-radius: 999px;
  background: #0f172a;
  color: #fff;
  font-size: 13px;
}
.home-quickstart__inner span {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Give the landing page more breathing room and clearer hierarchy. */
main > section {
  scroll-margin-top: 84px;
}
.section {
  padding-top: clamp(48px, 6vw, 78px);
  padding-bottom: clamp(48px, 6vw, 78px);
}
h1 {
  letter-spacing: -.035em;
  line-height: 1.05;
}
h2 {
  letter-spacing: -.025em;
  line-height: 1.12;
}
p {
  line-height: 1.7;
}
.btn {
  min-height: 44px;
  border-radius: 12px;
}
.btn-primary {
  box-shadow: 0 8px 22px rgba(15, 23, 42, .12);
}

/* Keep supporting cards cleaner and easier to scan. */
.card,
.feature-card,
.template-card,
.pricing-card,
.faq-item {
  border-color: rgba(15, 23, 42, .08);
  box-shadow: 0 8px 24px rgba(15, 23, 42, .045);
}

@media (max-width: 860px) {
  .home-quickstart__inner {
    grid-template-columns: 1fr 1fr;
  }
  .home-quickstart__inner > div:nth-child(3) {
    grid-column: 1 / 2;
  }
  .home-quickstart__inner > a {
    grid-column: 2 / 3;
    grid-row: 2 / 3;
  }
}

@media (max-width: 640px) {
  .section {
    padding-top: 42px;
    padding-bottom: 42px;
  }
  .home-quickstart {
    padding-top: 8px;
  }
  .home-quickstart__inner {
    grid-template-columns: 1fr;
    gap: 8px;
    padding: 12px;
  }
  .home-quickstart__inner > div,
  .home-quickstart__inner > div:nth-child(3),
  .home-quickstart__inner > a {
    grid-column: auto;
    grid-row: auto;
  }
  .home-quickstart__inner > a {
    width: 100%;
    justify-content: center;
    margin-top: 4px;
  }
}
'''
    css_path.write_text(css, encoding="utf-8")

print("Applied professional simple homepage polish.")
