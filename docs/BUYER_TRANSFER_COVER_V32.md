# Sirati CV — V32 buyer transfer cover sheet
**As of:** 2026-10-14  
**Source candidate:** [PR #149](https://github.com/Abdulrahmanelsayyad/sirati/pull/149) (Ready for independent review, not merged)  
**Product main at last reconciliation:** `cfaf128f9f5ed4678efbe60dc9741eff57ca81a7`  
**Tested V32 code head:** `7448f4df2f4a4450f7f82e3013c71b55d3e17dd6`  
**Status:** TECHNICAL DUE-DILIGENCE PACKET PREPARED; PR READY FOR REVIEW — **NOT** unconditional sale, independent security acceptance, buyer deployment, or seller production release.

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
1. [#130 PDF](https://github.com/Abdulrahmanelsayyad/sirati/issues/130): **CLOSED — not planned for V32**, not claimed fixed. Joined Arabic/Latin tokens such as `الـICU/ER` remain outside the supported searchable-export contract; the preflight and V32 bilingual recovery preserve original input. Physical Android supported-input acceptance remains NOT RUN and is a release condition under #24.
2. [#99 staging analytics](https://github.com/Abdulrahmanelsayyad/sirati/issues/99): **CLOSED — verified.** On Sirati-Staging only, `EXECUTE` was revoked from `PUBLIC`, `anon`, and `authenticated` for the two optional analytics functions. Catalog confirms both functions remain; refreshed Security Advisor has no SECURITY DEFINER executable RPC warnings. No Production grants, Auth settings, functions or data changed. The remaining Staging advisory is Auth leaked-password protection, tracked in #24.
3. [#24 security/release](https://github.com/Abdulrahmanelsayyad/sirati/issues/24): A/B synthetic Staging checks passed. Independent human reviewer, buyer-owned backend provisioning/restore, actual phone/offline/expiry coverage and legal sign-off are **not completed**. Supabase Production warns leaked-password protection is disabled under the current Free-plan configuration; there is no evidence of a breach, but no complete security clearance.

Decisions on #99 and #130 are final for V32; only #24 is still an open security/release acceptance gate. No paid Supabase upgrade is planned under the zero-cost build policy. The Free-plan leaked-password warning is recorded and must be presented to an independent reviewer and buyer; this record is not an owner-signed security risk acceptance. Do not claim all security checks passed or that a real Android/independent buyer acceptance occurred.

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

**Subsequent tracked Staging-only action:** The optional Analytics function grants were revoked as described above, with no data/function deletion. No live customer data export, Production backend permission/Auth setting change, paid-plan change, production merge/deploy, or asset transfer was performed. Any production deploy, paid upgrade or buyer transfer needs separate specifically scoped authorization.
