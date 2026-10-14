"""V34 QA: assert authenticated changes and guest-first registration boundaries."""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
def read(name):return (root/name).read_text(encoding="utf-8")
auth=read("app/auth/page.tsx")
dialog=read("components/SiratiBuilderPdfButton.tsx")
password=read("app/account/password/page.tsx")
recovery=read("app/auth/recovery/page.tsx")
confirm=read("app/auth/confirm/page.tsx")
css=read("app/globals.css")
for token in [
    "type Mode='signin'|'signup'",
    "safeNext(raw:string|null)",
    "mode==='signup' && password!==confirm",
    "autoComplete=\"new-password\"",
    "mode==='signin'?'current-password':'new-password'",
    "client.auth.resend(",
    "client.auth.signUp(",
    "client.auth.signInWithPassword(",
    "client.auth.getUser()",
    "window.location.assign(returnTarget)",
    "withBasePath('/auth/recovery')",
    "sirati-auth-v34-tabs",
    "sirati-auth-v34-strength",
]:
    assert token in auth, "Missing auth marker: "+token
assert "OnboardingSteps" not in auth, "Guest first must not imply account required before editing"
assert "sessionStorage" not in auth and "localStorage" not in auth, "No credentials persisted by sign-in form"
assert "password !== passwordConfirm" in dialog
assert "passwordConfirm" in dialog and "sirati-auth-v34-modal-password" in dialog
assert 'target="_blank" rel="noopener noreferrer"' in dialog, "Recovery should preserve original CV tab"
assert "storeTransfer" in dialog and "readTransfer()" in dialog, "Existing CV restoration must remain"
assert "auth.signInWithPassword({email,password:currentPassword})" in password
assert "after.user.id!==data.user.id" in password
assert "client.auth.updateUser({password})" in password
assert "setCurrentPassword('')" in password, "Must clear old secret after success"
assert "resetPasswordForEmail" in recovery and "verified.user.email?.toLowerCase()!==verifiedEmail.toLowerCase()" in recovery
assert "exchangeCodeForSession" in confirm and "verifyOtp" in confirm
assert "setMessage(error.message" not in confirm, "Do not expose raw confirmation provider errors"
assert "/* Sirati Auth V34 */" in css and "@media(max-width:400px)" in css
print("PASS: bilingual account UX, confirmation, current-password reauthentication, guest draft and mobile CSS guards")
