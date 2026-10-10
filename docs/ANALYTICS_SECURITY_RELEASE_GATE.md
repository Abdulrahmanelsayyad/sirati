# Sirati Analytics — Security and launch gate (read-only review, 2026-10-11)

**Scope:** Staging `ykfxcxhozqqsvhtdyxho` and GitHub PR #115 only. No Production database inspection, writes, deployment, migration, paid services, secrets or real customer CV inspection. This is a preparatory technical assessment, **not an independent Security Agent sign-off**.

## Evidence and disposition

| Check | Finding / evidence | Gate |
|---|---|---|
| GitHub PR #115 | Build, isolated Staging smoke and E2E workflow all reported **success** on head `aa82ac22d4d19b302162fc193f312fdb57ab2a01`; remains **Draft / unmerged** | PASS for CI; manual verification pending |
| Metrics schema | Present in Staging; `events`, `session_quota`, `day_quota`, `admin_users` all have **0 rows** during read-only check. No owner admin provisioned | BLOCKED for live dashboard |
| Direct metrics access | `anon` and `authenticated` have no `USAGE` on `sirati_metrics`; direct access blocked by schema grants/RLS | PASS for read-only metadata check |
| `public.rls_auto_enable()` | `SECURITY DEFINER`, owner `postgres`, callable by PUBLIC/anon/authenticated; attached to active `ensure_rls` event trigger | **P1 harden public EXECUTE** after compatibility test |
| `public.sirati_track_event` | Deliberately executable by anonymous visitors for `page_view` only, validates event type and fixed normalized routes; 80 calls per session/day, 15,000 site-wide/day | **P1 abuse/residual-risk review**; current caps not bot protection |
| `public.sirati_analytics_summary(1/7/30)` | Executable by authenticated only; checks `auth.uid()` against private admin allowlist and returns aggregates | Access design reasonable; **real A/B and admin tests NOT RUN** |
| RLS-without-policy notices | Five private, RLS-enabled tables, no direct `anon`/`authenticated` schema access | INFO, expected deny unless proven otherwise |
| Leaked-password protection | Disabled in Staging; Supabase docs state availability on **Pro plan and above** | Do not incur charges or modify Auth; owner choice later |
| Automatic retention | `pg_cron` **available but not installed** in Staging; metrics cleanup not scheduled | **BLOCKED** before Production collection |
| Production analytics | `sirati_metrics.events` and `public.sirati_analytics_summary` absent in prior read-only Production inventory. GitHub Pages feature flag remains OFF | **No Production tracking** |

Sources: [Issue #87](https://github.com/Abdulrahmanelsayyad/sirati/issues/87), [Issue #99](https://github.com/Abdulrahmanelsayyad/sirati/issues/99), [PR #115](https://github.com/Abdulrahmanelsayyad/sirati/pull/115), [Supabase advisor on anonymous definer functions](https://supabase.com/docs/guides/observability/advisors?queryGroups=lint&lint=0028_anon_security_definer_function_executable), [Supabase Cron](https://supabase.com/docs/guides/cron), [Supabase Password security](https://supabase.com/docs/guides/auth/password-security).

## Proposed, **not executed**, least-privilege remediation

**First**, on a dedicated reviewed Staging migration **after explicit Staging change authorization**:

```sql
-- Protect an event-trigger helper that should not be a client RPC.
-- This is a proposal, NOT applied in any database.
REVOKE EXECUTE ON FUNCTION public.rls_auto_enable()
  FROM PUBLIC, anon, authenticated;
```

Pre/post assertions: `has_function_privilege('anon', 'public.rls_auto_enable()', 'EXECUTE')` and the equivalent for `authenticated` must be false. Independently verify that event trigger `ensure_rls` still fires on safe synthetic `CREATE TABLE` in Staging (transactionally rolled back); if broken, rollback the grant change. Do not alter/remove the `ensure_rls` trigger itself.

**Second**, retain the deliberate limited `sirati_track_event` exposure only with written Security acceptance and mitigation for caller-controlled random session IDs, spoofable events and exhausting the global cap. Consider checking the site-wide quota **before** creating a per-session quota row and a separate operational kill switch to disable tracking without breaking CV creation. Verify successful and rejected inserts with rollback-only synthetic data. Do **not** treat the 15k/day limit as robust rate limiting or distinct-person measurement.

**Third**, retain `sirati_analytics_summary` as authenticated with its internal admin allowlist. Provision the owner's Auth UUID server-side only after verification, with no UUID, token, private email, or secret added to source. Test verified owner vs regular user vs anonymous user; no public direct read grants.

## Proposed retention and collection controls (owner/design approval pending)

- Use **35 days** retention for accepted analytics events, allowing 30-day reports with a modest grace margin. Count **page views** and **estimated browser sessions**, never assert a number of unique people.
- Use **2 UTC days** retention for `session_quota` and `day_quota` records after their calendar day has passed; these quotas serve abuse/cost safety, not visit analytics.
- Introduce a reviewed and versioned cleanup function that deletes **only** qualifying records in `sirati_metrics.events`, `sirati_metrics.session_quota` and `sirati_metrics.day_quota`. Never prune `auth.users`, `cv_documents`, CV versions, payments, or historical order data.
- Enable `pg_cron` in **Staging** and schedule one daily job only after separate explicit approval and tests; `pg_cron` is not installed there now. Confirm cron execution, date boundaries, privileges and job-run visibility. Retention is **not operational** until the job completes at least one controlled trial.
- Display a bilingual privacy explanation, obtain opt-in consent, respect DNT/GPC/owner QA exclusion, avoid raw URLs, IPs, identifiers or CV contents. Manual mobile (360/390px), RTL/LTR and test-traffic checks still required.
- Exclude Staging traffic from Production analytics; avoid any event collection without consent.
- Historical page views cannot be reconstructed from existing user registrations or saved CVs.

## Required release decisions

1. Independent Security Agent signs off on Issue #99 and an authorized Staging migration plus retention mechanism, including an exploitability/risk classification for each advisor notice.
2. Independent QA verifies the exact candidate revision and live Staging consent, Auth A/B, roles, mobile, PDF, consent rejection, malformed requests, rate-limit/failure paths, and deletion boundaries.
3. Operator verifies the owner's Auth UUID **privately** and runs admin allowlist tests. No client-side role flag is an authorization boundary.
4. Owner explicitly approves each **Production** analytics migration, merge/deploy, and activation of `NEXT_PUBLIC_ANALYTICS_ENABLED`. No automatic publication or payment.
5. After approved activation, record the first real page view and compare privacy-safe aggregate with the dashboard. Do not claim old traffic totals.

**Decision:** Staging security review prepared; activation **BLOCKED**, no data writes or independent sign-off.