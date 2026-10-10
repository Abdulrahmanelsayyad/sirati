const { readFileSync } = require('node:fs');
const { resolve } = require('node:path');
const assert = require('node:assert/strict');
const { test } = require('node:test');
const source = readFileSync(resolve(process.argv[2] || 'decoded/sirati-cv-source', 'app/builder/page.tsx'), 'utf8');
const initStart = source.indexOf('    const params = new URLSearchParams(window.location.search);');
const initEnd = source.indexOf('    setHydrated(true);', initStart);
const branchStart = source.indexOf('      if (!requestedDocumentId) {');
const branchEnd = source.indexOf('      setCloudLoading(true);', branchStart);
assert(initStart >= 0 && initEnd > initStart && branchStart >= 0 && branchEnd > branchStart);
function scenario({ fresh = false, query = '', replay = false, owner = 'A', sessionExisting = false } = {}) {
  const values = new Map([
    ['sirati.cv.v2.A', JSON.stringify({ data: { fullName: 'Previous A' }, template: 'classic', language: 'en' })],
    ['sirati.cv.v2.B', JSON.stringify({ data: { fullName: 'Previous B' }, template: 'compact', language: 'ar' })],
  ]);
  const sessionValues = new Map(sessionExisting ? [
    ['sirati.cv.v2.A', JSON.stringify({ data: { fullName: 'Current Tab A' }, template: 'compact', language: 'ar' })],
    ['sirati.cv.v2.B', JSON.stringify({ data: { fullName: 'Current Tab B' }, template: 'classic', language: 'en' })],
  ] : []);
  if (fresh) {
    values.set('sirati.onboarding.newCv', '1');
    values.set('sirati.onboarding.template', 'compact-ats');
    values.set('sirati.onboarding.language', 'ar');
  }
  const result = { data: { fullName: '' }, template: 'modern', language: 'en' };
  const ref = { current: false };
  const localStorage = { getItem: k => values.get(k) ?? null, removeItem: k => values.delete(k) };
  const sessionStorage = {
    getItem: k => sessionValues.get(k) ?? null,
    setItem: (k, v) => sessionValues.set(k, v),
    removeItem: k => sessionValues.delete(k),
  };
  const args = {
    window: { location: { search: query }, localStorage, sessionStorage }, URLSearchParams,
    localStorage, sessionStorage,
    newCvRequestedRef: ref, isSupabaseConfigured: () => true,
    cloneEmptyCv: () => ({ fullName: '' }), normalizeCv: x => x,
    setData: x => { result.data = x; }, setTemplate: x => { result.template = x; },
    setLanguage: x => { result.language = x; },
    STORAGE_KEY: 'sirati.cv.v2', LEGACY_STORAGE_KEY: 'sirati.cv.v1',
    requestedDocumentId: new URLSearchParams(query).get('doc'),
    accountDraftStorageKey: id => 'sirati.cv.v2.' + id, user: { id: owner },
    setCloudStatus: () => {}, cloudReadyRef: { current: false },
  };
  const run = code => new Function(...Object.keys(args), code)(...Object.values(args));
  run(source.slice(initStart, initEnd));
  if (replay) run(source.slice(initStart, initEnd));
  run(source.slice(branchStart, branchEnd));
  return { ...result, newIntent: ref.current, values, sessionValues };
}
test('new CV keeps blank data and selected Arabic Compact ATS', () => {
  const s = scenario({ fresh: true, query: '?template=compact-ats&language=ar' });
  assert.equal(s.data.fullName, ''); assert.equal(s.template, 'compact-ats'); assert.equal(s.language, 'ar');
});
test('ordinary return restores only an active-tab draft', () => {
  const s = scenario({ sessionExisting: true });
  assert.equal(s.data.fullName, 'Current Tab A'); assert.equal(s.template, 'compact');
});
test('another account restores only its own draft', () => {
  assert.equal(scenario({ owner: 'B', sessionExisting: true }).data.fullName, 'Current Tab B');
});
test('effect replay does not lose new-CV intent after keys are consumed', () => {
  const s = scenario({ fresh: true, query: '?template=compact-ats&language=ar', replay: true });
  assert.equal(s.data.fullName, ''); assert.equal(s.template, 'compact-ats'); assert.equal(s.newIntent, true);
});
test('explicit saved-document request takes priority over stale onboarding flag', () => {
  assert.equal(scenario({ fresh: true, query: '?doc=saved-document' }).newIntent, false);
});
test('fresh CV is blank even when this account has an active-tab draft', () => {
  const s = scenario({ fresh: true, sessionExisting: true });
  assert(s.sessionValues.has('sirati.cv.v2.A'));
  assert.equal(s.data.fullName, '');
});
test('a persistent legacy CV draft is never auto-restored', () => {
  const s = scenario({ owner: 'A' });
  assert.equal(s.data.fullName, '');
  assert(!s.sessionValues.has('sirati.cv.v2.A'));
  // The sitewide pre-launch purge handles old persistent keys once.
  assert(s.values.has('sirati.cv.v2.A'));
});
test('existing tab draft takes precedence over older persistent draft', () => {
  const s = scenario({ owner: 'A', sessionExisting: true });
  assert.equal(s.data.fullName, 'Current Tab A');
  assert.equal(s.language, 'ar');
  assert(s.values.has('sirati.cv.v2.A'));
});
