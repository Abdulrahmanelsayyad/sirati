# Sirati CV — V32 buyer transfer cover sheet
**As of:** 2026-10-14  
**Source candidate:** [PR #149](https://github.com/Abdulrahmanelsayyad/sirati/pull/149) (Draft, not merged)  
**Product main at last reconciliation:** `cfaf128f9f5ed4678efbe60dc9741eff57ca81a7`  
**Tested V32 code head:** `7448f4df2f4a4450f7f82e3013c71b55d3e17dd6`  
**Status:** TECHNICAL DUE-DILIGENCE PACKET PREPARED — **NOT** unconditional sale, independent security acceptance, buyer deployment, or seller production release.

## Buyer receives — subject to a signed asset agreement
- Repository source at the **specified accepted revision**, including nine encoded source parts, build scripts, generated app, templates, rule-based CV suggestions, PDFs, and QA workflows.
- Written reconstruction procedure and known limitations in [BUYER_TECHNICAL_HANDOVER.md](BUYER_TECHNICAL_HANDOVER.md), with [BUYER_ACCEPTANCE_MATRIX.md](BUYER_ACCEPTANCE_MATRIX.md) as the evidence/acceptance log.
- Current product proposition: a **free** Arabic/English CV builder with editable CV content, print/browser PDF workflow, and Supabase-connected accounts/documents where configured. Do **not** market guaranteed ATS compatibility, an AI LLM integration, earnings, or subscription revenue.

**Excluded unless separately agreed and legally transferable:** seller's GitHub/hosting/Supabase/email accounts and credentials, the GitHub Pages personal namespace URL, real users/CVs/Auth data, analytics, private secrets, payment records, and third-party rights not owned by seller. No production customer data should be used in demos.

## Verified CI for tested code head (not a promise of production coverage)
| Test / evidence | Result |
| --- | --- |
| [End-to-end](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38531991515) | PASS |
| [Staging build + feedback browser](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38531991400) | PASS |
| [Staging synthetic A/B accounts and save recovery](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38531991475) | PASS; not buyer-owned backend |
| [Buyer path portability: root, /buyer-cv, /builder-tools](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38531991372) | PASS |
| [GitHub Pages build](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38531991341) | PASS; deploy **SKIPPED** |
| [Detailed PDF run](https://github.com/Abdulrahmanelsayyad/sirati/actions/runs/38531991394) | PDF rendering job PASS; whole workflow FAIL due to unchanged historical PDF-only release-scope guard |

**Do not interpret PASS as live-production or independent legal/security acceptance.** The main application remains on the older revision until an owner-approved merge and separate manual deploy.

## Current disposition: three tracked items, no repetition of completed fixes
1. [#130 PDF](https://github.com/Abdulrahmanelsayyad/sirati/issues/130): existing supported PDF reader matrix passed. Joined Arabic/Latin tokens such as `الـICU/ER` are **not safely supported**, and physical Android acceptance is not recorded. This is a disclosed product constraint, not a completed universal PDF fix; preflight preserves entered text and explains a user-controlled space-separated workaround.
2. [#99 staging analytics](https://github.com/Abdulrahmanelsayyad/sirati/issues/99): production analytics is disabled. Staging-only RPC privilege warnings remain; the least-privilege revoke was **proposed, not executed**, pending explicit owner approval. Do not claim the grants were revoked.
3. [#24 security/release](https://github.com/Abdulrahmanelsayyad/sirati/issues/24): A/B synthetic Staging checks passed. Independent human reviewer, buyer-owned backend provisioning/restore, actual phone/offline/expiry coverage and legal sign-off are **not completed**. Supabase Production warns leaked-password protection is disabled under the current Free-plan configuration; there is no evidence of a breach, but no complete security clearance.

These are **outstanding conditions or accepted-to-be-disclosed limits**, not reasons to reopen closed historical implementation work. Record separate, explicit owner risk acceptance if constraints are shipped as-is. Do not close security tickets as “fixed” merely to empty an issue board.

## Operator reproduction (clean, buyer-controlled environment)
- Clone a frozen, explicitly transferred revision. Use Node.js 22, Python 3, Bash, `unzip`, and `base64`; inspect [build.sh](../build.sh) and the archived source reconstruction before trusting it.
- Guest-only isolated build: `NEXT_PUBLIC_BASE_PATH=/buyer-cv NEXT_PUBLIC_ANALYTICS_ENABLED=false bash build.sh`; static files output to `site-src/sirati-cv-source/out`. For a buyer-root domain use empty base path instead.
- Run the repository's current QA and independent smoke tests; compare **exact revision** and logs to this packet. Record hash, hosting paths, browser/device, results, and rollback artifact.
- Buyer configures separate authorized hosting, origin-specific Auth URLs, email and **buyer-owned** Supabase, then executes a fresh synthetic-account A/B access and document restore drill. Do not copy seller credentials or user data.
- Review third-party licenses/fonts, chain of title and IP assignment. Reconstructed/encoded source adds maintenance cost. Selling the software does not automatically transfer service accounts.

## Formal handover sign-off — intentionally UNEXECUTED
| Acceptance item | As of 2026-10-14 |
| --- | --- |
| Source, features, known limitations, CI evidence documented | PREPARED |
| Tested candidate merged onto seller main | NOT DONE |
| Seller production release at same candidate SHA | NOT DONE |
| Independent human security + exact-release QA reviewer approval | NOT DONE |
| Buyer-owned hosted deploy and Auth/database restore smoke | NOT DONE |
| Physical Android/supported-input PDF check | NOT DONE |
| Legal IP/asset schedule, payment, signatures, credential rotation | NOT DONE |

Seller sign-off (name/date): **NOT SIGNED**  
Buyer sign-off (name/date): **NOT SIGNED**

**Next irreversible actions require specifically scoped owner authorization.** Do not infer it from request to prepare buyer handover. No live customer data export, backend permissions, paid-plan change, production merge/deploy, or transfer was performed by producing this cover sheet.
