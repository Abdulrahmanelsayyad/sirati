"""Apply owner-requested review fixes after legacy generators; fail on changed anchors."""
from pathlib import Path
import re, shutil, sys
root=Path(sys.argv[1]); repo=Path(__file__).resolve().parents[2]
def patch(path, old, new):
    p=root/path; s=p.read_text()
    if s.count(old)!=1: raise RuntimeError(f'{path}: expected one anchor: {old[:90]}')
    p.write_text(s.replace(old,new,1))
for path in ['lib/careerReviewContent.ts','components/ExperienceDates.tsx']:
    shutil.copyfile(repo/path,root/path)
# The gallery catalog, not an independently maintained integer, supplies every count.
p=root/'app/templates/page.tsx'; s=p.read_text()
a=s.index('const templateOptions:'); b=s.index('\n];',a)+3
catalog=s[a:b].replace('const templateOptions:', 'export const templateOptions:',1)
(root/'lib/templateCatalog.ts').write_text("import type { TemplateName } from '@/lib/types';\n"+catalog+'\nexport const TEMPLATE_COUNT = templateOptions.length;\n')
p.write_text(s[:a]+"import {templateOptions,TEMPLATE_COUNT} from '@/lib/templateCatalog';"+s[b:])
patch('app/templates/page.tsx', "'8 مميزة • 33 قالبًا في المكتبة' : '8 featured · 33 templates available'", '`8 مميزة • ${TEMPLATE_COUNT} قالبًا في المكتبة` : `8 featured · ${TEMPLATE_COUNT} templates available`')
patch('app/templates/page.tsx', "'استعرض الـ33 قالبًا' : 'Browse all 33 templates'", '`استعرض الـ${TEMPLATE_COUNT} قالبًا` : `Browse all ${TEMPLATE_COUNT} templates`')
for file in ['components/SiratiSiteMenu.tsx','app/page.tsx']:
    p=root/file; s=p.read_text(); s="import {TEMPLATE_COUNT} from '@/lib/templateCatalog';\n"+s if not s.startswith("'use client';") else s.replace("'use client';","'use client';\nimport {TEMPLATE_COUNT} from '@/lib/templateCatalog';",1)
    s=s.replace("detail: '32 CV templates'", 'detail: `${TEMPLATE_COUNT} CV templates`').replace("title: 'تنزيل السيرة PDF'", "title: 'Download PDF'")
    s=s.replace('View all 33 templates →', 'View all {TEMPLATE_COUNT} templates →');p.write_text(s)
# Restore a non-sensitive section index per account/document, not CV data.
patch('app/builder/page.tsx', "import JobTitleInput", "import ExperienceDates from '@/components/ExperienceDates';\nimport JobTitleInput")
patch('app/builder/page.tsx', '  const [currentSection, setCurrentSection] = useState(0);', '''  const [currentSection, setCurrentSection] = useState(0);
  const sectionKey = 'sirati.builder.section:' + (userId || 'guest') + ':' + (documentId || 'draft');
  const restoredSectionKey = useRef('');
  useEffect(() => {
    if (!hydrated || (!userId && !guestRestoreReady) || isSessionBoundaryBlocked()) return;
    try {
      const stored = sessionStorage.getItem(sectionKey);
      const saved = stored === null ? NaN : Number(stored);
      const navParams = new URLSearchParams(window.location.search);
      const focus = navParams.get('focus');
      const afterSave = documentId && !navParams.get('doc') && restoredSectionKey.current === 'sirati.builder.section:' + (userId || 'guest') + ':draft';
      const section = newCvRequestedRef.current ? 0 : focus === 'smart' ? 1 : focus === 'quality' ? 8 : Number.isInteger(saved) && saved >= 0 && saved < 9 ? saved : afterSave ? currentSection : 0;
      setCurrentSection(section);
      sessionStorage.setItem(sectionKey,String(section));
    } catch { setCurrentSection(0); }
    restoredSectionKey.current = sectionKey;
  }, [hydrated,guestRestoreReady,userId,documentId]);
  function rememberSection(section:number) {
    setCurrentSection(section);
    if (restoredSectionKey.current !== sectionKey || isSessionBoundaryBlocked()) return;
    try { sessionStorage.setItem(sectionKey,String(section)); } catch {}
  }''')
