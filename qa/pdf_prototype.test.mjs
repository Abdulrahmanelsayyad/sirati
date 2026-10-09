import test from 'node:test';
import assert from 'node:assert/strict';
import handler, { renderSyntheticCompactAtsPdf, renderCompactAtsSnapshotPdf } from '../netlify/functions/pdf-prototype.mjs';

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


const snapshot = {
  order_id: 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',
  source_revision: 'cccccccc-cccc-4ccc-8ccc-cccccccccccc',
  snapshot_template: 'compact-ats',
  snapshot_language: 'en',
  snapshot_data: {
    fullName: 'FROZEN ALICE', title: 'Registered Nurse',
    email: 'alice@example.invalid', profile: 'Triage and critical care.',
    experience: [{ role: 'Emergency Nurse', company: 'Sample Hospital',
      period: '2022-2026', details: 'Patient assessment and safe handoff.' }],
    skills: 'BLS\nACLS',
  },
};

test('new renderer produces content from the FROZEN order snapshot, not a demo CV', () => {
  const pdf = renderCompactAtsSnapshotPdf(snapshot).toString('ascii');
  assert.match(pdf, /^%PDF-1\.4/);
  assert.match(pdf, /MediaBox \[0 0 595\.28 841\.89\]/);
  assert.match(pdf, /\(FROZEN ALICE\)/);
  assert.match(pdf, /Sample Hospital/);
  assert.doesNotMatch(pdf, /JANE SAMPLE/);
  const changedCurrentCv = { ...snapshot.snapshot_data, fullName: 'MUTABLE MALLORY' };
  assert.notEqual(changedCurrentCv.fullName, snapshot.snapshot_data.fullName);
  assert.deepEqual(renderCompactAtsSnapshotPdf(snapshot),
    renderCompactAtsSnapshotPdf(snapshot), 'repeat download must remain deterministic');
});

test('renderer fails closed instead of silently corrupting Arabic, photos or other templates', () => {
  for (const modification of [
    { snapshot_language: 'ar' },
    { snapshot_template: 'gold-sidebar' },
    { snapshot_data: { ...snapshot.snapshot_data, fullName: 'علي' } },
    { snapshot_data: { ...snapshot.snapshot_data, avatar: 'data:image/png;base64,xx' } },
    { snapshot_data: { ...snapshot.snapshot_data, experience: 'invalid' } },
  ]) assert.throws(() => renderCompactAtsSnapshotPdf({ ...snapshot, ...modification }));
});

test('PDF escaping and safe pagination for long immutable content', () => {
  const long = { ...snapshot, snapshot_data: {
    ...snapshot.snapshot_data,
    profile: ('Handles (complex) \\ tasks safely. ').repeat(90),
  }};
  const pdf = renderCompactAtsSnapshotPdf(long).toString('ascii');
  assert.match(pdf, /Handles \\(complex\\) \\\\ tasks safely/);
  assert.match(pdf, /\/Count [2-8] /);
  assert.match(pdf, /startxref\n\d+\n%%EOF/);
});
