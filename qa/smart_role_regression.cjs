// Execute the generated recommendation tables, not a copy of their regexes.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(process.argv[2]);
const ts = require(path.join(root, 'node_modules/typescript'));
function classifier(file, end, expression) {
  const source = fs.readFileSync(path.join(root, 'components', file), 'utf8');
  const prefix = source.slice(0, source.indexOf(end)).replace(/^import .*;$/gm, '');
  return vm.runInNewContext(ts.transpileModule(prefix + '\n(job) => ' + expression,
    {compilerOptions:{target:ts.ScriptTarget.ES2020}}).outputText);
}
const skills = classifier('SmartContentSuggestions.tsx', 'type Props =',
  '(PACKS.find(p => p.match.test(job)) || GENERIC).label.en');
const summary = classifier('PersonalSummaryPicker.tsx', 'function cvLanguage()',
  '(careers.find(p => p.match.test(job)) || general).name.en');
const cases = [
  ['ICU physician','General professional','medicine'],
  ['طبيب عناية مركزة','General professional','medicine'],
  ['طبيب طوارئ','General professional','medicine'],
  ['ICU software developer','Software development','software development'],
  ['مبرمج أنظمة طوارئ','Software development','software development'],
  ['Critical care accountant','Accounting','accounting'],
  ['محاسب عناية مركزة','Accounting','accounting'],
  ['Nursery teacher','Education','education'],
  ['ICU','General professional','professional work'],
  ['طوارئ','General professional','professional work'],
  ['ICU nurse','Critical care nursing','critical care nursing'],
  ['Critical care nurse','Critical care nursing','critical care nursing'],
  ['ممرضة عناية مركزة','Critical care nursing','critical care nursing'],
  ['تمريض الرعاية الحرجة','Critical care nursing','critical care nursing'],
  ['Emergency nurse','Nursing','emergency nursing'],
  ['ممرضة طوارئ','Nursing','emergency nursing'],
  ['Registered nurse','Nursing','nursing'],
  ['ممرض','Nursing','nursing'],
  ['Software developer','Software development','software development'],
  ['مهندس مدني','Engineering','engineering'],
];
for (const [role, skill, career] of cases) {
  assert.equal(skills(role), skill, 'Skills: ' + role);
  assert.equal(summary(role), career, 'Summary: ' + role);
}
console.log('PASS: 20 EN/AR roles select appropriate skill/summary domains; care settings alone never imply nursing.');

// Run the generated summary function across vowel/consonant/abbreviated titles.
const summarySource = fs.readFileSync(path.join(root, 'components/PersonalSummaryPicker.tsx'), 'utf8');
const summaryFunctions = summarySource.slice(summarySource.indexOf('function makeSuggestions('), summarySource.indexOf('export default function PersonalSummaryPicker'));
const makeSuggestions = vm.runInNewContext(ts.transpileModule(summaryFunctions + '\nmakeSuggestions;',
  {compilerOptions:{target:ts.ScriptTarget.ES2020}}).outputText);
const track = {focusEn:'financial reporting',focusAr:'التقارير المالية'};
for (const role of ['Accountant','Engineer','Nurse','HR specialist','IT consultant']) {
  const suggestions = makeSuggestions(role,'en',track,'mid','','','','');
  assert(suggestions[2].startsWith('Seeking ' + role + ' opportunities,'));
  assert(!suggestions.join(' ').includes('Achievement supplied:'));
}
assert(makeSuggestions('Accountant','en',track,'mid','','','Finance Manager','')[2]
  .startsWith('Seeking Finance Manager opportunities,'));
assert(makeSuggestions('محاسب','ar',track,'mid','','','','')[2].startsWith('أسعى إلى '));
console.log('PASS: summary career wording across 5 titles, explicit target, and Arabic preservation.');
