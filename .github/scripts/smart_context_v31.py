"""Local-only Smart CV improvements, layered on the existing V4-V6 assistant."""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()

def edit(file, before, after):
    path = root / file
    source = path.read_text()
    if source.count(before) != 1:
        raise RuntimeError(f'{file}: expected one anchor: {before[:80]}')
    path.write_text(source.replace(before, after, 1))

# Direct React props keep context scoped to the active Builder and avoid storage reads,
# global personal-data events, or any external service. Existing writes remain untouched.
edit('app/layout.tsx', "import PersonalSummaryPicker from '@/components/PersonalSummaryPicker';\n", '')
edit('app/layout.tsx', '              <PersonalSummaryPicker />', '')
edit('app/builder/page.tsx', "import { useEffect,", "import PersonalSummaryPicker from '@/components/PersonalSummaryPicker';\nimport { useEffect,")
edit('app/builder/page.tsx', '<main className="builder-page wizard-builder-page">', '''<main className="builder-page wizard-builder-page">
      <PersonalSummaryPicker key={`${userId || 'guest'}:${documentId || 'draft'}`} data={data} />''')

p = 'components/PersonalSummaryPicker.tsx'
edit(p, "import { createPortal } from 'react-dom';", "import { createPortal } from 'react-dom';\nimport type { CvData } from '@/lib/types';")
edit(p, 'export default function PersonalSummaryPicker() {', 'export default function PersonalSummaryPicker({data}: {data: CvData}) {')
edit(p, "  const titleRef = useRef('');", """  const titleRef = useRef('');
  const [undo, setUndo] = useState<{field: HTMLTextAreaElement; before: string; after: string} | null>(null);
  // The current CV is authoritative, including when Profile is on a hidden wizard step.
  useEffect(() => { titleRef.current = data.title; setRole(data.title); }, [data.title]);
  const actualSkills = uniqueSkills([data.skills, skills].join(', '));
  const cvEvidence = [data.profile, data.skills,
    ...data.experience.flatMap(item => [item.role, item.details]),
    ...data.education.flatMap(item => [item.degree, item.details]),
    ...data.certifications.map(item => item.name),
    ...data.projects.flatMap(item => [item.name, item.details])].join('\\n');
""")
edit(p, "makeSuggestions(role.trim(), lang, track, level, skills, achievement, targetRole, jobAd),\n    [role, lang, track, level, skills, achievement, targetRole, jobAd]);",
     "makeSuggestions(role.trim(), lang, track, level, actualSkills, achievement, targetRole, jobAd),\n    [role, lang, track, level, actualSkills, achievement, targetRole, jobAd]);")
edit(p, 'analyzeJobPosting(jobAd,skills,achievement),\n    [jobAd,skills,achievement]);', 'analyzeJobPosting(jobAd,actualSkills,achievement,cvEvidence),\n    [jobAd,actualSkills,achievement,cvEvidence]);')
edit(p, "const evidenceItems = [skills.trim()", "const evidenceItems = [actualSkills.trim()")
edit(p, "'Professional title & selected specialty'", "'Current CV title, skills & selected specialty'")
edit(p, "'Mentioned in your optional facts:'", "'Exact terms mentioned in your CV or supplied facts:'")
edit(p, "'Not listed in your optional facts:'", "'Not confirmed in your CV — add only if true:'")
edit(p, "'Requirements are never inserted automatically. Not an ATS score.'", "'Local vocabulary check, not qualification verification or an ATS score. Negated mentions and proficiency need your review; requirements are never inserted automatically.'")
edit(p, "'Add your verified skills or achievements for more personalized drafts'", "'Add actual skills to your CV or supply an achievement below. Examples do not establish qualifications.'")
edit(p, "styles:['ATS concise','Evidence-led','Career direction']", "styles:['ATS-Optimized','Achievement-Focused','Concise Professional']")

