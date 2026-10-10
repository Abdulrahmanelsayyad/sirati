"""Generate an opt-in client pageview tracker and server-gated owner dashboard.
Feature flag OFF by default. Existing account, Builder and PDF code untouched.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
(root / "components").mkdir(parents=True, exist_ok=True)
(root / "app" / "analytics").mkdir(parents=True, exist_ok=True)

(root / "components" / "SiratiAnalyticsTracker.tsx").write_text(r"""'use client';

import { useEffect, useRef, useState } from 'react';
import { usePathname } from 'next/navigation';
import { createClient } from '@/lib/supabase/client';

const ENABLED = process.env.NEXT_PUBLIC_ANALYTICS_ENABLED === 'true';
const CONSENT_KEY = 'sirati.analytics.consent.v1';
const SID_KEY = 'sirati.analytics.session.v1';
type Choice = 'loading' | 'unset' | 'yes' | 'no';

function safeRoute(path: string) {
  const clean = (path.replace(/^\/sirati(?=\/|$)/, '') || '/').replace(/\/+$/, '') || '/';
  if (clean === '/') return '/';
  for (const route of ['/auth', '/templates', '/builder', '/documents',
                       '/career-tools', '/profile']) {
    if (clean === route || clean.startsWith(route + '/')) return route;
  }
  return '/other'; // Never transmit raw paths, names, search strings or CV data.
}

function trackingBlocked() {
  // QA exclusion must be enforced at every send, not just at component mount.
  // When browser storage is inaccessible, fail closed for analytics only.
  if (typeof navigator === 'undefined' || typeof localStorage === 'undefined') return true;
  const nav = navigator as Navigator & { globalPrivacyControl?: boolean };
  try {
    return nav.doNotTrack === '1' || nav.globalPrivacyControl === true ||
      localStorage.getItem('sirati.analytics.qa_optout') === 'yes';
  } catch {
    return true;
  }
}

export default function SiratiAnalyticsTracker() {
  const pathname = usePathname() || '/';
  const [choice, setChoice] = useState<Choice>('loading');
  const sentFor = useRef('');
  useEffect(() => {
    if (!ENABLED) return;
    try {
      if (trackingBlocked()) {
        setChoice('no'); return;
      }
      const saved = localStorage.getItem(CONSENT_KEY);
      setChoice(saved === 'yes' || saved === 'no' ? saved : 'unset');
    } catch { setChoice('no'); }
  }, []);
  useEffect(() => {
    if (!ENABLED || choice !== 'yes' || trackingBlocked() || sentFor.current === pathname) return;
    try {
      const client = createClient();
      if (!client) return;
      let sid = sessionStorage.getItem(SID_KEY);
      if (!sid) { sid = crypto.randomUUID(); sessionStorage.setItem(SID_KEY, sid); }
      sentFor.current = pathname;
      // The RPC accepts only enumerated event types and normalized routes.
      Promise.resolve(client.rpc('sirati_track_event', {
        p_session: sid, p_event: crypto.randomUUID(),
        p_type: 'page_view', p_route: safeRoute(pathname),
      })).catch(() => { /* Analytics failures never break Sirati. */ });
    } catch { /* Browser storage/crypto may be blocked. */ }
  }, [pathname, choice]);
  if (!ENABLED || choice === 'loading' || trackingBlocked()) return null;
  const choose = (value: 'yes' | 'no') => {
    try { localStorage.setItem(CONSENT_KEY, value); } catch { return; }
    setChoice(value);
  };
  return (
    <div className="no-print" style={{position:'fixed',bottom:8,left:8,zIndex:1200,maxWidth:'min(92vw,390px)'}}>
      {choice === 'unset' ? (
        <aside aria-label="Analytics preferences · تفضيلات الإحصائيات"
          style={{background:'#fff',border:'1px solid #d4e0d8',borderRadius:12,padding:14,
                  boxShadow:'0 8px 35px #10281822',fontSize:13,color:'#1e3528'}}>
          <strong>Private, optional analytics · إحصائيات اختيارية</strong>
          <p style={{margin:'8px 0'}}>Help us count visits without storing your CV, email,
            IP address or job details. No advertising tracking.
            <span dir="rtl" style={{display:'block',marginTop:4}}>
              نطلب موافقتك لقياس الزيارات دون حفظ بيانات سيرتك أو بريدك أو عنوان IP.
            </span>
          </p>
          <div style={{display:'flex',gap:8,flexWrap:'wrap'}}>
            <button type="button" onClick={() => choose('yes')}>Allow · موافق</button>
            <button type="button" onClick={() => choose('no')}>No thanks · لا شكرًا</button>
          </div>
        </aside>
      ) : (
        <button type="button" title="Change optional analytics consent"
          aria-label="Analytics privacy settings · إعدادات الخصوصية"
          onClick={() => setChoice('unset')}
          style={{fontSize:10,background:'#ffffffed',color:'#52645a',border:'1px solid #d7dfd7',
                  borderRadius:6,padding:'4px 6px'}}>
          Privacy · الخصوصية
        </button>
      )}
    </div>
  );
}
""", encoding="utf-8")

(root / "app" / "analytics" / "page.tsx").write_text(r"""'use client';

import { useEffect, useState } from 'react';
import { createClient } from '@/lib/supabase/client';
import { withBasePath } from '@/lib/basePath';

