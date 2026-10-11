import fs from 'node:fs';
import { chromium } from 'playwright';
const browser = await chromium.launch({headless:true});
const page = await browser.newPage({viewport:{width:390,height:844}});
const base = process.env.QA_PDF_BASE_URL;
const folder = process.env.QA_PDF_RESULTS_DIR;
if (!base || !folder) throw Error('Isolated QA URL/output required');
fs.mkdirSync(folder,{recursive:true});
try {
  await page.goto(base+'/qa-pdf-metadata/');
  const error = page.locator('[role=alert]');
  const outcome = await Promise.race([
    page.waitForEvent('download',{timeout:60000}).then(download=>({download})),
    error.waitFor({state:'visible',timeout:60000}).then(()=>({bad:true})),
    page.getByRole('button',{name:'Download metadata fixture'}).click().then(()=>new Promise(()=>{})),
  ]);
  if (outcome.bad) throw Error(await error.textContent());
  const path=folder+'/metadata.pdf';
  await outcome.download.saveAs(path);
  if(fs.statSync(path).size<800)throw Error('Synthetic metadata PDF is empty');
  console.log('PASS synthetic metadata exported',path,fs.statSync(path).size,'bytes');
} finally {await browser.close();}
