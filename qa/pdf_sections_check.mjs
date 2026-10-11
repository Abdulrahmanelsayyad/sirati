import { chromium } from 'playwright';
import { getDocument } from 'pdfjs-dist/legacy/build/pdf.mjs';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const browser=await chromium.launch({headless:true});
const page=await browser.newPage();
const base=process.env.QA_PDF_BASE_URL || 'http://127.0.0.1:4173';
const dir = process.env.QA_PDF_RESULTS_DIR || '/tmp/sirati-pdf-section-qa';
fs.mkdirSync(dir,{recursive:true});
const results=[];
try {
await page.goto(base+'/qa-pdf-sections/');
for(const width of (process.env.QA_SMOKE ? [390] : (process.env.QA_PDF_ALL_WIDTHS ? [1440,390,360] : [1440,390]))){
await page.setViewportSize({width,height:1000});
for(const language of (process.env.QA_SMOKE ? ['ar'] : ['en','ar'])){
await page.getByLabel('Language',{exact:true}).selectOption(language);
for(const template of (process.env.QA_SMOKE ? ['gold-sidebar'] : ['modern','classic','compact','compact-ats','healthcare-pro','executive-ats','profile-sidebar','gold-sidebar','executive-letterhead'])){
await page.getByLabel('Template',{exact:true}).selectOption(template);
await page.getByLabel('Documents rendering').setChecked(width===1440);
const id=`${template}-${language}-${width}`;
const expected=language==='en'?['SummaryMarker','ExperienceMarker','EducationMarker','CertificationMarker','CourseMarker','ProjectMarker','SkillsMarker','LanguagesMarker']:['ملخص','خبرة','درجة','شهادة','دورة','مشروع','مهارات','اللغة'];
const dom=await page.locator('.cv-sheet').innerText();
for(const token of expected) assert(dom.includes(token),id+' DOM missing '+token);
const downloadStartedAt = performance.now();
const outcome=await Promise.race([
page.waitForEvent('download',{timeout:60000}).then(d=>({d})),
page.waitForFunction(()=>document.querySelector('[role=alert]')?.textContent,{timeout:60000}).then(()=>({error:true})),
page.getByRole('button',{name:'Download fixture'}).click().then(()=>new Promise(()=>{}))]);
if(outcome.error)throw Error(id+' '+await page.locator('p[role=alert]').innerText());
const elapsedMs = Math.round(performance.now() - downloadStartedAt);
const path=dir+'/'+id+'.pdf'; await outcome.d.saveAs(path);
const sizeBytes = fs.statSync(path).size;
assert(sizeBytes > 800 && sizeBytes < 3_500_000,
  id+' PDF output is empty or unexpectedly large: '+sizeBytes+' bytes');
const pdf=await getDocument({data:new Uint8Array(fs.readFileSync(path)),useSystemFonts:true}).promise;
let text='';
for(let n=1;n<=pdf.numPages;n++){const p=await pdf.getPage(n);const v=p.getViewport({scale:1});assert(Math.abs(v.width-595.28)<2&&Math.abs(v.height-841.89)<2);text+=(await p.getTextContent()).items.map(i=>i.str||'').join(' ')+' ';}
for(const token of expected)assert(text.includes(token),id+' PDF missing '+token);
fs.writeFileSync(path+'.txt',text); results.push({id,pages:pdf.numPages,sections:expected.length,sizeBytes,elapsedMs});console.log('PASS',id,pdf.numPages,'pages',expected.length,'sections',sizeBytes,'bytes',elapsedMs,'ms');await pdf.destroy();
}
}
}
fs.writeFileSync(dir+'/results.json',JSON.stringify(results,null,2));
}finally{await browser.close();}
