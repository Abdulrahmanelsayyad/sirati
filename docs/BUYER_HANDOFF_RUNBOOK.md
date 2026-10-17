# Sirati CV — Buyer-controlled Deployment & Handover Runbook

**Scope:** Preparation guide for a prospective buyer and independent reviewer. This is NOT evidence that a buyer-specific migration, production account transfer, security audit, or disaster recovery exercise has happened. Use test accounts and synthetic CVs only until contracts and data-protection obligations are satisfied.

## 1. Sale asset schedule and rights
Record an attachment to the signed purchase agreement specifying: repository/code and history; proprietary branding/design/template rights the seller owns; documentation; any transferable domain(s) (if independently proven); any support/training commitment; exclusions and third-party licenses. A personal GitHub account, its github.io Pages URL, and the seller's Supabase project are **not** inherently transferable. Third-party rights require their own terms. Do not give GitHub org administration, production database access or secrets to prospective buyers.

## 2. Current production reference
- Owner/repo: Abdulrahmanelsayyad/sirati
- Reference revision: a063f214ab91f121bd51b7a084be92cdf958be58 (17 Oct 2026).
- Verified build + deploy run: https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/39033220780
- Current public demo: https://abdulrahmanelsayyad.github.io/sirati/
- Open release/buyer acceptance gate: https://github.com/Abdulrahmanelsayyad/sirati/issues/24
- **Deployment caution:** main branch pushes currently trigger an automatic Pages publish in .github/workflows/pages.yml. Do not merge staging or buyer-integration work into main as a test. Use a separate clone/branch and buyer-controlled preview.

## 3. Reproducible source build (buyer staging)
Prerequisites: trusted Node.js 22, npm, Python 3, base64, unzip, git, a Bash/POSIX shell and a clean working directory.

    git clone https://github.com/Abdulrahmanelsayyad/sirati.git
    cd sirati
    git checkout a063f214ab91f121bd51b7a084be92cdf958be58
    SIRATI_BUILD_DIR=site-src-buyer-check NEXT_PUBLIC_BASE_PATH=/sirati bash build.sh

This reconstructs archive parts (source.part1, part2, part3, part4a/b/c, part5, part6, part7), executes generator/print patches, installs dependencies and builds a static output at site-src-buyer-check/sirati-cv-source/out. The output does NOT by itself prove account/cloud features work. The reconstruction currently relies on archived pieces and ordered patch scripts; do not delete/flatten them without a separately verified migration.

**For buyer-owned deployment** choose the actual hosting path and replace build-time public settings with buyer-controlled values, including NEXT_PUBLIC_BASE_PATH, NEXT_PUBLIC_SITE_URL, NEXT_PUBLIC_SUPABASE_URL and NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY, following the reviewed build pipeline. These values are embedded into the built frontend and must point to the buyer's setup. Public/publishable keys are not server secrets, but do not share service-role, JWT secrets, signing credentials, production backups, or real account passwords. Domain/auth redirects, static base paths, CORS, DNS, CSP, SSL and integration URLs need validation for the buyer environment.

## 4. Backend & authorization validation
1. Prepare a completely separate **buyer-controlled** Supabase test project and verify plan/cost requirements.
2. Inventory actual schema, RLS, functions, storage, auth providers, email templates, redirects, backups, analytics and retention procedures with seller-authorized read-only review. Do not assume the public repository alone contains all backend configuration.
3. Recreate **approved schema/config**, not a copy of seller's production customer records. Have qualified reviewers verify policies and least-privilege; do not deploy unreviewed RLS/auth changes.
4. On synthetic test accounts A and B, verify that A's save/reopen works, B cannot read/update/delete A's CV via UI or API, and logout/account change clears improperly retained drafts. Inspect browser storage; account-scoped key names/sessionStorage alone are not confidentiality controls.
5. Verify auth email/recovery and invitation flows, including correct redirect URLs and handling of key rotation. Record any Free-plan leaked-password warning as an accepted risk or approved fix.
6. Back up and restore **synthetic** data, prove controlled rollback, record ownership and billing access. Any real personal data transfer needs separate legal/privacy authorization.

## 5. Acceptance cases (record PASS / FAIL / BLOCKED / NOT RUN)
| Case | Evidence to capture |
| --- | --- |
| Clean build and static publish on buyer path | commit, command, job URL, URL, build output |
| Login/logout + email flow | test user IDs only (no passwords/tokens) |
| New CV + save/reopen after reload | synthetic record, browser version |
| A to B account isolation, UI/storage/API | sanitized audit notes |
| Arabic RTL + English controls | browser screenshots with dummy content |
| 33 templates + name/date formatting | template IDs, observed exceptions |
| Profile/title/responsibility refresh and edit | representative synthetic job titles |
| PDF export on actual physical Android | device/Android/browser, template, output opened/copied, issues |
| PDF on desktop and responsive 360/390px | paper layout, text order and copy/paste |
| Subscription/payment gates | existing service is free; do NOT assert an operating payment business |
| Failed build/rollback | separate preview, restore confirmation |
| Licenses/assets | asset-rights inventory and remedies |

Buyer and seller should sign the final accepted revision, environment, open exceptions, ownership transfer steps and time-limited support window. Open #24 cannot be represented as PASS just because prior CI was green.

## 6. Protected closing sequence
1. Execute signed asset/IP purchase agreement with explicit seller authority, representations, warranties, exclusions, accepted defects, support scope and governing law.
2. Establish independent escrow or comparable mutually trusted payment protection; no transfer before contractual payment milestones.
3. Deliver project code and permitted owned assets to buyer-controlled destination; deploy isolated Supabase/frontend and rotate buyer-owned secrets.
4. Conduct synthetic acceptance; only migrate legitimate data where lawful and agreed. Never send real CVs in email/marketplace chat.
5. Complete buyer acceptance, release escrow under agreed milestones, revoke temporary access, store signed receipts/records.

**Never** test transfer by moving the seller's personal GitHub account, publishing a preview directly over production, exposing admin secrets, or copying live user data.
