"""Sirati Feedback Dashboard V2: limited client-side insights and editable own review.

Runs after the original feedback generator. No database writes, migrations, or auth/RLS changes.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
dashboard = root / "app/feedback-dashboard/page.tsx"
component = root / "components/SiratiFeedbackRating.tsx"
css_path = root / "app/globals.css"
if not dashboard.exists() or not component.exists():
    raise RuntimeError("Feedback V2 requires the existing generated feedback pages")

dashboard.write_text(r"""'use client';

import { useEffect, useMemo, useState } from 'react';
import { createClient } from '@/lib/supabase/client';
import { withBasePath } from '@/lib/basePath';

type Review = { rating: number; category: string; comment: string; created_at: string };
type Phase = 'loading' | 'ready' | 'signin' | 'denied' | 'failed';
const categories: Record<string, string> = {
  overall: 'التجربة العامة · Overall',
  templates: 'القوالب · Templates',
  editing: 'المحرر · Editor',
  pdf: 'PDF',
  mobile: 'الموبايل · Mobile',
};
const ratingSteps = [5, 4, 3, 2, 1] as const;

export default function FeedbackDashboard() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [totalCount, setTotalCount] = useState<number | null>(null);
  const [phase, setPhase] = useState<Phase>('loading');
  const [retry, setRetry] = useState(0);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');
  const [stars, setStars] = useState('all');
  const [sort, setSort] = useState('latest');

  useEffect(() => {
    let alive = true;
    let authorizedUserId: string | null = null;
    let revoked = false;
    setPhase('loading');
    setReviews([]);
    setTotalCount(null);

    const client = createClient();
    if (!client) { setPhase('failed'); return; }
    const { data: listener } = client.auth.onAuthStateChange((event, session) => {
      if (!alive || event === 'INITIAL_SESSION' || authorizedUserId === null) return;
      if (session?.user?.id !== authorizedUserId ||
          session.user.app_metadata?.sirati_feedback_admin !== true) {
        revoked = true;
        setReviews([]);
        setTotalCount(null);
        setPhase('denied');
      }
    });
    (async () => {
      try {
        const { data: auth, error: authError } = await client.auth.getUser();
        if (!alive || revoked) return;
        if (authError || !auth.user) { setPhase('signin'); return; }
        if (auth.user.app_metadata?.sirati_feedback_admin !== true) {
          setPhase('denied'); return;
        }
        authorizedUserId = auth.user.id;
        // One bounded owner-only RLS query. Counts may cover more than the 200
        // rows used for the summary; never present the sample average as global.
        const { data, count, error } = await client.from('sirati_site_feedback')
          .select('rating,category,comment,created_at', { count: 'exact' })
          .order('created_at', { ascending: false }).limit(200);
        if (error) throw error;
        if (!alive || revoked) return;
        setReviews((data || []) as Review[]);
        setTotalCount(typeof count === 'number' ? count : null);
        setPhase('ready');
      } catch {
        if (alive && !revoked) setPhase('failed');
      }
    })();
    return () => { alive = false; listener.subscription.unsubscribe(); };
  }, [retry]);

  const shown = reviews.length;
  const avg = shown ? (reviews.reduce((sum, item) => sum + item.rating, 0) / shown).toFixed(1) : '—';
  const filtered = useMemo(() => {
    const q = search.trim().toLocaleLowerCase();
    const subset = reviews.filter(item =>
      (category === 'all' || item.category === category) &&
      (stars === 'all' || item.rating === Number(stars)) &&
      (!q || (item.comment + ' ' + (categories[item.category] || '')).toLocaleLowerCase().includes(q))
    );
    return subset.sort((a, b) =>
      sort === 'lowest' ? a.rating - b.rating :
      sort === 'highest' ? b.rating - a.rating :
      new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
  }, [reviews, category, stars, search, sort]);

  return (
    <main className="container sirati-rating-admin sirati-rating-v2" dir="rtl">
      <a className="sirati-rating-v2__back" href={withBasePath('/')}>← الرئيسية · Home</a>
      <header className="sirati-rating-v2__header">
        <div><span className="sirati-rating-v2__eyebrow">SIRATI · PRIVATE INSIGHTS</span>
          <h1>تقييمات المستخدمين <span aria-hidden="true">★</span></h1>
          <p>Visitor feedback · لوحة خاصة بصاحب الموقع</p>
        </div>
      </header>

      {phase === 'loading' && <p role="status">جاري تحميل التقييمات · Loading feedback…</p>}
      {phase === 'signin' && <div role="alert" className="sirati-rating-v2__notice">
        سجّل دخولك لحساب المالك لعرض التقييمات · Sign in as owner.
        {' '}<a href={withBasePath('/auth?next=/feedback-dashboard')}>تسجيل الدخول · Sign in</a>
      </div>}
      {phase === 'denied' && <div role="alert" className="sirati-rating-v2__notice">
        غير متاح إلا لمالك الموقع · Owner access required
      </div>}
      {phase === 'failed' && <div role="alert" className="sirati-rating-v2__notice">
        تعذر تحميل التقييمات الآن · Could not load feedback.
        <button type="button" onClick={() => setRetry(v => v + 1)}>إعادة المحاولة · Retry</button>
      </div>}
      {phase === 'ready' && <>
        <div className="sirati-rating-admin__stats">
          <div><span>إجمالي التقييمات · Total reviews</span>
            <strong>{totalCount === null ? '—' : totalCount}</strong></div>
          <div><span>التقييمات المحمّلة · Reviews loaded</span><strong>{shown}</strong></div>
          <div><span>متوسط التقييمات المحمّلة · Loaded average</span><strong dir="ltr">{avg} / 5</strong></div>
        </div>
        <p className="sirati-rating-v2__scope">
          الإحصائيات والتوزيع تشمل أحدث {shown} تقييم فقط (بحد أقصى 200)، وليست بالضرورة كل التقييمات.
          {' '}· Metrics reflect the latest loaded reviews, not necessarily all-time.
        </p>

        <section className="sirati-rating-v2__distribution" aria-label="توزيع النجوم · Star distribution">
          <h2>توزيع التقييمات · Rating breakdown</h2>
          {ratingSteps.map(value => {
            const n = reviews.filter(item => item.rating === value).length;
            const percentage = shown ? Math.round(n / shown * 100) : 0;
            return <div className="sirati-rating-v2__bar-row" key={value}>
              <span aria-label={value + ' stars'} dir="ltr">{value} ★</span>
              <div className="sirati-rating-v2__track" aria-hidden="true">
                <span style={{ width: percentage + '%' }} />
              </div>
              <span dir="ltr">{n} ({percentage}%)</span>
            </div>;
          })}
        </section>

        <section className="sirati-rating-v2__filters" aria-label="فلترة التقييمات · Filter reviews">
          <h2>تصفّح الآراء · Explore reviews</h2>
          <div className="sirati-rating-v2__filter-grid">
            <label>بحث في التعليقات · Search
              <input type="search" value={search} onChange={e => setSearch(e.target.value)}
                placeholder="ابحث بكلمة أو قسم…" dir="auto" />
            </label>
            <label>القسم · Category
              <select value={category} onChange={e => setCategory(e.target.value)}>
                <option value="all">جميع الأقسام · All categories</option>
                {Object.entries(categories).map(([value, name]) =>
                  <option value={value} key={value}>{name}</option>)}
              </select>
            </label>
            <label>النجوم · Stars
              <select value={stars} onChange={e => setStars(e.target.value)}>
                <option value="all">كل التقييمات · All ratings</option>
                {ratingSteps.map(value => <option value={String(value)} key={value}>{value} ★</option>)}
              </select>
            </label>
            <label>الترتيب · Sort
              <select value={sort} onChange={e => setSort(e.target.value)}>
                <option value="latest">الأحدث · Newest</option>
                <option value="lowest">الأقل تقييمًا · Lowest</option>
                <option value="highest">الأعلى تقييمًا · Highest</option>
              </select>
            </label>
          </div>
          <p role="status">{filtered.length} نتيجة من {shown} تقييم محمّل · {filtered.length} matching loaded reviews</p>
        </section>

        <div className="sirati-rating-admin__list">
          {shown === 0 && <p className="sirati-rating-v2__empty">لا توجد تقييمات حتى الآن · No feedback yet.</p>}
          {shown > 0 && filtered.length === 0 && <div className="sirati-rating-v2__empty">
            <p>لا توجد نتائج مطابقة · No matching feedback</p>
            <button type="button" onClick={() => { setSearch(''); setCategory('all'); setStars('all'); setSort('latest'); }}>
              مسح الفلاتر · Clear filters
            </button>
          </div>}
          {filtered.map((item, index) => (
            <article key={item.created_at + ':' + index}>
              <div className="sirati-rating-v2__review-head">
                <strong aria-label={item.rating + ' of 5 stars'}>{'★'.repeat(item.rating)}{'☆'.repeat(5 - item.rating)}</strong>
                <span>{categories[item.category] || 'أخرى · Other'}</span>
              </div>
              {item.comment ? <p dir="auto">{item.comment}</p> :
                <p className="sirati-rating-v2__no-comment">بدون تعليق · No comment</p>}
              <time dateTime={item.created_at}>
                {new Date(item.created_at).toLocaleDateString('en-GB')}
              </time>
            </article>
          ))}
        </div>
        <p className="sirati-rating-v2__scope">
          الآراء تطوعية وغير موثقة بشكل مستقل. لا تظهر رسائل البريد أو السير الذاتية أو معرفات الحسابات.
          {' '}· Voluntary, unverified feedback; no email, CV or user ID is displayed.
        </p>
      </>}
    </main>
  );
}
""", encoding="utf-8")

text = component.read_text(encoding="utf-8")
def replace_one(before, after, label):
    global text
    if text.count(before) != 1:
        raise RuntimeError(f"Feedback V2 {label}: expected exactly one anchor; got {text.count(before)}")
    text = text.replace(before, after, 1)

replace_one("import { useState, type FormEvent } from 'react';",
    "import { useEffect, useRef, useState, type FormEvent } from 'react';",
    "useEffect import")

replace_one("  const resetNotice = () => setStatus('idle');", r"""  const [previous, setPrevious] = useState(false);
  const [loadingPrevious, setLoadingPrevious] = useState(true);
  const [previousError, setPreviousError] = useState(false);
  const currentUserId = useRef<string | null>(null);
  const edited = useRef(false);
  const resetNotice = () => { setStatus('idle'); edited.current = true; };

  useEffect(() => {
    const client = createClient();
    if (!client) { setLoadingPrevious(false); setPreviousError(true); return; }
    let alive = true;
    let sequence = 0;

    const loadOwnReview = async () => {
      const seq = ++sequence;
      setLoadingPrevious(true);
      setPreviousError(false);
      try {
        const { data: auth, error: authError } = await client.auth.getUser();
        if (!alive || sequence !== seq) return;
        if (authError) throw authError;
        currentUserId.current = auth.user?.id ?? null;
        if (!auth.user) {
          setPrevious(false);
          setLoadingPrevious(false);
          return;
        }
        // Only the caller's record is requested. RLS is the server boundary.
        const { data, error } = await client.from('sirati_site_feedback')
          .select('rating,category,comment').eq('user_id', auth.user.id).maybeSingle();
        if (!alive || sequence !== seq) return;
        if (error) throw error;
        if (data && !edited.current) {
          setRating(data.rating);
          if (areas.some(item => item.value === data.category)) setArea(data.category as Area);
          setComment(data.comment || '');
        }
        setPrevious(Boolean(data));
        setLoadingPrevious(false);
      } catch {
        if (alive && sequence === seq) {
          setPreviousError(true);
          setLoadingPrevious(false);
        }
      }
    };
    const { data: listener } = client.auth.onAuthStateChange((event, session) => {
      if (!alive || event === 'INITIAL_SESSION') return;
      const nextUserId = session?.user?.id ?? null;
      if (nextUserId === currentUserId.current) return;
      // Only an actual account change clears the previous account's draft.
      edited.current = false;
      currentUserId.current = nextUserId;
      sequence++; // Immediately invalidate any in-flight review SELECT.
      setRating(0);
      setArea('overall');
      setComment('');
      setPrevious(false);
      setStatus('idle');
      // Do not call awaitable Supabase methods synchronously inside Auth callbacks.
      window.setTimeout(() => { if (alive) void loadOwnReview(); }, 0);
    });
    void loadOwnReview();
    return () => { alive = false; sequence++; listener.subscription.unsubscribe(); };
  }, []);
