import assert from 'node:assert/strict';
import { mkdirSync } from 'node:fs';

const { chromium } = await import('playwright');
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
const origin = 'http://127.0.0.1:4173/sirati/';
const out = '/tmp/sirati-premium-editorial-v2';
mkdirSync(out, { recursive: true });

try {
  for (const width of [320, 390, 768, 1440]) {
    await page.setViewportSize({ width, height: width > 1000 ? 900 : 844 });
    await page.goto(origin, { waitUntil: 'networkidle' });

    assert.equal(await page.locator('.marketing-hero .sirati-v2-paper').count(), 1,
      'Readable CV preview missing');
    assert.match(await page.locator('.marketing-hero h1').innerText(), /A CV that looks/);
    assert.equal(await page.locator('.home-quickstart').count(), 0,
      'Duplicate three-step strip remained on landing page');
    assert.equal(await page.locator('.sirati-studio').count(), 0,
      'Duplicate Studio steps remained on landing page');
    assert.equal(await page.locator('.template-showcase').count(), 1,
      'Existing CV templates section disappeared');
    assert.equal(await page.locator('.marketing-hero .sirati-v2-paper').getByText('EXAMPLE CV').count(), 1,
      'Sample nature of preview not disclosed');

    const previewRect = await page.locator('.marketing-hero .sirati-v2-preview-frame').boundingBox();
    assert(previewRect && previewRect.width > 240 && previewRect.width <= width + 1,
      'Document preview does not fit at ' + width + 'px');

    const overflow = await page.evaluate(() =>
      document.documentElement.scrollWidth - document.documentElement.clientWidth);
    assert(overflow <= 2, 'Landing has horizontal overflow at ' + width + 'px: ' + overflow);
    assert(await page.locator('.marketing-hero .hero-actions a').first().isVisible(),
      'Main CV creation CTA is hidden at ' + width + 'px');

    const bodyText = await page.locator('.sirati-v2-paper').innerText();
    for (const name of ['Alex Morgan', 'PROFILE', 'EXPERIENCE', 'EDUCATION', 'SKILLS'])
      assert(bodyText.includes(name), 'Missing readable CV sample section: ' + name);

    if (width === 320 || width === 390 || width === 1440) {
      await page.locator('.marketing-hero').screenshot({
        path: out + '/editorial-hero-' + width + '.png',
        animations: 'disabled'
      });
    }
    console.log('PASS: Premium Editorial V2 visual layout at ' + width + 'px');
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(origin, { waitUntil: 'networkidle' });
  const link = page.locator('.marketing-hero .hero-actions a').first();
  const href = await link.getAttribute('href');
  assert(href && /templates/.test(href), 'Main CTA must lead to CV templates');
  console.log('PASS: homepage start action points to templates');
} finally {
  await browser.close();
}
console.log('PREMIUM EDITORIAL V2 QA COMPLETE');
