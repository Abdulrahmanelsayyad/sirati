# Sirati Agent Changelog

This file records autonomous maintenance changes made to Sirati.


## 2026-10-07 — Smart Nursing Library, Compact ATS and Account Data QA

- Shipped Smart Nursing CV Library with eight nursing specialties, four experience levels and three target-market wording modes. Content insertion requires explicit user confirmation and remains editable.
- Shipped Compact ATS as the fourth CV template.
- Fixed mobile Builder horizontal overflow; browser E2E passed all four templates at 390px.
- Browser E2E passed template selection, Compact ATS onboarding persistence, Smart Nursing insertion, local draft persistence after refresh, four-template switching, Arabic RTL and PDF smoke tests.
- Supabase production data layer reviewed against current RLS guidance.
- Applied migration `20261007131224_tighten_cv_data_api_grants`: removed Data API table privileges from `anon` and reduced `authenticated` to the exact CRUD capabilities needed per table.
- Ran rollback-only two-user RLS tests. Own CV create/update, version creation and PDF-order creation passed. Cross-user read/update/delete/owner spoofing/version creation/PDF-order creation were blocked.
- Verified version numbering and retention: after 31 saves, only versions 2–31 remained, for a 30-version cap.
- Verified existing production integrity without reading CV content: 2 documents, 4 versions, zero orphan versions, zero owner mismatches and zero duplicate version numbers.
- Added `qa/supabase_rls.sql` regression test and tracked the production migration under `supabase/migrations/`.
- Remaining credential-dependent manual check: a full browser logout -> login -> reopen cloud CV round trip with a second real loginable account. The project currently has one real Auth user, so this was not fabricated or bypassed.
- Security follow-up: Supabase Security Advisor currently warns that leaked-password protection is disabled.


## 2026-10-07 — New CV Draft Restoration

- Fixed the new-CV onboarding flow so a fresh CV remains blank instead of restoring an older account draft after onboarding/effect replay.
- Added regression coverage for new-CV intent, account-scoped draft restoration, saved-document priority and cross-account draft isolation.
- Restored the Builder feedback-panel stacking rule after E2E caught the regression.
- PR #6 passed the production build and Sirati E2E QA, was merged to `main`, deployed successfully to GitHub Pages, and was manually verified on the live site for refresh restore, fresh-CV behavior, PDF, mobile and English/Arabic presentation.


## 2026-10-08 — PDF Order / Payment Clarity

- Clarified the EGP 50 clean-PDF journey into explicit payment, reference-submission and manual-review steps.
- Improved pending, approved and rejected payment states and added a real Sirati Support fallback when WhatsApp is not configured.
- Added E2E coverage for payment guidance, support-link fallback and mobile layout.
- PR #7 passed build and Sirati E2E QA, deployed successfully to GitHub Pages, and was manually verified on the live site.


## 2026-10-08 — Live CV Readiness Check

- Added a zero-cost live CV readiness indicator inside the Builder.
- Checks six essentials: full name, contact details, professional summary, work experience, education and skills.
- Supports English and Arabic, updates while the user edits, and includes a clear disclaimer that the percentage is not a guaranteed ATS score.
- Added E2E coverage for visibility, score response, disclaimer and mobile containment.
- PR #8 passed build and Sirati E2E QA, deployed successfully to GitHub Pages, and was manually verified on the live site.


## 2026-10-08 — Job Match factuality regressions (review branch; not deployed)

- P1-TAILOR-01 remains IN PROGRESS; this change is not a production completion claim.
- Match only rendered CV evidence; reject negated, planned, pending, expired and eligibility-only credential statements. Require explicit licensing wording for license requirements and language-specific fluency evidence.
- Resolve repeated requirement priority, heading inheritance and mixed required/preferred clauses; preserve separate required/preferred experience thresholds and recognized specialty scope.
- Parse lower bounds of year ranges and Arabic digits; preserve fallback phrase boundaries.
- Added generated-engine regression checks to the existing E2E entry point, plus browser assertions for no CV mutation and exclusion of unrelated inputs.
- Local production build and TypeScript checks passed; account draft regression (6 cases) and duplicate-CV invariants passed. Full desktop/mobile, Arabic, persistence, four-template and PDF smoke E2E passed, including the final no-mutation and unrelated-input assertions.
- Limitations: deterministic evidence matching is conservative, not credential verification or complete natural-language interpretation. Date-derived tenure and unrecognized specialty/qualification wording still require manual review. No merge, deployment, paid API or protected-setting change.
