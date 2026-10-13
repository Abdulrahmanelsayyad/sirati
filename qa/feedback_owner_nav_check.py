"""Fail-closed source check for the private feedback link in the generated site menu.

Build/typecheck and browser acceptance are independent; this check only
asserts the intended owner role gate and correct production base path.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
menu = (root / "components/SiratiSiteMenu.tsx").read_text(encoding="utf-8")
dashboard = (root / "app/feedback-dashboard/page.tsx").read_text(encoding="utf-8")

guard = "user?.app_metadata?.sirati_feedback_admin === true && ("
href = "href={withBasePath('/feedback-dashboard/')}"
assert menu.count(guard) == 1, "Missing or repeated owner role visibility guard"
assert menu.count(href) == 1, "Missing or repeated base-path-safe dashboard link"
assert menu.count('className="sirati-menu-item sirati-feedback-owner-link"') == 1
assert menu.index(guard) < menu.index(href) < menu.index('<NavGroup title="السيرة الذاتية"'), (
    "Feedback link must live within the owner-only menu section"
)
assert "getUser()" in menu, "Account identity must be verified"
assert "user?.email ===" not in menu, "An email-only check is not an owner permission"
assert "app_metadata?.sirati_feedback_admin !== true" in dashboard, (
    "Dashboard must independently verify the trusted owner role"
)
assert "from('sirati_site_feedback')" in dashboard, "Dashboard should read existing feedback"
print("PASS: feedback menu guarded by trusted owner claim, with base path; dashboard remains guarded")
