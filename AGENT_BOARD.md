# Sirati Agent Board

- **Live review fixes — 2026-10-17** — Owner: Codex; branch `fix/review-content-and-editor`, base `98fedf5`. Scope: optional rating before PDF auth (skip supported), catalog count/English menu, neutral evidence-based summaries, LinkedIn/interview drafting, tab-scoped section restore, compatible experience date controls. Local reconstruction + production build/typecheck PASS; focused rating/guest-save/new-CV/role/content/restore regressions PASS. Existing review retained; feedback failure does not block PDF; session changes block export. No database/auth configuration, PDF renderer, payment or deployment changes. Full browser CI and real-account/device acceptance remain separate; Draft PR only.

## Priority
Keep Sirati reliable, secure, polished, easy to use, and focused on the core customer journey:
Login -> Template -> CV Builder -> Save -> Preview -> PDF Order.

## Now
- **Guest refresh persistence — 2026-10-16** — Owner: Codex; branch `fix/refresh-draft-20261016`, base `771cd58`. Status: IMPLEMENTATION VERIFIED / DRAFT PR; no merge/deploy. User explicitly requested retaining CV data on refresh. Scope: existing guest-save generator, existing regression and this board. Reproduced missing pre-Save snapshot; now create bounded tab-only drafts after identity/hydration restoration, preserve data/template/language across refresh, and clear stale transfer intent for New CV. Ordinary guest drafts last for the tab; explicit account transfers retain their 30-minute/email restrictions. No Auth configuration, RLS, database, PDF engine, pricing or workflow edits. Benchmark: MDN sessionStorage reload lifetime. Verification: new regression fails on baseline and passes on candidate; existing guest-save/concurrency, rating gate, account-storage/new-CV/signout/session-boundary suites PASS; production build and TypeScript PASS. Generated runtime differences limited to Builder and SiratiBuilderPdfButton. Real browser/mobile/live-account and independent review NOT RUN. Lesson: restoration must finish before autosave; preserve draft content separately from expired action authorization. Closing the tab is not durable account storage; quota failure retains the editor and warns.
- **PDF rating before auth — 2026-10-16** — Owner: Codex; branch `feat/pdf-rating-before-signin`, base `b2d4438`. Scope: Builder Save PDF only: honest 1–5 rating, existing inline sign-in/signup, confirmed review save, then export; existing reviews skip prompt. Save CV, PDF engine, backend settings/schema unchanged. Synthetic rating/auth/retry/account-boundary and existing guest-save regression PASS. Production build/typecheck checked; live database/browser/mobile flow NOT RUN. Draft PR only, no merge/deploy. Benchmark: W3C modal pattern and Supabase upsert docs. Lesson: preserve the review in the existing bounded tab transfer, ignore duplicate inserts, and reverify identity before export.
- **V32 local document completion — 2026-10-14** — Owner: Codex; branch `feat/v32-local-pdf-review`, base `c11e99d`. Scope: local text-PDF extraction, editable review and explicit Builder insertion, English-first import UI; synthetic regression/build/browser validation. No merge/deploy or backend mutations.
- **P2 Smart CV occupation matching — 2026-10-12** — Owner: Codex; branch `fix/smart-cv-nursing-role-boundaries`, base `316a98a`. Reproduced ICU physician / Arabic emergency titles receiving nursing skills; Nursery teacher receiving nursing summaries. Require an explicit bounded nursing title before specialty matching; preserve opt-in confirmation and neutral fallback. Generated runtime changes only PersonalSummaryPicker and SmartContentSuggestions. Local production build/TypeScript, 40 domain assertions, guest-save/concurrency, bounded verification and 10 verifier contracts PASS. Existing E2E extended with six bilingual roles at 390/1440px; exact-head CI pending, local Chromium download failed. No auth/DB/PDF engine changes or merge/deploy. Benchmark: CareerOneStop relevant-role guidance; lesson: workplace/specialty keywords alone do not establish occupation. Release NO-GO until browser and applicable account/device review gates are satisfied.
- **P1-TAILOR-01 — Target Job Tailoring / Job Match Center** — Status: RETIRED BY OWNER REQUEST (2026-10-08). Removal work is tracked on `fix/remove-job-match-center`: delete the feature code and UI, clear only deprecated `sirati.jobTailor.v2.*` browser data, preserve Experience Description Pro V2, and require Build + E2E + QA review before any merge/deploy.
- **P1-READINESS-01 — Live CV Readiness Check** — Owner: Design Agent + Bug Fixer — Status: VERIFIED (2026-10-08) — Zero-cost live completion guide for six essential CV sections shipped; PR #8 passed build + Sirati E2E QA, deployed successfully, and was manually verified on the live site.
- **P0-BUILDER-01 — Builder status messages overlap the sticky CV preview** — Owner: Sirati Bug Fixer — Status: VERIFIED (2026-10-07) — CSS stacking regression fixed; PR #6 passed build + Sirati E2E QA and was verified on the live site after deployment.
- **P0-AUTH-01 — Account Save/Restore + Data Isolation** — Owner: Security Agent + QA & Release Agent — Status: VERIFIED (2026-10-07) — Production RLS tested bidirectionally with rollback-only users; own create/update/version/PDF-order operations succeed; cross-user read/update/delete/insert/version/order operations are blocked; Data API grants tightened to least privilege.
- **P0-PDF-01 — PDF order / payment clarity** — Owner: Customer Liaison + Design Agent — Status: VERIFIED (2026-10-08) — Manual EGP 50 clean-PDF flow clarified for InstaPay/Vodafone Cash, reference submission and pending/approval messaging; PR #7 passed build + E2E, deployed successfully, and was verified on the live site.
- **Coordination** — Owner: Deputy Manager — Status: ACTIVE — Maintain conflict map and enforce handoffs; no production completion claim before QA and changelog entry.

