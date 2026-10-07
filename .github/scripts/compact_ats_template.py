from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()

# Expand common template-id unions without changing persisted CV data.
for rel in ["lib/types.ts", "app/builder/page.tsx", "app/templates/page.tsx", "components/CvPreview.tsx"]:
    path = root / rel
    if not path.exists():
        continue
    s = path.read_text(encoding="utf-8")
    s = s.replace("'modern' | 'classic' | 'compact'", "'modern' | 'classic' | 'compact' | 'compact-ats'")
    s = s.replace('"modern" | "classic" | "compact"', '"modern" | "classic" | "compact" | "compact-ats"')
    path.write_text(s, encoding="utf-8")

# Add the fourth template card.
templates = root / "app" / "templates" / "page.tsx"
s = templates.read_text(encoding="utf-8")
if "id: 'compact-ats'" not in s:
    card = "{ id: 'compact-ats', name: 'Compact ATS', description: 'Single-column, content-first resume built for clear ATS parsing and fast recruiter scanning.', badge: 'ATS Focused' },\n  "
    anchors = [
        "{ id: 'modern', name: 'Professional ATS'",
        "{ id: 'modern', name: 'Modern'",
        "{ id: 'classic'",
    ]
    anchor = next((item for item in anchors if item in s), None)
    if not anchor:
        raise SystemExit("Could not locate a template card anchor")
    s = s.replace(anchor, card + anchor, 1)
templates.write_text(s, encoding="utf-8")

# Add the fourth option in the builder.
builder = root / "app" / "builder" / "page.tsx"
s = builder.read_text(encoding="utf-8")
if 'value="compact-ats"' not in s:
    m = re.search(r'(<option\s+value="compact"[^>]*>.*?</option>)', s, flags=re.S)
    if m:
        option = m.group(1) + '\n                <option value="compact-ats">Compact ATS</option>'
        s = s[:m.start()] + option + s[m.end():]
    else:
        m = re.search(r'(<select[^>]*>.*?value="modern".*?)(</select>)', s, flags=re.S)
        if not m:
            raise SystemExit("Could not locate builder template selector")
        replacement = m.group(1) + '\n                <option value="compact-ats">Compact ATS</option>\n              ' + m.group(2)
        s = s[:m.start()] + replacement + s[m.end():]
# Preserve Compact ATS when starting a new CV or restoring a local draft.
def expand_template_guard(text):
    pattern = re.compile(
        r"(?P<value>[A-Za-z_$][\\w.$]*)\\s*===\\s*['\\\"]classic['\\\"]"
        r"\\s*\\|\\|\\s*(?P=value)\\s*===\\s*['\\\"]compact['\\\"]"
        r"\\s*\\?\\s*(?P=value)\\s*:\\s*['\\\"]modern['\\\"]"
    )

    def replacement(match):
        value = match.group("value")
        return (
            value + " === 'classic' || " +
            value + " === 'compact' || " +
            value + " === 'compact-ats' ? " +
            value + " : 'modern'"
        )

    return pattern.subn(replacement, text)

s, expanded_guards = expand_template_guard(s)
if expanded_guards < 2:
    print("WARN: expected to expand at least two template guards, expanded", expanded_guards)

builder.write_text(s, encoding="utf-8")

