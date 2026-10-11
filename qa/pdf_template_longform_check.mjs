// Exact shared CvPreview/exporter: real templates, synthetic content, no account mocks.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { chromium } from 'playwright';
import { getDocument } from 'pdfjs-dist/legacy/build/pdf.mjs';
const base=process.env.QA_PDF_BASE_URL;
assert(['http://127.0.0.1:4175/sirati','http://127.0.0.1:4174/sirati'].includes(base));
const folder=process.env.QA_PDF_RESULTS_DIR||'/tmp/sirati-pdf-template-long-candidate';
const smoke=process.env.QA_PDF_LONG_SMOKE==='1';
fs.mkdirSync(folder,{recursive:true});
const browser=await chromium.launch({headless:true});
const results=[];
try {
  const page=await browser.newPage();
  await page.goto(base+'/qa-pdf-sections/');
  for(const width of (smoke?[360]:[360,390,1440])) {
    await page.setViewportSize({width,height:1000});
    await page.getByLabel('Documents rendering').setChecked(width===1440);
    for(const language of (smoke?['en']:['en','ar'])) {
      await page.getByLabel('Language',{exact:true}).selectOption(language);
      for(const template of (smoke?['modern']:['modern','classic','compact','compact-ats','healthcare-pro','executive-ats','profile-sidebar','gold-sidebar','executive-letterhead'])) {
        await page.getByLabel('Template',{exact:true}).selectOption(template);
        // Tune the synthetic line count to approximately 2, 3 and 5 A4 pages.
        for(const target of (smoke?[3]:[2,3,5])) {
          let lines=target*35;
          for(let attempt=0;attempt<4;attempt++) {
            await page.getByLabel('Long fixture lines').fill(String(lines));
            await page.waitForFunction(n=>document.querySelector('.cv-sheet')?.textContent?.includes('BoundaryToken'+String(n-1).padStart(3,'0')),lines);
            // Measure the A4 export clone, not the scaled responsive preview.
            const ratio=await page.locator('.cv-sheet').evaluate(async el=>{
              await document.fonts.ready;
              const stage=document.createElement('div');
              stage.className='sirati-pdf-offscreen';
              stage.style.cssText='position:fixed;left:-20000px;top:0;width:210mm;pointer-events:none';
              const copy=el.cloneNode(true);
              for(const [key,value] of [['width','210mm'],['max-width','none'],['transform','none'],['margin','0'],['box-sizing','border-box']]) copy.style.setProperty(key,value,'important');
              stage.appendChild(copy);document.body.appendChild(stage);
              try{return copy.scrollHeight/(copy.getBoundingClientRect().width*841.8898/595.2756);}
              finally{stage.remove();}
            });
            if(ratio>target-0.75&&ratio<target-0.15) break;
            lines=Math.max(1,Math.round(lines*(target-0.4)/ratio));
          }
          const id=`${template}-${language}-${width}-target${target}`;
          const download=page.waitForEvent('download',{timeout:60000});
          await page.getByRole('button',{name:'Download fixture'}).click();
          const path=`${folder}/${id}.pdf`;
          await (await download).saveAs(path);
          const doc=await getDocument({data:new Uint8Array(fs.readFileSync(path))}).promise;
          const errors=[];
          if(doc.numPages<target||doc.numPages>target+1) errors.push('Unexpected page count '+doc.numPages);
          let text='';
          for(let n=1;n<=doc.numPages;n++) {
            const p=await doc.getPage(n),v=p.getViewport({scale:1});
            assert(Math.abs(v.width-595.28)<2&&Math.abs(v.height-841.89)<2,id+' non-A4');
            const chunk=(await p.getTextContent()).items.map(i=>i.str||'').join(' ');
            assert(chunk.trim().length>15,id+' blank page '+n);
            text+=chunk+' ';
          }
          for(let n=0;n<lines;n++) {
            const token='BoundaryToken'+String(n).padStart(3,'0');
            const count=text.split(token).length-1;
            if(count!==1) errors.push((count===0?'Missing ':'Duplicated ')+token);
          }
          const status=errors.length?'FAIL':'PASS';
          results.push({id,status,pages:doc.numPages,lines,sizeBytes:fs.statSync(path).size,errors});
          console.log(status,id,doc.numPages,'pages',lines,'paragraphs',errors.join('; '));
          await doc.destroy();
        }
      }
    }
  }
  assert.equal(results.length,smoke?1:162);
  fs.writeFileSync(folder+'/results.json',JSON.stringify(results,null,2));
  const failed=results.filter(r=>r.status==='FAIL');
  assert.equal(failed.length,0,failed.length+' long-template cases failed; see results.json');
} finally {await browser.close();}
