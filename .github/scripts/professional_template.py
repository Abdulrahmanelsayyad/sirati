from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()

# Optional photo stored with the CV JSON; no database migration is needed.
types = root / 'lib' / 'types.ts'
s = types.read_text(encoding='utf-8')
if 'photoDataUrl: string;' not in s:
    s = s.replace('  linkedin: string;\n  profile: string;', '  linkedin: string;\n  photoDataUrl: string;\n  profile: string;')
types.write_text(s, encoding='utf-8')

defaults = root / 'lib' / 'defaultCv.ts'
s = defaults.read_text(encoding='utf-8')
if 'photoDataUrl' not in s:
    s = s.replace("  linkedin: '',\n  profile: '',", "  linkedin: '',\n  photoDataUrl: '',\n  profile: '',")
    s = s.replace("  linkedin: 'linkedin.com/in/your-profile',\n  profile:", "  linkedin: 'linkedin.com/in/your-profile',\n  photoDataUrl: '',\n  profile:")
defaults.write_text(s, encoding='utf-8')

builder = root / 'app' / 'builder' / 'page.tsx'
s = builder.read_text(encoding='utf-8')
if "photoDataUrl: input.photoDataUrl || ''" not in s:
    s = s.replace("    linkedin: input.linkedin || '',\n    profile: input.profile || '',", "    linkedin: input.linkedin || '',\n    photoDataUrl: input.photoDataUrl || '',\n    profile: input.profile || '',")
if 'function handlePhotoUpload' not in s:
    handler = """  function handlePhotoUpload(file?: File) {
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      alert('Please choose an image file.');
      return;
    }
    if (file.size > 8 * 1024 * 1024) {
      alert('Please choose an image smaller than 8 MB.');
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      const source = String(reader.result || '');
      const image = new Image();
      image.onload = () => {
        const scale = Math.min(1, 360 / image.width, 480 / image.height);
        const canvas = document.createElement('canvas');
        canvas.width = Math.max(1, Math.round(image.width * scale));
        canvas.height = Math.max(1, Math.round(image.height * scale));
        const context = canvas.getContext('2d');
        if (!context) return;
        context.drawImage(image, 0, 0, canvas.width, canvas.height);
        setData(prev => ({ ...prev, photoDataUrl: canvas.toDataURL('image/jpeg', 0.84) }));
      };
      image.src = source;
    };
    reader.readAsDataURL(file);
  }

"""
    s = s.replace('  function resetCv() {\n', handler + '  function resetCv() {\n')

if 'photo-upload-row' not in s:
    needle = '              <div className="field"><label>Professional title</label><input value={data.title} onChange={e => update(\'title\', e.target.value)} placeholder="Registered Nurse · Emergency Department" /></div>\n'
    photo = """              <div className="field">
                <label>Professional photo <span className="small">(optional)</span></label>
                <div className="photo-upload-row">
                  <label className="btn btn-secondary photo-upload-button">
                    {data.photoDataUrl ? 'Change photo' : 'Upload photo'}
                    <input type="file" accept="image/*" onChange={e => handlePhotoUpload(e.target.files?.[0])} />
                  </label>
                  {data.photoDataUrl && <button type="button" className="text-btn danger-text" onClick={() => setData(prev => ({ ...prev, photoDataUrl: '' }))}>Remove</button>}
                </div>
                <span className="field-help">Optional. Use a clean head-and-shoulders photo for this template.</span>
              </div>
"""
    if needle in s:
        s = s.replace(needle, needle + photo)
s = s.replace('<option value="modern">Modern</option>', '<option value="modern">Professional ATS</option>')
builder.write_text(s, encoding='utf-8')

templates = root / 'app' / 'templates' / 'page.tsx'
s = templates.read_text(encoding='utf-8')
s = s.replace("{ id: 'modern', name: 'Modern', description: 'Balanced spacing, subtle accent and clear section hierarchy.', badge: 'Recommended' },", "{ id: 'modern', name: 'Professional ATS', description: 'Clean one-column layout with strong black headings and an optional professional photo.', badge: 'Recommended' },")
templates.write_text(s, encoding='utf-8')

preview = root / 'components' / 'CvPreview.tsx'
s = preview.read_text(encoding='utf-8')
s = s.replace("profile: 'Profile',", "profile: 'Professional Summary',")
s = s.replace("experience: 'Experience',", "experience: 'Professional Experience',")
s = s.replace("certifications: 'Certifications & Licenses',", "certifications: 'Licensure and Certifications',")
s = s.replace("courses: 'Courses & Training',", "courses: 'Additional Training',")
s = s.replace("languages: 'Languages'", "languages: 'Languages and Additional Information'")
old_header = """      <header className="cv-head">
        <h1>{data.fullName || (language === 'ar' ? 'اسمك الكامل' : 'Your full name')}</h1>
        <div className="cv-title">{data.title || (language === 'ar' ? 'المسمى الوظيفي' : 'Professional title')}</div>
        <div className="cv-contact">
          {data.email && <span>{data.email}</span>}
          {data.phone && <span>{data.phone}</span>}
          {data.location && <span>{data.location}</span>}
          {data.linkedin && <span>{data.linkedin}</span>}
        </div>
      </header>"""
