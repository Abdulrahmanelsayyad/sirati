// Run against generated TypeScript and actual Smart CV V7 functions, not duplicate matchers.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(process.argv[2] || '.');
const ts = require(path.join(root, 'node_modules/typescript'));
const code = fs.readFileSync(path.join(root, 'components/PersonalSummaryPicker.tsx'), 'utf8');
assert(code.includes('sirati-summary-v7-guidance'), 'Missing specific-facts guidance');
assert(code.includes('These are prompts, not claims about your experience.'));
assert(code.includes('هذه ليست خبرات مؤكدة عنك.'));
const start = code.indexOf('function makeSuggestions(');
const end = code.indexOf('export default function PersonalSummaryPicker()', start);
assert(start >= 0 && end > start, 'Could not locate generated Smart CV functions');

const compiled = ts.transpileModule(code.slice(start, end) +
  '\n({makeSuggestions, analyzeJobPosting, hasKeyword});',
  {compilerOptions: {target: ts.ScriptTarget.ES2020}}).outputText;
const {makeSuggestions, analyzeJobPosting, hasKeyword} = vm.runInNewContext(compiled);

const compare = (actual, expected) => assert.deepEqual(Array.from(actual), expected);
const ar = analyzeJobPosting(
  'مطلوب محاسب يجيد Excel والتسويات المحاسبية والتقارير المالية',
  'أستخدم الإكسل في العمل', '', 'ar');
compare(ar.matched, ['إكسل']);
compare(ar.notInEvidence, ['التقارير المالية', 'التسويات المحاسبية']);

const en = analyzeJobPosting(
  'Accountant: Excel, SAP, bank reconciliation, financial reporting',
  'اكسل، ساب', '', 'en');
compare(en.matched, ['Excel', 'SAP']);
compare(en.notInEvidence, ['Financial reporting','Reconciliation']);

const nursing = analyzeJobPosting(
  'Emergency nurse: triage, patient safety, infection control, ACLS',
  'سلامة المرضى، مكافحة العدوى', '', 'ar');
compare(nursing.matched, ['سلامة المرضى','مكافحة العدوى']);
compare(nursing.notInEvidence, ['فرز المرضى','الإنعاش المتقدم ACLS']);

const diacritics = analyzeJobPosting(
  'مُكافحة العَدوى مطلوبة', 'مكافحة العدوى', '', 'ar');
compare(diacritics.matched, ['مكافحة العدوى']);

assert.equal(hasKeyword('excelled', 'Excel'), false, 'Substring false positive');
assert.equal(hasKeyword('ABLS', 'BLS'), false, 'Abbreviation false positive');
assert.equal(hasKeyword('Power-BI', 'Power BI'), true, 'Hyphen separator');
compare(analyzeJobPosting('Excel and SQL', '', '', 'en').matched, []);
compare(analyzeJobPosting('', 'Excel', '', 'en').matched, []);

const track = {focusEn:'ledger reconciliations and financial reporting',
  focusAr:'التسويات والتقارير المالية'};
const noFacts = makeSuggestions('Accountant','en',track,'mid','','','','Excel SAP');
assert.equal(noFacts.length, 3);
assert(!noFacts.join(' ').includes('SAP'), 'Job posting was inserted as factual skill');
assert(!noFacts.join(' ').includes('Skills you entered:'), 'Invented user evidence');
const confirmed = makeSuggestions('Accountant','en',track,'mid','Excel','','','Excel SAP');
assert(confirmed[0].includes('Terms you entered relevant to the job ad: Excel.'));
assert(!confirmed[0].includes('relevant to the job ad: SAP.'));
const Arabic = makeSuggestions('محاسب','ar',track,'mid','إكسل','','','Excel SAP');
assert(Arabic[0].includes('مصطلحات أدخلتها ذات صلة بالإعلان: إكسل.'));
assert(Arabic[2].startsWith('أسعى إلى '), 'Arabic career direction regression');
assert(!code.includes('ATS score: '), 'This is not an ATS scoring product');

console.log('PASS: Smart CV V7 Arabic/English facts match, role specificity, boundaries, privacy and summary safety');
