# Sirati Analytics — Security and launch gate (read-only review, 2026-10-11)

**Scope:** Staging `ykfxcxhozqqsvhtdyxho` and GitHub PRs #115/#116. A narrowly scoped permission migration **was applied to Staging only** and verified; no Production changes, paid services, secrets or customer CV inspection. This is a technical assessment, **not an independent Security Agent sign-off**.

## Evidence and disposition

| Check | Finding / evidence | Gate |
|---|---|---|
| GitHub PR #115 | Build, isolated Staging smoke and E2E workflow all reported **success** on head `aa82ac22d4d19b302162fc193f312fdb57ab2a01`; remains **Draft / unmerged** | PASS for CI; manual verification pending |
| Metrics schema | Present in Staging; `events`, `session_quota`, `day_quota`, `admin_users` all have **0 rows** during read-only check. No owner admin provisioned | BLOCKED for live dashboard |
| Direct metrics access | `anon` and `authenticated` have no `USAGE` on `sirati_metrics`; direct access blocked by schema grants/RLS | PASS for read-only metadata check |
| `public.rls_auto_enable()` | **STAGING FIXED** with migration `20261010223236`: `EXECUTE` revoked for PUBLIC/anon/authenticated; `postgres` retains execute; `ensure_rls` still active and synthetic public-table RLS test passed in rolled-back transaction | **PASS in Staging; independent review pending** |
| `public.sirati_track_event` | Deliberately executable by anonymous visitors for `page_view` only, validates event type and fixed normalized routes; 80 calls per session/day, 15,000 site-wide/day | **P1 abuse/residual-risk review**; current caps not bot protection |
| `public.sirati_analytics_summary(1/7/30)` | Executable by authenticated only; checks `auth.uid()` against private admin allowlist and returns aggregates | Access design reasonable; **real A/B and admin tests NOT RUN** |
| RLS-without-policy notices | Five private, RLS-enabled tables, no direct `anon`/`authenticated` schema access | INFO, expected deny unless proven otherwise |
| Leaked-password protection | Disabled in Staging; Supabase docs state availability on **Pro plan and above** | Do not incur charges or modify Auth; owner choice later |
| Automatic retention | `pg_cron` **installed on Staging**; 1 active daily 02:12 UTC/GMT cron job; cleanup function tested with rolled-back synthetic records and no leftovers | **Staging manual execution PASS; first automatic run NOT OBSERVED** |
| Production analytics | `sirati_metrics.events` and `public.sirati_analytics_summary` absent in prior read-only Production inventory. GitHub Pages feature flag remains OFF | **No Production tracking** |

