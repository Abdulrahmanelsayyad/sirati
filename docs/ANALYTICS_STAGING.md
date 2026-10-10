# Sirati Analytics — implementation gate (#87)
 
## What this first PR provides
A first-party, zero-SaaS-cost Supabase schema with an anonymous-safe event
ingest RPC and a **server-enforced, administrator-only** aggregate report RPC.
No data from existing CV content is copied or indexed for analytics. The
migration is designed for **Staging first**; Production remains unchanged.
 
## Terms of measurement
- `page_views`: accepted, client-reported page views after activation.
- `estimated_sessions`: distinct randomly generated session UUIDs, not
  distinct people, devices, or durable visitors. Refresh may increase views,
  but normally not session count.
- `registered_accounts`: undeleted, non-anonymous Supabase Auth users.
- `cv_creators` / `saved_cvs`: existing saved-document rows.
- `pdf_export_events`: browser-reported completed exports, not paid orders
  or a cryptographically verified download.
- Events can be spoofed; do not use these metrics for certified revenue,
  billing, or externally guaranteed traffic claims.
 
## Security/operating procedure
1. No direct read/write grants on private `sirati_metrics` tables; RLS is enabled.
2. Ingestion accepts only six event names and eight normalized route names:
   **never submit path queries, CV contents, emails, IPs, or free-form text**.
3. Anonymous visitors may report only `page_view`. Other events require login.
4. Daily quotas limit one session to 80 calls and the site to 15,000 accepted
   attempts. These are **cost safety caps, not anti-bot guarantees**.
5. To authorize an admin, the operator must first verify the owner Auth UUID
   and provision it **server-side** into `sirati_metrics.admin_users`.
   Do not insert that UUID into public source or expose the table to clients.
6. Frontend instrumentation and owner dashboard are separate follow-up work:
   no event recording begins just by merging this SQL file.
7. Only activate collection with opt-out + DNT/GPC handling, test-traffic
   exclusion, and user-facing privacy notice reviewed in the applicable locale.
8. Keep Production migrations, RLS, authentication, deployment and merge behind
   separate explicit owner approval and independent Security/QA sign-off.
9. Data retention is **not automated** in this first PR; agree on retention
   policy and a tested cleanup mechanism before activation.
 
## QA checklist
- Anonymous page-view allowed; anonymous non-page-view denied.
- Invalid event, route and session rejected; no unexpected content accepted.
- Duplicate event UUID idempotent.
- Private tables inaccessible as `anon` and `authenticated`.
- Unauthorized report access denied even when logged in.
- Authorized report returns aggregates only; window restricted to 1/7/30 days.
- New build/CI, browser integration, DNT/opt-out, real PDF success events,
  owner UI and A/B test: **NOT RUN** (pending next PRs).
