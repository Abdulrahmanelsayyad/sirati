import assert from 'node:assert/strict';
import fs from 'node:fs';

// Removal is a security and UX regression gate: don't ship the old feature.
assert.equal(fs.existsSync('components/TargetJobTailor.tsx'), false, 'retired Job Match component must not ship');
assert(fs.existsSync('components/ExperienceDescriptionPicker.tsx'), 'Experience Description Pro must be preserved');
assert(!fs.readFileSync('app/layout.tsx', 'utf8').includes('TargetJobTailor'), 'Job Match must not mount in layout');
assert(!fs.readFileSync('app/globals.css', 'utf8').includes('.job-tailor'), 'retired Job Match styles must not ship');
console.log('PASS: retired Job Match absent from source, layout and CSS; Experience Pro preserved');

const { chromium } = await import('playwright');


const base = 'http://127.0.0.1:4173/sirati';
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
const page = await context.newPage();

// Premium Minimal V1: verify the actual rendered landing page before other E2E.
await page.goto(base + '/', { waitUntil: 'networkidle' });
assert.equal(await page.locator('.marketing-page').count(), 1, 'Sirati landing page missing');
assert((await page.locator('.marketing-hero h1').innerText()).includes('A CV that looks'),
  'Premium Editorial V2 headline was not applied');
const brandColor = await page.locator('.marketing-page').evaluate(el =>
  getComputedStyle(el).getPropertyValue('--pm-green').trim()
);
assert.equal(brandColor, '#184237', 'unified Premium Minimal color token missing');
for (const width of [320, 390, 1440]) {
  await page.setViewportSize({ width, height: 844 });
  const bounds = await page.locator('.marketing-hero').evaluate(el => {
    const rect = el.getBoundingClientRect();
    return { left: rect.left, right: rect.right, viewport: window.innerWidth };
  });
  assert(bounds.left >= -2 && bounds.right <= bounds.viewport + 2,
    'Premium landing hero overflows at ' + width + 'px: ' + JSON.stringify(bounds));
  assert(await page.locator('.marketing-hero .hero-actions a').first().isVisible(),
    'Main CV creation CTA must remain visible at ' + width + 'px');
}
await page.setViewportSize({ width: 1440, height: 1000 });
console.log('PASS: Premium Minimal rendered homepage, brand token, and 320/390/1440 responsive hero');

function log(name) {
  console.log('PASS:', name);
}

async function optionValues(locator) {
  return await locator.locator('option').evaluateAll((options) => options.map((option) => option.value));
}

await page.goto(base + '/templates/', { waitUntil: 'networkidle' });
const cards = page.locator('.template-choice');
assert.equal(await cards.count(), 8);
log('eight template cards');

const names = await cards.locator('strong').allTextContents();
for (const name of ['Compact ATS', 'Professional ATS', 'Classic', 'Compact', 'Healthcare Pro', 'Executive ATS', 'Profile Sidebar', 'Gold Sidebar']) {
  assert(names.includes(name), 'missing template ' + name);
}
log('all eight template names');

// True finished-resume previews use the same CvPreview renderer as the Builder,
// never six generic line-pattern illustrations or customer account data.
const templateIds = ['modern', 'classic', 'compact', 'compact-ats', 'healthcare-pro', 'executive-ats', 'profile-sidebar', 'gold-sidebar'];
assert.equal(await page.locator('.template-real-preview__stage > .cv-sheet').count(), 8);
const actualMiniatures = await cards.evaluateAll(buttons => buttons.map(button => {
  const stage = button.querySelector('.template-real-preview__stage');
  const sheet = stage?.querySelector('.cv-sheet');
  return {
    id: stage?.getAttribute('data-demo-template'),
    actualClass: sheet?.classList.contains('template-' + stage?.getAttribute('data-demo-template')),
    name: sheet?.querySelector('h1')?.textContent?.trim(),
    sections: sheet?.querySelectorAll('section').length,
    features: button.querySelectorAll('.template-feature-tag').length,
    demoLabel: button.querySelector('.template-real-preview__demo')?.textContent?.trim(),
    watermark: button.querySelectorAll('.cv-watermark').length
  };
}));
assert.equal(new Set(actualMiniatures.map(item => item.id)).size, 8, 'each of eight miniature previews needs a unique template ID');
assert(templateIds.every(id => actualMiniatures.some(item => item.id === id && item.actualClass)), 'mini CV must use the matching real CV template styling');
for (const thumbnail of actualMiniatures) {
  assert.equal(thumbnail.name, 'Ahmed Hassan', 'sample-only demo name must render on every CV');
  assert(thumbnail.sections >= 4, thumbnail.id + ' preview must show a completed CV, not placeholder skeleton');
  assert.equal(thumbnail.features, 2, thumbnail.id + ' must explain two real differentiators');
  assert.equal(thumbnail.demoLabel, 'SAMPLE CV', thumbnail.id + ' must identify placeholder data');
  assert.equal(thumbnail.watermark, 0, 'avoid watermark obscuring miniature');
}
log('all eight template cards render genuine sample CvPreview with distinct feature tags');

const sidebarCard = page.locator('.template-choice').filter({ hasText: 'Profile Sidebar' });
assert.equal(await sidebarCard.locator('.profile-sidebar-layout > .profile-sidebar-rail').count(), 1, 'new template must have a genuine sidebar');
assert.equal(await sidebarCard.locator('.profile-sidebar-layout > .profile-sidebar-main').count(), 1, 'new template must have a genuine main content column');
assert.equal(await sidebarCard.locator('.profile-sidebar-portrait-placeholder').count(), 1, 'demo requires honest portrait placeholder');
assert.equal(await sidebarCard.locator('.profile-sidebar-rail .profile-sidebar-skills li').count() > 0, true, 'skills must be in sidebar');
assert.equal(await sidebarCard.locator('.profile-sidebar-main .profile-sidebar-section').count() > 2, true, 'main must include summary, experience and education');
assert((await sidebarCard.innerText()).includes('Photo + sidebar'), 'card must describe true visual difference');
log('Profile Sidebar thumbnail shows actual portrait slot, skill rail and main body');

const goldCard = page.locator('.template-choice').filter({hasText:'Gold Sidebar'});
assert.equal(await goldCard.count(), 1, 'Gold Sidebar must appear once in the catalog');
assert.equal(await goldCard.locator('.cv-sheet.template-gold-sidebar').count(), 1, 'Gold miniature must use actual CvPreview');
assert.equal(await goldCard.locator('.gold-sidebar-layout > .gold-sidebar-rail').count(), 1);
assert.equal(await goldCard.locator('.gold-sidebar-layout > .gold-sidebar-main').count(), 1);
assert.equal(await goldCard.locator('.gold-sidebar-portrait-placeholder').count(), 1, 'demo portrait should use an honest no-photo illustration');
assert((await goldCard.locator('.gold-sidebar-rail').innerText()).includes('EDUCATION'), 'side rail should contain actual education');
assert((await goldCard.locator('.gold-sidebar-main').innerText()).includes('WORK EXPERIENCE'), 'main panel should contain actual experience');
assert((await goldCard.locator('.gold-sidebar-main').innerText()).includes('SKILLS'), 'skills should be in main panel per reference');
assert.equal(await goldCard.locator('.gold-sidebar-timeline .gold-sidebar-entry').count(), 2);
const goldVisual = await goldCard.locator('.gold-sidebar-rail').evaluate(rail => ({
  background:getComputedStyle(rail).backgroundColor,
  accent:getComputedStyle(rail,'::before').backgroundColor,
  clip:getComputedStyle(rail,'::before').clipPath,
  width:rail.getBoundingClientRect().width
}));
assert.equal(goldVisual.accent, 'rgb(247, 185, 20)', 'diagonal rail must have actual gold accent');
assert(goldVisual.clip.includes('polygon'), 'gold diagonal shape is missing');
assert(goldVisual.width > 0, 'the charcoal rail is not being laid out');
log('Gold Sidebar sample miniature has actual charcoal/gold diagonal rail, portrait, side education and main timeline');


