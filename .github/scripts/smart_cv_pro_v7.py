"""Smart CV V7: bilingual job-ad keyword evidence and specific, fact-first guidance.

Incremental generated UI patch applied after Smart CV V6.
No authentication, cloud storage, CV persistence, third-party API, or PDF changes.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
target = root / "components/PersonalSummaryPicker.tsx"
styles = root / "app/globals.css"
source = target.read_text(encoding="utf-8")

def replace_once(before: str, after: str, label: str) -> None:
    global source
    count = source.count(before)
    if count != 1:
        raise RuntimeError(f"Smart CV V7 {label}: expected one anchor, got {count}")
    source = source.replace(before, after, 1)

begin = source.index("const jobTerms = [")
end = source.index("\nexport default function PersonalSummaryPicker()", begin)
helper = r"""
type JobKeyword = {en:string; ar:string; aliases:string[]};
// Closed, local vocabulary: a job advertisement is NEVER itself evidence of skills.
// Each keyword has Arabic and English variants, with plain-language, non-scored output.
const JOB_KEYWORDS: JobKeyword[] = [
  {en:'Excel', ar:'إكسل', aliases:['Excel','إكسل','اكسل']},
  {en:'SAP', ar:'ساب SAP', aliases:['SAP','ساب']},
  {en:'Power BI', ar:'باور بي آي', aliases:['Power BI','باور بي آي']},
  {en:'SQL', ar:'SQL', aliases:['SQL']},
  {en:'Python', ar:'بايثون', aliases:['Python','بايثون']},
  {en:'React', ar:'React', aliases:['React']},
  {en:'TypeScript', ar:'TypeScript', aliases:['TypeScript']},
  {en:'JavaScript', ar:'JavaScript', aliases:['JavaScript']},
  {en:'API', ar:'واجهة برمجة التطبيقات', aliases:['API','واجهات البرمجة','واجهات برمجة التطبيقات']},
  {en:'Financial reporting', ar:'التقارير المالية', aliases:['financial reporting','financial statements','التقارير المالية','القوائم المالية']},
  {en:'Budgeting', ar:'إعداد الميزانيات', aliases:['budgeting','budget planning','إعداد الميزانيات','الموازنات','الميزانيات']},
  {en:'Reconciliation', ar:'التسويات المحاسبية', aliases:['reconciliation','reconciliations','bank reconciliation','التسويات','تسوية الحسابات','التسويات المحاسبية']},
  {en:'Cost accounting', ar:'محاسبة التكاليف', aliases:['cost accounting','محاسبة التكاليف']},
  {en:'Auditing', ar:'المراجعة والتدقيق', aliases:['auditing','internal audit','المراجعة','التدقيق']},
  {en:'Inventory management', ar:'إدارة المخزون', aliases:['inventory management','inventory control','إدارة المخزون','ضبط المخزون']},
  {en:'Project management', ar:'إدارة المشروعات', aliases:['project management','إدارة المشاريع','إدارة المشروعات']},
  {en:'Customer service', ar:'خدمة العملاء', aliases:['customer service','customer support','خدمة العملاء']},
  {en:'Salesforce', ar:'Salesforce', aliases:['Salesforce']},
  {en:'Digital marketing', ar:'التسويق الرقمي', aliases:['digital marketing','التسويق الرقمي']},
  {en:'SEO', ar:'تحسين محركات البحث', aliases:['SEO','search engine optimization','تحسين محركات البحث']},
  {en:'Data analysis', ar:'تحليل البيانات', aliases:['data analysis','تحليل البيانات']},
  {en:'Risk management', ar:'إدارة المخاطر', aliases:['risk management','إدارة المخاطر']},
  {en:'Communication', ar:'التواصل', aliases:['communication','التواصل']},
  {en:'Team leadership', ar:'قيادة الفريق', aliases:['team leadership','team management','قيادة الفريق','قيادة الفرق']},
  {en:'Patient safety', ar:'سلامة المرضى', aliases:['patient safety','سلامة المرضى']},
  {en:'Triage', ar:'فرز المرضى', aliases:['triage','فرز المرضى','الفرز']},
  {en:'Critical care', ar:'الرعاية الحرجة', aliases:['critical care','intensive care','الرعاية الحرجة','العناية المركزة']},
  {en:'Infection control', ar:'مكافحة العدوى', aliases:['infection control','infection prevention','مكافحة العدوى']},
  {en:'Patient assessment', ar:'تقييم المرضى', aliases:['patient assessment','تقييم المرضى']},
  {en:'Clinical documentation', ar:'التوثيق السريري', aliases:['clinical documentation','التوثيق السريري','التوثيق الطبي']},
  {en:'Quality assurance', ar:'ضمان الجودة', aliases:['quality assurance','ضمان الجودة']},
  {en:'BLS', ar:'الإنعاش الأساسي BLS', aliases:['BLS','basic life support','الإنعاش الأساسي']},
  {en:'ACLS', ar:'الإنعاش المتقدم ACLS', aliases:['ACLS','advanced cardiovascular life support','الإنعاش المتقدم']}
];
function normalizeKeywordText(value: string): string {
  return value.normalize('NFKC').toLowerCase()
    .replace(/[\u064B-\u065F\u0670\u0640]/g,'')
    .replace(/[أإآ]/g,'ا').replace(/ى/g,'ي');
}
function hasKeyword(haystack: string, alias: string): boolean {
  const term = normalizeKeywordText(alias)
    .replace(/[^\p{L}\p{N}\s-]/gu, '\\$&')
    .replace(/[\s-]+/g, '[\\s-]+');
  // An Arabic definite article is often attached (إكسل / الإكسل).
  const normAlias = normalizeKeywordText(alias);
  const prefix = /[\u0600-\u06FF]/u.test(normAlias) && !normAlias.startsWith('ال')
    ? '(?:ال)?' : '';
  return new RegExp('(?:^|[^\\p{L}\\p{N}])' + prefix + term +
    '(?=$|[^\\p{L}\\p{N}])', 'u')
    .test(normalizeKeywordText(haystack));
}
function analyzeJobPosting(posting: string, skills: string, achievement: string, lang: Lang) {
  if (!posting.trim()) return {matched:[] as string[], notInEvidence:[] as string[]};
  const ad = posting.slice(0,2000);
  const evidence = (skills + '\n' + achievement).slice(0,270);
  const detected = JOB_KEYWORDS
    .filter(item => item.aliases.some(alias => hasKeyword(ad,alias)))
    .slice(0,10);
  return {
    matched: detected.filter(item => item.aliases.some(alias => hasKeyword(evidence,alias)))
      .map(item => item[lang]),
    notInEvidence: detected.filter(item => !item.aliases.some(alias => hasKeyword(evidence,alias)))
      .map(item => item[lang])
  };
}
"""
source = source[:begin] + helper + source[end:]

replace_once("analyzeJobPosting(jobAd, skills, evidence).matched",
             "analyzeJobPosting(jobAd, skills, evidence, lang).matched", "summary matching")
replace_once("analyzeJobPosting(jobAd,skills,achievement)",
             "analyzeJobPosting(jobAd,skills,achievement,lang)", "UI matching")
replace_once("[jobAd,skills,achievement]);",
             "[jobAd,skills,achievement,lang]);", "language-aware memo")
replace_once("' Verified skills supplied: '", "' Skills you entered: '", "fact provenance")
replace_once("' مهارات مدخلة ذات صلة بالإعلان: '", "' مصطلحات أدخلتها ذات صلة بالإعلان: '", "Arabic provenance")
replace_once("' User-listed skills relevant to the job ad: '",
             "' Terms you entered relevant to the job ad: '", "English provenance")

choices = """        {options.length
          ? <div className="sirati-summary-choices">"""
guidance = """        {role.trim() && !skills.trim() && !achievement.trim() && (
          <p className="sirati-summary-v7-guidance" role="note">
            {lang === 'ar'
              ? 'لتحصل على ملخص أكثر تحديدًا لوظيفة ' + role +
                '، أضف مهارة تستخدمها بالفعل ونتيجة يمكنك إثباتها في خانة المهارات والإنجازات. أمثلة مجالات للتفكير فقط: ' +
                track.focusAr + '. هذه ليست خبرات مؤكدة عنك.'
              : 'To make your ' + role +
                ' summary more specific, add a skill you actually use and a result you can support in the optional facts fields. Possible areas to consider: ' +
                track.focusEn + '. These are prompts, not claims about your experience.'}
          </p>
        )}
"""
replace_once(choices, guidance + choices, "actionable facts guidance")

target.write_text(source, encoding="utf-8")
css = styles.read_text(encoding="utf-8")
if "/* Smart CV V7 bilingual facts */" in css:
    raise RuntimeError("Smart CV V7 already applied")
css += r"""
/* Smart CV V7 bilingual facts */
@media screen {
  .sirati-summary-v7-guidance {
    border: 1px solid #cbded2; border-inline-start: 4px solid #47805f;
    background: #f4f9f5; color: #234b38;
    border-radius: 10px; padding: 10px 12px; margin: 0;
    font-size: 12px; line-height: 1.65; overflow-wrap: anywhere;
  }
}
"""
styles.write_text(css, encoding="utf-8")
print("PASS: Smart CV V7 bilingual matching, no inferred skills and specific facts guidance.")
