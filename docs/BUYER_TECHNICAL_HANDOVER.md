# Sirati CV: buyer technical handover (Beta)

**Snapshot:** 2026-10-13 | **Reference main SHA:** `47b224b668dc99d87e2dcf0f9588a5725185ce32`
**Purpose:** a transparent technical checklist for a possible asset transfer. This document is not a claim that the product is production-certified, profitable, or already sold.

## Product and included code
- Free Arabic/English CV builder, live preview, templates, browser PDF export, editable role-aware writing suggestions, CV readiness checks, and career tools; see [README](../README.md).
- Stack: Next.js / React / TypeScript static export; GitHub Pages deployment; Supabase-backed accounts and saved documents when correctly configured.
- Source is reconstructed from split encoded archive parts and ordered Python patch scripts, then built using `NEXT_PUBLIC_BASE_PATH=/sirati bash build.sh`. This is a real maintainability cost, not a standard clean-source repository.
- GitHub repository is **public but proprietary**, per [LICENSE](../LICENSE). A sale does not automatically transfer third-party component/font licenses or legal ownership; use a signed asset purchase/IP assignment agreement.

## What is not automatically transferable
- `https://abdulrahmanelsayyad.github.io/sirati/` is tied to the seller's GitHub Pages namespace, **not** a standalone domain asset. Buyer should deploy the product under a buyer-controlled repository, domain and hosting account.
- Seller personal GitHub, email and Supabase credentials/accounts are **excluded** unless separately agreed and legally transferable. Never send credentials in the repository, public PR, listing or chat.
- Real users, CV content, authentication data, invoices/payment history and analytics are **not included by default**. Any lawful migration must have a separate approved scope, privacy/legal review, backup and validation.
- Historical payment/order code or tables may remain but the currently documented product policy is free; do not market recurring revenue.

