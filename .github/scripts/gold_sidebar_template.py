"""Add the first reference-inspired Sirati template: Gold Sidebar.

Reference: user-supplied charcoal/gold diagonal-sidebar CV (image #1).
Original CSS/markup only, no third-party image, copied text or fake fields.
Reuses CvData, existing photo uploader, genuine CvPreview, current storage/PDF.
Run AFTER real_template_previews.py and Profile Sidebar generated styles.
"""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
types = root / "lib/types.ts"
builder = root / "app/builder/page.tsx"
cards = root / "app/templates/page.tsx"
preview = root / "components/CvPreview.tsx"
css_path = root / "app/globals.css"

s = types.read_text(encoding="utf-8")
anchor = "'profile-sidebar'"
if anchor not in s or "photoDataUrl: string;" not in s:
    raise RuntimeError("Gold Sidebar requires the existing typed photo and Profile Sidebar")
if "'gold-sidebar'" in s:
    raise RuntimeError("Gold Sidebar already exists")
s = s.replace(anchor, anchor + " | 'gold-sidebar'", 1)
types.write_text(s, encoding="utf-8")

s = builder.read_text(encoding="utf-8")
anchor = '<option value="profile-sidebar">Profile Sidebar (Photo)</option>'
if anchor not in s:
    raise RuntimeError("Missing Builder Profile Sidebar template selector")
s = s.replace(anchor, anchor + '\n                <option value="gold-sidebar">Gold Sidebar (Photo)</option>', 1)
if "function handlePhotoUpload" not in s:
    raise RuntimeError("Existing compressed user photo upload missing")
# Preserve onboarding URL, saved draft and document restore on every known guard.
guard = re.compile(r"(?P<lhs>[A-Za-z_$][\w.$]*)\s*===\s*'profile-sidebar'")
def add_guard(m):
    return m.group(0) + " || " + m.group("lhs") + " === 'gold-sidebar'"
s, count = guard.subn(add_guard, s)
if count < 1:
    raise RuntimeError("No allowed-template guard in Builder")
builder.write_text(s, encoding="utf-8")

s = cards.read_text(encoding="utf-8")
anchor = re.search(r"(?m)^(?P<indent>\s*)\{ id: 'profile-sidebar',[^\n]+\n", s)
if not anchor:
    raise RuntimeError("Template catalog profile-sidebar anchor missing")
card = (anchor.group("indent") + "{ id: 'gold-sidebar', name: 'Gold Sidebar', description: 'Distinctive charcoal and gold CV with a geometric photo rail, education on the side, and a gold-accented professional timeline.', badge: 'Creative Photo' },\n")
s = s[:anchor.end()] + card + s[anchor.end():]
anchor = "  'profile-sidebar': { en: ['Photo + sidebar', 'Visual two-column'], ar: ['صورة وشريط جانبي', 'تصميم بعمودين'] }"
if anchor not in s:
    raise RuntimeError("Real preview benefit map changed; do not fake the thumbnail")
s = s.replace(anchor, anchor + ",\n  'gold-sidebar': { en: ['Charcoal + gold', 'Diagonal photo rail'], ar: ['فحمي وذهبي', 'شريط وصورة هندسية'] }", 1)
cards.write_text(s, encoding="utf-8")

s = preview.read_text(encoding="utf-8")
anchor = "  if (template === 'modern') {"
if anchor not in s or "template === 'gold-sidebar'" in s:
    raise RuntimeError("Cannot safely insert Gold Sidebar renderer")
