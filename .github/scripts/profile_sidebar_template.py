"""Add a genuine two-column photo sidebar CV using existing, user-controlled fields.

No schema migration, storage change, network image, payment, or authentication edit.
Runs after existing six templates and demo-thumbnail generator. The same CvPreview
renders Builder, miniature and print/PDF, so there is no deceptive thumbnail.
"""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
types = root / "lib/types.ts"
builder = root / "app/builder/page.tsx"
cards = root / "app/templates/page.tsx"
preview = root / "components/CvPreview.tsx"
styles = root / "app/globals.css"

# Keep the user's established photoDataUrl (compressed by existing photo upload).
src = types.read_text(encoding="utf-8")
if "photoDataUrl: string;" not in src:
    raise RuntimeError("Existing photo upload/data field missing: do not change storage")
if "'profile-sidebar'" in src:
    raise RuntimeError("Profile Sidebar already exists")
old = "'executive-ats'"
if old not in src:
    raise RuntimeError("Missing final template in TemplateName discriminated union")
src = src.replace(old, old + " | 'profile-sidebar'", 1)
types.write_text(src, encoding="utf-8")

src = builder.read_text(encoding="utf-8")
if "function handlePhotoUpload" not in src or 'photo-upload-row' not in src:
    raise RuntimeError("Existing user photo workflow missing")
anchor = '<option value="executive-ats">Executive ATS</option>'
if anchor not in src:
    raise RuntimeError("Missing template switcher option")
src = src.replace(anchor, anchor + '\n                <option value="profile-sidebar">Profile Sidebar (Photo)</option>', 1)

# Existing onboarding, URL, restore and clone template validators share these
# comparisons. Append the new id on the same value without changing user data.
guard = re.compile(r"(?P<lhs>[A-Za-z_$][\w.$]*)\s*===\s*'executive-ats'")
def add_guard(match):
    lhs = match.group("lhs")
    return match.group(0) + " || " + lhs + " === 'profile-sidebar'"
src, count = guard.subn(add_guard, src)
if count < 1:
    raise RuntimeError("Template onboarding/restore guard not found")
builder.write_text(src, encoding="utf-8")

src = cards.read_text(encoding="utf-8")
anchor = re.search(r"(?m)^(?P<indent>\s*)\{ id: 'executive-ats',[^\n]+\n", src)
if not anchor:
    raise RuntimeError("Cannot find final template option")
indent = anchor.group("indent")
new_card = (indent +
    "{ id: 'profile-sidebar', name: 'Profile Sidebar', description: 'Two-column visual CV with an optional portrait, contact and skills in the side rail, and experience on the main page.', badge: 'Photo + Sidebar' },\n")
src = src[:anchor.end()] + new_card + src[anchor.end():]

benefit_anchor = "  'executive-ats': { en: ['Centered header', 'Navy accent'], ar: ['عنوان في المنتصف', 'لمسة كحلي'] }"
if benefit_anchor not in src:
    raise RuntimeError("Real mini CV benefits object changed")
src = src.replace(benefit_anchor, benefit_anchor +
    ",\n  'profile-sidebar': { en: ['Photo + sidebar', 'Visual two-column'], ar: ['صورة وشريط جانبي', 'تصميم بعمودين'] }", 1)
cards.write_text(src, encoding="utf-8")

src = preview.read_text(encoding="utf-8")
marker = "  if (template === 'modern') {"
if marker not in src:
    raise RuntimeError("No production CvPreview insertion point")
if "template === 'profile-sidebar'" in src:
    raise RuntimeError("Sidebar branch already installed")

