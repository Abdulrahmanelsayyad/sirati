import assert from 'node:assert/strict';
import fs from 'node:fs';
import { chromium } from 'playwright';
// Candidate-only computed DOM style check, no account data or network CVs.
const base=process.env.QA_PDF_BASE_URL;
assert(base==='http://127.0.0.1:4175/sirati','RTL style QA needs candidate local production-path build');
const browser=await chromium.launch({headless:true});
try {
  const page=await browser.newPage({viewport:{width:390,height:844}});
  await page.goto(base+'/qa-pdf-sections/');
  await page.getByLabel('Template',{exact:true}).selectOption('compact-ats');
  await page.getByLabel('Long fixture lines').fill('4');
  const images='/tmp/sirati-pdf-rtl-visual-candidate';
  fs.mkdirSync(images,{recursive:true});
  for(const width of [360,390,1440]){
    await page.setViewportSize({width,height:1000});
    await page.getByLabel('Language',{exact:true}).selectOption('ar');
    await page.getByLabel('Documents rendering').setChecked(width===1440);
    // V16: the previously overlooked Experience DetailLines uses .cv-bullets,
    // not the certification/course .compact-ats-list selectors tested below.
    const experience=page.locator('.cv-sheet[dir="rtl"] .compact-ats-entry .cv-bullets');
    assert((await experience.count())>0,'Arabic '+width+': no real Experience bullets in fixture');
    for(let i=0;i<await experience.count();i++){
      const s=await experience.nth(i).evaluate(ul=>{
        const li=ul.querySelector('li');
        const cs=getComputedStyle(ul),lc=li&&getComputedStyle(li);
        return {dir:cs.direction,align:cs.textAlign,position:cs.listStylePosition,
          padStart:cs.paddingInlineStart,padEnd:cs.paddingInlineEnd,
          marker:lc?.listStyleType,liDir:lc?.direction,liAlign:lc?.textAlign};
      });
      assert.equal(s.dir,'rtl','Arabic Experience list direction at '+width);
      assert.equal(s.liDir,'rtl','Arabic Experience item direction at '+width);
      assert.equal(s.liAlign,'right','Arabic Experience item alignment at '+width);
      assert.equal(s.position,'outside','Arabic Experience marker position at '+width);
      assert(parseFloat(s.padStart)>=16,'Arabic Experience padding at '+width);
      assert.equal(parseFloat(s.padEnd),0,'Arabic Experience opposite padding at '+width);
      assert.notEqual(s.marker,'none','Arabic Experience bullet disappeared at '+width);
      console.log('PASS Arabic Experience RTL',width,JSON.stringify(s));
    }
    // Read-only approved Staging comparison screenshots plus post-fix screenshots.
    // The desktop fixture deliberately moves its rendering stage offscreen;
    // return it to the visible preview only for Playwright's screenshot.
    if (width===1440) await page.getByLabel('Documents rendering').setChecked(false);
    await page.locator('.cv-sheet').screenshot({path:`${images}/after-compact-ar-${width}.png`});
    if (width===1440) await page.getByLabel('Documents rendering').setChecked(true);
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
    const enExp=page.locator('.cv-sheet[dir="ltr"] .compact-ats-entry .cv-bullets');
    assert((await enExp.count())>0,'English '+width+': missing Experience list');
    const enExpStyle=await enExp.first().evaluate(ul=>{
      const cs=getComputedStyle(ul),lc=getComputedStyle(ul.querySelector('li'));
      return {direction:cs.direction,marker:lc.listStyleType};
    });
    assert.equal(enExpStyle.direction,'ltr','English Experience direction changed '+width);
    assert.notEqual(enExpStyle.marker,'none','English Experience markers removed '+width);
    const enList=page.locator('.cv-sheet[dir="ltr"] .compact-ats-list');
    assert.equal(await enList.count(),2,'English '+width+' lists missing');
    const enStyle=await enList.first().evaluate(ul=>getComputedStyle(ul).listStyleType);
    assert.notEqual(enStyle,'none','English '+width+' list lost original markers');
    console.log('PASS English',width,'list and Experience markers preserved');
    // Approved Staging is a historical visual comparator, not a claim of
    // exact V15 source parity. Same synthetic inputs and device widths.
    await page.goto('http://127.0.0.1:4174/sirati/qa-pdf-sections/');
    await page.getByLabel('Template',{exact:true}).selectOption('compact-ats');
    await page.getByLabel('Long fixture lines').fill('4');
    await page.setViewportSize({width,height:1000});
    await page.getByLabel('Language',{exact:true}).selectOption('ar');
    await page.getByLabel('Documents rendering').setChecked(width===1440);
    if (width===1440) await page.getByLabel('Documents rendering').setChecked(false);
    await page.locator('.cv-sheet').screenshot({path:`${images}/before-staging-compact-ar-${width}.png`});
    // Restore candidate before the next width's assertions.
    await page.goto(base+'/qa-pdf-sections/');
    await page.getByLabel('Template',{exact:true}).selectOption('compact-ats');
    await page.getByLabel('Long fixture lines').fill('4');
  }
} finally{await browser.close();}
