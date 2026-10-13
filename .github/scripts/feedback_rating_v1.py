"""Sirati V2 in-site feedback: no mailto or third-party form/tracker.

Home keeps the existing five-section hierarchy. The optional feedback form
saves one editable review per authenticated user to a separately reviewed,
RLS-protected Supabase table. Private owner dashboard is a separate page.
No backend schema is changed by this generator.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
component = root / "components" / "SiratiFeedbackRating.tsx"
dashboard = root / "app" / "feedback-dashboard" / "page.tsx"
home_path = root / "app" / "page.tsx"
css_path = root / "app" / "globals.css"
home = home_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")
anchor = '      <div className="container sirati-v13-support" id="support">'
if home.count(anchor) != 1 or "SiratiFeedbackRating" in home:
    raise RuntimeError("Feedback V2: expected unmodified V13 home")
if "/* Sirati native feedback v2 */" in css:
    raise RuntimeError("Feedback V2: duplicate stylesheet")

component.write_text(r"""'use client';

import { useState, type FormEvent } from 'react';
import { createClient } from '@/lib/supabase/client';
import { withBasePath } from '@/lib/basePath';

const areas = [
  { value: 'overall', label: 'التجربة العامة · Overall' },
  { value: 'templates', label: 'القوالب · Templates' },
  { value: 'editing', label: 'المحرر · Editor' },
  { value: 'pdf', label: 'تنزيل PDF' },
  { value: 'mobile', label: 'الموبايل · Mobile' },
] as const;
type Area = (typeof areas)[number]['value'];
type Status = 'idle' | 'saving' | 'signin' | 'saved' | 'error';

export default function SiratiFeedbackRating() {
  const [rating, setRating] = useState(0);
  const [area, setArea] = useState<Area>('overall');
  const [comment, setComment] = useState('');
  const [status, setStatus] = useState<Status>('idle');
  const resetNotice = () => setStatus('idle');

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (rating < 1 || rating > 5 || status === 'saving') return;
    setStatus('saving');
    try {
      const client = createClient();
      if (!client) { setStatus('error'); return; }
      const { data: auth, error: authError } = await client.auth.getUser();
      if (authError || !auth.user) { setStatus('signin'); return; }
      // Only these explicit fields are transmitted. Never send the CV,
      // document ID, current URL/query string, email or session token.
      const { error } = await client.from('sirati_site_feedback').upsert({
        user_id: auth.user.id,
        rating,
        category: area,
        comment: comment.trim(),
      }, { onConflict: 'user_id' });
      setStatus(error ? 'error' : 'saved');
    } catch {
      setStatus('error');
    }
  }

  return (
    <div className="container sirati-feedback-v2 no-print" id="feedback"
      role="region" aria-labelledby="feedback-heading">
      <div className="sirati-feedback-v2__intro">
        <span className="sirati-feedback-v2__eyebrow">YOUR VOICE · رأيك يهمنا</span>
        <h2 id="feedback-heading">How was your experience? <span>إيه رأيك في سيرتي؟</span></h2>
        <p>ساعدنا نحسّن تجربة إنشاء الـCV · Help us make Sirati better.</p>
      </div>
      <form className="sirati-feedback-v2__form" onSubmit={submit}>
        <fieldset className="sirati-feedback-v2__fieldset">
          <legend>قيّم تجربتك · Rate your experience</legend>
          <div className="sirati-feedback-v2__stars" role="group" aria-label="Rating · التقييم">
            {[1, 2, 3, 4, 5].map(value => (
              <button type="button" key={value}
                aria-label={value + ' of 5 stars · ' + value + ' من 5 نجوم'}
                aria-pressed={rating === value}
                className={value <= rating ? 'selected' : ''}
                onClick={() => { setRating(value); resetNotice(); }}>
                <span aria-hidden="true">★</span>
              </button>
            ))}
          </div>
          <p className="sirati-feedback-v2__helper" aria-live="polite">
            {rating ? rating + ' / 5' : 'اختار عدد النجوم · Choose stars'}
          </p>
        </fieldset>
        <label htmlFor="sirati-feedback-area">إيه الجزء اللي بتقيّمه؟ · What are you rating?</label>
        <select id="sirati-feedback-area" value={area}
          onChange={event => { setArea(event.target.value as Area); resetNotice(); }}>
          {areas.map(item => <option key={item.value} value={item.value}>{item.label}</option>)}
        </select>
        <label htmlFor="sirati-feedback-comment">احكيلنا رأيك (اختياري) · Optional comment</label>
        <textarea id="sirati-feedback-comment" dir="auto" rows={3}
          value={comment} maxLength={400}
          onChange={event => { setComment(event.target.value); resetNotice(); }}
          placeholder="إيه اللي عجبك، وإيه اللي محتاج يتطور؟" />
        <div className="sirati-feedback-v2__foot">
          <p>لا تكتب أي بيانات شخصية أو محتوى سيرتك الذاتية.
            <span> No personal details or CV data. Free account needed to submit.</span>
          </p>
          <button className="sirati-feedback-v2__submit" type="submit"
            disabled={!rating || status === 'saving'}>
            {status === 'saving' ? 'جاري الإرسال... · Sending...' : 'إرسال التقييم · Send feedback'}
          </button>
        </div>
        <div role="status" aria-live="polite" className="sirati-feedback-v2__status">
          {status === 'signin' && <>
            يلزم تسجيل الدخول لحفظ التقييم · Sign in to submit your review.
            {' '}<a href={withBasePath('/auth?next=/')}>تسجيل الدخول · Sign in</a>
          </>}
          {status === 'saved' && 'شكرًا! تم حفظ تقييمك بنجاح. يمكنك تعديله لاحقًا · Thank you! Your rating was saved.'}
          {status === 'error' && 'تعذر حفظ التقييم الآن. لم يتم تأكيد الإرسال؛ حاول لاحقًا · Could not save. Please retry.'}
        </div>
      </form>
    </div>
  );
}
""", encoding="utf-8")

dashboard.parent.mkdir(parents=True, exist_ok=True)
dashboard.write_text(r"""'use client';

