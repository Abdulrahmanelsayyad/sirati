# Sirati CV: buyer acceptance matrix (Beta)

**Prepared:** 2026-10-13. **Original baseline main:** `47b224b668dc99d87e2dcf0f9588a5725185ce32`.
Use **PASS / FAIL / BLOCKED / NOT RUN**, exact Git commit + deployed URL + tester + date. Older CI and user screenshots are supporting evidence, not proof of a new buyer deployment.

| Priority | Test / buyer evidence | Status and bounded evidence |
| --- | --- | --- |
| P0 | Buyer clone reconstructs source and builds successfully under buyer-controlled settings | PASS: Node 22 CI clean static builds on a8c52bc at root, /buyer-cv and /builder-tools; buyer-owned backend NOT RUN |
| P0 | Verify actual seller demo deployed SHA; never assume merge equals deploy | PASS: manual Pages run 38441357657, main 47b224b |
| P0 | Guest creates CV -> sign-in/up -> preserves exact draft -> saves -> reopens after fresh session | NOT RUN |
| P0 | Saved document remains unchanged when sample/template starts an independent draft | NOT RUN |
| P0 | Offline/network Save failure gives retry without duplicate creation or draft loss | PASS: blocked document writes, retained editor/session draft, retry and reload for both accounts on a8c52bc; new-document duplicate creation and full-device offline NOT RUN |
| P0 | Synthetic A/B accounts: authenticated UI and direct API deny cross-user reads/writes | PASS: real Staging accounts, both API and browser directions on a8c52bc; independent sign-off NOT RUN |
| P0 | Same-browser sign-out, account switch, session expiry and local draft privacy | PASS: logout/switch/scoped draft cleanup in 8 browser scenarios on a8c52bc; actual token expiry NOT RUN |
| P0 | Backup and tested restore for agreed documents and configuration | NOT RUN |
| P0 | Commercial chain of title, dependency licenses and third-party asset rights reviewed | NOT RUN |
| P1 | Arabic + English PDF from all advertised templates, including 2-5 A4 pages | PASS: existing automated core/extra-template and long-form matrix on a8c52bc; exact case limits in run 38457804314, physical devices NOT RUN |
| P1 | Native readers recover correct words, order, spacing, dates and punctuation; unsupported mixed scripts warn | PASS: supported automated Poppler/PyMuPDF fixtures on a8c52bc; joined mixed-script warning retained; no universal ATS claim |
| P1 | Android Chrome real device, desktop Chromium/Firefox/Safari; 360/390/1440 widths | NOT RUN |
| P1 | Photo JPEG/PNG/transparent input, same-file retry, error reporting | NOT RUN |
| P1 | Arabic RTL/LTR switching preserves form fields and correct PDF structure | NOT RUN |
| P1 | Career tools and Smart CV output factual/editable with no credential or ATS guarantees | NOT RUN |
| P1 | New buyer host/repository/base path, Supabase environment isolation, rollback plan | NOT RUN |
| P2 | Lighthouse performance/accessibility/SEO evidence from buyer-hosted build | NOT RUN |
| P2 | Inventory business metrics, monthly costs, legal privacy/cookie notices | NOT RUN |
| P2 | Seller demo video/screenshots using synthetic data only | NOT RUN |

## V32 consolidated candidate — 2026-10-14 (supersedes older current-state notes)

Current main verified as `cfaf128f9f5ed4678efbe60dc9741eff57ca81a7`.
PR #158 head `3457cdee2fc000c3f6650f5b8b500910a3afc4b1` is incorporated with
PR #149 buyer portability and account harness. Both feedback race fixes and
bilingual saved-PDF recovery are retained. No PDF engine or release guard change.
The PR head and its linked Actions are authoritative for this integration.

- PASS (local integration): clean production build and TypeScript, zero npm audit vulnerabilities;
  bounded client scan (43 files), account draft/duplicate/PDF boundary checks,
  10 verification contracts, 14 release guard mutation tests, 18 feedback invariants,
  owner navigation and 30 exported links/assets under `/sirati`.
- Historical PASS reused: #158 exact-head E2E/build/browser runs 38530124979,
  38530125026, 38530124946; #149 native PDF job 115511144392 in run 38459638026,
  real-account run 38459638239 and buyer matrix 38459638190. These are not
  mislabeled as tests of the consolidated head.
