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

const panelZIndex = Number(await page.locator('.wizard-panel').evaluate((el) => getComputedStyle(el).zIndex));
const previewZIndex = Number(await page.locator('.wizard-preview-wrap').evaluate((el) => getComputedStyle(el).zIndex));
assert(panelZIndex > previewZIndex, 'Builder feedback panel must stack above the live CV preview');
log('Builder feedback layers above live CV preview');

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

const readinessTrigger = page.locator('.cv-readiness__trigger');
assert.equal(await readinessTrigger.count(), 1, 'CV readiness trigger missing');
await readinessTrigger.click();
const readinessPanel = page.locator('.cv-readiness__panel');
assert.equal(await readinessPanel.count(), 1, 'CV readiness panel missing');
assert.equal(await readinessPanel.locator('.cv-readiness__list li').count(), 11, 'CV Quality Center should show eleven transparent checks');
const readinessText = (await readinessPanel.innerText()).replace(/\s+/g, ' ');
for (const phrase of [
  'Valid professional email',
  'Focused summary (60–350 chars)',
  '5+ relevant skills',
  'Action-oriented experience wording',
  'Measurable impact when available'
]) {
  assert(readinessText.includes(phrase), 'CV Quality Center missing check: ' + phrase);
}
assert(readinessText.includes('not an ATS score or a hiring guarantee'), 'CV Quality Center disclaimer missing');
log('CV Quality Center shows essentials plus actionable content-quality checks');
await readinessTrigger.click();

const jobTailorTrigger = page.locator('.job-tailor__trigger');
assert.equal(await jobTailorTrigger.count(), 1, 'target job tailoring trigger missing');
await jobTailorTrigger.click();
const jobTailorPanel = page.locator('.job-tailor__panel');
assert.equal(await jobTailorPanel.count(), 1, 'target job tailoring panel missing');
await jobTailorPanel.locator('input').fill('ICU Nurse');
await jobTailorPanel.locator('textarea').fill(
  "Required: Registered Nurse with minimum 2 years of ICU experience. Must hold DHA license, BLS and ACLS. Skills required: ventilator care, patient safety, clinical documentation, hemodynamic monitoring, infection control, communication skills and computer skills. English language required. Bachelor's degree required. Preferred: TNCC, multidisciplinary teamwork and quality improvement."
);
await page.waitForTimeout(1000);
const tailorText = (await jobTailorPanel.innerText()).replace(/\s+/g, ' ');
for (const phrase of ['Overall coverage', 'Must-have coverage', 'Match breakdown', 'Requirements analysis']) {
  assert(tailorText.includes(phrase), 'target job V2 missing: ' + phrase);
}
assert(tailorText.includes('not an ATS score or a hiring guarantee'), 'target job ATS disclaimer missing');
assert((await jobTailorPanel.locator('.job-tailor__breakdown article').count()) >= 4, 'target job category breakdown too small');

const requirementLabels = await jobTailorPanel.locator('.job-tailor__requirements strong').allTextContents();
for (const expected of [
  'Minimum 2 years experience',
  'Dubai Health Authority (DHA) License',
  'Basic Life Support (BLS)',
  'Advanced Cardiovascular Life Support (ACLS)',
  'Trauma Nursing Core Course (TNCC)',
  'Communication Skills',
  'Computer Skills',
  'English Language'
]) {
  assert(requirementLabels.includes(expected), 'Job Match V2.1 missing structured requirement: ' + expected);
}
for (const noise of ['basic', 'patient', 'nursing', 'emergency', 'department', 'license']) {
  assert(!requirementLabels.some((label) => label.toLowerCase() === noise), 'generic noise leaked into requirements: ' + noise);
}
assert(requirementLabels.filter((label) => label.toLowerCase().includes('dha')).length === 1, 'DHA requirement duplicated');
const tailorCoverageBefore = Number((await jobTailorPanel.locator('.job-tailor__score').first().locator('strong').innerText()).replace('%', ''));
log('Job Match V2.1 extracts structured requirements without generic-word noise');
await jobTailorPanel.locator('.job-tailor__close').click();

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

await page.waitForTimeout(1200);
await jobTailorTrigger.click();
const tailorCoverageAfter = Number((await page.locator('.job-tailor__score').first().locator('strong').innerText()).replace('%', ''));
assert(tailorCoverageAfter > tailorCoverageBefore, 'target job coverage did not react to relevant CV content');
assert((await page.locator('.job-tailor__safety').innerText()).includes('Only add a skill'), 'target job factuality warning missing');
assert((await page.locator('.job-tailor__priority-list').count()) <= 1, 'unexpected duplicate must-have list');
log('Job Match V2.1 coverage reacts to confirmed CV content');
await page.locator('.job-tailor__close').click();

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
await page.waitForTimeout(800);
const readinessScoreAfterName = Number((await page.locator('.cv-readiness__trigger strong').innerText()).replace('%', ''));
assert(readinessScoreAfterName >= 10, 'CV Quality Center did not recognize completed name');
log('CV Quality Center score reacts to Builder input');
await page.reload({ waitUntil: 'networkidle' });
assert.equal(await page.locator('.field').filter({ hasText: 'Full name' }).locator('input').first().inputValue(), 'QA Sirati Nurse');
await page.locator('.job-tailor__trigger').click();
assert.equal(await page.locator('.job-tailor__panel input').inputValue(), 'ICU Nurse');
assert((await page.locator('.job-tailor__panel textarea').inputValue()).includes('ventilator care'));
assert((await page.locator('.job-tailor__input-meta').innerText()).includes('Kept in this tab'));
await page.locator('.job-tailor__close').click();
log('local CV save and target-job draft survive reload');

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

