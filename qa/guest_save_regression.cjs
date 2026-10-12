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
  function field(type,value){nodes().find(n=>n.type==='input'&&n.props.type===type).props.onChange({target:{value}});render()}
  async function submit(){await nodes().find(n=>n.type==='form').props.onSubmit({preventDefault(){}});render();await tick();render()}
  return {props,storage,render,nodes,field,submit,setFailed:v=>failed=v,setBlocked:v=>blocked=v,get saves(){return saves},get exports(){return exports},async begin(){render();props.saveRequest++;render();await tick();render()},signin(){nodes().find(n=>n.type==='button'&&n.props['aria-pressed']===false).props.onClick();render()}};
}
(async()=>{
  const s=setup();await s.begin();
  assert(s.nodes().some(n=>n.props?.role==='dialog'));
  let draft=JSON.parse(s.storage.get(key));
  assert.equal(draft.action,'save');assert.deepEqual(draft.data,s.props.data);assert.equal(draft.template,'modern');
  s.field('email','USER@example.invalid');s.field('password','synthetic-password');
  await s.submit(); // Confirmation required: keep mounted editor and snapshot.
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