gold = r'''  if (template === 'gold-sidebar') {
    const skillItems = data.skills
      .split(/[\n,،;]+/)
      .map(item => item.trim())
      .filter(Boolean);
    const languageItems = data.languages
      .split(/\n+/)
      .map(item => item.trim())
      .filter(Boolean);

    return (
      <article className="cv-sheet template-gold-sidebar" dir={dir}>
        {watermarked && <div className="cv-watermark">SIRATI · PREVIEW</div>}
        <div className="gold-sidebar-layout">
          <aside className="gold-sidebar-rail">
            <div className="gold-sidebar-portrait-wrap">
              {data.photoDataUrl ? (
                <img src={data.photoDataUrl} className="gold-sidebar-portrait" alt={language === 'ar' ? 'الصورة الشخصية' : 'Professional portrait'} />
              ) : (
                <div className="gold-sidebar-portrait-placeholder" role="img" aria-label={language === 'ar' ? 'مكان الصورة الشخصية' : 'Optional profile photo'}>
                  <svg viewBox="0 0 100 110" aria-hidden="true" focusable="false">
                    <circle cx="50" cy="34" r="19" fill="#a6b0b7" />
                    <path d="M9 110c0-27 15-44 41-44s41 17 41 44" fill="#a6b0b7" />
                  </svg>
                </div>
              )}
            </div>
            <div className="gold-sidebar-rail-content">
              {(data.email || data.phone || data.location || data.linkedin) && (
                <section className="gold-sidebar-rail-section keep-together">
                  <h2>{language === 'ar' ? 'بيانات التواصل' : 'CONTACT'}</h2>
                  <div className="gold-sidebar-contact">
                    {data.phone && <div><strong>{language === 'ar' ? 'هاتف' : 'Phone'}</strong><span>{data.phone}</span></div>}
                    {data.email && <div><strong>{language === 'ar' ? 'البريد الإلكتروني' : 'Email'}</strong><span>{data.email}</span></div>}
                    {data.location && <div><strong>{language === 'ar' ? 'الموقع' : 'Location'}</strong><span>{data.location}</span></div>}
                    {data.linkedin && <div><strong>LinkedIn</strong><span>{data.linkedin}</span></div>}
                  </div>
                </section>
              )}
              {visibleEducation.length > 0 && (
                <section className="gold-sidebar-rail-section">
                  <h2>{language === 'ar' ? 'التعليم' : 'EDUCATION'}</h2>
                  {visibleEducation.map(item => (
                    <div key={item.id} className="gold-sidebar-rail-entry keep-together">
                      <strong>{item.degree}</strong>
                      {item.school && <span>{item.school}</span>}
                      {item.period && <span>{item.period}</span>}
                      {item.location && <span>{item.location}</span>}
                      <DetailLines value={item.details} />
                    </div>
                  ))}
                </section>
              )}
              {languageItems.length > 0 && (
                <section className="gold-sidebar-rail-section keep-together">
                  <h2>{language === 'ar' ? 'اللغات' : 'LANGUAGES'}</h2>
                  <ul className="gold-sidebar-languages">
                    {languageItems.map((item, i) => <li key={i}>{item}</li>)}
                  </ul>
                </section>
              )}
            </div>
          </aside>
          <div className="gold-sidebar-main">
            <header className="gold-sidebar-head keep-together">
              <h1>{data.fullName || (language === 'ar' ? 'اسمك الكامل' : 'Your full name')}</h1>
              <p>{data.title || (language === 'ar' ? 'المسمى الوظيفي' : 'Professional title')}</p>
            </header>
            {data.profile && (
              <section className="gold-sidebar-section keep-together">
                <h2>{language === 'ar' ? 'الملخص المهني' : 'PROFESSIONAL SUMMARY'}</h2>
                <p>{data.profile}</p>
              </section>
            )}
            {visibleExperience.length > 0 && (
              <section className="gold-sidebar-section gold-sidebar-timeline">
                <h2>{language === 'ar' ? 'الخبرات المهنية' : 'WORK EXPERIENCE'}</h2>
                {visibleExperience.map(item => (
                  <div key={item.id} className="gold-sidebar-entry keep-together">
                    <div className="gold-sidebar-entry-heading">
                      <strong>{item.role}</strong>
                      {item.period && <span className="gold-sidebar-date">{item.period}</span>}
                    </div>
                    {(item.company || item.location) && <div className="gold-sidebar-company">
                      {item.company}{item.company && item.location ? ' · ' : ''}{item.location}
                    </div>}
                    <DetailLines value={item.details} />
                  </div>
                ))}
              </section>
            )}
            {skillItems.length > 0 && (
              <section className="gold-sidebar-section keep-together">
                <h2>{language === 'ar' ? 'المهارات' : 'SKILLS'}</h2>
                <ul className="gold-sidebar-skill-list">
                  {skillItems.map((skill, i) => <li key={i}>{skill}</li>)}
                </ul>
              </section>
            )}
            {visibleCertifications.length > 0 && (
              <section className="gold-sidebar-section">
                <h2>{language === 'ar' ? 'التراخيص والشهادات' : 'LICENSES & CERTIFICATIONS'}</h2>
                {visibleCertifications.map(item => (
                  <div key={item.id} className="gold-sidebar-entry keep-together">
                    <div className="gold-sidebar-entry-heading">
                      <strong>{item.name}</strong>
                      {item.date && <span className="gold-sidebar-date">{item.date}</span>}
                    </div>
                    {item.issuer && <div className="gold-sidebar-company">{item.issuer}</div>}
                  </div>
                ))}
              </section>
            )}
            {visibleCourses.length > 0 && (
              <section className="gold-sidebar-section">
                <h2>{language === 'ar' ? 'الدورات والتدريب' : 'COURSES & TRAINING'}</h2>
                {visibleCourses.map(item => (
                  <div key={item.id} className="gold-sidebar-entry keep-together">
                    <div className="gold-sidebar-entry-heading">
                      <strong>{item.name}</strong>
                      {item.date && <span className="gold-sidebar-date">{item.date}</span>}
                    </div>
                    {item.provider && <div className="gold-sidebar-company">{item.provider}</div>}
                  </div>
                ))}
              </section>
            )}
            {visibleProjects.length > 0 && (
              <section className="gold-sidebar-section">
                <h2>{language === 'ar' ? 'المشروعات' : 'PROJECTS'}</h2>
                {visibleProjects.map(item => (
                  <div key={item.id} className="gold-sidebar-entry keep-together">
                    <div className="gold-sidebar-entry-heading">
                      <strong>{item.name}</strong>
                      {item.period && <span className="gold-sidebar-date">{item.period}</span>}
                    </div>
                    {item.organization && <div className="gold-sidebar-company">{item.organization}</div>}
                    <DetailLines value={item.details} />
                  </div>
                ))}
              </section>
            )}
          </div>
        </div>
      </article>
    );
  }

'''
s = s.replace(anchor, gold + anchor, 1)
preview.write_text(s, encoding="utf-8")