## Top 10 Feature Roadmap — First Customer Growth Program

Implementation rule: one feature per branch/PR, full build + E2E QA before merge, then live verification before the next feature is treated as complete. Avoid overlapping Builder edits across open feature PRs.

1. **F1 — CV Quality Center** — Status: DEPLOYED / LIVE VERIFICATION PENDING — PR #13 passed build + E2E QA, was merged, and deployed successfully. Final completion still requires live manual verification.
2. **F2 — Multi-CV Versions / Duplicate CV** — Status: MERGED / LIVE VERIFICATION PENDING — PR #14 passed build + E2E QA and was merged. Final completion still requires live verification of the duplicate flow with a signed-in saved CV.
3. **F3 — Experience Description Pro V2** — Status: IN PROGRESS — Advanced guided experience writing: auto-detect nursing specialty and seniority from the nearby job title, category filters, search, recommended multi-select, add-one/add-many actions, similarity-aware duplicate prevention, reopen trigger, Arabic/English, mobile layout, and full manual editing. Never add responsibilities automatically or invent facts.
4. **F4 — Cover Letter Builder** — Status: PLANNED — Build a guided English/Arabic cover letter from verified CV facts plus the target job; use deterministic templates first, never invent claims, zero paid API dependency.
5. **F5 — Job Application Tracker** — Status: PLANNED — Track company, role, job link, status, dates, notes and linked Sirati CV version with a simple application pipeline.
6. **F6 — PDF Preflight Center** — Status: PLANNED — Before ordering/exporting, check A4 fit, likely overflow, page count, missing essentials and print-risk conditions with actionable fixes.
7. **F7 — Existing CV Import** — Status: PLANNED — Import an existing CV into editable Sirati fields with explicit review/confirmation and conservative parsing; do not silently overwrite saved data.
8. **F8 — Section Manager** — Status: PLANNED — Reorder, hide/show and add supported sections while preserving ATS reading order, Arabic/English behavior and saved data compatibility.
9. **F9 — Private Share Link** — Status: PLANNED — Optional read-only CV sharing with explicit publish/unpublish controls, privacy-first defaults and no public exposure without user action.
10. **F10 — Interview Prep Kit** — Status: PLANNED — Generate a structured practice checklist and question bank from the chosen role/job requirements using verified CV facts and local curated content first.