# Natural English drafts: no invented years, certifications, impact, or leadership.
start = (root / p).read_text().index('  return [\n    // ATS-ready:')
end = (root / p).read_text().index('\n}\n', start)
source = (root / p).read_text()
source = source[:start] + """  const sentence = (value: string) => value.trim().replace(/[.!?]+$/, '') + '.';
  const skillList = uniqueSkills(skills);
  const roleLabel = level === 'entry' && !/junior|intern|trainee|entry/i.test(role)
    ? 'Entry-level ' + role : level === 'senior' && !/senior|lead|manager|director|head|supervisor/i.test(role)
    ? 'Senior ' + role : role;
  const skillText = skillList ? ' Skills include ' + sentence(skillList) : '';
  const goalText = target ? ' Targeting ' + sentence(target + ' opportunities') : '';
  return [
    roleLabel + ' focused on ' + sentence(focus) + skillText + goalText,
    fact ? sentence(fact) + ' ' + roleLabel + '.' + skillText
      : roleLabel + ' focused on ' + sentence(focus) + ' Add a real contribution below to create an achievement-focused summary.',
    skillList ? roleLabel + ' with skills in ' + sentence(skillList) + goalText
      : 'Seeking ' + sentence(target ? target + ' opportunities' : 'opportunities in ' + role) + ' Professional focus: ' + sentence(focus)
  ];""" + source[end:]
(root / p).write_text(source)
# Missing achievement is a prompt, never insert placeholder guidance into the CV.
edit(p, "onClick={() => apply(text)} aria-label=", "disabled={i === 1 && !achievement.trim()} onClick={() => apply(text)} aria-label=")
edit(p, "onClick={() => setEditing({index:i,original:text,text})}", "disabled={i === 1 && !achievement.trim()} onClick={() => setEditing({index:i,original:text,text})}")

# A specialization cannot be assumed from a broad title (e.g. nurse -> emergency).
edit(p, "  return trackLibrary[domain] || [{", "  const specific = trackLibrary[domain];\n  return [{id:'role', en:'General role focus', ar:'التركيز العام للدور', focusEn:career.focus.en, focusAr:career.focus.ar}, ...(specific || [])];\n  /* legacy fallback */\n  return trackLibrary[domain] || [{")
# Remove the now unreachable legacy fallback entirely.
source = (root / p).read_text()
start = source.index('  /* legacy fallback */')
end = source.index('\n}\nfunction inferredTrack', start)
(root / p).write_text(source[:start] + source[end:])

edit(p, 'function analyzeJobPosting(posting: string, skills: string, achievement: string) {', 'function analyzeJobPosting(posting: string, skills: string, achievement: string, cvEvidence = \'\') {')
edit(p, "const terms=jobTerms.filter(t=>hasJobTerm(posting.slice(0,2000),t)).slice(0,10);", "const terms=jobTerms.filter(t=>hasJobTerm(posting.slice(0,2000),t));")
edit(p, "const evidence=(skills+' '+achievement).slice(0,270);", "const evidence=[skills,achievement,cvEvidence].join('\\n');")
edit(p, "  'Excel','SAP'", "  'BLS','ACLS','general ledger','accounts payable','accounts receivable','REST APIs','Git','Testing',\n  'lesson planning','classroom management','recruitment','onboarding','scheduling','record keeping',\n  'AutoCAD','maintenance','lead generation','CRM','content strategy','ticketing','troubleshooting',\n  'Excel','SAP'")
edit(p, '// Only match explicit job requirements', """function uniqueSkills(value: string) {
  const seen = new Set<string>();
  return value.split(/[,;\\n،]+/u).map(item => item.trim()).filter(item => {
    const key = item.normalize('NFKC').toLocaleLowerCase();
    if (!key || seen.has(key)) return false;
    seen.add(key); return true;
  }).join(', ');
}

// Only match explicit job requirements""")