Sources: [Issue #87](https://github.com/Abdulrahmanelsayyad/sirati/issues/87), [Issue #99](https://github.com/Abdulrahmanelsayyad/sirati/issues/99), [PR #115](https://github.com/Abdulrahmanelsayyad/sirati/pull/115), [Supabase advisor on anonymous definer functions](https://supabase.com/docs/guides/observability/advisors?queryGroups=lint&lint=0028_anon_security_definer_function_executable), [Supabase Cron](https://supabase.com/docs/guides/cron), [Supabase Password security](https://supabase.com/docs/guides/auth/password-security).

## Proposed, **not executed**, least-privilege remediation

**First**, the following migration has **already been applied on Staging only** after owner acceptance. It is recorded in `supabase/migrations/20261010223236_staging_restrict_rls_auto_enable_rpc_execution.sql`; **no Production execution authorized**:

```sql
-- Protect an event-trigger helper that should not be a client RPC.
-- Already applied to Staging, NOT Production.
REVOKE EXECUTE ON FUNCTION public.rls_auto_enable()
  FROM PUBLIC, anon, authenticated;
```

Verified on Staging: both client-role permissions are **false**, `postgres` retains execute, and active trigger `ensure_rls` enabled RLS on a synthetic public table in a transaction that was rolled back. The test table is absent. Independent review is still outstanding; do not change the trigger itself.

**Second**, retain the deliberate limited `sirati_track_event` exposure only with written Security acceptance and mitigation for caller-controlled random session IDs, spoofable events and exhausting the global cap. Consider checking the site-wide quota **before** creating a per-session quota row and a separate operational kill switch to disable tracking without breaking CV creation. Verify successful and rejected inserts with rollback-only synthetic data. Do **not** treat the 15k/day limit as robust rate limiting or distinct-person measurement.

**Third**, retain `sirati_analytics_summary` as authenticated with its internal admin allowlist. Provision the owner's Auth UUID server-side only after verification, with no UUID, token, private email, or secret added to source. Test verified owner vs regular user vs anonymous user; no public direct read grants.

## Proposed retention and collection controls (owner/design approval pending)

- Use **35 days** retention for accepted analytics events, allowing 30-day reports with a modest grace margin. Count **page views** and **estimated browser sessions**, never assert a number of unique people.
- Use **2 UTC days** retention for `session_quota` and `day_quota` records after their calendar day has passed; these quotas serve abuse/cost safety, not visit analytics.
- Introduce a reviewed and versioned cleanup function that deletes **only** qualifying records in `sirati_metrics.events`, `sirati_metrics.session_quota` and `sirati_metrics.day_quota`. Never prune `auth.users`, `cv_documents`, CV versions, payments, or historical order data.
- **Staging now has** `pg_cron` installed and a single active daily job `sirati-analytics-retention-staging` at 02:12 UTC/GMT; migration `20261010223659_staging_analytics_retention_schedule` is recorded in this PR. The invoker-rights cleanup function was manually verified with synthetic fixture records inside a fully rolled-back transaction; records and admin fixtures remain at zero. **First scheduled job execution has not yet occurred / was not observed.** Before any Production rollout, independently verify a cron job run and an explicitly approved separate Production retention schedule.
- Display a bilingual privacy explanation, obtain opt-in consent, respect DNT/GPC/owner QA exclusion, avoid raw URLs, IPs, identifiers or CV contents. Manual mobile (360/390px), RTL/LTR and test-traffic checks still required.
- Exclude Staging traffic from Production analytics; avoid any event collection without consent.
- Historical page views cannot be reconstructed from existing user registrations or saved CVs.

## Required release decisions

1. Independent Security Agent signs off on Issue #99 and an authorized Staging migration plus retention mechanism, including an exploitability/risk classification for each advisor notice.
2. Independent QA verifies the exact candidate revision and live Staging consent, Auth A/B, roles, mobile, PDF, consent rejection, malformed requests, rate-limit/failure paths, and deletion boundaries.
3. Operator verifies the owner's Auth UUID **privately** and runs admin allowlist tests. No client-side role flag is an authorization boundary.
4. Owner explicitly approves each **Production** analytics migration, merge/deploy, and activation of `NEXT_PUBLIC_ANALYTICS_ENABLED`. No automatic publication or payment.
5. After approved activation, record the first real page view and compare privacy-safe aggregate with the dashboard. Do not claim old traffic totals.

**Decision:** Staging RPC hardening **APPLIED and verified**; Staging retention function and daily cron job **INSTALLED**, manual synthetic deletion **PASS**, first automatic cron-run **NOT YET OBSERVED**. Real owner provisioning, independent Security/QA sign-off, and all Production changes/activation **BLOCKED**.

## Supplemental access-control verification (2026-10-11, Staging)

- `anon` has no execute permission for `public.sirati_analytics_summary(integer)`; logged-in users can call the endpoint, but the function enforces the admin UUID allowlist.
- In a **rollback-only transaction**, a synthetic `authenticated` non-admin was denied by the server function, while a synthetic allowlisted admin successfully retrieved the 7-day aggregate.
- Admin accepted 1-day and 30-day windows; unsupported 31-day window was rejected. No real user email, token, CV or identity was copied, and no synthetic allowlist membership persisted.
- `cron` scheduler process observed running. Daily job active; `cron.job_run_details` contained **0 executions for this job** at verification time.
- Manual function execution removed expired synthetic events and UTC-dated quota records only, retained recent rows and was rolled back. Real deletion automation is not accepted as fully verified until a scheduled run is observed.
- The security evidence is technical self-review, **not the required independent Security/QA reviewer sign-off**.

## Staging atomic quota hardening (2026-10-11, separately approved testing)

- **Applied on Staging only**: migration `20261010224342_staging_analytics_atomic_quota_ingest`, recorded in `supabase/migrations/20261010224342_staging_analytics_atomic_quota_ingest.sql`.
- The public collector now verifies the **sitewide** 15,000/day budget before allocating a caller-supplied session UUID's quota row. If the session cap (80/day) or global cap fails, an inner PL/pgSQL exception block atomically rolls back **both** quota updates and returns false. Concurrent duplicate event retries do not charge quota twice.
- **PASS** on Staging with synthetic rollback-only `anon` test: valid event inserted, retry idempotent, global limit denial creates no new session row, session limit denial consumes no daily budget, anonymous `pdf_export_succeeded` rejected. No persistent fixture rows; events, session quotas, day quotas and admin allowlist remain at **zero**.
- **Residual risk**: a determined remote caller can forge randomized session/event UUIDs and consume the genuine 15,000/day global allowance. The quota hardening limits write growth and partial accounting errors; it **does not establish real unique visitors or fully prevent denial of analytics**. Independent Security reviewer must accept this tradeoff, possibly require a non-exposing kill switch and telemetry abuse alert, before launch.
- Staging Security Advisor still reports deliberate `sirati_track_event` anonymous `SECURITY DEFINER` reachability, authenticated owner-aggregate `SECURITY DEFINER` reachability, and an Auth password warning. No report claims those warnings disappeared.
- PR #115 and PR #116 remain independent, unmerged drafts; their integration, live consent/mobile testing, real owner provisioning, independent reviewer sign-off, cron first real daily run, Production migration and activation remain separate gates.
