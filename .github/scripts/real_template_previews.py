"""Build real mini-CV previews on the Sirati template picker.

The exact production CvPreview component renders synthetic demo-only CV data
inside each selection card; no customer CV, storage, network, or PDF changes.
Run this after compact_template_carousel.py so compact horizontal navigation
remains intact. Never replace the real template styles with fake thumbnails.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
page = root / "app/templates/page.tsx"
source = page.read_text(encoding="utf-8")

old_import = "import type { CvLanguage, TemplateName } from '@/lib/types';"
new_import = """import type { CvData, CvLanguage, TemplateName } from '@/lib/types';
import CvPreview from '@/components/CvPreview';
import { sampleNurseCv } from '@/lib/defaultCv';"""
if old_import not in source:
    raise RuntimeError("Template page imports changed; refusing to fake preview")
source = source.replace(old_import, new_import, 1)

anchor = "export default function TemplatesPage() {"
if anchor not in source or "const templateOptions:" not in source:
    raise RuntimeError("Template page structure changed")

fixtures = r"""
// Synthetic example only. This is never saved as the user's CV.
const arabicDemoCv: CvData = {
  ...sampleNurseCv,
  fullName: 'أحمد حسن',
  title: 'ممرض مسجل | قسم الطوارئ',
  location: 'مصر',
  profile: 'ممرض مسجل بخبرة في قسم الطوارئ وتقييم المرضى والفرز السريري والتوثيق الدقيق والرعاية الآمنة.',
  skills: 'فرز الحالات، تمريض الطوارئ، الإنعاش، مكافحة العدوى، سلامة المرضى، التوثيق السريري',
  languages: 'العربية — اللغة الأم\nالإنجليزية — جيد',
  experience: [
    { ...sampleNurseCv.experience[0], role: 'ممرض قسم الطوارئ', company: 'مستشفى تجريبي',
      location: 'مصر', period: '٢٠٢١ — الآن',
      details: 'تقييم أولوية المرضى ومتابعة الحالات الحرجة.\nالمشاركة في الإنعاش وتسليم الحالات وتوثيق الرعاية.' },
    { ...sampleNurseCv.experience[1], role: 'ممرض', company: 'مستشفى سابق',
      location: 'مصر', period: '٢٠٢٠ — ٢٠٢١',
      details: 'تقديم الرعاية التمريضية والتواصل مع فريق الرعاية.' }
  ],
  education: [{ ...sampleNurseCv.education[0], degree: 'بكالوريوس تمريض',
    school: 'جامعة تجريبية', location: 'مصر', period: '٢٠٢٠' }],
  certifications: [
    { id: 'demo-cert-1', name: 'الإنعاش القلبي الرئوي الأساسي (BLS)', issuer: 'جهة تدريب', date: '' },
    { id: 'demo-cert-2', name: 'الإنعاش القلبي المتقدم (ACLS)', issuer: 'جهة تدريب', date: '' }
  ],
  courses: [{ id: 'demo-course-1', name: 'مكافحة العدوى', provider: 'جهة تدريب', date: '٢٠٢٥' }]
};

// Benefits must match the actual CvPreview styles, not imagined features.
const templateBenefits: Record<TemplateName, { en: [string, string]; ar: [string, string] }> = {
  modern: { en: ['ATS-focused', 'Clear hierarchy'], ar: ['مناسب للـATS', 'تنظيم واضح'] },
  classic: { en: ['Traditional', 'Black headings'], ar: ['طابع كلاسيكي', 'عناوين سوداء'] },
  compact: { en: ['Space-saving', 'Dense sections'], ar: ['يوفر المساحة', 'أقسام متقاربة'] },
  'compact-ats': { en: ['ATS single column', 'Keyword-friendly'], ar: ['عمود واحد ATS', 'مهارات واضحة'] },
  'healthcare-pro': { en: ['Clinical look', 'Teal headings'], ar: ['شكل طبي', 'عناوين بترولي'] },
  'executive-ats': { en: ['Centered header', 'Navy accent'], ar: ['عنوان في المنتصف', 'لمسة كحلي'] }
};