p=root/'app/builder/page.tsx'; s=p.read_text()
a=s.index("  const sectionKey ="); b=s.index("  const cloudReadyRef",a)
restore=s[a:b]; s=s[:a]+s[b:]
s=s.replace("  const newCvRequestedRef = useRef(false);", "  const newCvRequestedRef = useRef(false);\n"+restore)
p.write_text(s)
patch('app/builder/page.tsx','setCurrentSection(section => Math.min(section + 1, cvSections.length - 1));','rememberSection(Math.min(currentSection + 1, cvSections.length - 1));')
patch('app/builder/page.tsx','setCurrentSection(section => Math.max(section - 1, 0));','rememberSection(Math.max(currentSection - 1, 0));')
patch('app/builder/page.tsx','onClick={() => setCurrentSection(index)}','onClick={() => rememberSection(index)}')
patch('app/builder/page.tsx','  function resetCv() {','  function resetCv() {\n    rememberSection(0);\n    try {sessionStorage.setItem("sirati.builder.section:"+(userId||"guest")+":draft","0");} catch {}')
patch('app/builder/page.tsx','                    setCurrentSection(0);','                    rememberSection(0);')
patch('app/builder/page.tsx','<div className="field"><label htmlFor={`${fieldId}-field-11-${item.id}`}>{t("Period")}</label><input id={`${fieldId}-field-11-${item.id}`} value={item.period} onChange={e => updateExperience(item.id, { period: e.target.value })} placeholder="2021 — Present" /></div>', '<ExperienceDates value={item.period} arabic={uiLanguage === \'ar\'} onChange={period => updateExperience(item.id, {period})} />')
# Explicit choices only; an occupation is not proof of specialty/seniority.
patch('components/PersonalSummaryPicker.tsx', "type Seniority = 'entry' | 'mid' | 'senior';", "type Seniority = 'unspecified' | 'entry' | 'mid' | 'senior';")
# Keep legacy helper types compiling though new options use the shared pure function.
p=root/'components/PersonalSummaryPicker.tsx'; s=p.read_text().replace("{entry:'مبتدئ',mid:","{unspecified:'',entry:'مبتدئ',mid:").replace("{entry:'entry-level',mid:","{unspecified:'',entry:'entry-level',mid:")
s=s.replace("import { createPortal }", "import {profileDrafts} from '@/lib/careerReviewContent';\nimport { createPortal }")
s=s.replace("useState('auto')", "useState('unspecified')",1).replace("useState<'auto' | Seniority>('auto')", "useState<Seniority>('unspecified')")
a=s.index('  const tracks = useMemo('); b=s.index('  useEffect(() => { setProfilePage',a)
s=s[:a]+'''  const tracks = useMemo(() => [{id:'unspecified',en:'Choose specialization (optional)',ar:'اختر التخصص (اختياري)',focusEn:'',focusAr:''},...tracksFor(role)], [role]);
  const track = tracks.find(item => item.id === trackChoice) || tracks[0];
  const level = levelChoice;
  useEffect(() => { setTrackChoice('unspecified'); setLevelChoice('unspecified'); }, [role]);
  const options = useMemo(() => profileDrafts(role,lang,lang === 'ar' ? track.focusAr : track.focusEn,level,skills,achievement,targetRole), [role,lang,track,level,skills,achievement,targetRole]);
'''+s[b:]
s=s.replace("setLevelChoice('auto')","setLevelChoice('unspecified')").replace("setTrackChoice('auto')","setTrackChoice('unspecified')")
s=s.replace('<option value="entry">','<option value="unspecified">{lang === \'ar\' ? \'اختر مستوى الخبرة (اختياري)\' : \'Choose experience level (optional)\'}</option>\n              <option value="entry">',1)
s=s.replace("{t.styles[i % t.styles.length]}","{lang === 'ar' ? 'مسودة قابلة للتعديل' : 'Editable draft'}")
# Factual drafting supplies at most four genuinely different strategies. A
# six-item page made More unreachable. Keep three choices and expose the rest.
s=s.replace('profilePage * 6', 'profilePage * 3').replace('(profilePage + 1) * 6', '(profilePage + 1) * 3')
s=s.replace('(profilePage+1)*6', '(profilePage+1)*3').replace('options.length > 6', 'options.length > 3').replace('Math.ceil(options.length/6)', 'Math.ceil(options.length/3)')
s=s.replace("'Professional title & selected specialty'", "'Professional title & your explicit selections'")
a=s.index('function inferredTrack('); b=s.index('// Only match explicit job requirements',a); s=s[:a]+s[b:]
a=s.index('// Offline, editable alternatives;'); b=s.index('export default function PersonalSummaryPicker()',a); s=s[:a]+s[b:]
p.write_text(s)
# Career tools: exact user facts, clean sentences, role bank and optional explicit scope.
p=root/'app/career-tools/page.tsx'; s=p.read_text()
s=s.replace("import Link", "import {linkedInDraft,interviewQuestions} from '@/lib/careerReviewContent';\nimport Link",1)
s=s.replace("motivation = ''): string", "motivation = '', specialty = '', level = ''): string",1)
a=s.index("  if (mode === 'linkedin') {");b=s.index("  return (lang === 'ar'",a)
s=s[:a]+'''  if (mode === 'linkedin') return linkedInDraft(lang,role,facts,skills);
  const questions = interviewQuestions(role,specialty,level,lang);
'''+s[b:]
s=s.replace("  const [motivation, setMotivation] = useState('');", "  const [motivation, setMotivation] = useState('');\n  const [specialty,setSpecialty]=useState('');\n  const [level,setLevel]=useState('');")
s=s.replace('letterTone, motivation));','letterTone, motivation, specialty, level));')
anchor="          {mode === 'letter' && <label>{t('Company you are applying to'"
a=s.index(anchor)
s=s[:a]+'''          {mode === 'interview' && <>
            <label>{t('Specialization (optional)', 'التخصص (اختياري)')}<input maxLength={100} value={specialty} onChange={e=>setSpecialty(e.target.value)} /></label>
            <label>{t('Experience level (optional)', 'مستوى الخبرة (اختياري)')}<select value={level} onChange={e=>setLevel(e.target.value)}>
              <option value="">{t('Not specified','غير محدد')}</option><option value="entry">{t('Entry level','مبتدئ')}</option><option value="mid">{t('Mid level','متوسط')}</option><option value="senior">{t('Senior','متقدم')}</option>
            </select></label>
          </>}
'''+s[a:]
s=s.replace("    setFields(previous => ({ ...previous, [field]: value }));", "    if(field === 'role') {setSpecialty('');setLevel('');}\n    setFields(previous => ({ ...previous, [field]: value }));")
p.write_text(s)
print('Applied catalog, neutral factual suggestions, career content, section restore and compatible dates.')
# Optional rating precedes account gate. Failure never prevents the user's PDF.
p=root/'components/SiratiBuilderPdfButton.tsx'; s=p.read_text()
s=s.replace('  data: CvData; template:', '  reviewRating?: number;\n  data: CvData; template:',1)
s=s.replace('  const [downloaded,setDownloaded] = useState(false);', '''  const [downloaded,setDownloaded] = useState(false);
  const [ratingOpen,setRatingOpen] = useState(false);
  const [rating,setRating] = useState(0);
  const selectedRating = useRef(0);
  const ratingDialog = useRef<HTMLElement>(null);
  const [ratingNotice,setRatingNotice] = useState('');''',1)
