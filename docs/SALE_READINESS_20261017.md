# Sirati CV — Sale Readiness & Evidence (17 Oct 2026)

**Decision:** LISTABLE WITH DISCLOSURES; NOT approved for unconditional buyer handover. This is a factual seller-preparation record, not a security certification, valuation, or agreement to transfer user data.

## Product and business facts
- Live product: https://abdulrahmanelsayyad.github.io/sirati/
- Code: https://github.com/Abdulrahmanelsayyad/sirati (publicly readable, proprietary LICENSE).
- Arabic/English CV builder with RTL, 33 catalog templates, preview/browser PDF and career tools including editable, rule-based writing suggestions.
- Technology: Next.js / React / TypeScript static build, GitHub Pages, GitHub Actions, optional Supabase account/document backend.
- **No genuine registered users are reported by the seller.** This is a seller statement, not an independently audited database count. Automated test users do not count.
- Existing product is free; no paid subscriptions or recurring revenue are evidenced. Traffic, expenses and revenue statements have not been independently verified. Do not claim zero traffic or verified zero revenue merely from missing records.
- Suggestions use curated rules/facts: **do not advertise an LLM-powered AI service**. Do not promise ATS acceptance or employment outcomes.

## Verifiable technical evidence
| Test / event | Evidence | Status |
| --- | --- | --- |
| Exact production code | main SHA a063f214ab91f121bd51b7a084be92cdf958be58 (PR #179 merged 17 Oct 2026) | VERIFIED |
| GitHub Pages build + deploy | https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/39033220780 | PASS; both jobs |
| Latest merge PDF regression | https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/39033220731 | PASS |
| PR #179 browser E2E | https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/39032267360 | PASS on PR head |
| Independent human security sign-off for final release | https://github.com/Abdulrahmanelsayyad/sirati/issues/24 | OPEN / NOT VERIFIED |
| Physical Android CV export/open/text-copy/save/reopen | issue #24 | NOT RUN / NOT VERIFIED |
| Clean buyer-owned hosting + Supabase migration + A/B account acceptance | issue #24 | NOT RUN; buyer not selected |
| Live post-deploy manual full customer journey | needs owner evidence | NOT VERIFIED by this package |

A green build is not an independent audit. Historical staging A/B evidence applies to its recorded code revision, not automatically to all later commits.

## Mandatory material disclosures
1. **Build complexity:** current canonical source is a split encoded archive plus ordered Python patches; site-src is generated, not canonical. See README / build.sh. Buyer must reproduce a clean checkout.
2. **Privacy:** issue #25 was closed as consolidated into #24 after account draft storage was migrated to scoped sessionStorage and sign-out cleanup; browser sessionStorage is *not encryption*. Independently verify cross-account/privacy behavior in an isolated synthetic test setup.
3. **Authentication:** current Supabase Free-plan leaked-password-protection warning is documented in #24. Security review is outstanding.
4. **PDF:** contiguous mixed Arabic/Latin tokens are a documented unsupported edge case; space-separated phrases are the documented test scope. Actual physical Android acceptance is pending.
5. **Localization:** not every site/helper string is fully translated. Report bilingual support, not flawless full-site localization.
6. **IP:** third-party libraries/assets/fonts may carry separate licenses; seller must produce asset/license schedule. Public repository visibility does not confer reuse rights.
7. **No automatic account transfer:** seller's personal GitHub account, github.io URL, Supabase account, credentials, and any personal/customer data are excluded by default.
8. **No proven commercialization:** historical payment-related code/records are not current income.

## Suggested sale positioning
- Classification: pre-traction source-code/software-asset acquisition, NOT established SaaS.
- **Exploratory asking price: USD 2,900 negotiable**; not an independently appraised fair market value or a guaranteed close.
- Buyer audience: recruiting/HR software teams, career websites, agencies and developers seeking a bilingual CV builder.
- Show live demo, transparent limitations, CI evidence, original asset schedule, and buyer-controlled reproducible build path. Avoid investor-style forecasts unsupported by evidence.
- Never publish seller bank information, API/service-role keys, real CVs, contact PII, backup files or confidential contracts.

## Closing gates (must be evidenced before final handover)
- [ ] Owner approves exact source/IP asset schedule and third-party licenses.
- [ ] Owner records genuine user/traffic/revenue/expense evidence or clear explicit absence of evidence.
- [ ] Test live product on desktop and physical Android with synthetic Arabic + English inputs; record browser, template, device, output and observed issues.
- [ ] Independent security/QA reviewer signs off or buyer explicitly accepts written residual risks.
- [ ] Buyer reproduces isolated build on their own infrastructure using their own credentials.
- [ ] Buyer signs off on Supabase/Auth, backups (synthetic only), RLS, account A/B privacy, login/reopen and export tests.
- [ ] Parties sign written asset-purchase/IP assignment and transition/support terms; payment protected by mutually agreed escrow.
- [ ] Transfer only agreed rights after funds are secured, verify destination deployment and final acceptance. Do not transfer personal accounts or unrelated data.

**Related:** [Operational buyer handoff](BUYER_HANDOFF_RUNBOOK.md), [current open acceptance gate](https://github.com/Abdulrahmanelsayyad/sirati/issues/24), [proprietary license](../LICENSE).

## Seller-confirmed sale reason (17 October 2026)
The seller states that they do not currently have enough time to market and grow Sirati CV. This is a seller-provided explanation, not a representation that all product defects are resolved or that marketing/traction has already been achieved. Reflect this wording consistently in marketplace listings and buyer communications.
