"""Optional bilingual feedback UI using the existing support mail address.

This is a zero-backend, mailto-based feedback request. Ratings are NOT saved to
Supabase, sent automatically, counted as testimonials, or exposed publicly.
Only rating + an optional bounded comment are placed into an email draft.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
component = root / "components" / "SiratiFeedbackRating.tsx"
home_path = root / "app" / "page.tsx"
css_path = root / "app" / "globals.css"

home = home_path.read_text(encoding="utf-8")
css = css_path.read_text(encoding="utf-8")

support_anchor = '      <div className="container sirati-v13-support" id="support">'
if home.count(support_anchor) != 1:
    raise RuntimeError("Feedback: V13 homepage support anchor missing or duplicated")
if "SiratiFeedbackRating" in home or "/* Sirati voluntary feedback */" in css:
    raise RuntimeError("Feedback: patch already applied or conflicting")

component.write_text(r"""'use client';

import { useState } from 'react';

const FEEDBACK_EMAIL = 'sirati-support@agentmail.to';

export default function SiratiFeedbackRating() {
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');
  const [prepared, setPrepared] = useState(false);

  // Intentionally never include a CV, user ID, page query, or session data.
  // mailto creates a draft: the visitor must choose Send in their own app.
  const subject = 'Sirati CV website rating: ' + rating + '/5';
  const message = 'Website rating: ' + rating + '/5\n' +
    'Optional feedback:\n' + (comment.trim() || '(No comment)');
  const mailto = rating > 0
    ? 'mailto:' + FEEDBACK_EMAIL + '?subject=' + encodeURIComponent(subject) +
      '&body=' + encodeURIComponent(message)
    : undefined;

  return (
    <div className="container sirati-feedback no-print" id="feedback"
      role="region" aria-label="Website feedback · تقييم الموقع">
      <details className="sirati-feedback__details">
        <summary>Rate your experience · قيّم تجربتك مع سيرتي</summary>
        <div className="sirati-feedback__content">
          <p>Used Sirati? Tell us what worked and what needs improving.</p>
          <fieldset className="sirati-feedback__fieldset">
            <legend>Choose 1 to 5 stars · اختر من نجمة إلى 5 نجوم</legend>
            <div className="sirati-feedback__stars">
              {[1, 2, 3, 4, 5].map(value => (
                <button type="button" key={value}
                  aria-label={value + ' of 5 stars · ' + value + ' من 5 نجوم'}
                  aria-pressed={rating === value}
                  style={{ color: value <= rating ? '#a56800' : '#718096' }}
                  onClick={() => { setRating(value === rating ? 0 : value); setPrepared(false); }}>
                  <span aria-hidden="true">★</span>
                </button>
              ))}
            </div>
          </fieldset>
          <label htmlFor="sirati-feedback-comment">
            Optional feedback · تعليق اختياري
          </label>
          <textarea id="sirati-feedback-comment" value={comment} maxLength={400}
            onChange={event => { setComment(event.target.value); setPrepared(false); }}
            dir="auto" rows={3} placeholder="What should we improve? · إيه اللي محتاج يتحسن؟" />
          <p className="sirati-feedback__privacy">
            Please do not include your CV or personal information. · لا تكتب بياناتك الشخصية أو السيرة الذاتية.
          </p>
          {mailto ? (
            <a className="btn btn-secondary sirati-feedback__action" href={mailto}
              onClick={() => setPrepared(true)}>
              Open email draft · افتح رسالة التقييم
            </a>
          ) : (
            <button className="btn btn-secondary sirati-feedback__action"
              type="button" disabled>Choose a star rating · اختر التقييم</button>
          )}
          <p className="sirati-feedback__status" role="status">
            {prepared
              ? 'Finish by pressing Send in your email app. · اضغط إرسال من تطبيق البريد لإتمام التقييم.'
              : 'Opens your email app; nothing is sent or saved automatically. · لن يتم إرسال أو حفظ التقييم تلقائيًا.'}
          </p>
        </div>
      </details>
    </div>
  );
}
""", encoding="utf-8")

# App Router homepage is a server component; import the interactive rating client
# component there, without changing the CV Builder, login, or PDF action.
home = "import SiratiFeedbackRating from '@/components/SiratiFeedbackRating';\n" + home
home = home.replace(support_anchor, "      <SiratiFeedbackRating />\n" + support_anchor, 1)
home_path.write_text(home, encoding="utf-8")

css += r"""

/* Sirati voluntary feedback: compact, accessible, no overlays, no tracking. */
.sirati-feedback { padding-top: 12px; padding-bottom: 16px; }
.sirati-feedback__details {
  border: 1px solid #d7e1dc;
  border-radius: 14px;
  background: #fafcfb;
  color: #223229;
  overflow: hidden;
}
.sirati-feedback__details summary {
  cursor: pointer;
  padding: 14px 18px;
  font-weight: 650;
  min-height: 48px;
}
.sirati-feedback__details summary:focus-visible,
.sirati-feedback__stars button:focus-visible,
.sirati-feedback__action:focus-visible {
  outline: 3px solid #167d56;
  outline-offset: 2px;
}
.sirati-feedback__content {
  padding: 4px 18px 18px;
  max-width: 620px;
  display: grid;
  gap: 10px;
}
.sirati-feedback__content p { margin: 0; }
.sirati-feedback__fieldset { padding: 0; margin: 0; border: 0; }
.sirati-feedback__fieldset legend,
.sirati-feedback__content label { font-size: 14px; font-weight: 600; }
.sirati-feedback__stars { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 8px; }
.sirati-feedback__stars button {
  background: #fff;
  border: 1px solid #ccd8d1;
  border-radius: 8px;
  cursor: pointer;
  font-size: 30px;
  line-height: 1;
  width: 48px;
  height: 48px;
}
.sirati-feedback__stars button[aria-pressed="true"] { border-color: #a56800; background: #fff7e5; }
.sirati-feedback__content textarea {
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
  padding: 12px;
  border: 1px solid #aebdb5;
  border-radius: 8px;
  background: #fff;
  color: #172a20;
  font: inherit;
  resize: vertical;
}
.sirati-feedback__privacy, .sirati-feedback__status {
  font-size: 12px;
  color: #516459;
  line-height: 1.6;
}
.sirati-feedback__action { width: fit-content; max-width: 100%; }
.sirati-feedback__action:disabled { opacity: .65; cursor: not-allowed; }
@media (max-width: 420px) {
  .sirati-feedback__content { padding-inline: 12px; }
  .sirati-feedback__details summary { padding-inline: 12px; }
  .sirati-feedback__stars { justify-content: flex-start; }
}
"""
css_path.write_text(css, encoding="utf-8")
print("Applied optional, email-draft-based website feedback rating.")
