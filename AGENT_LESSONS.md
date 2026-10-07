# Sirati Agent Lessons

Verified, reusable lessons from real Sirati work go here.

## Format
### YYYY-MM-DD — Short lesson title
- **Context:** what happened.
- **What worked:** verified successful approach.
- **What failed:** if relevant.
- **Reusable rule:** what future agents should do.
- **Evidence:** commit / workflow / observable result.

## Current lessons

### 2026-10-07 — Repository visibility can disable GitHub Pages
- **Context:** Changing the Sirati repository from Public to Private caused GitHub Pages configuration to disappear for the current account/repository state.
- **What worked:** Return the repository to Public, re-enable Pages with GitHub Actions, and rerun the deployment.
- **What failed:** Re-running deployment before Pages was re-enabled.
- **Reusable rule:** After repository visibility changes, verify Pages configuration before diagnosing application code.
- **Evidence:** production build succeeded while Configure Pages failed; deployment succeeded after Pages was re-enabled.
