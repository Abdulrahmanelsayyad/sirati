import './pdf_prototype.test.mjs'; // Run auth guards and snapshot/A4 renderer tests on the exact same commit.
import test from 'node:test';
import { handleOfficialFrozenPdf } from '../netlify/functions/pdf-official-staging.mjs';
import assert from 'node:assert/strict';
import { handleAuthorizedPdfPrototype } from '../netlify/functions/pdf-auth-prototype.mjs';

const STAGING = 'https://ykfxcxhozqqsvhtdyxho.supabase.co';
const PROD = 'https://hzzojoiqzbeivxesjlyf.supabase.co';
const USER = '11111111-1111-4111-8111-111111111111';
const FOREIGN = '22222222-2222-4222-8222-222222222222';
const DOC = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';
const ORDER = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';
const KEY = 'sb_publishable_fake_test_only';
const env = {
  SIRATI_PDF_AUTH_POC_ENABLED: 'true',
  NEXT_PUBLIC_SUPABASE_URL: STAGING,
  SIRATI_STAGING_PUBLISHABLE_KEY: KEY,
};

function request(body = { documentId: DOC, orderId: ORDER, synthetic: true },
                 token = 'mock.JWT.token', method = 'POST') {
  return new Request('https://local.test/.netlify/functions/pdf-auth-prototype', {
    method,
    headers: token ? { Authorization: 'Bearer ' + token } : {},
    ...(method === 'POST' ? { body: JSON.stringify(body) } : {}),
  });
}

function fakeSupabase({
  authStatus = 200, userId = USER,
  document = { id: DOC, user_id: USER },
  order = {
    id: ORDER, document_id: DOC, user_id: USER,
    status: 'approved', amount_egp: 50, reviewed_at: '2026-10-08T12:00:00Z',
  },
  errorAt = null,
} = {}) {
  const calls = [];
  const fetcher = async (url, opts) => {
    const path = new URL(url).pathname;
    calls.push({ path, headers: opts.headers, url });
    assert.ok(url.startsWith(STAGING));
    assert.equal(opts.method, 'GET');
    assert.equal(opts.headers.apikey, KEY);
    assert.equal(opts.headers.Authorization, 'Bearer mock.JWT.token');
    if (path === errorAt) throw new Error('Synthetic network failure');
    if (path === '/auth/v1/user') return Response.json(
      authStatus === 200 ? { id: userId } : { error: 'invalid JWT' },
      { status: authStatus },
    );
    if (path === '/rest/v1/cv_documents') return Response.json(document ? [document] : []);
    if (path === '/rest/v1/pdf_orders') return Response.json(order ? [order] : []);
    throw new Error('Unexpected endpoint');
  };
  return { fetcher, calls };
}

async function check(body, { expected = 403, ...options } = {}) {
  const { fetcher } = fakeSupabase(options);
  const result = await handleAuthorizedPdfPrototype(request(body), { env, fetcher });
  assert.equal(result.status, expected);
  assert.notEqual(result.headers.get('content-type'), 'application/pdf');
  return result;
}

test('default deny: absent feature flag, wrong Supabase project, missing key', async () => {
  for (const badEnv of [
    { ...env, SIRATI_PDF_AUTH_POC_ENABLED: undefined },
    { ...env, NEXT_PUBLIC_SUPABASE_URL: PROD },
    { ...env, SIRATI_STAGING_PUBLISHABLE_KEY: undefined },
  ]) {
    assert.equal((await handleAuthorizedPdfPrototype(request(), { env: badEnv,
      fetcher() { throw new Error('No network expected'); },
    })).status, 404);
  }
});

test('method, missing JWT, and client-supplied fake status fail closed', async () => {
  const { fetcher } = fakeSupabase();
  assert.equal((await handleAuthorizedPdfPrototype(request({}, '', 'GET'), { env, fetcher })).status, 405);
  assert.equal((await handleAuthorizedPdfPrototype(request({}, ''), { env, fetcher })).status, 401);
  for (const body of [
    { documentId: DOC, orderId: ORDER, synthetic: true, status: 'approved' },
    { documentId: DOC, orderId: ORDER, synthetic: true, amount_egp: 0 },
    { documentId: 'not-a-uuid', orderId: ORDER, synthetic: true },
    { documentId: DOC, orderId: ORDER, synthetic: false },
  ]) {
    assert.equal((await handleAuthorizedPdfPrototype(request(body), { env, fetcher })).status, 400);
  }
});

test('Supabase Auth rejects token, and transport failures cannot issue a PDF', async () => {
  await check(undefined, { expected: 401, authStatus: 401 });
  await check(undefined, { expected: 503, errorAt: '/auth/v1/user' });
  await check(undefined, { expected: 503, errorAt: '/rest/v1/pdf_orders' });
});

test('document ownership, visible order identity, and exact document link required', async () => {
  await check(undefined, { document: { id: DOC, user_id: FOREIGN } });
  await check(undefined, { document: null });
  await check(undefined, { order: null });
  await check(undefined, { order: {
    id: ORDER, document_id: DOC, user_id: FOREIGN,
    status: 'approved', amount_egp: 50, reviewed_at: '2026-10-08T12:00:00Z',
  } });
  await check(undefined, { order: {
    id: ORDER, document_id: FOREIGN, user_id: USER,
    status: 'approved', amount_egp: 50, reviewed_at: '2026-10-08T12:00:00Z',
  } });
});