## Backlog
- Continuously improve agent playbooks from verified outcomes and record reusable lessons.
- Improve customer-facing polish when clear, low-risk opportunities are found.
- Continuously watch for reproducible UI or deployment defects.
- Review security posture without exposing or modifying secrets.\n- Auth hardening follow-up: Supabase Security Advisor reports leaked-password protection is disabled; enable when available/approved.

## Blocked
- In-page AI CV assistance requires an approved AI backend/API or equivalent runtime integration.

## Completed
- Multi-agent operating model defined.


## Product improvement backlog — Manager assigned

### P0 — Customer journey / Builder
- Transform the CV Builder into short, simple guided steps instead of a long dense form.
- Improve the live preview so users can understand the result while editing.
- Reduce visible field clutter and show only the information needed for the current step.
- Run a full mobile usability pass focused on navigation, touch targets, scrolling, and form completion.

### P0 — PDF order / payment clarity
- Simplify the manual PDF order flow for InstaPay and Vodafone Cash.
- Make payment instructions, pending status, proof/reference submission, and next steps obvious.
- Do not change pricing, approval logic, payment rules, or add automated collection without owner approval.

### P1 — Trust and conversion
- Improve first-30-seconds clarity: explain what Sirati does, who it is for, and why it is useful.
- Strengthen trust pages/sections: Contact, Privacy, Terms, payment/delivery expectations, and support clarity.
- Improve CTA hierarchy so the primary action is obvious and secondary actions do not compete.

### P1 — Templates
- Focus on 2–3 excellent templates rather than increasing template count.
- Improve ATS readability, spacing, print fidelity, Arabic/English consistency, and professional visual quality.

### P1 — End-to-end QA
- Test the full journey: landing -> sign in -> choose template -> build CV -> save -> return/edit -> preview -> PDF order.
- Check desktop and mobile.
- Record reproducible defects for Bug Fixer and verify fixes before closing.

### Delegation guidance
- Design Agent: homepage clarity, CTA hierarchy, builder UX, mobile polish, template presentation.
- Bug Fixer: reproducible navigation, form, save/restore, rendering, preview, and deployment defects.
- CV Expert: section guidance, ATS wording quality, template content structure, factual CV assistance.
- Customer Liaison: support wording, customer-facing instructions, FAQs, payment/order communication clarity.
- Security Agent: review changes for exposure/privacy/security regressions without modifying protected settings.
- Deputy Manager: maintain ownership, sequencing, handoffs, and blocker visibility.
- Manager: prioritize, assign one owner per task, verify outcome, and report only meaningful progress/blockers.

### Completion rule
No task is complete until the relevant user flow is verified on the live site and the change is recorded in AGENT_CHANGELOG.md.


## Feature Program — Smart CV Library / Guided Specialty Builder

### Goal
Reduce user thinking and typing. Let the customer choose a field/specialty, role, experience level, and target market, then show curated factual options that can be selected and inserted into the CV.

### P0 — Product design and content model
- Define the guided flow: Field -> Specialty -> Job title -> Experience level -> Target market -> Suggested content -> Add selected items to CV.
- Start with Healthcare/Nursing before expanding to other sectors.
- Define reusable content categories: Professional Summary, Skills, Experience Bullets, Achievements, Certifications, ATS Keywords, optional section guidance.
- User must explicitly select or confirm every factual item before it is added. Never invent employment, dates, licenses, certifications, achievements, or clinical competencies.
- Keep implementation zero-cost: local/static JSON or existing database structures only; no paid AI/API dependency.

### P0 — Initial Nursing library
- Build the first curated library for nursing roles, beginning with Emergency Nurse, ICU Nurse, OR Nurse, Ward/Medical-Surgical Nurse, Infection Control Nurse, Dialysis Nurse, Pediatric Nurse, and Nursing Supervisor.
- Include experience levels such as Beginner / Experienced / Senior / Supervisor where appropriate.
- Include target-market variants only when they are factually and safely supportable (for example Egypt/Gulf/ATS-oriented wording), without implying legal or licensing eligibility.
- Each content item must be concise, editable, and suitable for ATS-friendly CV use.