type Daily = { date: string; views: number; sessions: number };
type Report = {
  registered_accounts: number; cv_creators: number; saved_cvs: number;
  page_views: number; estimated_sessions: number;
  daily: Daily[];
};
export default function AnalyticsPage() {
  const [days, setDays] = useState<1 | 7 | 30>(7);
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let active = true;
    setLoading(true); setError(''); setReport(null);
    const client = createClient();
    if (!client) { setError('Account services unavailable · الحساب غير متاح'); setLoading(false); return; }
    (async () => {
      const { data: auth, error: authError } = await client.auth.getUser();
      if (authError || !auth.user) throw new Error('Sign in required · يلزم تسجيل الدخول');
      // Client-side UI is NEVER the permission boundary. The RPC independently
      // checks auth.uid() against a private admin UUID table.
      const { data, error: reportError } = await client.rpc('sirati_analytics_summary', { p_days: days });
      if (reportError) throw new Error('Owner access only · هذه الصفحة مخصصة للمالك');
      if (active) setReport(data as Report);
    })().catch((e: unknown) => {
      if (active) setError(e instanceof Error ? e.message : 'Analytics unavailable');
    }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [days]);

  const maximum = Math.max(1, ...(report?.daily || []).map(row => row.views));
  const cards: Array<[string, number]> = report ? [
    ['Page views · مشاهدات الصفحات', report.page_views],
    ['Browser sessions · جلسات المتصفح', report.estimated_sessions],
    ['Registered accounts · الحسابات', report.registered_accounts],
    ['CV creators · منشئو السير', report.cv_creators],
    ['Saved CVs · السير المحفوظة', report.saved_cvs],
  ] : [];
  return (
    <main className="container" style={{maxWidth:990,margin:'32px auto',padding:'18px 16px',minHeight:'72vh'}}>
      <a href={withBasePath('/')} style={{fontSize:14}}>← Sirati · الرئيسية</a>
      <h1 style={{margin:'18px 0 4px'}}>Site Analytics · إحصائيات الموقع</h1>
      <p style={{color:'#52675a'}}>Private aggregate dashboard · لوحة خاصة لمالك الموقع</p>
      <label htmlFor="analytics-window" style={{display:'inline-flex',gap:12,alignItems:'center',margin:'12px 0 22px'}}>
        Period · الفترة
        <select id="analytics-window" value={days}
          onChange={e => setDays(Number(e.target.value) as 1 | 7 | 30)}>
          <option value={1}>24 hours · يوم</option>
          <option value={7}>7 days · أسبوع</option>
          <option value={30}>30 days · شهر</option>
        </select>
      </label>
      {loading && <p role="status">Loading · جاري التحميل...</p>}
      {error && <p role="alert" style={{color:'#97432d'}}>{error}</p>}
      {report && <>
        <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(180px,1fr))',gap:12}}>
          {cards.map(([title,count]) => (
            <section key={title} style={{padding:16,background:'#f5f8f4',
              border:'1px solid #dfe7df',borderRadius:12}}>
              <span style={{fontSize:12,color:'#567161'}}>{title}</span>
              <div style={{fontSize:30,fontWeight:800,marginTop:6}}>{count.toLocaleString('en-US')}</div>
            </section>
          ))}
        </div>
        <section style={{marginTop:25,padding:18,border:'1px solid #dfe7df',borderRadius:12}}>
          <h2 style={{fontSize:20}}>Daily views · الزيارات اليومية</h2>
          {report.daily.length ? (
            <div role="img" aria-label="Daily accepted page-view counts"
              style={{display:'flex',gap:8,alignItems:'end',height:155,overflowX:'auto',padding:'20px 0 0'}}>
              {report.daily.map(row => (
                <div key={row.date} title={row.date + ': ' + row.views + ' views'}
                  style={{flex:'1 0 18px',minWidth:18,display:'flex',alignItems:'center',
                    flexDirection:'column',justifyContent:'end',height:'100%'}}>
                  <span style={{fontSize:10}}>{row.views}</span>
                  <div style={{height:Math.max(3,115*row.views/maximum),
                    background:'#3b7656',width:'100%',borderRadius:'5px 5px 0 0'}} />
                  <span style={{fontSize:9,whiteSpace:'nowrap'}}>{row.date.slice(5)}</span>
                </div>
              ))}
            </div>
          ) : <p>Not collecting yet · لا توجد زيارات مسجلة بعد</p>}
        </section>
        <p style={{fontSize:12,color:'#617368',marginTop:16}}>
          Visits start only after approved tracking activation and user consent.
          Sessions are not unique people; they are browser-tab/session estimates.
          Some users opt out. PDF exports and other events are not instrumented yet.
          <span dir="rtl" style={{display:'block',marginTop:5}}>
            يبدأ العد بعد تفعيل التتبع وموافقة الزائر. الجلسات لا تعني عدد أشخاص فريدين،
            وقد يرفض بعض الزوار القياس. تنزيلات PDF لم تُربط بالتتبع بعد.
          </span>
        </p>
      </>}
    </main>
  );
}
""", encoding="utf-8")

layout_path = root / "app" / "layout.tsx"
layout = layout_path.read_text(encoding="utf-8")
if layout.count("</body>") != 1:
    raise RuntimeError("Analytics install: RootLayout body anchor missing")
if "SiratiAnalyticsTracker" in layout:
    raise RuntimeError("Analytics install: tracker already present")
layout = "import SiratiAnalyticsTracker from '@/components/SiratiAnalyticsTracker';\n" + layout
layout = layout.replace("</body>", "        <SiratiAnalyticsTracker />\n      </body>", 1)
layout_path.write_text(layout, encoding="utf-8")
