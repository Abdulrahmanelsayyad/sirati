const { readFileSync } = require('node:fs');
const { resolve } = require('node:path');
const assert = require('node:assert/strict');
const { test } = require('node:test');
const source = readFileSync(resolve(process.argv[2], 'app/builder/page.tsx'), 'utf8');
const start = source.indexOf('onClick={event => {', source.indexOf('sirati-header-samples-menu'));
const end = source.indexOf('\n                  }}', start);
assert(start >= 0 && end > start);
const handler = source.slice(start + 'onClick={event => {'.length, end);
const effectStart = source.indexOf('    if (!hydrated || !cloudReadyRef.current || !documentId');
const effectEnd = source.indexOf('\n  }, [data,', effectStart);
assert(effectStart >= 0 && effectEnd > effectStart);
function scenario(options = {}) {
  const state = { documentId: 'saved-cv', data: { fullName: 'Original' }, versions: ['old'],
    historyOpen: true, currentSection: 4, url: '/builder?doc=saved-cv', writes: [] };
  let confirmation = '';
  const args = {
    hydrated: true, cloudReadyRef: { current: true }, cloudLoading: false,
    saveInFlight: { current: false }, language: 'en', uiLanguage: 'en', template: 'modern', userId: 'synthetic-user',
    choice: {}, normalizeCv: x => x, makeHeaderSampleCv: () => ({ fullName: 'Sample Candidate' }),
    withBasePath: x => '/sirati' + x,
    event: { currentTarget: { closest: () => ({ removeAttribute() {} }) } },
    setDocumentId: x => state.documentId = x, setData: x => state.data = x,
    setVersions: x => state.versions = x, setHistoryOpen: x => state.historyOpen = x,
    rememberSection: x => state.currentSection = x, setCloudStatus() {},
    window: { confirm: text => { confirmation = text; return options.accept !== false; },
      history: { replaceState: (_, __, url) => state.url = url },
      setTimeout: fn => { fn(); return 1; }, clearTimeout() {} },
    isSessionBoundaryBlocked: () => false, documentTitle: () => 'Synthetic',
    createClient: () => ({ from: () => ({ update: data => ({ eq: (_, id) => {
      state.writes.push({ id, data }); return Promise.resolve({ error: null });
    } }) }) }),
    ...options.args,
  };
  const run = code => new Function(...Object.keys(args), code.replaceAll('supabase!', 'supabase'))(...Object.values(args));
  run(handler);
  Object.assign(args, { documentId: state.documentId, data: state.data });
  run(source.slice(effectStart, effectEnd));
  return { state, confirmation };
}
test('sample becomes independent draft and cannot autosave over saved CV', () => {
  const { state } = scenario();
  assert.equal(state.data.fullName, 'Sample Candidate');
  assert.equal(state.documentId, null);
  assert.deepEqual(state.writes, []);
  assert.deepEqual(state.versions, []);
  assert.equal(state.historyOpen, false);
  assert.equal(state.currentSection, 0);
  assert.equal(state.url, '/sirati/builder?template=modern&language=en');
});
test('cancel preserves original document, data, history and URL', () => {
  const { state } = scenario({ accept: false });
  assert.equal(state.documentId, 'saved-cv');
  assert.equal(state.data.fullName, 'Original');
  assert.deepEqual(state.versions, ['old']);
  assert.equal(state.url, '/builder?doc=saved-cv');
  assert.equal(state.writes[0].data.data.fullName, 'Original');
});
test('Arabic sample keeps selected template and language with Arabic confirmation', () => {
  const { state, confirmation } = scenario({ args: { language: 'ar', uiLanguage: 'ar', template: 'compact-ats' } });
  assert.match(confirmation, /مسودة جديدة/);
  assert.equal(state.url, '/sirati/builder?template=compact-ats&language=ar');
});
for (const args of [{ hydrated: false }, { cloudReadyRef: { current: false } },
  { cloudLoading: true }, { saveInFlight: { current: true } }]) {
  test(`sample selection waits for initialization or active save: ${JSON.stringify(args)}`, () => {
    const { state, confirmation } = scenario({ args });
    assert.equal(confirmation, '');
    assert.equal(state.data.fullName, 'Original');
    assert.equal(state.documentId, 'saved-cv');
  });
}
