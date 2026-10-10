import assert from 'node:assert/strict';
import { mkdirSync } from 'node:fs';

// V13 replaces the V2's long homepage preview with three compact template cards.
// Keep the original screenshot workflow, now validating the current homepage.
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
    assert.match(await page.locator('.marketing-hero h1').innerText(), /Build a CV/);
    assert.equal(await page.locator('.marketing-hero .sirati-v2-paper').count(), 0,
      'V13 must not ship a redundant enormous CV sample');
    assert.equal(await page.locator('.home-quickstart,.sirati-studio').count(), 0,
      'Duplicate workflow walkthrough should remain absent');
    assert.equal(await page.locator('.template-showcase').count(), 1,
      'Three-template showcase missing');
    assert.equal(await page.locator('.template-showcase .template-card').count(), 3,
      'V13 must keep the three existing preview styles');
    assert.equal(await page.locator('.marketing-page > section').count(), 5,
      'V13 five-section structure changed');
    const heroRect = await page.locator('.marketing-hero').boundingBox();
    assert(heroRect && heroRect.width <= width + 1 && heroRect.height > 100,
      'V13 compact hero does not fit viewport at ' + width);
    const overflow = await page.evaluate(() =>
      document.documentElement.scrollWidth - document.documentElement.clientWidth);
    assert(overflow <= 2, 'V13 horizontal overflow at ' + width + 'px: ' + overflow);
    const cvButton = page.locator('.marketing-hero .hero-actions a').first();
    assert(await cvButton.isVisible(), 'Primary CV creation CTA hidden at ' + width);
    assert.match(await cvButton.innerText(), /Create My CV/);
    assert.match((await cvButton.getAttribute('href')) || '', /templates/);
    if (width === 320 || width === 390 || width === 1440) {
      await page.locator('.marketing-hero').screenshot({
        path: out + '/editorial-hero-' + width + '.png',
        animations: 'disabled'
      });
    }
    console.log('PASS: V13 minimal homepage at ' + width + 'px');
  }
} finally {
  await browser.close();
}
console.log('V13 MINIMAL HOMEPAGE VISUAL QA COMPLETE');