""", "load/edit existing")

replace_one("if (rating < 1 || rating > 5 || status === 'saving') return;",
            "if (rating < 1 || rating > 5 || status === 'saving' || loadingPrevious || previousError) return;",
            "prevent overwrite before own review loaded")
replace_one("      if (authError || !auth.user) { setStatus('signin'); return; }",
            "      if (authError || !auth.user) { setStatus('signin'); return; }\n      if (currentUserId.current !== auth.user.id) { setStatus('error'); return; }",
            "only current verified owner of review")
replace_one("      setStatus(error ? 'error' : 'saved');",
            "      if (currentUserId.current !== auth.user.id) return;\n      if (!error) setPrevious(true);\n      setStatus(error ? 'error' : 'saved');",
            "only confirm after save")
replace_one('''        <fieldset className="sirati-feedback-v2__fieldset">''', '''        {previous && !loadingPrevious && !previousError &&
          <p className="sirati-feedback-v2__previous" role="status">
            ★ تقييمك السابق ظاهر ويمكنك تعديله وإرساله مرة أخرى · Your previous review is loaded; edit and resubmit.
          </p>}
        {loadingPrevious && <p className="sirati-feedback-v2__account-note" role="status">
          جاري التحقق من تقييمك السابق · Loading your review…
        </p>}
        {previousError && <p className="sirati-feedback-v2__status is-error" role="alert">
          تعذر تحميل تقييمك السابق. حدّث الصفحة قبل الإرسال لتجنّب استبداله.
          {' '}· Could not load your review; reload before submitting.
        </p>}
        <fieldset className="sirati-feedback-v2__fieldset">''', "previous review notice")
replace_one("disabled={!rating || status === 'saving'} aria-busy={status === 'saving'}",
            "disabled={!rating || status === 'saving' || loadingPrevious || previousError} aria-busy={status === 'saving'}",
            "disable submit while loading")
replace_one("{status === 'saving' ? 'جاري الإرسال · Sending...' : 'إرسال التقييم · Send feedback'}",
            "{status === 'saving' ? 'جاري الإرسال · Sending...' : previous ? 'تحديث التقييم · Update feedback' : 'إرسال التقييم · Send feedback'}",
            "edit button")
component.write_text(text, encoding="utf-8")

css = css_path.read_text(encoding="utf-8")
if "/* Sirati feedback insights V2 */" in css: raise RuntimeError("Duplicate insights stylesheet")
css += r"""

