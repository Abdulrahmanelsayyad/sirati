"""Refine the existing Modern template to the owner's October 2026 PDF reference."""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
preview = root / 'components/CvPreview.tsx'
text = preview.read_text()
start = text.index("  if (template === 'modern') {")
end = text.index('\n  return (', start)
modern = text[start:end]
if 'modern-reference-layout' not in modern:
    # Move whole sections in DOM order, so visual and extracted order agree.
    def take(key):
        global modern
        a = modern.index('        {' + key + ' && (')
        b = modern.index('\n        )}', a) + len('\n        )}')
        block = modern[a:b]
        modern = modern[:a] + modern[b:]
        return block

    cert = take('visibleCertifications.length > 0')
    skills = take('skillLine')
    anchor = '        {visibleEducation.length > 0 && ('
    modern = modern.replace(anchor, skills + '\n\n' + cert + '\n\n' + anchor, 1)
    modern = modern.replace('template-modern professional-v2"', 'template-modern professional-v2 modern-reference-layout"')
    modern = modern.replace("'PROFESSIONAL SUMMARY'", "'PROFESSIONAL PROFILE'")
    modern = modern.replace(".join(' | ')", ".join(' • ')")
    modern = modern.replace('                  {exp.period && <span> | {exp.period}</span>}\n', '')
    modern = modern.replace('{(exp.company || exp.location) && (', '{(exp.company || exp.location || exp.period) && (')
    modern = modern.replace('                    {exp.location && <span>{exp.location}</span>}', '                    {exp.location && <span>{exp.location}</span>}\n                    {exp.period && <span>{exp.company || exp.location ? \' | \' : \'\'}{exp.period}</span>}')
    modern = modern.replace('                  {item.date && <span> | {item.date}</span>}', '                  {item.date && <span className="modern-reference-cert-date">{item.date}</span>}', 1)
    text = text[:start] + modern + text[end:]
    preview.write_text(text)

css_path = root / 'app/globals.css'
css = css_path.read_text()
marker = '/* Modern reference layout: shared preview and A4 export */'
if marker not in css:
    css += '\n' + marker + r'''
.cv-sheet.template-modern.professional-v2.modern-reference-layout {
  padding:28px 53px 48px;
  border:0; border-top:21px solid #16364a; border-radius:0;
  background:#fff; color:#293943; font-family:Arial,Helvetica,sans-serif;
  font-size:12.5px; line-height:1.4;
}
.modern-reference-layout .professional-v2-head { gap:24px; margin:0 0 20px; }
.modern-reference-layout .professional-v2-head h1 {
  margin:0 0 12px; color:#16364a; font-size:28px;
  font-weight:800; line-height:1.15; letter-spacing:.5px; text-transform:uppercase;
}
.modern-reference-layout .professional-v2-title {
  color:#21828d; font-size:15px; line-height:1.3; margin-bottom:10px;
}
.modern-reference-layout .professional-v2-contact-line {
  color:#293943; font-size:12.5px; line-height:1.4; margin-bottom:2px;
  overflow-wrap:anywhere;
}
.modern-reference-layout .professional-v2-photo {
  width:88px; height:103px; flex:0 0 88px; border:0; border-radius:0;
}
.modern-reference-layout .professional-v2-section { margin:0 0 10px; }
.modern-reference-layout .professional-v2-section h2 {
  color:#21828d; font-size:13px; line-height:1.25; font-weight:800;
  border-bottom:1px solid #d4e0e6; padding:0 0 5px; margin:0 0 10px;
}
.modern-reference-layout .professional-v2-section p,
.modern-reference-layout .professional-v2-list li,
.modern-reference-layout .professional-v2-org-line,
.modern-reference-layout .cv-bullets li,
.modern-reference-layout .professional-v2-training-line {
  font-size:12.5px; line-height:1.4; color:#293943;
}
.modern-reference-layout .professional-v2-role-line {
  color:#16364a; font-size:14px; line-height:1.3; margin:0 0 3px;
}
.modern-reference-layout .professional-v2-org-line { color:#596c7b; margin-bottom:5px; }
.modern-reference-layout .professional-v2-entry { margin-bottom:12px; }
.modern-reference-layout .professional-v2-list { list-style:none; padding:0; margin:0; }
.modern-reference-layout .professional-v2-list li { margin-bottom:6px; }
.modern-reference-layout .professional-v2-cert-name,
.modern-reference-layout .professional-v2-training-line strong { font-weight:700; }
.modern-reference-cert-date { display:block; }
.modern-reference-layout .cv-bullets { padding-inline-start:11px; margin:4px 0 0; }
.modern-reference-layout .cv-bullets li { margin-bottom:3px; }
.modern-reference-layout[dir="rtl"] .professional-v2-head h1 { letter-spacing:normal; }
/* Responsive preview only: PDF always retains the A4 dimensions above. */
@media screen and (max-width:560px) {
  .cv-sheet.template-modern.professional-v2.modern-reference-layout:not(.sirati-pdf-offscreen *) {
    padding:20px 18px 28px; border-top-width:12px;
  }
  .modern-reference-layout:not(.sirati-pdf-offscreen *) .professional-v2-head { gap:12px; }
  .modern-reference-layout:not(.sirati-pdf-offscreen *) .professional-v2-head h1 { font-size:21px; }
  .modern-reference-layout:not(.sirati-pdf-offscreen *) .professional-v2-title { font-size:13px; }
  .modern-reference-layout:not(.sirati-pdf-offscreen *) .professional-v2-photo { width:64px; height:76px; flex-basis:64px; }
}
'''
    css_path.write_text(css)
print('Applied Modern navy/teal reference layout to shared preview and PDF.')
