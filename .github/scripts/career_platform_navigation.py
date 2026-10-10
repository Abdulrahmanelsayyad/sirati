"""Career-wide Sirati homepage, accessible feature drawer and account profile.
All links point to existing features; account values are derived from the signed-in
Supabase user, never cross-account localStorage. No paid APIs or database migration.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()

def once(source, before, after, label):
    count = source.count(before)
    if count != 1:
        raise RuntimeError(f"{label}: expected 1 anchor, found {count}")
    return source.replace(before, after, 1)

home_path = root / "app/page.tsx"
home = home_path.read_text(encoding="utf-8")
home = once(home,
    """          <h1>
            A CV that looks
            <span>as professional as you are.</span>
          </h1>""",
    """          <h1>
            Your career.
            <span>Beautifully presented.</span>
          </h1>""",
    "homepage broad headline")
home = once(home,
    '<Link className="btn btn-primary nav-build" href="/auth?next=/templates">Build my CV</Link>',
    '<Link className="btn btn-primary nav-build" href="/career-tools/">Explore Studio</Link>',
    "homepage nav")
home = once(home,
    """            <Link className="btn btn-primary btn-lg" href="/auth?next=/templates">
              Build my CV <span aria-hidden="true">→</span>
            </Link>
            <a className="btn btn-quiet btn-lg" href="#templates">
              View CV templates
            </a>""",
    """            <Link className="btn btn-primary btn-lg" href="/career-tools/">
              Explore Career Studio <span aria-hidden="true">→</span>
            </Link>
            <Link className="btn btn-quiet btn-lg" href="/templates">
              Create my CV
            </Link>""",
    "career-wide homepage CTA")
home_path.write_text(home, encoding="utf-8")

layout = root / "app/layout.tsx"
text = layout.read_text(encoding="utf-8")
if 'import SiratiSiteMenu' in text:
    raise RuntimeError("Site menu was already mounted")
text = "import SiratiSiteMenu from '@/components/SiratiSiteMenu';\n" + text
text = once(text, '<body>{children}', '<body><SiratiSiteMenu />{children}', 'global navigation injection')
text = once(text,
    "title: 'Sirati CV | Professional CV Builder in Arabic & English'",
    "title: 'Sirati | Free Career Studio, CV Builder and Professional Tools'",
    "site metadata title")
text = once(text,
    "description: 'Build a clear, professional CV in Arabic or English with live preview, flexible sections, clean templates, account sync and version history.'",
    "description: 'Build CVs, write cover letters, improve LinkedIn profiles and prepare for interviews — all free in Arabic and English.'",
    "site metadata description")
layout.write_text(text, encoding="utf-8")

component = root / "components/SiratiSiteMenu.tsx"
component.parent.mkdir(parents=True, exist_ok=True)
if component.exists(): raise RuntimeError("Site menu already exists")
component.write_text(r"""'use client';

import { useEffect, useRef, useState } from 'react';
import { withBasePath } from '@/lib/basePath';
import { createClient, isSupabaseConfigured } from '@/lib/supabase/client';
import type { User } from '@supabase/supabase-js';

type Item = { title: string; detail: string; route: string; icon: string };
const cvFeatures: Item[] = [
  { title: 'إنشاء CV', detail: 'CV Builder', route: '/templates', icon: '▤' },
  { title: 'مكتبة القوالب', detail: '32 CV templates', route: '/templates', icon: '▦' },
  { title: 'مساعد الكتابة الذكي', detail: 'Smart CV — inside the builder', route: '/auth?next=/templates', icon: '✦' },
  { title: 'مراجعة جودة السيرة', detail: 'CV Quality — inside the builder', route: '/auth?next=/templates', icon: '◉' },
  { title: 'طباعة السيرة PDF', detail: 'Free export — inside the builder', route: '/auth?next=/templates', icon: '⇩' },
];
const careerFeatures: Item[] = [
  { title: 'خطاب التقديم', detail: 'Cover Letter Pro', route: '/career-tools/?tool=letter', icon: '✉' },
  { title: 'ملف LinkedIn', detail: 'Headline & About assistant', route: '/career-tools/?tool=linkedin', icon: 'in' },
  { title: 'التحضير للمقابلة', detail: 'Interview preparation', route: '/career-tools/?tool=interview', icon: '◇' },
];

