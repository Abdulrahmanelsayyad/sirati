import assert from 'node:assert/strict';
import { chromium } from 'playwright';

// Browser acceptance of the actual compiled staging React/Supabase client.
// HTTP responses are intercepted; NO live Auth sessions, user data, tokens,
// backend writes or Production project are used by this test.
const base = 'http://127.0.0.1:4173/sirati';
const stagingHost = 'https://ykfxcxhozqqsvhtdyxho.supabase.co';
const sessionKey = 'sb-ykfxcxhozqqsvhtdyxho-auth-token';
const personId = 'c9000000-0000-4000-a000-000000000011';
const ownerId = 'c9000000-0000-4000-a000-000000000022';
const now = Math.floor(Date.now() / 1000);
const validJwt = (id) => [
  Buffer.from(JSON.stringify({alg:'HS256',typ:'JWT'})).toString('base64url'),
  Buffer.from(JSON.stringify({
    aud:'authenticated', role:'authenticated', sub:id,
    iat:now, exp:now + 3600, is_anonymous:false
  })).toString('base64url'),
  'qa-synthetic-only'
].join('.');

const browser = await chromium.launch({headless:true});
let accepted = 0;
try {
  async function makePage({signedIn=false, owner=false, rejectWrite=false, existingReview=null}={}) {
    const context = await browser.newContext({viewport:{width:390,height:844}});
    const writes = [];
    const reads = [];
    const id = owner ? ownerId : personId;
    const user = {
      id, aud:'authenticated', role:'authenticated',
      app_metadata: owner ? {sirati_feedback_admin:true} : {},
      user_metadata:{}, created_at:new Date(now*1000).toISOString(),
      email:'qa-feedback@example.invalid'
    };
    if (signedIn) {
      const payload = {
        access_token:validJwt(id),refresh_token:'qa-refresh-not-real',
        token_type:'bearer',expires_in:3600,expires_at:now+3600,user
      };
      await context.addInitScript(({key,session})=>{
        if (location.hostname === '127.0.0.1') {
          localStorage.setItem(key,JSON.stringify(session));
        }
      },{key:sessionKey,session:payload});
    }
    await context.route(stagingHost+'/**',async route=>{
      const request=route.request();
      const url=new URL(request.url());
      const reply=async (code,body)=>{
        await route.fulfill({
          status:code, contentType:'application/json',
          headers:{'access-control-allow-origin':'*','access-control-allow-headers':'*'},
          body:JSON.stringify(body)
        });
      };
      if (request.method()==='OPTIONS') {
        await route.fulfill({status:204,headers:{
          'access-control-allow-origin':'*',
          'access-control-allow-methods':'GET,POST,OPTIONS',
          'access-control-allow-headers':'*'
        }});
        return;
      }
      if (url.pathname==='/auth/v1/user' && request.method()==='GET') {
        await reply(200,{user});return;
      }
      if (url.pathname==='/rest/v1/sirati_site_feedback') {
        if (request.method()==='POST') {
          let posted;
          try {posted=JSON.parse(request.postData()||'null');}
          catch { throw Error('Bad feedback request body'); }
          writes.push({posted,url:request.url()});
          if (rejectWrite) await reply(403,{code:'42501',message:'permission denied'});
          else await reply(201,[]);
          return;
        }
        if (request.method()==='GET') {
          reads.push(request.url());
          if (url.searchParams.has('user_id')) {
            // maybeSingle(): PostgREST returns one JSON object, or PGRST116
            // (zero rows) which supabase-js translates into null.
            if (existingReview) await reply(200,existingReview);
            else await reply(406,{code:'PGRST116',
              details:'The result contains 0 rows',
              message:'JSON object requested, multiple (or no) rows returned'});
            return;
          }
          await reply(200,[
            {rating:5,category:'overall',comment:'Very good',created_at:'2026-10-13T12:00:00Z'},
            {rating:3,category:'pdf',comment:'تحسين المسافات',created_at:'2026-10-12T12:00:00Z'}
          ]);
          return;
        }
      }
      // Explicitly reject anything else, never send traffic to real Supabase.
      await reply(404,{error:'unexpected synthetic endpoint'});
    });
    const page=await context.newPage();
    return {page,context,writes,reads};
  }

  // Unauthenticated user: must not write or claim a saved rating.
  {
    const {page,context,writes}=await makePage();
    await page.goto(base+'/',{waitUntil:'networkidle'});
    await page.locator('#feedback').getByRole('button',{name:/4 of 5 stars/}).click();
    await page.locator('#feedback').getByRole('button',{name:/Send feedback/}).click();
    await assert.doesNotReject(()=>
      page.locator('#feedback').getByRole('status').getByText(/Sign in to submit/).waitFor());
    assert.equal(writes.length,0,'Guest must never send feedback');
    await context.close();
    accepted++;
  }

  // Signed-in account: test the real browser Supabase client request fields
  // and UI confirmation against a mocked successful REST response.
  {
    const {page,context,writes}=await makePage({signedIn:true});
    await page.goto(base+'/',{waitUntil:'networkidle'});
    const form=page.locator('#feedback');
    await form.getByRole('button',{name:/4 of 5 stars/}).click();
    await form.getByRole('button',{name:/تنزيل PDF/}).click();
    assert.equal(await form.getByRole('button',{name:/تنزيل PDF/}).getAttribute('aria-pressed'),'true');
    await form.locator('textarea').fill('تجربة حقيقية من واجهة الاختبار');
    await form.getByRole('button',{name:/Send feedback/}).click();
    await form.getByRole('status').getByText(/Your rating was saved/).waitFor({timeout:10000});
    assert(await form.locator('.sirati-feedback-v2__status.is-saved').isVisible(),
      'confirmed successful submission must render the dedicated success card');
    assert.equal(writes.length,1,'Expected one POST when signed in');
    assert.deepEqual(Object.keys(writes[0].posted).sort(),
      ['category','comment','rating','user_id'].sort(),
      'Feedback payload may only contain explicit permitted fields');
    assert.equal(writes[0].posted.user_id,personId);
    assert.equal(writes[0].posted.rating,4);
    assert.equal(writes[0].posted.category,'pdf');
    assert.equal(writes[0].posted.comment,'تجربة حقيقية من واجهة الاختبار');
    assert(writes[0].url.includes('on_conflict=user_id'),
      'Upsert must target one feedback row per account');
    await context.close();
    accepted++;
  }

  // A server-side access denial must NOT display a success message.
  {
    const {page,context,writes}=await makePage({signedIn:true,rejectWrite:true});
    await page.goto(base+'/',{waitUntil:'networkidle'});
    await page.locator('#feedback').getByRole('button',{name:/2 of 5 stars/}).click();
    await page.locator('#feedback').getByRole('button',{name:/Send feedback/}).click();
    await page.locator('#feedback').getByRole('status')
      .getByText(/Could not save/).waitFor({timeout:10000});
    assert.equal(writes.length,1,'A rejected write must be attempted once');
    assert.equal(await page.locator('#feedback').getByText(/Your rating was saved/).count(),0);
    await context.close();
    accepted++;
  }

  // Normal user cannot open dashboard; client-side check is additional
  // UX only, actual authorization remains database RLS tested separately.
  {
    const {page,context,reads}=await makePage({signedIn:true});
    await page.goto(base+'/feedback-dashboard/',{waitUntil:'networkidle'});
    await page.getByRole('alert').getByText(/Owner access required/).waitFor({timeout:10000});
    assert.equal(reads.length,0,'Non-owner UI must not issue dashboard SELECT');
    await context.close();
    accepted++;
  }

  // Owner claims from controlled app_metadata: dashboard can show ratings.
  {
    const {page,context,reads}=await makePage({signedIn:true,owner:true});
    await page.goto(base+'/feedback-dashboard/',{waitUntil:'networkidle'});
    await page.getByText('4.0 / 5').waitFor({timeout:10000});
    assert.equal(reads.length,1,'Owner should request one review listing');
    assert(await page.getByText('Very good').isVisible());
    assert(await page.getByText('تحسين المسافات').isVisible());
    await context.close();
    accepted++;
  }

  // Existing personal review must be prefilled, with a safe update action.
  {
    const {page,context,writes,reads}=await makePage({signedIn:true,
      existingReview:{rating:2,category:'pdf',comment:'Old review'}});
    await page.goto(base+'/',{waitUntil:'networkidle'});
    const form=page.locator('#feedback');
    await form.locator('.sirati-feedback-v2__previous').waitFor({timeout:10000});
    assert.equal(await form.getByRole('button',{name:/2 of 5 stars/}).getAttribute('aria-pressed'),'true');
    assert.equal(await form.locator('textarea').inputValue(),'Old review');
    assert(reads.some(url=>url.includes('user_id=eq.')),'Must select only current member review');
    await form.getByRole('button',{name:/5 of 5 stars/}).click();
    await form.getByRole('button',{name:/Update feedback/}).click();
    await form.getByText(/Your rating was saved/).waitFor({timeout:10000});
    assert.equal(writes.length,1);
    assert.equal(writes[0].posted.rating,5);
    await context.close();
    accepted++;
  }

  // Owner can filter by stars and search comments on mobile.
  {
    const {page,context}=await makePage({signedIn:true,owner:true});
    await page.goto(base+'/feedback-dashboard/',{waitUntil:'networkidle'});
    await page.getByText('4.0 / 5').waitFor({timeout:10000});
    await page.locator('.sirati-rating-v2__filters select').nth(1).selectOption('3');
    assert.equal(await page.locator('.sirati-rating-admin__list article').count(),1);
    assert(await page.getByText('تحسين المسافات').isVisible());
    await page.locator('.sirati-rating-v2__filters select').nth(1).selectOption('all');
    await page.locator('.sirati-rating-v2__filters input').fill('Very good');
    assert.equal(await page.locator('.sirati-rating-admin__list article').count(),1);
    assert(await page.getByText('Very good').isVisible());
    await context.close();
    accepted++;
  }

  assert.equal(accepted,7);
  console.log('PASS: 7 browser feedback acceptance scenarios (mocked HTTP only)');
  console.log('NOT TESTED: real login, live Supabase HTTP, full end-to-end write, owner metadata provisioning');
} finally {
  await browser.close();
}
