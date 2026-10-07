import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const base = 'http://127.0.0.1:4173/sirati';
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
const page = await context.newPage();

function log(name) {
  console.log('PASS:', name);
}

async function optionValues(locator) {
  return await locator.locator('option').evaluateAll((options) => options.map((option) => option.value));
}

await page.goto(base + '/templates/', { waitUntil: 'networkidle' });
const cards = page.locator('.template-choice');
assert.equal(await cards.count(), 4);
log('four template cards');

const names = await cards.locator('strong').allTextContents();
for (const name of ['Compact ATS', 'Professional ATS', 'Classic', 'Compact']) {
  assert(names.includes(name), 'missing template ' + name);
}
log('all four template names');

await cards.filter({ hasText: 'Compact ATS' }).click();
await page.getByRole('button', { name: 'Continue to CV details →' }).click();
await page.waitForLoadState('networkidle');
assert(page.url().includes('/builder'));
log('template flow reaches builder');

let onboardingTemplateSelect = null;
const onboardingSelects = page.locator('select');
for (let i = 0; i < await onboardingSelects.count(); i++) {
  const values = await optionValues(onboardingSelects.nth(i));
  if (['modern', 'classic', 'compact', 'compact-ats'].every((value) => values.includes(value))) {
    onboardingTemplateSelect = onboardingSelects.nth(i);
    break;
  }
}
assert(onboardingTemplateSelect, 'onboarding template selector not found');
assert.equal(await onboardingTemplateSelect.inputValue(), 'compact-ats');
assert((await page.locator('.cv-sheet').getAttribute('class')).includes('template-compact-ats'));
log('Compact ATS selection survives template onboarding');

const library = page.locator('details.smart-nursing-library');
assert.equal(await library.count(), 1);
await library.locator('summary').click();
assert(await library.getAttribute('open') !== null);
assert.equal(await library.locator('select').nth(0).locator('option').count(), 8);
assert.equal(await library.locator('select').nth(1).locator('option').count(), 4);
assert.equal(await library.locator('select').nth(2).locator('option').count(), 3);
log('Smart Nursing selectors 8 specialties / 4 levels / 3 markets');

await library.locator('select').nth(0).selectOption('icu');
await library.getByRole('button', { name: 'Select essentials' }).click();
await library.locator('.smart-library-confirm input').check();
const addButton = library.getByRole('button', { name: 'Add selected items to my CV' });
assert(await addButton.isEnabled());
await addButton.click();
await page.locator('.smart-library-success').waitFor();
assert((await page.locator('.smart-library-success').innerText()).includes('Selected items were added'));
log('curated content insertion with explicit confirmation');

const continueButton = page.getByRole('button', { name: /Continue/ }).last();
await continueButton.click();
await page.waitForTimeout(100);
let foundSummary = false;
for (let i = 0; i < await page.locator('textarea').count(); i++) {
  const value = await page.locator('textarea').nth(i).inputValue();
  if (value.toLowerCase().includes('critically ill') || value.toLowerCase().includes('critical')) {
    foundSummary = true;
    break;
  }
}
assert(foundSummary);
log('inserted summary remains editable');

await page.getByRole('button', { name: '← Back' }).click();
await page.locator('.field').filter({ hasText: 'Full name' }).locator('input').first().fill('QA Sirati Nurse');
await page.waitForTimeout(700);
await page.reload({ waitUntil: 'networkidle' });
assert.equal(await page.locator('.field').filter({ hasText: 'Full name' }).locator('input').first().inputValue(), 'QA Sirati Nurse');
log('local save survives reload');

let templateSelect = null;
const selects = page.locator('select');
for (let i = 0; i < await selects.count(); i++) {
  const values = await optionValues(selects.nth(i));
  if (['modern', 'classic', 'compact', 'compact-ats'].every((value) => values.includes(value))) {
    templateSelect = selects.nth(i);
    break;
  }
}
assert(templateSelect, 'template selector not found');

