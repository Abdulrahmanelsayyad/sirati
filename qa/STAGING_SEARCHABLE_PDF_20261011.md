# Searchable PDF integration — Staging only

Base: docs/analytics-security-readiness-20261011 at 1b41ae9559303358303d8112a9df174d63329326.
Production main observed unchanged at 54461f950554c18d64690331020596dcf79e43cb.
Netlify deployed base confirmed by read-only API: deploy 6acaca3a22b00e656bbe266e.

## Changes
- Reuse PR #114 Unicode PDF exporter in this Staging branch, without merging unrelated branches.
- Fix reproducible failure in Documents rendering: aria-hidden on the export staging container must not suppress visible PDF text. SVG/script/hidden nodes remain excluded.
- Clone the selected CV to an isolated 210mm export sheet; preserve the existing template, then remove the clone in finally. The editable CV stays unchanged.
- Keep html2canvas media queries equal to the measured DOM. The previous windowWidth change lost Languages/Certification text in mobile templates.
- Reset Arabic heading letter spacing in the export clone; visually confirmed connected Arabic name.
- QA fixtures exist only when SIRATI_PDF_QA_FIXTURE=1; use synthetic data only.

## Verified locally against the reconstructed Staging build
- Next static build and TypeScript PASS. Staging bundle guard PASS; Production Supabase URL absent.
- 36 real browser downloads: nine template families x EN/AR x 1440/390px. Eight populated sections retained in PDF.js extraction in every case: summary, experience, education, certifications, courses, projects, skills, languages. All short fixtures one A4 page.
- Documents-style offscreen aria-hidden rendering exercised at 1440px; Builder-style responsive preview at 390px. These are component/export tests, NOT real authenticated account tests.
- English 1-page and 2-page, Arabic 4-page, short-CV fixtures PASS; searchable phrases retained across page breaks with the inherited >=90% repeated-paragraph assertion.
- Independent pdftotext extraction PASS for all eight section markers in 18 English PDFs.
- Rendered samples inspected: Modern Arabic, Executive Letterhead English mobile, Gold Sidebar Arabic mobile. No clipped section content observed in those samples.

## Reproduce
From a clean generated-source directory, run:
```
SIRATI_PDF_QA_FIXTURE=1 NEXT_PUBLIC_SUPABASE_URL=https://ykfxcxhozqqsvhtdyxho.supabase.co NEXT_PUBLIC_BASE_PATH='' bash qa/render_staging_build.sh
cd site-src/sirati-cv-source
npm install --no-save playwright@1.55.0
npx playwright install chromium
cp ../../qa/pdf_sections_check.mjs ./qa-pdf-sections.mjs
python3 -m http.server 4173 --directory out &
node qa-pdf-sections.mjs
```

## Pending and limits
- No Staging deployment, merge, Production change, migrations, auth changes, or customer-data access performed.
- Staging site currently requires Netlify team sign-in according to read-only access-control metadata.
- Physical Android search/copy/paste, live signed-in Builder/Documents download, and owner PDF review remain pending after separately approved Staging publication.
- This is a hybrid raster template plus invisible Unicode text, not a fully vector, tagged PDF/UA or guaranteed ATS-compatible file.
- Modern profession-specific heading wording is pre-existing and remains a separate PR #117 concern.