branch = r'''  if (template === 'profile-sidebar') {
    const sidebarSkills = data.skills
      .split(/[\n,،;]+/)
      .map(item => item.trim())
      .filter(Boolean);
    const sidebarLanguages = data.languages
      .split(/\n+/)
      .map(item => item.trim())
      .filter(Boolean);

    return (
      <article className="cv-sheet template-profile-sidebar" dir={dir}>
        {watermarked && <div className="cv-watermark">SIRATI · PREVIEW</div>}
        <div className="profile-sidebar-layout">
          <aside className="profile-sidebar-rail">
            <div className="profile-sidebar-portrait-wrap">
              {data.photoDataUrl ? (
                <img className="profile-sidebar-portrait" src={data.photoDataUrl} alt={language === 'ar' ? 'الصورة الشخصية' : 'Professional portrait'} />
              ) : (
                <div className="profile-sidebar-portrait-placeholder" aria-label={language === 'ar' ? 'مكان الصورة الشخصية' : 'Photo placeholder'}>
                  <svg viewBox="0 0 100 120" width="100" height="120" aria-hidden="true" focusable="false">
                    <circle cx="50" cy="39" r="21" fill="#9ab2c5" />
                    <path d="M10 116c0-26 14-43 40-43s40 17 40 43" fill="#9ab2c5" />
                  </svg>
                </div>
              )}
            </div>
            {(data.email || data.phone || data.location || data.linkedin) && (
              <section className="profile-sidebar-block keep-together">
                <h2>{language === 'ar' ? 'معلومات التواصل' : 'CONTACT'}</h2>
                <div className="profile-sidebar-contact">
                  {data.phone && <div><strong>{language === 'ar' ? 'الهاتف' : 'Phone'}</strong><span>{data.phone}</span></div>}
                  {data.email && <div><strong>{language === 'ar' ? 'البريد الإلكتروني' : 'Email'}</strong><span>{data.email}</span></div>}
                  {data.location && <div><strong>{language === 'ar' ? 'الموقع' : 'Location'}</strong><span>{data.location}</span></div>}
                  {data.linkedin && <div><strong>LinkedIn</strong><span>{data.linkedin}</span></div>}
                </div>
              </section>
            )}
            {sidebarSkills.length > 0 && (
              <section className="profile-sidebar-block keep-together">
                <h2>{language === 'ar' ? 'المهارات' : 'SKILLS'}</h2>
                <ul className="profile-sidebar-skills">
                  {sidebarSkills.map((skill, index) => <li key={index}>{skill}</li>)}
                </ul>
              </section>
            )}
            {sidebarLanguages.length > 0 && (
              <section className="profile-sidebar-block keep-together">
                <h2>{language === 'ar' ? 'اللغات' : 'LANGUAGES'}</h2>
                <ul className="profile-sidebar-languages">
                  {sidebarLanguages.map((item, index) => <li key={index}>{item}</li>)}
                </ul>
              </section>
            )}
          </aside>
          <div className="profile-sidebar-main">
            <header className="profile-sidebar-head keep-together">
              <h1>{data.fullName || (language === 'ar' ? 'اسمك الكامل' : 'Your full name')}</h1>
              <p>{data.title || (language === 'ar' ? 'المسمى الوظيفي' : 'Professional title')}</p>
            </header>
            {data.profile && (
              <section className="profile-sidebar-section keep-together">
                <h2>{language === 'ar' ? 'الملخص المهني' : 'PROFESSIONAL SUMMARY'}</h2>
                <p>{data.profile}</p>
              </section>
            )}
            {visibleExperience.length > 0 && (
              <section className="profile-sidebar-section">
                <h2>{language === 'ar' ? 'الخبرة المهنية' : 'PROFESSIONAL EXPERIENCE'}</h2>
                {visibleExperience.map(exp => (
                  <div className="profile-sidebar-entry keep-together" key={exp.id}>
                    <div className="profile-sidebar-entry-heading">
                      <strong>{exp.role}</strong>
                      {exp.period && <span className="profile-sidebar-period">{exp.period}</span>}
                    </div>
                    {(exp.company || exp.location) && <p className="profile-sidebar-organization">
                      {exp.company}{exp.company && exp.location ? ' · ' : ''}{exp.location}
                    </p>}
                    <DetailLines value={exp.details} />
                  </div>
                ))}
              </section>
            )}
            {visibleEducation.length > 0 && (
              <section className="profile-sidebar-section">
                <h2>{language === 'ar' ? 'التعليم' : 'EDUCATION'}</h2>
                {visibleEducation.map(edu => (
                  <div className="profile-sidebar-entry keep-together" key={edu.id}>
                    <div className="profile-sidebar-entry-heading">
                      <strong>{edu.degree}</strong>
                      {edu.period && <span className="profile-sidebar-period">{edu.period}</span>}
                    </div>
                    {(edu.school || edu.location) && <p className="profile-sidebar-organization">
                      {edu.school}{edu.school && edu.location ? ' · ' : ''}{edu.location}
                    </p>}
                    <DetailLines value={edu.details} />
                  </div>
                ))}
              </section>
            )}
            {visibleCertifications.length > 0 && (
              <section className="profile-sidebar-section">
                <h2>{language === 'ar' ? 'التراخيص والشهادات' : 'LICENSES & CERTIFICATIONS'}</h2>
                {visibleCertifications.map(item => (
                  <div className="profile-sidebar-entry keep-together" key={item.id}>
                    <div className="profile-sidebar-entry-heading">
                      <strong>{item.name}</strong>
                      {item.date && <span className="profile-sidebar-period">{item.date}</span>}
                    </div>
                    {item.issuer && <p className="profile-sidebar-organization">{item.issuer}</p>}
                  </div>
                ))}
              </section>
            )}
            {visibleCourses.length > 0 && (
              <section className="profile-sidebar-section">
                <h2>{language === 'ar' ? 'الدورات والتدريب' : 'COURSES & TRAINING'}</h2>
                {visibleCourses.map(item => (
                  <div className="profile-sidebar-entry keep-together" key={item.id}>
                    <div className="profile-sidebar-entry-heading">
                      <strong>{item.name}</strong>
                      {item.date && <span className="profile-sidebar-period">{item.date}</span>}
                    </div>
                    {item.provider && <p className="profile-sidebar-organization">{item.provider}</p>}
                  </div>
                ))}
              </section>
            )}
            {visibleProjects.length > 0 && (
              <section className="profile-sidebar-section">
                <h2>{language === 'ar' ? 'المشروعات' : 'PROJECTS'}</h2>
                {visibleProjects.map(item => (
                  <div className="profile-sidebar-entry keep-together" key={item.id}>
                    <div className="profile-sidebar-entry-heading">
                      <strong>{item.name}</strong>
                      {item.period && <span className="profile-sidebar-period">{item.period}</span>}
                    </div>
                    {item.organization && <p className="profile-sidebar-organization">{item.organization}</p>}
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
src = src.replace(marker, branch + marker, 1)
preview.write_text(src, encoding="utf-8")

src = styles.read_text(encoding="utf-8")
if "/* Profile Sidebar true two-column template */" in src:
    raise RuntimeError("Sidebar CSS already installed")
src += r'''