- FAIL / bounded limitation (#130): joined `الـICU/ER` and `الـACLS/BLS` remain
  unsupported. Existing PR #147 experiments already tested splitting and ISO
  ActualText: Poppler inserted spaces or reversed the Arabic prefix. Do not
  repeat or ship these failed approaches. Preserve the exact user data and
  fail closed; only the user may choose to separate abbreviations with spaces.
  Existing Arabic-Indic date export preserves numeric value via ASCII text-layer
  digits, not identical Unicode code points. No universal ATS/PDF-UA claim.
- FAIL (release qualification): historical PDF-only scope guard rejects broader
  product changes. Rendering and release authorization are separate. The guard
  is unchanged; a separately reviewed general release scope is required.
- BLOCKED: physical Android, distinct human reviewer, owner security decisions,
  and buyer-owned backend bootstrap/restore acceptance. Native feedback live
  backend acceptance is NOT RUN; synthetic browser evidence is separate.
- No production merge/deployment, Auth/RLS changes, customer-data writes or new tracking.

### Current read-only security evidence and precise owner decision

Staging migrations through `20261013193334` inspected; no migration reapplied.
`rls_auto_enable()` denies anon/authenticated EXECUTE. Both analytics functions
are owned by postgres with fixed search paths; summary checks an internal owner
allowlist and collection validates route/type with 80/session and 15,000/day
quotas. Caller-chosen session IDs still permit quota abuse. CV policies bind
SELECT/INSERT/UPDATE/DELETE to auth.uid(); UPDATE retains WITH CHECK. Feedback
owner access uses app_metadata, not user-editable user_metadata.

Analytics is unnecessary for this sale. Recommended owner-approved action on
**Staging only**, not executed: REVOKE EXECUTE from PUBLIC, anon, authenticated
on `public.sirati_track_event(uuid,uuid,text,text)` and
`public.sirati_analytics_summary(integer)`. Retain functions, data and internal
retention job. Then recheck grants/advisors and CV/feedback regression. This
removes optional RPC access without deleting records or enabling tracking.

Production advisor reports only leaked-password protection disabled. Production
organization is currently **Free**; Supabase's current password-security docs
limit this protection to **Pro and above**. Under the zero-cost constraint the
owner must explicitly accept this residual limitation, or separately authorize
an upgrade and Auth setting change. No upgrade is required by the CV product.
Source: https://supabase.com/docs/guides/auth/password-security

**NO-GO for unconditional final release acceptance.** Keep #130, #99 and #24 open
until their respective bounded acceptance, owner and reviewer decisions exist.

## Current source-linked evidence (not a substitute for buyer tests)
- Existing build and synthetic E2E matrix: [QA workflow](../.github/workflows/qa.yml).
- Explicit, manually gated deploy: [Pages workflow](../.github/workflows/pages.yml).
- Guest sign-in/save and duplicate protection history: [PR #135](https://github.com/Abdulrahmanelsayyad/sirati/pull/135), [PR #136](https://github.com/Abdulrahmanelsayyad/sirati/pull/136).
- Saved-CV example overwrite protection: [PR #143](https://github.com/Abdulrahmanelsayyad/sirati/pull/143).
- Joined Arabic/English PDF warning: [PR #148](https://github.com/Abdulrahmanelsayyad/sirati/pull/148). [PR #147](https://github.com/Abdulrahmanelsayyad/sirati/pull/147) failed strict native-reader parity and was not merged.
- Privacy/security review: [Issue #24](https://github.com/Abdulrahmanelsayyad/sirati/issues/24), [#25](https://github.com/Abdulrahmanelsayyad/sirati/issues/25), [#99](https://github.com/Abdulrahmanelsayyad/sirati/issues/99). Legacy issues may include resolved work; reconcile with the exact build before final acceptance.

## Exit rules
1. A release is **not** marked buyer-ready if any P0 row remains FAIL or NOT RUN.
2. The buyer must be able to build and independently operate the purchased software without seller personal credentials.
3. The final agreement must explicitly state which code/IP, marks, source files, domain(s), datasets, accounts, licenses, third-party services and transitional support are included/excluded.
4. Payment/escrow, legal assignment, credential rotation, verified migration and written acceptance occur only after both parties authorize them.

**Non-destructive protocol:** All first-pass checks must use synthetic fixtures or read-only repository metadata. No production database changes, customer exports or account transfers through this document.


## Historical V29 evidence boundaries (superseded where later evidence is explicit)
- **PASS (bounded local):** clean main build at `/buyer-cv`, generated route/asset checks, 10 verification-runner tests, synthetic account draft/logout/session and stale-write boundaries, duplicate protection and PDF boundary checks. These are not real account or native-reader tests.
- **BLOCKED:** real two-account/UI/API isolation and buyer backend bootstrap; no dedicated authorized QA credentials supplied or customer accounts used.
- **NOT RUN locally:** browser/E2E and native PDF reader matrix. Managed environment has no supported browser-control skill. The buyer CI workflow runs existing E2E/print smoke at root and `/buyer-cv`; inspect exact-head results before promoting any row.
- **NOT RUN:** independent security sign-off, buyer domain deployment, restore drill, legal/title acceptance, physical Android/Safari/Firefox and current native PDF long-form matrix.
- **P0 outstanding:** buyer-controlled backend and two-account acceptance; independent security gate; agreed backup/restore and ownership/license scope.
- **P1 outstanding:** current native-reader mixed-script/long-form acceptance and real-device coverage; staging is older than main and cannot serve as current release evidence; transitive dependency lock reproducibility.
- **P2 outstanding:** buyer cost/usage measurements and synthetic presentation assets.
- **Decision: NOT READY for transferable buyer acceptance.** The local frontend build is reproducible, but does not establish independent operation of the authenticated product. Do not close #24/#25/#99 from synthetic tests.


## V30 integration evidence (2026-10-13)
- Main at that inspection was `47b224b668dc99d87e2dcf0f9588a5725185ce32`. Both #149 and #151 were open, draft and unmerged at inspection.
- #151 exact head `66b21bb90b4e12e444235ab40cb5103fdd395ae0`: E2E [38446318062](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38446318062), Pages build [38446318015](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38446318015), and Staging build-only [38446318029](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38446318029) PASS. These are not acceptance of the combined candidate.
- PDF-only [38446317998](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38446317998) FAIL: production build and 42 PDF-boundary regressions passed, then `pdf_release_guard.py:39` rejected files outside the historical V26 PDF-only scope. Detailed browser/native-reader PDF steps were skipped, not passed. Guard and allowlist remain unchanged; this does not establish a rendering defect or qualify a new release.
- Reconciled three E2E merge conflicts using #151's local-only dual-variable configuration and strict link boundary, while retaining #149's synthetic logout base-path substitution. The existing buyer matrix now also builds `/builder-tools`.
- PASS locally on combined source: clean custom-output `/builder-tools` build with Node 24.19.0, 29 exported link/asset targets, route normalization, 10 verification-runner tests and bounded synthetic verification. Node 22/browser acceptance must use the combined head's CI.
- BLOCKED locally: browser/PDF reader regression execution because the Playwright browser binary is absent. `pdftotext` alone cannot validate a PDF that was not generated. Physical Android and all-template native-reader coverage remain NOT RUN.
- BLOCKED: authenticated buyer bootstrap, synthetic A/B browser/direct API isolation and real session-expiration checks; no dedicated buyer environment/account fixtures supplied. Source checks do not close #24/#25/#99.
- NO-GO for final buyer acceptance: backend and independent security/restore/legal gates remain open, and historical PDF-only source qualification still fails. No merge or deployment authorized or performed.


## Verified Staging account acceptance — 2026-10-13
- **PASS**, exact tested code `172b56efb30041fd4ba459d1eb74f299d2496df2`: [real-account CI run 38456172777](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38456172777), job 115499354419. Local Node 22 static frontend connected only to Sirati-Staging (`ykfxcxhozqqsvhtdyxho`); real password login for two owner-designated synthetic accounts. This is not buyer-owned backend bootstrap or production acceptance.
- Both directions of direct API cross-account document SELECT/UPDATE/DELETE denied; own document create/update/read/delete passed. Original synthetic rows remained unchanged after cross-account probes.
- Browser A-to-second-account login/logout, own-document reopen, document-list/profile isolation, direct foreign-document URL and prior draft removal passed at 360/390/1440px through the menu, plus 390px through Documents > Account details > Sign out. The latter requires opening the collapsed details control; the test was corrected without removing that scenario. Account drafts were observed in sessionStorage and checked for absence after logout; no marker persisted in localStorage.
- Both run-created synthetic documents deleted and absence verified. Only public client key plus dedicated account passwords used; no privileged key, live Auth/RLS/schema change or deployment. Passwords remain in GitHub Secrets; no secrets or real CVs are part of this handover.
- **NOT RUN:** real token expiration, offline browser save/retry, reverse browser switch, all remaining PDF/native-device cases and independent security sign-off. This bounded evidence does not close #24/#25/#99 wholesale. Buyer-owned provisioning, restore drill and legal acceptance remain outstanding.
- Subsequent documentation-only commits record this evidence; do not relabel the linked test as having run on an untested later SHA.


## V30 follow-up — exact candidate a8c52bc
- Product main `bd38ea06b5dc47df8e65218f4f5a5e31946cbb46` is incorporated into candidate `a8c52bc26b19d86944e3f5de6a5af54ae5bae875`. Main subsequently advanced to `6b98f14d67cfec9f1a5c3e60297b65ee6a4d3de6` with a separate mock-HTTP feedback acceptance script/workflow step; those two QA-only files are not part of this tested candidate. Existing native feedback/dashboard changes are preserved; `docs/FEEDBACK_RLS_REVIEW.sql` remains a separate reviewed buyer setup requirement, not proof it was applied to a live backend.
- **PASS:** [real-account run 38457804295](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38457804295), job 115504916474: real Staging password login, both directions of direct API read/update/delete isolation, own operations, and eight shared-browser scenarios. Each direction covers menu logout at 360/390/1440px and Documents account-details logout at 390px; list/profile/foreign-document URL and session-draft cleanup assertions remain enabled.
- **PASS:** both accounts at 390px retain editor and session draft when actual document write requests are aborted, then explicitly retry, save a version and reopen the persisted edit after reload. This tests targeted network failure on an existing synthetic document, not full-device offline behavior, first-save duplication or token expiry.
- Both synthetic documents were deleted and absence checked; a subsequent read-only Staging aggregate query found zero `SIRATI-SYNTHETIC-%` documents. Existing version foreign keys use `ON DELETE CASCADE`. No production data, Auth/RLS configuration or schema was changed.
- **PASS:** [Node 22 buyer matrix 38457804512](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38457804512) at root, `/buyer-cv`, `/builder-tools`, including generated-source verification and existing E2E/PDF smoke. [E2E 38457804223](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38457804223) also passed; its PR merge tree `79daf95cf0f26433530b0b95ae4689e5a6604168` was verified byte-identical to the candidate tree.
- **PASS:** [Staging build-only 38457804257](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38457804257). Pages run 38457804122 completed its build step but was CANCELLED overall; it is not a passing workflow or a deployment.
- Corrected the QA login wait to inspect URL pathname instead of matching `?next=/documents`; wait for interactive login state and authenticated document cards before account actions. Earlier transient UI timeouts are not relabeled as security failures or hidden with retries/skipped assertions.
- The unchanged PDF release-scope guard and detailed PDF regression now run as independent mandatory jobs. A source-scope failure still fails the whole workflow; no `continue-on-error`, allowlist expansion or assertion removal. Local guard mutation regressions (14) and verification runner tests (10) pass. Detailed PDF status is recorded separately below.
- **NOT RUN / BLOCKED:** real token expiration, full-device offline/reconnect, buyer-owned backend provisioning and restore drill, independent security acceptance, physical Android/other browser coverage and legal/IP transfer. The newer feedback backend needs its own live acceptance; this CV account test does not certify it. No merge/deployment performed or authorized. **NO-GO** for final buyer acceptance.
- Documentation-only follow-ups record the exact tested source above; do not relabel those results as a test of a later SHA.

- **PASS (detailed PDF job):** [run 38457804314](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38457804314), `isolated-pdf` job 115504916830, exact source `a8c52bc26b19d86944e3f5de6a5af54ae5bae875`. Production reconstruction, boundary/security source checks, synthetic PDF generation, independent text/font/A4/visual checks, long-template readers, 24 extra variants, guest journey and Staging smoke all passed. Poppler and PyMuPDF recorded 324 PASS / 0 FAIL long-template observations; Arabic sentence punctuation, numeric values and RTL raster checks passed. Existing joined mixed-script warnings remain; physical devices and universal ATS acceptance are not claimed.
- **FAIL (release qualification):** the same run's `protected-release-scope` job 115504916937 rejected non-PDF changes against the historical V26 pin at `qa/pdf_release_guard.py:39`. The overall workflow remains FAIL despite rendering regression PASS. A new reviewed release scope/baseline is required before release qualification; do not remove this gate or call the workflow green.
