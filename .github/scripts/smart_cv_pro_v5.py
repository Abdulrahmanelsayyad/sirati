"""Smart CV Pro V5: three distinct, evidence-labelled and job-targeted CV summaries.

UI-only patch on V4's generated picker. Uses only current user-entered data,
never guesses years, skills, credentials or numerical impact.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
p = root / "components/PersonalSummaryPicker.tsx"
css = root / "app/globals.css"
s = p.read_text(encoding="utf-8")

def swap(before, after, label):
    global s
    count = s.count(before)
    if count != 1:
        raise RuntimeError(f"V5 {label}: expected one anchor, found {count}")
    s = s.replace(before, after, 1)

first = s.index("function makeSuggestions(job: string, lang: Lang, track: Track, level: Seniority, skills: string, evidence: string) {")
last = s.index("\nexport default function PersonalSummaryPicker()", first)
s = s[:first] + r"""
function makeSuggestions(job: string, lang: Lang, track: Track, level: Seniority, skills: string, evidence: string, targetRole: string) {
  if (!job.trim()) return [];
  const role = job.trim().slice(0, 90);
  const target = targetRole.trim().slice(0, 90);
  const skill = skills.trim().slice(0, 110);
  const fact = evidence.trim().slice(0, 150);
  const focus = lang === 'ar' ? track.focusAr : track.focusEn;
  const seniority = lang === 'ar'
    ? ({entry:'مبتدئ',mid:'متوسط الخبرة',senior:'في مستوى متقدم'} as const)[level]
    : ({entry:'entry-level',mid:'career-focused',senior:'senior-level'} as const)[level];
  const skillSentence = skill
    ? (lang === 'ar' ? ' المهارات التي أدخلتها: ' : ' Verified skills supplied: ') + skill + '.'
    : '';
  const factSentence = fact
    ? (lang === 'ar' ? ' إنجاز قمت بإدخاله: ' : ' Achievement supplied: ') + fact + '.'
    : '';
  if (lang === 'ar') {
    return [
      // ATS: role and relevant specialization, without inventing proficiency.
      role + ' (' + seniority + ')، مع اهتمام متخصص بـ' + focus + '.' +
        skillSentence + factSentence,
      // Evidence-first: lead with evidence if it exists; otherwise emphasize role focus.
      (fact ? 'أبرز إنجاز مهني مذكور: ' + fact + '. ' : 'التركيز المهني: ') +
        role + ' يركز على ' + focus + ' وتطوير أساليب العمل.' +
        skillSentence + (fact ? '' : factSentence),
      // Targeted: target job is an aspiration, not a claimed current appointment.
      'أسعى إلى ' + (target ? 'فرصة في وظيفة ' + target : 'تطوير مساري في مجال ' + role) +
        '، من خلال التركيز على ' + focus + ' والتعلم المستمر.' +
        skillSentence + factSentence
    ];
  }
  return [
    // ATS-ready: short and directly related to the title and selected specialty.
    role + ' (' + seniority + ') focused on ' + focus + '.' +
      skillSentence + factSentence,
    // Evidence-led: put actual user-entered evidence first only when present.
    (fact ? 'Documented achievement supplied: ' + fact + '. ' : 'Professional focus: ') +
      role + ' with an interest in ' + focus + ' and continuous improvement.' +
      skillSentence + (fact ? '' : factSentence),
    // Career direction: distinguish intended role from verified current experience.
    'Seeking ' + (target ? target + ' opportunities' : 'opportunities as a ' + role) +
      ', with a professional focus on ' + focus + ' and continuous learning.' +
      skillSentence + factSentence
  ];
}
""" + s[last:]

swap("  const [achievement, setAchievement] = useState('');",
"""  const [achievement, setAchievement] = useState('');
  const [targetRole, setTargetRole] = useState('');""", "target role state")
swap("setTrackChoice('auto'); setLevelChoice('auto'); setSkills(''); setAchievement('');",
"setTrackChoice('auto'); setLevelChoice('auto'); setSkills(''); setAchievement(''); setTargetRole('');",
"reset on leaving builder")
swap("""    makeSuggestions(role.trim(), lang, track, level, skills, achievement),
    [role, lang, track, level, skills, achievement]);""",
"""    makeSuggestions(role.trim(), lang, track, level, skills, achievement, targetRole),
    [role, lang, track, level, skills, achievement, targetRole]);
  const evidenceItems = [skills.trim() ? (lang === 'ar' ? 'مهارات مدخلة' : 'Supplied skills') : null,
    achievement.trim() ? (lang === 'ar' ? 'إنجاز مدخل' : 'Supplied achievement') : null].filter(Boolean);""",
"targeted memo and provenance")
swap("styles:['مختصر ومباشر','احترافي','مركز على المهارات']",
"styles:['متوافق مع ATS','أدلة وإنجازات','اتجاه مهني']","Arabic styles")
swap("styles:['Concise','Professional','Skills focused']",
"styles:['ATS concise','Evidence-led','Career direction']","English styles")
swap("""          <details className="sirati-summary-pro-facts">""",
"""          <label className="sirati-summary-v5-target">
            {lang === 'ar' ? 'الوظيفة المستهدفة (اختياري)' : 'Target job (optional)'}
            <input aria-label="Summary target job" maxLength={90} value={targetRole}
              onChange={event => setTargetRole(event.target.value)}
              placeholder={lang === 'ar' ? 'مثال: مدير الحسابات' : 'e.g. Finance Manager'} />
          </label>
          <details className="sirati-summary-pro-facts">""",
"target job input")
swap("""        {options.length
          ? <div className="sirati-summary-choices">""",
"""        {role.trim() && <div className="sirati-summary-v5-sources" aria-live="polite">
          <strong>{lang === 'ar' ? 'مصادر الاقتراح' : 'Suggestion sources'}:</strong>
          <span>{lang === 'ar' ? 'المسمى الوظيفي والتخصص المختار' : 'Professional title & selected specialty'}</span>
          {evidenceItems.map(item => <span key={item}>{item}</span>)}
          {!evidenceItems.length && <em>{lang === 'ar'
            ? 'أضف مهارات أو إنجازات حقيقية للحصول على محتوى أدق'
            : 'Add your verified skills or achievements for more personalized drafts'}</em>}
        </div>}
        {options.length
          ? <div className="sirati-summary-choices">""",
"evidence transparency section")
p.write_text(s, encoding="utf-8")

styles = css.read_text(encoding="utf-8")
if "/* Smart CV Pro V5 */" in styles:
    raise RuntimeError("V5 styles already applied")
styles += r"""
/* Smart CV Pro V5 */
@media screen {
  .sirati-summary-pro-controls .sirati-summary-v5-target { grid-column: 1 / -1; }
  .sirati-summary-v5-sources {
    display: flex; flex-wrap: wrap; gap: 6px; align-items: center;
    padding: 8px; border-radius: 10px; background: #eff6f0;
    color: #1d4c35; font-size: 11px; line-height: 1.55;
  }
  .sirati-summary-v5-sources > strong { font-size: 11px; }
  .sirati-summary-v5-sources > span {
    padding: 3px 7px; border: 1px solid #cddfd1;
    border-radius: 20px; background: #fffefa; font-weight: 650;
  }
  .sirati-summary-v5-sources > em { flex-basis: 100%; font-style: normal; color: #597564; }
  .sirati-summary-choice__style { font-weight: 850; }
  .sirati-summary-v5-target input { min-height: 44px; }
}
"""
css.write_text(styles, encoding="utf-8")
print("PASS: V5 distinct ATS/evidence/career-direction drafts with optional target role and transparent user-entered facts.")
