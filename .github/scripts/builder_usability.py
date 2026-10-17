"""Scoped editor UX: completion, A4 fitting, labels and independent UI language."""
from pathlib import Path
import sys, re, json
root=Path(sys.argv[1]); p=root/'app/builder/page.tsx'; s=p.read_text()
def replace(old,new):
 global s
 if s.count(old)!=1: raise RuntimeError('Builder UX anchor changed: '+old[:70])
 s=s.replace(old,new,1)
# Reuse the exact names already offered by the template selector.
names=dict(re.findall(r'<option value="([^"]+)">([^<]+)</option>',s))
names.pop('en',None); names.pop('ar',None)
replace("import { useEffect,", "import { createContext, useContext, useId, useEffect,")
replace('export default function BuilderPage() {','''const BuilderUi = createContext({uiLanguage: 'en' as CvLanguage, setUiLanguage: (_: CvLanguage) => {}});
function useBuilderUi() {
  const value = useContext(BuilderUi);
  return {...value, t: (text: string) => value.uiLanguage === 'ar' ? UI_AR[text] || text : text};
}
export default function BuilderPage() {
  const [uiLanguage,setUiLanguage] = useState<CvLanguage>('en');
  useEffect(() => { try { setUiLanguage(sessionStorage.getItem('sirati.builder.uiLanguage') === 'ar' ? 'ar' : 'en'); } catch {} }, []);
  function changeUiLanguage(value: CvLanguage) {
    setUiLanguage(value);
    try { sessionStorage.setItem('sirati.builder.uiLanguage',value); } catch {}
  }
  return <BuilderUi.Provider value={{uiLanguage,setUiLanguage:changeUiLanguage}}><BuilderEditor /></BuilderUi.Provider>;
}
function BuilderEditor() {
  const {uiLanguage,setUiLanguage,t} = useBuilderUi();
  const fieldId = useId();
  const previewRef = useRef<HTMLElement>(null);
  useEffect(() => {
    const element = previewRef.current;
    if (!element) return;
    const resize = () => element.style.setProperty('--cv-preview-scale', String(Math.min(1, element.clientWidth / 794)));
    resize();
    const observer = new ResizeObserver(resize);
    observer.observe(element);
    return () => observer.disconnect();
  }, []);''')
replace('  const progressPercent = Math.round(((currentSection + 1) / cvSections.length) * 100);','''  const sectionComplete = [
    !!(data.fullName.trim() && data.title.trim() && (data.email.trim() || data.phone.trim())),
    !!data.profile.trim(),
    data.experience.some(x => x.role.trim() && x.company.trim() && x.period.trim()),
    data.education.some(x => x.degree.trim() && x.school.trim() && x.period.trim()),
    data.certifications.some(x => x.name.trim() && x.issuer.trim()),
    data.courses.some(x => x.name.trim() && x.provider.trim()),
    data.projects.some(x => x.name.trim() && x.details.trim()),
    !!(data.skills.trim() && data.languages.trim()),
    false // Opening Review is navigation, never proof of completion.
  ];
  const essentialChecks = [sectionComplete[0], sectionComplete[1], sectionComplete[2] || sectionComplete[3], sectionComplete[7]];
  const progressPercent = Math.round(100 * essentialChecks.filter(Boolean).length / essentialChecks.length);''')
s=s.replace("index < currentSection ? 'complete' : ''", "sectionComplete[index] ? 'complete' : ''").replace("index < currentSection ? '✓' : index + 1", "sectionComplete[index] ? '✓' : index + 1")
s=s.replace('{cvSections[currentSection].label}','{t(cvSections[currentSection].label)}').replace('{section.short}','{t(section.short)}')
s=s.replace('<strong>{progressPercent}%</strong>','<strong>{t(\'Essential details\')}: {progressPercent}%</strong>')
s=s.replace('<span>Section {currentSection + 1} of {cvSections.length}</span>',"<span>{t('Section')} {currentSection + 1} / {cvSections.length}</span>")
s=s.replace('onClick={() => setCurrentSection(index)}',"aria-current={index === currentSection ? 'step' : undefined}\n                onClick={() => setCurrentSection(index)}")
s=s.replace('<main className="builder-page wizard-builder-page">','<main className="builder-page wizard-builder-page" dir={uiLanguage === \'ar\' ? \'rtl\' : \'ltr\'} lang={uiLanguage}>')
s=s.replace('<section className="preview-wrap wizard-preview-wrap">','<section ref={previewRef} className="preview-wrap wizard-preview-wrap">')
s=s.replace('<strong>{template} ·', '<strong>{TEMPLATE_NAMES[template] || template} ·')
# Accessible labels, including independently identified repeating rows.
pattern=r'<label>([^<]+)</label>(\s*)<(input|textarea|select)([^>]*?)(?=\s(?:value|type)=)'
# Match the complete field prefix instead, so a type attribute before value is safe.
pattern=r'<label>([^<]+)</label>(\s*)<(input|textarea|select)(?=\s)'
count=[0]
def bind(m):
 count[0]+=1
 following=s[m.end():m.end()+200]
 suffix="-${item.id}" if re.search(r'value=\{item\.',following) else ''
 idexpr="{`${fieldId}-field-"+str(count[0])+suffix+"`}"
 return '<label htmlFor='+idexpr+'>'+m[1]+'</label>'+m[2]+'<'+m[3]+' id='+idexpr