test('pending, rejected, altered price, or missing reviewed_at cannot issue', async () => {
  const base = { id: ORDER, document_id: DOC, user_id: USER,
    status: 'approved', amount_egp: 50, reviewed_at: '2026-10-08T12:00:00Z' };
  for (const overrides of [
    { status: 'pending' }, { status: 'rejected' }, { amount_egp: 1 },
    { reviewed_at: null }, { reviewed_at: 'invalid' },
  ]) {
    await check(undefined, { order: { ...base, ...overrides } });
  }
});

test('approved owned order produces ONLY fixed synthetic demo, never customer CV', async () => {
  const { fetcher, calls } = fakeSupabase();
  const reply = await handleAuthorizedPdfPrototype(request(), { env, fetcher });
  assert.equal(reply.status, 200);
  assert.equal(reply.headers.get('content-type'), 'application/pdf');
  assert.match(reply.headers.get('cache-control'), /no-store/);
  const pdf = Buffer.from(await reply.arrayBuffer()).toString('ascii');
  assert.ok(pdf.startsWith('%PDF-1.4'));
  assert.match(pdf, /JANE SAMPLE/);
  assert.doesNotMatch(pdf, /REAL CUSTOMER/);
  assert.deepEqual(calls.map(c => c.path),
    ['/auth/v1/user', '/rest/v1/cv_documents', '/rest/v1/pdf_orders']);
});


