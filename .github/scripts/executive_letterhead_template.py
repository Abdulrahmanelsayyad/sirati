"""Executive Letterhead: an original, right-rail editorial CV layout.

A genuinely new semantic document layout, not a recolor of an earlier template.
Uses existing CvData fields, sanitized DetailLines, watermark, real thumbnail,
saved template selection, Arabic RTL, existing PDF pipeline. No new dependencies.
"""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
template_id = "executive-letterhead"

def read(name):
    file = root / name
    return file, file.read_text(encoding="utf-8")

def one(source, old, new):
    if source.count(old) != 1:
        raise RuntimeError("Executive Letterhead anchor missing/ambiguous: " + old[:95])
    return source.replace(old, new, 1)

file, source = read("lib/types.ts")
source = one(source, "'slate-timeline'", "'slate-timeline' | 'executive-letterhead'")
file.write_text(source, encoding="utf-8")

file, source = read("app/builder/page.tsx")
source = one(source,
    '<option value="slate-timeline">Slate Timeline</option>',
    '<option value="slate-timeline">Slate Timeline</option>\n'
    '                <option value="executive-letterhead">Executive Letterhead</option>')
guard = re.compile(r"(?P<lhs>[A-Za-z_$][\w.$]*)\s*===\s*'slate-timeline'")
source, count = guard.subn(
    lambda m: m.group(0) + " || " + m.group("lhs") + " === 'executive-letterhead'", source)
if not count:
    raise RuntimeError("Saved template / Builder allowlist is missing")
file.write_text(source, encoding="utf-8")

file, source = read("app/templates/page.tsx")
match = re.search(r"(?m)^(?P<indent>\s*)\{ id: 'slate-timeline',[^\n]+\n", source)
if not match:
    raise RuntimeError("Template library catalogue anchor missing")
card = (match.group("indent") +
    "{ id: 'executive-letterhead', name: 'Executive Letterhead', "
    "description: 'Editorial full-width masthead, airy experience column and right-side qualifications rail.', "
    "badge: 'Executive Layout' },\n")
source = source[:match.end()] + card + source[match.end():]
match = re.search(r"(?m)^\s*'slate-timeline': \{[^\n]+\}", source)
if not match:
    raise RuntimeError("Live mini-CV benefit list anchor missing")
source = (source[:match.end()] +
    ",\n  'executive-letterhead': { en: ['Editorial masthead', 'Right-side rail'], "
    "ar: ['ترويسة تحريرية', 'عمود جانبي يمين'] }" + source[match.end():])
source = one(source,
    "['modern', 'classic', 'executive-ats'].includes(id)",
    "['modern', 'classic', 'executive-ats', 'executive-letterhead'].includes(id)")
source = source.replace('32 قالبًا', '33 قالبًا')
source = source.replace('32 templates', '33 templates')
source = source.replace('الـ32', 'الـ33')
file.write_text(source, encoding="utf-8")

file, source = read("components/CvPreview.tsx")
anchor = "  if (template === 'modern') {"
new_layout = r'''  if (template === 'executive-letterhead') {
    const skillList = data.skills.split(/[\n,،;]+/).map(s => s.trim()).filter(Boolean);
    const languageList = data.languages.split(/\n+/).map(s => s.trim()).filter(Boolean);
    return (
      <article className="cv-sheet template-executive-letterhead" dir={dir}>
        {watermarked && <div className="cv-watermark">SIRATI · PREVIEW</div>}
        <header className="executive-lh-masthead keep-together">
          <span className="executive-lh-kicker">{language === 'ar' ? 'السيرة المهنية' : 'PROFESSIONAL PROFILE'}</span>
          <h1>{data.fullName || (language === 'ar' ? 'اسمك الكامل' : 'Your full name')}</h1>
          <p className="executive-lh-role">{data.title || (language === 'ar' ? 'المسمى الوظيفي' : 'Professional title')}</p>
          <div className="executive-lh-contact">
            {[data.location, data.phone, data.email, data.linkedin].filter(Boolean).map((part, i) =>
              <span key={i}>{part}</span>)}
          </div>
        </header>
        <div className="executive-lh-grid">
          <main className="executive-lh-main">
            {data.profile && <section className="executive-lh-block keep-together">
              <h2>{language === 'ar' ? 'النبذة المهنية' : 'ABOUT ME'}</h2>
              <p>{data.profile}</p>
            </section>}
            {visibleExperience.length > 0 && <section className="executive-lh-block">
              <h2>{language === 'ar' ? 'الخبرة العملية' : 'CAREER EXPERIENCE'}</h2>
              {visibleExperience.map(item => <div className="executive-lh-entry keep-together" key={item.id}>
                <div className="executive-lh-entry-head"><strong>{item.role}</strong><span>{item.period}</span></div>
                {(item.company || item.location) && <p className="executive-lh-meta">
                  {item.company}{item.company && item.location ? ' · ' : ''}{item.location}
                </p>}
                <DetailLines value={item.details} />
              </div>)}
            </section>}
            {visibleProjects.length > 0 && <section className="executive-lh-block">
              <h2>{language === 'ar' ? 'المشروعات' : 'PROJECT HIGHLIGHTS'}</h2>
              {visibleProjects.map(item => <div className="executive-lh-entry keep-together" key={item.id}>
                <div className="executive-lh-entry-head"><strong>{item.name}</strong><span>{item.period}</span></div>
                {item.organization && <p className="executive-lh-meta">{item.organization}</p>}
                <DetailLines value={item.details} />
              </div>)}
            </section>}
          </main>
          <aside className="executive-lh-rail">
            {skillList.length > 0 && <section className="executive-lh-block keep-together">
              <h2>{language === 'ar' ? 'المهارات' : 'CORE STRENGTHS'}</h2>
              <ul className="executive-lh-skills">{skillList.map((skill, i) => <li key={i}>{skill}</li>)}</ul>
            </section>}
            {visibleEducation.length > 0 && <section className="executive-lh-block">
              <h2>{language === 'ar' ? 'التعليم' : 'EDUCATION'}</h2>
              {visibleEducation.map(item => <div className="executive-lh-entry keep-together" key={item.id}>
                <strong>{item.degree}</strong><span>{item.period}</span>
                {item.school && <p>{item.school}</p>}
                {item.location && <p>{item.location}</p>}
                <DetailLines value={item.details} />
              </div>)}
            </section>}
            {visibleCertifications.length > 0 && <section className="executive-lh-block">
              <h2>{language === 'ar' ? 'الشهادات والتراخيص' : 'CERTIFICATIONS'}</h2>
              {visibleCertifications.map(item => <div className="executive-lh-entry keep-together" key={item.id}>
                <strong>{item.name}</strong>
                {item.issuer && <p>{item.issuer}</p>}
                {item.date && <span>{item.date}</span>}
              </div>)}
            </section>}
            {visibleCourses.length > 0 && <section className="executive-lh-block">
              <h2>{language === 'ar' ? 'الدورات والتدريب' : 'TRAINING'}</h2>
              {visibleCourses.map(item => <div className="executive-lh-entry keep-together" key={item.id}>
                <strong>{item.name}</strong>
                {item.provider && <p>{item.provider}</p>}
                {item.date && <span>{item.date}</span>}
              </div>)}
            </section>}
            {languageList.length > 0 && <section className="executive-lh-block keep-together">
              <h2>{language === 'ar' ? 'اللغات' : 'LANGUAGES'}</h2>
              {languageList.map((value, i) => <p key={i}>{value}</p>)}
            </section>}
          </aside>
        </div>
      </article>
    );
  }

'''
source = one(source, anchor, new_layout + anchor)
file.write_text(source, encoding="utf-8")