const polishedMini = await sidebarCard.locator('.profile-sidebar-portrait-placeholder').evaluate(el => {
  const rect = el.getBoundingClientRect();
  const styles = getComputedStyle(el);
  return { width: rect.width, height: rect.height, borderRadius: styles.borderRadius, borderColor: styles.borderTopColor };
});
assert(Math.abs(polishedMini.width - polishedMini.height) <= 1, 'sidebar miniature portrait must be square for circular crop');
assert.equal(polishedMini.borderRadius, '50%', 'portrait in mini-CV must be circular');
fs.mkdirSync('/tmp/sirati-qa-pdfs', { recursive: true });
log('Profile Sidebar template card shows integrated circular photo framing');



await page.getByRole('button', { name: 'العربية' }).click();
assert.equal(await page.locator('.template-real-preview__stage > .cv-sheet[dir="rtl"]').count(), 8, 'all eight mini CVs must support Arabic RTL');
assert.equal(await page.locator('.template-real-preview__demo').filter({ hasText: 'نموذج توضيحي' }).count(), 8);
assert.equal(await page.locator('.template-feature-tag').filter({ hasText: 'عناوين بترولي' }).count(), 1);
await page.getByRole('button', { name: 'English' }).click();
log('template demo CV and feature tags localize to Arabic RTL and back to English');


const carousel = page.locator('.template-carousel-track');
assert.equal(await carousel.count(), 1, 'horizontal template carousel missing');
const desktopMetrics = await carousel.evaluate(el => ({
  client: el.clientWidth, scroll: el.scrollWidth,
  card: Math.round(el.querySelector('.template-choice').getBoundingClientRect().width),
  preview: Math.round(el.querySelector('.template-choice-preview').getBoundingClientRect().height),
}));
assert(desktopMetrics.scroll > desktopMetrics.client + 100, 'desktop templates must scroll horizontally');
assert(desktopMetrics.card <= 235 && desktopMetrics.preview <= 230, 'desktop cards must stay compact');
assert(desktopMetrics.card >= 205 && desktopMetrics.preview >= 175, 'miniature completed CV is too small to inspect');
const nextTemplates = page.getByRole('button', { name: 'Next templates' });
const previousTemplates = page.getByRole('button', { name: 'Previous templates' });
assert(await previousTemplates.isDisabled(), 'previous arrow should start disabled');
assert(await nextTemplates.isEnabled(), 'next arrow should be available');
await nextTemplates.click();
await page.waitForFunction(() => document.querySelector('.template-carousel-track').scrollLeft > 30);
assert(await previousTemplates.isEnabled(), 'previous arrow should enable after scrolling');
log('compact desktop carousel with working horizontal arrow navigation');

await page.setViewportSize({ width: 390, height: 844 });
const mobileMetrics = await carousel.evaluate(el => ({
  client: el.clientWidth, scroll: el.scrollWidth,
  card: Math.round(el.querySelector('.template-choice').getBoundingClientRect().width),
  page: document.documentElement.scrollWidth,
}));
assert(mobileMetrics.scroll > mobileMetrics.client + 100, 'mobile templates must scroll horizontally');
assert(mobileMetrics.card <= 195, 'mobile template card too wide');
assert(mobileMetrics.page <= 392, 'mobile template carousel causes page overflow');
await page.setViewportSize({ width: 1440, height: 1000 });
log('mobile horizontal template strip stays inside viewport');

// Template Library: opt-in gallery must not overload initial mobile view.
await page.getByRole('button', { name: 'Browse all 32 templates' }).click();
assert.equal(await page.locator('.template-carousel-track.template-library-grid').count(), 1, 'gallery grid is not active');
assert.equal(await cards.count(), 8, 'gallery must render only eight CV previews initially');
assert.equal(await page.locator('.template-library-count').innerText(), 'Showing 8 of 32 templates');
for (let batch = 0; batch < 3; batch++) {
  await page.getByRole('button', { name: 'Show 8 more templates ↓' }).click();
}
assert.equal(await cards.count(), 32, 'all 32 templates must be reachable with progressive loading');
const allVariantIds = await page.locator('.template-real-preview__stage').evaluateAll(nodes =>
  nodes.map(node => node.getAttribute('data-demo-template'))
);
assert.equal(new Set(allVariantIds).size, 32, 'every gallery entry needs its own stable ID');
for (const id of ['aurora-ats', 'ocean-profile', 'copper-timeline']) {
  assert(allVariantIds.includes(id), id + ' not found in library');
  assert.equal(await page.locator('.template-real-preview__stage[data-demo-template="' + id + '"] .cv-sheet.template-' + id).count(), 1, id + ' must use a genuine CvPreview');
}
log('Template Library: progressive gallery exposes 32 genuine CV previews');
await page.getByRole('button', { name: 'Photo + Sidebar' }).click();
await page.locator('.template-library-count').waitFor();
assert((await page.locator('.template-library-count').innerText()).includes('of 14'), 'photo category should match fourteen real templates');
await page.getByRole('button', { name: 'All', exact: true }).click();
await page.getByRole('searchbox', { name: 'Search templates' }).fill('Copper Timeline');
assert.equal(await cards.count(), 1, 'search should filter by visible template name');
assert.equal(await page.locator('.template-real-preview__stage[data-demo-template="copper-timeline"]').count(), 1);
await page.getByRole('searchbox', { name: 'Search templates' }).fill('impossible-template-query');
assert.equal(await cards.count(), 0, 'unknown search should not show unrelated templates');
await page.getByRole('searchbox', { name: 'Search templates' }).fill('');
await page.setViewportSize({ width: 390, height: 844 });
const galleryWidth = await page.evaluate(() => document.documentElement.scrollWidth);
assert(galleryWidth <= 392, 'mobile gallery overflows viewport: ' + galleryWidth);
await page.getByRole('button', { name: 'Back to featured' }).click();
assert.equal(await cards.count(), 8, 'featured carousel should restore original eight cards');
await page.setViewportSize({ width: 1440, height: 1000 });
log('Template Library: category/search, empty state, mobile width and featured return');

await sidebarCard.screenshot({path:'/tmp/sirati-qa-pdfs/profile-sidebar-card-desktop.png'});
log('captured Profile Sidebar sample card for independent visual review');
await goldCard.screenshot({path:'/tmp/sirati-qa-pdfs/gold-sidebar-card-desktop.png'});
log('captured Gold Sidebar complete sample card screenshot');



// Template choice should bring the next action into view, not submit for the user.
await page.setViewportSize({ width: 390, height: 844 });
await cards.filter({ hasText: 'Compact ATS' }).click();
await page.waitForFunction(() => {
  const button = [...document.querySelectorAll('button')].find(
    el => el.textContent?.includes('Continue to CV details')
  );
  if (!button) return false;
  const rect = button.getBoundingClientRect();
  return rect.top >= -1 && rect.bottom <= window.innerHeight + 1;
});
assert(page.url().includes('/templates'), 'template choice must not skip confirmation');
log('mobile template choice automatically scrolls to visible Continue CTA');
await page.setViewportSize({ width: 1440, height: 1000 });
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
  if (['modern', 'classic', 'compact', 'compact-ats', 'healthcare-pro', 'executive-ats', 'profile-sidebar', 'gold-sidebar'].every((value) => values.includes(value))) {
    onboardingTemplateSelect = onboardingSelects.nth(i);
    break;
  }
}
assert(onboardingTemplateSelect, 'onboarding template selector not found');
assert.equal(await onboardingTemplateSelect.inputValue(), 'compact-ats');
assert((await page.locator('.cv-sheet').getAttribute('class')).includes('template-compact-ats'));
log('Compact ATS selection survives template onboarding');

const qualityImplementation = fs.readFileSync('components/CvReadinessCheck.tsx', 'utf8');
assert(qualityImplementation.includes('evaluateCvQuality(data)'), 'Quality engine must evaluate Builder CV data');
assert(!qualityImplementation.includes('document.querySelectorAll'), 'Quality must not scan editable DOM fields');
assert(!qualityImplementation.includes('setInterval'), 'Quality must not poll the browser for field text');
log('CV Quality checker V2 uses the authoritative CV data object, not DOM scraping');

