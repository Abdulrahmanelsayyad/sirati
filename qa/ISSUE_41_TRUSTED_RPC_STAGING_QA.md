# Issue #41 — Trusted RPC and Official PDF: isolated Staging QA checklist (DRAFT ONLY)

Target branch: `feat/issue-41-synthetic-server-pdf-poc`.
Target migration: `supabase/migrations/20261009120000_issue41_trusted_snapshot_rpc.sql` (**NOT applied**).
Existing #42 Staging migration history ID: **`20261009031951_issue42_freeze_pdf_order_snapshot_atomic_revision`**. Do not infer deployed IDs from repository filenames.

## Gate before any new live test

- [ ] Independent Security review of **exact source SHA**, the new public RPC's SECURITY DEFINER ownership/search_path/EXECUTE grants, least privilege, exposed-schema configuration, and server-only secret handling.
- [ ] Independent QA reviewer assigned (not the code implementer); confirm staging branch SHA and no drift in the 20 previously passed mocked tests.
- [ ] Owner gives separate explicit approval for **Staging-only** DDL AND, separately, any staging site/backend deployment, configuration and live use of a staging secret. This document authorizes neither.
- [ ] Read-only Staging preflight: inspect actual schema, pg_proc owner/permissions, pg_policies, RLS, current migration ledger. Save a recoverable logical backup; verify rollback plan. **Never run `supabase db push` blindly** and never touch Production.
- [ ] Use test-only A and B identities, fake CVs and dummy references. No real payments, credentials, customer snapshots or JWTs in repository/CI logs.

## Test matrix: SQL integration (only *after* authorized Staging DDL)

| ID | Input and caller | Expected |
|---|---|---|
| R01 | Catalog: public.sirati_pdf_snapshot_for_server(uuid,uuid) signature/owner/grants | SECURITY DEFINER owned by reviewed privileged DB role, search_path empty, EXECUTE only service_role; no PUBLIC/anon/authenticated function privilege |
| R02 | anon directly attempts RPC for synthetic approved A order | 401/403 permission denial; **no JSON snapshot** |
| R03 | authenticated A directly attempts RPC for own approved order | 403 / permission denial; **no JSON snapshot**, even with correct ids |
| R04 | authenticated B directly attempts RPC for A approved order | 403 / permission denial; **no JSON snapshot** |
| R05 | trusted server service_role calls RPC with A approved order and **verified A ID** | Exactly one immutable record, owner/order/document/revision match |
| R06 | trusted service_role calls with A order but B ID | NULL; no A fields returned |
| R07 | trusted service_role calls B order but A ID | NULL |
| R08 | trusted service_role calls pending/rejected/unapproved/price not 50/approval time null synthetic order | NULL; never an official PDF (use rollback-only fixtures; don't modify preexisting paid rows) |
| R09 | historical approved order with expected_revision=NULL and no frozen snapshot | NULL; no retrospective snapshot/backfill |
| R10 | order with mismatched snapshot owner/document/source_revision or unsupported schema version | NULL; construct only in isolated fixture transaction, rollback |
| R11 | deleted parent document/order/snapshot / dangling id | NULL; deletion cascade intact |
| R12 | over-limit snapshot payload (> 131072 bytes) | NULL or safely rejected; enforce upstream/body/memory limits |
| R13 | direct anon/authenticated SELECT of sirati_private.pdf_order_snapshots and private schema API probe | permission denied / private schema not exposed |
| R14 | verify privileges and grants on underlying public objects and definer role | Only intended function can read private rows; no unexpected direct public export |

Record real HTTP status, SQLSTATE, selected role and schema, row counts, timestamp and redacted trace for each. Distinguish 401/403 permission-denied from an HTTP 200 JSON `null` returned by the *privileged* RPC.

## Test matrix: actual server route (only after separate deployment/config approval)

| ID | Input | Expected |
|---|---|---|
| H01 | Route disabled, wrong BRANCH, wrong Supabase URL, missing/invalid sb_secret_ key | 404; zero upstream requests |
| H02 | Invalid/missing/expired user JWT | 401/503; no privileged RPC call |
| H03 | Malformed/oversized body, extra fields or arbitrary CV/status/price/customer ID | 400; no RPC |
| H04 | Valid A JWT, approved A order and supported frozen Compact ATS English snapshot | 200 PDF with ordered snapshot's content, A4 and extractable text |
| H05 | Valid B JWT, A order | 403; no PDF |
| H06 | Pending, rejected, unbound legacy, missing/deleted order | 403; no PDF |
| H07 | Mutate A current CV *after* paid order: repeat original order download | Identical frozen revision/content, not current CV, with no duplicate payment |
| H08 | Unsupported Arabic, profile photo or other seven template variants | 422; no corrupted/downgraded PDF; remains a release blocker |
| H09 | Timeout, malformed server JSON, oversized RPC response | 503; no PDF; no secrets or PII in logs |
| H10 | Server-to-PostgREST credentials | `apikey: sb_secret_...` on trusted backend only; **no** `Authorization: Bearer sb_secret_` header; bearer JWT only for end-user Auth verification |
| H11 | Repeat downloads and concurrent requests | Identical immutable content, no new order or snapshot; rate-limit/cost risk assessed separately |
| H12 | Actual two-tab Builder flow and Android/mobile customer UX | Independently signed off before release; not asserted by existing HTTP-only #42 evidence |

**Environment hygiene:** staging secret only in protected server runtime config after explicit owner approval, never in browser bundles, screenshots, QA artifacts, GitHub comments, HTTP logs or URLs. Do not create or rotate secrets as part of this document.

## STOP / final decision

Stop immediately on unauthorized snapshot disclosure, direct client EXECUTE, wrong version, regression of #42 atomic safeguards, logging of credentials, unsupported mandatory CV content, or an unsafe deploy plan. Document `PASS / FAIL / NOT RUN / BLOCKED` and root cause. Rollback only under separate owner approval using the saved plan, without dropping paid snapshots or the #26 RLS policy.

**Expected status at time of writing:** all R/H live cases are **NOT RUN**. Existing 20/20 Node CI is a mocked-code result, not evidence of real DB authorization. Parent #41 customer launch stays **BLOCKED** until independent review, explicitly authorized Staging tests and Arabic/photos/all-template parity are complete.