### P0 — Builder integration
- Add a guided specialty selector inside the CV Builder.
- Show curated checklists/cards instead of forcing users to write from scratch.
- Provide a clear action such as "Add selected items to my CV".
- Preserve manual editing after insertion.
- Do not break existing save/restore, preview, templates, Arabic/English, or mobile behavior.

### P1 — Quality and expansion
- Benchmark respected CV/resume builders and specialty onboarding flows before implementation; extract principles without copying branding, wording, layouts, or proprietary assets.
- Validate Arabic/English clarity and medical terminology.
- Add QA for mobile/desktop, save/restore, duplicates, removal/editing, preview, and PDF order flow.
- Expand to Doctors, Pharmacy, Lab, Radiology, Infection Control, Quality, Patient Safety, and Healthcare Administration only after the Nursing MVP is verified.

### Delegation
- Manager: owns sequencing, scope, zero-cost constraint, and final closeout.
- CV Expert: owns specialty taxonomy, factual content library, ATS wording, and anti-hallucination/factuality rules.
- Design Agent: owns guided selection UX, cards/checklists, low-friction mobile interaction, and Arabic/English presentation.
- Bug Fixer: owns safe integration with builder state, insertion/removal, persistence, duplicate handling, and regressions.
- QA & Release Agent: owns end-to-end verification on desktop/mobile and live-site validation.
- Security Agent: reviews any storage/data-handling changes for privacy/security regressions.
- Performance & SEO Agent: reviews page weight and loading impact after the MVP is stable.
- Deputy Manager: prevents overlap, manages handoffs, and maintains the conflict map.

### Completion criteria
- A user can choose a nursing specialty and experience level and receive relevant selectable content without paid AI.
- Nothing factual is inserted without user selection/confirmation.
- Selected content remains editable and saves/restores correctly.
- Existing CV journey remains functional.
- Live-site QA passes on mobile and desktop.


### Manager benchmark brief — 2026-10-07
Current public benchmark research found useful principles to adapt, not copy:
- Resume.io exposes relevant skill suggestions and keyword-oriented sample sentences while keeping the resume editable.
- Teal uses a reusable content library where users toggle bullets on/off for a tailored resume, preserving one source of truth and user control.
- Canva reduces blank-page friction with ready-made, customizable starting points and supports mobile editing.
- Sirati adaptation: specialty-first curated options + explicit user confirmation + editable insertion + zero-cost static/local content. This is intentionally narrower and simpler than copying full competitor feature sets.

### Smart CV conflict map
- SCV-01 may touch only taxonomy/content specification or dedicated content-data files.
- SCV-02 may touch only UX specification/design artifacts until SCV-01 handoff.
- SCV-03 is the sole owner allowed to touch builder state/insertion/persistence for this feature.
- SCV-04/05/06 review after integration and must not concurrently edit SCV-03-owned files; defects return to SCV-03 as a handoff.


## Template Program — Compact ATS

### Owner request — 2026-10-07
Add a fourth Sirati CV template focused on maximum ATS readability and compact professional presentation.

### TPL-01 — Design specification
- **Owner:** Sirati Design Agent
- **Status:** COMPLETE (2026-10-07)
- Benchmark leading ATS-oriented resume builders and extract principles without copying branding, layouts, wording, or proprietary assets.
- Template working name: **Compact ATS**.
- Use a true single-column reading order.
- Keep contact information in the main document body.
- Use standard section headings and highly readable typography.
- Avoid content-bearing sidebars, tables, text boxes, skill bars, charts, profile-photo dependence, and decorative elements that may impair parsing.
- Prioritize Experience, Skills, Education, Certifications, and optional Projects/Achievements.
- Support both English LTR and Arabic RTL with equivalent hierarchy.
- Target clean A4 output and a strong one-page presentation for moderate content without forcing all users into one page.
- The design must remain visually distinct from Sirati's existing templates while preserving the same CV data model.

