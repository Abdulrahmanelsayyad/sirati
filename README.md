# Sirati CV — Free bilingual CV & career toolkit

**Live website:** https://abdulrahmanelsayyad.github.io/sirati/  
**Repository:** https://github.com/Abdulrahmanelsayyad/sirati

Sirati is a web application for creating, editing, previewing and exporting CVs in
Arabic and English. It includes multiple CV layouts, contextual Smart CV suggestions,
a CV quality/readiness helper, and free self-service career tools such as cover-letter
drafting, LinkedIn profile wording and interview practice.

**Current product policy (9 October 2026):** Existing templates, tools and browser
PDF export are free. Historical payment/order code and records can exist in the
repository/database; do not treat those as an active paywall or recurring revenue.
Suggestions are editable writing aids, **not** verified qualifications or promises of
ATS acceptance, employment or interview success.

## Technology and repository layout

- Next.js/React/TypeScript static site, deployed through GitHub Actions to GitHub Pages.
- Supabase is used for account and saved-document services when configured.
- English and Arabic/RTL support; print/PDF rendering is browser-based.
- The original source is distributed in an encoded, split archive
  (`source.part1` through `source.part7`, with **`source.part4a`,
  `source.part4b`, and `source.part4c` instead of `source.part4`**).
- `.github/scripts/prepare_pages.py` applies the versioned app patches in order.
  `qa/print_isolation_fix.py` is also required for the release build.
- `site-src/` is generated at build time and is **not** the canonical tracked source.

The encoded-source/patch architecture is functional but makes ordinary source review
and onboarding harder. Any future conversion to regular tracked app files needs a
separate, tested migration; **do not** remove these parts or patch scripts casually.

## Build from a clean checkout

**Prerequisites:** Node.js 22, npm, Python 3, `unzip`, `base64`, Git,
and a POSIX/Bash environment. Install using sources you trust.

```bash
git clone https://github.com/Abdulrahmanelsayyad/sirati.git
cd sirati
NEXT_PUBLIC_BASE_PATH=/sirati bash build.sh
```

The local build script now matches the archive-part order and preparation hooks
used by `.github/workflows/pages.yml`. It refuses to overwrite an existing
generated build directory. For another build, choose a new destination:

```bash
SIRATI_BUILD_DIR=site-src-check-2 NEXT_PUBLIC_BASE_PATH=/sirati bash build.sh
```

The static output is at `site-src/sirati-cv-source/out/` (or inside the
selected `SIRATI_BUILD_DIR`).

**Important:** Without the appropriate runtime public Supabase configuration,
the static build can succeed while account/cloud features remain unavailable.
For live configuration, consult the reviewed deployment workflow and verify
ownership/access with the authorized operator. Never commit or share secret keys,
private user records, or customer CVs. The browser-publishable key is not a
service-role secret and does not override database RLS.

## CI and release checks

- `.github/workflows/pages.yml` builds on PRs and builds/deploys on `main`.
  Pull-request builds do **not** deploy.
- `.github/workflows/qa.yml` runs reconstruction, static checks, Playwright
  E2E, mobile/print and template regressions on pull requests.
- See `qa/` for the test files and `AGENT_POLICY.md` for change boundaries.
- A green CI run is **not** evidence of a real two-account privacy test, a
  verified production data transfer, or a manual visual acceptance test.

Release procedure: feature branch -> PR -> build/tests -> independent
security/QA review as applicable -> **explicit owner approval** -> merge/deploy
-> verified live smoke test. Do not change Supabase auth/RLS, payments, secrets,
or customer data merely to test a build.

## Known handoff / due-diligence items

Before representing the project as fully ready for sale or transferring operations,
the owner and buyer should verify the following **on a controlled test setup**:

1. **Privacy:** [Issue #25](https://github.com/Abdulrahmanelsayyad/sirati/issues/25)
   documents unencrypted account CV drafts in origin-wide browser
   `localStorage`. Account-scoped key names prevent mistaken normal UI restore
   but **do not** make plaintext inaccessible to other users of the same browser.
   Independent A/B verification is still tracked by
   [Issue #24](https://github.com/Abdulrahmanelsayyad/sirati/issues/24).
2. **Customer journey:** login, create/edit, save/reopen, account switch,
   language switching, 360/390px mobile, all templates, and print/export.
   CI helps; real user and independent QA checks remain necessary.
3. **Hosting/dependencies:** GitHub repository, GitHub Pages deployment,
   Supabase project/billing/backup/RLS ownership, configuration, third-party
   asset and dependency licenses, and any external domains must be inventoried
   and explicitly transferred only by their authorized owners.
4. **Business verification:** unique users, traffic, retention, expenses and
   revenue are **not certified by this repository**. Historic payment code or
   records must not be used as proof of active revenue.
5. **Operational handoff:** obtain reviewed access procedures, backup and
   recovery instructions, open issues/PRs, QA sign-offs, and a rollback plan.
   Never place account credentials, tokens or real CV information in a buyer
   demo or public issue.

The repository is public but **proprietary**. See [LICENSE](LICENSE). Public
read access is not permission to reuse or resell the code, templates or brand;
any sale/license transfer needs a separate written agreement covering ownership,
assets, dependencies and obligations.

## Contribution and maintenance

Read `AGENT_POLICY.md`, `AGENT_TEAM.md`, and `AGENT_BOARD.md` before work.
Avoid overlapping edits to the generated Builder and its generator scripts.
Keep fixes small and reversible; never make unverified production-readiness claims.