s = css_path.read_text(encoding="utf-8")
if "/* Gold Sidebar — original charcoal and geometric gold photo rail */" in s:
    raise RuntimeError("Gold Sidebar CSS already present")
s += r'''

/* Gold Sidebar — original charcoal and geometric gold photo rail */
.cv-sheet.template-gold-sidebar {
  display: block;
  box-sizing: border-box;
  overflow: hidden;
  padding: 0;
  color: #292b2e;
  background: #fff;
  font-family: Arial, Helvetica, sans-serif;
  font-size: 12px;
  line-height: 1.5;
}
.template-gold-sidebar .gold-sidebar-layout {
  display: grid;
  grid-template-columns: 35% minmax(0,1fr);
  min-height: 1122px;
  align-items: stretch;
}
.template-gold-sidebar .gold-sidebar-rail {
  min-width: 0;
  box-sizing: border-box;
  background: #303136;
  color: #f8f8f8;
  position: relative;
  padding: 0 25px 40px 31px;
  print-color-adjust: exact;
  -webkit-print-color-adjust: exact;
}
.template-gold-sidebar .gold-sidebar-rail::before {
  content:"";
  position: absolute;
  z-index: 0;
  inset: 0 0 auto;
  height: 239px;
  background: #f7b914;
  clip-path: polygon(0 0, 100% 0, 0 100%);
  pointer-events:none;
}
[dir="rtl"].template-gold-sidebar .gold-sidebar-rail::before {
  clip-path:polygon(0 0,100% 0,100% 100%);
}
.template-gold-sidebar .gold-sidebar-portrait-wrap {
  display:grid;
  place-items:center;
  position:relative;
  z-index:1;
  width: 174px;
  height: 194px;
  max-width:100%;
  margin: 50px auto 25px;
}
.template-gold-sidebar .gold-sidebar-portrait,
.template-gold-sidebar .gold-sidebar-portrait-placeholder {
  width: 168px;
  height: 180px;
  max-width:100%;
  box-sizing:border-box;
  display:block;
  position:relative;
  overflow:hidden;
  background:#edf0f2;
  border: 5px solid #fff;
  border-radius: 84px 84px 57px 57px;
  box-shadow: 0 5px 15px rgba(0,0,0,.24);
}
.template-gold-sidebar .gold-sidebar-portrait {
  object-fit:cover;
  object-position:50% 28%;
}
.template-gold-sidebar .gold-sidebar-portrait-placeholder {
  display:grid;
  place-items:center;
  background:#e3e6e7;
}
.template-gold-sidebar .gold-sidebar-portrait-placeholder svg {
  width:90px;
  height:105px;
  max-width:100%;
}
.template-gold-sidebar .gold-sidebar-rail-content {
  position:relative;
  z-index:1;
  padding-inline-start: 9px;
  border-inline-start: 2px solid rgba(247,185,20,.38);
}
.template-gold-sidebar .gold-sidebar-rail-section {
  position:relative;
  margin:0 0 30px;
  padding:0 0 0 0;
}
.template-gold-sidebar .gold-sidebar-rail-section::before {
  content:"";
  position:absolute;
  top:4px;
  inset-inline-start:-15px;
  width:10px;
  height:22px;
  border-radius:9px;
  background:#f7b914;
}
.template-gold-sidebar .gold-sidebar-rail-section h2 {
  color:white;
  font-size:12px;
  font-weight:800;
  letter-spacing:.4px;
  margin:0 0 15px;
  padding: 0 0 9px;
  border-bottom: 1px dashed rgba(255,255,255,.33);
}
.template-gold-sidebar .gold-sidebar-contact {
  display:grid;
  gap:10px;
}
.template-gold-sidebar .gold-sidebar-contact > div {
  display:grid;
  gap:1px;
  overflow-wrap:anywhere;
}
.template-gold-sidebar .gold-sidebar-contact strong {
  color:#f9cb58;
  font-size:10px;
  font-weight:700;
}
.template-gold-sidebar .gold-sidebar-contact span,
.template-gold-sidebar .gold-sidebar-rail-entry span {
  display:block;
  color:#f0f0f0;
  font-size:11px;
  overflow-wrap:anywhere;
}
.template-gold-sidebar .gold-sidebar-rail-entry {margin-bottom:16px}
.template-gold-sidebar .gold-sidebar-rail-entry strong {
  font-size:11px;
  font-weight:800;
  display:block;
  margin-bottom:4px;
  overflow-wrap:anywhere;
}
.template-gold-sidebar .gold-sidebar-rail-entry p,
.template-gold-sidebar .gold-sidebar-rail-entry li {font-size:11px}
.template-gold-sidebar .gold-sidebar-languages {
  padding:0;
  margin:0;
  list-style:none;
  display:grid;
  gap:6px;
}
.template-gold-sidebar .gold-sidebar-languages li {
  overflow-wrap:anywhere;
  font-size:11px;
}
.template-gold-sidebar .gold-sidebar-languages li::before {
  content:"•";
  color:#f7b914;
  margin-inline-end:7px;
}
.template-gold-sidebar .gold-sidebar-main {
  box-sizing:border-box;
  min-width:0;
  padding:66px 42px 43px 40px;
}
.template-gold-sidebar .gold-sidebar-head {
  background:#f5f5f5;
  border-inline-start: 6px solid #f7b914;
  margin:0 -42px 38px -40px;
  padding:30px 39px 25px;
}
.template-gold-sidebar .gold-sidebar-head h1 {
  color:#28292c;
  font-size:29px;
  font-weight:850;
  line-height:1.18;
  letter-spacing:.25px;
  margin:0 0 7px;
  overflow-wrap:anywhere;
}
.template-gold-sidebar .gold-sidebar-head p {
  color:#515257;
  font-size:12px;
  margin:0;
  font-weight:600;
  letter-spacing:.6px;
}
.template-gold-sidebar .gold-sidebar-section {
  margin:0 0 24px;
}
.template-gold-sidebar .gold-sidebar-section h2 {
  color:#28292c;
  font-size:12.5px;
  letter-spacing:.3px;
  font-weight:800;
  margin:0 0 12px;
  padding:0 0 9px;
  border-bottom:1px solid #d9dadd;
  position:relative;
}
.template-gold-sidebar .gold-sidebar-section h2::before {
  content:"";
  position:absolute;
  background:#f7b914;
  height:18px;
  width:5px;
  border-radius:6px;
  inset-inline-start:-19px;
  top:0;
}
.template-gold-sidebar .gold-sidebar-section > p {
  margin:0;
  color:#4b4e52;
  line-height:1.58;
}
.template-gold-sidebar .gold-sidebar-entry {
  margin:0 0 16px;
  position:relative;
  overflow-wrap:anywhere;
}
.template-gold-sidebar .gold-sidebar-entry-heading {
  display:flex;
  justify-content:space-between;
  align-items:baseline;
  flex-wrap:wrap;
  gap:6px 10px;
}
.template-gold-sidebar .gold-sidebar-entry-heading strong {font-size:12px;color:#25272a}
.template-gold-sidebar .gold-sidebar-date {
  font-size:10px;
  white-space:nowrap;
  color:#66686c;
}
.template-gold-sidebar .gold-sidebar-company {
  font-size:10.5px;
  font-weight:600;
  color:#76787b;
  margin:3px 0 6px;
}
.template-gold-sidebar .gold-sidebar-entry p {margin:4px 0}
.template-gold-sidebar .gold-sidebar-entry .cv-bullets {
  margin:7px 0 0;
  padding-inline-start:17px;
}
.template-gold-sidebar .gold-sidebar-entry .cv-bullets li {margin-bottom:3px}
.template-gold-sidebar .gold-sidebar-timeline .gold-sidebar-entry {
  padding-inline-start:14px;
  border-inline-start:1px solid #dedede;
  margin-inline-start:3px;
}
.template-gold-sidebar .gold-sidebar-timeline .gold-sidebar-entry::before {
  content:"";
  width:8px;
  height:8px;
  border-radius:50%;
  background:#f7b914;
  position:absolute;
  top:3px;
  inset-inline-start:-5px;
}
.template-gold-sidebar .gold-sidebar-skill-list {
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:6px 12px;
  padding:0;
  margin:0;
  list-style:none;
}
.template-gold-sidebar .gold-sidebar-skill-list li {
  position:relative;
  padding-inline-start:12px;
  overflow-wrap:anywhere;
  font-size:11px;
}
.template-gold-sidebar .gold-sidebar-skill-list li::before {
  content:"";
  width:5px;
  height:5px;
  border-radius:50%;
  background:#f7b914;
  position:absolute;
  inset-inline-start:0;
  top:7px;
}
[dir="rtl"].template-gold-sidebar .gold-sidebar-main {
  padding:66px 40px 43px 42px;
}
[dir="rtl"].template-gold-sidebar .gold-sidebar-head {
  margin:0 -40px 38px -42px;
}
[dir="rtl"].template-gold-sidebar .gold-sidebar-rail-section h2,
[dir="rtl"].template-gold-sidebar .gold-sidebar-head h1,
[dir="rtl"].template-gold-sidebar .gold-sidebar-section h2 {letter-spacing:0}
@media (max-width:920px) {
  .template-gold-sidebar .gold-sidebar-layout {min-height:0}
  .template-gold-sidebar .gold-sidebar-rail {padding:0 15px 25px 18px}
  .template-gold-sidebar .gold-sidebar-rail::before {height:180px}
  .template-gold-sidebar .gold-sidebar-portrait-wrap {
    width:130px;height:145px;margin:28px auto 24px
  }
  .template-gold-sidebar .gold-sidebar-portrait,
  .template-gold-sidebar .gold-sidebar-portrait-placeholder {
    width:125px;height:136px;border-width:4px
  }
  .template-gold-sidebar .gold-sidebar-main,
  [dir="rtl"].template-gold-sidebar .gold-sidebar-main {padding:35px 26px}
  .template-gold-sidebar .gold-sidebar-head,
  [dir="rtl"].template-gold-sidebar .gold-sidebar-head {margin:0 -26px 25px;padding:19px 23px}
}
@media (max-width:560px) {
  .template-gold-sidebar .gold-sidebar-layout {
    grid-template-columns:37% minmax(0,1fr);
  }
  .template-gold-sidebar .gold-sidebar-rail {padding:0 8px 19px 12px}
  .template-gold-sidebar .gold-sidebar-rail::before {height:120px}
  .template-gold-sidebar .gold-sidebar-portrait-wrap {
    width:84px;height:98px;margin:15px auto 16px;
  }
  .template-gold-sidebar .gold-sidebar-portrait,
  .template-gold-sidebar .gold-sidebar-portrait-placeholder {
    width:80px;height:92px;border-width:3px;
  }
  .template-gold-sidebar .gold-sidebar-rail-content {padding-inline-start:6px}
  .template-gold-sidebar .gold-sidebar-rail-section::before {
    width:6px;height:14px;inset-inline-start:-11px;
  }
  .template-gold-sidebar .gold-sidebar-rail-section h2,
  .template-gold-sidebar .gold-sidebar-section h2 {font-size:9px}
  .template-gold-sidebar .gold-sidebar-contact span,
  .template-gold-sidebar .gold-sidebar-rail-entry strong,
  .template-gold-sidebar .gold-sidebar-rail-entry span,
  .template-gold-sidebar .gold-sidebar-languages li {font-size:9px}
  .template-gold-sidebar .gold-sidebar-main,
  [dir="rtl"].template-gold-sidebar .gold-sidebar-main {padding:22px 13px}
  .template-gold-sidebar .gold-sidebar-head,
  [dir="rtl"].template-gold-sidebar .gold-sidebar-head {margin:0 -13px 18px;padding:13px}
  .template-gold-sidebar .gold-sidebar-head h1 {font-size:18px}
  .template-gold-sidebar .gold-sidebar-head p {font-size:9.5px}
  .template-gold-sidebar .gold-sidebar-skill-list {grid-template-columns:1fr}
}
@media print {
  .cv-sheet.template-gold-sidebar {
    width:210mm !important;
    min-height:297mm;
    overflow:visible;
    padding:0 !important;
    margin:0;
    box-shadow:none;
    border:0;
  }
  .template-gold-sidebar .gold-sidebar-layout {
    grid-template-columns:35% minmax(0,1fr);
    min-height:297mm;
  }
  .template-gold-sidebar .gold-sidebar-rail {
    padding:0 6.5mm 10mm;
    background:#303136 !important;
  }
  .template-gold-sidebar .gold-sidebar-rail::before {height:64mm}
  .template-gold-sidebar .gold-sidebar-portrait-wrap {
    width:46mm;height:52mm;margin:13mm auto 6mm
  }
  .template-gold-sidebar .gold-sidebar-portrait,
  .template-gold-sidebar .gold-sidebar-portrait-placeholder {
    width:44mm;height:47mm;border:1.3mm solid #fff;
  }
  .template-gold-sidebar .gold-sidebar-main,
  [dir="rtl"].template-gold-sidebar .gold-sidebar-main {padding:18mm 11mm 10mm}
  .template-gold-sidebar .gold-sidebar-head,
  [dir="rtl"].template-gold-sidebar .gold-sidebar-head {
    margin:0 -11mm 10mm;
    padding:8mm 10mm 7mm;
  }
  .template-gold-sidebar .gold-sidebar-head h1 {font-size:21pt}
}
/* Keep an A4-faithful *render* inside each small template-picker card on mobile. */
@media (max-width:920px) {
  .flow-shell .template-carousel-track .template-real-preview__stage > .cv-sheet.template-gold-sidebar .gold-sidebar-layout {
    grid-template-columns:35% minmax(0,1fr);
    min-height:1122px;
  }
  .flow-shell .template-carousel-track .template-real-preview__stage > .cv-sheet.template-gold-sidebar .gold-sidebar-rail {
    padding:0 25px 40px 31px;
  }
  .flow-shell .template-carousel-track .template-real-preview__stage > .cv-sheet.template-gold-sidebar .gold-sidebar-rail::before {height:239px}
  .flow-shell .template-carousel-track .template-real-preview__stage > .cv-sheet.template-gold-sidebar .gold-sidebar-portrait-wrap {
    width:174px;height:194px;margin:50px auto 25px;
  }
  .flow-shell .template-carousel-track .template-real-preview__stage > .cv-sheet.template-gold-sidebar .gold-sidebar-portrait,
  .flow-shell .template-carousel-track .template-real-preview__stage > .cv-sheet.template-gold-sidebar .gold-sidebar-portrait-placeholder {
    width:168px;height:180px;border-width:5px;
  }
  .flow-shell .template-carousel-track .template-real-preview__stage > .cv-sheet.template-gold-sidebar .gold-sidebar-main {
    padding:66px 42px 43px 40px;
  }
  .flow-shell .template-carousel-track .template-real-preview__stage > .cv-sheet.template-gold-sidebar .gold-sidebar-head {
    margin:0 -42px 38px -40px;
    padding:30px 39px 25px;
  }
}
.flow-shell .template-carousel-track .template-real-preview__stage > .cv-sheet.template-gold-sidebar {
  padding:0 !important;
}
'''
css_path.write_text(s, encoding="utf-8")
print("Added Gold Sidebar with existing photo, authentic thumbnail, English/Arabic and print CSS.")
