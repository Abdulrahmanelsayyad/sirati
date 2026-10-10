"""Add a bilingual, accessible signed-in logout control to the existing site drawer.

This patches only generated UI/CSS; no Supabase schema, auth configuration,
saved CVs or payment handling are changed.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
menu_path = root / "components/SiratiSiteMenu.tsx"
style_path = root / "app/globals.css"
menu = menu_path.read_text(encoding="utf-8")

def replace_once(before, after, label):
    global menu
    count = menu.count(before)
    if count != 1:
        raise RuntimeError(f"Menu sign-out {label}: expected 1 anchor, got {count}")
    menu = menu.replace(before, after, 1)

replace_once(
    "  const [loading, setLoading] = useState(true);\n  const opener = useRef<HTMLButtonElement>(null);",
    """  const [loading, setLoading] = useState(true);
  const [signingOut, setSigningOut] = useState(false);
  const [signOutError, setSignOutError] = useState('');
  const opener = useRef<HTMLButtonElement>(null);""",
    "state",
)
replace_once(
    "  const close = () => { setOpen(false); setSearch(''); };",
    """  const close = () => { setOpen(false); setSearch(''); };
  async function handleSignOut() {
    if (!user || signingOut) return;
    const supabase = createClient();
    if (!supabase) {
      setSignOutError('تعذّر تسجيل الخروج الآن · Sign out unavailable.');
      return;
    }
    // A local draft may be the only copy of unsaved edits on this device.
    // Warn before discarding it, and never remove other accounts' drafts.
    const draftKey = `sirati.cv.v2.${user.id}`;
    let hasDeviceDraft = false;
    try {
      hasDeviceDraft = Boolean(window.localStorage.getItem(draftKey));
    } catch {
      // Blocked storage should not prevent signing out.
    }
    if (hasDeviceDraft && !window.confirm(
      'Your CV may have unsaved changes on this device. Save to My Documents before signing out. ' +
      'Continuing will remove this device draft, but not cloud-saved CVs. Continue? ' +
      'قد توجد تغييرات غير محفوظة. احفظ السيرة في مستنداتي أولاً. المتابعة تحذف مسودة الجهاز فقط.'
    )) return;
    setSigningOut(true);
    setSignOutError('');
    try {
      // End this browser's session, without deleting account CV documents.
      const { error } = await supabase.auth.signOut({ scope: 'local' });
      if (error) throw error;
      // Clean this account's plaintext device draft only after successful logout.
      try { window.localStorage.removeItem(draftKey); }
      catch { /* Storage may be disabled; cloud-saved documents remain untouched. */ }
      setUser(null);
      close();
      window.location.assign(withBasePath('/'));
    } catch {
      setSignOutError('فشل تسجيل الخروج. حاول مرة أخرى · Sign out failed. Please try again.');
    } finally {
      setSigningOut(false);
    }
  }""",
    "handler",
)
replace_once(
    """                <a href={withBasePath('/profile')} onClick={close}>الملف الشخصي وبياناتي ←</a>
              </div>""",
    """                <a href={withBasePath('/profile')} onClick={close}>الملف الشخصي وبياناتي ←</a>
                <button type="button" className="sirati-menu-signout"
                  disabled={signingOut} onClick={handleSignOut}>
                  {signingOut ? 'جارٍ تسجيل الخروج… · Signing out…' : 'تسجيل الخروج · Log out'}
                </button>
                {signOutError && <small className="sirati-menu-signout-error" role="alert">{signOutError}</small>}
              </div>""",
    "signed-in account control",
)

menu_path.write_text(menu, encoding="utf-8")
css = style_path.read_text(encoding="utf-8")
marker = "/* Sirati menu: signed-in logout */"
if marker in css:
    raise RuntimeError("Menu sign-out CSS already installed")
css += r"""
/* Sirati menu: signed-in logout */
@media screen {
  .sirati-menu-signout {
    align-self: flex-start;
    min-height: 44px;
    max-width: 100%;
    padding: 9px 13px;
    margin-top: 5px;
    border: 1px solid #bdcdc1;
    border-radius: 10px;
    background: #fffefa;
    color: #70402b;
    font: inherit;
    font-size: 13px;
    font-weight: 750;
    cursor: pointer;
    text-align: start;
  }
  .sirati-menu-signout:hover { background: #f8eee7; border-color: #d6aa8a; }
  .sirati-menu-signout:focus-visible { outline: 3px solid #d2b16e; outline-offset: 2px; }
  .sirati-menu-signout:disabled { cursor: wait; opacity: .65; }
  .sirati-menu-signout-error { color: #9b2f28 !important; font-size: 12px; }
}
"""
style_path.write_text(css, encoding="utf-8")
print("PASS: signed-in drawer has accessible local logout with error handling.")


# PR #81 parity: apply the same tested scoped draft safeguard to the two
# existing AccountNav / My Documents logout routes.  Putting it here ensures
# it executes *after* the latest global menu generator, avoiding the stale
# prepare_pages.py insertion conflict. No other generator changes.
import re
signout_call = re.compile(
    r"(?P<indent>^[ \t]*)await (?P<client>[A-Za-z_$][\w$]*(?:\(\))?)(?:\?)?\.auth\.signOut\(\);",
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
        f"const draftAuthClient = {client};",
        "if (!draftAuthClient) return;",
        "const { data: { session: draftSession } } = await draftAuthClient.auth.getSession();",
        "const draftScopedKey = draftSession?.user?.id",
        "  ? 'sirati.cv.v2.' + draftSession.user.id : null;",
        "let hasDeviceDraft = false;",
        "try {",
        "  hasDeviceDraft = Boolean(draftScopedKey && window.localStorage.getItem(draftScopedKey));",
        "} catch { /* Storage may be disabled; do not block sign-out. */ }",
        "if (hasDeviceDraft && !window.confirm(",
        "  'A device-only CV draft may contain unsaved changes. Save your CV to My Documents before signing out. Continuing will clear this device draft, but will NOT delete cloud-saved CVs. Continue?'",
        ")) return;",
        "const { error: draftSignOutError } = await draftAuthClient.auth.signOut();",
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