import { useEffect, useState } from 'react';
import { createClient } from '@/lib/supabase/client';
import { withBasePath } from '@/lib/basePath';

type Review = {
  rating: number; category: string; comment: string; created_at: string;
};
const names: Record<string, string> = {
  overall: 'Overall · عام', templates: 'Templates · القوالب',
  editing: 'Editor · المحرر', pdf: 'PDF', mobile: 'Mobile · الموبايل',
};
export default function FeedbackDashboard() {
  const [reviews, setReviews] = useState<Review[] | null>(null);
  const [error, setError] = useState('');
  useEffect(() => {
    let alive = true;
    (async () => {
      const client = createClient();
      if (!client) throw Error('unavailable');
      const { data: auth, error: authError } = await client.auth.getUser();
      if (authError || !auth.user) throw Error('denied');
      // Cosmetic early check only. The table RLS is the actual admin boundary:
      // no client-side flag can grant access to any other user's review.
      if (auth.user.app_metadata?.sirati_feedback_admin !== true) throw Error('denied');
      const { data, error: queryError } = await client
        .from('sirati_site_feedback')
        .select('rating,category,comment,created_at')
        .order('created_at', { ascending: false }).limit(200);
      if (queryError) throw Error('denied');
      if (alive) setReviews((data || []) as Review[]);
    })().catch(() => { if (alive) setError('غير متاح إلا لمالك الموقع · Owner access required'); });
    return () => { alive = false; };
  }, []);
  const total = reviews?.length || 0;
  const average = total ? reviews!.reduce((sum, item) => sum + item.rating, 0) / total : 0;
  return (
    <main className="container sirati-rating-admin">
      <a href={withBasePath('/')}>← Sirati · الرئيسية</a>
      <h1>Visitor feedback · تقييمات الزوار</h1>
      <p>Private owner view · لوحة خاصة بالمالك · أحدث 200 تقييم فقط</p>
      {!error && reviews === null && <p role="status">جاري التحميل · Loading...</p>}
      {error && <p role="alert">{error}</p>}
      {reviews && <>
        <div className="sirati-rating-admin__stats">
          <div><span>Reviews shown · التقييمات المعروضة</span><strong>{total}</strong></div>
          <div><span>Average · المتوسط</span><strong>{average.toFixed(1)} / 5</strong></div>
        </div>
        <div className="sirati-rating-admin__list">
          {reviews.length === 0 && <p>لا توجد تقييمات حتى الآن · No feedback yet.</p>}
          {reviews.map((item, index) => (
            <article key={item.created_at + ':' + index}>
              <div><strong>{'★'.repeat(item.rating)}{'☆'.repeat(5 - item.rating)}</strong>
                <span>{names[item.category] || 'Overall'}</span></div>
              {item.comment && <p dir="auto">{item.comment}</p>}
              <time dateTime={item.created_at}>
                {new Date(item.created_at).toLocaleDateString('en-GB')}
              </time>
            </article>
          ))}
        </div>
        <p>These are voluntary ratings, not independently verified reviews.
           No emails, CVs or account identifiers are displayed.</p>
      </>}
    </main>
  );
}
""", encoding="utf-8")

home = "import SiratiFeedbackRating from '@/components/SiratiFeedbackRating';\n" + home
home = home.replace(anchor, "      <SiratiFeedbackRating />\n" + anchor, 1)
home_path.write_text(home, encoding="utf-8")

css += r"""

