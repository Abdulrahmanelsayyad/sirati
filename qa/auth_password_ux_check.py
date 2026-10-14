"""Assert the V33 password flows exist without changing the identity/data boundary."""
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve()
recovery=(root/"app/auth/recovery/page.tsx").read_text(encoding="utf-8")
password=(root/"app/account/password/page.tsx").read_text(encoding="utf-8")
dialog=(root/"components/SiratiBuilderPdfButton.tsx").read_text(encoding="utf-8")
menu=(root/"components/SiratiSiteMenu.tsx").read_text(encoding="utf-8")
for marker in (
    "resetPasswordForEmail",
    "PASSWORD_RECOVERY",
    "getUser()",
    "updateUser({password:newPassword})",
    "withBasePath('/auth/recovery?flow=password')",
    "verified.user.email?.toLowerCase()!==verifiedEmail.toLowerCase()",
):
    assert marker in recovery, f"Recovery guard absent: {marker}"
for marker in (
    "auth.getUser()",
    "updateUser({password})",
    "data.user.email?.toLowerCase()!==email.toLowerCase()",
    "withBasePath('/auth/recovery')",
):
    assert marker in password, f"Account guard absent: {marker}"
assert "withBasePath('/auth/recovery')" in dialog
assert "withBasePath('/account/password')" in menu
for source in (recovery,password):
    assert "service_role" not in source
    assert "localStorage" not in source
    assert "sessionStorage" not in source
    assert "PASSWORD_RECOVERY" not in password
print("PASS: recovery, password change, URLs, account verification and isolated client scope")