s=re.sub(pattern,bind,s)
# Interface preferences are independent of CV content direction.
anchor='          </div>\n\n          {documentId && ('
s=s.replace(anchor,'''\n            <div className="field compact-field">
              <label htmlFor={`${fieldId}-ui-language`}>Interface language</label>
              <select id={`${fieldId}-ui-language`} value={uiLanguage} onChange={e=>setUiLanguage(e.target.value as CvLanguage)}>
                <option value="en">English</option><option value="ar">العربية</option>
              </select>
            </div>\n'''+anchor,1)
# UI-only child components; content-generating helpers keep CV language.
s=s.replace('<OnboardingSteps current={3} language={language}', '<OnboardingSteps current={3} language={uiLanguage}')
s=s.replace('<CvReadinessCheck data={data} language={language}', '<CvReadinessCheck data={data} language={uiLanguage}')
s=s.replace('<SiratiBuilderPdfButton language={language}', '<SiratiBuilderPdfButton uiLanguage={uiLanguage} language={language}')
s=re.sub(r'(<SectionWritingAssistant[^>]*?)language=\{language\}', r'\1language={uiLanguage}', s)
s=s.replace('<SmartContentSuggestions ', '<SmartContentSuggestions uiLanguage={uiLanguage} ')
# Change only UI conditionals in the render; preserve the preview's language label.
a=s.index('    <main className="builder-page'); b=s.index('        <section ref={previewRef}',a)
s=s[:a]+s[a:b].replace("language === 'ar'", "uiLanguage === 'ar'")+s[b:]
s=s.replace("<small>Changes save automatically on this device{userId && documentId ? ' and to your account' : ''}.</small>","<small>{userId && documentId ? t('Changes save to your account.') : t('Draft kept in this tab across refreshes. Save to My Documents before closing.')}</small>")
# Consistent text across the editor, without translating user-entered CV content.
translations={
'Interface language':'لغة الواجهة','CV language':'لغة السيرة الذاتية','Template':'القالب','Essential details':'البيانات الأساسية','Section':'القسم',
'Personal':'البيانات الشخصية','Profile':'الملخص','Experience':'الخبرات','Education':'التعليم','Certificates':'الشهادات','Courses':'الدورات','Projects':'المشروعات','Skills':'المهارات','Review':'المراجعة',
'Personal details':'البيانات الشخصية','Professional profile':'الملخص المهني','Certifications & licenses':'الشهادات والتراخيص','Courses & training':'الدورات والتدريب','Skills & languages':'المهارات واللغات','Review your CV':'مراجعة السيرة الذاتية',
'Full name':'الاسم الكامل','Professional title':'المسمى الوظيفي','Email':'البريد الإلكتروني','Phone':'الهاتف','City & country':'المدينة والدولة','LinkedIn / professional link':'رابط لينكدإن أو الملف المهني','Profile summary':'الملخص المهني','Role':'المسمى الوظيفي','Company / hospital':'الشركة أو المستشفى','Location':'المكان','Period':'الفترة','Achievements / responsibilities':'الإنجازات والمسؤوليات','Degree / qualification':'الدرجة أو المؤهل','School / university':'المدرسة أو الجامعة','Period / graduation year':'الفترة أو سنة التخرج','Details (optional)':'تفاصيل (اختياري)','Certification / license':'الشهادة أو الترخيص','Issuer':'جهة الإصدار','Date / status':'التاريخ أو الحالة','Course / training':'الدورة أو التدريب','Provider':'الجهة المقدمة','Date':'التاريخ','Project name':'اسم المشروع','Organization / context':'المؤسسة أو السياق','Highlights':'أبرز الإنجازات','Languages':'اللغات','Contact details':'بيانات التواصل','Experience or education':'الخبرات أو التعليم',
'My CVs':'سيري الذاتية','Explore samples':'استعراض الأمثلة','Choose an example CV':'اختر مثالًا للسيرة','Demo data only. Replace it with your own information.':'بيانات توضيحية فقط. استبدلها بمعلوماتك.','New CV':'سيرة جديدة','Save version':'حفظ نسخة','Save CV':'حفظ السيرة','Save final version':'حفظ النسخة النهائية','Save CV to my account':'حفظ السيرة في حسابي','Live A4 preview':'معاينة مباشرة بحجم A4','← Back':'رجوع','Continue / Skip →':'متابعة أو تخطي','Continue →':'متابعة','Finish → My documents':'إنهاء — مستنداتي','Add item':'إضافة عنصر','Move up':'تحريك لأعلى','Move down':'تحريك لأسفل','Remove':'حذف','Change photo':'تغيير الصورة','Upload photo':'رفع صورة','Professional photo':'الصورة الشخصية','(optional)':'(اختياري)',
'+ Add experience':'+ إضافة خبرة','+ Add education':'+ إضافة مؤهل','+ Add certification':'+ إضافة شهادة','+ Add course':'+ إضافة دورة','+ Add project':'+ إضافة مشروع',
'Complete one section at a time. Your preview updates as you type.':'أكمل قسمًا في كل مرة. تتحدث المعاينة أثناء الكتابة.',
'Start with the information recruiters use to identify and contact you.':'ابدأ بالبيانات التي تساعد جهة التوظيف في التعرف عليك والتواصل معك.',
'Optional. Use a clean head-and-shoulders photo for this template.':'اختياري. استخدم صورة واضحة للرأس والكتفين.',
'Write a short introduction focused on your experience, strengths and target role.':'اكتب مقدمة قصيرة عن خبرتك ونقاط قوتك والوظيفة المستهدفة.',
'Keep it specific, evidence-based and focused on the role you want. Review local suggestions before applying.':'استخدم معلومات محددة وحقيقية ومرتبطة بالوظيفة. راجع الاقتراحات قبل تطبيقها.',
'Add your most relevant roles, newest first.':'أضف الخبرات الأكثر ارتباطًا بالوظيفة، بدءًا بالأحدث.',
'Each new line appears as a CV bullet.':'يظهر كل سطر جديد كنقطة في السيرة.',
'Add your degrees and relevant qualifications.':'أضف درجاتك العلمية ومؤهلاتك ذات الصلة.',
'Add professional licenses and certifications that support your target role.':'أضف التراخيص والشهادات المرتبطة بالوظيفة المستهدفة.',
'Include training that is relevant to the jobs you are targeting.':'أضف التدريبات المرتبطة بالوظائف المستهدفة.',
'Useful for new graduates, research, quality work and portfolio projects.':'مناسب للخريجين والبحث العلمي ومشروعات الجودة وملف الأعمال.',
'Finish the content with role-relevant skills and honest language proficiency.':'أكمل السيرة بالمهارات المرتبطة بالوظيفة ومستوى اللغات الحقيقي.',
'Check the preview, fix anything missing, then save a version before export.':'راجع المعاينة وأكمل البيانات الناقصة، ثم احفظ نسخة قبل التنزيل.',
'No experience added. Add a role when relevant.':'لم تضف خبرات. أضف وظيفة إن وُجدت.','No education added.':'لم تضف مؤهلات.',
'Optional: add BLS, ACLS, licenses or professional certifications.':'اختياري: أضف الشهادات أو التراخيص المهنية.',
'Optional: add relevant courses or structured training.':'اختياري: أضف الدورات أو التدريب ذي الصلة.',
'Optional: skip this section if projects are not relevant to your CV.':'اختياري: تخطّ هذا القسم إن لم تكن لديك مشروعات ذات صلة.',
'Changes save to your account.':'تُحفظ التعديلات في حسابك.',
'Draft kept in this tab across refreshes. Save to My Documents before closing.':'تُحفظ المسودة في هذا التبويب بعد التحديث. احفظها في مستنداتي قبل إغلاقه.',
'Loading…':'جارٍ التحميل…','Guest draft · Kept in this tab across refreshes':'مسودة ضيف — محفوظة في هذا التبويب بعد التحديث',
'Up to 30 saved versions':'حتى 30 نسخة محفوظة','No saved versions yet. Choose “Save version”.':'لا توجد نسخ محفوظة. اختر حفظ نسخة.',
'Hide version history':'إخفاء النسخ السابقة','Version history':'النسخ السابقة','Version':'نسخة','Certification':'شهادة','Course':'دورة','Project':'مشروع'
}
# Helper components use the same scoped preference.
s=s.replace('function EditorCard({ title, index, total, onMoveUp, onMoveDown, onRemove, children }: EditorCardProps) {','function EditorCard({ title, index, total, onMoveUp, onMoveDown, onRemove, children }: EditorCardProps) {\n  const {t} = useBuilderUi();')
s=s.replace('function EmptySection({ text, onAdd }: { text: string; onAdd: () => void }) {','function EmptySection({ text, onAdd }: { text: string; onAdd: () => void }) {\n  const {t} = useBuilderUi();')
for en in sorted(translations,key=len,reverse=True):
 q=json.dumps(en,ensure_ascii=False)
 s=s.replace('>'+en+'<','>{t('+q+')}<')
 for attr in ['label','text','title','aria-label']:
  s=s.replace(attr+'="'+en+'"',attr+'={t('+q+')}')
 for enquoted in ["'"+en+"'"]:
  # UI ternary text only, not model keys or dictionary/constants.
  s=s.replace('? '+enquoted, '? t('+q+')').replace(': '+enquoted+'}', ': t('+q+')}')
 for tag in ['Experience','Education','Certification','Course','Project','Version']:
  if en==tag: s=s.replace('`'+tag+' ${','`${t('+q+')} ${')
