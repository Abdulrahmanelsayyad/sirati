# Sirati Agent Board

## Priority
Keep Sirati reliable, secure, polished, easy to use, and focused on the core customer journey:
Login -> Template -> CV Builder -> Save -> Preview -> PDF Order.

## Now
- No active autonomous task.

## Backlog
- Continuously improve agent playbooks from verified outcomes and record reusable lessons.
- Improve customer-facing polish when clear, low-risk opportunities are found.
- Continuously watch for reproducible UI or deployment defects.
- Review security posture without exposing or modifying secrets.

## Blocked
- In-page AI CV assistance requires an approved AI backend/API or equivalent runtime integration.

## Completed
- Multi-agent operating model defined.


## Product improvement backlog — Manager assigned

### P0 — Customer journey / Builder
- Transform the CV Builder into short, simple guided steps instead of a long dense form.
- Improve the live preview so users can understand the result while editing.
- Reduce visible field clutter and show only the information needed for the current step.
- Run a full mobile usability pass focused on navigation, touch targets, scrolling, and form completion.

### P0 — PDF order / payment clarity
- Simplify the manual PDF order flow for InstaPay and Vodafone Cash.
- Make payment instructions, pending status, proof/reference submission, and next steps obvious.
- Do not change pricing, approval logic, payment rules, or add automated collection without owner approval.

### P1 — Trust and conversion
- Improve first-30-seconds clarity: explain what Sirati does, who it is for, and why it is useful.
- Strengthen trust pages/sections: Contact, Privacy, Terms, payment/delivery expectations, and support clarity.
- Improve CTA hierarchy so the primary action is obvious and secondary actions do not compete.

### P1 — Templates
- Focus on 2–3 excellent templates rather than increasing template count.
- Improve ATS readability, spacing, print fidelity, Arabic/English consistency, and professional visual quality.

### P1 — End-to-end QA
- Test the full journey: landing -> sign in -> choose template -> build CV -> save -> return/edit -> preview -> PDF order.
- Check desktop and mobile.
- Record reproducible defects for Bug Fixer and verify fixes before closing.

### Delegation guidance
- Design Agent: homepage clarity, CTA hierarchy, builder UX, mobile polish, template presentation.
- Bug Fixer: reproducible navigation, form, save/restore, rendering, preview, and deployment defects.
- CV Expert: section guidance, ATS wording quality, template content structure, factual CV assistance.
- Customer Liaison: support wording, customer-facing instructions, FAQs, payment/order communication clarity.
- Security Agent: review changes for exposure/privacy/security regressions without modifying protected settings.
- Deputy Manager: maintain ownership, sequencing, handoffs, and blocker visibility.
- Manager: prioritize, assign one owner per task, verify outcome, and report only meaningful progress/blockers.

### Completion rule
No task is complete until the relevant user flow is verified on the live site and the change is recorded in AGENT_CHANGELOG.md.
