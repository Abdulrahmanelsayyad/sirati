# Sirati Autonomous Maintainer Policy

This repository is maintained by an autonomous ChatGPT-based maintainer for the Sirati CV product.

## Allowed autonomous changes
- UI/UX polish and consistency
- Mobile responsiveness
- Accessibility fixes
- Performance improvements that do not change product behavior
- SEO/meta copy improvements
- Arabic RTL and English presentation fixes
- CV template visual refinements
- Minor copy improvements
- Non-breaking bug fixes in presentation code

## Protected areas — do not modify autonomously
- Supabase schema, migrations, RLS policies, authentication configuration, or auth redirects
- Payment/PDF order rules, pricing, or approval logic
- Environment variables, API keys, secrets, tokens, or credentials
- GitHub Actions permissions, repository visibility, or security settings
- Major dependency upgrades
- Business model, legal terms, privacy policy, or customer promises
- Destructive data operations

## Change limits
- Prefer small, reversible changes.
- Maximum 3 logical files or about 200 changed lines per maintenance run.
- Preserve the core journey: Login -> Template -> CV Builder -> Save -> Preview -> PDF Order.
- Preserve Arabic/English support and RTL.
- Never add third-party trackers or external scripts without explicit owner approval.

## Verification
Before deploying:
1. Reconstruct the Sirati source.
2. Run the production build.
3. Reject the change if the build fails.
4. Never expose secrets in source, logs, or generated assets.
5. If GitHub Pages deployment fails, revert the autonomous change.

## Reporting
Do not ask the owner for approval for allowed changes.
After a successful deployment, send only a concise summary of what changed and why.
If no safe improvement is available, make no change.


## Zero-cost constraint
- Autonomous work must use zero-cost implementation paths.
- Do not activate, purchase, subscribe to, or depend on paid APIs, paid AI inference, paid SaaS, paid templates/assets, paid hosting upgrades, premium plugins, or credit-consuming services without explicit owner approval.
- Do not require the owner to add billing details as part of autonomous work.
- Prefer existing infrastructure, free/open-source libraries with suitable licenses, native browser/platform features, and currently available free tiers.
- If the best-known approach requires payment, document the idea as an optional future upgrade and implement the strongest safe zero-cost alternative now.
- Zero-cost does not override security, privacy, licensing, protected settings, or quality gates.
