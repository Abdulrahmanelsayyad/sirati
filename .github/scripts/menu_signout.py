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
    setSigningOut(true);
    setSignOutError('');
    try {
      // End this browser's session, without deleting account CV documents.
      const { error } = await supabase.auth.signOut({ scope: 'local' });
      if (error) throw error;
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
