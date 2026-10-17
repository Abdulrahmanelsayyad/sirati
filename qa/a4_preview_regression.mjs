// Real local Builder renderers, synthetic CV only; never contact a backend.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { chromium } from 'playwright';
const base = process.env.SIRATI_PREVIEW_BASE_URL || 'http://127.0.0.1:4173/sirati';
assert(['127.0.0.1', 'localhost'].includes(new URL(base).hostname));
const browser = await chromium.launch({headless:true});
const results = [];
try {
  const context = await browser.newContext({viewport:{width:1440,height:1000}});
  await context.route('**/*', route => new URL(route.request().url()).origin === new URL(base).origin
    ? route.continue() : route.abort());
  const page = await context.newPage();
  await page.goto(base + '/builder/', {waitUntil:'networkidle'});
  const template = page.getByLabel('Template', {exact:true});
  const language = page.getByLabel('CV language', {exact:true});
  await template.selectOption('compact-ats');
  await page.getByLabel('Full name', {exact:true}).fill('Synthetic A4 QA');
  await page.getByLabel('Professional title', {exact:true}).fill('Accountant');
  await page.locator('.cv-substep').nth(1).click();
  await page.getByLabel('Profile summary', {exact:true}).fill('Synthetic short profile.');
  const templates = await template.locator('option').evaluateAll(options => options.map(o => o.value));
  // Compact ATS first so the baseline fails on the originally reported case.
  templates.sort((a,b) => a === 'compact-ats' ? -1 : b === 'compact-ats' ? 1 : a.localeCompare(b));
  for (const name of templates) {
    await template.selectOption(name);
    for (const lang of ['en','ar']) {
      await language.selectOption(lang);
      for (const width of [390,320,360,720,721,980,1440]) {
        await page.setViewportSize({width,height:1000});
        await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
        const state = await page.locator('.wizard-preview-wrap .cv-sheet').evaluate(el => {
          const rect = el.getBoundingClientRect(), stage = el.parentElement;
          return {width:el.offsetWidth,height:el.offsetHeight,dir:el.getAttribute('dir'),
            minHeight:getComputedStyle(el).minHeight,shownWidth:rect.width,shownHeight:rect.height,
            stageWidth:stage.clientWidth,text:el.textContent};
        });
        results.push({template:name,language:lang,viewport:width,...state,text:undefined});
        const label = name + '/' + lang + '/' + width;
        assert(state.width >= 793 && state.width <= 795, label + ': paper width');
        assert(state.height >= 1122, label + ': collapsed A4 height: ' + state.height);
        assert(state.shownHeight / state.shownWidth >= 1.41, label + ': displayed A4 ratio');
        assert(state.shownWidth <= state.stageWidth + 2, label + ': horizontal preview overflow');
        assert.equal(state.dir, lang === 'ar' ? 'rtl' : 'ltr', label + ': direction');
        assert(state.text.includes('Synthetic A4 QA'), label + ': CV text lost');
      }
    }
  }
  await template.selectOption('compact-ats');
  for (const lang of ['en','ar']) {
    await language.selectOption(lang);
    const longText = Array(600).fill(lang === 'ar' ? 'نص تجريبي للتحقق من امتداد المعاينة.' : 'Synthetic long profile must grow beyond one page.').join('\n');
    await page.getByLabel('Profile summary', {exact:true}).fill(longText);
    for (const width of [390,1440]) {
      await page.setViewportSize({width,height:1000});
      const sheet = page.locator('.wizard-preview-wrap .cv-sheet');
      await page.waitForFunction(() => document.querySelector('.wizard-preview-wrap .cv-sheet').offsetHeight > 1123);
      const state = await sheet.evaluate(el => ({height:el.offsetHeight,scrollHeight:el.scrollHeight}));
      assert(state.scrollHeight <= state.height + 2, 'Long CV must grow without clipping');
    }
  }
  console.log(`PASS: ${results.length} short-CV renders, ${templates.length} templates, EN/AR, seven widths; long CV grows at mobile/desktop.`);
} finally {
  if (process.env.SIRATI_PREVIEW_EVIDENCE) fs.writeFileSync(process.env.SIRATI_PREVIEW_EVIDENCE, JSON.stringify(results,null,2));
  await browser.close();
}