const anchoredQuality = page.locator('.wizard-preview-wrap .preview-stage > .cv-readiness');
assert.equal(await anchoredQuality.count(), 1, 'CV Quality must be mounted in the CV preview panel');
assert.equal(await page.locator('body > .cv-readiness').count(), 0, 'old floating CV Quality must be absent');
const anchoredMetrics = await anchoredQuality.evaluate((el) => {
  const wrap = el.parentElement;
  const sheet = wrap?.querySelector('.cv-sheet');
  const bounds = el.getBoundingClientRect();
  const parentBounds = wrap?.getBoundingClientRect();
  return {
    position: getComputedStyle(el).position,
    insidePreview: Boolean(sheet && (el.compareDocumentPosition(sheet) & Node.DOCUMENT_POSITION_FOLLOWING)),
    width: Math.round(bounds.width),
    parentWidth: Math.round(parentBounds?.width || 0)
  };
});
assert.notEqual(anchoredMetrics.position, 'fixed', 'CV Quality must not float over form fields');
assert(anchoredMetrics.insidePreview, 'CV Quality must appear before the actual printable CV');
assert(anchoredMetrics.width <= anchoredMetrics.parentWidth + 2, 'quality card exceeds CV preview width');
const inlineProgress = anchoredQuality.getByRole('progressbar', { name: 'CV quality completion' });
assert.equal(await inlineProgress.count(), 1, 'always-visible quality progress bar missing');
assert.equal(await inlineProgress.getAttribute('aria-valuemax'), '100');
log('CV Quality percentage and progress bar anchored to preview, not floating');

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

// Smart CV: Professional Title shows three ready-to-select Summary templates.
await page.evaluate(() => {
  const title = document.createElement('div');
  title.className = 'field';
  title.id = 'qa-summary-role-field';
  title.innerHTML = '<label>Professional title</label><input id="qa-summary-role" value="Accountant">';
  const summary = document.createElement('div');
  summary.className = 'field';
  summary.id = 'qa-personal-summary-field';
  summary.innerHTML = '<label>Personal Summary</label><textarea id="qa-personal-summary"></textarea>';
  document.body.append(title, summary);
});
const qaSummary = page.locator('#qa-personal-summary');
const summaryPanel = page.locator('#qa-personal-summary-field .sirati-summary-panel');
await summaryPanel.waitFor();
assert.equal(await summaryPanel.locator('.sirati-summary-choice').count(), 3, 'three Summary choices must appear without an extra click');
assert((await summaryPanel.locator('.sirati-summary-context').innerText()).includes('Accountant'), 'must reuse Professional Title');
assert.equal(await summaryPanel.locator('.sirati-summary-role input').count(), 0, 'must not ask for title a second time');
assert((await summaryPanel.innerText()).includes('accurate financial records'), 'accountant-specific suggestions missing');
assert.equal(await qaSummary.inputValue(), '', 'suggestions must never insert without selection');
const pickedSummary = (await summaryPanel.locator('.sirati-summary-choice__text').nth(1).innerText()).trim();
await summaryPanel.locator('.sirati-summary-choice').nth(1).click();
assert.equal(await qaSummary.inputValue(), pickedSummary, 'one-click choice should insert into Summary');
await qaSummary.fill('My existing personally written summary.');
await page.locator('#qa-personal-summary-field .sirati-summary-trigger').click();
page.once('dialog', dialog => dialog.dismiss());
await summaryPanel.locator('.sirati-summary-choice').first().click();
assert.equal(await qaSummary.inputValue(), 'My existing personally written summary.', 'declined replacement must preserve manual summary');
await page.locator('#qa-summary-role').fill('Software Developer');
await page.waitForFunction(() => document.querySelector('.sirati-summary-panel')?.textContent?.includes('maintainable software'));
assert((await summaryPanel.locator('.sirati-summary-context').innerText()).includes('Software Developer'), 'Professional Title changes must update choices');
await summaryPanel.getByRole('button', { name: 'Hide suggestions' }).click();
await page.locator('#qa-summary-role').fill('Unlisted Job Profession');
await summaryPanel.waitFor();
assert((await summaryPanel.innerText()).includes('organized work and clear communication'), 'unknown title should receive generic editable suggestions');
await page.evaluate(() => {
  document.getElementById('qa-summary-role-field')?.remove();
  document.getElementById('qa-personal-summary-field')?.remove();
});
log('Smart CV auto-shows 3 role-matched Summary cards, safely selects and respects existing text');

await page.evaluate(() => {
  const field = document.createElement('div');
  field.className = 'field';
  field.id = 'qa-experience-description-field';
  field.innerHTML = '<label>Job title<input id="qa-experience-role" value="Senior ICU Nurse"></label><label>Description<textarea id="qa-experience-description"></textarea></label>';
  document.body.appendChild(field);
});
const qaExperienceDescription = page.locator('#qa-experience-description');
await qaExperienceDescription.focus();
const contextualTrigger = page.locator('.sirati-description-assistant-slot .experience-picker-trigger');
assert.equal(await contextualTrigger.count(), 1, 'contextual description action missing next to Description');
assert.equal(await page.locator('.experience-picker').count(), 0, 'suggestions must remain closed until the user requests them');
await contextualTrigger.click();
const experiencePicker = page.locator('.experience-picker');
assert.equal(await experiencePicker.count(), 1, 'description suggestions did not open on user click');
assert((await experiencePicker.innerText()).includes('Job description suggestions'), 'job-description title missing');
assert((await experiencePicker.innerText()).includes('Senior ICU Nurse'), 'active role context missing');
assert((await experiencePicker.innerText()).includes('Auto-detected from role'), 'role auto-detection indicator missing');
assert.equal(await experiencePicker.locator('.experience-picker__selectors select').nth(0).inputValue(), 'icu', 'ICU specialty was not auto-detected');
assert.equal(await experiencePicker.locator('.experience-picker__selectors select').nth(1).inputValue(), 'senior', 'Senior level was not auto-detected');
assert.equal(await experiencePicker.locator('.experience-picker__categories button').count(), 6, 'Experience Pro category filters missing');
assert.equal(await experiencePicker.locator('.experience-picker__career-selectors').count(), 0, 'nursing roles must retain nursing-specific selectors in Pro V3');
await experiencePicker.getByRole('button', { name: 'Select recommended' }).click();
const selectedExperienceOptions = experiencePicker.locator('.experience-picker__options input:checked');
assert((await selectedExperienceOptions.count()) >= 2, 'recommended multi-select did not select enough experience options');
assert.equal(await page.locator('.experience-picker').count(), 1, 'selecting suggestions must not close Smart CV before insertion');
const selectedTexts = await experiencePicker.locator('.experience-picker__options article.is-selected label span').allTextContents();
const addSelectedExperience = experiencePicker.getByRole('button', { name: 'Add selected' });
assert(await addSelectedExperience.isEnabled(), 'Add selected should be enabled');
await addSelectedExperience.click();
assert.equal(await page.locator('.experience-picker').count(), 0, 'Smart CV should close automatically after Add selected');
assert.equal(await contextualTrigger.count(), 1, 'closed Smart CV should keep its reopen button');
await page.waitForTimeout(100);
const insertedExperience = await qaExperienceDescription.inputValue();
assert(selectedTexts.some((value) => insertedExperience.includes(value.trim())), 'selected experience descriptions were not inserted');

await contextualTrigger.click(); // Reopen manually to adjust choices or add more items.
await experiencePicker.locator('.experience-picker__search input').fill('monitor');
assert((await experiencePicker.locator('.experience-picker__options article').count()) >= 1, 'experience suggestion search returned no matching options');
await experiencePicker.locator('.experience-picker__search input').fill('');

await qaExperienceDescription.fill((await qaExperienceDescription.inputValue()) + '\nManual custom responsibility');
assert((await qaExperienceDescription.inputValue()).includes('Manual custom responsibility'), 'manual experience description editing was blocked');