# Dedicated ATS rendering branch.
preview = root / "components" / "CvPreview.tsx"
s = preview.read_text(encoding="utf-8")
if "template === 'compact-ats'" not in s:
    marker = "  if (template === 'modern') {"
    if marker not in s:
        raise SystemExit("Could not locate CvPreview modern template branch")

    branch = r'''  if (template === 'compact-ats') {
    const skillItems = data.skills
      ? data.skills.split('\n').map(item => item.trim()).filter(Boolean)
      : [];
    const languageItems = data.languages
      ? data.languages.split('\n').map(item => item.trim()).filter(Boolean)
      : [];

    return (
      <article className="cv-sheet template-compact-ats" dir={dir}>
        {watermarked && <div className="cv-watermark">SIRATI · PREVIEW</div>}

        <header className="compact-ats-head keep-together">
          <h1>{data.fullName || (language === 'ar' ? 'اسمك الكامل' : 'Your full name')}</h1>
          <div className="compact-ats-title">
            {data.title || (language === 'ar' ? 'المسمى الوظيفي' : 'Professional title')}
          </div>
          <div className="compact-ats-contact">
            {data.phone && <span>{data.phone}</span>}
            {data.email && <span>{data.email}</span>}
            {data.location && <span>{data.location}</span>}
            {data.linkedin && <span>{data.linkedin}</span>}
          </div>
        </header>

        {data.profile && (
          <section className="compact-ats-section keep-together">
            <h2>{language === 'ar' ? 'الملخص المهني' : 'PROFESSIONAL SUMMARY'}</h2>
            <p>{data.profile}</p>
          </section>
        )}

        {visibleExperience.length > 0 && (
          <section className="compact-ats-section">
            <h2>{language === 'ar' ? 'الخبرة المهنية' : 'PROFESSIONAL EXPERIENCE'}</h2>
            {visibleExperience.map(exp => (
              <div key={exp.id} className="compact-ats-entry keep-together">
                <div className="compact-ats-entry-head">
                  <strong>{exp.role}</strong>
                  {exp.period && <span>{exp.period}</span>}
                </div>
                {(exp.company || exp.location) && (
                  <div className="compact-ats-meta">
                    {exp.company && <span>{exp.company}</span>}
                    {exp.company && exp.location && <span> · </span>}
                    {exp.location && <span>{exp.location}</span>}
                  </div>
                )}
                <DetailLines value={exp.details} />
              </div>
            ))}
          </section>
        )}

        {skillItems.length > 0 && (
          <section className="compact-ats-section keep-together">
            <h2>{language === 'ar' ? 'المهارات الأساسية' : 'CORE SKILLS'}</h2>
            <div className="compact-ats-keywords">
              {skillItems.map((item, index) => <span key={index}>{item}</span>)}
            </div>
          </section>
        )}

        {visibleEducation.length > 0 && (
          <section className="compact-ats-section">
            <h2>{language === 'ar' ? 'التعليم' : 'EDUCATION'}</h2>
            {visibleEducation.map(edu => (
              <div key={edu.id} className="compact-ats-entry keep-together">
                <div className="compact-ats-entry-head">
                  <strong>{edu.degree}</strong>
                  {edu.period && <span>{edu.period}</span>}
                </div>
                {(edu.school || edu.location) && (
                  <div className="compact-ats-meta">
                    {edu.school && <span>{edu.school}</span>}
                    {edu.school && edu.location && <span> · </span>}
                    {edu.location && <span>{edu.location}</span>}
                  </div>
                )}
                <DetailLines value={edu.details} />
              </div>
            ))}
          </section>
        )}

        {visibleCertifications.length > 0 && (
          <section className="compact-ats-section keep-together">
            <h2>{language === 'ar' ? 'التراخيص والشهادات' : 'LICENSURE & CERTIFICATIONS'}</h2>
            <ul className="compact-ats-list">
              {visibleCertifications.map(item => (
                <li key={item.id}>
                  <strong>{item.name}</strong>
                  {item.issuer && <span> — {item.issuer}</span>}
                  {item.date && <span> · {item.date}</span>}
                </li>
              ))}
            </ul>
          </section>
        )}

        {visibleCourses.length > 0 && (
          <section className="compact-ats-section keep-together">
            <h2>{language === 'ar' ? 'التدريب الإضافي' : 'ADDITIONAL TRAINING'}</h2>
            <ul className="compact-ats-list">
              {visibleCourses.map(item => (
                <li key={item.id}>
                  <span>{item.name}</span>
                  {item.provider && <span> — {item.provider}</span>}
                  {item.date && <span> · {item.date}</span>}
                </li>
              ))}
            </ul>
          </section>
        )}

        {visibleProjects.length > 0 && (
          <section className="compact-ats-section">
            <h2>{language === 'ar' ? 'المشروعات' : 'PROJECTS'}</h2>
            {visibleProjects.map(item => (
              <div key={item.id} className="compact-ats-entry keep-together">
                <div className="compact-ats-entry-head">
                  <strong>{item.name}</strong>
                  {item.period && <span>{item.period}</span>}
                </div>
                {item.organization && <div className="compact-ats-meta">{item.organization}</div>}
                <DetailLines value={item.details} />
              </div>
            ))}
          </section>
        )}

        {languageItems.length > 0 && (
          <section className="compact-ats-section keep-together">
            <h2>{language === 'ar' ? 'اللغات' : 'LANGUAGES'}</h2>
            <p>{languageItems.join(' · ')}</p>
          </section>
        )}
      </article>
    );
  }

'''
    s = s.replace(marker, branch + marker, 1)
preview.write_text(s, encoding="utf-8")

