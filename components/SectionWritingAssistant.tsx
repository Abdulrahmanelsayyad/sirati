'use client';
import { useState } from 'react';

// Deliberately narrow edits: never infer seniority, outcomes, skills or numbers.
export function improveSection(text: string, experience: boolean) {
  return text.split(/\r?\n/).map(line => {
    let result = line.trim().replace(/[\t ]+/g, ' ');
    if (experience) result = result.replace(/^[•●▪]\s+/, '');
    return result
      .replace(/^I am responsible for\s+/i, 'Responsible for ')
      .replace(/^I was responsible for\s+/i, 'Was responsible for ')
      .replace(/^I have experience (in|with)\s+/i, 'Experience $1 ')
      .replace(/^My responsibilities include\s+/i, 'Responsibilities include ')
      .replace(/^I (manage|coordinate|prepare|maintain|support|monitor|assist|document|review|develop|deliver)\b/i,
        (_, verb: string) => verb[0].toUpperCase() + verb.slice(1));
  }).join('\n').trim();
}

type Props = { value: string; experience?: boolean; language: 'en'|'ar';
  onApply: (expected: string, replacement: string) => void };
export default function SectionWritingAssistant({value, experience = false, language, onApply}: Props) {
  const [review, setReview] = useState<{before: string; after: string} | null>(null);
  const [last, setLast] = useState<{before: string; after: string} | null>(null);
  const [confirmed, setConfirmed] = useState(false);
  const ar = language === 'ar';
  const stale = !!review && review.before !== value;
  const button = {minHeight: 44, padding: '8px 14px', borderRadius: 8, border: '1px solid #cbd5e1', background: '#fff', color: '#0f172a', cursor: 'pointer'};
  return <div dir={ar ? 'rtl' : 'ltr'} style={{marginTop: 10, padding: 12, border: '1px solid #cbd5e1', borderRadius: 12, background: '#f8fafc', minWidth: 0}}>
    <button type="button" style={button} disabled={!value.trim()} onClick={() => {
      setReview({before: value, after: improveSection(value, experience)}); setConfirmed(false);
    }}>{ar ? 'تحسين هذا القسم' : 'Improve this section'}</button>
    <p style={{fontSize: 13}}>{ar ? 'مساعد محلي مجاني بقواعد محددة؛ ليس ذكاءً اصطناعياً توليدياً. لا يرسل النص للخارج.' : 'Free local writing helper. Uses limited rules, not generative AI. No text is sent to an AI service.'}</p>
    {review && <div>
      <strong>{ar ? 'النص الحالي عند بدء المراجعة' : 'Original text'}</strong>
      <p style={{whiteSpace: 'pre-wrap', overflowWrap: 'anywhere', maxHeight: 180, overflowY: 'auto'}}>{review.before}</p>
      <label style={{display: 'block'}}>{ar ? 'الاقتراح — قابل للتعديل' : 'Suggested text — edit before applying'}
        <textarea rows={5} value={review.after} style={{width: '100%', boxSizing: 'border-box', resize: 'vertical'}} onChange={e => {setReview({...review, after: e.target.value}); setConfirmed(false);}} />
      </label>
      {review.after === review.before && <p role="status">{ar ? 'لا توجد تعديلات تلقائية مفيدة. يمكنك تعديل النص أعلاه.' : 'No useful automatic edits found. You can edit the text above.'}</p>}
      <p>{experience
        ? (ar ? 'وضّح الإجراء الذي نفذته والأداة أو السياق والنتيجة إن كانت موثقة.' : 'Name the action you performed, the tool or context, and a result only if you can verify it.')
        : (ar ? 'اذكر تخصصك وخبرتك الفعلية ومهاراتك المرتبطة بالوظيفة المستهدفة.' : 'Include your actual specialization, relevant experience and skills for your target role.')}</p>
      {stale && <p role="alert">{ar ? 'تغير النص الأصلي. اضغط تحسين هذا القسم لبدء مراجعة جديدة.' : 'The original text changed. Click Improve this section to start a fresh review.'}</p>}
      <label style={{display: 'flex', gap: 8, alignItems: 'center', minHeight: 44}}><input type="checkbox" checked={confirmed} onChange={e => setConfirmed(e.target.checked)} style={{width: 20, height: 20}} />{ar ? 'راجعت النص ويعبّر عن خبرتي الحقيقية.' : 'I reviewed this text and it reflects my actual experience.'}</label>
      <div style={{display: 'flex', flexWrap: 'wrap', gap: 8}}>
        <button type="button" style={button} disabled={stale || !confirmed || !review.after.trim() || review.after === review.before} onClick={() => {
          if (stale || !confirmed || !review.after.trim()) return;
          onApply(review.before, review.after); setLast(review); setReview(null); setConfirmed(false);
        }}>{ar ? 'تطبيق' : 'Apply'}</button>
        <button type="button" style={button} onClick={() => {setReview(null); setConfirmed(false);}}>{ar ? 'إلغاء' : 'Cancel'}</button>
      </div>
    </div>}
    {last && <p><button type="button" style={button} disabled={value !== last.after} onClick={() => {
      if (value !== last.after) return;
      onApply(last.after, last.before); setLast(null); setReview(null);
    }}>{ar ? 'تراجع عن التحسين' : 'Undo improvement'}</button>
    {value !== last.after && <span role="status">{ar ? ' تم تعطيل التراجع لحماية تعديلاتك اللاحقة.' : ' Undo disabled to preserve your later edits.'}</span>}</p>}
  </div>;
}