await page.goto(base + '/builder/?template=modern&language=en', { waitUntil: 'networkidle' });
for (let step = 0; step < 8; step++) {
  const next = page.getByRole('button', { name: /Continue/ }).last();
  assert((await next.count()) > 0, 'missing Continue button before clean-PDF review step');
  await next.click();
  await page.waitForTimeout(50);
}
const paymentCard = page.locator('.manual-payment-card');
assert.equal(await paymentCard.count(), 1, 'clean-PDF payment card missing');
const paymentCopy = (await paymentCard.innerText()).replace(/\s+/g, ' ');
for (const phrase of [
  'Clean PDF · EGP 50',
  'Get payment details from Sirati Support',
  'Pay EGP 50 by InstaPay or Vodafone Cash',
  'Payment transaction reference',
  'Submit payment reference'
]) {
  assert(paymentCopy.includes(phrase), 'missing payment guidance: ' + phrase);
}
const supportLink = paymentCard.getByRole('link', { name: /Get payment details from Sirati Support/ });
const supportHref = await supportLink.getAttribute('href');
assert(supportHref && supportHref !== '#', 'payment support link must have a real fallback');
assert(supportHref.startsWith('mailto:') || supportHref.startsWith('http'), 'unexpected payment support link: ' + supportHref);
log('clean PDF payment flow clarity and support fallback');

await page.setViewportSize({ width: 390, height: 844 });
overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
assert(overflow <= 2, 'payment review mobile horizontal overflow=' + overflow);
const paymentCardWidth = await paymentCard.evaluate((el) => Math.round(el.getBoundingClientRect().width));
assert(paymentCardWidth <= 390, 'payment card exceeds mobile viewport: ' + paymentCardWidth);
log('clean PDF payment card mobile layout');

await page.setViewportSize({ width: 390, height: 844 });
await page.goto(base + '/builder/?template=modern&language=en', { waitUntil: 'networkidle' });

let mobileTemplateSelect = null;
const mobileSelects = page.locator('select');
for (let i = 0; i < await mobileSelects.count(); i++) {
  const values = await optionValues(mobileSelects.nth(i));
  if (['modern', 'classic', 'compact', 'compact-ats'].every((value) => values.includes(value))) {
    mobileTemplateSelect = mobileSelects.nth(i);
    break;
  }
}
assert(mobileTemplateSelect, 'mobile template selector not found');

for (const value of ['modern', 'classic', 'compact', 'compact-ats']) {
  await mobileTemplateSelect.selectOption(value);
  await page.waitForTimeout(80);
  overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  if (overflow > 2) {
    const offenders = await page.evaluate(() =>
      Array.from(document.querySelectorAll('*'))
        .map((el) => {
          const rect = el.getBoundingClientRect();
          return {
            tag: el.tagName,
            cls: String(el.className || '').slice(0, 120),
            width: Math.round(rect.width),
            left: Math.round(rect.left),
            right: Math.round(rect.right),
            scrollWidth: el.scrollWidth
          };
        })
        .filter((item) => item.right > window.innerWidth + 2 || item.left < -2)
        .sort((a, b) => b.right - a.right)
        .slice(0, 18)
    );
    console.log('MOBILE_OVERFLOW_ELEMENTS_' + value, JSON.stringify(offenders));
  }
  assert(overflow <= 2, value + ' mobile horizontal overflow=' + overflow);
}
const mobileReadiness = page.locator('.cv-readiness');
assert.equal(await mobileReadiness.count(), 1, 'mobile CV readiness missing');
const readinessRect = await mobileReadiness.evaluate((el) => {
  const rect = el.getBoundingClientRect();
  return { left: Math.round(rect.left), right: Math.round(rect.right), width: Math.round(rect.width) };
});
assert(readinessRect.left >= -2 && readinessRect.right <= 392, 'mobile CV readiness exceeds viewport: ' + JSON.stringify(readinessRect));
const mobileTailor = page.locator('.job-tailor');
assert.equal(await mobileTailor.count(), 1, 'mobile target job tailoring missing');
const tailorRect = await mobileTailor.evaluate((el) => {
  const rect = el.getBoundingClientRect();
  return { left: Math.round(rect.left), right: Math.round(rect.right), width: Math.round(rect.width) };
});
assert(tailorRect.left >= -2 && tailorRect.right <= 392, 'mobile target job tailoring trigger exceeds viewport: ' + JSON.stringify(tailorRect));
await page.locator('.job-tailor__trigger').click();
const mobileTailorPanelWidth = await page.locator('.job-tailor__panel').evaluate((el) => Math.round(el.getBoundingClientRect().width));
assert(mobileTailorPanelWidth <= 390, 'mobile Job Match panel exceeds viewport: ' + mobileTailorPanelWidth);
assert((await page.locator('.job-tailor__score-grid').evaluate((el) => getComputedStyle(el).gridTemplateColumns)).split(' ').length === 1, 'mobile Job Match score cards are not stacked');
await page.locator('.job-tailor__close').click();
log('mobile overflow check for all four templates, readiness and Job Match Center');

await mobileTemplateSelect.selectOption('compact-ats');
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
