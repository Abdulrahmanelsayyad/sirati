# Sirati Agent Team

The names below are contributor roles and historical playbooks, not nine implemented autonomous AI services. Repository audit at `2d46485` found no model client, inference endpoint, scheduler, or executable agent manager in the reconstructed app. All contributors must follow `AGENT_POLICY.md`.

## Current execution architecture
- One task owner coordinates implementation and handoff in one branch/PR. Manager and Deputy are one coordination responsibility; retain historical names for continuity only.
- Product work uses the existing deterministic generators and editable browser content libraries. Design, Bug Fixer, CV Expert and Performance/SEO are review specialties, not separately deployed agents.
- Quality verification uses existing build/browser/PDF tests plus `qa/verification.py`; Security uses independent boundary, dependency and authorization checks. These remain separate acceptance results, not producer self-approval.
- Customer Liaison is a manual support responsibility. A mailto link is not a monitored inbox or an autonomous reply service. Do not send customer messages without explicit authorization.
- No deployment, merge, database/auth/payment mutation or secret access is granted by a role name, board status or passing test. Each needs separate owner authorization.
- Handoff: one owner, scope/files, base/head SHA, reproducible commands, evidence, failures/not-run checks and next reviewer. An unresolved check blocks the claim it would establish.
- See `docs/AGENT_ARCHITECTURE_AUDIT.md` for inventory, scores, evidence and limitations.


## Historical role names (not executable agents)
1. **Sirati Manager** — coordinates the whole team, resolves priorities, prevents conflicting work, reviews outcomes, and reports only meaningful issues or progress to the owner.
2. **Sirati Deputy Manager** — maintains the shared work board, detects overlaps/blockers, prepares handoffs, and acts as continuity backup for the Manager.
3. **Sirati Design Agent** — improves visual design, spacing, layout, mobile responsiveness, Arabic RTL/English consistency, and CV template presentation. Runs daily.
4. **Sirati Security Agent** — reviews repository/deployment security posture, dependency alerts, accidental exposure risks, public assets, and configuration hygiene. It may make only low-risk security hardening changes allowed by AGENT_POLICY.md. Protected settings always require owner approval.
5. **Sirati Bug Fixer** — detects and fixes reproducible low-risk defects in navigation, forms, rendering, persistence, responsive behavior, and deployment output. It must verify the build and affected behavior; deployment requires separate owner authorization.
6. **Sirati Customer Liaison** — monitors customer-facing requests, PDF-order/support signals, and connected communication channels. It replies only through an explicitly connected customer communication channel and escalates payment, disputes, privacy, abuse, or ambiguous cases to the owner.
7. **Sirati CV Expert** — helps customers build stronger CVs using factual information supplied by the customer. It improves wording, structure, ATS clarity, and section guidance without inventing qualifications, jobs, dates, licenses, or achievements.
8. **Sirati QA & Release Agent** — owns end-to-end testing before a task is considered complete. It checks landing → sign in → template → builder → save/restore → preview → PDF order on desktop and mobile, records reproducible failures, and verifies the live deployment after fixes.
9. **Sirati Performance & SEO Agent** — improves loading performance, technical SEO, metadata, accessibility basics, and page-weight hygiene without changing business logic or protected settings. It must use measurable before/after checks when possible.

## Shared coordination rules
- Use `AGENT_BOARD.md` as the shared queue/status board.
- Use `AGENT_CHANGELOG.md` for completed autonomous changes.
- Before editing, check the board and recent commits to avoid duplicate/conflicting work.
- One agent owns a task at a time.
- Prefer small, reversible changes.
- Any protected or high-risk action is marked **BLOCKED — OWNER DECISION REQUIRED**.
- Manager has coordination priority; Deputy handles handoffs and continuity, not product-policy overrides.


## Continuous improvement
- Every agent reads `AGENT_SKILLS.md` and `AGENT_LESSONS.md` before meaningful work.
- After a verified result, the responsible agent records reusable lessons and improves its playbook.
- The Manager decides whether a lesson should become a shared team rule.
- The Deputy checks that lessons are not duplicated, speculative, or contradictory.
- Agents improve methods, checklists, prompts, tests, and execution patterns; they do not alter model weights, permissions, or protected safety boundaries.
- A learned technique is applied to the site only when it is relevant, low-risk, reversible, and verified.


## Coordination & conflict-prevention protocol
- Every active task must have exactly one **Owner**, one status, and one clearly defined scope in `AGENT_BOARD.md`.
- No agent may edit files or UI areas currently owned by another active task unless the Manager explicitly reassigns or merges the work.
- Before starting, each agent must check: current board ownership, recent commits, and any open handoff notes.
- Work touching the same feature must be serialized: **Design/Content proposal → Implementation/Fix → QA verification → Security/Performance review when relevant → Manager closeout**.
- Handoffs must state: what changed, files/areas touched, what remains, verification completed, and known risks.
- If two agents detect overlapping work, both stop changes and the Deputy resolves ownership before either continues.
- The Deputy maintains a conflict map for active tasks and flags shared files/components before work starts.
- The Manager is the only role that may reprioritize or reassign overlapping tasks.
- A PR can be implementation-complete after local/CI checks; release-complete additionally requires separately authorized deployment and live acceptance. Never deploy merely to close a board entry.
- If a deployment fails, the active owner pauses related downstream work until the failure is understood or rolled back.
- Protected areas (auth, RLS, secrets, payment rules, repo/security settings) remain owner-approval gated regardless of agent ownership.


## Benchmark-first, zero-cost rule
- Before meaningful product work, the assigned agent performs a focused benchmark of leading, reputable products relevant to its specialty using current public information when available.
- Examples by role: Design studies leading CV/design builders; CV Expert studies high-quality resume guidance and ATS-oriented builders; QA studies polished onboarding and checkout flows; Performance/SEO studies technically strong SaaS landing experiences; Customer Liaison studies excellent support/help-center patterns; Security studies established secure-by-default practices; Bug Fixer studies proven interaction/state patterns when relevant.
- The goal is not to copy branding, layouts, wording, proprietary assets, or trade dress. Extract principles, friction-reduction ideas, interaction patterns, quality bars, and reusable lessons.
- Each agent asks: "Can Sirati make this simpler, clearer, faster, more trustworthy, or more useful for its target user?"
- Prefer solutions that are better for Sirati's actual audience rather than feature-for-feature imitation.
- Every proposed implementation must remain zero-cost unless the owner explicitly approves spending: no paid APIs, no paid SaaS dependency, no paid templates/assets, no paid hosting upgrade, no paid AI calls, and no credit-consuming feature.
- Free/open-source/browser-native capabilities are preferred when their licenses and security posture are suitable.
- Benchmark findings must be concise and task-specific; research must not delay execution unnecessarily.
- A benchmark-inspired change still follows normal ownership, conflict-prevention, protected-area, build, QA, and live-verification rules.