await experiencePicker.locator('.experience-picker__heading button').click();
const experienceTrigger = page.locator('.experience-picker-trigger');
assert.equal(await experienceTrigger.count(), 1, 'Experience Pro reopen trigger missing after close');
await experienceTrigger.click();
assert.equal(await page.locator('.experience-picker').count(), 1, 'Experience Pro did not reopen from trigger');
await page.locator('.experience-picker__heading button').click();

// Manual specialty/level edits must survive refocus for the same job.
const qaExperienceRole = page.locator('#qa-experience-role');
await qaExperienceDescription.focus();
await contextualTrigger.click();
await page.locator('.experience-picker__selectors select').nth(0).selectOption('emergency');
await page.locator('.experience-picker__selectors select').nth(1).selectOption('beginner');
await qaExperienceRole.focus();
await qaExperienceDescription.focus();
await contextualTrigger.click();
assert.equal(await page.locator('.experience-picker__selectors select').nth(0).inputValue(), 'emergency', 'manual specialty should survive refocus');
assert.equal(await page.locator('.experience-picker__selectors select').nth(1).inputValue(), 'beginner', 'manual level should survive refocus');

// A new job title should re-enable clinical specialty and leadership-level detection.
await qaExperienceRole.fill('ER Supervisor');
await qaExperienceDescription.focus();
await contextualTrigger.click();
assert.equal(await page.locator('.experience-picker__selectors select').nth(0).inputValue(), 'emergency', 'ER Supervisor should retain ER as the specialty');
assert.equal(await page.locator('.experience-picker__selectors select').nth(1).inputValue(), 'supervisor', 'ER Supervisor should be detected at supervisor level');
await page.locator('.experience-picker__heading button').click();

await page.evaluate(() => document.getElementById('qa-experience-description-field')?.remove());
log('Smart CV advanced nursing suggestions, selection-to-insert auto-close, reopen and manual editing');

assert.equal(await page.locator('.job-tailor, .job-tailor__trigger, .job-tailor__panel').count(), 0, 'Job Match Center must not render');

// Previously saved Job Match data must be cleared without touching other Sirati data.
await page.evaluate(() => {
  localStorage.setItem('sirati.jobTailor.v2.doc.qa-legacy', '{"targetRole":"QA legacy marker"}');
  sessionStorage.setItem('sirati.jobTailor.v2.draft', '{"jobDescription":"QA legacy marker"}');
  localStorage.setItem('sirati.qa.unrelated-keep', 'keep');
});
await page.reload({ waitUntil: 'networkidle' });
await page.waitForFunction(() =>
  !localStorage.getItem('sirati.jobTailor.v2.doc.qa-legacy') &&
  !sessionStorage.getItem('sirati.jobTailor.v2.draft')
);
assert.equal(await page.evaluate(() => localStorage.getItem('sirati.qa.unrelated-keep')), 'keep', 'cleanup must not clear unrelated data');
await page.evaluate(() => localStorage.removeItem('sirati.qa.unrelated-keep'));
assert.equal(await page.locator('.job-tailor').count(), 0, 'Job Match must remain removed after reload');
log('Job Match Center removed; legacy storage cleaned without touching CV data');

assert.equal(await page.locator('details.smart-nursing-library').count(), 0, 'standalone nursing section must be hidden');

// Other professions should get role-specific examples, not the nursing library.
await page.evaluate(() => {
  const field = document.createElement('div');
  field.className = 'field';
  field.id = 'qa-accountant-description-field';
  field.innerHTML = '<label>Job title<input id="qa-accountant-role" value="Accountant"></label><label>Description<textarea id="qa-accountant-description"></textarea></label>';
  document.body.appendChild(field);
});
await page.locator('#qa-accountant-description').focus();
await page.locator('#qa-accountant-description-field .sirati-description-assistant-slot .experience-picker-trigger').click();
const accountantPicker = page.locator('.experience-picker');
assert((await accountantPicker.innerText()).includes('Analyzed ledger reconciliations'), 'advanced accounting examples were not detected');
assert((await accountantPicker.innerText()).includes('Prepared and reconciled financial records'), 'original safe examples should remain accessible');
assert.equal(await accountantPicker.locator('.experience-picker__career-selectors select').count(), 2, 'non-nursing professionals must have specialization and experience-level controls');
assert.equal(await accountantPicker.locator('select[aria-label="Career specialization"]').inputValue(), '', 'broad Accountant should not auto-claim a specialization');
assert.equal(await accountantPicker.locator('select[aria-label="Professional experience level"]').inputValue(), 'experienced', 'default professional career level should be appropriate');
assert.equal(await accountantPicker.locator('.experience-picker__selectors select').count(), 2, 'non-nursing roles must not show nursing-specific selectors');
const accountingBullet = (await accountantPicker.locator('.experience-picker__options article label span').first().innerText()).trim();
await accountantPicker.locator('.experience-picker__options article').first().getByRole('button', { name: '+ Add' }).click();
assert((await page.locator('#qa-accountant-description').inputValue()).includes(accountingBullet), 'accounting example was not inserted');
assert.equal(await page.locator('.experience-picker').count(), 0, 'single + Add should also close Smart CV after insertion');
// Pro V3: senior accountant should auto-select the exact financial track and seniority.
await page.locator('#qa-accountant-role').fill('Senior Financial Accountant');
await page.locator('#qa-accountant-description').focus();
await page.locator('#qa-accountant-description-field .sirati-description-assistant-slot .experience-picker-trigger').click();
assert.equal(await accountantPicker.locator('select[aria-label="Career specialization"]').inputValue(), 'financial-accounting', 'financial accounting track not recognized');
assert.equal(await accountantPicker.locator('select[aria-label="Professional experience level"]').inputValue(), 'senior', 'seniority not detected');
assert((await accountantPicker.innerText()).includes('Investigated general-ledger variances'), 'financial role-specific snippets absent');
assert((await accountantPicker.innerText()).includes('Reviewed complex work outputs'), 'senior-level options absent');
assert(!(await accountantPicker.innerText()).includes('Coordinated workload assignments'), 'manager-only descriptions must not be suggested for senior role');
await accountantPicker.locator('select[aria-label="Professional experience level"]').selectOption('beginner');
assert((await accountantPicker.innerText()).includes('Applied documented procedures'), 'manually selected early-career level not reflected in suggestions');
assert(!(await accountantPicker.innerText()).includes('Reviewed complex work outputs'), 'senior-level suggestions should not leak into early career');
await accountantPicker.locator('.experience-picker__heading button').click();
// Pro V3: frontend title must switch the career domain without reusing accounting.
await page.locator('#qa-accountant-role').fill('Frontend Developer');
await page.locator('#qa-accountant-description').focus();
await page.locator('#qa-accountant-description-field .sirati-description-assistant-slot .experience-picker-trigger').click();
assert.equal(await accountantPicker.locator('select[aria-label="Career specialization"]').inputValue(), 'frontend', 'frontend track not recognized');
assert.equal(await accountantPicker.locator('select[aria-label="Professional experience level"]').inputValue(), 'experienced', 'manually selected previous-role level must reset on role change');
assert((await accountantPicker.innerText()).includes('accessible interface specifications'), 'frontend snippets missing');
assert(!(await accountantPicker.innerText()).includes('general-ledger variances'), 'accounting-specific snippets leaked to developer');
await accountantPicker.locator('.experience-picker__heading button').click();
// A broad software title may choose a precise specialization manually.
await page.locator('#qa-accountant-role').fill('Software Developer');
await page.locator('#qa-accountant-description').focus();
await page.locator('#qa-accountant-description-field .sirati-description-assistant-slot .experience-picker-trigger').click();
assert.equal(await accountantPicker.locator('select[aria-label="Career specialization"]').inputValue(), '', 'broad software role must not auto-claim a track');
await accountantPicker.locator('select[aria-label="Career specialization"]').selectOption('backend');
assert((await accountantPicker.innerText()).includes('Designed API contracts'), 'manual backend specialization not reflected');
await accountantPicker.locator('.experience-picker__heading button').click();
await page.locator('#qa-accountant-role').fill('Unlisted specialty role');
await page.locator('#qa-accountant-description').focus();
await page.locator('#qa-accountant-description-field .sirati-description-assistant-slot .experience-picker-trigger').click();
assert((await page.locator('.experience-picker').innerText()).includes('Organized assigned tasks'), 'unknown job titles need safe fallback examples');
await page.evaluate(() => document.getElementById('qa-accountant-description-field')?.remove());
log('Pro V3 detailed career tracks, professional levels, manual specialization, fallback and no nursing leakage');

