from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()

preview = root / "components" / "CvPreview.tsx"
text = preview.read_text(encoding="utf-8")

marker = "  return (\\n    <article className={`cv-sheet template-${template} ${template === 'compact' ? 'compact' : ''}`} dir={dir}>"
if "professional-v2" not in text:
    modern = r'''  if (template === 'modern') {
    const skillLine = data.skills
      ? data.skills.split('\n').map(item => item.trim()).filter(Boolean).join(' | ')
      : '';
    const languageLine = data.languages
      ? data.languages.split('\n').map(item => item.trim()).filter(Boolean).join(' | ')
      : '';

    return (
      <article className="cv-sheet template-modern professional-v2" dir={dir}>
        {watermarked && <div className="cv-watermark">SIRATI · PREVIEW</div>}

        <header className="professional-v2-head">
          <div className="professional-v2-copy">
            <h1>{data.fullName || (language === 'ar' ? 'اسمك الكامل' : 'Your full name')}</h1>
            <div className="professional-v2-title">
              {data.title || (language === 'ar' ? 'المسمى الوظيفي' : 'Professional title')}
            </div>
            <div className="professional-v2-contact-line">
              {data.phone && <span>{data.phone}</span>}
              {data.phone && data.email && <span className="sep">|</span>}
              {data.email && <span>{data.email}</span>}
            </div>
            {(data.location || data.linkedin) && (
              <div className="professional-v2-contact-line secondary">
                {data.location && <span>{data.location}</span>}
                {data.location && data.linkedin && <span className="sep">|</span>}
                {data.linkedin && <span>{data.linkedin}</span>}
              </div>
            )}
          </div>
          {data.photoDataUrl && <img className="professional-v2-photo" src={data.photoDataUrl} alt="Professional portrait" />}
        </header>

        {data.profile && (
          <section className="professional-v2-section keep-together">
            <h2>{language === 'ar' ? 'الملخص المهني' : 'PROFESSIONAL SUMMARY'}</h2>
            <p>{data.profile}</p>
          </section>
        )}

        {visibleCertifications.length > 0 && (
          <section className="professional-v2-section keep-together">
            <h2>{language === 'ar' ? 'التراخيص والشهادات' : 'LICENSURE AND CERTIFICATIONS'}</h2>
            <ul className="professional-v2-list professional-v2-cert-list">
              {visibleCertifications.map(item => (
                <li key={item.id}>
                  <span className="professional-v2-cert-name">{item.name}</span>
                  {item.issuer && <span> - {item.issuer}</span>}
                  {item.date && <span> | {item.date}</span>}
                </li>
              ))}
            </ul>
          </section>
        )}

        {visibleExperience.length > 0 && (
          <section className="professional-v2-section">
            <h2>{language === 'ar' ? 'الخبرة المهنية' : 'PROFESSIONAL EXPERIENCE'}</h2>
            {visibleExperience.map(exp => (
              <div key={exp.id} className="professional-v2-entry keep-together">
                <div className="professional-v2-role-line">
                  <strong>{exp.role}</strong>
                  {exp.period && <span> | {exp.period}</span>}
                </div>
                {(exp.company || exp.location) && (
                  <div className="professional-v2-org-line">
                    {exp.company && <span>{exp.company}</span>}
                    {exp.company && exp.location && <span>, </span>}
                    {exp.location && <span>{exp.location}</span>}
                  </div>
                )}
                <DetailLines value={exp.details} />
              </div>
            ))}
          </section>
        )}

        {visibleEducation.length > 0 && (
          <section className="professional-v2-section">
            <h2>{language === 'ar' ? 'التعليم' : 'EDUCATION'}</h2>
            {visibleEducation.map(edu => (
              <div key={edu.id} className="professional-v2-entry keep-together">
                <div className="professional-v2-role-line">
                  <strong>{edu.degree}</strong>
                  {edu.period && <span> | {edu.period}</span>}
                </div>
                {(edu.school || edu.location) && (
                  <div className="professional-v2-org-line">
                    {edu.school && <span>{edu.school}</span>}
                    {edu.school && edu.location && <span> | </span>}
                    {edu.location && <span>{edu.location}</span>}
                  </div>
                )}
                <DetailLines value={edu.details} />
              </div>
            ))}
          </section>
        )}

        {visibleCourses.length > 0 && (
          <section className="professional-v2-section keep-together">
            <h2>{language === 'ar' ? 'التدريب الإضافي' : 'ADDITIONAL TRAINING'}</h2>
            <div className="professional-v2-plain-list">
              {visibleCourses.map(item => (
                <div key={item.id} className="professional-v2-training-line">
                  <strong>{item.name}</strong>
                  {item.provider && <span>{item.name ? ': ' : ''}{item.provider}</span>}
                  {item.date && <span> | {item.date}</span>}
                </div>
              ))}
            </div>
          </section>
        )}

        {visibleProjects.length > 0 && (
          <section className="professional-v2-section">
            <h2>{language === 'ar' ? 'المشروعات' : 'PROJECTS'}</h2>
            {visibleProjects.map(item => (
              <div key={item.id} className="professional-v2-entry keep-together">
                <div className="professional-v2-role-line">
                  <strong>{item.name}</strong>
                  {item.period && <span> | {item.period}</span>}
                </div>
                {item.organization && <div className="professional-v2-org-line">{item.organization}</div>}
                <DetailLines value={item.details} />
              </div>
            ))}
          </section>
        )}

        {skillLine && (
          <section className="professional-v2-section keep-together">
            <h2>{language === 'ar' ? 'المهارات السريرية' : 'CLINICAL SKILLS'}</h2>
            <p>{skillLine}</p>
          </section>
        )}

        {languageLine && (
          <section className="professional-v2-section keep-together">
            <h2>{language === 'ar' ? 'اللغات ومعلومات إضافية' : 'LANGUAGES AND ADDITIONAL INFORMATION'}</h2>
            <p>{languageLine}</p>
          </section>
        )}
      </article>
    );
  }

'''
    if marker not in text:
        raise SystemExit("Could not locate CvPreview return marker")
    text = text.replace(marker, modern + marker, 1)
    preview.write_text(text, encoding="utf-8")

