import './pdf_prototype.test.mjs'; // Run auth guards and snapshot/A4 renderer tests on the exact same commit.
import test from 'node:test';
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