s=s.replace('  async function begin() {', '''  useEffect(() => {
    if (!ratingOpen) return;
    const dialog=ratingDialog.current;
    dialog?.querySelector<HTMLButtonElement>('button')?.focus();
    function keys(event:KeyboardEvent) {
      if(event.key==='Escape') {event.preventDefault();setRatingOpen(false);selectedRating.current=0;trigger.current?.focus();}
      if(event.key==='Tab') {
        const buttons=Array.from(dialog?.querySelectorAll<HTMLButtonElement>('button:not([disabled])') || []);
        const first=buttons[0],last=buttons[buttons.length-1];
        if(event.shiftKey&&document.activeElement===first){event.preventDefault();last?.focus();}
        else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first?.focus();}
      }
    }
    window.addEventListener('keydown',keys);
    return()=>window.removeEventListener('keydown',keys);
  },[ratingOpen]);

  async function saveOptionalRating(expectedId:string, expectedEmail:string|null) {
    if(saving || isSessionBoundaryBlocked()) return;
    const pending=readTransfer();
    const value=selectedRating.current || (pending?.requested ? pending.reviewRating : 0) || 0;
    if(!Number.isInteger(value)||value<1||value>5) return;
    if(pending?.email && pending.email.toLowerCase()!==expectedEmail?.toLowerCase()) return;
    const client=createClient();if(!client)return;
    const {data:verified,error:verifyError}=await client.auth.getUser();
    if(verifyError||verified.user?.id!==expectedId||isSessionBoundaryBlocked()) throw new Error('Account changed. Reopen your CV.');
    selectedRating.current=0;
    try {
      const {error:writeError}=await client.from('sirati_site_feedback').upsert({user_id:expectedId,rating:value,category:'editing',comment:''}, {onConflict:'user_id',ignoreDuplicates:true}).abortSignal(AbortSignal.timeout(5000));
      if(isSessionBoundaryBlocked()) throw new Error('Account changed. Reopen your CV.');
      const {data:after,error:afterError}=await client.auth.getUser();
      if(afterError||after.user?.id!==expectedId) throw new Error('Account changed. Reopen your CV.');
      setRatingNotice(writeError ? 'Rating could not be saved. PDF download is still available.' : 'Feedback processed. Any existing review was kept unchanged.');
    } catch {
      setRatingNotice('Rating could not be confirmed. PDF download is still available.');
    }
    // Account changes must stop export even when the optional review request fails.
    const {data:current,error:identityError}=await client.auth.getUser();
    if(identityError||current.user?.id!==expectedId||isSessionBoundaryBlocked()) throw new Error('Account changed. Reopen your CV.');
  }

  async function continueAfterRating(skip:boolean) {
    selectedRating.current=skip?0:rating;
    const pending=readTransfer();
    if(pending) try {storeTransfer({...pending,reviewRating:undefined});} catch {}
    setRatingOpen(false);
    await begin();
  }
  async function begin() {''',1)
