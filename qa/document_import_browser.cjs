const assert = require('node:assert/strict');
const { chromium } = require('playwright');
const { PDFDocument, StandardFonts } = require('pdf-lib');
(async()=>{
 const pdf=await PDFDocument.create();const font=await pdf.embedFont(StandardFonts.Helvetica);const sheet=pdf.addPage();
 ['Name: PDF Test Person','Job title: Accountant','Email: pdf@example.invalid','Education: Bachelor of Accounting, 2020','Experience: Accountant at Test Company, 2021-2024','Certification: Accounting Diploma'].forEach((line,i)=>sheet.drawText(line,{x:30,y:760-i*24,size:12,font}));
 const bytes=Buffer.from(await pdf.save());
 const blank=await PDFDocument.create();blank.addPage();const blankBytes=Buffer.from(await blank.save());
 const oversized=await PDFDocument.create();for(let i=0;i<31;i++)oversized.addPage();const bigBytes=Buffer.from(await oversized.save());
 const browser=await chromium.launch({headless:true});
 try {
 const page=await browser.newPage({viewport:{width:390,height:844}});
 const requests=[];const errors=[];
 page.on('request',r=>{if(!['GET','HEAD'].includes(r.method())||!r.url().startsWith('http://127.0.0.1:4173/'))requests.push(r.url());});
 page.on('pageerror',e=>errors.push(e.message));
 const base='http://127.0.0.1:4173/sirati';
 await page.goto(base+'/import-documents/',{waitUntil:'networkidle'});
 await page.getByLabel('CV documents').setInputFiles({name:'sample.pdf',mimeType:'application/pdf',buffer:bytes});
 await page.getByLabel('Edit fact 1',{exact:true}).waitFor();
 assert.equal(await page.getByLabel('Edit fact 1',{exact:true}).inputValue(),'PDF Test Person');
 assert(await page.getByRole('button',{name:'Copy reviewed facts',exact:true}).isDisabled());
 await page.getByLabel('Approve fact 1',{exact:true}).check();
 await page.getByLabel('Edit fact 1',{exact:true}).fill('Corrected Person');
 assert(await page.getByRole('button',{name:'Copy reviewed facts',exact:true}).isDisabled());
 await page.getByLabel('Approve fact 1',{exact:true}).check();
 assert((await page.getByLabel('Approved CV facts').inputValue()).includes('Corrected Person'));
 for(const width of [360,390]){await page.setViewportSize({width,height:844});assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2));}
 await page.getByRole('button',{name:'العربية',exact:true}).click();assert(await page.getByRole('heading',{name:'استيراد مستندات السيرة الذاتية',exact:true}).isVisible());
 await page.getByRole('button',{name:'English',exact:true}).click();
 for (const [name,buffer,warning] of [['scan.pdf',blankBytes,/Scanned pages/],['long.pdf',bigBytes,/30-page limit/],['broken.pdf',Buffer.from('broken'),/Could not read this file locally/]]) {
  await page.getByLabel('CV documents').setInputFiles({name,mimeType:'application/pdf',buffer});await page.getByRole('status').filter({hasText:warning}).waitFor();assert.equal(await page.locator('input[type=checkbox]').count(),0);
 }
 await page.goto(base+'/builder/',{waitUntil:'networkidle'});
 await page.getByText('Import documents into your CV',{exact:true}).click();
 await page.getByLabel('CV documents').setInputFiles({name:'sample.pdf',mimeType:'application/pdf',buffer:bytes});
 await page.getByLabel('Edit fact 1',{exact:true}).waitFor();
 for(const item of await page.locator('section input[type=checkbox][aria-label^="Approve fact"]').all())await item.check();
 await page.getByRole('button',{name:'Add approved facts to CV',exact:true}).click();
 await page.waitForFunction(()=>document.querySelector('.cv-sheet')?.textContent?.includes('PDF Test Person'));
 assert((await page.locator('.cv-sheet').innerText()).includes('pdf@example.invalid'));
 assert.equal(requests.length,0,'No uploads or external asset requests');assert.deepEqual(errors,[]);
 console.log('PASS: actual PDF worker extraction; editable explicit consent; scanned/invalid/page-limit warnings; direct Builder apply; EN/AR; 360/390px; no uploads/external requests/page errors.');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
