# Issue #41 — Frozen paid CV snapshot migration: DESIGN REVIEW ONLY

**Status:** DRAFT COMMITTED TO EXPERIMENTAL GITHUB BRANCH. NO MIGRATION APPLIED. NO SITE/STAGING DEPLOYMENT.

Owner-approved commercial rules:
- **EGP 50 purchases one frozen CV revision.** The same revision can be downloaded repeatedly after trusted manual approval, while the document/account still exists.
- Editing the CV creates a *different* revision requiring a new EGP 50 order for a clean official export.
- **Deleting the original CV also deletes its attached order(s) and frozen paid version(s)**, but the UI must clearly warn the customer and get their confirmation first.
- Deletion can stop *future in-app downloads*, not erase PDF copies already saved on the user's devices.

## The SQL file

`supabase/migrations/20261009100000_freeze_pdf_order_snapshot.sql`

**Additive, transactional draft only:**
1. Abort unless PDF RLS is enabled and the already-deployed Issue #26 restrictive pending/EGP 50 INSERT policy exists. Do not weaken the restriction.
2. Create a new **non-Data-API-exposed** `sirati_private` schema and `pdf_order_snapshots` table. Each record is keyed 1:1 to its `pdf_orders.id`.
3. Copy server-read values from `cv_documents.data`, `template`, `language`, `updated_at` under a row lock when a **new** pending EGP 50 order is inserted. The trigger and snapshot INSERT occur in the same transaction. Failure aborts order creation.
4. Deny client SELECT/INSERT/UPDATE/DELETE on private snapshots, enable RLS defense in depth, grant *read only* to trusted server `service_role`; function uses a fixed `search_path` and is not publicly callable.
5. Snapshots inherit `ON DELETE CASCADE` through `cv_documents -> pdf_orders -> pdf_order_snapshots`. User delete of the parent CV clears the related paid versions and order references at the database level. **Never change ON DELETE to RESTRICT without new UX/security review.**
6. Legacy rows receive **no invented backfill** and are **not** eligible for trusted official export without separately documented recovery.

No changes to `pdf_orders` amounts/status/review data, RLS policies, public customer grants, Staging/Production settings, or customer CV data. No changes to existing payment flow are deployed.

## Critical integration requirements before any future Staging activation

- **Save-before-pay:** UI must commit and confirm all latest CV data, image, template choice and language in `cv_documents` BEFORE creating `pdf_orders`. Otherwise snapshot captures the last *saved* CV, not the unsaved browser edits.
- **Renderer completeness:** Existing CV avatar and layout assets may live outside `cv_documents.data`. Audit and explicitly snapshot all render-relevant inputs, pin chosen template/renderer version, and verify Arabic RTL and ATS text extraction. Current draft captures only persisted data, template, language and source_updated_at; NOT proven complete.
- **Private export read:** `sirati_private` must NOT be exposed via PostgREST. A trusted server may use approved direct DB access (appropriately scoped) or a carefully reviewed, narrow API. The existing Netlify POC **does not** read this table or output a real customer CV. Never embed service-role/DB credentials in browser, GitHub source, tests or logs.
- **Official entitlement check:** verify current JWT and order, owner, document, `approved`, EGP 50, trusted approval timestamp, matching snapshot order/owner/doc, and no deleted/revoked entitlement; render exclusively from frozen data. No trust in client-supplied snapshot, amount, status, HTML or order timestamp.
- **Existing old orders:** Staging last read-only count: 3 orders (2 approved synthetic, 1 pending); Production: 1 pending. All pre-migration; they do NOT get a snapshot. Do not silently point them to latest CV or accidentally refuse a real paid request without support/reconciliation plan. This needs a manual rollout transition.
- **Revision retention/deletion:** Parent-delete CASCADE clears trusted copy. User-saved files on their own devices remain; don't promise remotely deleting existing downloads. Update privacy/terms and deletion UX as needed.
- **Version/hash:** If future changes to the renderer affect appearance, add an immutable template/renderer asset manifest or stored final PDF. Merely freezing JSON doesn't guarantee byte-for-byte identical PDF after deployment.

