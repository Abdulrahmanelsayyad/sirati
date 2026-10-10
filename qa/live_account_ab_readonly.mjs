// Optional independent QA gate: two synthetic accounts, one browser profile.
// The script performs no CV writes, SQL, payments or production configuration changes.
// No secrets, real CV fields, tokens, screenshots, traces or private markers are logged.
import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const required = [
  'SIRATI_AB_BASE_URL', 'SIRATI_AB_A_EMAIL', 'SIRATI_AB_A_PASSWORD',
  'SIRATI_AB_B_EMAIL', 'SIRATI_AB_B_PASSWORD', 'SIRATI_AB_A_DOC_ID',
  'SIRATI_AB_A_TITLE', 'SIRATI_AB_B_TITLE', 'SIRATI_AB_A_MARKER',
];
const missing = required.filter(key => !process.env[key]);
if (missing.length) {
  console.log('NOT RUN: dedicated A/B fixtures and credentials must be supplied locally or securely.');
  console.log('Missing environment variable names: ' + missing.join(', '));
  process.exit(2);
}

const base = new URL(process.env.SIRATI_AB_BASE_URL);
const production = base.origin === 'https://abdulrahmanelsayyad.github.io';
const local = ['127.0.0.1', 'localhost'].includes(base.hostname)
  && base.protocol === 'http:';
assert(base.pathname === '/sirati/', 'Expected the exact /sirati/ base path');
assert(production || local, 'Only the verified Sirati domain or local staging is allowed');
assert(!production || process.env.SIRATI_AB_ALLOW_PRODUCTION === 'YES',
  'Explicit opt-in required for testing the production site');
assert(process.env.SIRATI_AB_A_EMAIL !== process.env.SIRATI_AB_B_EMAIL,
  'Use two different dedicated test accounts');
const docId = process.env.SIRATI_AB_A_DOC_ID;
assert(/^[0-9a-f-]{36}$/i.test(docId), 'Fixture A document ID must be a UUID');
const marker = process.env.SIRATI_AB_A_MARKER;
assert(marker.length >= 10, 'Use a distinctive non-sensitive A-only marker');
// Prefer the newest sitewide menu route, but allow the My Documents route as a
// separate regression. Each run uses one pre-existing synthetic A/B fixture pair.
const signOutPath = process.env.SIRATI_AB_SIGNOUT_PATH || 'menu';
assert(['menu', 'documents'].includes(signOutPath),
  'SIRATI_AB_SIGNOUT_PATH must be menu or documents');
const viewportWidth = Number(process.env.SIRATI_AB_VIEWPORT_WIDTH || 390);
assert([360, 390, 1440].includes(viewportWidth),
  'Use an explicitly supported QA viewport: 360, 390 or 1440');

