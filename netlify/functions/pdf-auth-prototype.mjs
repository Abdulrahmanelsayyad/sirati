// Issue #41: UNDEPLOYED, staging-only secure authorization handshake POC.
// On approval this issues ONLY the fixed synthetic demonstration PDF; not a customer CV.
// No service_role, real payment data mutation, CV HTML, or private keys are used.
import { renderSyntheticCompactAtsPdf } from './pdf-prototype.mjs';

const STAGING_URL = 'https://ykfxcxhozqqsvhtdyxho.supabase.co';
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const TOKEN_RE = /^Bearer ([A-Za-z0-9._~-]{10,8192})$/;

function answer(message, status) {
  return new Response(JSON.stringify({ error: message }), {
    status,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  });
}

async function readJson(response) {
  if (!response.ok) throw new Error('Upstream rejected request');
  return response.json();
}

function headersFor(key, token) {
  return { apikey: key, Authorization: 'Bearer ' + token, Accept: 'application/json' };
}

async function rowsFor(table, fields, id, headers, fetcher) {
  // The caller's verified JWT is forwarded unchanged: Supabase RLS is enforced.
  const url = new URL(STAGING_URL + '/rest/v1/' + table);
  url.searchParams.set('select', fields);
  url.searchParams.set('id', 'eq.' + id);
  url.searchParams.set('limit', '2');
  const result = await readJson(await fetcher(url.toString(), {
    method: 'GET', headers, redirect: 'error',
  }));
  if (!Array.isArray(result) || result.length > 1) {
    throw new Error('Invalid database response');
  }
  return result.length === 1 ? result[0] : null;
}

export async function handleAuthorizedPdfPrototype(request, {
  env = process.env,
  fetcher = globalThis.fetch,
} = {}) {
  // Inert on production/ordinary staging. Explicitly gated for narrow local tests.
  if (env.SIRATI_PDF_AUTH_POC_ENABLED !== 'true' ||
      env.NEXT_PUBLIC_SUPABASE_URL !== STAGING_URL ||
      !env.SIRATI_STAGING_PUBLISHABLE_KEY?.startsWith('sb_publishable_')) {
    return answer('Not found', 404);
  }
  if (request.method !== 'POST') return answer('Method not allowed', 405);

  const auth = TOKEN_RE.exec(request.headers.get('authorization') || '');
  if (!auth) return answer('Authentication required', 401);
  const token = auth[1];

  let payload;
  try {
    const body = await request.text();
    if (body.length > 500) return answer('Invalid request', 400);
    payload = JSON.parse(body);
  } catch {
    return answer('Invalid request', 400);
  }
  if (payload === null || Array.isArray(payload) || typeof payload !== 'object' ||
      Object.keys(payload).sort().join(',') !== 'documentId,orderId,synthetic' ||
      payload.synthetic !== true ||
      !UUID_RE.test(payload.documentId) || !UUID_RE.test(payload.orderId)) {
    return answer('Invalid request', 400);
  }

  const headers = headersFor(env.SIRATI_STAGING_PUBLISHABLE_KEY, token);
  let user, document, order;
  try {
    // Verify token with Supabase Auth, NOT locally decoded JWT user claims.
    const authReply = await fetcher(STAGING_URL + '/auth/v1/user', {
      method: 'GET', headers, redirect: 'error',
    });
    if (authReply.status === 401 || authReply.status === 403) {
      return answer('Authentication required', 401);
    }
    user = await readJson(authReply);
    if (!UUID_RE.test(user?.id)) return answer('Authentication required', 401);

    // Both reads run under user JWT and RLS; also check every relation explicitly.
    document = await rowsFor(
      'cv_documents', 'id,user_id', payload.documentId, headers, fetcher,
    );
    if (!document || document.id !== payload.documentId || document.user_id !== user.id) {
      return answer('Document unavailable', 403);
    }
    order = await rowsFor(
      'pdf_orders', 'id,user_id,document_id,status,amount_egp,reviewed_at',
      payload.orderId, headers, fetcher,
    );
    if (!order || order.id !== payload.orderId || order.user_id !== user.id ||
        order.document_id !== document.id) {
      return answer('Order unavailable', 403);
    }
  } catch {
    return answer('Authorization unavailable', 503); // fail closed; no PDF
  }

  // The client cannot create approved orders because staging has restrictive RLS.
  if (order.status !== 'approved' || order.amount_egp !== 50 ||
      typeof order.reviewed_at !== 'string' ||
      !Number.isFinite(Date.parse(order.reviewed_at))) {
    return answer('Order not approved', 403);
  }

  // Deliberately emits FIXED, FICTIONAL content, not cv_documents.data.
  // Version/approved-snapshot binding remains unimplemented; customer launch blocked.
  return new Response(renderSyntheticCompactAtsPdf(), {
    status: 200,
    headers: {
      'Content-Type': 'application/pdf',
      'Content-Disposition': 'attachment; filename="sirati-auth-gated-synthetic-demo.pdf"',
      'Cache-Control': 'no-store, private',
      'X-Content-Type-Options': 'nosniff',
    },
  });
}

export default function handler(request) {
  return handleAuthorizedPdfPrototype(request);
}
