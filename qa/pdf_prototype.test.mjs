import test from 'node:test';
import assert from 'node:assert/strict';
import handler, { renderSyntheticCompactAtsPdf } from '../netlify/functions/pdf-prototype.mjs';

const staging = 'https://ykfxcxhozqqsvhtdyxho.supabase.co';
const request = (payload = '{"synthetic":true}', method = 'POST') => new Request(
  'http://localhost/.netlify/functions/pdf-prototype',
  { method, ...(method === 'POST' ? { body: payload } : {}) },
);

test('PDF header, A4 dimensions, xref and synthetic text are present', () => {
  const pdf = renderSyntheticCompactAtsPdf().toString('ascii');
  assert.ok(pdf.startsWith('%PDF-1.4\n'));
  assert.match(pdf, /MediaBox \[0 0 595.28 841.89\]/);
  assert.match(pdf, /\/Count 1\b/);
  assert.match(pdf, /\(JANE SAMPLE\)/);
  assert.match(pdf, /jane.sample@example.invalid/);
  assert.match(pdf, /xref\n0 7\n/);
  assert.match(pdf, /%%EOF\n$/);
});

test('function is disabled by default and for production Supabase', async () => {
  delete process.env.SIRATI_PDF_POC_ENABLED;
  process.env.NEXT_PUBLIC_SUPABASE_URL = staging;
  assert.equal((await handler(request())).status, 404);
  process.env.SIRATI_PDF_POC_ENABLED = 'true';
  process.env.NEXT_PUBLIC_SUPABASE_URL = 'https://hzzojoiqzbeivxesjlyf.supabase.co';
  assert.equal((await handler(request())).status, 404);
});

test('synthetic-only allowed under explicit staging flags', async () => {
  process.env.SIRATI_PDF_POC_ENABLED = 'true';
  process.env.NEXT_PUBLIC_SUPABASE_URL = staging;
  assert.equal((await handler(request('{"document_id":"real"}'))).status, 400);
  assert.equal((await handler(request('', 'GET'))).status, 405);
  const response = await handler(request());
  assert.equal(response.status, 200);
  assert.equal(response.headers.get('content-type'), 'application/pdf');
  assert.equal(response.headers.get('cache-control'), 'no-store');
  assert.ok((await response.arrayBuffer()).byteLength > 600);
});
