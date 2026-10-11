# Sirati PDF-only Production Release Candidate V14

Date: 2026-10-11. Owner: this V14 engineering session. Status: draft; no merge or deployment authorized.

## Locked inputs and scope

- Fresh Git remote read: main `54461f950554c18d64690331020596dcf79e43cb`.
- Approved Staging comparator: `78ab9519599bf3436fce4418b3fe7bdfdd8e56b7`.
- New branch `release/pdf-only-v14-20261011` starts from main; no Staging branch merge.
- Staging is 62 commits ahead with 23 changed paths. Completed #118/#119/#121/#122/#123 were merged to Staging, not main. #114 is an older PDF draft; it is not the latest exporter and is not merged or modified by this task. #115/#116 Analytics and #117 Modern headings stay separate.

| Runtime file | Exact change and dependency |
|---|---|
| `.github/scripts/pdf_text_layer_v19.py` | Port latest validated shared exporter, unchanged algorithm. Generates `lib/siratiPdfExport.ts`, pinned `pdf-lib` 1.17.1, fontkit 1.1.1, Noto Naskh Arabic 5.3.0, PDF.js 4.10.38 for tests, font-copy prebuild. Same-origin fonts; no CV uploads. |
| `.github/scripts/compact_ats_template.py` | Exactly 14 lines of Arabic-only list-marker CSS; preserve English markers. |
| `.github/scripts/prepare_pages.py` | Append exporter and gated synthetic fixture after unchanged V18 Save PDF auth gate. Existing source archive/reconstruction preserved. |

Dependency order: source archive -> existing prepare hooks -> V16 shared PDF caller -> V18 auth gate -> V19 exporter -> local fonts -> static build. Builder and My Documents continue calling the same exporter. No changes to their data, save or authorization logic.

PDF-only QA files carried from Staging: `qa/pdf_sections_fixture.py`, `qa/pdf_sections_check.mjs`, `qa/pdf_photo_check.mjs`, `qa/pdf_longform_check.mjs`, `qa/pdf_quality_check.py`, `qa/pdf_word_boundary_fixture.py`, `qa/pdf_word_boundaries_check.py`, `qa/pdf_metadata_fixture.py`, `qa/pdf_metadata_download.mjs`, `qa/pdf_metadata_check.py`, `qa/pdf_rtl_list_style_check.mjs`, `qa/pdf_rtl_numerals_bullets_check.py`.

New/adapted release QA: `qa/pdf_release_guard.py`, `qa/pdf_release_run.sh`, `qa/pdf_template_longform_check.mjs`, `.github/workflows/pdf-release-qa.yml`, this report. Tests use local `/sirati` and a pinned approved Staging comparator, never a real backend. Extend short fixtures to 360px and add long real-template markers. Fixed-baseline numeral comparison explicitly allows zero baseline failures; numeric correctness assertions remain strict. Original Staging workflow is not copied.

Explicitly excluded: all three Staging migrations, Analytics activation/retention/ACL changes, Supabase/Auth/RLS/payments/secrets, Staging smoke edits, unrelated feature/template-heading work and Staging documentation. Existing main `netlify.toml` is already a Staging-only configuration; it is unchanged and is not used by GitHub Pages or isolated release QA.

## Test evidence

Results below distinguish execution from planned checks. Final exact PR CI links and counts are recorded in the PR description after execution.

