"""Safely remove only the active account's device CV draft on explicit logout.

Generated-source patch only: no changes to Supabase Auth/RLS/database.
Never erase a draft before confirmation and successful sign-out.
"""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
signout_call = re.compile(
    r"(?P<indent>^[ \t]*)await (?P<client>[A-Za-z_$][\w$]*)(?:\?)?\.auth\.signOut\(\);",
    re.MULTILINE,
)

for relative in ("components/AccountNav.tsx", "app/documents/page.tsx"):
    path = root / relative
    source = path.read_text(encoding="utf-8")
    matches = list(signout_call.finditer(source))
    if len(matches) != 1:
        # Diagnostics expose only static source-code call shapes, never CV data.
        calls = [line.strip()[:180] for line in source.splitlines() if "signOut" in line]
        raise RuntimeError(
            f"{relative}: expected exactly one awaited signOut() call, found {len(matches)}; candidates={calls[:5]!r}"
        )
    match = matches[0]
    indent, client = match.group("indent", "client")
    lines = [
        "// SIRATI_PRIVACY_SIGNOUT_START",
        f"if (!{client}) return;",
        f"const {{ data: {{ session: draftSession }} }} = await {client}.auth.getSession();",
        "const draftScopedKey = draftSession?.user?.id",
        "  ? 'sirati.cv.v2.' + draftSession.user.id : null;",
        "let hasDeviceDraft = false;",
        "try {",
        "  hasDeviceDraft = Boolean(draftScopedKey && window.localStorage.getItem(draftScopedKey));",
        "} catch { /* Storage may be disabled; do not block sign-out. */ }",
        "if (hasDeviceDraft && !window.confirm(",
        "  'A device-only CV draft may contain unsaved changes. Save your CV to My Documents before signing out. Continuing will clear this device draft, but will NOT delete cloud-saved CVs. Continue?'",
        ")) return;",
        f"const {{ error: draftSignOutError }} = await {client}.auth.signOut();",
        "if (draftSignOutError) {",
        "  window.alert('Sign-out failed; your CV device draft has been kept. Please retry.');",
        "  return;",
        "}",
        "if (draftScopedKey) {",
        "  try { window.localStorage.removeItem(draftScopedKey); }",
        "  catch { /* Storage disabled; no additional data is deleted. */ }",
        "}",
        "// SIRATI_PRIVACY_SIGNOUT_END",
    ]
    replacement = ("\n" + indent).join(lines)
    path.write_text(
        source[:match.start()] + indent + replacement + source[match.end():],
        encoding="utf-8",
    )
    print(f"PASS: guarded active-account draft cleanup installed in {relative}")