## Required Arabic deletion confirmation (UX NOT implemented by SQL)

Before deletion show a dialog with destructive styling, the correct CV title and explicit confirmation:

> **تأكيد حذف السيرة الذاتية**
>
> حذف هذه السيرة الذاتية سيحذف أيضًا كل النسخ المدفوعة المرتبطة بها وطلبات PDF المحفوظة، ولن تتمكن من تحميلها مرة أخرى من Sirati بعد الحذف.
>
> الملفات التي سبق تحميلها على جهازك لن تُحذف تلقائيًا.
>
> هل تريد حذف السيرة الذاتية نهائيًا؟

Buttons: **إلغاء** (safe default) / **حذف السيرة والنسخ المدفوعة** (deliberate second action). Block double submission. Never auto-delete on selecting CV. If permission/access fails, no mutation.

The warning is a UI and QA release requirement; raw API deletion by an authenticated owner remains permitted and cannot itself display dialogs.

## Future review/isolated Staging QA plan (NOT RUN)

After an independent reviewer signs off and the owner authorizes **Staging database only**:
1. Preflight actual schema/RLS/current migration versions, pending and approved counts, backup/recovery, concurrent writes and customer flow. The Supabase Free plan may lack restorable backups; a policy-text snapshot is not a data backup.
2. Apply on Staging inside a transaction. Confirm private schema NOT in Data API; test role grants, lack of public-function execution, and actual trigger behavior.
3. Synthetic two-user A/B: owned pending order creates **exactly one** snapshot of persisted data; client cannot read/update/delete snapshots; changing current CV and saving later does not alter snapshot; repeat download returns same purchased revision.
4. Fail closed for unauthorized/foreign CVs, user spoofing, altered amount/status/review timestamp, requests without a persisted CV; validate concurrent update/order capture consistency; test overlong/malformed CV data safely.
5. Approve synthetic order via trusted reviewer; rejected/pending never export; edited version requires **new paid order**.
6. Delete CV after explicit dialog; verify DB cascades delete **all** its orders and snapshots; verify another account's CV and snapshots untouched. A downloaded local PDF cannot be revoked.
7. Legacy orders remain intact and unbound. Prove manual reconciliation protocol without inventing a snapshot.
8. PDF layouts: English/Arabic, all templates, mobile, A4, very long content, text extraction and image rendering. Reuse existing unrelated passing tests rather than rerunning them indiscriminately.
9. Security and QA signoff exact SHAs, then seek **separate** production SQL / merge / deploy approvals. GitHub Pages push to `main` triggers deploy.

## STOP / rollback and recovery

- If proposed DDL fails before COMMIT, transaction rolls back, but still inspect schema and migration history; don't assume a rollback without reading live metadata.
- If the new trigger prevents customer orders, first **pause new order submission** and capture logs; fix forward without weakening the existing Issue #26 guard. Never drop the restrictive insert policy to restore orders.
- Before any authorized rollback, prevent new order creation and generation/downloads. Do NOT drop `sirati_private.pdf_order_snapshots`: paid snapshot rows could be irrevocably lost. Safely disabling the capture trigger is a separate owner-approved emergency action **only while new orders are paused**. Restore processing after testing.
- If reverting app code, do it separately from schema. Data deletion or dropping new private tables requires explicit owner approval, export/recovery plan and privacy review.
- Supabase migration history in this repo is *not identical* to Production's actual applied migration IDs. Compare recorded history before any automated CLI `db push`; never assume this SQL file is safe to bulk-apply with old migrations.
- Do not run or test this SQL against any live project until owner explicitly authorizes. A GitHub branch commit **is not permission to execute the migration**.

**Release status:** NOT READY for paid customers; the official authenticated PDF renderer, snapshot entitlement integration, deletion dialog and integration tests are still missing.
