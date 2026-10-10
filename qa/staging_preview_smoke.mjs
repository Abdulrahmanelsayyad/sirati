import assert from 'node:assert/strict';
import { chromium } from 'playwright';

// This is a no-credentials staging browser boot/auth gate smoke test.
// It DOES NOT claim approval/payment authorization or clean PDF export passes.
const base = 'http://127.0.0.1:4173/sirati';
const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });

  for (const path of ['/auth/', '/templates/', '/builder/']) {
    const response = await page.goto(base + path, { waitUntil: 'networkidle' });
    assert(response && response.status() < 400, path + ' returned an HTTP error');
    await page.waitForTimeout(350);

    const actual = new URL(page.url());
    assert.equal(actual.origin, 'http://127.0.0.1:4173', 'unexpected remote redirect');
    assert(actual.pathname.startsWith('/sirati/'), 'left the staging app basePath');

    const cards = await page.locator('.template-choice').count();
    const hasAuthForm = (await page.locator('input[type="password"]').count()) > 0
      || (await page.locator('input[type="email"]').count()) > 0;
    const onAuth = actual.pathname.includes('/auth');
    const hasBuilder = (await page.locator('.wizard-panel').count()) > 0;

    console.log('INFO:', path, 'landed on', actual.pathname,
      'cards=', cards, 'auth=', onAuth || hasAuthForm, 'builder=', hasBuilder);
    assert(
      cards > 0 || hasAuthForm || onAuth || hasBuilder,
      path + ' shows neither templates, builder nor authentication; investigate blank page'
    );

    if (path === '/auth/') {
      assert(onAuth || hasAuthForm, 'auth page was not accessible');
    }
  }
  // Exercise the actual generated analytics route in the isolated Staging
  // Playwright browser, without fetching any private owner data or credentials.
  const analytics = await page.goto(base + '/analytics/', { waitUntil: 'domcontentloaded' });
  assert(analytics && analytics.status() < 400, 'analytics route unavailable in staging build');
  await page.getByRole('heading', { name: /Site Analytics/ }).waitFor({ timeout: 15000 });
  const accessAlert = page.getByRole('alert').filter({ hasText: /Sign in required|يلزم تسجيل الدخول|Owner access only|مخصصة للمالك/ });
  await accessAlert.waitFor({ timeout: 15000 });
  const denied = await accessAlert.innerText();
  assert.match(denied, /Sign in required|يلزم تسجيل الدخول|Owner access only|مخصصة للمالك/,
    'an unauthenticated visitor did not receive an owner-access denial');
  assert.equal(await page.getByText('Page views · مشاهدات الصفحات').count(), 0,
    'an unauthenticated visitor can see owner metric cards');
  console.log('PASS: staging /analytics loads and denies unauthenticated browser');
  console.log('NOT RUN: signed-in owner versus signed-in non-owner browser sessions');

  console.log('PASS: staging app loads and its login/preview routes are reachable');
  console.log('NOT RUN: signed-in payment reference -> approval -> clean PDF unlock');
} finally {
  await browser.close();
}
