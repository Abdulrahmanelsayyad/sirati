"""Smart CV Pro V4: opt-in, precise, factual professional summary suggestions.

Applied to generated PersonalSummaryPicker; no paid AI, account, CV storage or
backend changes. Fails closed if an expected V3 anchor is missing.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
path = root / "components/PersonalSummaryPicker.tsx"
css_path = root / "app/globals.css"
source = path.read_text(encoding="utf-8")

def once(old, new, label):
    global source
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"Smart CV Pro V4 {label}: expected 1 anchor, found {count}")
    source = source.replace(old, new, 1)

begin = source.index("function makeSuggestions(job: string, lang: Lang) {")
end = source.index("\nexport default function PersonalSummaryPicker()", begin)
source = source[:begin] + r"""
type Seniority = 'entry' | 'mid' | 'senior';
type Track = {id: string; en: string; ar: string; focusEn: string; focusAr: string};
const trackLibrary: Record<string, Track[]> = {
  'accounting': [
    {id:'financial',en:'Financial reporting',ar:'المحاسبة المالية',focusEn:'ledger reconciliations, month-end close and financial reporting',focusAr:'تسوية الحسابات والإقفال الشهري والتقارير المالية'},
    {id:'cost',en:'Cost accounting',ar:'محاسبة التكاليف',focusEn:'cost allocation, variance analysis and inventory valuation',focusAr:'توزيع التكاليف وتحليل الانحرافات وتقييم المخزون'},
    {id:'audit',en:'Audit & controls',ar:'المراجعة والرقابة',focusEn:'control testing, audit documentation and risk reporting',focusAr:'اختبار الرقابة وتوثيق المراجعة وتقارير المخاطر'}
  ],
  'nursing': [
    {id:'emergency',en:'Emergency care',ar:'تمريض الطوارئ',focusEn:'triage, rapid assessment and safe escalation',focusAr:'الفرز والتقييم السريع والتصعيد الآمن'},
    {id:'icu',en:'Critical care',ar:'الرعاية الحرجة',focusEn:'patient monitoring, clinical handovers and coordinated critical care',focusAr:'مراقبة المرضى والتسليم السريري وتنسيق الرعاية الحرجة'},
    {id:'general',en:'Patient care',ar:'رعاية المرضى',focusEn:'patient-centered care, documentation and teamwork',focusAr:'رعاية المرضى والتوثيق والعمل الجماعي'}
  ],
  'software development': [
    {id:'frontend',en:'Frontend',ar:'تطوير الواجهات',focusEn:'responsive interfaces, accessibility and UI performance',focusAr:'الواجهات المتجاوبة وإمكانية الوصول وأداء الواجهة'},
    {id:'backend',en:'Backend',ar:'تطوير الخلفية',focusEn:'API design, data integrity and maintainable services',focusAr:'تصميم واجهات API وسلامة البيانات والخدمات القابلة للصيانة'},
    {id:'mobile',en:'Mobile development',ar:'تطبيقات الهاتف',focusEn:'mobile usability, app reliability and platform integration',focusAr:'سهولة استخدام التطبيقات والاعتمادية والتكامل'}
  ],
  'engineering': [
    {id:'civil',en:'Civil engineering',ar:'الهندسة المدنية',focusEn:'site coordination, construction documentation and quality checks',focusAr:'تنسيق المواقع وتوثيق الإنشاءات وفحوص الجودة'},
    {id:'mechanical',en:'Mechanical engineering',ar:'الهندسة الميكانيكية',focusEn:'mechanical systems, maintenance planning and technical documentation',focusAr:'الأنظمة الميكانيكية وتخطيط الصيانة والتوثيق الفني'},
    {id:'electrical',en:'Electrical engineering',ar:'الهندسة الكهربائية',focusEn:'electrical systems, safety practices and troubleshooting',focusAr:'الأنظمة الكهربائية والسلامة واستكشاف الأعطال'}
  ],
  'marketing': [
    {id:'digital',en:'Digital marketing',ar:'التسويق الرقمي',focusEn:'campaign planning, audience insights and performance measurement',focusAr:'تخطيط الحملات وفهم الجمهور وقياس الأداء'},
    {id:'seo',en:'SEO & content',ar:'تحسين البحث والمحتوى',focusEn:'search visibility, content strategy and keyword research',focusAr:'الظهور في البحث واستراتيجية المحتوى وبحث الكلمات'}
  ],
  'sales': [
    {id:'b2b',en:'B2B sales',ar:'مبيعات الشركات',focusEn:'client discovery, proposals and account relationships',focusAr:'فهم احتياجات الشركات والعروض وعلاقات الحسابات'},
    {id:'retail',en:'Retail sales',ar:'مبيعات التجزئة',focusEn:'customer needs, product recommendations and service quality',focusAr:'احتياجات العملاء وترشيح المنتجات وجودة الخدمة'}
  ],
  'human resources': [
    {id:'recruitment',en:'Recruitment',ar:'الاستقطاب',focusEn:'candidate screening, interviews and hiring coordination',focusAr:'فرز المرشحين والمقابلات وتنسيق التوظيف'},
    {id:'hr-ops',en:'HR operations',ar:'عمليات الموارد البشرية',focusEn:'employee records, onboarding and policy coordination',focusAr:'سجلات العاملين والتهيئة وتنسيق السياسات'}
  ],
  'education': [
    {id:'teaching',en:'Teaching',ar:'التدريس',focusEn:'lesson planning, learner assessment and classroom engagement',focusAr:'تخطيط الدروس وتقييم المتعلمين والتفاعل الصفي'},
    {id:'training',en:'Training',ar:'التدريب',focusEn:'training delivery, learner feedback and practical instruction',focusAr:'تقديم التدريب وتغذية المتعلمين الراجعة والتعليم العملي'}
  ],
  'customer service': [
    {id:'support',en:'Customer support',ar:'دعم العملاء',focusEn:'issue resolution, clear communication and customer follow-up',focusAr:'حل المشكلات والتواصل الواضح ومتابعة العملاء'},
    {id:'technical',en:'Technical support',ar:'الدعم الفني',focusEn:'ticket triage, troubleshooting and user guidance',focusAr:'فرز البلاغات واستكشاف الأعطال وإرشاد المستخدمين'}
  ],
  'logistics': [
    {id:'inventory',en:'Inventory',ar:'المخزون',focusEn:'stock accuracy, inventory control and replenishment',focusAr:'دقة المخزون وضبطه وإعادة التوريد'},
    {id:'procurement',en:'Procurement',ar:'المشتريات',focusEn:'supplier coordination, purchase orders and cost awareness',focusAr:'التنسيق مع الموردين وأوامر الشراء ومراقبة التكلفة'}
  ],
  'design': [
    {id:'uiux',en:'UI/UX design',ar:'تصميم تجربة المستخدم',focusEn:'user flows, interface clarity and accessibility',focusAr:'رحلات المستخدم ووضوح الواجهات وإمكانية الوصول'},
    {id:'visual',en:'Visual design',ar:'التصميم البصري',focusEn:'visual identity, layout systems and brand communication',focusAr:'الهوية البصرية وأنظمة التخطيط والتواصل البصري'}
  ],
  'pharmacy': [
    {id:'clinical',en:'Clinical pharmacy',ar:'الصيدلة الإكلينيكية',focusEn:'medication review, patient counseling and safety',focusAr:'مراجعة الأدوية وتثقيف المرضى والسلامة'},
    {id:'community',en:'Community pharmacy',ar:'صيدلة المجتمع',focusEn:'prescription processing, safe dispensing and customer guidance',focusAr:'الوصفات والصرف الآمن وإرشاد العملاء'}
  ],
  'medicine': [
    {id:'clinical',en:'Clinical care',ar:'الممارسة السريرية',focusEn:'clinical assessment, patient communication and care coordination',focusAr:'التقييم السريري والتواصل مع المرضى وتنسيق الرعاية'},
    {id:'public',en:'Public health',ar:'الصحة العامة',focusEn:'prevention, health education and community health',focusAr:'الوقاية والتثقيف الصحي وصحة المجتمع'}
  ],
  'administration': [
    {id:'office',en:'Office operations',ar:'إدارة المكاتب',focusEn:'scheduling, records and efficient office coordination',focusAr:'الجدولة والسجلات وتنسيق أعمال المكتب'},
    {id:'projects',en:'Project coordination',ar:'تنسيق المشروعات',focusEn:'task tracking, documentation and stakeholder updates',focusAr:'متابعة المهام والتوثيق وتحديثات الأطراف'}
  ],
  'laboratory services': [
    {id:'testing',en:'Laboratory testing',ar:'التحاليل المعملية',focusEn:'specimen handling, testing workflows and result documentation',focusAr:'تداول العينات وإجراءات الفحص وتوثيق النتائج'},
    {id:'quality',en:'Laboratory quality',ar:'جودة المختبر',focusEn:'quality control, traceability and safe lab procedures',focusAr:'ضبط الجودة والتتبع وإجراءات السلامة'}
  ],
  'hospitality': [
    {id:'guest',en:'Guest services',ar:'خدمات الضيوف',focusEn:'guest communication, service recovery and reservations',focusAr:'التواصل مع الضيوف ومعالجة شكاوى الخدمة والحجوزات'},
    {id:'culinary',en:'Culinary',ar:'فنون الطهي',focusEn:'food preparation, kitchen organization and food safety',focusAr:'إعداد الطعام وتنظيم المطبخ وسلامة الغذاء'}
  ],
  'legal services': [
    {id:'research',en:'Legal research',ar:'البحث القانوني',focusEn:'case research, legal writing and evidence organization',focusAr:'البحث في القضايا والصياغة القانونية وتنظيم الأدلة'},
    {id:'contracts',en:'Contracts',ar:'العقود',focusEn:'contract review, document consistency and risk awareness',focusAr:'مراجعة العقود واتساق المستندات والوعي بالمخاطر'}
  ]
};
function tracksFor(job: string): Track[] {
  const career = careers.find(item => item.match.test(job)) || general;
  const domain = career.name.en.includes('nursing') ? 'nursing' : career.name.en;
  return trackLibrary[domain] || [{
    id:'role',en:'Role-specific focus',ar:'تخصص المسمى الوظيفي',
    focusEn:career === general ? 'core responsibilities associated with the stated role' : career.focus.en,
    focusAr:career === general ? 'المهام الأساسية المرتبطة بالمسمى المذكور' : career.focus.ar
  }];
}
function inferredTrack(job: string, tracks: Track[]): string {
  const lower = job.toLowerCase();
  const matches: Record<string, RegExp> = {
    financial:/financial|مالي/,cost:/cost|تكاليف/,audit:/audit|مراجع|تدقيق/,
    emergency:/emergency|trauma|طوارئ/,icu:/icu|critical|intensive|عناية|حرجة/,
    frontend:/frontend|front.end|react|واجهات/,backend:/backend|back.end|api|خلفية/,
    mobile:/mobile|android|ios|هاتف/,civil:/civil|مدني/,mechanical:/mechanical|ميكانيك/,
    electrical:/electrical|كهرباء/,seo:/seo|search engine|سيو|محركات/,
    digital:/digital|رقمي/,b2b:/b2b|corporate|شركات/,recruitment:/recruit|talent|توظيف/,
    technical:/technical|فني/,procurement:/procure|purchase|مشتريات/,
    inventory:/inventory|warehouse|مخزون/,uiux:/ux|ui\/|تجربة المستخدم/,
    visual:/graphic|بصري|جرافيك/,clinical:/clinical|إكلينيك|سرير/,
    public:/public health|صحة عامة/,training:/trainer|مدرب|تدريب/,
    projects:/project|مشروع/,quality:/quality|جودة/,culinary:/chef|cook|طباخ|شيف/,
    contracts:/contract|عقود/
  };
  return tracks.find(t => matches[t.id]?.test(lower))?.id || tracks[0].id;
}
function inferredLevel(job: string): Seniority {
  if (/senior|lead|principal|head of|manager|director|supervisor|خبير|أول|مدير|مشرف|رئيس/i.test(job)) return 'senior';
  if (/junior|intern|trainee|entry.level|fresh graduate|مبتدئ|متدرب|حديث التخرج/i.test(job)) return 'entry';
  return 'mid';
}
function makeSuggestions(job: string, lang: Lang, track: Track, level: Seniority, skills: string, evidence: string) {
  if (!job.trim()) return [];
  const focus = lang === 'ar' ? track.focusAr : track.focusEn;
  const seniority = lang === 'ar'
    ? ({entry:'في بداية المسار المهني',mid:'في مجال العمل',senior:'في دور متقدم'} as const)[level]
    : ({entry:'early-career',mid:'career-focused',senior:'senior-level'} as const)[level];
  const skill = skills.trim().slice(0, 110);
  const fact = evidence.trim().slice(0, 150);
  const skillFact = skill ? (lang === 'ar' ? ' المهارات المذكورة: ' : ' Stated skills: ') + skill + '.' : '';
  const outcomeFact = fact ? (lang === 'ar' ? ' من الإنجازات المذكورة: ' : ' Provided achievement: ') + fact + '.' : '';
  if (lang === 'ar') return [
    job + ' ' + seniority + '، يركز على ' + focus + '.' + skillFact + outcomeFact,
    'مهتم بدور ' + job + ' مع تركيز مهني على ' + focus + ' والتواصل الواضح والعمل المنظم.' + skillFact + outcomeFact,
    'ملخص مهني لوظيفة ' + job + ': الاهتمام بـ' + focus + ' وتنفيذ المهام بدقة.' + skillFact + outcomeFact
  ];
  return [
    job + ' with a ' + seniority + ' focus on ' + focus + '.' + skillFact + outcomeFact,
    'Professional in the ' + job + ' field, focusing on ' + focus + ' through organized work and clear communication.' + skillFact + outcomeFact,
    'Role-focused ' + job + ' profile emphasizing ' + focus + ' and reliable collaboration.' + skillFact + outcomeFact
  ];
}
""" + source[end:]

once("  const [lang, setLang] = useState<Lang>('en');",
"""  const [lang, setLang] = useState<Lang>('en');
  const [trackChoice, setTrackChoice] = useState('auto');
  const [levelChoice, setLevelChoice] = useState<'auto' | Seniority>('auto');
  const [skills, setSkills] = useState('');
  const [achievement, setAchievement] = useState('');""", "state")
once("target.current = null; setMount(null); setRole(''); setOpen(false);",
"""target.current = null; setMount(null); setRole(''); setOpen(false);
          setTrackChoice('auto'); setLevelChoice('auto'); setSkills(''); setAchievement('');""", "route cleanup")
once("        setRole(currentTitle);\n      }\n      const summary",
"""        setRole(currentTitle);
        setTrackChoice('auto'); setLevelChoice('auto');
      }
      const summary""", "role change")
once("        // Show ready-to-choose templates directly in the Summary step.\n        setOpen(Boolean(currentTitle || titleRef.current));",
"""        // Suggestions are opt-in: avoid an oversized panel on mobile.
        setOpen(false);""", "disable auto open")
once("        if (target.current) setOpen(Boolean(title));",
"""        setTrackChoice('auto');
        setLevelChoice('auto');
        // Do not pop open while someone is editing their title.""", "input auto open")
