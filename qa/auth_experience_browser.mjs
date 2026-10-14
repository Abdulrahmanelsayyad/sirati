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
    assert.equal(await page.locator('.sirati-auth-v34-tabs button').first().innerText(),'Sign in');
    assert.equal(await page.locator('.sirati-auth-v34-card').getAttribute('dir'),null);
    assert(!/[\u0600-\u06ff]/.test(await page.locator('.sirati-auth-v34-card').innerText()),'Account copy should be English by default');
    await page.locator('.sirati-auth-v34-tabs button').nth(1).click();
    assert.equal(await page.locator('#sirati-auth-confirm').count(),1,'Signup requires password confirmation');
    await page.locator('#sirati-auth-email').fill('test-user@example.invalid');
    await page.locator('#sirati-auth-password').fill('synthetic-safe-value-123!');
    await page.locator('#sirati-auth-confirm').fill('synthetic-safe-value-123!');
    assert.equal(await page.locator('#sirati-auth-password').getAttribute('type'),'password');
    await page.getByRole('button',{name:'Show password'}).click();
    assert.equal(await page.locator('#sirati-auth-password').getAttribute('type'),'text','Show password toggle broken');
    assert.equal(await page.locator('#sirati-auth-confirm').getAttribute('type'),'text','Confirmation visibility differs');
    await page.locator('.sirati-auth-v34-tabs button').first().click();
    assert.equal(await page.locator('#sirati-auth-password').inputValue(),'','Switching modes must clear secret');
    assert.equal(await page.locator('#sirati-auth-confirm').count(),0);
    assert.equal(await page.locator('a.sirati-auth-v34-forgot').count(),1);
    await page.locator('.sirati-auth-v34-lang button').first().click();
    assert.equal(await page.locator('.sirati-auth-v34-tabs button').first().innerText(),'تسجيل الدخول','Arabic option must remain available');
    await page.locator('.sirati-auth-v34-lang button').nth(1).click();
    assert.equal(await page.locator('.sirati-auth-v34-tabs button').nth(0).innerText(),'Sign in');
    // V35: verification and reset completion must return to explicit login.
    await page.goto(base+'/auth/?confirmed=1',{waitUntil:'networkidle'});
    assert.equal(await page.locator('.sirati-auth-v34-card').count(),1);
    assert.match(await page.locator('.sirati-auth-v35-confirmed').innerText(),/Email confirmed successfully/);
    assert.equal(await page.locator('#sirati-auth-password').count(),1,'Confirmed user must type password again');
    assert.equal(await page.locator('#sirati-auth-email').inputValue(),'','Do not prefill personal email from callback');
    assert(page.url().includes('/auth/'),'Must remain on login instead of auto-redirecting after confirmation');
    await page.goto(base+'/auth/?password_changed=1',{waitUntil:'networkidle'});
    assert.match(await page.locator('.sirati-auth-v35-confirmed').innerText(),/Password updated successfully/);
    assert.equal(await page.locator('#sirati-auth-password').count(),1,'Reset user must type NEW password again');
    assert(page.url().includes('/auth/'),'Must remain on login after password recovery');
    await page.goto(base+'/auth/confirm/',{waitUntil:'networkidle'});
    assert.equal(await page.getByRole('link',{name:/Back to sign in/}).count(),1,
      'Unverified/invalid callback must offer safe sign-in path');
    await page.goto(base+'/auth/recovery/',{waitUntil:'networkidle'});
    assert.equal(await page.locator('#recovery-email').count(),1,'Recover-by-email missing');
    await page.goto(base+'/account/password/',{waitUntil:'networkidle'});
    assert(await page.locator('main').count()>0,'Account password route must render logged-out state');
    await page.close();
  }
  console.log('PASS: English-first account UI, opt-in Arabic translations, manual sign-in boundary and 360–1280px UX');
} finally {await browser.close();}
