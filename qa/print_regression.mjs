// Regression for P1 #39: actual built print CSS on mobile+desktop,
// no accounts, no bypass of paid PDF authorization.
import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const origin = 'http://127.0.0.1:4173';
const browser = await chromium.launch({headless:true});
const fixture = `
<header class="site-header">LEAKED-SITE-HEADER</header>
<main class="container wizard-builder-page">
  <div class="wizard-journey-wrap">LEAKED-JOURNEY</div>
  <div class="wizard-builder-shell">
    <aside class="wizard-panel">
      <div style="min-height:900px">LEAKED-INPUTS-AND-PAYMENT-BUTTONS</div>
    </aside>
    <section class="preview-wrap wizard-preview-wrap">
      <div class="preview-stage">
        <div class="preview-label no-print">LEAKED-PREVIEW-LABEL</div>
        <article class="cv-sheet template-compact-ats" dir="ltr">
          <header class="compact-ats-head keep-together">
            <h1>QA TEST COMPACT ATS CV</h1>
            <p>Registered Nurse — Emergency Department</p>
            <p>qa@example.invalid | +20 100 000 0000</p>
          </header>
          <section class="compact-ats-section keep-together">
            <h2>Professional Summary</h2>
            <p>Test-only nursing CV demonstrating that the printed PDF contains the CV sheet and no wizard controls.</p>
          </section>
          <section class="compact-ats-section keep-together">
            <h2>Experience</h2>
            <p>Emergency nurse — Sample Hospital — 2022–Present</p>
            <p>Patient assessment, triage, documentation, handover.</p>
          </section>
          <section class="compact-ats-section keep-together">
            <h2>Education and certifications</h2>
            <p>BSc Nursing | BLS | ACLS</p>
          </section>
        </article>
      </div>
    </section>
  </div>
  <div class="wizard-footer-nav">LEAKED-WIZARD-FOOTER</div>
</main>
<footer>LEAKED-SITE-FOOTER</footer>
`;
const tests=[{name:'mobile-390px',width:390,height:844},{name:'desktop-1440px',width:1440,height:900}];
try {
  for(const test of tests){
    const page=await browser.newPage({viewport:{width:test.width,height:test.height}});
    const resp=await page.goto(origin + '/',{waitUntil:'networkidle'});
    assert(resp?.ok(), 'staging build cannot serve home page');
    await page.evaluate(html=>{document.body.innerHTML=html;},fixture);
    await page.emulateMedia({media:'print'});
    const state=await page.evaluate(()=>{
      const visible=sel=>{const el=document.querySelector(sel);return el&&getComputedStyle(el).display!=='none';};
      const sheet=document.querySelector('.cv-sheet');
      return {
        wizardHidden:!visible('.wizard-panel'),
        journeyHidden:!visible('.wizard-journey-wrap'),
        previewLabelHidden:!visible('.preview-label'),
        footerHidden:!visible('.wizard-footer-nav'),
        headerHidden:!visible('.site-header'),
        siteFooterHidden:!visible('body > footer'),
        sheetVisible:visible('.cv-sheet'),
        paperWidth:sheet?.getBoundingClientRect().width || 0,
        height:sheet?.getBoundingClientRect().height || 0,
        sheetMinHeight:getComputedStyle(sheet).minHeight,
      };
    });
    for(const prop of ['wizardHidden','journeyHidden','previewLabelHidden','footerHidden','headerHidden','siteFooterHidden','sheetVisible']){
      assert.equal(state[prop],true,test.name+' '+prop+' failed: '+JSON.stringify(state));
    }
    assert(state.paperWidth>=790 && state.paperWidth<=798,test.name+' not 210mm: '+state.paperWidth);
    assert.equal(state.sheetMinHeight,'0px',test.name+' paper min-height forces an extra page');
    const pdf=await page.pdf({format:'A4',printBackground:true,preferCSSPageSize:true});
    const n=(pdf.toString('latin1').match(/\/Type\s*\/Page\b/g)||[]).length;
    assert.equal(n,1,test.name+' should produce one CV-only A4 page, got '+n);
    console.log('PASS:',test.name,'A4 pages=',n,'wizard/chrome hidden, min-height=0, CV width=',state.paperWidth);
    await page.close();
  }
  console.log('PASS: P1 #39 synthetic CV print isolation regression; real Android approval/clean PDF still requires manual QA');
} finally {
  await browser.close();
}