## Confirmed project controls and limitations
- `.github/workflows/pages.yml` builds on PR/main; production deploy requires explicit `workflow_dispatch` approval. **Merged main != verified live site**.
- Automated QA includes reconstructed builds, browser E2E, mobile/print and synthetic PDF checks. Green CI does not certify real-device compatibility, direct production access isolation or legal compliance.
- [PR #148](https://github.com/Abdulrahmanelsayyad/sirati/pull/148) merged a bilingual PDF preflight warning for joined Arabic/Latin tokens. Underlying exact-text export remains unsupported for certain tokens; [PR #147](https://github.com/Abdulrahmanelsayyad/sirati/pull/147) was closed unmerged following native-reader failures.
- [Issue #25](https://github.com/Abdulrahmanelsayyad/sirati/issues/25) tracks historical shared-browser account draft confidentiality questions. Later session-scoped cleanup exists; independently verify the current shipped revision and close only on evidence.
- [Issue #24](https://github.com/Abdulrahmanelsayyad/sirati/issues/24), [Issue #99](https://github.com/Abdulrahmanelsayyad/sirati/issues/99), and [Issue #113](https://github.com/Abdulrahmanelsayyad/sirati/issues/113) track security/QA release gates; some text refers to older commits and requires fresh evidence rather than being treated as a current exploit.
- Searchable/selectable PDF and CV quality guidance are **not an ATS certification or hiring guarantee**.

## Buyer-controlled reproduction procedure
1. Clone the repository in a disposable environment with Node.js 22, Python 3, npm, `unzip`, `base64` and Bash.
2. Run `NEXT_PUBLIC_BASE_PATH=/sirati bash build.sh` in a fresh checkout; log the exact commit and output path.
3. Independently review any bundled font and third-party dependency licenses before redistribution.
4. Configure a **separate buyer-owned test Supabase project** through an approved process; do not point tests to seller production or copy customer data.
5. Verify browser launch, registration, create/edit/save/reopen, document separation, Arabic/English, mobile widths and PDF text extraction.
6. Migrate only agreed assets via written transfer inventory. Rotate credentials after any authorized handover; document DNS/hosting changes, rollback and acceptance.

## Conditions to call this buyer-ready
- Confirm **actual deployed SHA** for seller demo and a separately verified clean buyer build.
- Obtain independent security/privacy and QA acceptance on the relevant exact SHA, including synthetic two-account browser + API isolation.
- Provide reproducible source/build/deploy, license inventory, backup/restore runbook and owner-approved transfer agreement.
- Disclose lack of verified revenue/traction if that remains the case, as well as ongoing issues.
- Complete [Buyer acceptance matrix](BUYER_ACCEPTANCE_MATRIX.md); any unperformed checks must remain **NOT RUN**.

**No credentials, keys, customer data or financial statements belong in this public handover file.**


## V29 verified deployment and portable build
- Seller Production: GitHub Actions manual deploy [38441357657](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38441357657), success for the reference main SHA above. This session did not deploy.
- Netlify site `sirati-staging-elsayyad`: published deploy `6acbd1e2b0b5a0b15a43375b`, commit `25b29f883edfd09797bbc974c0acf2224844479e`, branch `fix/pdf-mixed-script-export`, published 2026-10-11. **It is not the current main demo.** Do not treat its mixed-script exporter as accepted main behavior.
- A fresh clone reconstructed and built successfully locally using `/buyer-cv` without Supabase variables. Local runtime was Node 24.19.0; the documented Node 22 runtime is exercised by the new buyer CI matrix, not inferred from the local result.
- `.github/workflows/buyer-portability.yml` checks the exact PR head on Node 22 at root, `/buyer-cv` and `/builder-tools`, including existing synthetic E2E, EN/AR 360/390/1440px and print/PDF smoke. No publishing or backend credentials. Consult the latest head's run, not an older green run.
- Analytics route normalization now uses the configured base path and retains its route allowlist. Analytics remains OFF. The previous hardcoded `/sirati` misclassified buyer-prefixed routes if analytics was enabled.

### Reproduction and hosting procedure
1. Record `git rev-parse HEAD` and use a clean clone of the buyer-authorized source revision. Install the documented build tools.
2. In a clean shell with no seller environment variables, run:
   ```bash
   NEXT_PUBLIC_BASE_PATH=/buyer-cv NEXT_PUBLIC_ANALYTICS_ENABLED=false bash build.sh
   python3 qa/verification.py site-src/sirati-cv-source --output /tmp/buyer-verification.json
   python3 qa/buyer_portability_check.py site-src/sirati-cv-source /buyer-cv
   ```
   For a custom-domain root use `NEXT_PUBLIC_BASE_PATH=''` and pass `''` to the portability check. The output directory contains the root of the app; the host must mount it at the configured prefix. Use directory-index/trailing-slash support, not a blanket SPA rewrite that hides missing assets.
3. Run `npm run typecheck` inside the generated source. Preserve the resulting lockfile and tool versions with the candidate: the current process uses `npm install`, so byte-for-byte dependency reproducibility is **not established**.
4. Configure buyer hosting to run `bash build.sh`, publish `site-src/sirati-cv-source/out`, and use the buyer base path. **Do not import the existing `netlify.toml` or generated `render.yaml` unchanged:** they identify seller backends. `qa/render_staging_build.sh` deliberately refuses other projects; it is not the buyer installer. Keep current seller protections intact and prepare buyer settings in a separate buyer repository.
5. The current Pages workflow likewise hardcodes the seller base path/backend; a fork needs its own reviewed workflow variables. No buyer repository/domain was created or deployed in V29.
6. The minimal frontend needs no backend to open the guest editor. Cloud accounts/save/restore and the authenticated PDF journey require a separately approved buyer Supabase setup. Review reconstructed `supabase/schema.sql` together with tracked `supabase/migrations/`; do not blindly apply staging analytics migrations. Full backend bootstrap, Auth redirect allowlist, grants/RLS, email delivery and two-account acceptance remain **BLOCKED / unverified** until dedicated buyer QA fixtures are available. Never copy seller Auth users or customer rows.
7. Only publish after owner authorization, then execute the acceptance matrix against the resulting exact revision and URL.

### Rollback and acceptance
- Retain the last accepted static artifact, revision, dependency lockfile and a non-secret record of base path/public environment settings. Revert by republishing that exact artifact to the same mount point after approval, then verify home/templates/builder/auth and a synthetic saved CV.
- Static rollback does not roll back database migrations. No database migration is part of V29. Any future database change needs a separately tested backup/restore and rollback plan before execution.
- Verify a buyer build has no seller Supabase host in emitted JS; validate assets, internal links and Auth redirects on the buyer origin. Test synthetic account A/B UI and direct API isolation before acceptance.
- A local build and green CI are not a deployed buyer environment or independent security sign-off.

### Asset and operating inventory
| Asset / requirement | Handover status |
| --- | --- |
| Nine encoded source archive parts, ordered `.github/scripts` generators, `build.sh`, QA and workflows | Repository assets; retain all parts and generator order |
| Templates, CSS, rule-based writing suggestions | Included source; no claim that an LLM service is operating |
| Proprietary application and branding | `LICENSE` reserves ownership; transfer scope needs written owner agreement |
| PDF fonts | `assets/pdf-fonts/OFL.txt`, patched Naskh WOFF, Fontsource license; retain OFL and notices, review modified-font naming/redistribution rights |
| Cloud document schema/migrations | Source included; live database and account ownership excluded by default |
| Personal GitHub Pages URL, seller hosting/email/Supabase accounts | Not included as transferable software assets |
| Real CVs, credentials, analytics, payment records | Excluded; no export or migration performed |
| Hosting, build minutes, domain, Supabase and email | Buyer-selected recurring costs; actual invoices/usage and plan limits not verified; no fixed monthly-cost claim |
| Paid model APIs | No new API or paid service added |

Direct package inventory from the reconstructed V29 source and installed package metadata (license labels are not a legal review):

| Package | Version | Declared license |
| --- | --- | --- |
| next | 16.3.8 | MIT |
| react | 19.2.0 | MIT |
| react-dom | 19.2.0 | MIT |
| @supabase/supabase-js | 2.117.2 | MIT |
| html2canvas | 1.4.1 | MIT |
| pdf-lib | 1.17.1 | MIT |
| @pdf-lib/fontkit | 1.1.1 | MIT |
| @fontsource/noto-naskh-arabic | 5.3.0 | OFL-1.1 |
| @types/node | 22.10.5 | MIT |
| @types/react | 19.0.3 | MIT |
| @types/react-dom | 19.0.2 | MIT |
| typescript | 5.7.2 | Apache-2.0 |
| pdfjs-dist | 4.10.38 | Apache-2.0 |


Review transitive package licenses and preserve notices before redistribution; the direct inventory alone does not clear chain of title.

### Synthetic buyer demonstration
Use a fresh disposable browser profile with **Maya Hassan — Operations Coordinator**, email `maya@example.com`, fictional employer **Demo Operations Ltd**, role dates `2022–2025`, and a clearly labeled synthetic summary/experience. Do not claim credentials, quantified achievements or real employment. Demonstrate template choice, language switching, editing, reload and PDF review. Use dedicated authorized QA accounts for cloud save/download; do not substitute seller/customer accounts. Show the mixed-script warning with `تمريضICU` and explain the limitation without changing the user's CV. No real customer screenshot or demo video was created in V29.


## V30 integration and backend source inventory
The combined draft incorporates #151 into #149, preserving both QA URL variable names and rejecting conflicting values. Review #149 as the integrated candidate; do not independently cherry-pick its E2E edits against #151. `/builder-tools` joins root and `/buyer-cv` in the Node 22 buyer matrix. The PDF-only scope guard is intentionally unchanged; its historical release qualification is a separate unresolved gate, not a passed PDF test. See the acceptance matrix for exact historical run links and current limits.

Read-only inspection of reconstructed `supabase/schema.sql` and tracked migrations found:
- Core tables: `cv_documents`, `cv_versions`; legacy `pdf_orders` remains in the schema, although the product is free. Document policies bind SELECT/INSERT/UPDATE/DELETE to `auth.uid() = user_id`; version INSERT additionally requires ownership of the parent document. This is source evidence, not a live policy audit.
- `20261007131224_tighten_cv_data_api_grants.sql` removes anon table grants and narrows authenticated operations. The order-insert guard migration and analytics migration are separate concerns; do not blindly apply an incomplete subset or staging-specific configuration to a buyer database.
- No application Supabase Storage bucket calls were found in the reconstructed app/lib/components scan. Profile images use the existing CV data path; no buyer storage bucket requirement has been established. Confirm against the final transfer revision.
- Buyer setup still needs a reviewed empty-project schema/migration plan, Auth email delivery and confirmation behavior, buyer Site URL and the exact buyer-origin plus base-path `/auth/confirm` redirect allowlist. The current signup code constructs that redirect from the browser origin and `withBasePath`; successful real email confirmation remains untested.

| Build variable | Buyer requirement |
| --- | --- |
| `NEXT_PUBLIC_BASE_PATH` | Empty for root, otherwise the exact hosting prefix without trailing slash |
| `NEXT_PUBLIC_SUPABASE_URL` | Buyer-owned test/production project endpoint as appropriate |
| `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` | Matching public client key; never a service-role/secret key |
| `NEXT_PUBLIC_ANALYTICS_ENABLED` | Keep false until separate security/privacy acceptance |
| `NEXT_PUBLIC_SITE_URL` | Present in seller Pages workflow; not found as a runtime consumer in inspected application files; review buyer workflow separately |
| `SIRATI_BUILD_DIR` | Optional fresh reconstruction destination; custom directory tested locally |
| `SIRATI_QA_BASE_URL` / `SIRATI_E2E_BASE_URL` | Local HTTP loopback test target only; when both supplied they must agree |
| `SIRATI_PDF_QA_FIXTURE` | Synthetic test builds only; do not ship fixture routes |

Buyer-owned backend provisioning, backup restore and ownership transfer remain BLOCKED or NOT RUN. Bounded real-account Staging RLS and authenticated document operations are recorded below; they do not certify a new buyer backend. No seller database, live Auth setting, hosting configuration or customer row was changed.


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