/* Sirati feedback insights V2 */
/* Owner dashboard, mobile filters and own-review hint */
@media screen {
.sirati-rating-v2 { max-width:1060px; color:#173d2f; }
.sirati-rating-v2__back { display:inline-block;margin-bottom:14px;color:#286348;font-weight:750;text-decoration:none; }
.sirati-rating-v2__header { padding:clamp(20px,4vw,35px);border-radius:22px;background:linear-gradient(125deg,#143f31,#246a4e);color:#fff; }
.sirati-rating-v2__header h1 {margin:8px 0;font-size:clamp(24px,3.6vw,35px);color:#fff; }
.sirati-rating-v2__header h1 span {color:#ebc877;}
.sirati-rating-v2__header p {margin:0;color:#e0eee3;}
.sirati-rating-v2__eyebrow {letter-spacing:.1em;font-size:11px;color:#d4e9d5;font-weight:750;}
.sirati-rating-v2 .sirati-rating-admin__stats {grid-template-columns:repeat(3,minmax(0,1fr));margin:20px 0 12px;}
.sirati-rating-v2 .sirati-rating-admin__stats>div {box-shadow:0 5px 22px #173a2110;}
.sirati-rating-v2__scope {font-size:12px;line-height:1.9;color:#526d5d;margin:12px 1px 20px;}
.sirati-rating-v2__distribution,.sirati-rating-v2__filters {border:1px solid #dce8df;border-radius:18px;background:#fff;padding:clamp(16px,3vw,24px);margin:20px 0;}
.sirati-rating-v2 :is(.sirati-rating-v2__distribution,.sirati-rating-v2__filters) h2 {font-size:18px;color:#173d2f;margin:0 0 19px;}
.sirati-rating-v2__bar-row {display:grid;grid-template-columns:48px minmax(0,1fr) 90px;align-items:center;gap:12px;margin:12px 0;font-size:12px;}
.sirati-rating-v2__bar-row>span:last-child {text-align:right;color:#4d6c5b;}
.sirati-rating-v2__track {height:11px;background:#eaf0e9;border-radius:99px;overflow:hidden;}
.sirati-rating-v2__track span {display:block;height:100%;background:#bd8526;border-radius:99px;}
.sirati-rating-v2__filter-grid {display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:15px;}
.sirati-rating-v2__filter-grid label {display:grid;gap:7px;font-weight:700;font-size:12px;min-width:0;}
.sirati-rating-v2__filter-grid :is(input,select) {width:100%;min-width:0;box-sizing:border-box;min-height:44px;border:1px solid #c7d8cb;border-radius:10px;padding:9px 11px;font:inherit;font-weight:400;background:#fbfcfa;color:#193f2f;}
.sirati-rating-v2__filters>p {margin-bottom:0;color:#52715f;font-size:12px;}
.sirati-rating-v2__review-head {align-items:center;justify-content:space-between;}
.sirati-rating-v2__no-comment {color:#7b8d7d;font-style:italic;}
.sirati-rating-v2__notice,.sirati-rating-v2__empty {border:1px solid #dce8df;border-radius:14px;background:#fff;padding:22px;margin:18px 0;}
.sirati-rating-v2__notice button,.sirati-rating-v2__empty button {margin-inline-start:10px;min-height:42px;padding:9px 15px;border:1px solid #aac3b1;border-radius:10px;background:#edf5ee;color:#205d3d;cursor:pointer;}
.sirati-rating-v2 :is(button,input,select,a):focus-visible {outline:3px solid #bd8526;outline-offset:3px;}
.sirati-feedback-v2__previous {font-size:12px;line-height:1.7;padding:12px;border-radius:10px;background:#eaf5ed;color:#21533b;margin:0;}
}
@media(max-width:600px) {
.sirati-rating-v2 .sirati-rating-admin__stats {grid-template-columns:repeat(2,minmax(0,1fr));}
.sirati-rating-v2 .sirati-rating-admin__stats>div:last-child {grid-column:1/-1;}
.sirati-rating-v2__filter-grid {grid-template-columns:1fr;}
.sirati-rating-v2__bar-row {grid-template-columns:40px minmax(0,1fr) 76px;gap:8px;}
}
"""
css_path.write_text(css, encoding="utf-8")
print("PASS: feedback insights V2 and editable own review applied, no database schema changes")
