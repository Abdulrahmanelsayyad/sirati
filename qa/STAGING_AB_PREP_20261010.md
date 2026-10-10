# Sirati CV — A/B privacy Staging preparation (2026-10-10)

**Status: BRANCH PREPARED ONLY — NO DEPLOYMENT, NO PR, NO MERGE, NO DATABASE CHANGE.**

## Exact baseline and ownership

- Repository: `Abdulrahmanelsayyad/sirati`
- Isolated branch: `qa/staging-ab-privacy-20261010`
- Based on reviewed `main` commit: `d5cf774a07e0b0160b0bdb5882547e0e0fe7141b`.
- Contains already merged fixes: PR #73 (optional A/B harness), #81 (synthetic draft-cleanup regression checks), #83 (three sign-out paths); PR #95 (anonymous template gallery).
- Old Netlify staging publish branch: `qa/staging-pdf-preview-37` at `47e2faef7cef42fe4808ef01cb5c87c354a8786e`. **Do not update that branch**.
- Existing GitHub Actions staging build: `.github/workflows/staging-pdf-preview.yml`. It is PR-triggered and builds/uploads an **artifact only**, not a deployed website. Avoid starting PR/CI or Netlify previews without an explicit separate approval. No workflow or GitHub Actions permission changes are requested in this branch.

## Strict environment isolation

- Allowed Supabase project: **Sirati-Staging** (`ykfxcxhozqqsvhtdyxho`).
- Allowed published browser API URL for a future staging build: `https://ykfxcxhozqqsvhtdyxho.supabase.co`.
- **Forbidden** in the staging browser bundle: Production project `hzzojoiqzbeivxesjlyf` / `https://hzzojoiqzbeivxesjlyf.supabase.co`.
- Reuse `qa/staging_bundle_guard.py` against a future exported static `out/`. It asserts a staging reference exists and a production reference does not. This proves bundle configuration, **not** actual server connection, RLS, or account isolation.
- Do not add secrets, service-role keys, customer records, credentials, or active payment tests. Netlify's project-level environment-variable list is empty as observed by the owner; the existing historic Netlify deployment has **not** been independently checked for staging-only runtime configuration.

## Verification gates to complete before any hosted A/B test

1. Owner separately approves a staging-only build/preview; do not update `main`, Production, or the old Netlify branch.
2. Reconstruct/build the **exact isolated branch SHA**, with existing pipeline and staging-only Supabase publishable browser config. Run existing static guard + staging smoke and reuse their CI evidence. Mark any unrun steps NOT RUN.
3. Verify preview hosting will remain staging-only: no production keys/URL in emitted browser assets; the hosted URL, runtime configuration, and Auth redirect allow-list are verified before login. A build artifact alone is not a live website.
4. Use two **pre-existing synthetic Staging accounts** and synthetic saved CVs with harmless distinct markers. No credentials in chat, GitHub logs, or screenshots. Get separate consent before creating/modifying Staging fixtures or hosting.
5. From one fresh browser profile: A signs in, opens own document, logs out via menu (and separately via My Documents/AccountNav), B signs in, cannot see A's data, cannot open A's document or see A's plaintext draft after normal logout. Confirm cloud-saved A data remains when A returns. Check old-cache/nonstandard session-expiry paths as separate limitations.
6. Authorized independent security reviewer performs Staging RLS-denied read/update/delete checks with disposable fixtures (UI checks alone are insufficient). Independent QA signs off with exact tested SHA, time, environment and sanitized PASS/FAIL/NOT RUN evidence.
7. Only then consider closing Issues #24 and #25. Any residual plaintext browser-storage risk must be explicitly addressed, not dismissed based on a successful logout path.

## Prior evidence to reuse — do not rerun automatically

- PR #83 and PR #81 existing synthetic sign-out tests and GitHub Actions E2E/build results.
- PR #73 optional test script: `qa/live_account_ab_readonly.mjs` (its ordinary CI runs syntax only, not a real A/B journey).
- Current main build/deploy evidence (not staging): GitHub Actions run `38042328031`.
- Separate PR #96 mobile/PDF QA is draft and not part of this branch.

**Handoff outcome:** Branch exists with latest merged app code, but **no updated staging website or independently validated two-account security PASS exists yet**. Netlify publishing and Production changes are outside this authorization.
