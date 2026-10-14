// Optional independent QA gate: two synthetic accounts, one browser profile.
// Default journey is read-only; optional recovery edits only the supplied synthetic
// local-Staging fixture. No SQL, payments or production configuration changes.
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
  if (process.env.SIRATI_AB_STAGING_ONLY === 'YES') {
    assert(local && !production, 'Staging QA requires the isolated local frontend');
    await context.route('**/*', route => {
      const url = new URL(route.request().url());
      return [base.origin, 'https://ykfxcxhozqqsvhtdyxho.supabase.co'].includes(url.origin)
        ? route.continue() : route.abort();
    });
  }
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

  let phase = 'start';
  async function signIn(email, password) {
    phase = 'open login page';
    await page.goto(path('auth/?next=/documents'), {waitUntil: 'networkidle'});
    // Static HTML is visible before React hydration. Exercise an existing
    // stateful control and wait for both renders before filling credentials.
    phase = 'wait for interactive login form';
    const switchMode = page.locator('.auth-switch');
    await switchMode.click();
    await page.locator('input[autocomplete=new-password]').waitFor({timeout});
    await switchMode.click();
    await page.locator('input[autocomplete=current-password]').waitFor({timeout});
    phase = 'fill login form';
    await page.locator('input[type=email]').fill(email);
    await page.locator('input[type=password]').fill(password);
    phase = 'submit login form';
    const valid = await page.locator('input[type=password]').evaluate(el => el.checkValidity());
    if (!valid) record('Login form accepts supplied password length', 'FAIL', 'Existing account password rejected by HTML form validation');
    await page.locator('form button').first().click();
    phase = 'wait documents redirect';
    // Inspect pathname: the login URL already contains ?next=/documents.
    await page.waitForURL(url => url.pathname === '/sirati/documents/' ||
      url.pathname === '/sirati/documents', {timeout});
    phase = 'wait documents section';
    await page.locator('.documents-section').waitFor({timeout});
    phase = 'wait document cards';
    await page.locator('.document-grid .document-card').first().waitFor({timeout});
  }

  let originalKey = null;
  try {
    await signIn(process.env.SIRATI_AB_A_EMAIL, process.env.SIRATI_AB_A_PASSWORD);
    phase = 'find A fixture title';
    await page.locator('.document-card')
      .filter({hasText: process.env.SIRATI_AB_A_TITLE}).first().waitFor({timeout});
    record('A can view own pre-existing synthetic document', 'PASS');
    await page.goto(path('builder/?doc=' + encodeURIComponent(docId)), {waitUntil:'domcontentloaded'});
    await waitForMarker(marker);
    record('A can open own existing document with A-only marker', 'PASS');
    assert(!(await page.evaluate(value => Object.values(localStorage).some(v => v.includes(value)), marker)),
      'Authenticated draft must not persist in localStorage');
    try {
      await page.waitForFunction(marker => Object.keys(sessionStorage).some(key =>
        key.startsWith('sirati.cv.v2.') && (sessionStorage.getItem(key) || '').includes(marker)),
        marker, {timeout:8000});
      originalKey = await page.evaluate(marker => Object.keys(sessionStorage).find(key =>
        key.startsWith('sirati.cv.v2.') && (sessionStorage.getItem(key) || '').includes(marker)
      ) || null, marker);
      record('A device draft created by the existing builder', 'PASS');
    } catch {
      record('A device draft created by the existing builder', 'NOT RUN',
        'The builder did not create a matching device cache during this read-only test');
    }

    if (process.env.SIRATI_AB_SAVE_RECOVERY === 'YES') {
      assert(local && process.env.SIRATI_AB_STAGING_ONLY === 'YES',
        'Save recovery is restricted to the isolated Staging frontend');
      phase = 'failed network save retains synthetic editor data';
      const editedMarker = marker + '-RECOVERY';
      const nameInput = page.locator('.field').filter({has: page.locator('label', {hasText: /^Full name$/})}).locator('input');
      const documentApi = 'https://ykfxcxhozqqsvhtdyxho.supabase.co/rest/v1/cv_documents*';
      let deniedWrites = 0;
      const failWrites = route => {
        if (['PATCH', 'POST'].includes(route.request().method())) {
          deniedWrites++;
          return route.abort('internetdisconnected');
        }
        return route.continue();
      };
      await context.route(documentApi, failWrites);
      try {
        await nameInput.fill(editedMarker);
        await page.locator('.save-status').filter({hasText: /Cloud save failed|Save failed/}).waitFor({timeout});
        assert(deniedWrites > 0, 'A real document write must have been blocked');
        assert.equal(await nameInput.inputValue(), editedMarker);
        assert(await page.evaluate(value => Object.keys(sessionStorage).some(key =>
          key.startsWith('sirati.cv.v2.') && sessionStorage.getItem(key)?.includes(value)), editedMarker));
        record('Failed document network save retains editor and session draft', 'PASS');
      } finally {
        await context.unroute(documentApi, failWrites);
      }
      phase = 'retry save after reconnect and reopen synthetic document';
      await page.locator('.sirati-builder-save').click();
      await page.locator('.save-status').filter({hasText: 'Saved + version created'}).waitFor({timeout});
      await page.reload({waitUntil:'networkidle'});
      await waitForMarker(editedMarker);
      assert.equal(await nameInput.inputValue(), editedMarker);
      record('Explicit retry after network recovery persists edits across reload', 'PASS');
      // Restore the fixture name/title for subsequent isolation scenarios.
      await nameInput.fill(marker);
      await page.locator('.save-status').filter({hasText: /^Saved to account$/}).waitFor({timeout});
    }

    await page.goto(path('documents/'), {waitUntil:'networkidle'});
    phase = 'wait documents section';
    await page.locator('.documents-section').waitFor({timeout});
    phase = 'wait for authenticated document list before sign out';
    await page.locator('.document-card').filter({hasText: process.env.SIRATI_AB_A_TITLE}).first().waitFor({timeout});
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
        phase = 'open Documents account details and sign out';
        await page.locator('.sirati-documents-account-disclosure > summary').click();
        phase = 'click Documents sign out';
        await page.getByRole('button', {name:'Sign out', exact:true}).click();
      }
      phase = 'wait for signed-out home redirect';
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
        const stored = sessionStorage.getItem(key) || localStorage.getItem(key);
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
      'Stage: ' + phase + '; failure type: ' + (error instanceof Error ? error.name : 'Unknown'));
    const msg = await page.locator('.auth-message').textContent({timeout:1000}).catch(() => '');
    if (msg?.includes('at least 8 characters')) record('Login form minimum length', 'FAIL', 'UI requires eight characters even for existing accounts');
    if (msg?.includes('Invalid login credentials')) record('Browser login', 'FAIL', 'Auth rejected credentials');
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