new_header = """      <header className={`cv-head ${template === 'modern' ? 'professional-head' : ''}`}>
        <div className="professional-head-copy">
          <h1>{data.fullName || (language === 'ar' ? 'اسمك الكامل' : 'Your full name')}</h1>
          <div className="cv-title">{data.title || (language === 'ar' ? 'المسمى الوظيفي' : 'Professional title')}</div>
          <div className="cv-contact">
            {data.phone && <span>{data.phone}</span>}
            {data.email && <span>{data.email}</span>}
            {data.location && <span>{data.location}</span>}
            {data.linkedin && <span>{data.linkedin}</span>}
          </div>
        </div>
        {template === 'modern' && data.photoDataUrl && <img className="professional-photo" src={data.photoDataUrl} alt="Professional portrait" />}
      </header>"""
if old_header in s:
    s = s.replace(old_header, new_header)
preview.write_text(s, encoding='utf-8')

css_path = root / 'app' / 'globals.css'
s = css_path.read_text(encoding='utf-8')
marker = '/* Professional ATS reference template */'
if marker not in s:
    s += r'''

/* Professional ATS reference template */
.template-modern {
  font-family: Arial, Helvetica, sans-serif;
  color:#111;
  padding:52px 58px 50px;
  font-size:13.5px;
  line-height:1.45;
}
.template-modern .professional-head {
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:28px;
  border:0;
  padding:0;
  margin:0 0 20px;
}
.template-modern .professional-head-copy { min-width:0; flex:1; }
.template-modern .cv-head h1 {
  margin:0 0 6px;
  font-size:28px;
  line-height:1.12;
  font-weight:500;
  letter-spacing:0;
}
.template-modern .cv-title {
  margin:0 0 9px;
  color:#111;
  font-size:13px;
  line-height:1.25;
  font-weight:800;
  text-transform:uppercase;
}
.template-modern .cv-contact {
  display:flex;
  flex-wrap:wrap;
  gap:4px 8px;
  margin-top:0;
  color:#111;
  font-size:12.5px;
  line-height:1.35;
}
.template-modern .cv-contact span:not(:last-child)::after { content:' |'; margin-inline-start:7px; color:#444; }
.template-modern .cv-contact span:nth-child(3) { flex-basis:100%; }
.template-modern .cv-contact span:nth-child(2)::after { content:''; margin:0; }
.template-modern .professional-photo {
  width:82px;
  height:108px;
  flex:0 0 82px;
  object-fit:cover;
  object-position:center top;
  background:#f1f1f1;
}
.template-modern .cv-section { margin-top:17px; }
.template-modern .cv-section h2 {
  margin:0 0 7px;
  color:#111;
  font-size:12.5px;
  line-height:1.2;
  font-weight:800;
  letter-spacing:0;
  text-transform:uppercase;
}
.template-modern .cv-section p,
.template-modern .cv-section li,
.template-modern .cv-entry,
.template-modern .cv-meta,
.template-modern .cv-date { font-size:12.5px; line-height:1.42; }
.template-modern .cv-section p { margin:0; }
.template-modern .cv-entry { margin-bottom:8px; }
.template-modern .cv-entry-top { gap:12px; }
.template-modern .cv-entry-top strong { font-weight:800; }
.template-modern .cv-date { color:#111; font-weight:700; }
.template-modern .cv-meta { color:#111; margin-top:2px; }
.template-modern .cv-bullets { margin:4px 0 0; padding-inline-start:20px; }
.template-modern .cv-bullets li { margin:1px 0; }
.template-modern .cv-entry-row { position:relative; padding-inline-start:15px; margin-bottom:3px; }
.template-modern .cv-entry-row::before { content:'•'; position:absolute; inset-inline-start:0; top:0; font-weight:800; }
.template-modern .pre-line { white-space:pre-line; }
.photo-upload-row { display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
.photo-upload-button { position:relative; overflow:hidden; cursor:pointer; }
.photo-upload-button input { position:absolute; inset:0; opacity:0; cursor:pointer; }
[dir="rtl"].template-modern .professional-head { flex-direction:row-reverse; }

@media (max-width: 920px) {
  .template-modern { padding:36px 38px; font-size:12px; }
  .template-modern .cv-head h1 { font-size:25px; }
  .template-modern .professional-photo { width:72px; height:94px; flex-basis:72px; }
}
@media (max-width: 560px) {
  .template-modern { padding:28px 24px; }
  .template-modern .professional-head { gap:16px; }
  .template-modern .cv-head h1 { font-size:22px; }
  .template-modern .professional-photo { width:62px; height:82px; flex-basis:62px; }
}
@media print {
  .template-modern { padding:15mm 17mm 14mm; font-size:10pt; }
  .template-modern .cv-head h1 { font-size:20pt; }
  .template-modern .cv-title { font-size:9.4pt; }
  .template-modern .cv-contact,
  .template-modern .cv-section p,
  .template-modern .cv-section li,
  .template-modern .cv-entry,
  .template-modern .cv-meta,
  .template-modern .cv-date { font-size:9.2pt; }
  .template-modern .cv-section { margin-top:4.3mm; }
  .template-modern .cv-section h2 { margin-bottom:1.8mm; font-size:9.2pt; }
  .template-modern .professional-photo { width:21mm; height:28mm; flex-basis:21mm; }
}
'''
css_path.write_text(s, encoding='utf-8')

print('Applied Professional ATS reference template.')