// An explicit Continue changes the Builder step and reveals its beginning.
await page.evaluate(() => {
  const original = Element.prototype.scrollIntoView;
  window.__siratiStepScrolls = 0;
  Element.prototype.scrollIntoView = function (...args) {
    if (this.classList.contains('wizard-panel')) window.__siratiStepScrolls++;
    return original.apply(this, args);
  };
});
await page.locator('.field').filter({ hasText: 'Professional title' }).locator('input').first().fill('Emergency Nurse');
log('Professional Title entered once in profile section');
const continueButton = page.getByRole('button', { name: /Continue/ }).last();
await continueButton.click();
await page.waitForFunction(() => window.__siratiStepScrolls > 0);
log('Builder next step is scrolled into view after Continue');
await page.waitForTimeout(100);
assert.equal(await page.locator('details.smart-nursing-library').count(), 0, 'nursing widget must not return after step navigation');
log('guided builder continues without standalone Nursing library');

// Verify real profile Professional Title flows to Summary without retyping it.
const realSummary = page.locator('.wizard-section-card textarea').first(); // stable even after suggestion panel closes
assert.equal(await realSummary.count(), 1, 'actual Personal Summary field must exist');
const realSummaryPanel = page.locator('.sirati-summary-panel');
await realSummaryPanel.waitFor();
assert((await realSummaryPanel.locator('.sirati-summary-context').innerText()).includes('Emergency Nurse'), 'Summary must use Professional Title from earlier wizard step');
assert.equal(await realSummaryPanel.locator('.sirati-summary-choice').count(), 3, 'real Summary must auto-offer 3 templates');
const realSummaryChoice = (await realSummaryPanel.locator('.sirati-summary-choice__text').first().innerText()).trim();
await realSummaryPanel.locator('.sirati-summary-choice').first().click();
const afterSmartChoice = await page.evaluate((selected) => ({
  progress: document.querySelector('.wizard-progress-meta')?.textContent?.trim(),
  summaryMounted: Boolean(document.querySelector('.wizard-section-card textarea')),
  previewUpdated: Boolean(document.querySelector('.cv-sheet')?.textContent?.includes(selected)),
  visibleCardText: document.querySelector('.wizard-section-card')?.textContent?.slice(0,180),
  focus: document.activeElement?.tagName
}), realSummaryChoice);
log('SMART SUMMARY POST-CLICK DIAGNOSTIC ' + JSON.stringify(afterSmartChoice));
assert(afterSmartChoice.summaryMounted, 'Summary field disappeared after choosing a template: ' + JSON.stringify(afterSmartChoice));
assert.equal(await realSummary.inputValue(), realSummaryChoice, 'Summary selection should update controlled field');
await page.waitForFunction(text => document.querySelector('.cv-sheet')?.textContent?.includes(text), realSummaryChoice);
log('Professional Title templates update real Personal Summary, React preview and saved CV');

await page.getByRole('button', { name: '← Back' }).click();
await page.locator('.field').filter({ hasText: 'Full name' }).locator('input').first().fill('QA Sirati Nurse');
await page.waitForTimeout(800);
const readinessScoreAfterName = Number((await page.locator('.cv-readiness__trigger strong').innerText()).replace('%', ''));
assert(readinessScoreAfterName >= 10, 'CV Quality Center did not recognize completed name');
assert.equal(await inlineProgress.getAttribute('aria-valuenow'), String(readinessScoreAfterName), 'anchored progress must match quality score');
log('CV Quality Center score reacts to Builder input');
await page.getByRole('button', { name: 'Continue →' }).click();
await page.waitForTimeout(400);
const qualityAfterStepSwitch = Number((await page.locator('.cv-readiness__trigger strong').innerText()).replace('%', ''));
assert.equal(qualityAfterStepSwitch, readinessScoreAfterName, 'Quality score changed merely because the active wizard step changed');
await page.getByRole('button', { name: '← Back' }).click();
log('CV Quality score remains stable between wizard steps when the CV data is unchanged');
await page.reload({ waitUntil: 'networkidle' });
assert.equal(await page.locator('.field').filter({ hasText: 'Full name' }).locator('input').first().inputValue(), 'QA Sirati Nurse');
assert.equal(await page.locator('.job-tailor').count(), 0);
assert((await page.locator('.cv-sheet').innerText()).includes(realSummaryChoice), 'Personal Summary must survive reload and appear in CV preview');
log('local CV save survives reload with Personal Summary and without Job Match');

// Verify integration with the real controlled Experience field and CV preview.
// Verify integration with the real controlled Experience field and CV preview.
for (let step = 0; step < 2; step++) await page.getByRole('button', { name: /Continue/ }).last().click();
const realExperience = page.locator('.field').filter({ hasText: 'Achievements / responsibilities' }).locator('textarea').first();
await page.locator('.field').filter({ hasText: /^Role$/ }).locator('input').first().fill('Senior ICU Nurse');
await realExperience.fill('Manual responsibility retained during QA.');
const realTrigger = page.locator('.sirati-description-assistant-slot .experience-picker-trigger').last();
await realTrigger.click();
const realPicker = page.locator('.experience-picker');
await realPicker.waitFor();
assert.equal(await realPicker.locator('.experience-picker__selectors select').first().inputValue(), 'icu');
const realOption = realPicker.locator('.experience-picker__options article').first();
const realSuggestion = (await realOption.locator('label span').innerText()).trim();
await realOption.getByRole('button', { name: '+ Add', exact: true }).click();
assert((await realExperience.inputValue()).includes(realSuggestion), 'suggestion must reach the real controlled field');
assert.equal(await page.locator('.experience-picker').count(), 0, 'real Experience Smart CV should auto-close after + Add');
await page.waitForFunction((text) => document.querySelector('.cv-sheet')?.textContent.includes(text), realSuggestion);
assert((await realExperience.inputValue()).includes('Manual responsibility retained during QA.'));
await page.reload({ waitUntil: 'networkidle' });
assert((await page.locator('.cv-sheet').innerText()).includes(realSuggestion), 'inserted experience must survive reload in preview');
log('real Experience insertion updates React state, preview and saved CV');

let templateSelect = null;
const selects = page.locator('select');
for (let i = 0; i < await selects.count(); i++) {
  const values = await optionValues(selects.nth(i));
  if (['modern', 'classic', 'compact', 'compact-ats', 'healthcare-pro', 'executive-ats', 'profile-sidebar', 'gold-sidebar'].every((value) => values.includes(value))) {
    templateSelect = selects.nth(i);
    break;
  }
}
assert(templateSelect, 'template selector not found');

const expectedClasses = {
  modern: 'template-modern',
  classic: 'template-classic',
  compact: 'template-compact',
  'compact-ats': 'template-compact-ats',
  'healthcare-pro': 'template-healthcare-pro',
  'executive-ats': 'template-executive-ats',
  'profile-sidebar': 'template-profile-sidebar',
  'gold-sidebar': 'template-gold-sidebar'
};

for (const [value, expectedClass] of Object.entries(expectedClasses)) {
  await templateSelect.selectOption(value);
  await page.waitForTimeout(70);
  const className = await page.locator('.cv-sheet').getAttribute('class');
  assert(className.includes(expectedClass), value + ' did not render expected class');
  assert.equal(await page.locator('.field').filter({ hasText: 'Full name' }).locator('input').first().inputValue(), 'QA Sirati Nurse');
}
log('switching all eight templates retains CV data');

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
for (const value of ['healthcare-pro', 'executive-ats', 'profile-sidebar', 'gold-sidebar']) {
  await templateSelect.selectOption(value);
  const sheet = page.locator('.cv-sheet');
  assert((await sheet.getAttribute('class')).includes('template-' + value), value + ' RTL design missing');
  assert.equal(await sheet.getAttribute('dir'), 'rtl', value + ' must be RTL in Arabic');
  assert((await sheet.innerText()).includes('QA Sirati Nurse'), value + ' lost CV content on Arabic toggle');
}
assert.equal(await page.locator('details.smart-nursing-library').count(), 0, 'Arabic Builder must not show Nursing-only library');
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