function accountName(user: User | null) {
  const meta = user?.user_metadata;
  const candidate = meta?.full_name ?? meta?.name ?? meta?.display_name;
  return typeof candidate === 'string' && candidate.trim()
    ? candidate.trim().slice(0, 100)
    : (user?.email?.split('@')[0] || 'Sirati member');
}

function NavGroup({ title, items, close }: { title: string; items: Item[]; close: () => void }) {
  return <section className="sirati-menu-group">
    <h3>{title}</h3>
    {items.map(item => <a key={item.title} className="sirati-menu-item"
      href={withBasePath(item.route)} onClick={close}>
      <span className="sirati-menu-icon" aria-hidden="true">{item.icon}</span>
      <span className="sirati-menu-item-copy"><strong>{item.title}</strong><small>{item.detail}</small></span>
      <span className="sirati-menu-arrow" aria-hidden="true">‹</span>
    </a>)}
  </section>;
}

export default function SiratiSiteMenu() {
  const [open, setOpen] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const opener = useRef<HTMLButtonElement>(null);
  const closeButton = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    let mounted = true;
    let accountChangeSequence = 0;
    if (!isSupabaseConfigured()) { setLoading(false); return; }
    const supabase = createClient();
    if (!supabase) { setLoading(false); return; }
    const { data: listener } = supabase.auth.onAuthStateChange((event, session) => {
      if (!mounted || event === 'INITIAL_SESSION') return;
      accountChangeSequence++;
      setUser(session?.user ?? null);
      setLoading(false);
    });
    const initialSequence = accountChangeSequence;
    // Verify the current account instead of trusting a cached initial session.
    supabase.auth.getUser().then(({ data }) => {
      if (mounted && accountChangeSequence === initialSequence) {
        setUser(data.user ?? null);
        setLoading(false);
      }
    }).catch(() => { if (mounted) setLoading(false); });
    return () => { mounted = false; listener.subscription.unsubscribe(); };
  }, []);

  useEffect(() => {
    if (!open) return;
    const prior = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    closeButton.current?.focus();
    function handleKeys(event: KeyboardEvent) {
      if (event.key === 'Escape') setOpen(false);
      if (event.key !== 'Tab') return;
      const menu = document.getElementById('sirati-site-menu');
      const focusable = menu?.querySelectorAll<HTMLElement>('a[href],button:not([disabled])');
      if (!focusable?.length) return;
      const first = focusable[0], last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault(); last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault(); first.focus();
      }
    }
    document.addEventListener('keydown', handleKeys);
    return () => { document.body.style.overflow = prior; document.removeEventListener('keydown', handleKeys); opener.current?.focus(); };
  }, [open]);

  const name = accountName(user);
  const close = () => setOpen(false);

  return <>
    <button ref={opener} type="button" className="sirati-menu-trigger no-print"
      aria-label="Open Sirati menu" aria-expanded={open} aria-controls="sirati-site-menu"
      onClick={() => setOpen(true)}>
      <span aria-hidden="true" className="sirati-menu-bars"><i /><i /><i /></span>
      <span className="sirati-menu-trigger-text">القائمة</span>
    </button>
    {open && <div className="sirati-menu-layer no-print">
      <button className="sirati-menu-backdrop" type="button" aria-label="Close navigation" onClick={close}/>
      <aside id="sirati-site-menu" className="sirati-menu-panel" role="dialog" aria-modal="true"
        aria-label="Sirati features and customer account" dir="rtl">
        <header className="sirati-menu-header">
          <div className="sirati-menu-brand"><strong>Sirati</strong><small>Career Studio · استوديو المسار المهني</small></div>
          <button type="button" ref={closeButton} className="sirati-menu-close"
            aria-label="Close Sirati menu" onClick={close}>✕</button>
        </header>
        <div className="sirati-menu-scroll">
          <section className="sirati-menu-account" aria-label="Customer profile">
            {user ? <>
              <span className="sirati-menu-avatar" aria-hidden="true">{name.slice(0,1).toUpperCase()}</span>
              <div className="sirati-menu-account-copy">
                <strong>{name}</strong><small dir="auto">{user.email || 'No email available'}</small>
                <a href={withBasePath('/profile')} onClick={close}>الملف الشخصي وبياناتي ←</a>
              </div>
            </> : <>
              <span className="sirati-menu-avatar" aria-hidden="true">S</span>
              <div className="sirati-menu-account-copy">
                <strong>{loading ? 'جارٍ تحميل الحساب…' : 'حسابك في Sirati'}</strong>
                <small>{loading ? 'Account loading' : 'سجّل دخولك لإظهار بياناتك ومستنداتك'}</small>
                {!loading && <a href={withBasePath('/auth?next=/profile')} onClick={close}>تسجيل الدخول ←</a>}
              </div>
            </>}
          </section>
          <section className="sirati-menu-group">
            <h3>مساحة العمل</h3>
            <a className="sirati-menu-item" href={withBasePath('/')} onClick={close}>
              <span className="sirati-menu-icon" aria-hidden="true">⌂</span><span className="sirati-menu-item-copy"><strong>الرئيسية</strong><small>Home · Career Studio</small></span><span className="sirati-menu-arrow" aria-hidden="true">‹</span>
            </a>
            <a className="sirati-menu-item" href={withBasePath(user ? '/documents' : '/auth?next=/documents')} onClick={close}>
              <span className="sirati-menu-icon" aria-hidden="true">▣</span><span className="sirati-menu-item-copy"><strong>مستنداتي المحفوظة</strong><small>My Documents · Saved CVs</small></span><span className="sirati-menu-arrow" aria-hidden="true">‹</span>
            </a>
          </section>
          <NavGroup title="السيرة الذاتية" items={cvFeatures} close={close} />
          <NavGroup title="أدوات التطوير المهني" items={careerFeatures} close={close} />
          <section className="sirati-menu-group">
            <h3>المساعدة</h3>
            <a className="sirati-menu-item" href={withBasePath('/#faq')} onClick={close}>
              <span className="sirati-menu-icon" aria-hidden="true">?</span><span className="sirati-menu-item-copy"><strong>الأسئلة الشائعة</strong><small>FAQ</small></span><span className="sirati-menu-arrow" aria-hidden="true">‹</span>
            </a>
            <a className="sirati-menu-item" href={withBasePath('/#support')} onClick={close}>
              <span className="sirati-menu-icon" aria-hidden="true">✉</span><span className="sirati-menu-item-copy"><strong>التواصل والدعم</strong><small>Support</small></span><span className="sirati-menu-arrow" aria-hidden="true">‹</span>
            </a>
          </section>
          <div className="sirati-menu-footer">كل الأدوات مجانية · All tools are free</div>
        </div>
      </aside>
    </div>}
  </>;
}
""",encoding="utf-8")

profile = root / "app/profile/page.tsx"
profile.parent.mkdir(parents=True, exist_ok=True)
if profile.exists(): raise RuntimeError("Profile route already exists")
profile.write_text(r"""'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import type { User } from '@supabase/supabase-js';
import { createClient, isSupabaseConfigured } from '@/lib/supabase/client';

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);
  const [name, setName] = useState('');
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  useEffect(() => {
    const supabase = createClient();
    let alive = true;
    let accountChangeSequence = 0;
    if (!supabase) { setReady(true); return; }
    const { data: listener } = supabase.auth.onAuthStateChange((event, session) => {
      if (!alive || (event !== 'SIGNED_OUT' && event !== 'SIGNED_IN')) return;
      accountChangeSequence++;
      const u = session?.user ?? null;
      setUser(u);
      setName(typeof u?.user_metadata?.full_name === 'string' ? u.user_metadata.full_name : '');
      setReady(true);
    });
    const initialSequence = accountChangeSequence;
    supabase.auth.getUser().then(({ data }) => {
      if (!alive || accountChangeSequence !== initialSequence) return;
      const u = data.user ?? null;
      setUser(u);
      setName(typeof u?.user_metadata?.full_name === 'string' ? u.user_metadata.full_name : '');
      setReady(true);
    }).catch(() => { if (alive) setReady(true); });
    return () => { alive = false; listener.subscription.unsubscribe(); };
  }, []);
  async function saveProfile(event: React.FormEvent) {
    event.preventDefault();
    if (!user || saving) return;
    const supabase = createClient();
    if (!supabase) return;
    setSaving(true); setMessage('');
    try {
      const { data: fresh, error: refreshError } = await supabase.auth.getUser();
      if (refreshError || !fresh.user || fresh.user.id !== user.id) {
        throw new Error('Your session changed. Please reload the profile before saving.');
      }
      const { data, error } = await supabase.auth.updateUser({ data: { full_name: name.trim().slice(0,100) } });
      if (error) throw error;
      setUser(data.user);
      setMessage('Profile name saved. / تم حفظ الاسم.');
    } catch (error: unknown) {
      setMessage(error instanceof Error ? error.message : 'Could not save your name.');
    } finally {
      setSaving(false);
    }
  }
  return <main className="sirati-profile-page" dir="rtl">
    <div className="sirati-profile-shell">
      <header className="sirati-profile-heading"><span className="eyebrow">SIRATI ACCOUNT</span><h1>الملف الشخصي</h1>
        <p>راجع بيانات حسابك وأدر اسم العرض الخاص بك. لا تظهر بيانات أي حساب آخر.</p></header>
      {!ready ? <div className="sirati-profile-card" role="status">جارٍ تحميل الحساب…</div> :
        !user || !isSupabaseConfigured() ?
          <div className="sirati-profile-card"><h2>سجّل دخولك لعرض بياناتك</h2>
            <p>بيانات الحساب متاحة فقط لصاحب الحساب بعد تسجيل الدخول.</p>
            <Link className="btn btn-primary" href="/auth?next=/profile">تسجيل الدخول</Link></div> :
          <section className="sirati-profile-card">
            <div className="sirati-profile-identity">
              <span className="sirati-profile-avatar" aria-hidden="true">{(name || user.email || 'S').slice(0,1).toUpperCase()}</span>
              <div><h2>{name.trim() || 'Sirati member'}</h2><p dir="auto">{user.email || '—'}</p></div>
            </div>
            <form onSubmit={saveProfile}>
              <label htmlFor="sirati-profile-name">الاسم الظاهر على الملف الشخصي / Display name</label>
              <input id="sirati-profile-name" autoComplete="name" maxLength={100} value={name}
                onChange={e => setName(e.target.value)} placeholder="Your name"/>
              <button className="btn btn-primary" type="submit" disabled={saving}>{saving ? 'جارٍ الحفظ…' : 'حفظ الاسم'}</button>
            </form>
            <div className="sirati-profile-details">
              <div><span>البريد الإلكتروني / Email</span><strong dir="auto">{user.email || '—'}</strong></div>
              <div><span>حالة البريد / Email status</span><strong>{user.email_confirmed_at ? 'مؤكد / Verified' : 'غير مؤكد / Not verified'}</strong></div>
              <div><span>تاريخ إنشاء الحساب / Joined</span><strong>{new Date(user.created_at).toLocaleDateString()}</strong></div>
            </div>
            <Link className="btn btn-secondary" href="/documents">مستنداتي / My documents</Link>
          </section>}
    </div>
  </main>;
}
""",encoding="utf-8")

career = root / "app/career-tools/page.tsx"
s = career.read_text(encoding="utf-8")
s = once(s, "import { useState } from 'react';", "import { useEffect, useState } from 'react';",
    "career route useEffect import")
s = once(s, "  const [mode, setMode] = useState<Mode>('letter');",
    """  const [mode, setMode] = useState<Mode>('letter');
  useEffect(() => {
    const requested = new URLSearchParams(window.location.search).get('tool');
    if (requested === 'letter' || requested === 'linkedin' || requested === 'interview') {
      setMode(requested);
    }
  }, []);""", "career mode deep link")
career.write_text(s, encoding="utf-8")

css_file = root / "app/globals.css"
css = css_file.read_text(encoding="utf-8")
if "/* Sirati Career Platform Navigation */" in css: raise RuntimeError("Menu styles already installed")
css += r"""
/* Sirati Career Platform Navigation */
@media screen {
  .marketing-page .marketing-hero .hero-lead {
    color: #edf4ed !important;
    opacity: 1 !important;
    font-weight: 470;
    text-shadow: 0 1px 1px rgba(0,0,0,.10);
  }
  .marketing-page .marketing-hero h1 {
    color: #fffefa !important;
    font-size: clamp(38px, 5.25vw, 74px);
    line-height: 1.06;
  }
  .marketing-page .marketing-hero h1 span { color: #f1d9ad !important; }
  .marketing-page .marketing-nav { padding-right: 124px; }
  .sirati-menu-trigger {
    position: fixed; top: 15px; right: 15px; z-index: 1050;
    display: inline-flex; align-items: center; gap: 8px;
    padding: 10px 12px; min-height: 49px;
    color: #fffefa; background: #153c31; border: 1px solid #366d53;
    border-radius: 13px; cursor: pointer; font-weight: 750; font-size: 13px;
    box-shadow: 0 8px 23px rgba(17,50,40,.18);
  }
  .sirati-menu-trigger:focus-visible,.sirati-menu-close:focus-visible,
  .sirati-menu-panel a:focus-visible { outline: 3px solid #cfae74; outline-offset: 3px; }
  .sirati-menu-bars { display: grid; gap: 4px; }
  .sirati-menu-bars i { display: block; background: #f3e3bd; width: 20px; height: 2px; border-radius: 9px; }
  .sirati-menu-layer { position: fixed; inset: 0; z-index: 2000; }
  .sirati-menu-backdrop { position: absolute; inset: 0; width: 100%; border: 0; background: rgba(9,26,19,.64); cursor: pointer; }
  .sirati-menu-panel {
    position: absolute; inset-block: 0; right: 0;
    width: min(420px, 92vw); display: flex; flex-direction: column;
    background: #f8faf7; color: #1a372c; box-shadow: -20px 0 80px rgba(0,0,0,.18);
    overscroll-behavior: contain;
  }
  .sirati-menu-header {
    display: flex; align-items: center; justify-content: space-between; gap: 12px;
    padding: 21px 21px 18px; color: #f8fff9;
    background: linear-gradient(120deg,#14392f,#285c49);
  }
  .sirati-menu-brand { display: flex; flex-direction: column; gap: 3px; }
  .sirati-menu-brand strong { font-size: 26px; font-weight: 800; letter-spacing: -.04em; }
  .sirati-menu-brand small { color: #e5d2a8; font-size: 12px; }
  .sirati-menu-close {
    border-radius: 11px; border: 1px solid rgba(255,255,255,.3);
    background: rgba(255,255,255,.1); color: white; width: 43px; height: 43px;
    font-size: 19px; cursor: pointer;
  }
  .sirati-menu-scroll { overflow-y: auto; min-height: 0; padding: 18px; }
  .sirati-menu-account {
    display: flex; align-items: center; gap: 13px; min-width: 0; padding: 16px;
    border-radius: 17px; background: #eaf2ea; border: 1px solid #d4e1d6;
  }
  .sirati-menu-avatar {
    flex: 0 0 50px; width: 50px; height: 50px; display: grid; place-items: center;
    border-radius: 16px; background: #1b4f3d; color: #f5dfb6; font-size: 24px; font-weight: 800;
  }
  .sirati-menu-account-copy { min-width: 0; display: flex; flex-direction: column; gap: 5px; }
  .sirati-menu-account-copy strong { font-size: 16px; color: #14382f; overflow-wrap: anywhere; }
  .sirati-menu-account-copy small { font-size: 12px; color: #536a5d; overflow-wrap: anywhere; }
  .sirati-menu-account-copy a { color: #1b5b47; text-decoration: underline; text-underline-offset: 3px; font-weight: 700; font-size: 12px; }
  .sirati-menu-group { margin-top: 25px; }
  .sirati-menu-group h3 { font-size: 12px; color: #62796d; letter-spacing: .05em; padding: 0 8px; margin: 0 0 10px; }
  .sirati-menu-item {
    display: flex; align-items: center; gap: 11px; color: #14392e;
    background: #fffefa; border: 1px solid #dde8df; border-radius: 13px;
    margin-top: 7px; padding: 11px 12px; min-height: 56px;
    text-decoration: none; transition: background .15s ease, border-color .15s ease;
  }
  .sirati-menu-item:hover { background: #eaf3ec; border-color: #c3d5c8; }
  .sirati-menu-icon {
    flex: 0 0 38px; display: grid; place-items: center;
    width: 38px; height: 38px; background: #eaf2e9; color: #245d47;
    border-radius: 10px; font-size: 19px; font-weight: 760;
  }
  .sirati-menu-item-copy { min-width: 0; flex: 1; display: flex; flex-direction: column; gap: 3px; }
  .sirati-menu-item-copy strong { font-size: 14px; font-weight: 750; }
  .sirati-menu-item-copy small { font-size: 11px; color: #647769; }
  .sirati-menu-arrow { color: #557968; font-size: 25px; }
  .sirati-menu-footer { padding: 24px 5px 8px; font-size: 12px; color: #60766a; text-align: center; }
  .sirati-profile-page { min-height: 100vh; background: #f4f7f3; padding: 80px 16px 56px; }
  .sirati-profile-shell { max-width: 850px; margin: auto; }
  .sirati-profile-heading { margin-bottom: 26px; }
  .sirati-profile-heading h1 { font-size: clamp(28px,4vw,45px); color: #143c30; }
  .sirati-profile-heading p { color: #586b61; }
  .sirati-profile-card {
    padding: clamp(20px,4vw,36px); border: 1px solid #dbe8dd;
    background: #fffefa; border-radius: 22px; box-shadow: 0 15px 40px rgba(14,49,33,.06);
  }
  .sirati-profile-identity { display: flex; align-items: center; gap: 15px; padding-bottom: 25px; }
  .sirati-profile-avatar { flex: 0 0 70px; display: grid; place-items: center; height: 70px; border-radius: 19px; background: #184735; color: #f1dbac; font-size: 32px; font-weight: 800; }
  .sirati-profile-identity h2 { margin: 0; color: #173a30; overflow-wrap: anywhere; }
  .sirati-profile-identity p { color: #607367; overflow-wrap: anywhere; }
  .sirati-profile-card form { display: grid; gap: 12px; margin-bottom: 23px; }
  .sirati-profile-card form label { font-weight: 700; color: #264c3b; }
  .sirati-profile-card input {
    display: block; padding: 13px; border: 1px solid #b6ccbb;
    border-radius: 12px; min-height: 46px; font: inherit; background: #fff; color: #1a372c;
  }
  .sirati-profile-card form button { justify-self: start; }
  .sirati-profile-details { display: grid; gap: 10px; margin-bottom: 25px; }
  .sirati-profile-details div { display: grid; gap: 4px; border: 1px solid #e2eae3; border-radius: 12px; padding: 12px 15px; }
  .sirati-profile-details span { color: #597165; font-size: 12px; }
  .sirati-profile-details strong { overflow-wrap: anywhere; font-size: 14px; font-weight: 690; }
}
@media screen and (max-width: 800px) {
  .marketing-page .nav-cta { display: none !important; }
  .marketing-page .marketing-nav { padding-right: 100px; }
  .sirati-menu-trigger { top: 15px; right: 14px; }
}
@media screen and (max-width: 390px) {
  .sirati-menu-trigger { padding: 10px; }
  .sirati-menu-trigger-text { display: none; }
  .marketing-page .marketing-nav { padding-right: 67px; }
  .sirati-menu-panel { width: min(375px, 96vw); }
  .sirati-profile-identity { align-items: flex-start; }
}
@media print { .sirati-menu-trigger, .sirati-menu-layer { display: none !important; } }
@media (prefers-reduced-motion: reduce) {
  .sirati-menu-item { transition: none; }
}
"""
css_file.write_text(css, encoding="utf-8")
print("PASS: Career-wide homepage, customer profile and accessible feature drawer installed.")
