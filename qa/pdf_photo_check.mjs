import assert from 'node:assert/strict';
import fs from 'node:fs';
import { chromium } from 'playwright';
import { getDocument } from 'pdfjs-dist/legacy/build/pdf.mjs';

const base = process.env.QA_PDF_BASE_URL || 'http://127.0.0.1:4173';
const dir = process.env.QA_PDF_RESULTS_DIR || '/tmp/sirati-pdf-photo';
fs.mkdirSync(dir,{recursive:true});
const browser = await chromium.launch({headless:true});
const page = await browser.newPage();
const results = [];
try {
  await page.goto(base+'/qa-pdf-sections/');
  await page.getByLabel('Portrait',{exact:true}).setChecked(true);
  for (const width of [390,1440]) {
    await page.setViewportSize({width,height:1000});
    for (const language of ['en','ar']) {
      await page.getByLabel('Language',{exact:true}).selectOption(language);
      for (const template of ['profile-sidebar','gold-sidebar']) {
        await page.getByLabel('Template',{exact:true}).selectOption(template);
        await page.getByLabel('Documents rendering').setChecked(width===1440);
        const id = 'photo-'+template+'-'+language+'-'+width;
        const photos = page.locator('.cv-sheet img');
        assert(await photos.count()>0, id+' did not render any CV portrait element');
        await page.waitForFunction(() => [...document.querySelectorAll('.cv-sheet img')]
          .some(img=>img.complete && img.naturalWidth>=64 && img.naturalHeight>=64),
          {timeout:12000});
        const outcome = await Promise.race([
          page.waitForEvent('download',{timeout:60000}).then(d=>({download:d})),
          page.waitForFunction(()=>document.querySelector('[role=alert]')?.textContent,
            {timeout:60000}).then(()=>({error:true})),
          page.getByRole('button',{name:'Download fixture'}).click()
            .then(()=>new Promise(()=>{})),
        ]);
        if(outcome.error) throw new Error(id+': '+await page.locator('p[role=alert]').innerText());
        const path=dir+'/'+id+'.pdf';
        await outcome.download.saveAs(path);
        const sizeBytes=fs.statSync(path).size;
        assert(sizeBytes>1200 && sizeBytes<4_000_000,id+' invalid image-backed PDF size');
        const pdf=await getDocument({data:new Uint8Array(fs.readFileSync(path)),
          useSystemFonts:true}).promise;
        assert(pdf.numPages>=1 && pdf.numPages<=3,id+' unexpected page count');
        let all='';
        for(let n=1;n<=pdf.numPages;n++){
          const p=await pdf.getPage(n);
          const v=p.getViewport({scale:1});
          assert(Math.abs(v.width-595.28)<2 && Math.abs(v.height-841.89)<2,id+' non-A4');
          all+=(await p.getTextContent()).items.map(i=>i.str||'').join(' ')+' ';
        }
        const tokens=language==='en'
          ? ['SummaryMarker','ExperienceMarker','EducationMarker','SkillsMarker']
          : ['ملخص','خبرة','درجة','مهارات'];
        for(const token of tokens)assert(all.includes(token),id+' lost text '+token);
        results.push({id,pages:pdf.numPages,sizeBytes});
        console.log('PASS',id,pdf.numPages,sizeBytes,'bytes and synthetic photo DOM');
        await pdf.destroy();
      }
    }
  }
  fs.writeFileSync(dir+'/results.json',JSON.stringify(results,null,2));
} finally {
  await browser.close();
}
