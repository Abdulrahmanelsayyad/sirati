"""Smart CV V6 Pro Max: local job-ad relevance and draft editor on V5.

No persistence, API, authentication, PDF, payment or database changes.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
path=root/"components/PersonalSummaryPicker.tsx"
style=root/"app/globals.css"
s=path.read_text(encoding="utf-8")
def swap(old,new,label):
    global s
    if s.count(old)!=1:
        raise RuntimeError(f"V6 {label}: anchor count {s.count(old)}")
    s=s.replace(old,new,1)

anchor="\nexport default function PersonalSummaryPicker()"
helper=r"""
// Only match explicit job requirements against facts typed by the user.
// Job-ad terms MUST NEVER be treated as CV evidence by themselves.
const jobTerms = [
  'Excel','SAP','Power BI','SQL','Python','React','TypeScript','JavaScript','API',
  'financial reporting','budgeting','reconciliation','cost accounting','auditing',
  'inventory management','project management','customer service','Salesforce',
  'digital marketing','SEO','data analysis','risk management','communication',
  'team leadership','patient safety','triage','critical care','infection control',
  'patient assessment','clinical documentation','quality assurance'
];
function hasJobTerm(haystack: string, term: string) {
  // All terms above are safe literal words/phrases; no user regex is evaluated.
  return new RegExp('(?:^|[^\\p{L}\\p{N}])' + term + '(?=$|[^\\p{L}\\p{N}])','iu')
    .test(haystack);
}
function analyzeJobPosting(posting: string, skills: string, achievement: string) {
  if (!posting.trim()) return {matched:[] as string[], notInEvidence:[] as string[]};
  const terms=jobTerms.filter(t=>hasJobTerm(posting.slice(0,2000),t)).slice(0,10);
  const evidence=(skills+' '+achievement).slice(0,270);
  return {matched:terms.filter(t=>hasJobTerm(evidence,t)),
          notInEvidence:terms.filter(t=>!hasJobTerm(evidence,t))};
}
"""
swap(anchor,"\n"+helper+anchor,"helper")
swap("function makeSuggestions(job: string, lang: Lang, track: Track, level: Seniority, skills: string, evidence: string, targetRole: string) {",
"function makeSuggestions(job: string, lang: Lang, track: Track, level: Seniority, skills: string, evidence: string, targetRole: string, jobAd: string) {","signature")
swap("  const focus = lang === 'ar' ? track.focusAr : track.focusEn;",
"""  const focus = lang === 'ar' ? track.focusAr : track.focusEn;
  const supported = analyzeJobPosting(jobAd, skills, evidence).matched;
  const matchNote = supported.length
    ? (lang === 'ar' ? ' مهارات مدخلة ذات صلة بالإعلان: ' : ' User-listed skills relevant to the job ad: ') +
      supported.join(lang === 'ar' ? '، ' : ', ') + '.'
    : '';""","supported only")
swap("""role + ' (' + seniority + ')، مع اهتمام متخصص بـ' + focus + '.' +
        skillSentence + factSentence,""",
"""role + ' (' + seniority + ')، مع اهتمام متخصص بـ' + focus + '.' +
        skillSentence + factSentence + matchNote,""","Arabic ATS")
swap("""role + ' (' + seniority + ') focused on ' + focus + '.' +
      skillSentence + factSentence,""",
"""role + ' (' + seniority + ') focused on ' + focus + '.' +
      skillSentence + factSentence + matchNote,""","English ATS")
swap("  const [targetRole, setTargetRole] = useState('');",
"""  const [targetRole, setTargetRole] = useState('');
  const [jobAd, setJobAd] = useState('');
  const [editing, setEditing] = useState<{index:number; original:string; text:string} | null>(null);""","state")
swap("setTrackChoice('auto'); setLevelChoice('auto'); setSkills(''); setAchievement(''); setTargetRole('');",
"""setTrackChoice('auto'); setLevelChoice('auto'); setSkills(''); setAchievement(''); setTargetRole('');
          setJobAd(''); setEditing(null);""","clear sensitive transient state")
swap("""    makeSuggestions(role.trim(), lang, track, level, skills, achievement, targetRole),
    [role, lang, track, level, skills, achievement, targetRole]);""",
"""    makeSuggestions(role.trim(), lang, track, level, skills, achievement, targetRole, jobAd),
    [role, lang, track, level, skills, achievement, targetRole, jobAd]);
  const jobFit = useMemo(() => analyzeJobPosting(jobAd,skills,achievement),
    [jobAd,skills,achievement]);""","memo")
swap("    putSummary(target.current, value);\n    setOpen(false);",
"    putSummary(target.current, value);\n    setEditing(null);\n    setOpen(false);","reset edited on save")
swap("""          <details className="sirati-summary-pro-facts">""",
"""          <details className="sirati-summary-v6-job">
            <summary>{lang === 'ar' ? 'مقارنة إعلان الوظيفة (اختياري)' : 'Match a job description (optional)'}</summary>
            <p>{lang === 'ar'
              ? 'تتم المقارنة محليًا. متطلبات الإعلان ليست دليلًا على امتلاكك المهارات.'
              : 'Processed locally. Job requirements are not proof of your skills.'}</p>
            <textarea aria-label="Summary job description" rows={4} maxLength={2000}
              value={jobAd} onChange={event=>setJobAd(event.target.value)}
              placeholder={lang === 'ar' ? 'الصق إعلان الوظيفة هنا…' : 'Paste your target job posting…'} />
          </details>
          <details className="sirati-summary-pro-facts">""","job ad field")
swap("""        {options.length
          ? <div className="sirati-summary-choices">""",
"""        {jobAd.trim() && <div className="sirati-summary-v6-match" aria-live="polite">
          <strong>{lang === 'ar' ? 'الوظيفة مقابل البيانات المدخلة' : 'Job ad vs. your entered facts'}</strong>
          <span>{lang === 'ar' ? 'متطابقة مع بياناتك:' : 'Mentioned in your optional facts:'}</span>
          <b>{jobFit.matched.length ? jobFit.matched.join(', ') : (lang === 'ar' ? 'لا يوجد بعد' : 'None yet')}</b>
          <span>{lang === 'ar' ? 'غير مذكورة في البيانات الاختيارية:' : 'Not listed in your optional facts:'}</span>
          <b>{jobFit.notInEvidence.length ? jobFit.notInEvidence.join(', ') : (lang === 'ar' ? 'لا توجد مصطلحات أخرى' : 'No other detected terms')}</b>
          <small>{lang === 'ar' ? 'لا تُضاف المتطلبات تلقائيًا. ليست درجة ATS.'
          : 'Requirements are never inserted automatically. Not an ATS score.'}</small>
        </div>}
        {options.length
          ? <div className="sirati-summary-choices">""","transparent keyword insights")
swap("""              {options.map((text,i) =>
                <button type="button" key={i} className="sirati-summary-choice"
                  onClick={() => apply(text)} aria-label={t.choose + ' ' + (i+1)}>
                  <span className="sirati-summary-choice__style">{i+1}. {t.styles[i]}</span>
                  <span className="sirati-summary-choice__text">{text}</span>
                  <span className="sirati-summary-choice__action">{t.choose} →</span>
                </button>
              )}
            </div>""",
"""              {options.map((text,i) =>
                <div key={i} className="sirati-summary-v6-card">
                  <button type="button" className="sirati-summary-choice"
                    onClick={() => apply(text)} aria-label={t.choose + ' ' + (i+1)}>
                    <span className="sirati-summary-choice__style">{i+1}. {t.styles[i]}</span>
                    <span className="sirati-summary-choice__text">{text}</span>
                    <span className="sirati-summary-choice__action">{t.choose} →</span>
                  </button>
                  <button type="button" className="sirati-summary-v6-edit-btn"
                    onClick={() => setEditing({index:i,original:text,text})}>
                    {lang === 'ar' ? 'راجع وعدّل قبل الاختيار' : 'Customize before selecting'}
                  </button>
                </div>
              )}
            </div>""","card edit button")
swap("""            </div>
          : <p role="status">{t.empty}</p>}
        <small>{t.safety}""",
"""            </div>
          : <p role="status">{t.empty}</p>}
        {editing && options[editing.index] === editing.original && <div className="sirati-summary-v6-editor">
          <label htmlFor="sirati-summary-v6-edit">
            {lang === 'ar' ? 'حرّر الملخص قبل إضافته' : 'Edit the summary before inserting'}
          </label>
          <textarea id="sirati-summary-v6-edit" aria-label="Edit summary draft" rows={5}
            maxLength={1000} value={editing.text}
            onChange={event=>setEditing({...editing,text:event.target.value})} />
          <small>{editing.text.length}/1000 {lang === 'ar' ? 'حرف' : 'characters'}</small>
          <div className="sirati-summary-v6-editor-actions">
            <button type="button" disabled={!editing.text.trim()}
              onClick={() => apply(editing.text.trim())}>
              {lang === 'ar' ? 'استخدم الملخص المعدل' : 'Use edited summary'}</button>
            <button type="button" onClick={() => setEditing(null)}>
              {lang === 'ar' ? 'إلغاء' : 'Cancel editing'}</button>
          </div>
        </div>}
        <small>{t.safety}""","in-place editing and consent")
path.write_text(s,encoding="utf-8")
css=style.read_text(encoding="utf-8")
if "/* Smart CV Pro V6 Max */" in css:
    raise RuntimeError("Already applied")
css+=r"""
/* Smart CV Pro V6 Max */
@media screen {
  .sirati-summary-v6-job {grid-column:1/-1;border:1px solid #dbe8de;border-radius:10px;padding:10px}
  .sirati-summary-v6-job summary {font-size:12px;font-weight:750;color:#20543d;cursor:pointer}
  .sirati-summary-v6-job p {margin:8px 0}
  .sirati-summary-v6-job textarea,.sirati-summary-v6-editor textarea {
    display:block;box-sizing:border-box;width:100%;min-width:0;min-height:96px;resize:vertical;
    border:1px solid #bed4c5;border-radius:9px;background:#fff;color:#173e2a;
    padding:10px;font:inherit;line-height:1.5;
  }
  .sirati-summary-v6-match {display:grid;gap:5px;padding:12px;border:1px solid #d1e1d5;
    border-radius:12px;background:#f1f8f2;overflow-wrap:anywhere;font-size:12px;color:#264c38}
  .sirati-summary-v6-match span {color:#557565}
  .sirati-summary-v6-match strong {font-size:13px}
  .sirati-summary-v6-card {min-width:0;border:1px solid #e0ebe3;border-radius:12px;overflow:hidden}
  .sirati-summary-v6-card .sirati-summary-choice {border:0;border-radius:0}
  .sirati-summary-v6-edit-btn {display:block;width:100%;min-height:44px;padding:8px 12px;
    border:0;border-top:1px solid #d6e6dc;background:#edf5ef;color:#1e523a;text-align:start;
    font:inherit;font-size:12px;font-weight:750;cursor:pointer}
  .sirati-summary-v6-editor {display:grid;gap:8px;padding:12px;min-width:0;border:1px solid #c2d9c7;
    border-radius:12px;background:#f7fbf8}
  .sirati-summary-v6-editor label {font-weight:750}
  .sirati-summary-v6-editor-actions {display:flex;flex-wrap:wrap;gap:8px}
  .sirati-summary-v6-editor-actions button {min-height:44px;padding:8px 12px;
    border:1px solid #bbd1c2;border-radius:9px;background:#fff;color:#184632;cursor:pointer;font-weight:750}
  .sirati-summary-v6-editor-actions button:first-child {background:#215a40;color:#fff}
  .sirati-summary-v6-editor-actions button:disabled {opacity:.45;cursor:not-allowed}
  .sirati-summary-v6-editor textarea:focus-visible,.sirati-summary-v6-job textarea:focus-visible,
  .sirati-summary-v6-edit-btn:focus-visible {outline:3px solid #80b995;outline-offset:2px}
}
@media screen and (max-width:390px) {
  .sirati-summary-v6-match,.sirati-summary-v6-editor {padding:9px}
  .sirati-summary-v6-editor-actions button {flex:1 1 130px}
}
"""
style.write_text(css,encoding="utf-8")
print("PASS: V6 privacy-first job match and editable summaries.")