# ATS-first responsive + print styling.
css_path = root / "app" / "globals.css"
css = css_path.read_text(encoding="utf-8")
marker = "/* Compact ATS — single-column ATS-first template */"
if marker not in css:
    css += r'''

/* Compact ATS — single-column ATS-first template */
.template-compact-ats {
  width:794px;
  min-height:1123px;
  box-sizing:border-box;
  padding:34px 42px 38px;
  background:#fff;
  color:#111827;
  font-family:Arial, Helvetica, sans-serif;
  font-size:12.6px;
  line-height:1.38;
}
.template-compact-ats .compact-ats-head {
  margin:0 0 15px;
  padding:0 0 11px;
  border-bottom:1.5px solid #111827;
}
.template-compact-ats .compact-ats-head h1 {
  margin:0 0 3px;
  font-size:25px;
  line-height:1.08;
  font-weight:800;
  letter-spacing:-.25px;
  color:#111827;
}
.template-compact-ats .compact-ats-title {
  margin:0 0 7px;
  font-size:12.6px;
  line-height:1.25;
  font-weight:700;
  color:#374151;
}
.template-compact-ats .compact-ats-contact {
  display:flex;
  flex-wrap:wrap;
  gap:3px 0;
  font-size:11.7px;
  line-height:1.25;
  color:#374151;
}
.template-compact-ats .compact-ats-contact span:not(:last-child)::after {
  content:" | ";
  padding:0 7px;
  color:#6b7280;
}
.template-compact-ats .compact-ats-section { margin:0 0 12px; padding:0; }
.template-compact-ats .compact-ats-section:last-child { margin-bottom:0; }
.template-compact-ats .compact-ats-section h2 {
  margin:0 0 5px;
  padding:0 0 3px;
  border-bottom:1px solid #9ca3af;
  color:#111827;
  font-size:11.5px;
  line-height:1.2;
  font-weight:800;
  letter-spacing:.35px;
  text-transform:uppercase;
}
.template-compact-ats .compact-ats-section p {
  margin:0;
  color:#111827;
  font-size:12.1px;
  line-height:1.4;
}
.template-compact-ats .compact-ats-entry { margin:0 0 7px; padding:0; }
.template-compact-ats .compact-ats-entry:last-child { margin-bottom:0; }
.template-compact-ats .compact-ats-entry-head {
  display:flex;
  align-items:baseline;
  justify-content:space-between;
  gap:14px;
  margin:0 0 1px;
  font-size:12.2px;
  line-height:1.3;
}
.template-compact-ats .compact-ats-entry-head strong { font-weight:800; }
.template-compact-ats .compact-ats-entry-head > span {
  flex:0 0 auto;
  font-size:11.4px;
  font-weight:700;
  color:#374151;
}
.template-compact-ats .compact-ats-meta {
  margin:0 0 3px;
  font-size:11.7px;
  line-height:1.28;
  color:#374151;
}
.template-compact-ats .cv-bullets {
  margin:3px 0 0;
  padding-inline-start:18px;
}
.template-compact-ats .cv-bullets li {
  margin:0 0 1px;
  padding:0;
  font-size:11.9px;
  line-height:1.36;
}
.template-compact-ats .compact-ats-keywords {
  display:flex;
  flex-wrap:wrap;
  gap:0;
  font-size:11.9px;
  line-height:1.38;
}
.template-compact-ats .compact-ats-keywords span:not(:last-child)::after {
  content:" · ";
  padding:0 4px;
  color:#6b7280;
}
.template-compact-ats .compact-ats-list {
  margin:0;
  padding-inline-start:18px;
}
.template-compact-ats .compact-ats-list li {
  margin:0 0 2px;
  padding:0;
  font-size:11.9px;
  line-height:1.34;
}
[dir="rtl"].template-compact-ats .compact-ats-entry-head { flex-direction:row-reverse; }

@media (max-width: 920px) {
  .template-compact-ats {
    width:100%;
    min-height:auto;
    padding:28px 30px 32px;
  }
}
@media (max-width: 560px) {
  .template-compact-ats { padding:22px 18px 26px; font-size:11.8px; }
  .template-compact-ats .compact-ats-head h1 { font-size:22px; }
  .template-compact-ats .compact-ats-entry-head { display:block; }
  .template-compact-ats .compact-ats-entry-head > span { display:block; margin-top:1px; }
}
@media print {
  .template-compact-ats {
    width:210mm;
    min-height:297mm;
    padding:11mm 13mm 12mm;
    border:0;
    box-shadow:none;
    font-size:9.2pt;
    line-height:1.34;
  }
  .template-compact-ats .compact-ats-head { margin-bottom:3.4mm; padding-bottom:2.5mm; }
  .template-compact-ats .compact-ats-head h1 { font-size:18.5pt; margin-bottom:.8mm; }
  .template-compact-ats .compact-ats-title { font-size:9.2pt; margin-bottom:1.5mm; }
  .template-compact-ats .compact-ats-contact { font-size:8.5pt; }
  .template-compact-ats .compact-ats-section { margin-bottom:3.1mm; }
  .template-compact-ats .compact-ats-section h2 {
    margin-bottom:1.2mm;
    padding-bottom:.8mm;
    font-size:8.6pt;
  }
  .template-compact-ats .compact-ats-section p,
  .template-compact-ats .compact-ats-entry-head,
  .template-compact-ats .cv-bullets li,
  .template-compact-ats .compact-ats-keywords,
  .template-compact-ats .compact-ats-list li { font-size:8.8pt; }
  .template-compact-ats .compact-ats-meta,
  .template-compact-ats .compact-ats-entry-head > span { font-size:8.3pt; }
  .template-compact-ats .compact-ats-entry { margin-bottom:1.9mm; }
  .template-compact-ats .cv-bullets,
  .template-compact-ats .compact-ats-list { padding-inline-start:5mm; }
  .template-compact-ats .keep-together,
  .template-compact-ats .compact-ats-entry { break-inside:avoid; page-break-inside:avoid; }
}
'''
    css_path.write_text(css, encoding="utf-8")

print("Applied Compact ATS template.")