const report = [];
const record = (name, status, reason = '') => {
  report.push({ name, status, reason });
  console.log(status + ': ' + name + (reason ? ' — ' + reason : ''));
};
const path = segment => new URL(segment, base).href;
const timeout = 25000;
const browser = await chromium.launch({headless: process.env.SIRATI_AB_HEADED !== 'YES'});
try {
  const context = await browser.newContext({viewport: {width: viewportWidth, height: 844}});
  const page = await context.newPage();
  const safeVisibleText = async () => page.locator('body').innerText();
  const anyVisibleFieldContains = async value => page.evaluate(value => {
    const content = document.body?.innerText || '';
    return content.includes(value) || Array.from(
      document.querySelectorAll('input:not([type=password]),textarea')
    ).some(element => element.value?.includes(value));
  }, value);
  const waitForMarker = value => page.waitForFunction(value => {
    return document.body?.innerText?.includes(value) || Array.from(
      document.querySelectorAll('input:not([type=password]),textarea')
    ).some(element => element.value?.includes(value));
  }, value, {timeout});

  async function signIn(email, password) {
    await page.goto(path('auth/?next=/documents'), {waitUntil: 'domcontentloaded'});
    await page.locator('input[type=email]').fill(email);
    await page.locator('input[type=password]').fill(password);
    await page.locator('form button').first().click();
    await page.waitForURL(/\/documents\/?(?:\?|$)/, {timeout});
    await page.locator('.documents-section').waitFor({timeout});
    await page.locator('.document-grid .document-card').first().waitFor({timeout});
  }

  let originalKey = null;
  try {
    await signIn(process.env.SIRATI_AB_A_EMAIL, process.env.SIRATI_AB_A_PASSWORD);
    await page.locator('.document-card')
      .filter({hasText: process.env.SIRATI_AB_A_TITLE}).first().waitFor({timeout});
    record('A can view own pre-existing synthetic document', 'PASS');
    await page.goto(path('builder/?doc=' + encodeURIComponent(docId)), {waitUntil:'domcontentloaded'});
    await waitForMarker(marker);
    record('A can open own existing document with A-only marker', 'PASS');
    try {
      await page.waitForFunction(marker => Object.keys(localStorage).some(key =>
        key.startsWith('sirati.cv.v2.') && (localStorage.getItem(key) || '').includes(marker)),
        marker, {timeout:8000});
      originalKey = await page.evaluate(marker => Object.keys(localStorage).find(key =>
        key.startsWith('sirati.cv.v2.') && (localStorage.getItem(key) || '').includes(marker)
      ) || null, marker);
      record('A device draft created by the existing builder', 'PASS');
    } catch {
      record('A device draft created by the existing builder', 'NOT RUN',
        'The builder did not create a matching device cache during this read-only test');
    }

    await page.goto(path('documents/'), {waitUntil:'domcontentloaded'});
    await page.locator('.documents-section').waitFor({timeout});
    // New privacy guards warn before deleting device-only drafts. Without
    // explicitly accepting the confirmation, Playwright may dismiss it by
    // default, leaving A signed in and causing a misleading navigation FAIL.
    let confirmations = 0;
    const respondToSignOutDialog = async dialog => {
      if (dialog.type() === 'confirm') {
        confirmations++;
        await dialog.accept();
      } else {
        await dialog.dismiss();
      }
    };
    page.on('dialog', respondToSignOutDialog);
    try {
      if (signOutPath === 'menu') {
        await page.getByRole('button', {name:'Open Sirati menu'}).click();
        await page.locator('.sirati-menu-signout').click();
      } else {
        await page.getByRole('button', {name:'Sign out'}).click();
      }
      await page.waitForURL(url => url.pathname === '/sirati/' || url.pathname === '/sirati', {timeout});
    } finally {
      page.off('dialog', respondToSignOutDialog);
    }
    assert(!originalKey || confirmations === 1,
      'A device draft was found, but sign-out did not show its required confirmation');
    record('A explicitly signed out via '+signOutPath+' with draft warning when needed', 'PASS');

    await signIn(process.env.SIRATI_AB_B_EMAIL, process.env.SIRATI_AB_B_PASSWORD);
    await page.locator('.document-card')
      .filter({hasText: process.env.SIRATI_AB_B_TITLE}).first().waitFor({timeout});
    const bCards = await page.locator('.document-grid').innerText();
    assert(!bCards.includes(process.env.SIRATI_AB_A_TITLE),
      'A account document title leaked into B document list');
    record('B sees own document but not A document in My Documents', 'PASS');

    await page.goto(path('profile/'), {waitUntil:'domcontentloaded'});
    await page.locator('.sirati-profile-details').waitFor({timeout});
    const profile = await safeVisibleText();
    assert(profile.includes(process.env.SIRATI_AB_B_EMAIL), 'B email missing from B profile');
    assert(!profile.includes(process.env.SIRATI_AB_A_EMAIL), 'A email displayed in B profile');
    record('B profile shows only B account identity', 'PASS');

    await page.goto(path('builder/?doc=' + encodeURIComponent(docId)), {waitUntil:'networkidle'});
    await page.waitForTimeout(1500); // allow asynchronous loading/error UI to settle
    assert(!(await anyVisibleFieldContains(marker)),
      'B builder displayed A-only marker on an A-owned document URL');
    record('B builder does not render A document marker via direct URL', 'PASS',
      'UI-only probe; not a server-side RLS permission test');

    if (originalKey) {
      const stillReadable = await page.evaluate(key => {
        const stored = localStorage.getItem(key);
        return Boolean(stored);
      }, originalKey);
      record('A local CV draft is inaccessible to B in the same browser',
        stillReadable ? 'FAIL' : 'PASS',
        stillReadable
          ? 'A scoped plaintext device draft remains accessible after logout (Issue #25)'
          : 'A scoped draft no longer remains in browser storage');
    } else {
      record('A local CV draft is inaccessible to B in the same browser', 'NOT RUN',
        'No A device draft cache was observed');
    }
  } catch (error) {
    record('A/B browser journey', 'FAIL',
      'Scenario did not pass; inspect the local failure details without sharing credentials or user data');
    if (process.env.SIRATI_AB_DEBUG === 'YES') {
      console.error('Step failure type:', error instanceof Error ? error.name : 'Unknown');
    }
  } finally {
    await context.close();
  }
} finally {
  await browser.close();
}

const failed = report.some(result => result.status === 'FAIL');
const incomplete = report.some(result => result.status === 'NOT RUN');
console.log('SUMMARY: ' + (failed ? 'FAIL' : incomplete ? 'INCOMPLETE' : 'PASS')
  + '. This is not independent Security/QA sign-off or proof of database RLS.');
process.exitCode = failed ? 1 : incomplete ? 2 : 0;
