import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { resolve } from 'node:path';

const cases = [
  ['Software Developer', 'technical'], ['Registered Nurse', 'clinical'],
  ['Accountant', 'neutral'], ['', 'neutral'], ['Unknown role', 'neutral'],
  ['مطور برمجيات', 'technical'], ['ممرض طوارئ', 'clinical'],
  ['طبيبة أسنان', 'clinical'], ['مُمَرِّضة', 'clinical'],
  ['محاسب', 'neutral'], ['مدير مطبخ', 'neutral'],
  ['Medical Software Developer', 'technical'], ['Healthcare Accountant', 'neutral'],
];
const headings = {
  en: { technical: 'TECHNICAL SKILLS', clinical: 'CLINICAL SKILLS', neutral: 'PROFESSIONAL SKILLS' },
  ar: { technical: 'المهارات التقنية', clinical: 'المهارات السريرية', neutral: 'المهارات المهنية' },
};
const certifications = (language, category) => category === 'clinical'
  ? (language === 'ar' ? 'التراخيص والشهادات' : 'LICENSURE AND CERTIFICATIONS')
  : (language === 'ar' ? 'الشهادات المهنية' : 'CERTIFICATIONS');

// Render the actual generated component; does not claim browser or PDF acceptance.
if (process.argv.includes('--render-only')) {
  const root = resolve(process.argv[process.argv.indexOf('--render-only') + 1]);
  const require = createRequire(resolve(root, 'package.json'));
  const ts = require('typescript');
  const React = require('react');
  const { renderToStaticMarkup } = require('react-dom/server');
  const source = readFileSync(resolve(root, 'components/CvPreview.tsx'), 'utf8');
  const output = ts.transpileModule(source, { compilerOptions: {
    module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX, target: ts.ScriptTarget.ES2022,
  } }).outputText;
  const module = { exports: {} };
  new Function('require', 'module', 'exports', output)(require, module, module.exports);
  for (const language of ['en', 'ar']) for (const [title, category] of cases) {
    const data = { fullName: 'Synthetic QA', title, email: '', phone: '', location: '',
      linkedin: '', photoDataUrl: '', profile: '', skills: 'Synthetic QA skill', languages: '',
      certifications: [{ id: 'test', name: 'Synthetic QA certificate', issuer: '', date: '' }],
      experience: [], education: [], courses: [], projects: [] };
    const before = JSON.stringify(data);
    const render = () => renderToStaticMarkup(React.createElement(module.exports.default,
      { data, language, template: 'modern', watermarked: false }));
    const html = render();
    assert(html.includes('<h2>' + headings[language][category] + '</h2>'), title);
    assert(html.includes('<h2>' + certifications(language, category) + '</h2>'), title);
    assert(html.includes('Synthetic QA skill') && html.includes('Synthetic QA certificate'));
    assert.equal(JSON.stringify(data), before, 'render must not rewrite CV content');
    data.skills = ''; data.certifications = [];
    assert(!render().includes('<h2>'), 'empty sections must stay hidden');
  }
  console.log('PASS: 26 generated Modern renders, skills/certification headings, content preservation and empty sections.');
  process.exit(0);
}
const { chromium } = await import('playwright');

const base = 'http://127.0.0.1:4173/sirati';
const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  await page.goto(base + '/builder/?template=modern&language=en', { waitUntil: 'networkidle' });
  const preview = page.locator('.cv-sheet.template-modern');
  await preview.waitFor({ timeout: 15000 });

  const templateSelect = page.locator('select').filter({
    has: page.locator('option[value="modern"]')
  }).first();
  await templateSelect.selectOption('modern');

  const titleInput = () => page.locator('.wizard-section-card .field')
    .filter({ hasText: 'Professional title' }).locator('input').first();

  await page.getByRole('button', { name: /^8 Skills$/ }).click();
  const skillsInput = page.locator('.wizard-section-card .field')
    .filter({ hasText: 'Skills' }).locator('textarea').first();
  await skillsInput.fill('Synthetic QA skill');

  const checkHeading = async (jobTitle, expectedHeading) => {
    await page.locator('.cv-substep').first().click();
    await titleInput().fill(jobTitle);
    const heading = preview.locator('.professional-v2-section h2')
      .filter({ hasText: expectedHeading });
    await heading.waitFor({ state: 'visible', timeout: 8000 });
    const rendered = (await preview.locator('.professional-v2-section h2').allTextContents())
      .map(text => text.trim());
    assert(rendered.includes(expectedHeading),
      JSON.stringify({ jobTitle, expectedHeading, rendered }));
  };

  const languageSelect = page.locator('select')
    .filter({ has: page.locator('option[value="ar"]') })
    .filter({ has: page.locator('option[value="en"]') }).first();
  for (const width of [360, 390, 1440]) {
    await page.setViewportSize({ width, height: 1000 });
    for (const language of ['en', 'ar']) {
      await languageSelect.selectOption(language);
      for (const [job, category] of cases) await checkHeading(job, headings[language][category]);
    }
  }
  console.log('PASS: Modern headings for 13 roles, EN/AR, 360/390/1440 widths.');
} finally {
  await browser.close();
}