once("  const options = useMemo(() => role.trim() ? makeSuggestions(role.trim(), lang) : [], [role, lang]);",
"""  const tracks = useMemo(() => tracksFor(role), [role]);
  const trackId = trackChoice === 'auto' ? inferredTrack(role, tracks) : trackChoice;
  const track = tracks.find(item => item.id === trackId) || tracks[0];
  const level = levelChoice === 'auto' ? inferredLevel(role) : levelChoice;
  const options = useMemo(() =>
    makeSuggestions(role.trim(), lang, track, level, skills, achievement),
    [role, lang, track, level, skills, achievement]);""", "derived suggestions")
once("trigger:'عرض الملخصات المقترحة', title:'اختر الملخص المهني المناسب', role:'المسمى الوظيفي',",
     "trigger:'✨ اقتراحات مخصصة للملخص', title:'ملخصات مخصصة لوظيفتك', role:'المسمى الوظيفي',", "Arabic labels")
once("trigger:'Show suggested summaries', title:'Choose your professional summary', role:'Professional title',",
     "trigger:'✨ Get specific suggestions', title:'Role-specific summary suggestions', role:'Professional title',", "English labels")
once("        <p>{t.help}</p>\n        {options.length",
"""        {role.trim() && <div className="sirati-summary-pro-controls">
          <label>{lang === 'ar' ? 'التخصص' : 'Specialization'}
            <select aria-label="Summary specialization" value={track.id}
              onChange={event => setTrackChoice(event.target.value)}>
              {tracks.map(item => <option key={item.id} value={item.id}>{item[lang]}</option>)}
            </select>
          </label>
          <label>{lang === 'ar' ? 'مستوى الخبرة' : 'Experience level'}
            <select aria-label="Summary experience level" value={level}
              onChange={event => setLevelChoice(event.target.value as Seniority)}>
              <option value="entry">{lang === 'ar' ? 'مبتدئ' : 'Entry level'}</option>
              <option value="mid">{lang === 'ar' ? 'متوسط' : 'Mid level'}</option>
              <option value="senior">{lang === 'ar' ? 'متقدم' : 'Senior'}</option>
            </select>
          </label>
          <details className="sirati-summary-pro-facts">
            <summary>{lang === 'ar' ? 'إضافة مهارات وإنجازات حقيقية (اختياري)' : 'Add verified skills & achievements (optional)'}</summary>
            <label>{lang === 'ar' ? 'مهاراتك التي ذكرتها' : 'Your actual skills'}
              <input aria-label="Summary actual skills" maxLength={110} value={skills}
                onChange={event => setSkills(event.target.value)} placeholder={lang === 'ar' ? 'اكتب مهاراتك الفعلية' : 'Only skills you can verify'} />
            </label>
            <label>{lang === 'ar' ? 'إنجاز مثبت من خبرتك' : 'An actual achievement'}
              <input aria-label="Summary actual achievement" maxLength={150} value={achievement}
                onChange={event => setAchievement(event.target.value)} placeholder={lang === 'ar' ? 'اكتب إنجازك الحقيقي' : 'Only an achievement you can verify'} />
            </label>
          </details>
        </div>}
        {options.length""", "opt-in specialization and facts")