/* Profile Sidebar true two-column template */
.cv-sheet.template-profile-sidebar {
  box-sizing: border-box;
  display: block;
  overflow: hidden;
  padding: 0;
  color: #223247;
  background: #fff;
  font-family: Arial, Helvetica, sans-serif;
  font-size: 12px;
  line-height: 1.48;
}
.template-profile-sidebar .profile-sidebar-layout {
  display: grid;
  grid-template-columns: 32% minmax(0, 1fr);
  align-items: stretch;
  min-height: 1122px;
}
.template-profile-sidebar .profile-sidebar-rail {
  min-width: 0;
  box-sizing: border-box;
  padding: 38px 21px 35px;
  color: #eef6ff;
  background: #17324c;
  print-color-adjust: exact;
  -webkit-print-color-adjust: exact;
}
.template-profile-sidebar .profile-sidebar-portrait-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 0 0 31px;
}
.template-profile-sidebar .profile-sidebar-portrait,
.template-profile-sidebar .profile-sidebar-portrait-placeholder {
  width: 130px;
  height: 143px;
  max-width: 100%;
  box-sizing: border-box;
  border: 5px solid rgba(255,255,255,.75);
  border-radius: 7px;
  box-shadow: 0 6px 16px rgba(0,0,0,.12);
}
.template-profile-sidebar .profile-sidebar-portrait { object-fit: cover; }
.template-profile-sidebar .profile-sidebar-portrait-placeholder {
  display: grid;
  place-items: center;
  overflow: hidden;
  background: #d6e1eb;
}
.template-profile-sidebar .profile-sidebar-portrait-placeholder svg {
  display: block;
  max-width: 100%;
  max-height: 100%;
}
.template-profile-sidebar .profile-sidebar-block { margin: 0 0 27px; }
.template-profile-sidebar .profile-sidebar-block h2 {
  margin: 0 0 13px;
  padding: 0 0 7px;
  border-bottom: 1px solid rgba(255,255,255,.32);
  color: #fff;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 1.35px;
}
.template-profile-sidebar .profile-sidebar-contact {
  display: grid;
  gap: 12px;
}
.template-profile-sidebar .profile-sidebar-contact > div {
  display: grid;
  gap: 1px;
  min-width: 0;
}
.template-profile-sidebar .profile-sidebar-contact strong {
  font-size: 10px;
  letter-spacing: .3px;
  color: #acc5d8;
}
.template-profile-sidebar .profile-sidebar-contact span {
  overflow-wrap: anywhere;
  word-break: break-word;
  font-size: 10.7px;
}
.template-profile-sidebar .profile-sidebar-skills,
.template-profile-sidebar .profile-sidebar-languages {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 9px;
}
.template-profile-sidebar .profile-sidebar-skills li {
  padding: 0 0 8px;
  border-bottom: 1px solid rgba(255,255,255,.16);
  font-size: 11px;
  line-height: 1.36;
  overflow-wrap: anywhere;
}
.template-profile-sidebar .profile-sidebar-languages li {
  font-size: 11px;
  line-height: 1.42;
  overflow-wrap: anywhere;
}
.template-profile-sidebar .profile-sidebar-main {
  min-width: 0;
  box-sizing: border-box;
  padding: 47px 40px 45px 36px;
}
.template-profile-sidebar .profile-sidebar-head {
  margin-bottom: 30px;
  padding: 0 0 20px;
  border-bottom: 3px solid #36a4a1;
}
.template-profile-sidebar .profile-sidebar-head h1 {
  margin: 0 0 7px;
  font-size: 29px;
  font-weight: 800;
  letter-spacing: .2px;
  line-height: 1.18;
  overflow-wrap: anywhere;
  color: #17324c;
}
.template-profile-sidebar .profile-sidebar-head p {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  letter-spacing: .4px;
  color: #25878b;
}
.template-profile-sidebar .profile-sidebar-section { margin: 0 0 22px; }
.template-profile-sidebar .profile-sidebar-section h2 {
  margin: 0 0 10px;
  padding: 0 0 7px;
  border-bottom: 1px solid #d7e2e7;
  color: #176e77;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 1.0px;
}
.template-profile-sidebar .profile-sidebar-section > p {
  margin: 0;
  color: #334155;
  line-height: 1.56;
}
.template-profile-sidebar .profile-sidebar-entry { margin: 0 0 12px; }
.template-profile-sidebar .profile-sidebar-entry:last-child { margin-bottom: 0; }
.template-profile-sidebar .profile-sidebar-entry-heading {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 5px 12px;
}
.template-profile-sidebar .profile-sidebar-entry-heading strong {
  font-size: 12.4px;
  font-weight: 750;
  color: #17324c;
}
.template-profile-sidebar .profile-sidebar-period {
  color: #64748b;
  font-size: 10px;
  white-space: nowrap;
}
.template-profile-sidebar .profile-sidebar-organization {
  margin: 3px 0 5px;
  font-weight: 600;
  font-size: 10.7px;
  color: #64748b;
}
.template-profile-sidebar .profile-sidebar-entry p { margin: 4px 0; }
.template-profile-sidebar .profile-sidebar-entry .cv-bullets {
  margin: 6px 0;
  padding-inline-start: 17px;
}
.template-profile-sidebar .profile-sidebar-entry .cv-bullets li {
  margin-bottom: 4px;
  overflow-wrap: anywhere;
}
[dir="rtl"].template-profile-sidebar .profile-sidebar-main {
  padding: 47px 36px 45px 40px;
}
[dir="rtl"].template-profile-sidebar .profile-sidebar-block h2,
[dir="rtl"].template-profile-sidebar .profile-sidebar-section h2 {
  letter-spacing: 0;
}
@media (max-width: 920px) {
  .cv-sheet.template-profile-sidebar { width: 100%; }
  .template-profile-sidebar .profile-sidebar-layout { min-height: 0; }
  .template-profile-sidebar .profile-sidebar-rail { padding: 26px 16px; }
  .template-profile-sidebar .profile-sidebar-main { padding: 31px 23px; }
  [dir="rtl"].template-profile-sidebar .profile-sidebar-main { padding: 31px 23px; }
}
@media (max-width: 560px) {
  .template-profile-sidebar .profile-sidebar-layout { grid-template-columns: 35% minmax(0,1fr); }
  .template-profile-sidebar .profile-sidebar-rail { padding: 18px 9px; }
  .template-profile-sidebar .profile-sidebar-main,
  [dir="rtl"].template-profile-sidebar .profile-sidebar-main { padding: 22px 12px; }
  .template-profile-sidebar .profile-sidebar-portrait,
  .template-profile-sidebar .profile-sidebar-portrait-placeholder {
    width: 75px; height: 85px; border-width: 3px;
  }
  .template-profile-sidebar .profile-sidebar-head { margin-bottom: 16px; padding-bottom: 12px; }
  .template-profile-sidebar .profile-sidebar-head h1 { font-size: 18px; }
  .template-profile-sidebar .profile-sidebar-head p { font-size: 10px; }
  .template-profile-sidebar .profile-sidebar-block h2,
  .template-profile-sidebar .profile-sidebar-section h2 { font-size: 9px; }
  .template-profile-sidebar .profile-sidebar-block { margin-bottom: 18px; }
  .template-profile-sidebar .profile-sidebar-skills li,
  .template-profile-sidebar .profile-sidebar-languages li,
  .template-profile-sidebar .profile-sidebar-contact span { font-size: 9px; }
  .template-profile-sidebar .profile-sidebar-section { margin-bottom: 15px; }
  .template-profile-sidebar .profile-sidebar-section > p { font-size: 10px; }
  .template-profile-sidebar .profile-sidebar-entry-heading strong { font-size: 10px; }
}
@media print {
  .cv-sheet.template-profile-sidebar {
    width: 210mm !important;
    min-height: 297mm;
    padding: 0 !important;
    margin: 0;
    border: 0;
    box-shadow: none;
    overflow: visible;
  }
  .template-profile-sidebar .profile-sidebar-layout { min-height: 297mm; grid-template-columns: 32% minmax(0,1fr); }
  .template-profile-sidebar .profile-sidebar-rail { padding: 12mm 6mm 12mm; }
  .template-profile-sidebar .profile-sidebar-main,
  [dir="rtl"].template-profile-sidebar .profile-sidebar-main { padding: 15mm 10mm 12mm; }
  .template-profile-sidebar .profile-sidebar-head h1 { font-size: 21pt; }
  .template-profile-sidebar .profile-sidebar-portrait,
  .template-profile-sidebar .profile-sidebar-portrait-placeholder {
    width: 36mm; height: 39mm;
  }
}
/* The existing thumbnail is the real CV, scaled, and keeps its left rail. */
.flow-shell .template-carousel-track .template-real-preview__stage > .cv-sheet.template-profile-sidebar {
  padding: 0 !important;
}
'''
styles.write_text(src, encoding="utf-8")
print("Added Profile Sidebar real 2-column photo CV (uses existing photo uploader).")
