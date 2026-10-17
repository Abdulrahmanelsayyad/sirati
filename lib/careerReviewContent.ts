type Lang = 'en' | 'ar';
export const sentence = (text: string) => {
  const clean = text.trim().replace(/\.{2,}$/u, '.');
  return clean && !/[.!?؟۔]$/u.test(clean) ? clean + '.' : clean;
};
export function linkedInDraft(lang: Lang, role: string, facts: string, skills: string) {
  const items = [...new Set(skills.split(/[,،;\n]/).map(s => s.trim()).filter(Boolean))];
  // Only supplied facts/skills may become claims. No guessed seniority or credentials.
  const factHeadline = facts.trim().split(/[.!?\n]/u)[0].trim().slice(0, 100);
  const headline = [role.trim(), ...(items.length ? items.slice(0, 3) : factHeadline ? [factHeadline] : [])].join(' | ').slice(0, 220);
  const paragraphs = facts.trim().split(/\n+/).filter(Boolean).map(sentence);
  return (lang === 'ar' ? 'العنوان المهني:\n' : 'HEADLINE:\n') + headline +
    (lang === 'ar' ? '\n\nنبذة عني:\n' : '\n\nABOUT:\n') + sentence(role) + '\n\n' +
    paragraphs.join('\n\n') + (items.length ? '\n\n' + (lang === 'ar' ? 'مهاراتي: ' : 'Skills: ') + sentence(items.join(lang === 'ar' ? '، ' : ', ')) : '');
}
const banks: {match:RegExp; questions:[string,string][]}[] = [
  {match:/\bnurs(?:e|es|ing)\b|تمريض|ممرض/iu, questions:[
    ['How would you recognize deterioration and escalate concerns within your scope and local policy?', 'كيف تتعرف على تدهور الحالة وتصعّد مخاوفك ضمن اختصاصك وسياسة المنشأة؟'],
    ['Describe how you check medication safety and respond to a discrepancy.', 'كيف تتحقق من سلامة إعطاء الدواء وتتعامل مع اختلاف في البيانات؟'],
    ['What information would you prioritize in an SBAR handover?', 'ما المعلومات التي تعطيها الأولوية في تسليم الحالة باستخدام SBAR؟'],
    ['Give a real example of infection prevention or patient education in your work.', 'اذكر مثالًا حقيقيًا لمكافحة العدوى أو تثقيف المرضى في عملك.']]},
  {match:/developer|software|programmer|مبرمج|برمجيات/iu,questions:[
    ['Walk through diagnosing a production defect and verifying the fix.', 'اشرح تشخيص عطل في الإنتاج والتحقق من الإصلاح.'],
    ['How do you choose tests for a change and protect existing behavior?', 'كيف تختار اختبارات التعديل وتحافظ على السلوك الحالي؟'],
    ['Explain a design trade-off in code you actually wrote.', 'اشرح مفاضلة تصميمية في كود كتبته بالفعل.']]},
  {match:/accountant|accounting|محاسب/iu,questions:[
    ['How would you investigate an unreconciled balance?', 'كيف تفحص رصيدًا غير مطابق في التسويات؟'],
    ['Explain your checks during month-end close.', 'اشرح فحوصك خلال الإقفال الشهري.'],
    ['Describe a control that helps detect a posting error.', 'صف إجراء رقابيًا يساعد في كشف خطأ تسجيل.']]},
  {match:/teacher|educator|instructor|مدرس|معلم/iu,questions:[
    ['How would you adapt a lesson for learners with different starting levels?', 'كيف تكيّف الدرس لمتعلمين بمستويات مختلفة؟'],
    ['How do you check understanding and adjust your teaching?', 'كيف تتحقق من الفهم وتعدّل طريقة التدريس؟'],
    ['Describe a classroom challenge and your response.', 'صف تحديًا داخل الصف وطريقة تعاملك معه.']]},
  {match:/marketing|marketer|تسويق|مسوق/iu,questions:[
    ['How would you choose a campaign objective and measure its result?', 'كيف تختار هدف حملة وتقيس نتيجتها؟'],
    ['Describe how you would test two messages with the same audience.', 'كيف تختبر رسالتين لنفس الجمهور؟']]},
  {match:/sales|مبيعات/iu,questions:[
    ['How do you discover a customer need before proposing a solution?', 'كيف تحدد احتياج العميل قبل اقتراح حل؟'],
    ['Describe handling an objection without making unsupported promises.', 'صف التعامل مع اعتراض دون تقديم وعود غير مؤكدة.']]}
];
export function interviewQuestions(role:string, specialty:string, level:string, lang:Lang) {
  const pick = (pair:[string,string]) => pair[lang === 'ar' ? 1 : 0];
  const bank = banks.find(b => b.match.test(role));
  const questions = [pick(['Tell us about your background relevant to ' + role + '.', 'حدثنا عن خبرتك المناسبة لوظيفة ' + role + '.']), ...(bank?.questions || []).map(pick)];
  if (specialty.trim()) {
    const nursing = banks[0].match.test(role);
    if (nursing && /emergency|triage|طوارئ|فرز/iu.test(specialty)) questions.push(pick(['How would you prioritize simultaneous arrivals and communicate a change in urgency?', 'كيف ترتب أولوية الحالات الواصلة معًا وتبلّغ عن تغير درجة الإلحاح؟']));
    else if (nursing && /icu|critical|intensive|عناية|حرجة/iu.test(specialty)) questions.push(pick(['How would you verify a monitoring alarm and communicate your findings to the critical care team?', 'كيف تتحقق من إنذار المراقبة وتبلّغ النتائج لفريق الرعاية الحرجة؟']));
    else questions.push(pick(['Walk through a task in ' + specialty + ': risks, checks and escalation.', 'اشرح مهمة في ' + specialty + ': المخاطر والفحوص والتصعيد.']));
  }
  if (level === 'entry') questions.push(pick(['Use a training or placement example: when did you ask for supervision?', 'اذكر مثالًا من التدريب: متى طلبت الإشراف؟']));
  if (level === 'mid') questions.push(pick(['Describe an independent decision, its limits and when you sought help.', 'صف قرارًا اتخذته باستقلالية وحدوده ومتى طلبت المساعدة.']));
  if (level === 'senior') questions.push(pick(['Describe how you delegate, supervise and review team outcomes.', 'اشرح كيف تفوض وتشرف وتراجع نتائج الفريق.']));
  questions.push(pick(['Describe a real challenge using Situation, Task, Action and Result.', 'صف تحديًا حقيقيًا باستخدام الموقف والمهمة والإجراء والنتيجة.']), pick(['What would you ask this employer about the role?', 'ما الأسئلة التي ستوجهها لجهة العمل عن الوظيفة؟']));
  return questions;
}
export function profileDrafts(role:string, lang:Lang, focus:string, level:string, skills:string, evidence:string, target:string) {
  if (!role.trim()) return [];
  const ar=lang==='ar';
  const levelName:Record<string,string> = ar ? {entry:'مبتدئ',mid:'متوسط الخبرة',senior:'متقدم'} : {entry:'Entry level',mid:'Mid level',senior:'Senior level'};
  const identity = sentence([role.trim(),levelName[level]].filter(Boolean).join(' — '));
  const skillLine=skills.trim() ? sentence((ar?'مهاراتي: ':'Skills: ')+skills.trim()) : '';
  const fact=sentence(evidence);
  const focusLine=focus ? sentence((ar?'مجال اهتمامي: ':'Professional focus: ')+focus) : '';
  // Distinct content strategies, not twelve paraphrases of one unsupported claim.
  const drafts=[ [identity,skillLine,focusLine].filter(Boolean).join(' ') ];
  if(fact) drafts.push([fact,identity,skillLine].filter(Boolean).join(' '));
  if(target.trim()) drafts.push([sentence((ar?'أستهدف وظيفة ':'Seeking a role as ')+target.trim()),fact,skillLine].filter(Boolean).join(' '));
  if(skills.trim()) drafts.push([skillLine,identity,fact].filter(Boolean).join(' '));
  return [...new Set(drafts)];
}
