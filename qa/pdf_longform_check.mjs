import * as qaPath from 'node:path';
const qaRoot = qaPath.resolve(process.env.SIRATI_QA_ARTIFACT_DIR || 'qa-artifacts');
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { chromium } from 'playwright';
import { getDocument } from 'pdfjs-dist/legacy/build/pdf.mjs';

const base=process.env.QA_PDF_BASE_URL || 'http://127.0.0.1:4173';
const dir=process.env.QA_PDF_RESULTS_DIR || qaPath.join(qaRoot, "sirati-pdf-long");
fs.mkdirSync(dir,{recursive:true});
const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:390,height:844}});
const cases=[
  {mode:'en1',min:1,max:1,token:'Professional',minRepeated:5},
  {mode:'en2',min:2,max:3,token:'Professional',minRepeated:25},
  {mode:'ar3',min:3,max:8,token:'الخبرة',minRepeated:75},
  {mode:'short',min:1,max:1,token:'SOFTWARE',minRepeated:0},
];
const results=[];
try {
  await page.goto(base+'/qa-pdf-ats/');
  for(const item of cases) {
    await page.getByLabel('PDF sample scenario').selectOption(item.mode);
    const id='long-'+item.mode;
    const outcome=await Promise.race([
      page.waitForEvent('download',{timeout:60000}).then(d=>({download:d})),
      page.waitForFunction(()=>document.querySelector('[role=alert]')?.textContent,
        {timeout:60000}).then(()=>({error:true})),
      page.getByRole('button',{name:'QA Download searchable PDF'}).click()
        .then(()=>new Promise(()=>{})),
    ]);
    if(outcome.error)throw Error(id+': '+await page.locator('[role=alert]').innerText());
    const path=dir+'/'+id+'.pdf';
    await outcome.download.saveAs(path);
    const pdf=await getDocument({data:new Uint8Array(fs.readFileSync(path)),useSystemFonts:true}).promise;
    assert(pdf.numPages>=item.min && pdf.numPages<=item.max,
      id+' unexpected pages '+pdf.numPages);
    let text='';
    for(let n=1;n<=pdf.numPages;n++){
      const p=await pdf.getPage(n);
      const v=p.getViewport({scale:1});
      assert(Math.abs(v.width-595.28)<2 && Math.abs(v.height-841.89)<2,id+' not A4');
      const chunk=(await p.getTextContent()).items.map(i=>i.str||'').join(' ');
      assert(chunk.trim().length>15,id+' page '+n+' has no searchable text');
      text+=chunk+' ';
    }
    assert(text.includes(item.token),id+' lost native Unicode '+item.token);
    const repeats=text.split(item.token).length-1;
    if(item.minRepeated)assert(repeats>=item.minRepeated,
      id+' lost paragraph text: only '+repeats+' tokens');
    const result={id,pages:pdf.numPages,sizeBytes:fs.statSync(path).size,repeats};
    results.push(result);console.log('PASS',JSON.stringify(result));
    await pdf.destroy();
  }
  fs.writeFileSync(dir+'/results.json',JSON.stringify(results,null,2));
} finally {await browser.close();}
