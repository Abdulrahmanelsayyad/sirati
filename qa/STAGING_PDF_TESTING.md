# Sirati – isolated PDF / manual-payment QA handoff

**Scope:** Issue #37; staging-only build; **no merge, deployment, real payment, or production changes**.

## Connected environments
- Staging Supabase project: `Sirati-Staging` / `ykfxcxhozqqsvhtdyxho`.
- Production Supabase project: `Sirati` / `hzzojoiqzbeivxesjlyf` (DO NOT USE for tests).
- This PR adds a **pull_request-only** GitHub Actions workflow that reconstructs the existing app, injects *only* the staging **publishable** key, checks that exported browser assets contain the staging URL but not the production URL, and runs a staging-specific login/route bootstrap smoke test. The repository's existing E2E UI/PDF rendering check also runs as a **separate PR workflow**, not as proof of staging account payment unlock.
- A successful job uploads `sirati-staging-pdf-preview` as an **Actions artifact only**. This is not a live hosted website or a public testing link. No secrets or service-role keys are provided to the browser.

## Steps to use the preview (after CI passes)
1. Open the PR > **Checks** > **Sirati Staging PDF Preview (build only)** > job. Confirm PASS, the staging bundle guard PASS, and the staging login/route bootstrap check PASS.
2. Download the `sirati-staging-pdf-preview` artifact from the Actions run. Extract the contents into a local folder `preview-root/sirati/`.
3. Serve `preview-root` locally with `python3 -m http.server 4173 --directory preview-root` (or another static local server). Browse to `http://127.0.0.1:4173/sirati/`.
4. For actual sign-in, configure the **staging-only** Supabase Auth allowed redirect URL to match the chosen test origin (e.g. `http://127.0.0.1:4173/sirati/auth/confirm`), after owner approval. Do **not** change production auth redirect settings.
5. Use staging-only test account A/B. Never submit credentials, JWTs, payment proof, or private CV content into public GitHub logs.

## Real manual payment → unlock test — NOT covered by the PR's browser smoke
Record PASS/FAIL/BLOCKED/NOT RUN, exact PR SHA, environment, date, and reproducible evidence for each:
- [ ] A logs into the locally-served staging app, creates/saves a synthetic CV, submits a fake reference; an owned `pdf_orders` row appears with `status=pending`, `amount_egp=50`, `reviewed_at=NULL`.
- [ ] Before approval: clean PDF export stays blocked after refresh and new session. A cannot get a clean PDF by print/DOM/download even if a UI button is disabled. **This requires a separate paywall-bypass security review; do not assume client-side watermarks are enforcement.**
- [ ] B cannot read/change A's CV, order, or approval state; A cannot self-approve or alter price.
- [ ] A trusted operator manually marks the **specific synthetic** A request `approved` in *staging*; verify change with a staged role; never treat this as real payment.
- [ ] A refreshes order status and obtains an actual clean, correctly paginated A4 PDF via **Save clean PDF**; correct account/CV, no watermark; test desktop and mobile, English and Arabic.
- [ ] B and an unapproved/rejected A order remain blocked. Duplicate requests, wrong reference, session expiry/re-login and different CV version are tested.
- [ ] Independent Security + QA agents sign off on the *exact* patch and evidence. Align with #26, #31, #33 before any production rollout.

## Known limitations / release gate
- Existing `qa/e2e.mjs` verifies payment copy, mobile layout and browser-generated PDF smoke **but does not perform an approved-order integration test**. The staging preview workflow does not invent that result.
- A static GitHub Pages-style app cannot securely rely on a disabled button or removable watermark as the only enforcement for a paid download. Review the actual untrusted-client export path and require a trusted source of authorization before calling it secure.
- The staging database was configured and tested manually using synthetic users. This PR does not replay or migrate its database state, and it does not include PR #31's production migration. **Do not merge or deploy this test-only workflow until project owner and QA approve**; the workflow is intended for review as a draft.
- No source or tokens from real customers, service-role key or paid transactions should be used.