s=s.replace("hydrated ? cloudStatus :", "hydrated ? t(cloudStatus) :")
s=s.replace("`Version history (${versions.length})`", "`${t('Version history')} (${versions.length})`")
# Restore names accidentally touched in template option literals (brand names stay stable).
s=s.replace('<span className="step-badge">✓</span>', '<span className="step-badge">9</span>')
s=s.replace("const STORAGE_KEY =", 'const TEMPLATE_NAMES: Record<string,string> = '+json.dumps(names,ensure_ascii=False)+';\nconst UI_AR: Record<string,string> = '+json.dumps(translations,ensure_ascii=False)+';\n\nconst STORAGE_KEY =',1)
s=s.replace('complete={Boolean(data.experience.some(x => x.role.trim() || x.company.trim()) || data.education.some(x => x.degree.trim() || x.school.trim()))}', 'complete={sectionComplete[2] || sectionComplete[3]}')
p.write_text(s)
pdf=root/'components/SiratiBuilderPdfButton.tsx'; text=pdf.read_text()
text=text.replace('language: string; data: CvData;', 'uiLanguage?: string; language: string; data: CvData;')
text=text.replace("const arabic = language === 'ar';", "const arabic = (props.uiLanguage || language) === 'ar';")
pdf.write_text(text)
smart=root/'components/SmartContentSuggestions.tsx'; text=smart.read_text()
text=text.replace('language: CvLanguage };','language: CvLanguage; uiLanguage?: CvLanguage };').replace('setData, language }: Props','setData, language, uiLanguage }: Props')
text=text.replace("const ar = language === 'ar';", "const ar = (uiLanguage || language) === 'ar';")
text=text.replace("s[ar ? 'ar' : 'en']", "s[language]").replace("pack.achievements[index][ar ? 'ar':'en']", "pack.achievements[index][language]").replace("item[ar?'ar':'en']", "item[language]")
smart.write_text(text)
# Remove the redundant navigator at source, leaving the nine-section navigation.
layout=root/'app/layout.tsx'; text=layout.read_text();text=text.replace('<BuilderNavigator />','');layout.write_text(text)
css=root/'app/globals.css';css.write_text(css.read_text()+'''
/* Editor preview sizing never changes print or detached PDF export. */
@media screen {
 .wizard-builder-shell {grid-template-columns:minmax(0, .92fr) minmax(0, 1.08fr);}
 .wizard-panel,.wizard-preview-wrap,.wizard-preview-wrap .preview-stage {min-width:0;max-width:100%;}
 .wizard-preview-wrap .preview-stage {align-items:flex-start;overflow:visible;}
 /* Override legacy mobile min-height:auto before scaling the full A4 paper. */
 .wizard-preview-wrap .preview-stage > .cv-sheet {width:794px!important;min-width:794px!important;max-width:794px!important;min-height:1123px;flex-shrink:0;zoom:var(--cv-preview-scale,1);margin:0;transform:none;}
 .wizard-document-settings {grid-template-columns:repeat(auto-fit,minmax(140px,1fr));}
 .save-status {white-space:normal;}
 .sirati-pdf-feedback-optional {display:block;font-size:13px;margin-top:8px;}
 body:has(.wizard-builder-page) {padding-bottom:0;}
 @media(max-width:980px){.wizard-builder-shell {grid-template-columns:minmax(0,1fr);}}
}
''')
print('Applied editor completion, preview, names, single navigation, UI language and',count[0],'label bindings')