/* Sirati native feedback v2 — scoped screen-only, mobile-first and no overlays */
@media screen {
.sirati-feedback-v2 { max-width: 1120px; padding-top: 28px; padding-bottom: 26px;
  display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.12fr); gap: 26px;
  align-items: center; }
.sirati-feedback-v2__intro { padding: 14px 2px; }
.sirati-feedback-v2__eyebrow { font-size: 11px; font-weight: 750; letter-spacing: .12em; color:#277153; }
.sirati-feedback-v2__intro h2 { color: #152e26; font-size: clamp(24px, 3vw, 34px); line-height: 1.24; margin: 12px 0; }
.sirati-feedback-v2__intro h2 span { display:block; font-size:.77em; margin-top:8px; }
.sirati-feedback-v2__intro p { font-size:14px; color:#53695d; }
.sirati-feedback-v2__form { min-width: 0; display: grid; gap: 12px;
  padding: clamp(18px, 3vw, 26px); border:1px solid #dbe8e1; border-radius:20px;
  background:#fff; box-shadow:0 12px 32px #102f2312; }
.sirati-feedback-v2__fieldset { margin:0; border:0; padding:0; min-width:0; }
.sirati-feedback-v2__fieldset legend,.sirati-feedback-v2__form label { color:#1e4130; font-size:13px; font-weight:680; }
.sirati-feedback-v2__stars { display:flex; gap:6px; flex-wrap:wrap; margin:9px 0 4px; }
.sirati-feedback-v2__stars button { width:50px; height:48px; border:1px solid #dde4df;
  border-radius:11px; background:#f9faf9; color:#8c9c93; font-size:30px; line-height:1; cursor:pointer; }
.sirati-feedback-v2__stars button.selected { color:#c1830c; background:#fff8e8; border-color:#f0cf82; }
.sirati-feedback-v2__form textarea,.sirati-feedback-v2__form select {
  color:#172e23; background:#fff; padding:11px 13px; border:1px solid #bccdc2;
  border-radius:10px; font:inherit; width:100%; min-width:0; box-sizing:border-box; }
.sirati-feedback-v2__form textarea { resize:vertical; }
.sirati-feedback-v2__helper,.sirati-feedback-v2__foot p { margin:0; font-size:12px; color:#65796e; }
.sirati-feedback-v2__foot { display:flex; flex-wrap:wrap; gap:12px; justify-content:space-between; align-items:center; }
.sirati-feedback-v2__foot p { max-width:245px; line-height:1.55; }
.sirati-feedback-v2__foot p span { display:block; }
.sirati-feedback-v2__submit { border:0; border-radius:12px; padding:12px 16px; min-height:48px;
  background:#206e4c; color:#fff; font:inherit; font-weight:700; cursor:pointer; }
.sirati-feedback-v2__submit:disabled { opacity:.5; cursor:not-allowed; }
.sirati-feedback-v2__status { min-height:18px; font-size:12px; color:#1d6c4b; }
.sirati-feedback-v2__form :is(button,a,textarea,select):focus-visible { outline:3px solid #19885c; outline-offset:2px; }
.sirati-rating-admin { padding:28px 16px 60px; max-width:940px; min-height:65vh; }
.sirati-rating-admin h1 { margin:22px 0 5px; }
.sirati-rating-admin__stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:14px; margin:18px 0; }
.sirati-rating-admin__stats>div,.sirati-rating-admin__list article { border:1px solid #dce8df;
  border-radius:15px; padding:18px; background:#fff; }
.sirati-rating-admin__stats span { display:block; color:#53695d; font-size:13px; }
.sirati-rating-admin__stats strong { display:block; font-size:29px; margin-top:8px; }
.sirati-rating-admin__list { display:grid; gap:12px; }
.sirati-rating-admin__list article>div { display:flex; flex-wrap:wrap; gap:14px; }
.sirati-rating-admin__list article strong { color:#b47b12; }
.sirati-rating-admin__list article time { font-size:12px; color:#637269; }
@media (max-width:750px) { .sirati-feedback-v2 { grid-template-columns:1fr; gap:12px; } }
@media (max-width:360px) { .sirati-feedback-v2__stars button { width:45px; } }
}
"""
css_path.write_text(css, encoding="utf-8")
print("Applied in-site rating form and private owner dashboard; DB migration is separate.")