// #41 official staging endpoint: mocked DB/auth. No customer/real payment/network.
const frozenEnv = {
  ...env, BRANCH: 'feat/issue-41-synthetic-server-pdf-poc',
  SIRATI_OFFICIAL_PDF_STAGING_ENABLED: 'true',
  SIRATI_STAGING_SERVER_KEY: 'sb_secret_fake_offline_unit_test_only_12345',
};
const frozen = {
  order_id: ORDER, owner_user_id: USER, source_document_id: DOC,
  source_revision: 'cccccccc-cccc-4ccc-8ccc-cccccccccccc',
  expected_revision: 'cccccccc-cccc-4ccc-8ccc-cccccccccccc',
  snapshot_schema_version: 1,
  snapshot_template: 'compact-ats', snapshot_language: 'en',
  snapshot_data: { fullName: 'FROZEN ALICE', title: 'Registered Nurse',
    email: 'alice@example.invalid', profile: 'Approved original CV snapshot.' },
};
const officialRequest = (payload = { orderId: ORDER }, token = 'mock.JWT.token',
                         method = 'POST') => new Request('https://local.test/.netlify/functions/pdf-official-staging', {
  method, headers: token ? { Authorization: 'Bearer ' + token } : {},
  ...(method === 'POST' ? { body: typeof payload === 'string' ? payload : JSON.stringify(payload) } : {}),
});
function frozenFetcher({
  authStatus = 200, userId = USER, returned = frozen, rpcStatus = 200,
  networkError = '', oversize = false,
} = {}) {
  const calls = [];
  const fetcher = async (url, options) => {
    const path = new URL(url).pathname;
    calls.push({ path, ...options });
    assert.ok(url.startsWith(STAGING));
    assert.equal(options.redirect, 'error');
    assert.ok(options.signal);
    if (path === networkError) throw new Error('Simulated upstream outage');
    if (path === '/auth/v1/user') {
      assert.equal(options.method, 'GET');
      assert.equal(options.headers.apikey, KEY);
      assert.equal(options.headers.Authorization, 'Bearer mock.JWT.token');
      return Response.json(authStatus === 200 ? { id: userId } : { error: 'invalid' },
        { status: authStatus });
    }
    if (path === '/rest/v1/rpc/sirati_pdf_snapshot_for_server') {
      assert.equal(options.method, 'POST');
      assert.equal(options.headers.apikey, frozenEnv.SIRATI_STAGING_SERVER_KEY);
      // API key must not be forwarded as a JWT in the Authorization header.
      assert.equal(Object.hasOwn(options.headers, 'Authorization'), false);
      assert.equal(Object.hasOwn(options.headers, 'authorization'), false);
      assert.deepEqual(JSON.parse(options.body), { p_order_id: ORDER, p_user_id: userId });
      return oversize ? new Response('x'.repeat(200000)) :
        Response.json(returned, { status: rpcStatus });
    }
    throw new Error('Unexpected external call: ' + path);
  };
  return { calls, fetcher };
}
async function official(body, cfg = {}) {
  const { fetcher, calls } = frozenFetcher(cfg);
  const reply = await handleOfficialFrozenPdf(officialRequest(body), {
    env: frozenEnv, fetcher,
  });
  return { reply, calls };
}
test('official route is branch/staging/secret-guarded and disabled by default', async () => {
  for (const patch of [
    { SIRATI_OFFICIAL_PDF_STAGING_ENABLED: undefined }, { BRANCH: 'main' },
    { NEXT_PUBLIC_SUPABASE_URL: PROD }, { SIRATI_STAGING_SERVER_KEY: undefined },
    { SIRATI_STAGING_SERVER_KEY: KEY },
    { SIRATI_STAGING_SERVER_KEY: 'fake_long_non_secret_key_only_12345' },
    { SIRATI_STAGING_SERVER_KEY: 'sb_publishable_wrong_role_only_12345' },
  ]) {
    let requests = 0;
    const response = await handleOfficialFrozenPdf(officialRequest(), {
      env: { ...frozenEnv, ...patch },
      fetcher: () => { requests++; throw new Error('No upstream allowed'); },
    });
    assert.equal(response.status, 404); assert.equal(requests, 0);
  }
});
test('official route rejects GET, unauthenticated and oversized/malformed input', async () => {
  let fetchCount = 0;
  const opts = { env: frozenEnv, fetcher: () => { fetchCount++; throw new Error('No upstream'); } };
  assert.equal((await handleOfficialFrozenPdf(officialRequest('', '', 'GET'), opts)).status, 405);
  assert.equal((await handleOfficialFrozenPdf(officialRequest({}, ''), opts)).status, 401);
  for (const invalid of [
    {}, { documentId: DOC, orderId: ORDER }, { orderId: FOREIGN },
    '{"orderId":null}', '{not json}', 'x'.repeat(300),
  ]) {
    // FOREIGN is a valid UUID: a foreign order must reach authorization, not 400.
    if (invalid?.orderId === FOREIGN) continue;
    assert.equal((await handleOfficialFrozenPdf(officialRequest(invalid), opts)).status, 400);
  }
  assert.equal(fetchCount, 0);
});
test('official route verifies JWT before privileged snapshot RPC, fails closed', async () => {
  for (const config of [
    { authStatus: 401, expected: 401 }, { userId: 'not-uuid', expected: 401 },
    { networkError: '/auth/v1/user', expected: 503 },
  ]) {
    const { expected, ...mock } = config;
    const { reply, calls } = await official(undefined, mock);
    assert.equal(reply.status, expected);
    assert.deepEqual(calls.map(c => c.path), ['/auth/v1/user']);
  }
});
test('approved immutable owned order returns official PDF, never current CV', async () => {
  const { reply, calls } = await official();
  assert.equal(reply.status, 200);
  assert.equal(reply.headers.get('content-type'), 'application/pdf');
  assert.match(reply.headers.get('cache-control'), /no-store/);
  assert.match(reply.headers.get('content-disposition'), /attachment/);
  const pdf = Buffer.from(await reply.arrayBuffer()).toString('ascii');
  assert.match(pdf, /FROZEN ALICE/);
  assert.doesNotMatch(pdf, /JANE SAMPLE|MUTABLE CURRENT/);
  assert.deepEqual(calls.map(c => c.path), [
    '/auth/v1/user', '/rest/v1/rpc/sirati_pdf_snapshot_for_server',
  ]);
  const again = await official();
  assert.equal(Buffer.compare(Buffer.from(pdf, 'ascii'),
    Buffer.from(await again.reply.arrayBuffer())), 0);
});
test('no snapshot, other user, revision mismatch or legacy unbound never yields PDF', async () => {
  for (const s of [
    null,
    { ...frozen, owner_user_id: FOREIGN },
    { ...frozen, order_id: FOREIGN },
    { ...frozen, source_document_id: 'nope' },
    { ...frozen, source_revision: 'dddddddd-dddd-4ddd-8ddd-dddddddddddd' },
    { ...frozen, expected_revision: null },
    { ...frozen, snapshot_schema_version: 2 },
  ]) {
    const { reply } = await official(undefined, { returned: s });
    assert.equal(reply.status, 403);
    assert.notEqual(reply.headers.get('content-type'), 'application/pdf');
  }
});
test('pending/rejected/unapproved/cross-user orders are not returned by privileged RPC', async () => {
  for (const returned of [null, null, null]) {
    const { reply } = await official(undefined, { returned });
    assert.equal(reply.status, 403);
  }
});
test('unsupported Arabic or any other template fail closed without PDF', async () => {
  for (const patch of [
    { snapshot_language: 'ar' },
    { snapshot_template: 'profile-sidebar' },
    { snapshot_data: { ...frozen.snapshot_data, fullName: 'علي' } },
    { snapshot_data: { ...frozen.snapshot_data, avatar: 'data:image/png;base64,abc' } },
  ]) {
    const { reply } = await official(undefined, { returned: { ...frozen, ...patch } });
    assert.equal(reply.status, 422);
    assert.notEqual(reply.headers.get('content-type'), 'application/pdf');
  }
});
test('snapshot RPC network/error/oversized result rejects and never returns PDF', async () => {
  for (const mock of [
    { networkError: '/rest/v1/rpc/sirati_pdf_snapshot_for_server' },
    { rpcStatus: 500 }, { oversize: true },
  ]) {
    const { reply } = await official(undefined, mock);
    assert.equal(reply.status, 503);
    assert.notEqual(reply.headers.get('content-type'), 'application/pdf');
  }
});