edit(p, '    putSummary(target.current, value);', '    setUndo({field: target.current, before: target.current.value, after: value});\n    putSummary(target.current, value);')
edit(p, '  return createPortal(!open', """  const revert = () => {
    if (!undo || !undo.field.isConnected || undo.field !== target.current) {setUndo(null); return;}
    if (undo.field.value !== undo.after && !window.confirm('Your summary has changed since insertion. Restore the previous summary?')) return;
    putSummary(undo.field, undo.before); setUndo(null);
  };
  return createPortal(<>
    {undo && undo.field === target.current && <button type="button" className="sirati-summary-trigger" onClick={revert}>Undo summary insertion</button>}
    {!open""")
edit(p, '      </section>, mount);', '      </section>}</>, mount);')
# Achievement templates follow the chosen employment record, never the CV headline.
# Stable IDs also prevent a removed/reordered row from redirecting an insertion.
c = 'components/SmartContentSuggestions.tsx'
edit(c, 'const PACKS: Pack[] = [', '''const PACKS: Pack[] = [
  {match:/administrator|administrative|secretary|office manager|executive assistant|إداري|اداري|سكرتير/i,
   label:pair('Administration','الإدارة'),
   skills:[pair('Calendar coordination','تنسيق المواعيد'),pair('Office correspondence','مراسلات المكتب'),pair('Records management','إدارة السجلات'),pair('Meeting preparation','إعداد الاجتماعات'),pair('Task prioritization','ترتيب أولويات المهام')],
   achievements:[pair('Organized [actual office process] by [your action], resulting in [observed outcome].','تنظيم [إجراء مكتبي فعلي] عبر [إجراء نفذته] بنتيجة [نتيجة ملحوظة].'),pair('Resolved [documented scheduling or records issue] through [your specific contribution].','حل [مشكلة موثقة في المواعيد أو السجلات] عبر [مساهمتك المحددة].')]},''')
edit(c, "const [entry, setEntry] = useState(0);", "const [entry, setEntry] = useState(data.experience[0]?.id || '');")
edit(c, "  const role = (data.title || '').trim();", """  const selectedExperience = data.experience.find(item => item.id === entry);
  const role = (tab === 'achievement' ? selectedExperience?.role || '' : data.title || '').trim();""")
edit(c, "if (!role || !confirmed || !data.experience.length || !value || /\\[[^\\]]+\\]/.test(value)) return;", "if (!role || !confirmed || !selectedExperience || !value || /\\[[^\\]]+\\]/.test(value)) return;")
edit(c, 'experience:prev.experience.map((item,i) => {\n      if (i !== Math.min(entry,prev.experience.length-1)) return item;', 'experience:prev.experience.map(item => {\n      if (item.id !== entry) return item;')
# Keep the selector outside the conditional role block so deletion/empty roles can recover.
source = (root / c).read_text()
start = source.index("          {data.experience.length ? <label>")
end = source.index("          {draft &&", start)
source = source[:start] + source[end:]
(root / c).write_text(source)
edit(c, '      {role ? <p', '''      {tab === 'achievement' && <label>
        {ar ? 'إضافة إلى خبرة' : 'Add to experience'}
        <select aria-label="Achievement target experience" value={selectedExperience?.id || ''}
          onChange={e => {setEntry(e.target.value); setDraft(''); setConfirmed(false);}}>
          <option value="">{ar ? 'اختر خبرة عمل' : 'Select a work experience'}</option>
          {data.experience.map(exp => <option key={exp.id} value={exp.id}>{exp.role || exp.company || 'Untitled experience'}</option>)}
        </select>
        {!selectedExperience && <p role="status">Select an existing experience to continue.</p>}
        <button type="button" onClick={() => {setTab('skills'); setConfirmed(false);}}>Back to skills</button>
      </label>}
      {role ? <p''')
print('PASS: Smart CV context, evidence matching, safe undo and stable achievement targeting installed.')
