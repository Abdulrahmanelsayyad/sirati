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
