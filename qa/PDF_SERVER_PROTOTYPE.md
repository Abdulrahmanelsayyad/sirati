# Issue #41 — synthetic server-side Compact ATS PDF POC

**Branch-only research artifact. No site integration, payment, database, storage, or deployment.**

`netlify/functions/pdf-prototype.mjs` emits one **server-generated**, one-page A4 PDF with embedded standard Helvetica text from a completely fictional English Compact ATS-like CV. It uses only the Node 22 runtime, without extra packages, Chromium, APIs, personal data or paid services.

## Local smoke test

```bash
node --test qa/pdf_prototype.test.mjs
node --input-type=module -e "import {writeFileSync} from 'node:fs'; import {renderSyntheticCompactAtsPdf} from './netlify/functions/pdf-prototype.mjs'; writeFileSync('/tmp/sirati-synthetic-compact-ats.pdf', renderSyntheticCompactAtsPdf())"
pdfinfo /tmp/sirati-synthetic-compact-ats.pdf  # expected: Pages 1, A4
pdftotext -layout /tmp/sirati-synthetic-compact-ats.pdf - # expected: extractable English words
```

## Safety / feature flag

The Netlify endpoint returns 404 unless **both** `SIRATI_PDF_POC_ENABLED=true` and `NEXT_PUBLIC_SUPABASE_URL=https://ykfxcxhozqqsvhtdyxho.supabase.co` are explicitly set. Even when enabled, it accepts only POST with the exact JSON string `{"synthetic":true}` and responds with a fixed fictional PDF; never accepts real CV content, arbitrary HTML or identifiers. Do not enable it on publicly accessible staging without a separate, narrow authorization.

## Not a solution to paid PDF authorization

No verified JWT, approved-order check, private download, version binding, rate-limit, production route, Arabic/RTL, embedded custom fonts, HTML/CSS parity or full set of templates is implemented. This does **not** demonstrate that Netlify can run Chromium or render the existing templates, nor guarantee Netlify runtime quota viability. It only tests the minimal dependency-free server-generated PDF alternative and Node feasibility. The live browser-print flow is unchanged. Before any paid-product launch, implement and independently test true server-side authorization and the full layout/ATS/RTL requirements; keep Issue #41 open.

**No deploy/merge/production changes are authorized by this POC.**


## Phase 2: authorization-gated synthetic PDF (code only, not deployed)

Source: `netlify/functions/pdf-auth-prototype.mjs`
Tests: `qa/pdf_auth_prototype.test.mjs`

This separate default-disabled function proves the intended **authorization sequence**, not paid CV issuance:
1. Require the staging project URL, explicit `SIRATI_PDF_AUTH_POC_ENABLED=true` and staging *publishable* API key in runtime environment (`SIRATI_STAGING_PUBLISHABLE_KEY`).
2. Require POST with Bearer token and exact `{documentId,orderId,synthetic:true}` UUID payload. Never accept client-provided price, status, document body or arbitrary HTML.
3. Send the token to Supabase `/auth/v1/user` to **verify** identity. Never trust a locally decoded JWT user ID.
4. Fetch `cv_documents` and `pdf_orders` through Supabase REST **as the authenticated user**, retaining database RLS. Check user, order, document linkage, amount=50, approved status, and nonempty/valid reviewed timestamp on the server.
5. Only on full approval does it return the **fixed fictional PDF** from Phase 1. All customer content is ignored. Other paths fail closed to 400/401/403/503, never PDF.

**This version is NOT a secure customer PDF export:** `pdf_orders` does not record a purchased `cv_version_id` or a canonical immutable CV snapshot. Version-based entitlements cannot be guaranteed until schema/product rules change through separate owner consent and testing. Also missing real CV template rendering, Arabic/RTL, private delivery, rate limiting/abuse controls, availability/quotas and live staging deployment.

Run only against locally mocked upstream responses; no test request should contact real Supabase:

```bash
node --test qa/pdf_prototype.test.mjs qa/pdf_auth_prototype.test.mjs
```

**Verification status (this branch update):** Code and tests have been committed to GitHub. Live Netlify and Supabase E2E tests were **NOT RUN**; unable to retrieve the private GitHub files into the separate runtime for local execution in this session. Do not claim the new tests PASS until CI or another reviewer executes the exact commit. The Phase-1 synthetic PDF test evidence predates Phase 2.

**Owner boundary:** No new Netlify environment variables, deployments, merges, Supabase settings, payment records or costs were authorized or changed. Staging activation must be separately approved.