// The inner 9-section progress stays visible while redundant outer onboarding
// is suppressed on narrow screens, leaving more space for input fields.
assert.equal(await page.locator('.wizard-journey-wrap').isVisible(), false,
  'duplicate builder onboarding ribbon must not take mobile space');
assert(await page.locator('.wizard-progress-meta').isVisible(),
  'section progress must remain visible on mobile');

// With Auto-Advance removed, the manual navigation must remain in the page
// on all steps even while a mobile field is focused. It flows BELOW the editor
// while the keyboard is active rather than disappearing.
const guidedNav = page.locator('.builder-guide');
const editorFooterNav = page.locator('.wizard-footer-nav');
async function assertCompactMobileNav(nav, context) {
  const metrics = await nav.evaluate(el => {
    const r = el.getBoundingClientRect();
    const parent = el.parentElement?.getBoundingClientRect();
    const buttons = Array.from(el.querySelectorAll('button')).map(button => {
      const b = button.getBoundingClientRect();
      return {width: b.width, height: b.height, visible: button.getClientRects().length>0};
    });
    return {width:r.width, left:r.left, right:r.right, bottom:r.bottom,
      parentRight:parent?.right, position:getComputedStyle(el).position,
      viewport:window.innerWidth, overflow:document.documentElement.scrollWidth-window.innerWidth,
      buttons};
  });
  assert(metrics.width <= 240 && metrics.width >= 165,
    context + ' must use a compact ~236px navigation cluster: ' + JSON.stringify(metrics));
  assert(metrics.position === 'static', context + ' footer must NOT overlay editable CV content');
  assert(metrics.right <= metrics.viewport + 2 && metrics.left >= -2,
    context + ' footer must stay within the mobile screen');
  assert(metrics.parentRight - metrics.right <= 24 && metrics.parentRight >= metrics.right - 2,
    context + ' compact buttons must align to physical right of their form container');
  assert(metrics.buttons.every(button => button.visible && button.height >= 44 && button.width <= 126),
    context + ' buttons must be compact but retain at least a 44px tap height');
  assert(metrics.overflow <= 2, context + ' must not cause mobile horizontal overflow');
}
const firstMobileEditor = page.locator('.wizard-section-card input:visible, .wizard-section-card textarea:visible').first();
assert(await firstMobileEditor.count(), 'expected an editable CV field on mobile');
// The editor autofocuses its first field. Blur that initial focus to assert
// the guide's normal resting state before testing focus-driven dismissal.
await page.evaluate(() => {
  const active = document.activeElement;
  if (active instanceof HTMLElement) active.blur();
});
await editorFooterNav.waitFor({ state: 'visible', timeout: 10000 });
await assertCompactMobileNav(editorFooterNav, 'unfocused 390px');
assert.equal(await guidedNav.isVisible(), false, 'duplicate guide must not appear over mobile CV editor');
await firstMobileEditor.focus();
assert(await editorFooterNav.isVisible(), 'Continue footer must stay visible when mobile input is focused');
await assertCompactMobileNav(editorFooterNav, 'focused 390px');
assert.equal(await editorFooterNav.evaluate(el => getComputedStyle(el).position), 'static',
  'focused mobile footer must flow below the editor instead of overlaying the keyboard');
await firstMobileEditor.evaluate(el => el.blur());
assert(await editorFooterNav.isVisible(), 'Continue footer must stay visible after editing');

// Capture genuine generated Builder screens at narrow phone widths.
// Images contain synthetic QA data, never live customer content.
await page.screenshot({ path: '/tmp/sirati-qa-pdfs/mobile-builder-390-rest.png', animations: 'disabled' });
await firstMobileEditor.focus();
assert(await editorFooterNav.isVisible(), 'focused mobile form must retain manual Continue and Back');
await page.screenshot({ path: '/tmp/sirati-qa-pdfs/mobile-builder-390-focused.png', animations: 'disabled' });
await firstMobileEditor.evaluate(el => el.blur());
await page.setViewportSize({ width: 320, height: 700 });
assert.equal(await page.locator('.wizard-journey-wrap').isVisible(), false,
  'duplicate onboarding must remain hidden at 320px');
const smallOverflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
assert(smallOverflow <= 2, '320px builder overflow=' + smallOverflow);
await assertCompactMobileNav(editorFooterNav, 'unfocused 320px');
await page.screenshot({ path: '/tmp/sirati-qa-pdfs/mobile-builder-320-rest.png', animations: 'disabled' });
await page.setViewportSize({ width: 390, height: 844 });
log('mobile focus mode: visible manual footer snapshots at 320px, 390px focused/unfocused');

// Regression for missing Continue/Back on selected CV sections.
// Use the existing section navigator on desktop to reach all 9 sections, then
// verify navigation is not hidden by either an unfocused or focused mobile editor.
assert.equal(await page.locator('.cv-substep').count(), 9, 'expected all nine Builder sections');
for (let stepNumber = 0; stepNumber < 9; stepNumber++) {
  await page.setViewportSize({width:1440, height:1000});
  await page.locator('.cv-substep').nth(stepNumber).click();
  await page.setViewportSize({width:390,height:844});
  const nav = page.locator('.wizard-footer-nav');
  assert(await nav.isVisible(), 'manual navigation missing on mobile Section '+(stepNumber+1));
  await assertCompactMobileNav(nav, 'Section '+(stepNumber+1)+' unfocused');
  const navButtons = nav.locator('button');
  assert(await navButtons.count() >= 1, 'no manual navigation buttons in Section '+(stepNumber+1));
  assert(await nav.getByRole('button', {name:/Back/i}).isVisible(),
    'Back button missing on mobile Section '+(stepNumber+1));
  if(stepNumber < 8) {
    assert(await nav.getByRole('button', {name:/Continue|Next/i}).isVisible(),
      'Continue button missing on mobile Section '+(stepNumber+1));
  }
  const editor = page.locator('.wizard-section-card input:visible, .wizard-section-card textarea:visible, .wizard-section-card select:visible').first();
  if(await editor.count()) {
    await editor.focus();
    assert(await nav.isVisible(), 'manual navigation disappeared on input focus at Section '+(stepNumber+1));
    await assertCompactMobileNav(nav, 'Section '+(stepNumber+1)+' focused');
    await editor.evaluate(el=>el.blur());
  }
  const overflowAtStep = await page.evaluate(() => document.documentElement.scrollWidth-window.innerWidth);
  assert(overflowAtStep <= 2, 'mobile navigation overflow at Section '+(stepNumber+1)+': '+overflowAtStep);
}
await page.setViewportSize({width:390,height:844});
log('Continue/Back remain visible across all nine mobile Builder sections, including focused inputs');

let mobileTemplateSelect = null;
const mobileSelects = page.locator('select');
for (let i = 0; i < await mobileSelects.count(); i++) {
  const values = await optionValues(mobileSelects.nth(i));
  if (['modern', 'classic', 'compact', 'compact-ats', 'healthcare-pro', 'executive-ats', 'profile-sidebar', 'gold-sidebar'].every((value) => values.includes(value))) {
    mobileTemplateSelect = mobileSelects.nth(i);
    break;
  }
}
assert(mobileTemplateSelect, 'mobile template selector not found');

