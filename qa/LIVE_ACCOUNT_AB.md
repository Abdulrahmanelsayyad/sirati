# Sirati A/B shared-browser privacy check (read-only fixture test)

This optional test supports [Issue #24](https://github.com/Abdulrahmanelsayyad/sirati/issues/24) and [Issue #25](https://github.com/Abdulrahmanelsayyad/sirati/issues/25). **It has not been run on actual A/B accounts by adding this file.** Ordinary CI does not sign in and should not claim A/B PASS.

## Safe prerequisites

Use **two dedicated synthetic QA accounts**, each already holding its **own saved test CV**, not real customer accounts or CV content. The existing A document should contain a distinctive harmless A-only text marker within a visible CV field (not just its title). Keep the existing B document title distinct. The test reads these fixtures but does **not** create, modify, approve, or delete server documents.

Test in a single fresh browser context (same profile for A then B), using **only environment variables local to the test runner**. Never paste credentials into an issue, chat, PR, workflow log, or source control. No screenshot, trace, or full CV field content is captured. Use a staging instance if available. Production requires explicit opt-in and a fixture-only procedure.

## Running locally with an existing reconstructed Sirati site

Install the repository's existing Playwright Chromium dependency in the working directory for the reconstructed Next.js source (as in `.github/workflows/qa.yml`), then copy `qa/live_account_ab_readonly.mjs` alongside that directory's Playwright installation. Set these environment variables privately:

| Variable | Purpose |
| --- | --- |
| `SIRATI_AB_BASE_URL` | Exact `https://abdulrahmanelsayyad.github.io/sirati/`, or `http://127.0.0.1:<port>/sirati/` for local testing |
| `SIRATI_AB_A_EMAIL` / `SIRATI_AB_A_PASSWORD` | Synthetic test account A |
| `SIRATI_AB_B_EMAIL` / `SIRATI_AB_B_PASSWORD` | Synthetic test account B |
| `SIRATI_AB_A_DOC_ID` | Existing A-owned test CV UUID |
| `SIRATI_AB_A_TITLE` | Existing A CV title in My Documents |
| `SIRATI_AB_B_TITLE` | Existing B CV title in My Documents |
| `SIRATI_AB_A_MARKER` | Unique A-only harmless CV field value |
| `SIRATI_AB_ALLOW_PRODUCTION=YES` | Mandatory explicit consent to run the fixture check on the production domain |
| `SIRATI_AB_HEADED=YES` | Optional visible browser for manually observing QA |

Run `node live_account_ab_readonly.mjs` from the folder with Playwright installed. Missing fixtures produce **NOT RUN**, exit 2. An actual test failure produces exit 1. No account usernames, passwords, tokens, or CV text should be included in shared QA output.

## Checks and interpretation

1. A signs in and sees its saved synthetic CV: PASS/FAIL.
2. A opens its saved document and confirms its harmless marker: PASS/FAIL.
3. Browser-local account draft is created through the existing builder: PASS/NOT RUN.
4. A logs out, then B signs in **in the same browser context**: PASS/FAIL.
5. B sees its own saved CV, not A's title: PASS/FAIL.
6. B's profile shows only B's verified account identity: PASS/FAIL.
7. B opens A's saved document URL, and A's unique CV marker never appears in the UI: PASS/FAIL. **This is UI-only, not an authoritative direct RLS test.**
8. Test whether A's earlier device draft remains readable in origin-wide `localStorage` after B signs in: PASS/FAIL/NOT RUN. If readable, mark **FAIL (privacy)** even when other UI checks pass. This is the already documented Issue #25 risk.

The test does **not** prove direct REST/PostgREST RLS permission enforcement, encryption, access to raw customer data, complete account isolation, or independent Security/QA sign-off. Do not close Issue #24 unless the independent reviewer also performs permitted server-side read-denial tests, signs a report for the exact deployed SHA, and explicitly resolves the Issue #25 device-storage risk. Do not purge or alter any existing customer's device drafts without an approved migration/recovery plan.

## Status at introduction

- Current source static finding: the A-scoped JSON draft is stored plaintext in shared-origin localStorage; there is no evidenced sign-out purge. **FAIL for shared-device confidentiality by source review, exploitation not tested here**.
- Real A→logout→B end-to-end: **NOT RUN until synthetic accounts and existing fixtures are available**.
- Earlier browser/E2E and PDF tests: retain their prior PASS evidence; do not rerun them just to claim this check.