once("        <small>{t.safety}</small>", """        <small>{t.safety} {lang === 'ar'
          ? 'التخصص يحدد نوع الصياغة فقط ولا يثبت خبرة أو إنجازًا.'
          : 'Specialization controls wording, not evidence of experience.'}</small>""", "safe helper")

path.write_text(source, encoding="utf-8")
style = css_path.read_text(encoding="utf-8")
if "/* Smart CV Pro V4 */" in style:
    raise RuntimeError("V4 already applied")
style += r"""
/* Smart CV Pro V4 */
@media screen {
  .sirati-summary-trigger {
    width: fit-content; max-width: 100%; padding: 8px 12px;
    min-height: 42px; background: #f0f5f1; color: #174637;
    border: 1px solid #bcd4c4; border-radius: 11px;
    font-size: 13px; font-weight: 750;
  }
  .sirati-summary-panel { gap: 10px; border-color: #dce9de; box-shadow: 0 7px 22px rgba(23,58,40,.07); }
  .sirati-summary-pro-controls { display: grid; grid-template-columns: repeat(2,minmax(0,1fr)); gap: 9px; }
  .sirati-summary-pro-controls label { display: grid; gap: 5px; min-width: 0; font-size: 12px; font-weight: 700; color: #325541; }
  .sirati-summary-pro-controls select, .sirati-summary-pro-controls input {
    width: 100%; min-width: 0; min-height: 42px; padding: 8px 10px;
    border: 1px solid #c1d1c5; border-radius: 9px;
    color: #1a392b; background: #fff; font: inherit; font-size: 13px;
  }
  .sirati-summary-pro-facts { grid-column: 1 / -1; border: 1px solid #e3ede5; border-radius: 10px; padding: 9px; }
  .sirati-summary-pro-facts summary { cursor: pointer; font-size: 12px; color: #305c46; font-weight: 700; }
  .sirati-summary-pro-facts[open] { display: grid; gap: 10px; }
  .sirati-summary-pro-facts[open] summary { margin-bottom: 4px; }
  .sirati-summary-panel .sirati-summary-choices { gap: 7px; }
  .sirati-summary-panel .sirati-summary-choice { padding: 10px; }
  .sirati-summary-panel :is(select,input):focus-visible { outline: 2px solid #5a9575; outline-offset: 2px; }
}
@media screen and (max-width: 390px) {
  .sirati-summary-pro-controls { grid-template-columns: 1fr; }
  .sirati-summary-panel { padding: 10px; }
  .sirati-summary-panel .sirati-summary-head strong { font-size: 14px; }
}
"""
css_path.write_text(style, encoding="utf-8")
print("PASS: Smart CV Pro V4 opt-in, role + specialization + seniority + user-verified facts.")
