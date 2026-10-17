const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { randomUUID } = require('node:crypto');
const root = path.resolve(process.argv[2]);
const ts = require(path.join(root,'node_modules/typescript'));
function load(file, globals={}, newline='\n') {
  const mod={exports:{}};
  // Pure helpers need no UI imports; generated source can use LF or Windows CRLF.
  const source=fs.readFileSync(path.join(root,file),'utf8').replace(/\r?\n/g,newline).replace(/^import .*;\r?\n/gm,'');
  vm.runInNewContext(ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.ReactJSX,target:ts.ScriptTarget.ES2020}}).outputText,{exports:mod.exports,module:mod,require:n=>n==='react/jsx-runtime'?{}:require(n),crypto:{randomUUID},...globals});
  return mod.exports;
}
for (const newline of ['\n','\r\n']) {
const {extractDocumentCvFacts}=load('lib/documentCvExtraction.ts',{},newline);
const {applyReviewedFacts}=load('components/DocumentImportReview.tsx',{},newline);
const facts=extractDocumentCvFacts('Name: Sample Person\nJob title: Nurse\nEmail: qa@example.invalid\nPhone: +20 100 123 4567\nEducation: Bachelor of Nursing, 2020\nExperience: Nurse at Test Hospital, 2022–2024\nCertification: BLS\nجامعة اختبار ٢٠٢٠','synthetic.txt');
for(const kind of ['name','title','email','phone','education','experience','certification','date']) assert(facts.some(f=>f.field===kind),kind);
assert(facts.every(f=>f.requiresReview && f.evidence.fileName==='synthetic.txt'));
const empty={fullName:'',title:'',email:'',phone:'',location:'',linkedin:'',photoDataUrl:'',profile:'Keep original summary',skills:'Keep skills',languages:'',education:[],experience:[],certifications:[],courses:[],projects:[]};
const filled=applyReviewedFacts(empty,facts);
assert.equal(filled.fullName,'Sample Person');assert.equal(filled.title,'Nurse');assert.equal(filled.education[0].period,'');assert.equal(filled.experience[0].role,'');assert.equal(filled.certifications[0].name,'BLS');
assert.equal(empty.education.length,0);assert.equal(filled.profile,empty.profile);
const again=applyReviewedFacts(filled,facts);assert.equal(again.education.length,filled.education.length);assert.equal(again.experience.length,1);assert.equal(again.certifications.length,1);
assert.equal(applyReviewedFacts({...empty,email:'keep@example.invalid'},facts).email,'keep@example.invalid');
assert.equal(applyReviewedFacts(empty,[]).fullName,'');
assert.equal(extractDocumentCvFacts('Invent 90% sales growth','x').length,0);
console.log('PASS ('+(newline==='\n'?'LF':'CRLF')+'): explicit bilingual evidence extraction; no invented roles/dates; immutable apply; existing fields preserved; duplicate entries prevented.');
}
