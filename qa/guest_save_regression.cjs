// Exercise the generated component with synthetic auth/storage; no customer accounts.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {createRequire} = require('node:module');
const root = path.resolve(process.argv[2]);
const req = createRequire(path.join(root,'package.json'));
const ts = req('typescript');
const component = fs.readFileSync(path.join(root,'components/SiratiBuilderPdfButton.tsx'),'utf8');
const builder = fs.readFileSync(path.join(root,'app/builder/page.tsx'),'utf8');
const save = builder.slice(builder.indexOf('  async function saveToAccount('),builder.indexOf("    setCloudStatus('Saving", builder.indexOf('  async function saveToAccount(')));
assert(save.includes('setSaveAuthRequest(request => request + 1)'));
assert(!save.includes('window.location.href'), 'guest save must not abandon the mounted editor');
assert(builder.includes('onSave={() => saveToAccount(saveVersionRequested.current)}'));
const code = ts.transpileModule(component,{compilerOptions:{jsx:ts.JsxEmit.ReactJSX,module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText;
const key = 'sirati.guest.pdf.pending.v1';
const tick = () => new Promise(resolve => setImmediate(resolve));
function setup({quota=false}={}) {
  let slots=[],index=0,effects=[],tree,user=null,failed=false,blocked=false,saves=0,exports=0,props;
  const storage=new Map();
  const hooks={
    useState(initial) {const i=index++;if(!(i in slots))slots[i]=initial;return [slots[i],v=>{slots[i]=typeof v==='function'?v(slots[i]):v}];},
    useRef(initial){const i=index++;return slots[i] ||= {current:initial};},
    useId(){index++;return 'synthetic-dialog';},
    useEffect(fn,deps){const i=index++;if(!slots[i]||deps.some((d,j)=>d!==slots[i][j])){slots[i]=deps;effects.push(fn)}}
  };
  const auth={
    async getUser(){return {data:{user},error:null}},
    async signInWithPassword({email}) {if(failed)return {error:new Error('Invalid password')}; user={id:'synthetic-user',email};return {error:null}},
    async signUp(){return {data:{session:null},error:null}}
  };
  const module={exports:{}};
  const jsx=(type,props)=>({type,props});
  vm.runInNewContext(code,{module,exports:module.exports,require(name){
    if(name==='react')return hooks;
    if(name==='react/jsx-runtime')return {jsx,jsxs:jsx};
    if(name.includes('supabase'))return {createClient:()=>({auth})};
    if(name.includes('sessionBoundary'))return {isSessionBoundaryBlocked:()=>blocked};
    if(name.includes('basePath'))return {withBasePath:x=>x};
    if(name.includes('siratiPdfExport'))return {downloadCvSheet:async()=>{exports++}};
    throw Error(name);
  },window:{location:{origin:'https://example.invalid'},sessionStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>{if(quota)throw Error('Storage full');storage.set(k,v)},removeItem:k=>storage.delete(k)},addEventListener(){},removeEventListener(){}},document:{activeElement:{focus(){}},querySelector(){throw Error('Save CV must not export PDF')}},requestAnimationFrame:fn=>fn(),Date,JSON,Error});
  props={language:'ar',data:{personal:{fullName:'Synthetic CV'},photo:'data:synthetic'},template:'modern',hydrated:true,userId:null,saveRequest:0,onAuthenticated(id){props.userId=id},async onSave(){saves++;return 'synthetic-document'}};
  function render(){index=0;effects=[];tree=module.exports.default(props);for(const fn of effects)fn();return tree}
  function nodes(node=tree){if(!node||typeof node!=='object')return [];if(Array.isArray(node))return node.flatMap(nodes);return [node,...nodes(node.props?.children ?? null)]}
  function field(type,value,index=0){nodes().filter(n=>n.type==='input'&&n.props.type===type)[index].props.onChange({target:{value}});render()}
  async function submit(){await nodes().find(n=>n.type==='form').props.onSubmit({preventDefault(){}});render();await tick();render()}
  return {props,storage,render,nodes,field,submit,setFailed:v=>failed=v,setBlocked:v=>blocked=v,get saves(){return saves},get exports(){return exports},async begin(){render();props.saveRequest++;render();await tick();render()},signin(){nodes().find(n=>n.type==='button'&&n.props['aria-pressed']===false).props.onClick();render()}};
}
(async()=>{
  const s=setup();await s.begin();
  assert(s.nodes().some(n=>n.props?.role==='dialog'));
  let draft=JSON.parse(s.storage.get(key));
  assert.equal(draft.action,'save');assert.deepEqual(draft.data,s.props.data);assert.equal(draft.template,'modern');
  s.field('email','USER@example.invalid');s.field('password','synthetic-password');
  await s.submit(); // Mismatched passwords must never create an account or save a CV.
  assert.equal(s.saves,0);assert.equal(JSON.parse(s.storage.get(key)).email,null);
  s.field('password','synthetic-password',1); // Confirm new password in V34.
  await s.submit(); // Email confirmation required: keep editor and snapshot.
  assert(s.nodes().some(n=>n.props?.role==='dialog'));assert.equal(s.saves,0);
  assert.equal(JSON.parse(s.storage.get(key)).email,'user@example.invalid');
  s.setFailed(true);await s.submit();assert.equal(s.saves,0);assert(s.storage.has(key));
  s.setFailed(false);await s.submit();assert.equal(s.saves,1);assert.equal(s.exports,0);assert(!s.storage.has(key));
  const failedSave=setup();await failedSave.begin();failedSave.signin();failedSave.field('email','user@example.invalid');failedSave.field('password','synthetic-password');
  failedSave.props.onSave=async()=>null;failedSave.render();await failedSave.submit();assert(failedSave.storage.has(key));assert(failedSave.nodes().some(n=>n.props?.role==='alert'));
  const full=setup({quota:true});await full.begin();assert(!full.nodes().some(n=>n.props?.role==='dialog'));assert(full.nodes().some(n=>n.props?.role==='alert'));assert.equal(full.saves,0);
  const boundary=setup();boundary.setBlocked(true);await boundary.begin();assert.equal(boundary.storage.size,0);assert.equal(boundary.saves,0);
  // A save transfer must never cause the separate PDF component to auto-export.
  const pdf=setup();pdf.storage.set(key,JSON.stringify({...draft,email:'user@example.invalid'}));delete pdf.props.saveRequest;pdf.props.userId='synthetic-user';pdf.render();await tick();assert.equal(pdf.exports,0);assert(pdf.storage.has(key));
  console.log('PASS: guest save preserves exact CV; confirmation/errors retain draft; verified sign-in saves once; quota/session boundary fail closed; document request never exports PDF.');
})().catch(e=>{console.error(e);process.exitCode=1});

// Run the actual generated save function with deferred synthetic network replies.
(async()=>{
  const fn=builder.slice(builder.indexOf('  async function saveToAccount('),builder.indexOf('\n  function restoreVersion('));
  const js=ts.transpileModule(fn,{compilerOptions:{target:ts.ScriptTarget.ES2020}}).outputText;
  let inserts=0,versions=0,resolveInsert,rejectInsert,status='',blocked=false;
  const client={from(table){return {
    insert(){
      if(table==='cv_versions'){versions++;return Promise.resolve({error:null});}
      inserts++;
      return {select(){return {single(){return new Promise((resolve,reject)=>{resolveInsert=resolve;rejectInsert=reject;});}};}};
    },
    update(){return {eq:async()=>({error:null})};}
  };}};
  const ctx={saveInFlight:{current:false},isSessionBoundaryBlocked:()=>blocked,isSupabaseConfigured:()=>true,createClient:()=>client,userId:'synthetic-A',documentId:null,data:{fullName:'Synthetic'},template:'modern',language:'en',setCloudStatus:v=>status=v,setDocumentId:v=>ctx.documentId=v,documentTitle:()=> 'Synthetic',withBasePath:x=>x,window:{history:{replaceState(){}}},refreshVersions:async()=>{},alert(){}};
  vm.createContext(ctx);vm.runInContext(js+'\nthis.save=saveToAccount;',ctx);
  const first=ctx.save();const second=ctx.save();
  assert.equal(inserts,1,'rapid Save clicks must issue one document insert');
  resolveInsert({data:{id:'synthetic-doc'},error:null});await Promise.all([first,second]);
  assert.equal(versions,1);assert.equal(ctx.saveInFlight.current,false);
  ctx.documentId=null;const failure=ctx.save();rejectInsert(new Error('offline'));assert.equal(await failure,null);
  assert.match(status,/retry|حاول/i);assert.equal(ctx.saveInFlight.current,false);
  const retry=ctx.save();resolveInsert({data:{id:'retry-doc'},error:null});assert.equal(await retry,'retry-doc');
  blocked=true;const before=inserts;assert.equal(await ctx.save(),null);assert.equal(inserts,before);
  console.log('PASS: concurrent Save creates one document/version; network failure preserves retry; session boundary still blocks.');
})().catch(e=>{console.error(e);process.exitCode=1});

// Refresh regression: run the generated Builder's persistence/restore blocks,
// including the first render and account-resolution boundary (no live accounts).
(() => {
  const start=builder.indexOf('    if (!hydrated || !guestRestoreReady || userId');
  const end=builder.indexOf('  }, [hydrated, guestRestoreReady',start);
  assert(start>=0 && end>start);
  const restoreStart=builder.indexOf('      let guestTransferRestored = false;');
  const restoreEnd=builder.indexOf('      setEmailReturnMissing(',restoreStart);
  assert(restoreStart>=0 && restoreEnd>restoreStart);
  const compile=src=>ts.transpileModule(src,{compilerOptions:{target:ts.ScriptTarget.ES2020}}).outputText;
  const values=new Map();let denied=false,blocked=false,status='';
  const fixture={personal:{fullName:'اختبار Synthetic',email:'test@example.invalid'},
    experience:[{role:'Engineer',bullets:['Built a CV']}],photoDataUrl:'data:synthetic'};
  const ctx={hydrated:true,guestRestoreReady:true,userId:null,data:fixture,
    template:'executive-letterhead',language:'ar',Date,JSON,Number,URLSearchParams,
    isSessionBoundaryBlocked:()=>blocked,setCloudStatus:v=>status=v,
    window:{location:{search:''},sessionStorage:{getItem:k=>values.get(k)||null,
      setItem:(k,v)=>{if(denied)throw Error('quota');values.set(k,v)},removeItem:k=>values.delete(k)}},
    newCvRequestedRef:{current:false},user:null,normalizeCv:x=>x,
    setData:v=>ctx.restoredData=v,setTemplate:v=>ctx.restoredTemplate=v,
    setLanguage:v=>ctx.restoredLanguage=v};
  vm.createContext(ctx);
  const persist=()=>vm.runInContext('(function(){'+compile(builder.slice(start,end))+'})()',ctx);
  const restore=()=>vm.runInContext('(function(){'+compile(builder.slice(restoreStart,restoreEnd))+'})()',ctx);
  ctx.guestRestoreReady=false;persist();assert.equal(values.size,0,'must not overwrite before restore');
  ctx.guestRestoreReady=true;ctx.hydrated=false;persist();assert.equal(values.size,0);
  ctx.hydrated=true;persist();assert(values.has(key),'typing before Save must create a tab draft');
  let snapshot=JSON.parse(values.get(key));assert.deepEqual(snapshot.data,fixture);
  assert.equal(snapshot.requested,false);assert.equal(snapshot.email,null);assert.equal(snapshot.action,undefined);
  restore();assert.deepEqual(ctx.restoredData,fixture);assert.equal(ctx.restoredTemplate,'executive-letterhead');
  assert.equal(ctx.restoredLanguage,'ar');
  snapshot.createdAt-=60*60*1000;values.set(key,JSON.stringify(snapshot));
  delete ctx.restoredData;restore();assert.deepEqual(ctx.restoredData,fixture,'ordinary draft survives an idle hour');
  for(const user of [{id:'A',email:'a@example.invalid'},{id:'B',email:'b@example.invalid'}]) {
    ctx.user=user;delete ctx.restoredData;restore();assert.equal(ctx.restoredData,undefined,'ordinary guest draft must not transfer to an account');
  }
  ctx.user=null;ctx.newCvRequestedRef.current=true;delete ctx.restoredData;restore();assert.equal(ctx.restoredData,undefined);
  ctx.newCvRequestedRef.current=false;ctx.window.location.search='?doc=other';restore();assert.equal(ctx.restoredData,undefined);
  ctx.window.location.search='';
  snapshot={...snapshot,createdAt:Date.now(),requested:true,email:'a@example.invalid',action:'save'};
  values.set(key,JSON.stringify(snapshot));persist();
  let updated=JSON.parse(values.get(key));assert.equal(updated.createdAt,snapshot.createdAt);
  assert.equal(updated.email,snapshot.email);assert.equal(updated.action,'save');
  ctx.user={id:'B',email:'b@example.invalid'};delete ctx.restoredData;restore();assert.equal(ctx.restoredData,undefined);
  ctx.user={id:'A',email:'a@example.invalid'};restore();assert.deepEqual(ctx.restoredData,fixture);
  snapshot.createdAt-=60*60*1000;values.set(key,JSON.stringify(snapshot));delete ctx.restoredData;
  restore();assert.equal(ctx.restoredData,undefined,'expired account-transfer intent remains invalid');
  ctx.user=null;values.set(key,'invalid JSON');persist();assert.equal(JSON.parse(values.get(key)).requested,false);
  const before=values.get(key);ctx.userId='A';ctx.data={private:'account'};persist();assert.equal(values.get(key),before);
  ctx.userId=null;blocked=true;persist();assert.equal(values.get(key),before);blocked=false;
  denied=true;persist();assert(status);assert.equal(values.get(key),before);denied=false;
  status='';ctx.data={large:'x'.repeat(1800001)};persist();assert(status);assert.equal(values.get(key),before);
  const resetStart=builder.indexOf('  function resetCv() {');
  const resetEnd=builder.indexOf('\n  const isLastSection',resetStart);
  Object.assign(ctx,{STORAGE_KEY:'sirati.cv.v2',LEGACY_STORAGE_KEY:'sirati.cv.v1',
    localStorage:{removeItem(){}},cloneEmptyCv:()=>({personal:{fullName:''}}),
    rememberSection(){},setDocumentId(){},setVersions(){},setHistoryOpen(){},withBasePath:x=>x});
  ctx.window.history={replaceState(){}};
  vm.runInContext(compile(builder.slice(resetStart,resetEnd))+';resetCv();',ctx);
  assert(!values.has(key),'New CV discards stale draft/transfer intent');
  assert.equal(ctx.restoredData.personal.fullName,'');
  console.log('PASS: pre-Save refresh preserves full CV/template/Arabic; hydration, idle, account/doc/new-CV, expiry, corruption, quota and session guards.');
})();
