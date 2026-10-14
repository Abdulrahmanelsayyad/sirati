// Browser-only account UX acceptance: synthetic input; no real credentials.
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
const base='http://127.0.0.1:4173/sirati';
const browser=await chromium.launch({headless:true});
try {
  for (const width of [360,390,768,1280]) {
    const page=await browser.newPage({viewport:{width,height:820}});
    const resp=await page.goto(base+'/auth/',{waitUntil:'networkidle'});
    assert(resp && resp.status()<400,'Account route unavailable');
    assert.equal(await page.locator('.sirati-auth-v34-card').count(),1,'Account card missing');
    const dimensions=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,width:window.innerWidth}));
    assert(dimensions.scroll<=dimensions.width+2,'Horizontal overflow at '+width+'px: '+JSON.stringify(dimensions));
    assert.equal(await page.locator('#sirati-auth-confirm').count(),0,'Sign-in must not request signup confirmation');
    await page.locator('.sirati-auth-v34-tabs button').nth(1).click();
    assert.equal(await page.locator('#sirati-auth-confirm').count(),1,'Signup requires password confirmation');
    await page.locator('#sirati-auth-email').fill('test-user@example.invalid');
    await page.locator('#sirati-auth-password').fill('synthetic-safe-value-123!');
    await page.locator('#sirati-auth-confirm').fill('synthetic-safe-value-123!');
    assert.equal(await page.locator('#sirati-auth-password').getAttribute('type'),'password');
    await page.getByRole('button',{name:'إظهار كلمة المرور'}).click();
    assert.equal(await page.locator('#sirati-auth-password').getAttribute('type'),'text','Show password toggle broken');
    assert.equal(await page.locator('#sirati-auth-confirm').getAttribute('type'),'text','Confirmation visibility differs');
    await page.locator('.sirati-auth-v34-tabs button').first().click();
    assert.equal(await page.locator('#sirati-auth-password').inputValue(),'','Switching modes must clear secret');
    assert.equal(await page.locator('#sirati-auth-confirm').count(),0);
    assert.equal(await page.locator('a.sirati-auth-v34-forgot').count(),1);
    await page.locator('.sirati-auth-v34-lang button').nth(1).click();
    assert.equal(await page.locator('.sirati-auth-v34-tabs button').nth(0).innerText(),'Sign in');
    await page.goto(base+'/auth/recovery/',{waitUntil:'networkidle'});
    assert.equal(await page.locator('#recovery-email').count(),1,'Recover-by-email missing');
    await page.goto(base+'/account/password/',{waitUntil:'networkidle'});
    assert(await page.locator('main').count()>0,'Account password route must render logged-out state');
    await page.close();
  }
  console.log('PASS: bilingual account tabs, secret clearing, reveal controls, recovery and 360–1280px no-overflow UX');
} finally {await browser.close();}