const expectedClasses = {
  modern: 'template-modern',
  classic: 'template-classic',
  compact: 'template-compact',
  'compact-ats': 'template-compact-ats'
};

for (const [value, expectedClass] of Object.entries(expectedClasses)) {
  await templateSelect.selectOption(value);
  await page.waitForTimeout(70);
  const className = await page.locator('.cv-sheet').getAttribute('class');
  assert(className.includes(expectedClass), value + ' did not render expected class');
  assert.equal(await page.locator('.field').filter({ hasText: 'Full name' }).locator('input').first().inputValue(), 'QA Sirati Nurse');
}
log('switching all four templates retains CV data');

let languageSelect = null;
for (let i = 0; i < await selects.count(); i++) {
  const values = await optionValues(selects.nth(i));
  if (values.includes('en') && values.includes('ar') && values.length <= 3) {
    languageSelect = selects.nth(i);
    break;
  }
}
assert(languageSelect, 'language selector not found');
await languageSelect.selectOption('ar');
await page.waitForTimeout(100);
assert.equal(await page.locator('.cv-sheet').getAttribute('dir'), 'rtl');
assert((await page.locator('details.smart-nursing-library').innerText()).includes('مكتبة Sirati الذكية للتمريض'));
await languageSelect.selectOption('en');
log('Arabic RTL and Smart Library localization');

let overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
assert(overflow <= 2, 'desktop horizontal overflow=' + overflow);
log('desktop page-level overflow check');

await page.setViewportSize({ width: 390, height: 844 });
await page.goto(base + '/builder/?template=compact-ats&language=en', { waitUntil: 'networkidle' });
overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
assert(overflow <= 2, 'mobile horizontal overflow=' + overflow);
const mobileLibrary = page.locator('details.smart-nursing-library');
if ((await mobileLibrary.getAttribute('open')) === null) await mobileLibrary.locator('summary').click();
const gridColumns = await mobileLibrary.locator('.smart-nursing-selectors').evaluate((el) => getComputedStyle(el).gridTemplateColumns);
assert(!gridColumns.trim().includes(' '), 'mobile selectors not stacked: ' + gridColumns);
const actionWidth = await mobileLibrary.locator('.smart-library-submit-row .btn').evaluate((el) => Math.round(el.getBoundingClientRect().width));
const rowWidth = await mobileLibrary.locator('.smart-library-submit-row').evaluate((el) => Math.round(el.getBoundingClientRect().width));
assert(actionWidth >= rowWidth - 4, 'mobile action width ' + actionWidth + '/' + rowWidth);
log('mobile responsive Smart Library');

await page.setViewportSize({ width: 1440, height: 1000 });
await page.goto(base + '/builder/?template=modern&language=en', { waitUntil: 'networkidle' });
await page.locator('.field').filter({ hasText: 'Full name' }).locator('input').first().fill('QA Sirati Nurse');

let printTemplateSelect = null;
const printSelects = page.locator('select');
for (let i = 0; i < await printSelects.count(); i++) {
  const values = await optionValues(printSelects.nth(i));
  if (['modern', 'classic', 'compact', 'compact-ats'].every((value) => values.includes(value))) {
    printTemplateSelect = printSelects.nth(i);
    break;
  }
}
assert(printTemplateSelect);

fs.mkdirSync('/tmp/sirati-qa-pdfs', { recursive: true });
for (const value of ['modern', 'classic', 'compact', 'compact-ats']) {
  await printTemplateSelect.selectOption(value);
  await page.waitForTimeout(70);
  const path = '/tmp/sirati-qa-pdfs/' + value + '.pdf';
  await page.pdf({ path, format: 'A4', printBackground: true, preferCSSPageSize: true });
  const size = fs.statSync(path).size;
  assert(size > 5000, value + ' PDF too small: ' + size);
}
log('print/PDF smoke test for all four templates');

await browser.close();
console.log('E2E QA COMPLETE');
