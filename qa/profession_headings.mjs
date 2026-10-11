import assert from 'node:assert/strict';
import { chromium } from 'playwright';

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

  for (const [job, heading] of [
    ['Software Developer', 'TECHNICAL SKILLS'],
    ['Registered Nurse', 'CLINICAL SKILLS'],
    ['Accountant', 'PROFESSIONAL SKILLS'],
    ['', 'PROFESSIONAL SKILLS'],
  ]) await checkHeading(job, heading);

  const languageSelect = page.locator('select')
    .filter({ has: page.locator('option[value="ar"]') })
    .filter({ has: page.locator('option[value="en"]') }).first();
  await languageSelect.selectOption('ar');

  for (const [job, heading] of [
    ['Software Developer', 'المهارات التقنية'],
    ['ممرض طوارئ', 'المهارات السريرية'],
    ['محاسب', 'المهارات المهنية'],
  ]) await checkHeading(job, heading);

  console.log('PASS: Modern role-aware Skills headings in English and Arabic; unknown roles stay neutral.');
} finally {
  await browser.close();
}