"""
if "const templateBenefits" in source:
    raise RuntimeError("Already has demo template benefits")
source = source.replace(anchor, fixtures + anchor, 1)

old_thumb = '''              <div className={\`template-choice-preview \${option.id}\`} aria-hidden="true">
                <div className="choice-name" />
                <div className="choice-role" />
                <div className="choice-rule" />
                <div className="choice-section"><span /><i /><i /><i /></div>
                <div className="choice-section"><span /><i /><i /></div>
                <div className="choice-columns"><div /><div /></div>
              </div>'''
new_thumb = '''              <div className={\`template-choice-preview \${option.id} template-real-preview\`} aria-hidden="true">
                <div className="template-real-preview__stage" data-demo-template={option.id}>
                  <CvPreview
                    data={language === 'ar' ? arabicDemoCv : sampleNurseCv}
                    template={option.id}
                    language={language}
                    watermarked={false}
                  />
                </div>
                <span className="template-real-preview__demo">
                  {language === 'ar' ? 'نموذج توضيحي' : 'SAMPLE CV'}
                </span>
              </div>'''
if old_thumb not in source:
    raise RuntimeError("Could not locate generic card skeleton")
source = source.replace(old_thumb, new_thumb, 1)

old_copy = '''                <p>{option.description}</p>
                <span className="choice-select">'''
new_copy = '''                <p>{option.description}</p>
                <div className="template-feature-tags">
                  {templateBenefits[option.id][language].map(feature => (
                    <span className="template-feature-tag" key={feature}>{feature}</span>
                  ))}
                </div>
                <span className="choice-select">'''
if old_copy not in source:
    raise RuntimeError("Template card text pattern changed")
source = source.replace(old_copy, new_copy, 1)
page.write_text(source, encoding="utf-8")

css_path = root / "app/globals.css"
css = css_path.read_text(encoding="utf-8")
marker = "/* Real CV previews for template selection — demo-only, source-true. */"
if marker in css:
    raise RuntimeError("Real thumbnail styles already exist")
css += r'''

/* Real CV previews for template selection — demo-only, source-true. */
.flow-shell .template-carousel-track .template-choice {
  flex: 0 0 228px;
  width: 228px;
  min-width: 228px;
  max-width: 228px;
  height: auto;
  padding: 11px;
}
.flow-shell .template-carousel-track .template-choice-preview.template-real-preview {
  box-sizing: border-box;
  position: relative;
  width: 100%;
  height: 216px;
  min-height: 216px;
  max-height: 216px;
  padding: 0;
  margin-bottom: 10px;
  overflow: hidden;
  background: #edf2f7;
  border: 1px solid #cbd5e1;
  border-radius: 11px;
  box-shadow: inset 0 2px 7px rgba(15,23,42,.06);
  pointer-events: none;
}
.flow-shell .template-carousel-track .template-real-preview__stage {
  display: flex;
  justify-content: center;
  position: absolute;
  inset: 7px 4px 0;
  overflow: hidden;
  pointer-events: none;
}
.flow-shell .template-carousel-track .template-real-preview__stage > .cv-sheet {
  /* An actual 210 × 297mm page, scaled uniformly to fit the carousel card. */
  display: block;
  box-sizing: border-box;
  flex: 0 0 794px;
  width: 794px !important;
  min-width: 794px !important;
  max-width: none !important;
  height: auto !important;
  min-height: 1122px !important;
  margin: 0 !important;
  padding: 38px 43px 40px;
  overflow: visible;
  transform: scale(.18);
  transform-origin: top center;
  background: #fff;
  border: 0;
  border-radius: 0;
  box-shadow: 0 6px 18px rgba(15,23,42,.14);
  pointer-events: none;
}
.flow-shell .template-carousel-track .template-real-preview__demo {
  position: absolute;
  inset: auto 6px 6px auto;
  padding: 3px 5px;
  border-radius: 4px;
  color: #334155;
  background: rgba(255,255,255,.94);
  border: 1px solid #cbd5e1;
  font-size: 9px;
  line-height: 1.2;
  font-weight: 700;
  letter-spacing: .04em;
  pointer-events: none;
}
.flow-shell .template-carousel-track .template-choice-copy p {
  min-height: 30px;
}
.flow-shell .template-carousel-track .template-feature-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin: 5px 0 9px;
  min-height: 39px;
}
.flow-shell .template-carousel-track .template-feature-tag {
  align-self: start;
  padding: 4px 6px;
  border-radius: 6px;
  background: #eff6ff;
  border: 1px solid #dbeafe;
  color: #1d4e7d;
  font-size: 10px;
  line-height: 1.3;
  font-weight: 600;
}
.flow-shell .template-carousel-track .template-choice.selected .template-feature-tag {
  border-color: #b6c9e4;
  background: #e8f0ff;
}
@media (max-width: 640px) {
  .flow-shell .template-carousel-track .template-choice {
    flex: 0 0 184px;
    width: 184px;
    min-width: 184px;
    max-width: 184px;
    padding: 9px;
  }
  .flow-shell .template-carousel-track .template-choice-preview.template-real-preview {
    height: 177px;
    min-height: 177px;
    max-height: 177px;
    margin-bottom: 9px;
  }
  .flow-shell .template-carousel-track .template-real-preview__stage > .cv-sheet {
    transform: scale(.148);
  }
  .flow-shell .template-carousel-track .template-feature-tag {
    font-size: 9px;
    padding: 3px 5px;
  }
  .flow-shell .template-carousel-track .template-real-preview__demo {
    font-size: 8px;
  }
}
@media print {
  .template-real-preview__stage .cv-sheet {
    display: none !important;
  }
}
'''
css_path.write_text(css, encoding="utf-8")
print("Rendered six real CV template mini previews with synthetic example and truthful feature tags.")
