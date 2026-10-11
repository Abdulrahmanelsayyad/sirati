import assert from 'node:assert/strict';
import { chromium } from 'playwright';
// Candidate-only computed DOM style check, no account data or network CVs.
const base=process.env.QA_PDF_BASE_URL;
assert(base==='http://127.0.0.1:4175','RTL style QA needs candidate local build');
const browser=await chromium.launch({headless:true});
try {
  const page=await browser.newPage({viewport:{width:390,height:844}});
  await page.goto(base+'/qa-pdf-sections/');
  await page.getByLabel('Template',{exact:true}).selectOption('compact-ats');
  for(const width of [390,1440]){
    await page.setViewportSize({width,height:1000});
    await page.getByLabel('Language',{exact:true}).selectOption('ar');
    await page.getByLabel('Documents rendering').setChecked(width===1440);
    const list=page.locator('.cv-sheet[dir="rtl"] .compact-ats-list');
    assert.equal(await list.count(),2,'Arabic '+width+': expected 2 lists');
    for(let i=0;i<2;i++){
      const attrs=await list.nth(i).evaluate(ul=>{
        const cs=getComputedStyle(ul);
        const li=ul.querySelector('li');
        return {listStyleType:cs.listStyleType,direction:cs.direction,
          paddingInlineStart:cs.paddingInlineStart,
          paddingInlineEnd:cs.paddingInlineEnd,
          liListStyle:li?getComputedStyle(li).listStyleType:null,
          liAlign:li?getComputedStyle(li).textAlign:null};
      });
      assert.equal(attrs.listStyleType,'none','RTL '+width+' list '+i+' still has markers');
      assert.equal(attrs.liListStyle,'none','RTL '+width+' list '+i+' li has markers');
      assert.equal(attrs.direction,'rtl','RTL '+width+' list '+i+' has wrong direction');
      assert.equal(parseFloat(attrs.paddingInlineStart),0,'RTL '+width+' list '+i+' left indent');
      assert.equal(parseFloat(attrs.paddingInlineEnd),0,'RTL '+width+' list '+i+' right indent');
      assert.equal(attrs.liAlign,'right','RTL '+width+' list '+i+' not right aligned');
      console.log('PASS Arabic',width,'list',i,JSON.stringify(attrs));
    }
    await page.getByLabel('Language',{exact:true}).selectOption('en');
    const enList=page.locator('.cv-sheet[dir="ltr"] .compact-ats-list');
    assert.equal(await enList.count(),2,'English '+width+' lists missing');
    const enStyle=await enList.first().evaluate(ul=>getComputedStyle(ul).listStyleType);
    assert.notEqual(enStyle,'none','English '+width+' list lost original markers');
    console.log('PASS English',width,'list markers preserved');
  }
} finally{await browser.close();}
