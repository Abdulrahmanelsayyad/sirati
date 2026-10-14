"""V35 acceptance: email verification and password reset may NOT auto-enter Sirati.

Generated sources are inspected after all patch scripts have run. This test
fails if session teardown or manual sign-in semantics regress. No live users.
"""
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve()
def source(name): return (root/name).read_text(encoding="utf-8")
callback=source("app/auth/confirm/page.tsx")
auth=source("app/auth/page.tsx")
reset=source("app/auth/recovery/page.tsx")
css=source("app/globals.css")

# Confirm link MUST verify email, end only the callback's device session,
# then land on sign-in without redirecting to templates, dashboard or editor.
for token in (
    "exchangeCodeForSession(code)",
    "verifyOtp({token_hash:tokenHash,type})",
    "hash.get('type')==='signup'",
    "client.auth.getSession()",
    "client.auth.getUser()",
    "data.user?.email_confirmed_at",
    "client.auth.signOut({scope:'local'})",
    "window.location.replace(withBasePath('/auth?confirmed=1&next='+encodeURIComponent(next)))",
    "window.history.replaceState(null,'',withBasePath('/auth/confirm'))",
    "if (!code && !(tokenHash && type) && !implicitSignup)",
    "setRetry(true);",
):
    assert token in callback, f"Confirmation safety step missing: {token}"
assert "window.location.href = next" not in callback
assert "window.location.href = withBasePath(next)" not in callback
assert "localStorage.clear(" not in callback
assert "localStorage.removeItem(" not in callback
assert "auth.signOut()" not in callback, "Explicit local scope required"

# Both confirmation and reset acknowledge the result, yet require manual
# re-entry of email + password. Existing sign-in is never auto-invoked.
for token in (
    "params.get('confirmed')==='1'",
    "params.get('password_changed')==='1'",
    "setPostVerification(outcome)",
    "if (outcome) {",
    "setMode('signin')",
    "postVerification&&",
    "تم تأكيد بريدك الإلكتروني بنجاح",
    "البريد الإلكتروني وكلمة المرور الجديدة",
    "client.auth.signInWithPassword({email:normalized,password})",
):
    assert token in auth, f"Manual login step missing: {token}"
outcome_block=auth.split("if (outcome) {",1)[1].split("const client=createClient();",1)[0]
assert "return;" in outcome_block, "Must suppress auth.getUser auto-redirect"
assert "window.location.assign(returnTarget)" in auth, "Manual sign-in must still work"

# Recovery callback is not the account's new login; it must log out and
# direct to sign-in AFTER successful updateUser and cleanup, never before.
for token in (
    "client.auth.updateUser({password:newPassword})",
    "client.auth.signOut({scope:'local'})",
    "setStage('signout_pending')",
    "window.location.replace(withBasePath('/auth?password_changed=1'))",
    "recoveryAuthorized.current=false",
    "role=\"status\"",
):
    assert token in reset, f"Recovery login boundary missing: {token}"
assert reset.index("updateUser({password:newPassword})") < reset.index("signOut({scope:'local'})")
assert "localStorage.clear(" not in reset and "localStorage.removeItem(" not in reset

assert ".sirati-auth-v35-confirmed" in css
print("PASS: confirm + password reset require new email/password sign-in; scoped signout only; CV storage untouched")