| Check | Status | Evidence / limit |
|---|---|---|
| Scope/source reconstruction and exporter parity | PASS | `pdf_release_guard.py`: original prepare preserved, algorithm equals approved Staging; allowlisted diff. |
| Production-path static build | PASS locally | `/sirati`, no fixture routes, local font assets, no Staging backend/key. Local Node 24 default Turbopack aborted with `fatal library error, lookup self`; same source built with `next build --webpack`. CI must validate normal Node 22 build. |
| Account draft safeguards | PASS synthetic | Existing `account_storage_check.py`: eight draft cases, logout cleanup/failure retention, source invariants. Does not establish server-side live account isolation. |
| Duplicate saved-document safety | PASS static | Existing `multi_cv_duplicate_check.py`; owner-scoped data copy invariants. No actual authenticated save performed. |
| Existing guest/browser E2E | PASS locally | Original `qa/e2e.mjs` completed against production artifact, including guest Save PDF gate, cancel/edit/reload, bilingual preview, navigation and templates. |
| PDF sections, A4, photos, Unicode, metadata, Arabic numbers and visual comparison | NOT RUN final gate | Execution in progress; update exact downloaded-output results before review. |
| All-template 360/390/desktop long PDFs | NOT RUN final gate | New synthetic paragraph-marker matrix; results pending. |
| Normal Node 22 GitHub build/QA at exact PR HEAD | NOT RUN | Await PR CI; earlier Staging successes are historical, not acceptance of candidate. |
| Real authenticated Save PDF + My Documents identity/restore | BLOCKED | Dedicated isolated accounts/session not supplied; local build intentionally has no real backend. |
| Real shared-browser A -> logout -> B isolation | BLOCKED | Same dependency; user-reported earlier success is not independent exact-candidate evidence. #24/#25 remain gates. |
| Independent human Security/QA signoff | BLOCKED | No separate reviewer signoff on candidate. Automated native-reader independence does not substitute for it. |
| Physical Android search/copy + screen-reader/ATS parser | NOT RUN | Chromium viewport emulation and independent extraction do not certify those behaviors. |

## Security and acceptance limits

No Production writes, database operations, migrations, customer-record access, real-account creation, secret changes, Analytics activation, payments or paid services. PDF export stays client-side with local font assets. Filename sanitization, clone cleanup, canvas release, and fail-closed missing-font/text checks are retained. The test workflow has only `contents: read`, no deploy job, and no backend credentials.

The PDF is a bitmap-faithful hybrid with transparent searchable Unicode text, not fully vector, tagged PDF/UA or guaranteed ATS compatible. Standalone Arabic-Indic digits remain Arabic visually but copy as equivalent ASCII decimal values (`٢٠٢٠` -> `2020`). Owner should explicitly accept that tradeoff during manual review. Mixed-script reading order and selection geometry need cross-viewer inspection.

## Outstanding priorities and decision

- P0: no confirmed new P0 in completed checks; do not infer absence from blocked tests.
- P1: #24/#25 independent authenticated A/B and save/restore confidentiality gates; exact-candidate reviewer signoff and normal production CI.
- P1: #97/#120 real Android search/copy, long-template visuals and reading-order acceptance remain until final evidence is reviewed.
- P2: existing hybrid PDF accessibility/selection limitations; no tagged PDF/UA or external ATS certification.
- P2: pre-existing Modern profession headings in #117 are outside this PDF scope.
- P3: emulated/local timing is not representative of every phone.
- #87/#99 Analytics security/activation remain a separate NO-GO and are excluded from this release.

**NO-GO for Production merge/release until exact-head build/PDF QA, independent review, manual device acceptance and explicit owner approval.** Draft candidate may be reviewed while remaining gates are blocked.

## Final manual QA and owner release gate

1. Inspect exact PR diff and CI HEAD; require no unapproved files/migrations/backend changes.
2. On an isolated accessible candidate with dedicated synthetic accounts, perform actual guest -> signup/signin -> Save PDF, verify current document ID/template/content, reload and download from My Documents. Do not use customer data.
3. Same browser: A creates/saves synthetic marker; logout; B must not see A in lists, direct URLs or browser draft storage; reload and switch accounts. Reviewer logs only sanitized PASS/FAIL proof and HEAD.
4. Android Chrome + PDF viewer: EN/AR search, select/copy whole phrases, Arabic dates/metadata, photo, 1/2/3/5+ page boundaries; inspect all nine families. Accept ASCII numeric extraction explicitly.
5. Separate Security/QA reviewers sign off. Owner gives explicit merge + Production-release approval on exact reviewed head. This session stops before either.

## Rollback (plan only, not executed)

Baseline is main `54461f950554c18d64690331020596dcf79e43cb`. If a future approved merge causes P0/P1 regression, stop rollout, revert that PDF merge through a reviewed revert PR (`git revert -m 1 <approved-merge-sha>` for a merge commit, ordinary revert for squash), rebuild and verify guest gate, save identity, A/B and baseline PDFs. Do not reset/force-push main or alter data. Main push automatically deploys via existing `pages.yml`; revert/deployment also needs owner authorization. No schema rollback is required because this release has no migrations.
