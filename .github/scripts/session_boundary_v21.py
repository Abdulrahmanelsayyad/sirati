"""Owner-approved client session boundary. No cloud deletes or Auth/RLS changes."""
from pathlib import Path
import sys

root = Path(sys.argv[1])

def replace(path, before, after, count=1):
    file = root / path
    text = file.read_text()
    assert text.count(before) == count, f"Session boundary anchor changed: {path}: {before[:60]}"
    file.write_text(text.replace(before, after))

(root / 'lib/sessionBoundary.ts').write_text('''// The owner marker contains an ID only, never CV contents or credentials.
const OWNER_KEY = 'sirati.session.owner.v1';
let owner: string | null | undefined;
let blocked = false;
export function isSessionBoundaryBlocked() { return blocked; }
export function observeSessionOwner(next: string | null) {
  if (blocked) return true;
  if (owner === undefined) {
    try { owner = window.sessionStorage.getItem(OWNER_KEY); }
    catch { owner = null; }
  }
  if (owner && owner !== next) {
    // Synchronous latch stops queued writes before React unmounts the editor.
    blocked = true;
    const key = 'sirati.cv.v2.' + owner;
    try { window.sessionStorage.removeItem(key); } catch {}
    try { window.localStorage.removeItem(key); } catch {}
    try { window.sessionStorage.removeItem('sirati.guest.pdf.pending.v1'); } catch {}
    try { window.sessionStorage.removeItem(OWNER_KEY); } catch {}
    return true;
  }
  owner = next;
  try {
    if (next) window.sessionStorage.setItem(OWNER_KEY, next);
    else window.sessionStorage.removeItem(OWNER_KEY);
  } catch {}
  return false;
}
''')

(root / 'components/SessionBoundary.tsx').write_text(''''use client';
import { useEffect, useState, type ReactNode } from 'react';
import { createClient } from '@/lib/supabase/client';
import { withBasePath } from '@/lib/basePath';
import { isSessionBoundaryBlocked, observeSessionOwner } from '@/lib/sessionBoundary';

export default function SessionBoundary({children}: {children: ReactNode}) {
  const [blocked, setBlocked] = useState(isSessionBoundaryBlocked);
  useEffect(() => {
    const client = createClient();
    if (!client) return;
    // Never await another Supabase call inside its auth event callback.
    const {data: {subscription}} = client.auth.onAuthStateChange((_event, session) => {
      if (observeSessionOwner(session?.user.id ?? null)) setBlocked(true);
    });
    return () => subscription.unsubscribe();
  }, []);
  if (blocked) return <main className="container" role="status">
    <h1>Session changed · تغيّرت جلسة الحساب</h1>
    <p>The previous account’s editor has been cleared. Cloud-saved CVs are unchanged.</p>
    <p dir="rtl">تم إغلاق محرر الحساب السابق. السير المحفوظة في حسابك لم تُحذف.</p>
    <a className="btn btn-primary" href={withBasePath('/builder')}>
      Continue safely · متابعة آمنة
    </a>
  </main>;
  return children;
}
''')
replace('app/layout.tsx', "import SiratiAnalyticsTracker", "import SessionBoundary from '@/components/SessionBoundary';\nimport SiratiAnalyticsTracker")
replace('app/layout.tsx', '<SiratiSiteMenu />{children}', '<SiratiSiteMenu /><SessionBoundary>{children}')
replace('app/layout.tsx', '      </body>', '      </SessionBoundary></body>')

path = 'app/builder/page.tsx'
replace(path, "import { useEffect,", "import { isSessionBoundaryBlocked } from '@/lib/sessionBoundary';\nimport { useEffect,")
replace(path, '    if (!hydrated) return;', '    if (!hydrated || isSessionBoundaryBlocked()) return;')
replace(path, '    if (!hydrated || !guestRestoreReady || userId) return;',
        '    if (!hydrated || !guestRestoreReady || userId || isSessionBoundaryBlocked()) return;')
replace(path, '      const user = userData.user;',
        '      if (isSessionBoundaryBlocked()) return;\n      const user = userData.user;')
replace(path, '      if (!error && row) {', '      if (isSessionBoundaryBlocked()) return;\n      if (!error && row) {')
replace(path, '    const timer = window.setTimeout(async () => {',
        '    const timer = window.setTimeout(async () => {\n      if (isSessionBoundaryBlocked()) return;')
replace(path, '    setVersions((rows ?? []) as CloudCvVersion[]);',
        '    if (isSessionBoundaryBlocked()) return;\n    setVersions((rows ?? []) as CloudCvVersion[]);')
replace(path, '  async function saveToAccount(createVersion = true) {',
        '  async function saveToAccount(createVersion = true) {\n    if (isSessionBoundaryBlocked()) return null;')
replace(path, '      activeUserId = userData.user?.id ?? null;',
        '      if (isSessionBoundaryBlocked()) return null;\n      activeUserId = userData.user?.id ?? null;')
replace(path, '      if (error || !created) {',
        '      if (isSessionBoundaryBlocked()) return null;\n      if (error || !created) {')
replace(path, '    if (createVersion && id) {',
        '    if (isSessionBoundaryBlocked()) return null;\n    if (createVersion && id) {')

# An export begun under A must not deliver its in-memory CV after account loss.
replace('lib/siratiPdfExport.ts', "import html2canvas", "import { isSessionBoundaryBlocked } from '@/lib/sessionBoundary';\nimport html2canvas")
replace('lib/siratiPdfExport.ts', '  downloadBlob(blob, name);',
        "  if (isSessionBoundaryBlocked()) throw new Error('Session changed. Reopen your CV before downloading.');\n  downloadBlob(blob, name);")
print('PASS: session boundary clears only prior local draft; blocks stale saves/export; cloud data untouched')