s=s.replace('        data,template,language});','        reviewRating:selectedRating.current || undefined,data,template,language});',1)
s=s.replace('        onAuthenticated(result.data.user.id, result.data.user.email || null);', '        onAuthenticated(result.data.user.id, result.data.user.email || null);\n        await saveOptionalRating(result.data.user.id,result.data.user.email || null);',1)
s=s.replace('        onAuthenticated(auth.user.id,auth.user.email||null);', '        onAuthenticated(auth.user.id,auth.user.email||null);\n        await saveOptionalRating(auth.user.id,auth.user.email||null);',1)
s=s.replace('          onAuthenticated(confirmed.user.id,confirmed.user.email||null);','          onAuthenticated(confirmed.user.id,confirmed.user.email||null);\n          await saveOptionalRating(confirmed.user.id,confirmed.user.email||null);',1)
s=s.replace('      try { await exportWithFeedback(); }','      try { await saveOptionalRating(verified.user.id,verified.user.email||null); await exportWithFeedback(); }',1)
s=s.replace('storeTransfer({...transfer,requested:false});','storeTransfer({...transfer,requested:false,reviewRating:undefined});',1)
s=s.replace("    setOpen(false);setPassword('');", "    selectedRating.current=0;setRating(0);\n    setOpen(false);setPassword('');",1)
s=s.replace('aria-busy={busy} onClick={begin}', '''aria-busy={busy} onClick={()=>{
        if(isSessionBoundaryBlocked()) return;
        const warning=pdfJoinedScriptWarning(data,arabic);
        if(warning){setError(warning);return;}
        setError('');setRatingNotice('');setRating(0);selectedRating.current=0;setRatingOpen(true);
      }}''',1)
anchor='    {downloaded && !saving &&'
a=s.index(anchor)
s=s[:a]+'''    {ratingNotice && <small role="status">{ratingNotice}</small>}
    {ratingOpen && <div className="sirati-pdf-auth-overlay"><section ref={ratingDialog} role="dialog" aria-modal="true" aria-labelledby={dialogId+'-rating'} className="sirati-pdf-auth-dialog">
      <button type="button" onClick={()=>{setRatingOpen(false);selectedRating.current=0;trigger.current?.focus();}}>{arabic?'العودة للتحرير':'Back to editing'}</button>
      <h2 id={dialogId+'-rating'}>{arabic?'قيّم تجربة التحرير (اختياري)':'Rate your editing experience (optional)'}</h2>
      <p>{arabic?'يُرسل تقييمك بعد تسجيل الدخول. يمكنك التخطي والمتابعة إلى PDF. يُحفظ أي تقييم سابق دون تغيير.':'Your rating will be submitted after sign-in. You can skip it and continue to PDF. Existing reviews are kept unchanged.'}</p>
      <div role="group" aria-label={arabic?'التقييم':'Rating'}>{[1,2,3,4,5].map(value=><button key={value} type="button" aria-label={value+(arabic?' من 5 نجوم':' of 5 stars')} aria-pressed={rating===value} style={{minWidth:44,minHeight:44,fontSize:24}} onClick={()=>setRating(value)}>{value<=rating?'★':'☆'}</button>)}</div>
      <button type="button" className="btn btn-primary" disabled={!rating} onClick={()=>continueAfterRating(false)}>{arabic?'حفظ التقييم والمتابعة':'Save rating and continue'}</button>
      <button type="button" className="btn btn-secondary" onClick={()=>continueAfterRating(true)}>{arabic?'تخطي ومتابعة':'Skip and continue'}</button>
    </section></div>}
'''+s[a:]
p.write_text(s)
