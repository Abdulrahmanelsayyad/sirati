# Sirati Agent Board

## Priority
Keep Sirati reliable, secure, polished, easy to use, and focused on the core customer journey:
Login -> Template -> CV Builder -> Save -> Preview -> PDF Order.

## Now
- **P1-READINESS-01 — Live CV Readiness Check** — Owner: Design Agent + Bug Fixer — Status: IN PROGRESS (2026-10-08) — Add a zero-cost live completion guide for essential CV sections; no fabricated ATS score, no paid API, and no changes to auth/payment/data rules.
- **P0-BUILDER-01 — Builder status messages overlap the sticky CV preview** — Owner: Sirati Bug Fixer — Status: VERIFIED (2026-10-07) — CSS stacking regression fixed; PR #6 passed build + Sirati E2E QA and was verified on the live site after deployment.
- **P0-AUTH-01 — Account Save/Restore + Data Isolation** — Owner: Security Agent + QA & Release Agent — Status: VERIFIED (2026-10-07) — Production RLS tested bidirectionally with rollback-only users; own create/update/version/PDF-order operations succeed; cross-user read/update/delete/insert/version/order operations are blocked; Data API grants tightened to least privilege.
- **P0-PDF-01 — PDF order / payment clarity** — Owner: Customer Liaison + Design Agent — Status: VERIFIED (2026-10-08) — Manual EGP 50 clean-PDF flow clarified for InstaPay/Vodafone Cash, reference submission and pending/approval messaging; PR #7 passed build + E2E, deployed successfully, and was verified on the live site.
- **Coordination** — Owner: Deputy Manager — Status: ACTIVE — Maintain conflict map and enforce handoffs; no production completion claim before QA and changelog entry.

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