### TPL-02 — Builder/preview integration
- **Owner:** Sirati Bug Fixer
- **Status:** COMPLETE (2026-10-07)
- Add Compact ATS as a selectable fourth template using the existing template-selection architecture.
- Reuse the existing CV data model; do not fork user data or persistence.
- Preserve manual editing, save/restore, preview, Arabic/English, mobile behavior, and PDF-order flow.
- Do not modify Authentication, RLS, payment rules, secrets, pricing, or protected settings.

### TPL-03 — QA and release verification
- **Owner:** Sirati QA & Release Agent
- **Status:** COMPLETE (2026-10-07)
- Verify template selection, switching between all templates, persistence after refresh/sign-out/sign-in where supported, desktop/mobile rendering, Arabic RTL, English LTR, long-content wrapping, page breaks, print/PDF fidelity, and regression of the existing customer journey.
- Test ATS-safe reading order by copying/extracting rendered text in expected logical order where feasible.
- Record reproducible defects; no production completion claim until live-site verification passes.

### TPL-04 — Security/performance review
- **Owner:** Security Agent + Performance & SEO Agent (serialized reviews)
- **Status:** COMPLETE (2026-10-07)
- Confirm no new external assets, paid dependencies, tracking, secret exposure, or unnecessary page-weight regression.

### Acceptance criteria
- Sirati offers four selectable CV templates.
- Compact ATS is genuinely single-column and content-first, not merely a recolor of an existing template.
- English and Arabic layouts both render correctly.
- Existing saved CV data can switch into/out of Compact ATS without data loss.
- A4 preview/PDF output has no clipping, overlap, broken page breaks, or hidden text in the verified test set.
- No paid dependency or API is introduced.
- Task is closed only after live QA and an entry in `AGENT_CHANGELOG.md`.

## V18 release preparation — 2026-10-11
- Owner: V18 technical execution session.
- Status: draft implementation verified locally; release BLOCKED, no merge/deploy.
- Scope: correct two obsolete homepage PDF FAQ answers; preserve strict generator scope check; rehearse rollback retaining manual deployment gate.
- Handoff: current evidence and remaining account/device/reviewer dependencies are in the V18 section of `docs/PDF_RELEASE_V14.md`. No other agent ownership is changed. Live acceptance remains open.

## P1 PDF punctuation export #130 — 2026-10-11
Owner: Codex. Branch: fix/pdf-mixed-script-export. Scope: add missing ASCII punctuation to the Arabic PDF font; retain mixed-letter guard until separately validated. No account/database changes. Draft candidate; no changed-SHA deployment or production approval.

## AI architecture audit V1 — 2026-10-11
- Owner: Codex architecture audit session.
- Branch: `audit/agent-architecture-v1-20261011`; base `2d464852dc11a98b2ab4d1bb05388b25eaaeaaf1`.
- Scope: QA runner and credential-boundary tests, existing QA CI wiring, agent governance and evidence documentation only. No product/PDF generator edits.
- Status: IN REVIEW — no merge/deploy.
- Handoff: `docs/AGENT_ARCHITECTURE_AUDIT.md`; security and QA evidence retain separate checks and unresolved gates. Historical board entries are not current live acceptance evidence.

## V21 PDF QA compatibility follow-up — 2026-10-12
- Owner: Codex continuation session; PR #133, runtime pinned at d909eba.
- Scope: PDF source-scope guard and adversarial regression only; no runtime/workflow changes.
- Finding: historical V14 whitelist rejected the approved session patch before PDF tests ran.
- Rule: use an explicit reviewed source snapshot for this successor; retain original historical checks, manual deployment gate, PDF invariants and production artifact checks.
- Status: local production build/artifact gate, 10 guard regressions, account suite, bounded verifier, 10 verifier contracts and 42 PDF boundary cases PASS. Exact-head CI pending; no merge/deploy or independent release approval.

