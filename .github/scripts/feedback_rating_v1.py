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

  const feeling = rating > 0 ? [
    '',
    'محتاجين نتحسّن · Needs improvement',
    'فيه حاجات محتاجة تطوير · Could be better',
    'تجربة جيدة · Good',
    'تجربة رائعة · Great',
    'تجربة ممتازة! · Excellent!'
  ][rating] : 'اختار تقييمك · Choose your rating';

  return (
    <div className="container sirati-feedback-v2 no-print" id="feedback"
      role="region" aria-labelledby="feedback-heading">
      <div className="sirati-feedback-v2__intro">
        <div className="sirati-feedback-v2__eyebrow">
          <span aria-hidden="true">✦</span> YOUR VOICE MATTERS
          <span lang="ar">رأيك يهمنا</span>
        </div>
        <h2 id="feedback-heading">
          <span lang="ar" dir="rtl">إيه رأيك في تجربتك مع سيرتي؟</span>
          <span lang="en">How was your experience?</span>
        </h2>
        <p lang="ar" dir="rtl" className="sirati-feedback-v2__intro-copy">
          بنطوّر سيرتي خطوة بخطوة. تقييمك الصادق بيساعدنا نخلّي إنشاء الـCV أسهل وأفضل.
        </p>
        <p className="sirati-feedback-v2__intro-copy" lang="en">
          Your honest feedback helps us build a better CV experience.
        </p>
        <div className="sirati-feedback-v2__signature">
          <span className="sirati-feedback-v2__signature-mark" aria-hidden="true">★</span>
          <span><strong>Simple. Thoughtful. Better.</strong>
            <small>Every voice shapes Sirati · كل رأي بيصنع فرق</small>
          </span>
        </div>
      </div>
      <form className="sirati-feedback-v2__form" onSubmit={submit}>
        <div className="sirati-feedback-v2__form-head">
          <strong>شاركنا رأيك <span lang="en">· Share your feedback</span></strong>
          <span className="sirati-feedback-v2__form-head-icon" aria-hidden="true">✳</span>
        </div>
        <fieldset className="sirati-feedback-v2__fieldset">
          <legend><span className="sirati-feedback-v2__step" aria-hidden="true">01</span>
            قيّم تجربتك <span lang="en">· Rate your experience</span>
          </legend>
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
          <p className={'sirati-feedback-v2__helper' + (rating ? ' is-rated' : '')}
            aria-live="polite">
            <span>{feeling}</span>
            {rating > 0 && <strong dir="ltr">{rating} / 5</strong>}
          </p>
        </fieldset>
        <div className="sirati-feedback-v2__category">
          <div className="sirati-feedback-v2__label" id="sirati-feedback-area-label">
            <span className="sirati-feedback-v2__step" aria-hidden="true">02</span>
            إيه الجزء اللي بتقيّمه؟ <span lang="en">· Which part?</span>
          </div>
          <div className="sirati-feedback-v2__chips" role="group"
            aria-labelledby="sirati-feedback-area-label">
            {areas.map(item => (
              <button type="button" key={item.value}
                className={area === item.value ? 'selected' : ''}
                aria-pressed={area === item.value}
                onClick={() => { setArea(item.value); resetNotice(); }}>
                {item.label}
              </button>
            ))}
          </div>
        </div>
        <div className="sirati-feedback-v2__comment-field">
          <label htmlFor="sirati-feedback-comment">
            <span className="sirati-feedback-v2__step" aria-hidden="true">03</span>
            اكتب رأيك <span lang="en">· Tell us more</span>
            <span className="sirati-feedback-v2__optional">اختياري · Optional</span>
          </label>
          <textarea id="sirati-feedback-comment" dir="auto" rows={3}
            value={comment} maxLength={400}
            onChange={event => { setComment(event.target.value); resetNotice(); }}
            placeholder="إيه اللي عجبك؟ وإيه اللي نقدر نحسّنه؟ · What could we improve?" />
          <div className="sirati-feedback-v2__count">
            <span>لا تكتب بيانات شخصية أو محتوى الـCV · No personal data</span>
            <span dir="ltr">{comment.length} / 400</span>
          </div>
        </div>
        <button className="sirati-feedback-v2__submit" type="submit"
          disabled={!rating || status === 'saving'} aria-busy={status === 'saving'}>
          <span aria-hidden="true">{status === 'saving' ? '◌' : '↗'}</span>
          {status === 'saving' ? 'جاري الإرسال · Sending...' : 'إرسال التقييم · Send feedback'}
        </button>
        <p className="sirati-feedback-v2__account-note">
          يتطلب الإرسال حسابًا مجانيًا · A free account is required to submit
        </p>
        {status !== 'idle' && <div role="status" aria-live="polite"
          className={'sirati-feedback-v2__status is-' + status}>
          {status === 'signin' && <>
            <span className="sirati-feedback-v2__status-icon" aria-hidden="true">↗</span>
            <span>سجّل دخولك لحفظ التقييم · Sign in to submit.
              {' '}<a href={withBasePath('/auth?next=/')}>تسجيل الدخول · Sign in</a>
            </span>
          </>}
          {status === 'saved' && <>
            <span className="sirati-feedback-v2__status-icon" aria-hidden="true">✓</span>
            <span><strong>شكرًا لرأيك! · Thank you!</strong>
              <small>تم حفظ تقييمك بنجاح، ويمكنك تعديله لاحقًا · Your rating was saved.</small>
            </span>
          </>}
          {status === 'error' && <>
            <span className="sirati-feedback-v2__status-icon" aria-hidden="true">!</span>
            <span>تعذر حفظ التقييم الآن، حاول مرة تانية · Could not save. Please retry.</span>
          </>}
        </div>}
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

/* Sirati native feedback v3: compact editorial layout + thoughtful mobile UX.
   No overlays, no external assets, no data/permissions changes. */
@media screen {
.sirati-feedback-v2 {
  --feedback-forest: #174938;
  --feedback-deep: #143a2e;
  --feedback-muted: #587163;
  --feedback-amber: #bd8526;
  position: relative; isolation: isolate;
  display: grid; grid-template-columns: minmax(0, .90fr) minmax(0, 1.12fr);
  align-items: center; gap: clamp(20px, 4vw, 64px);
  box-sizing: border-box; max-width: 1120px;
  padding: clamp(20px, 4vw, 52px);
  margin-top: 24px; margin-bottom: 24px;
  border: 1px solid #dfe9df; border-radius: 26px;
  background: linear-gradient(130deg, #e8f4ec 0%, #f3f8f2 48%, #fffdf7 100%);
  box-shadow: 0 12px 48px #173f2910;
  overflow: hidden; color: #173a2d;
}
.sirati-feedback-v2::before {
  content:""; position:absolute; z-index:-1;
  width: 270px; height:270px; border-radius: 50%;
  left:-90px; top:-110px; background: #bedec33b;
  pointer-events:none;
}
.sirati-feedback-v2__intro { padding: clamp(0px, 1.3vw, 18px); min-width: 0; }
.sirati-feedback-v2__eyebrow {
  display:inline-flex; align-items:center; flex-wrap:wrap;
  gap:8px; letter-spacing:.06em; font-size:11px; font-weight:800;
  color:#2f7156; text-transform:uppercase;
}
.sirati-feedback-v2__eyebrow span:last-child { letter-spacing:normal; text-transform:none; }
.sirati-feedback-v2__eyebrow span:first-child { font-size:18px; color:#bd8526; }
.sirati-feedback-v2__intro h2 {
  font-size:clamp(29px,3.6vw,42px); font-weight:800; line-height:1.25;
  color:var(--feedback-deep); letter-spacing:-.025em;
  margin:18px 0 18px; overflow-wrap:anywhere;
}
.sirati-feedback-v2__intro h2 span { display:block; }
.sirati-feedback-v2__intro h2 span[lang=en] {
  font-size:.65em; font-weight:560; line-height:1.4;
  letter-spacing:-.015em; margin-top:9px; color:#4c685b;
}
.sirati-feedback-v2__intro-copy {
  color:#4a685b; line-height:1.85; font-size:14px; margin:0 0 9px;
  max-width:360px;
}
.sirati-feedback-v2__intro-copy[lang=en] { font-size:13px; }
.sirati-feedback-v2__signature {
  display:flex; align-items:center; gap:13px;
  margin-top:32px; padding-top:22px; border-top:1px solid #bfcfc2;
}
.sirati-feedback-v2__signature-mark {
  display:grid;place-items:center;flex-shrink:0;
  width:48px;height:48px;border-radius:15px;
  background:#fff8e8;color:#bd8526;font-size:25px;border:1px solid #f0dbac;
}
.sirati-feedback-v2__signature strong {display:block;font-size:13px;color:#244d3b}
.sirati-feedback-v2__signature small {display:block;color:#557265;font-size:11px;margin-top:5px;line-height:1.5}
.sirati-feedback-v2__form {
  display:grid; gap:17px; min-width:0;
  box-sizing:border-box; padding:clamp(18px,3vw,32px);
  border:1px solid #e0e9e2; border-radius:22px;
  background:#fff; box-shadow:0 17px 42px #153f2517;
}
.sirati-feedback-v2__form-head {display:flex;align-items:center;justify-content:space-between;gap:12px;
  padding-bottom:15px;border-bottom:1px solid #edf1ec;color:#204b38;font-size:16px;line-height:1.5}
.sirati-feedback-v2__form-head span[lang=en] {font-size:12px;font-weight:500;color:#648072}
.sirati-feedback-v2__form-head-icon {font-size:25px;color:#b88732}
.sirati-feedback-v2__fieldset {border:0;padding:0;margin:0;min-width:0}
.sirati-feedback-v2__fieldset legend, .sirati-feedback-v2__label,
.sirati-feedback-v2__comment-field label {
  font-size:13px;line-height:1.55;color:#254737;font-weight:740;
}
.sirati-feedback-v2__fieldset legend span[lang=en],
.sirati-feedback-v2__label span[lang=en],
.sirati-feedback-v2__comment-field label span[lang=en] {font-size:12px;font-weight:500;color:#607466}
.sirati-feedback-v2__step {
  display:inline-flex;align-items:center;justify-content:center;
  width:25px;height:25px;border-radius:8px;margin-inline-end:7px;
  background:#edf5ef;color:#2c6b4f;font:700 10px/1 system-ui;
}
.sirati-feedback-v2__stars {
  display:flex;flex-wrap:wrap;gap:7px;margin-top:12px;direction:ltr;
}
.sirati-feedback-v2__stars button {
  display:grid;place-items:center; flex:0 0 49px;
  width:49px;height:50px;line-height:1;
  border-radius:13px;border:1px solid #e1e9e2;
  color:#aebcb2;background:#f7f9f7;
  font:32px/1 system-ui;cursor:pointer;
  transition:background .18s ease,color .18s ease,border-color .18s ease,transform .18s ease;
}
.sirati-feedback-v2__stars button.selected {
  background:#fff7e5;color:var(--feedback-amber);border-color:#edd394;
}
@media(hover:hover) {
  .sirati-feedback-v2__stars button:hover {transform:translateY(-3px);color:#ad7b1d;border-color:#e8cb88;background:#fff8e9}
  .sirati-feedback-v2__chips button:hover {border-color:#719e87;background:#f1f7f2}
  .sirati-feedback-v2__submit:not(:disabled):hover {background:#246d4e;transform:translateY(-1px)}
}
.sirati-feedback-v2__helper {
  min-height:22px;display:flex;align-items:center;flex-wrap:wrap;justify-content:space-between;gap:8px;
  color:#6c806f;font-size:12px;margin:7px 0 0;
}
.sirati-feedback-v2__helper.is-rated {color:#91630f}
.sirati-feedback-v2__helper strong {font:800 12px/1.2 system-ui;white-space:nowrap}
.sirati-feedback-v2__category {display:grid;gap:11px}
.sirati-feedback-v2__chips {display:flex;flex-wrap:wrap;gap:8px}
.sirati-feedback-v2__chips button {
  min-height:42px;max-width:100%;box-sizing:border-box;
  padding:9px 13px;border:1px solid #dce6de;border-radius:999px;
  background:#f8faf8;color:#476252;font-family:inherit;font-size:12px;font-weight:600;line-height:1.35;
  cursor:pointer;transition:background .18s,border-color .18s,color .18s;
}
.sirati-feedback-v2__chips button.selected {
  background:#eaf5ed;color:#19543b;border-color:#9bc4a9;box-shadow:inset 0 0 0 1px #a8d0b2;
}
.sirati-feedback-v2__comment-field {display:grid;gap:10px}
.sirati-feedback-v2__comment-field label {display:flex;align-items:center;flex-wrap:wrap;gap:3px}
.sirati-feedback-v2__optional {
  margin-inline-start:auto;background:#f3f5f2;border-radius:6px;
  color:#63776b;padding:3px 7px;font-size:11px;font-weight:500;
}
.sirati-feedback-v2__comment-field textarea {
  display:block;width:100%;box-sizing:border-box;min-width:0;
  min-height:92px;padding:13px 14px;resize:vertical;
  background:#fbfcfa;color:#233b2d;border:1px solid #d8e3d9;
  border-radius:13px;font:inherit;font-size:13px;line-height:1.7;
}
.sirati-feedback-v2__comment-field textarea::placeholder {color:#8a9e90}
.sirati-feedback-v2__count {
  display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;
  color:#788b7c;font-size:11px;line-height:1.5;
}
.sirati-feedback-v2__count span:last-child {font-variant-numeric:tabular-nums}
.sirati-feedback-v2__submit {
  display:flex;align-items:center;justify-content:center;gap:11px;
  width:100%;min-height:50px;padding:12px 16px;border:0;border-radius:13px;
  background:var(--feedback-forest);color:white;
  font-family:inherit;font-size:14px;font-weight:750;line-height:1.4;cursor:pointer;
  transition:transform .18s ease,background .18s ease;box-shadow:0 6px 14px #1749381b;
}
.sirati-feedback-v2__submit span {font:20px/1 system-ui}
.sirati-feedback-v2__submit:disabled {cursor:not-allowed;opacity:.5;box-shadow:none}
.sirati-feedback-v2__account-note {font-size:11px;color:#728477;text-align:center;margin:-10px 0 0}
.sirati-feedback-v2__status {
  display:flex;align-items:flex-start;gap:12px;
  border-radius:13px;padding:13px;font-size:13px;line-height:1.65;
  background:#f0f7f0;border:1px solid #cee2d0;color:#21583b;
}
.sirati-feedback-v2__status.is-signin {background:#f3f7f5}
.sirati-feedback-v2__status.is-error {background:#fff6f2;border-color:#f0d2c3;color:#9b4632}
.sirati-feedback-v2__status-icon {
  flex:0 0 25px;width:25px;height:25px;display:grid;place-items:center;
  border-radius:50%;background:#d5e9d7;font:750 16px/1 system-ui;
}
.sirati-feedback-v2__status.is-error .sirati-feedback-v2__status-icon {background:#ffe5d8}
.sirati-feedback-v2__status strong {display:block}
.sirati-feedback-v2__status small {display:block;font-size:12px;margin-top:3px}
.sirati-feedback-v2__status a {color:#11583b;font-weight:750;text-decoration:underline}
.sirati-feedback-v2 :is(button,textarea,a):focus-visible {
  outline:3px solid #168457;outline-offset:3px;
}
.sirati-rating-admin {padding:28px 16px 60px;max-width:940px;min-height:65vh}
.sirati-rating-admin h1 {margin:22px 0 5px}
.sirati-rating-admin__stats {display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:18px 0}
.sirati-rating-admin__stats>div,.sirati-rating-admin__list article {border:1px solid #dce8df;border-radius:15px;padding:18px;background:#fff}
.sirati-rating-admin__stats span {display:block;color:#53695d;font-size:13px}
.sirati-rating-admin__stats strong {display:block;font-size:29px;margin-top:8px}
.sirati-rating-admin__list {display:grid;gap:12px}
.sirati-rating-admin__list article>div {display:flex;flex-wrap:wrap;gap:14px}
.sirati-rating-admin__list article strong {color:#b47b12}
.sirati-rating-admin__list article time {font-size:12px;color:#637269}
@media(max-width:800px) {
  .sirati-feedback-v2 {grid-template-columns:minmax(0,1fr);gap:18px;padding:clamp(15px,4vw,28px);border-radius:21px}
  .sirati-feedback-v2__intro {padding:6px 3px 0}
  .sirati-feedback-v2__intro h2 {font-size:clamp(25px,6vw,32px);margin:9px 0}
  .sirati-feedback-v2__intro-copy {margin:0 0 5px;max-width:none}
  .sirati-feedback-v2__signature {display:none}
  .sirati-feedback-v2__form {padding:clamp(15px,4vw,24px)}
}
@media(max-width:420px) {
  .sirati-feedback-v2 {gap:14px;border-radius:17px}
  .sirati-feedback-v2__form {gap:14px;border-radius:16px}
  .sirati-feedback-v2__stars {gap:5px}
  .sirati-feedback-v2__stars button {flex-basis:46px;width:46px;height:48px}
  .sirati-feedback-v2__chips {gap:6px}
  .sirati-feedback-v2__chips button {padding:9px 10px;font-size:11px;min-height:44px}
}
@media(max-width:340px) {
  .sirati-feedback-v2__stars button {flex-basis:39px;width:39px;height:46px}
}
@media(prefers-reduced-motion:reduce) {
  .sirati-feedback-v2__stars button,.sirati-feedback-v2__chips button,.sirati-feedback-v2__submit {transition:none}
  .sirati-feedback-v2__stars button:hover,.sirati-feedback-v2__submit:hover {transform:none}
}
}
"""
css_path.write_text(css, encoding="utf-8")
print("Applied in-site rating form and private owner dashboard; DB migration is separate.")

# Keep owner-only navigation adjacent to the existing feedback dashboard generator.
# This does not change the global reconstruction script or the PDF-only release scope.
import subprocess
subprocess.run([sys.executable, str(Path(__file__).with_name('owner_feedback_menu.py')), str(root)], check=True)

# Feedback V2 UI/insights only. Keep the protected PDF build entrypoint unchanged.
subprocess.run([sys.executable, str(Path(__file__).with_name('feedback_dashboard_v2.py')), str(root)], check=True)
