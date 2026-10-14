// Owner-authorized synthetic accounts only. No admin key, schema change or deployment.
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { createClient } from '@supabase/supabase-js';
const endpoint = 'https://ykfxcxhozqqsvhtdyxho.supabase.co';
assert.equal(process.env.NEXT_PUBLIC_SUPABASE_URL, endpoint);
const key = process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY;
const emails = ['cesevaj849@calirona.com', 'megenik459@calirona.com'];
const passwords = [process.env.SIRATI_AB_A_PASSWORD, process.env.SIRATI_AB_B_PASSWORD];
if (!key || passwords.some(p => !p)) {
  console.log('BLOCKED: dedicated staging account secrets missing'); process.exit(2);
}
const clients = emails.map(() => createClient(endpoint, key, {
  auth: {persistSession:false, autoRefreshToken:false, detectSessionInUrl:false}
}));
const ids = [randomUUID(), randomUUID()];
const tag = 'SIRATI-SYNTHETIC-' + randomUUID();
// Match documentTitle(): the editor automatically saves this canonical title.
const titles = [tag + '-PRIVATE-A — Synthetic QA', tag + '-PRIVATE-B — Synthetic QA'];
const marker = tag + '-PRIVATE-A';
let step = 'login';
let failed = false;
const created = [];
const users = [];
const check = (condition) => assert(condition, 'Synthetic staging gate failed');
try {
  for (let i=0;i<2;i++) {
    const {data,error} = await clients[i].auth.signInWithPassword({email:emails[i],password:passwords[i]});
    if (error || !data.user || !data.session) {
      const code = /^[a-z_]+$/.test(error?.code || '') ? error.code : 'unclassified';
      const status = Number.isInteger(error?.status) ? error.status : 0;
      console.log(`FAIL: login ${i===0?'A':'B'} HTTP=${status} code=${code}`);
      continue;
    }
    // GitHub redaction before any child process can use this session.
    console.log('::add-mask::' + data.session.access_token);
    console.log('::add-mask::' + data.session.refresh_token);
    users.push(data.user.id);
  }
  check(users.length===2 && users[0] !== users[1]);
  console.log('PASS: real password login for both dedicated staging accounts');
  step = 'own document creation';
  for (let i=0;i<2;i++) {
    const {data,error} = await clients[i].from('cv_documents').insert({
      id:ids[i],user_id:users[i],title:titles[i],language:'en',template:'modern',
      data:{fullName:i===0?marker:tag+'-PRIVATE-B',title:'Synthetic QA',profile:'Test data only',
        experience:[],education:[],certifications:[],courses:[],projects:[]}
    }).select('id').single();
    check(!error && data?.id === ids[i]); created.push(i);
  }
  step = 'cross-account API isolation';
  for (let i=0;i<2;i++) {
    const foreign = ids[1-i];
    for (const op of ['select','update','delete']) {
      const table=clients[i].from('cv_documents');
      const query=op==='select'?table.select('id'):op==='update'?table.update({title:'BLOCKED-QA-CHANGE'}).select('id'):table.delete().select('id');
      const {data,error}=await query.eq('id',foreign);
      check(!error && Array.isArray(data) && data.length===0);
    }
    const {data,error}=await clients[i].from('cv_documents').select('id,title').eq('id',ids[i]).single();
    check(!error && data?.title===titles[i]);
  }
  console.log('PASS: A/B direct API cross-read, cross-update and cross-delete denied; originals unchanged');
  step = 'own save and restore';
  for(let i=0;i<2;i++) {
    const {error}=await clients[i].from('cv_documents').update({title:titles[i]+'-SAVED'}).eq('id',ids[i]);check(!error);
    const restored=await clients[i].from('cv_documents').select('id,title').eq('id',ids[i]).single();
    check(!restored.error && restored.data?.title===titles[i]+'-SAVED');
    const reverted=await clients[i].from('cv_documents').update({title:titles[i]}).eq('id',ids[i]);check(!reverted.error);
  }
  console.log('PASS: own document save and API restore');
  step = 'browser logout and account switching';
  for (const [first,second] of [[0,1],[1,0]]) {
  for (const [width,signOut] of [[360,'menu'],[390,'menu'],[1440,'menu'],[390,'documents']]) {
    console.log(`RUN: real account browser direction=${first}-${second}, width=${width}, signout=${signOut}`);
    const run=spawnSync(process.execPath,['qa-live-account-ab.mjs'],{stdio:'inherit',timeout:180000,env:{...process.env,
      SIRATI_AB_BASE_URL:'http://127.0.0.1:4173/sirati/',SIRATI_AB_STAGING_ONLY:'YES',
      SIRATI_AB_A_EMAIL:emails[first],SIRATI_AB_B_EMAIL:emails[second],SIRATI_AB_A_DOC_ID:ids[first],
      SIRATI_AB_A_PASSWORD:passwords[first],SIRATI_AB_B_PASSWORD:passwords[second],
      SIRATI_AB_A_TITLE:titles[first],SIRATI_AB_B_TITLE:titles[second],
      SIRATI_AB_A_MARKER:tag + (first===0?'-PRIVATE-A':'-PRIVATE-B'),
      SIRATI_AB_SAVE_RECOVERY:width===390 && signOut==='menu'?'YES':'NO',
      SIRATI_AB_VIEWPORT_WIDTH:String(width),SIRATI_AB_SIGNOUT_PATH:signOut}});
    check(run.status===0);
  }
  }
} catch {
  failed=true;console.log('FAIL: '+step+' (credentials and response bodies suppressed)');
} finally {
  // Only UUIDs successfully inserted in this run; never delete accounts or existing CVs.
  for(const i of created) {
    const {error}=await clients[i].from('cv_documents').delete().eq('id',ids[i]).eq('user_id',users[i]);
    const remaining=await clients[i].from('cv_documents').select('id').eq('id',ids[i]);
    if(error || remaining.error || remaining.data?.length!==0){failed=true;console.log('FAIL: synthetic fixture cleanup');}
    else console.log('PASS: own synthetic fixture delete and absence verified');
  }
  for(const client of clients) await client.auth.signOut({scope:'local'}).catch(()=>{});
}
console.log('NOT RUN: real token expiry, full device offline/reconnect, independent security sign-off');
process.exitCode=failed?1:0;