## Menu accessibility continuation — 2026-10-12
- Owner: Codex; branch `fix/mobile-menu-focus-20261012`, base `ff5e597` (merged V21).
- Scope: existing navigation generator and E2E only; background isolation, focus containment and restoration. No overlapping template/Smart CV work.
- Evidence before: generated drawer declares `aria-modal` but only locks scrolling and boundary Tab; background elements remain interactive to programmatic/assistive focus.
- Reference: W3C APG modal dialog pattern, https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/ .
- Reusable rule: pair modal semantics with actual background isolation, preserve prior inert/scroll state, restore it before returning focus, and exercise filtered results.
- Status: local production build/typecheck, bounded verification and generated-source comparison PASS (only SiratiSiteMenu.tsx changed; app/lib/public byte-identical). Existing CI now exercises modal isolation, Tab wrapping, filtered results and all dismissals at five widths. Exact-head browser CI pending; local browser unavailable. No merge/deploy; physical Android and assistive technology acceptance remain separate.

## Modern headings continuation — 2026-10-12
- Owner: Codex; existing Draft PR #117, branch `fix/modern-profession-headings-20261011`; updated onto main `ba1eb05`. Reuses the existing implementation and workflow, no duplicate PR.
- Scope: profession-heading generator and its existing regression. Unknown roles remain neutral; Arabic word boundaries/diacritic normalization prevent kitchen titles matching medicine; healthcare industry words alone do not prove a clinical occupation. No user CV content rewritten.
- Benchmark principle: standard, relevant section headings (CareerOneStop Resume Guide / Veterans resume format); no ATS certification claim.
- Local evidence: production build/TypeScript PASS; 26 real generated-component renders PASS (both headings, content unchanged, empty sections hidden); bounded account/draft, duplicate, SQL-static, PDF boundary and credential-boundary checks PASS. The expanded test rejects the old candidate. Initial candidate build attempt failed on a local dependency symlink; using the same dependencies as regular files passed without configuration changes.
- Browser matrix reuses #117 workflow and now covers 13 titles in EN/AR at 360/390/1440 widths. Exact-head CI pending. Browser unavailable locally; no new native-PDF/device/live-account acceptance claimed.
- Reusable lesson: test complete Arabic words and ambiguous industry/job combinations, not only obvious role examples. Keep nonclinical headings neutral when classification is uncertain.
- No merge to main or publication; existing PDF/account/menu changes retained. Release acceptance remains separate.

## Guest Save CV preservation — 2026-10-12
- Owner: Codex; branch `fix/guest-save-draft-20261012`, base main `3b925c5`; user-reported draft loss after email entry.
- Confirmed: Save CV redirected to /auth without snapshot/return path. Reuse the existing inline auth gate for every saveToAccount entry, preserving exact tab draft and requested save/version intent. Separate save/PDF intent; storage/auth/save failures retain editor. Email return without a matching tab snapshot explains returning to the original tab.
- Synthetic generated-component checks cover signup confirmation, failed password, successful save once, failed cloud save, quota, session block and no accidental PDF. No real accounts/data, Supabase configuration, RLS, dependencies or workflow settings changed.
- Local production build/typecheck and bounded account/draft/PDF checks PASS. Exact-head CI pending; no merge/deploy. Closed original tabs/expired snapshots are not recoverable by this fix; cross-tab draft transfer is not implemented.

## V22 explicit Save concurrency — 2026-10-12
- Owner: Codex, branch `fix/v22-save-retry`, base `0e49c54`; existing draft work preserved in another worktree.
- Reproduced two inserts from rapid Save calls in actual generated Builder function. Scope: existing auth-gate generator, existing synthetic regression and this board only.
- Serialize explicit saves with a synchronous ref, release on every exit, and display retry guidance on thrown network failures. No Auth/RLS/schema/PDF engine or deployment change.
- Reference: React useRef official documentation; event-handler refs persist synchronously across renders. Reusable rule: exercise overlapping requests, not just sequential successful saves.
- Verification in progress; live A/B fixtures, physical Android and independent reviewer unavailable. No merge/deploy authorized.