file, source = read("app/globals.css")
source += r'''
/* Executive Letterhead — editorial masthead + true right-side qualifications column. */
.cv-sheet.template-executive-letterhead {
  display:block;box-sizing:border-box;padding:0;overflow:visible;background:#fff;
  font-family:Arial,Helvetica,sans-serif;font-size:12px;line-height:1.48;color:#20313d;
}
.template-executive-letterhead .executive-lh-masthead {
  padding:44px 53px 30px;background:#173948;color:#fff;position:relative;
  border-bottom:8px solid #c7ac7e;overflow-wrap:anywhere;
  -webkit-print-color-adjust:exact;print-color-adjust:exact;
}
.template-executive-letterhead .executive-lh-kicker {display:block;font-size:10px;letter-spacing:.21em;font-weight:700;opacity:.83;}
.template-executive-letterhead h1 {font-size:37px;font-weight:700;line-height:1.12;margin:10px 0 4px;color:#fff;}
.template-executive-letterhead .executive-lh-role {font-size:16px;font-weight:500;margin:0 0 20px;color:#e9ded0;}
.template-executive-letterhead .executive-lh-contact {display:flex;gap:5px 17px;flex-wrap:wrap;font-size:10px;color:#edf4f2;overflow-wrap:anywhere;}
.template-executive-letterhead .executive-lh-grid {display:grid;grid-template-columns:minmax(0,1fr) 34%;align-items:stretch;}
.template-executive-letterhead .executive-lh-main {min-width:0;padding:36px 33px 46px 53px;}
.template-executive-letterhead .executive-lh-rail {min-width:0;background:#f1f0ec;padding:36px 31px 46px 27px;overflow-wrap:anywhere;}
.template-executive-letterhead .executive-lh-block {margin:0 0 24px;}
.template-executive-letterhead .executive-lh-block h2 {
  color:#1a4553;font-size:11px;letter-spacing:.09em;text-transform:uppercase;
  border-bottom:2px solid #c7ac7e;padding:0 0 6px;margin:0 0 13px;
}
.template-executive-letterhead .executive-lh-block p {margin:0 0 7px;white-space:pre-wrap;overflow-wrap:anywhere;}
.template-executive-letterhead .executive-lh-entry {margin:0 0 14px;overflow-wrap:anywhere;}
.template-executive-letterhead .executive-lh-entry strong {display:block;font-size:12px;color:#193947;}
.template-executive-letterhead .executive-lh-entry span {display:block;font-size:10px;color:#667984;}
.template-executive-letterhead .executive-lh-entry-head {display:flex;gap:6px 12px;justify-content:space-between;align-items:baseline;flex-wrap:wrap;}
.template-executive-letterhead .executive-lh-entry-head strong {font-size:13px;}
.template-executive-letterhead .executive-lh-meta {color:#627586;font-weight:600;}
.template-executive-letterhead .executive-lh-skills {margin:0;padding:0;list-style:none;}
.template-executive-letterhead .executive-lh-skills li {border-bottom:1px solid #d4d4cd;padding:5px 0;overflow-wrap:anywhere;}
[dir="rtl"].template-executive-letterhead .executive-lh-main {padding:36px 53px 46px 33px;}
[dir="rtl"].template-executive-letterhead .executive-lh-rail {padding:36px 27px 46px 31px;}
.flow-shell .template-carousel-track .template-real-preview__stage > .cv-sheet.template-executive-letterhead {padding:0!important;}
@media print {
  .cv-sheet.template-executive-letterhead {-webkit-print-color-adjust:exact;print-color-adjust:exact;}
  .template-executive-letterhead .executive-lh-entry {break-inside:avoid;page-break-inside:avoid;}
}
'''
file.write_text(source, encoding="utf-8")
print("Added original Executive Letterhead two-column document with full-width masthead.")