css_path = root / "app" / "globals.css"
css = css_path.read_text(encoding="utf-8")
css_marker = "/* Professional ATS v2 — closer to supplied reference */"
if css_marker not in css:
    css += r'''

/* Professional ATS v2 — closer to supplied reference */
.template-modern.professional-v2 {
  width:794px;
  min-height:1123px;
  box-sizing:border-box;
  padding:18px 20px 22px;
  font-family:Arial, Helvetica, sans-serif;
  color:#111;
  background:#fff;
  font-size:13.2px;
  line-height:1.42;
}
.professional-v2 .professional-v2-head {
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:20px;
  margin:0 0 17px;
  padding:0;
  border:0;
}
.professional-v2-copy { min-width:0; flex:1; padding-top:0; }
.professional-v2 .professional-v2-head h1 {
  margin:0 0 4px;
  font-size:27px;
  line-height:1.08;
  font-weight:500;
  letter-spacing:-.15px;
  color:#111;
}
.professional-v2-title {
  margin:0 0 7px;
  font-size:13px;
  line-height:1.2;
  font-weight:800;
  text-transform:uppercase;
  color:#111;
}
.professional-v2-contact-line {
  display:flex;
  align-items:center;
  flex-wrap:wrap;
  gap:0 7px;
  margin:0 0 5px;
  font-size:12.4px;
  line-height:1.25;
  color:#111;
}
.professional-v2-contact-line.secondary { margin-bottom:0; }
.professional-v2-contact-line .sep { color:#222; }
.professional-v2-photo {
  width:90px;
  height:105px;
  flex:0 0 90px;
  object-fit:cover;
  object-position:center top;
  margin:0;
  background:#f0f0f0;
}
.professional-v2-section {
  margin:0 0 15px;
  padding:0;
  break-inside:auto;
}
.professional-v2-section:last-child { margin-bottom:0; }
.professional-v2-section h2 {
  margin:0 0 7px;
  padding:0;
  color:#111;
  font-size:12.7px;
  line-height:1.15;
  font-weight:800;
  letter-spacing:0;
  text-transform:uppercase;
}
.professional-v2-section p {
  margin:0;
  font-size:12.6px;
  line-height:1.42;
  color:#111;
}
.professional-v2-list {
  margin:0;
  padding-inline-start:25px;
}
.professional-v2-list li {
  margin:0 0 3px;
  padding:0;
  font-size:12.6px;
  line-height:1.38;
}
.professional-v2-cert-name { font-weight:400; }
.professional-v2-entry {
  margin:0 0 8px;
  padding:0;
}
.professional-v2-entry:last-child { margin-bottom:0; }
.professional-v2-role-line {
  margin:0 0 4px;
  font-size:12.8px;
  line-height:1.3;
  color:#111;
}
.professional-v2-role-line strong { font-weight:800; }
.professional-v2-org-line {
  margin:0 0 4px;
  font-size:12.6px;
  line-height:1.3;
  color:#111;
}
.professional-v2 .cv-bullets {
  margin:4px 0 0;
  padding-inline-start:25px;
}
.professional-v2 .cv-bullets li {
  margin:0 0 3px;
  font-size:12.5px;
  line-height:1.36;
}
.professional-v2-training-line {
  margin:0 0 3px;
  font-size:12.6px;
  line-height:1.38;
}
.professional-v2-training-line:last-child { margin-bottom:0; }
.professional-v2-training-line strong { font-weight:400; }

@media (max-width: 920px) {
  .template-modern.professional-v2 {
    width:100%;
    min-height:auto;
    padding:20px 22px 24px;
    font-size:12px;
  }
  .professional-v2 .professional-v2-head h1 { font-size:24px; }
  .professional-v2-photo { width:78px; height:92px; flex-basis:78px; }
}
@media (max-width: 560px) {
  .template-modern.professional-v2 { padding:16px 16px 20px; }
  .professional-v2 .professional-v2-head { gap:14px; margin-bottom:14px; }
  .professional-v2 .professional-v2-head h1 { font-size:21px; }
  .professional-v2-title { font-size:11.5px; }
  .professional-v2-contact-line { font-size:11px; }
  .professional-v2-photo { width:64px; height:76px; flex-basis:64px; }
  .professional-v2-section { margin-bottom:12px; }
  .professional-v2-section h2 { font-size:11.5px; margin-bottom:5px; }
  .professional-v2-section p,
  .professional-v2-list li,
  .professional-v2-role-line,
  .professional-v2-org-line,
  .professional-v2 .cv-bullets li,
  .professional-v2-training-line { font-size:11.2px; }
}

@media print {
  .template-modern.professional-v2 {
    width:210mm;
    min-height:297mm;
    padding:5mm 5.5mm 6mm;
    border:0;
    box-shadow:none;
    font-size:9.7pt;
    line-height:1.38;
  }
  .professional-v2 .professional-v2-head { gap:5mm; margin-bottom:4.5mm; }
  .professional-v2 .professional-v2-head h1 { font-size:20.3pt; margin-bottom:1.1mm; }
  .professional-v2-title { font-size:9.6pt; margin-bottom:1.8mm; }
  .professional-v2-contact-line { font-size:9.2pt; margin-bottom:1.4mm; }
  .professional-v2-photo { width:24mm; height:28mm; flex-basis:24mm; }
  .professional-v2-section { margin-bottom:4mm; }
  .professional-v2-section h2 { font-size:9.4pt; margin-bottom:1.8mm; }
  .professional-v2-section p,
  .professional-v2-list li,
  .professional-v2-role-line,
  .professional-v2-org-line,
  .professional-v2 .cv-bullets li,
  .professional-v2-training-line { font-size:9.35pt; }
  .professional-v2-role-line { margin-bottom:1.1mm; }
  .professional-v2-org-line { margin-bottom:1.1mm; }
  .professional-v2-entry { margin-bottom:2.2mm; }
  .professional-v2 .cv-bullets { margin-top:1mm; padding-inline-start:6mm; }
  .professional-v2-list { padding-inline-start:6mm; }
}
'''
    css_path.write_text(css, encoding="utf-8")

print("Applied Professional ATS v2 layout.")
