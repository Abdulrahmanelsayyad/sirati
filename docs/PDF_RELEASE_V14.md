# Sirati PDF remediation V15 — current report

2026-10-11. Owner: V15 engineering session. **NO-GO; no merge or deployment performed or authorized.** This section supersedes the historical V14 report below.

## Candidate and cause

Dependent [Draft #125](https://github.com/Abdulrahmanelsayyad/sirati/pull/125) targets `release/pdf-only-v14-20261011` at `c18427445bd521e0acba5ee6f6c34ae30168037b`. Main remains `54461f950554c18d64690331020596dcf79e43cb`; approved comparator remains `78ab9519599bf3436fce4418b3fe7bdfdd8e56b7`. The final candidate is the commit containing this report/evidence; exact SHA is recorded in the PR body/checks. Historical intermediate head `94b1587adefde74a5abb338443d610dd86544982` is NOT the final validation target.

Recorded word `[2228.421875,2241.421875]` straddles old cut `2229.001846665645`. Break selection permitted 1px intersection, whereas page text inclusion permitted only 0.5px: the same word was owned by neither page. Fresh old-candidate Modern EN360/123-paragraph reproduction failed in PDF.js, Poppler and PyMuPDF; the final exporter places BoundaryToken108 exactly once on page3.

The fix computes cuts on the bitmap integer-pixel grid and retreats to the start of every crossing word box, including overlapping columns. A word's top edge selects exactly one half-open page interval; its whole box must fit or export rejects. The same cuts crop the bitmap without overlapping raster rows. All source words must be embedded, replacing the old 55% acceptance threshold. Unsafe geometry, unsupported glyphs and empty runs reject with an understandable error; no image-only fallback.

A stricter glyph check exposed the inherited removal of ASCII punctuation from Arabic font subsets. Existing Latin font now supplies terminal punctuation while the entire Arabic sentence stays in one text object. Tests verify 95 complete Arabic sentences with punctuation in both readers. Unsafe embedded mixed-script runs and unsupported alphabets reject rather than silently lose characters. Arabic-Indic values still extract as equivalent ASCII numerals. This does not certify universal mixed-script selection, external ATS compatibility or PDF/UA.

## Scope

Runtime change: `.github/scripts/pdf_text_layer_v19.py` only. Protected generated application source parity: 34 existing TS/TSX/CSS files match the PR124 reconstruction; only `lib/siratiPdfExport.ts` differs. No fonts/templates/auth/data/schema/dependency/payment/Analytics configuration changed.

QA: `qa/pdf_boundary_check.mjs`, `qa/pdf_staging_build.py`, `qa/pdf_release_guard.py`, `qa/pdf_release_run.sh`, `qa/pdf_template_longform_check.mjs`, `qa/pdf_template_native_check.py`, `qa/pdf_release_evidence.json`. Report: this file. Workflow: `.github/workflows/pdf-release-qa.yml` additionally targets the dependent base branch, executes exact-head boundary tests and reuses existing Staging build settings for a build-only smoke. Permissions stay `contents: read`; no deployment jobs or new credentials. Existing deploy workflows are unchanged. Every commit/title carries `[skip netlify]`.

## Results on final source

| Check | Before | After locally | Limits |
|---|---|---|---|
| Nine families × EN/AR × 360/390/1440 × 2/3/5 pages | 91 PASS / 71 FAIL | **162/162 PASS** | All 54 cases per page count match exact target; no missing/duplicate markers |
| Independent native readers | 182 PASS /142 FAIL | **324/324 PASS** | 40,052 complete paragraph-reader observations; full sentence count, unique markers, monotonic page ownership |
| Fractional boundary regression | Recorded failure | 42 PASS + touching edges, multi-column cascade and rejection cases | Executes actual generated TypeScript functions |
| All nine short families/EN/AR/three widths/eight sections | PASS historical | 54/54 PASS | Chromium emulation |
| Approved Staging paired PDFs | PASS historical | 48 pairs PASS | 36 sections,8 photos,4 synthetic long controls |
| Pixel comparisons / fonts / photos / A4 | PASS historical | 17 samples PASS | Additional fresh Modern boundary and Arabic/photo inspection; not an all-page human review |
| Word boundaries / metadata | PASS historical | 54 phrase assertions PASS; metadata non-overlap PASS | Poppler raw/layout and PyMuPDF |
| Arabic numerals / existing list-style checks | PASS historical | 270 numeric observations PASS; cert/course list checks PASS | ASCII-equivalent native numeric extraction retained |
| Original guest E2E / Smart CV / navigation | PASS historical | PASS | Save PDF gate retained; no authenticated server-side verification |
| Production build and scope guard | PASS historical | PASS | Normal Turbopack Node24; /sirati, offline fonts, no fixture routes or Staging backend |
| Existing Staging build/boot smoke | PASS historical | PASS | Existing config and bundle guard; no deploy, no actual login |
| Account draft/logout/duplicates | PASS synthetic | PASS synthetic/static | Eight draft cases; not real account isolation |
| Real login/logout/save/restore/multiple-document/A-B tests | BLOCKED | **BLOCKED** | Dedicated isolated accounts/session unavailable |
| Human Security and QA signoff | BLOCKED | **BLOCKED** | Automated reader independence is not human signoff |
| Physical Android copy/search; external ATS; PDF/UA | NOT RUN | **NOT RUN** | No certification claimed |
| Final-head CI | Not applicable | **PENDING at report commit** | [Current exact-head checks](https://github.com/Abdulrahmanelsayyad/sirati/pull/125/checks); PR body records final run conclusion |

Sanitized full matrix and reader records are in `qa/pdf_release_evidence.json`; the V14 evidence is retained under `historical_v14`. Exporter SHA256 binds locally tested output to the commit source; CI checks `github.event.pull_request.head.sha`. The no-deploy workflow archives synthetic PDFs/results. Intermediate [CI38136488878](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38136488878) is historical and must not be called final-head PASS. Normal Pages/E2E/Staging workflows target main only; the dependent PR uses the expanded read-only workflow to execute their relevant non-deploy validation route.

## Visual findings and remaining gates

Fresh Compact ATS Arabic 5-page Experience inspection shows bullet marks at the far left while prose is right aligned: **FAIL / P2**, inherited list styling (generated CSS byte-identical to PR124). Existing cert/course marker correction passes. No template redesign/CSS expansion was made. This should have a separately scoped visual follow-up. The previously omitted Modern boundary line is now intact/searchable on page3; page2 ends with token107. Pixel parity is sampled, not a claim of exhaustive human visual approval.

Own scoped security inspection: PASS for no auth/RLS/data/dependency/secret/Analytics/payment changes, same-origin PDF fonts, no customer test data, byte-identical protected sources and read-only no-deploy CI. Independent human Security/QA remains BLOCKED. No confirmed new P0/P1 text-loss defect remains in the validated synthetic matrix, but real-account confidentiality gates and independent signoff remain release blockers. PDF export deliberately rejects unrepresentable/unsafe text; hybrid text selection and untested mixed-script strings remain limits.

**NO-GO** until final-head CI succeeds, dedicated real-account save/restore/A-B confidentiality checks complete, independent human Security/QA signoff is obtained and manual Android/reading-order acceptance is recorded. Owner approval on the exact final SHA remains required. Neither #124 nor #125 is merged; Production and Staging are not published.

## Rollback readiness

Rollback baseline is unchanged main `54461f950554c18d64690331020596dcf79e43cb`. This fix is isolated above #124, so abandoning its draft needs no production rollback. If a future owner-approved release regresses, prepare a reviewed revert PR (`git revert -m 1` for a merge, ordinary revert for squash), rebuild and verify PDF/guest gate/save identity/A-B. Never force-push/reset main or modify customer data. Revert publication also requires owner approval; main pushes deploy automatically. No database/schema rollback is needed. Rollback is documented, not executed.

---

# Historical V14 report (retained for before evidence)

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

New/adapted release QA: `qa/pdf_release_guard.py`, `qa/pdf_release_run.sh`, `qa/pdf_template_longform_check.mjs`, `qa/pdf_template_native_check.py`, `qa/pdf_release_evidence.json`, `.github/workflows/pdf-release-qa.yml`, this report. Tests use local `/sirati` and a pinned approved Staging comparator, never a real backend. Extend short fixtures to 360px and add long real-template markers. Fixed-baseline numeral comparison explicitly allows zero baseline failures; numeric correctness assertions remain strict. Original Staging workflow is not copied.

Explicitly excluded: all three Staging migrations, Analytics activation/retention/ACL changes, Supabase/Auth/RLS/payments/secrets, Staging smoke edits, unrelated feature/template-heading work and Staging documentation. Existing main `netlify.toml` is already a Staging-only configuration; it is unchanged and is not used by GitHub Pages or isolated release QA.

## Test evidence

Results below distinguish execution from planned checks. Runtime exporter and template port are byte-identical to the reviewed Staging algorithm (apart from its introductory documentation). GitHub validated runtime head `a46339d07761f88d7d187b38106090444e036aaa`; later changes only add QA/evidence/report material. Full sanitized records are in `qa/pdf_release_evidence.json` and reproducible from the no-deploy workflow.

| Check | Status | Evidence / limit |
|---|---|---|
| Scope/source reconstruction and exporter parity | PASS | `pdf_release_guard.py`: original prepare preserved, algorithm equals approved Staging; allowlisted diff. |
| Production-path static build | PASS locally | `/sirati`, no fixture routes, local font assets, no Staging backend/key. Local Node 24 default Turbopack aborted with `fatal library error, lookup self`; same source built with `next build --webpack`. CI must validate normal Node 22 build. |
| Account draft safeguards | PASS synthetic | Existing `account_storage_check.py`: eight draft cases, logout cleanup/failure retention, source invariants. Does not establish server-side live account isolation. |
| Duplicate saved-document safety | PASS static | Existing `multi_cv_duplicate_check.py`; owner-scoped data copy invariants. No actual authenticated save performed. |
| Existing guest/browser E2E | PASS locally | Original `qa/e2e.mjs` completed against production artifact, including guest Save PDF gate, cancel/edit/reload, bilingual preview, navigation and templates. |
| PDF short sections, A4 and photos | PASS | 48 matched baseline/candidate cases (96 PDFs): 36 bilingual nine-family section pairs, 8 photo/sidebar pairs, 4 long synthetic controls. Independent Poppler Unicode/fonts; 17 sampled pixel comparisons passed. |
| Metadata and word spacing | PASS | Arabic education/language glyph boxes non-overlapping; 54 phrase assertions through Poppler raw/layout and PyMuPDF. |
| Arabic numeric values / list styles | PASS | 180 numeric reader observations at 390/1440px; Arabic Compact ATS markers removed, English retained. 90 additional numeric observations at 360px plus all sections in both native readers PASS. |
| All nine short families, both languages, 360/390/1440px | PASS | 54 PDFs, all eight populated sections via PDF.js, A4. Chromium emulation only. |
| PDF size / local latency vs approved Staging | PASS descriptive parity | 4,436,129 -> 4,436,141 bytes (+0.0003%); median 640 -> 636.5ms in one local run. No real-device performance claim. |
| Sampled human visual inspection | PASS limited samples | Rendered Modern EN, Compact ATS AR and photo Gold Sidebar AR inspected. Failing boundary sample confirms paragraph is visually present despite absent native text. All-family independent human review NOT RUN. |
| All-template 360/390/desktop long PDFs | FAIL | All 162 cases executed: nine families x EN/AR x three widths x 2/3/5 pages. A4 counts correct in all; 91 passed exact paragraph identity, 71 lost one or more native-text markers; zero duplicate markers. Both native readers reproduce the same failures: 182 PASS / 142 FAIL observations across 162 PDFs. |
| Missing paragraph reproduction on approved Staging | FAIL | Modern EN, 360px, 123 paragraphs, 3 pages: BoundaryToken108 absent in PDF.js, Poppler raw and PyMuPDF on both approved Staging and candidate. Visible bitmap retains it; no saved customer data touched. |
| Normal Node 22 GitHub production-path build | PASS at runtime head | [38135044370](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38135044370), build success; deploy SKIPPED. This clears the local Turbopack-environment limitation for runtime head. |
| GitHub original E2E | PASS at runtime head | [38135044399](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38135044399), success. Build-only Staging smoke [38135044404](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38135044404) success. |
| New expanded PDF release workflow | NOT RUN final conclusion | [38135044451](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38135044451) was executing at report preparation. Its long-template assertion must fail on unchanged exporter; inspect final PR checks on the final documentation/QA head. Do not classify pending CI as PASS. |
| Real authenticated Save PDF + My Documents identity/restore | BLOCKED | Dedicated isolated accounts/session not supplied; local build intentionally has no real backend. |
| Real shared-browser A -> logout -> B isolation | BLOCKED | Same dependency; user-reported earlier success is not independent exact-candidate evidence. #24/#25 remain gates. |
| Independent human Security/QA signoff | BLOCKED | No separate reviewer signoff on candidate. Automated native-reader independence does not substitute for it. |
| Physical Android search/copy + screen-reader/ATS parser | NOT RUN | Chromium viewport emulation and independent extraction do not certify those behaviors. |

## Security and acceptance limits

No Production writes, database operations, migrations, customer-record access, real-account creation, secret changes, Analytics activation, payments or paid services. PDF export stays client-side with local font assets. Filename sanitization, clone cleanup, canvas release, and fail-closed missing-font/text checks are retained. The test workflow has only `contents: read`, no deploy job, and no backend credentials.

The PDF is a bitmap-faithful hybrid with transparent searchable Unicode text, not fully vector, tagged PDF/UA or guaranteed ATS compatible. Standalone Arabic-Indic digits remain Arabic visually but copy as equivalent ASCII decimal values (`٢٠٢٠` -> `2020`). Owner should explicitly accept that tradeoff during manual review. Mixed-script reading order and selection geometry need cross-viewer inspection.

## Outstanding priorities and decision

- P0: no confirmed new P0 in completed checks; do not infer absence from blocked tests.
- P1 CONFIRMED: native-text paragraph loss at page boundaries in 71/162 expanded cases, affecting every family in at least one synthetic scenario. All are 2/3/5 A4 pages; this can harm copy/search/ATS despite visible content.
- P1 BLOCKED: #24/#25 independent authenticated A/B and save/restore confidentiality gates; exact-candidate reviewer signoff and final-head CI.
- P1: #97/#120 real Android search/copy, long-template visuals and reading-order acceptance remain until final evidence is reviewed.
- P2: existing hybrid PDF accessibility/selection limitations; no tagged PDF/UA or external ATS certification.
- P2: pre-existing Modern profession headings in #117 are outside this PDF scope.
- P3: emulated/local timing is not representative of every phone.
- #87/#99 Analytics security/activation remain a separate NO-GO and are excluded from this release.

**NO-GO for Production merge/release.** The confirmed P1 native-text loss must be corrected and retested before approval, in addition to independent review, actual account tests and manual device acceptance. This task intentionally ports only validated Staging runtime changes; it does not silently amend the exporter beyond that scope. Draft #124 is ready for failure review and focused remediation.

Measured root cause: page-3 boundary `2229.001846665645` CSS px; missing token top `2228.421875` and bottom `2241.421875`. `chooseBreak` allows a 1px overlap but text inclusion uses 0.5px tolerance, excluding this word from both pages. This is directly measured DOM geometry, not an assumption about Auth or database behavior. Proposed next scope: harmonize text-safe boundary/inclusion logic, then require zero missing/duplicate markers in the full matrix and rerun visual parity. No runtime fix was applied here.

## Final manual QA and owner release gate

1. Inspect exact PR diff and CI HEAD; require no unapproved files/migrations/backend changes.
2. On an isolated accessible candidate with dedicated synthetic accounts, perform actual guest -> signup/signin -> Save PDF, verify current document ID/template/content, reload and download from My Documents. Do not use customer data.
3. Same browser: A creates/saves synthetic marker; logout; B must not see A in lists, direct URLs or browser draft storage; reload and switch accounts. Reviewer logs only sanitized PASS/FAIL proof and HEAD.
4. Android Chrome + PDF viewer: EN/AR search, select/copy whole phrases, Arabic dates/metadata, photo, 1/2/3/5+ page boundaries; inspect all nine families. Accept ASCII numeric extraction explicitly.
5. Separate Security/QA reviewers sign off. Owner gives explicit merge + Production-release approval on exact reviewed head. This session stops before either.

## Rollback (plan only, not executed)

Baseline is main `54461f950554c18d64690331020596dcf79e43cb`. If a future approved merge causes P0/P1 regression, stop rollout, revert that PDF merge through a reviewed revert PR (`git revert -m 1 <approved-merge-sha>` for a merge commit, ordinary revert for squash), rebuild and verify guest gate, save identity, A/B and baseline PDFs. Do not reset/force-push main or alter data. Main push automatically deploys via existing `pages.yml`; revert/deployment also needs owner authorization. No schema rollback is required because this release has no migrations.