for (const value of ['modern', 'classic', 'compact', 'compact-ats', 'healthcare-pro', 'executive-ats', 'profile-sidebar', 'gold-sidebar']) {
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
assert.equal(await mobileReadiness.evaluate((el) => getComputedStyle(el).position), 'relative', 'mobile quality must not float over form');
assert.equal(await page.locator('.job-tailor').count(), 0, 'removed Job Match must not return on mobile');
log('mobile overflow check for all eight templates, readiness and removed Job Match');

await mobileTemplateSelect.selectOption('compact-ats');
assert.equal(await page.locator('details.smart-nursing-library').count(), 0, 'mobile Builder must hide standalone Nursing widget');
await page.evaluate(() => {
  const field = document.createElement('div');
  field.id = 'qa-mobile-career-field';
  field.className = 'field';
  field.innerHTML = '<label>Job title<input value="Sales Representative"></label><label>Description<textarea></textarea></label>';
  document.body.appendChild(field);
});
await page.locator('#qa-mobile-career-field textarea').focus();
await page.locator('#qa-mobile-career-field .sirati-description-assistant-slot .experience-picker-trigger').click();
const mobileCareerPanel = page.locator('.experience-picker');
const mobileCareerRect = await mobileCareerPanel.evaluate(el => el.getBoundingClientRect());
assert(mobileCareerRect.left >= -2 && mobileCareerRect.right <= 392, 'contextual mobile panel overflows');
assert((await mobileCareerPanel.innerText()).includes('Qualified opportunities'), 'advanced sales suggestions should load on mobile');
assert.equal(await mobileCareerPanel.locator('select[aria-label="Career specialization"]').inputValue(), 'retail-sales', 'Sales Representative specialization not detected on mobile');
assert.equal(await mobileCareerPanel.locator('select[aria-label="Professional experience level"]').inputValue(), 'experienced', 'mobile experience level missing');
assert((await mobileCareerPanel.innerText()).includes('Identified customer requirements'), 'original sales suggestions should remain available');
await page.evaluate(() => document.getElementById('qa-mobile-career-field')?.remove());
log('mobile role-specific descriptions stay inline and within viewport');

await page.setViewportSize({ width: 1440, height: 1000 });
await page.goto(base + '/builder/?template=modern&language=en', { waitUntil: 'networkidle' });
await page.locator('.field').filter({ hasText: 'Full name' }).locator('input').first().fill('QA Sirati Nurse');

let printTemplateSelect = null;
const printSelects = page.locator('select');
for (let i = 0; i < await printSelects.count(); i++) {
  const values = await optionValues(printSelects.nth(i));
  if (['modern', 'classic', 'compact', 'compact-ats', 'healthcare-pro', 'executive-ats', 'profile-sidebar', 'gold-sidebar'].every((value) => values.includes(value))) {
    printTemplateSelect = printSelects.nth(i);
    break;
  }
}
assert(printTemplateSelect);

fs.mkdirSync('/tmp/sirati-qa-pdfs', { recursive: true });
for (const value of ['modern', 'classic', 'compact', 'compact-ats', 'healthcare-pro', 'executive-ats', 'profile-sidebar', 'gold-sidebar']) {
  await printTemplateSelect.selectOption(value);
  await page.waitForTimeout(70);
  const path = '/tmp/sirati-qa-pdfs/' + value + '.pdf';
  await page.pdf({ path, format: 'A4', printBackground: true, preferCSSPageSize: true });
  const size = fs.statSync(path).size;
  assert(size > 5000, value + ' PDF too small: ' + size);
}
log('print/PDF smoke test for all eight templates');

// Exercise the existing photo upload end-to-end on the seventh template.
await page.setViewportSize({ width: 1440, height: 1000 });
await page.goto(base + '/builder/?template=profile-sidebar&language=en', { waitUntil: 'networkidle' });
// A saved local draft can be the currently active selection in the Builder,
// even if a direct URL has a template query. Select explicitly for this test.
let profileTemplateSelect = null;
for (const control of await page.locator('select').all()) {
  const values = await optionValues(control);
  if (values.includes('profile-sidebar') && values.includes('gold-sidebar')) {
    profileTemplateSelect = control;
    break;
  }
}
assert(profileTemplateSelect, 'Profile Sidebar must be selectable from the Builder');
await profileTemplateSelect.selectOption('profile-sidebar');
const sidebarPaper = page.locator('.wizard-preview-wrap .cv-sheet.template-profile-sidebar');
assert.equal(await sidebarPaper.count(), 1, 'Profile Sidebar should be selected from builder URL');
assert.equal(await sidebarPaper.locator('.profile-sidebar-layout > .profile-sidebar-rail').count(), 1);
assert.equal(await sidebarPaper.locator('.profile-sidebar-portrait-placeholder').count(), 1);
const photoInput = page.locator('.photo-upload-row input[type="file"]').first();
assert.equal(await photoInput.count(), 1, 'existing professional photo uploader must be available');
await photoInput.setInputFiles({
  name: 'qa-placeholder.png',
  mimeType: 'image/png',
  buffer: Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jQ1sAAAAASUVORK5CYII=', 'base64')
});
await sidebarPaper.locator('img.profile-sidebar-portrait').waitFor({ timeout: 8000 });
assert.equal(await sidebarPaper.locator('.profile-sidebar-portrait-placeholder').count(), 0);
const uploadedImage = await sidebarPaper.locator('img.profile-sidebar-portrait').getAttribute('src');
assert(uploadedImage?.startsWith('data:image/jpeg;base64,'), 'uploaded portrait must be compressed with existing local image flow');
assert.equal(await sidebarPaper.locator('.profile-sidebar-layout > .profile-sidebar-main').count(), 1);
log('Profile Sidebar uses existing photo upload and renders uploaded portrait');

const imageStyle = await sidebarPaper.locator('img.profile-sidebar-portrait').evaluate(image => {
  const photo = image.getBoundingClientRect();
  const wrap = image.closest('.profile-sidebar-portrait-wrap')?.getBoundingClientRect();
  const rail = image.closest('.profile-sidebar-rail')?.getBoundingClientRect();
  const css = getComputedStyle(image);
  return {width:photo.width, height:photo.height, borderRadius:css.borderRadius,
    objectFit:css.objectFit, objectPosition:css.objectPosition,
    centered: wrap ? Math.abs((photo.left+photo.right)/2-(wrap.left+wrap.right)/2) : 999,
    insideRail: Boolean(rail && photo.left >= rail.left && photo.right <= rail.right)};
});
assert(Math.abs(imageStyle.width - imageStyle.height) <= 2, 'headshot frame must use a square 1:1 crop');
assert.equal(imageStyle.borderRadius, '50%', 'headshot should be a circle');
assert.equal(imageStyle.objectFit, 'cover', 'headshot needs crop-to-fill, not distorted stretch');
assert(imageStyle.objectPosition.includes('30%'), 'headshot needs portrait-friendly face position');
assert(imageStyle.centered <= 2 && imageStyle.insideRail, 'portrait frame must align within left sidebar');
await sidebarPaper.screenshot({path:'/tmp/sirati-qa-pdfs/profile-sidebar-uploaded-photo-desktop.png'});
log('Profile Sidebar portrait is centered, circular and crop-to-fill without distortion');

await page.emulateMedia({media: 'print'});
const printStyle = await sidebarPaper.locator('img.profile-sidebar-portrait').evaluate(img => ({
  width:img.getBoundingClientRect().width, height:img.getBoundingClientRect().height,
  radius:getComputedStyle(img).borderRadius,
  railBackground:getComputedStyle(img.closest('.profile-sidebar-rail')).backgroundColor
}));
assert(Math.abs(printStyle.width-printStyle.height) <= 2, 'A4 print portrait must be square');
assert.equal(printStyle.radius, '50%', 'A4 print portrait should be circular');
assert.notEqual(printStyle.railBackground, 'rgba(0, 0, 0, 0)', 'A4 sidebar must have a visible background');
await page.emulateMedia({media: 'screen'});
log('Profile Sidebar circular crop and dark rail are retained in print media');


await page.reload({ waitUntil: 'networkidle' });
const sidebarAfterReload = page.locator('.wizard-preview-wrap .cv-sheet.template-profile-sidebar');
assert.equal(await sidebarAfterReload.locator('img.profile-sidebar-portrait').count(), 1, 'photo must survive existing draft restore');
log('Profile Sidebar photo and selected template survive reload');

await page.setViewportSize({width:390, height:844});
await page.waitForTimeout(100);
const mobilePortrait = await sidebarAfterReload.locator('img.profile-sidebar-portrait').evaluate(img => {
  const p=img.getBoundingClientRect();
  const rail=img.closest('.profile-sidebar-rail').getBoundingClientRect();
  return {w:p.width,h:p.height,inRail:p.left >= rail.left-1 && p.right <= rail.right+1,
    overflow:document.documentElement.scrollWidth-window.innerWidth};
});
assert(Math.abs(mobilePortrait.w-mobilePortrait.h) <= 2, 'mobile portrait should stay circular/square');
assert(mobilePortrait.inRail, 'mobile portrait should remain inside rail');
assert(mobilePortrait.overflow <= 2, 'mobile portrait causes page overflow: '+mobilePortrait.overflow);
await sidebarAfterReload.screenshot({path:'/tmp/sirati-qa-pdfs/profile-sidebar-mobile.png'});
log('Profile Sidebar mobile circular portrait stays inside rail without horizontal overflow');


// Gold Sidebar must reuse the same account-local photo & existing CV data without
// creating another data field or losing any content on template switching.
await page.setViewportSize({width:1440, height:1000});
let goldTemplateSelect = null;
for(const control of await page.locator('select').all()){
  const values = await optionValues(control);
  if(values.includes('gold-sidebar') && values.includes('profile-sidebar')){goldTemplateSelect = control;break;}
}
assert(goldTemplateSelect, 'the eighth template must be present in Builder selector');
await goldTemplateSelect.selectOption('gold-sidebar');
const goldPaper = page.locator('.wizard-preview-wrap .cv-sheet.template-gold-sidebar');
assert.equal(await goldPaper.count(),1,'Gold Sidebar must render when selected');
assert.equal(await goldPaper.locator('.gold-sidebar-rail .gold-sidebar-portrait').count(),1,'existing uploaded picture should be displayed on Gold Sidebar');
const goldPhotoStyle=await goldPaper.locator('img.gold-sidebar-portrait').evaluate(img=>{
  const p=img.getBoundingClientRect();
  const r=img.closest('.gold-sidebar-rail').getBoundingClientRect();
  return {width:p.width,height:p.height,fit:getComputedStyle(img).objectFit,
    rounded:getComputedStyle(img).borderRadius,inside:p.left>=r.left&&p.right<=r.right}
});
assert(goldPhotoStyle.width>0 && goldPhotoStyle.height>0 && goldPhotoStyle.inside,'photo should fit inside the Gold rail');
assert.equal(goldPhotoStyle.fit,'cover','portrait should crop rather than stretch');
assert(goldPhotoStyle.rounded.includes('px'),'Gold photo should use a distinctive portrait frame');
await goldPaper.screenshot({path:'/tmp/sirati-qa-pdfs/gold-sidebar-uploaded-desktop.png'});
await page.reload({waitUntil:'networkidle'});
assert.equal(await page.locator('.cv-sheet.template-gold-sidebar img.gold-sidebar-portrait').count(),1,'Gold Sidebar and its photo should survive draft reload');
log('Gold Sidebar shares existing uploaded photo and remains selected after reload');

await page.setViewportSize({width:390,height:844});
const goldMobile = await page.locator('.cv-sheet.template-gold-sidebar').evaluate(sheet=>{
  const r=sheet.querySelector('.gold-sidebar-portrait-wrap').getBoundingClientRect();
  const rail=sheet.querySelector('.gold-sidebar-rail').getBoundingClientRect();
  return {inside:r.left>=rail.left-1&&r.right<=rail.right+1,
    overflow:document.documentElement.scrollWidth-window.innerWidth};
});
assert(goldMobile.inside,'Gold Sidebar photo must stay within mobile rail');
assert(goldMobile.overflow<=2,'Gold Sidebar must not overflow narrow screen');
await page.locator('.cv-sheet.template-gold-sidebar').screenshot({path:'/tmp/sirati-qa-pdfs/gold-sidebar-mobile.png'});
log('Gold Sidebar narrow mobile render preserves portrait alignment and page width');

// Regression: Auto-Advance has been removed at the customer's request.
// Completing a field must never click Next. Manual Continue/Back must still work.
await page.goto(base + '/builder/?template=modern&language=en', {waitUntil:'networkidle'});
await page.locator('.cv-substep').first().click();
assert.equal(await page.locator('.sirati-auto-advance-control').count(), 0, 'removed Auto-Advance UI must not render');
assert.equal(await page.getByRole('checkbox', {name:'Auto-advance completed CV sections'}).count(), 0, 'old toggle must be removed');
const currentStep = () => page.locator('.wizard-progress-meta > span').first().textContent();
const field = (label) => page.locator('.wizard-section-card .field')
  .filter({has:page.locator('label', {hasText:label})}).locator('input,textarea').first();
await field('Full name').fill('Manual Navigation QA');
await field('Professional title').fill('Registered Nurse');
await field('Email').fill('not-an-email');
await field('Phone').fill('');
await field('LinkedIn / professional link').fill('https://example.com/profile');
await field('City & country').fill('Cairo, Egypt');
await field('LinkedIn / professional link').blur();
await page.waitForTimeout(700);
assert((await currentStep()).includes('Section 1 of 9'), 'invalid data must not change the CV step');
await field('Email').fill('qa@example.com');
await field('LinkedIn / professional link').fill('https://example.com/profile-updated');
await field('LinkedIn / professional link').blur();
await page.waitForTimeout(850);
assert((await currentStep()).includes('Section 1 of 9'), 'completed form and blur must not auto-advance anymore');
log('Auto-Advance removed: completed personal information does not advance without Continue');

await page.locator('.wizard-footer-nav button').filter({hasText:/Continue|Next step/i}).first().click();
await page.waitForFunction(() => document.querySelector('.wizard-progress-meta')?.textContent?.includes('Section 2 of 9'));
const profileEditor = page.locator('.wizard-section-card textarea').first();
await profileEditor.fill('Emergency nursing professional focused on timely assessment, communication and patient safety.');
await profileEditor.blur();
await page.waitForTimeout(850);
assert((await currentStep()).includes('Section 2 of 9'), 'completed summary must remain in the same section without Continue');
await page.locator('.wizard-footer-nav button').filter({hasText:/Continue|Next step/i}).first().click();
await page.waitForFunction(() => document.querySelector('.wizard-progress-meta')?.textContent?.includes('Section 3 of 9'));
await page.getByRole('button', {name:'← Back'}).click();
assert((await currentStep()).includes('Section 2 of 9'), 'manual Back must remain available');
log('Manual Continue and Back still change steps; completion alone does not');

await page.setViewportSize({width:390,height:844});
// The editor now preserves manual navigation even while focused; completing a
// mobile field must not restore the removed Auto-Advance behavior.
assert.equal(await page.locator('.sirati-auto-advance-control').count(), 0, 'Auto-Advance toggle must remain removed on mobile');
await profileEditor.fill('A completed summary can be reviewed manually on mobile without moving to a different CV section.');
await profileEditor.blur();
await page.waitForTimeout(800);
assert((await currentStep()).includes('Section 2 of 9'), 'mobile completed field must not auto-advance');
const mobileFlowOverflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
assert(mobileFlowOverflow <= 2, 'mobile removal must not introduce horizontal overflow: ' + mobileFlowOverflow);
log('Auto-Advance remains absent on 390px mobile and section does not change on blur');
await page.setViewportSize({width:1440,height:1000});

await page.locator('.cv-substep').last().click();
assert((await currentStep()).includes('Section 9 of 9'), 'review/payment remains manually reachable');
const paymentInput = page.locator('.manual-payment-card input').first();
if (await paymentInput.count()) {
  await paymentInput.fill('QA_TEST_ONLY');
  await paymentInput.blur();
  await page.waitForTimeout(700);
}
assert((await currentStep()).includes('Section 9 of 9'), 'payment/review must never automatically submit or navigate');
log('Review/payment remains manual and unchanged');
    
await browser.close();
console.log('E2E QA COMPLETE');

