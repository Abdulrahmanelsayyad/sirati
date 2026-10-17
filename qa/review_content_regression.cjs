const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(process.argv[2]),ts=require(path.join(root,'node_modules/typescript'));
const read=f=>fs.readFileSync(path.join(root,f),'utf8');
function load(file,stub=()=>{throw Error('unexpected import')}) {const mod={exports:{}}; vm.runInNewContext(ts.transpileModule(read(file),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020,jsx:ts.JsxEmit.ReactJSX}}).outputText,{module:mod,exports:mod.exports,require:stub});return mod.exports;}
const c=load('lib/careerReviewContent.ts');
for(const lang of ['en','ar']) {
 const text=c.linkedInDraft(lang,'Registered Nurse','Five years of emergency nursing.\nCoordinated handovers..','Triage, Documentation');
 assert(!text.includes('..'));assert(text.includes('Registered Nurse | Triage | Documentation'));assert(text.includes('Coordinated handovers.'));
 const questions=c.interviewQuestions('Registered Nurse','Emergency care','senior',lang).join(' ');
 assert(lang==='en'?questions.includes('SBAR')&&questions.includes('arrivals')&&questions.includes('delegate'):questions.includes('SBAR')&&questions.includes('الواصلة')&&questions.includes('تفوض'));
 const emergency=c.interviewQuestions('Registered Nurse','Emergency care','senior',lang);
 const intensive=c.interviewQuestions('Registered Nurse','ICU','mid',lang);
 const pediatrics=c.interviewQuestions('Registered Nurse','Pediatric','entry',lang);
 const general=c.interviewQuestions('Registered Nurse','','',lang);
 assert(emergency.length>=general.length+4,'Emergency nursing must have a true specialty question bank');
 assert(intensive.length>=general.length+4,'ICU nursing must have a true specialty question bank');
 assert(pediatrics.length>=general.length+3,'Pediatrics must have age-appropriate specialist questions');
 assert(lang==='en'?intensive.join(' ').includes('desaturates'):intensive.join(' ').includes('الأكسجين'));
 assert(lang==='en'?pediatrics.join(' ').includes('weight-based'):pediatrics.join(' ').includes('الوزن'));
}
assert(c.linkedInDraft('en','Nurse','Five years of emergency nursing.','').startsWith('HEADLINE:\nNurse | Five years of emergency nursing'));
assert(!c.interviewQuestions('ICU physician','','','en').join(' ').includes('medication safety'),'care setting does not imply nursing');
assert(c.interviewQuestions('Software Developer','','entry','en').join(' ').includes('production defect'));
assert(c.interviewQuestions('Teacher','','','en').join(' ').includes('learners'));
const neutral=c.profileDrafts('Registered Nurse','en','','unspecified','','','');
assert.equal(neutral.length,1);assert(!neutral[0].includes('triage'));assert(!neutral[0].includes('Mid'));
const drafts=c.profileDrafts('Nurse','en','Critical care','senior','Monitoring','Trained 3 colleagues.','ICU Educator');
assert.equal(new Set(drafts).size,4);assert(drafts[1].startsWith('Trained 3 colleagues.'));assert(drafts[2].startsWith('Seeking a role as ICU Educator.'));assert(!drafts.some(d=>d.includes('..')));
const dates=load('components/ExperienceDates.tsx',()=>({}));
assert(dates.parsePeriod('2020 — 2022').legacy);assert(dates.parsePeriod('٢٠٢٠ — الآن').legacy);
assert.equal(dates.parsePeriod('2022-01 — Present').current,true);assert.equal(dates.parsePeriod('2022-01 — 2024-02').end,'2024-02');
assert(dates.parsePeriod('2022-13 — Present').legacy);
const catalog=load('lib/templateCatalog.ts');assert.equal(catalog.TEMPLATE_COUNT,catalog.templateOptions.length);assert.equal(new Set(catalog.templateOptions.map(t=>t.id)).size,catalog.TEMPLATE_COUNT);
for(const file of ['app/page.tsx','app/templates/page.tsx','components/SiratiSiteMenu.tsx'])assert(read(file).includes('TEMPLATE_COUNT'));
assert(!read('components/SiratiSiteMenu.tsx').includes('تنزيل السيرة PDF'));
const source=read('app/builder/page.tsx');
const start=source.indexOf('    if (!hydrated || (!userId && !guestRestoreReady)');
const end=source.indexOf('\n  }, [hydrated,guestRestoreReady,userId,documentId]);',start);
const restore=source.slice(start,end);
function section({stored='8',userId=null,documentId=null,newCv=false,search='',blocked=false}={}) {
 let result=-1;const values=new Map();const sectionKey='sirati.builder.section:'+(userId||'guest')+':'+(documentId||'draft');if(stored!==null)values.set(sectionKey,stored);
 vm.runInNewContext('(function(){'+restore+'})()', {hydrated:true,guestRestoreReady:true,userId,documentId,isSessionBoundaryBlocked:()=>blocked,sectionKey,sessionStorage:{getItem:k=>values.get(k)??null,setItem:(k,v)=>values.set(k,v)},window:{location:{search}},URLSearchParams,newCvRequestedRef:{current:newCv},restoredSectionKey:{current:''},currentSection:8,setCurrentSection:v=>result=v});return result;
}
assert.equal(section(),8);assert.equal(section({stored:'-1'}),0);assert.equal(section({stored:'bad'}),0);assert.equal(section({newCv:true}),0);assert.equal(section({stored:null,userId:'other',documentId:'different'}),0);assert.equal(section({search:'?focus=smart'}),1);assert.equal(section({blocked:true}),-1);
console.log('PASS: factual EN/AR content, distinct evidence drafts, profession-specific interview bank, punctuation, legacy date parsing, one catalog and bounded section restore.');
