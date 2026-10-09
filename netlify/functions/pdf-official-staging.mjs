// Issue #41: BLOCKED customer launch. EXPERIMENTAL BRANCH / STAGING-ONLY.
// No live deployment or keys are configured by committing this file.
// Server verifies the JWT, then asks a service_role-ONLY PostgREST RPC to
// authorize + fetch the immutable approved-order snapshot in ONE DB query.
// NEVER import client-side, serve an arbitrary snapshot, or fall back to
// cv_documents.data or synthetic PDF on errors.
import { renderCompactAtsSnapshotPdf } from './pdf-prototype.mjs';

const STAGING = 'https://ykfxcxhozqqsvhtdyxho.supabase.co';
const EXPERIMENT_BRANCH = 'feat/issue-41-synthetic-server-pdf-poc';
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const BEARER = /^Bearer ([A-Za-z0-9._~-]{10,8192})$/;
const jsonError = (message, status) => new Response(JSON.stringify({ error: message }), {
  status,
  headers: { 'Content-Type': 'application/json', 'Cache-Control': 'private, no-store' },
});

// Stream with strict byte ceiling. Content-Length is not a security boundary.
async function bytesLimited(body, ceiling) {
  if (!body) throw new Error('Body missing');
  const reader = body.getReader();
  let size = 0;
  const chunks = [];
  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > ceiling) {
        await reader.cancel();
        throw new Error('Body too large');
      }
      chunks.push(Buffer.from(value));
    }
  } finally {
    reader.releaseLock();
  }
  return Buffer.concat(chunks, size).toString('utf8');
}

async function fetchJson(fetcher, url, opts, limit) {
  const response = await fetcher(url, {
    ...opts,
    redirect: 'error',
    signal: AbortSignal.timeout(4000),
  });
  if (response.status === 401 || response.status === 403) {
    return { denied: true };
  }
  if (!response.ok) throw new Error('Upstream unavailable');
  const text = await bytesLimited(response.body, limit);
  return { data: JSON.parse(text) };
}

export async function handleOfficialFrozenPdf(request, {
  env = process.env,
  fetcher = globalThis.fetch,
  render = renderCompactAtsSnapshotPdf,
} = {}) {
  // A deployment of this code to main or Production remains inert.
  if (env.SIRATI_OFFICIAL_PDF_STAGING_ENABLED !== 'true' ||
      env.BRANCH !== EXPERIMENT_BRANCH ||
      env.NEXT_PUBLIC_SUPABASE_URL !== STAGING ||
      !env.SIRATI_STAGING_PUBLISHABLE_KEY?.startsWith('sb_publishable_') ||
      typeof env.SIRATI_STAGING_SERVER_KEY !== 'string' ||
      !env.SIRATI_STAGING_SERVER_KEY.startsWith('sb_secret_') ||
      env.SIRATI_STAGING_SERVER_KEY.length < 24 ||
      env.SIRATI_STAGING_SERVER_KEY === env.SIRATI_STAGING_PUBLISHABLE_KEY) {
    return jsonError('Not found', 404);
  }
  if (request.method !== 'POST') return jsonError('Method not allowed', 405);
  const auth = BEARER.exec(request.headers.get('authorization') || '');
  if (!auth) return jsonError('Authentication required', 401);

  let body;
  try {
    body = JSON.parse(await bytesLimited(request.body, 128));
    if (!body || typeof body !== 'object' || Array.isArray(body) ||
        Object.keys(body).length !== 1 || !Object.hasOwn(body, 'orderId') ||
        typeof body.orderId !== 'string' || !UUID.test(body.orderId)) {
      return jsonError('Invalid request', 400);
    }
  } catch {
    return jsonError('Invalid request', 400);
  }

  let verifiedUserId;
  try {
    const authResponse = await fetchJson(
      fetcher, STAGING + '/auth/v1/user', {
        method: 'GET',
        headers: {
          apikey: env.SIRATI_STAGING_PUBLISHABLE_KEY,
          Authorization: 'Bearer ' + auth[1],
          Accept: 'application/json',
        },
      }, 16000,
    );
    if (authResponse.denied) return jsonError('Authentication required', 401);
    verifiedUserId = authResponse.data?.id;
    if (typeof verifiedUserId !== 'string' || !UUID.test(verifiedUserId)) {
      return jsonError('Authentication required', 401);
    }
  } catch {
    return jsonError('Identity verification unavailable', 503);
  }

  let snapshot;
  try {
    // sb_secret_* identifies this trusted server only through apikey.
    // It is NOT a JWT and must never appear in Authorization: Bearer.
    // p_user_id comes strictly from the preceding verified end-user JWT.
    const lookup = await fetchJson(
      fetcher, STAGING + '/rest/v1/rpc/sirati_pdf_snapshot_for_server', {
        method: 'POST',
        headers: {
          apikey: env.SIRATI_STAGING_SERVER_KEY,
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({ p_order_id: body.orderId, p_user_id: verifiedUserId }),
      }, 180000,
    );
    if (lookup.denied) return jsonError('Export unavailable', 503);
    snapshot = lookup.data;
  } catch {
    return jsonError('Export authorization unavailable', 503);
  }

  // Fail closed for missing legacy snapshots, stale/rebound or foreign orders.
  if (!snapshot || typeof snapshot !== 'object' || Array.isArray(snapshot)) {
    return jsonError('No approved frozen PDF for this order', 403);
  }
  if (snapshot.order_id !== body.orderId ||
      snapshot.owner_user_id !== verifiedUserId ||
      !UUID.test(snapshot.source_document_id || '') ||
      !UUID.test(snapshot.source_revision || '') ||
      snapshot.source_revision !== snapshot.expected_revision ||
      snapshot.snapshot_schema_version !== 1) {
    return jsonError('Snapshot authorization mismatch', 403);
  }

  let pdf;
  try {
    pdf = render(snapshot);
    if (!Buffer.isBuffer(pdf) || pdf.length < 100 ||
        pdf.length > 2_000_000 ||
        pdf.subarray(0, 5).toString('ascii') !== '%PDF-') {
      throw new Error('Bad PDF');
    }
  } catch {
    // Unsupported Arabic/RTL/photo/other template: never silently downgrade.
    return jsonError('Selected CV template cannot be exported safely yet', 422);
  }
  return new Response(pdf, {
    status: 200,
    headers: {
      'Content-Type': 'application/pdf',
      'Content-Disposition': 'attachment; filename="sirati-paid-' +
        body.orderId.slice(0, 8) + '.pdf"',
      'Cache-Control': 'private, no-store, max-age=0',
      'X-Content-Type-Options': 'nosniff',
      'X-Robots-Tag': 'noindex',
    },
  });
}

export default function handler(request) {
  return handleOfficialFrozenPdf(request);
}
