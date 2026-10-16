// Actual generated component; synthetic accounts, database and PDF sink only.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(process.argv[2]);
const ts=require(require.resolve('typescript',{paths:[root]}));
const code=ts.transpileModule(fs.readFileSync(path.join(root,'components/SiratiBuilderPdfButton.tsx'),'utf8'),{compilerOptions:{jsx:ts.JsxEmit.ReactJSX,module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText;
function setup({signed=false,previous=false,quota=false}={}) {
 let slots=[],idx=0,tree,user=signed?{id:'A',email:'a@example.invalid'}:null,review=previous?{rating:2}:null,writes=[],downloads=0,failed=false,writeFailed=false,blocked=false,changeOnWrite=false,downloadFailed=false;
 const storage=new Map(),hooks={useState(v){let i=idx++;if(!(i in slots))slots[i]=v;return[slots[i],x=>slots[i]=typeof x==='function'?x(slots[i]):x]},useRef(v){let i=idx++;return slots[i]||=( {current:v})},useId(){idx++;return'test'},useEffect(){idx++}};
 const auth={async getUser(){return{data:{user},error:null}},async signInWithPassword({email}){user={id:'A',email};return{error:null}},async signUp(){return{data:{session:null},error:null}}};
 const client={auth,from(table){assert.equal(table,'sirati_site_feedback');return{select(){return{eq(key,id){assert.equal(key,'user_id');assert.equal(id,user.id);return{async maybeSingle(){return{data:review,error:failed?Error('offline'):null}}}}}},async upsert(payload,options){assert.equal(options.ignoreDuplicates,true);writes.push(payload);if(writeFailed)return{error:Error('offline')};review={rating:payload.rating};if(changeOnWrite)user={id:'B',email:'b@example.invalid'};return{error:null}}}}};
 const mod={exports:{}},jsx=(type,props)=>({type,props});
 vm.runInNewContext(code,{module:mod,exports:mod.exports,require(n){if(n==='react')return hooks;if(n==='react/jsx-runtime')return{jsx,jsxs:jsx};if(n.includes('supabase'))return{createClient:()=>client};if(n.includes('sessionBoundary'))return{isSessionBoundaryBlocked:()=>blocked};if(n.includes('basePath'))return{withBasePath:x=>x};if(n.includes('siratiPdfExport'))return{downloadCvSheet:async()=>{if(downloadFailed)throw Error('render failed');downloads++}};throw Error(n)},window:{location:{origin:'https://example.invalid'},sessionStorage:{getItem:k=>storage.get(k)||null,setItem(k,v){if(quota)throw Error('full');storage.set(k,v)},removeItem:k=>storage.delete(k)}},document:{activeElement:null,querySelector:()=>({querySelector:()=>({textContent:'Synthetic CV'})})},requestAnimationFrame:fn=>fn(),Date,JSON,Error});
 const props={language:'en',data:{fullName:'Synthetic CV'},template:'modern',hydrated:true,userId:user?.id||null,onAuthenticated(){}};
 function render(){idx=0;tree=mod.exports.default(props)}
 function nodes(n=tree){if(!n||typeof n!=='object')return[];if(Array.isArray(n))return n.flatMap(nodes);return[n,...nodes(n.props?.children ?? null)]}
 async function click(find){const n=nodes().find(find);assert(n,'control exists');assert(!n.props.disabled,'control enabled');await n.props.onClick();await new Promise(r=>setImmediate(r));render()}
 function field(type,value,index=0){nodes().filter(n=>n.type==='input'&&n.props.type===type)[index].props.onChange({target:{value}});render()}
 render();return{nodes,storage,props,render,field,click,async begin(){await click(n=>n.type==='button'&&n.props.className==='btn btn-secondary btn-lg')},async rate(v){await click(n=>n.props['aria-label']===v+' of 5 stars')},async next(){await click(n=>n.type==='button'&&n.props.children==='Save rating and continue')},async submit(){await nodes().find(n=>n.type==='form').props.onSubmit({preventDefault(){}});render()},async signin(){await click(n=>n.type==='button'&&n.props.children==='Sign in')},set downloadFailed(v){downloadFailed=v},set writeFailed(v){writeFailed=v},set failed(v){failed=v},set blocked(v){blocked=v},set changeOnWrite(v){changeOnWrite=v},get writes(){return writes},get downloads(){return downloads}};
}
(async()=>{
 const s=setup();await s.begin();assert(s.nodes().some(n=>n.type==='input'),'guest proceeds directly to account form');
 assert.equal(s.downloads,0);assert.equal(s.writes.length,0);
 await s.signin();s.field('email','a@example.invalid');s.field('password','synthetic-password');await s.submit();
 assert.equal(s.downloads,1);assert.equal(s.writes.length,0);
 assert(s.nodes().some(n=>n.type==='a'&&n.props.children==='Rate your experience (optional)'));
 for(const previous of [false,true]) {
   const t=setup({signed:true,previous});t.failed=true;t.writeFailed=true;
   await t.begin();assert.equal(t.downloads,1,'feedback service failure must not block download');
   assert.equal(t.writes.length,0,'download must never submit a rating');
 }
 const broken=setup({signed:true});broken.downloadFailed=true;await broken.begin();assert.equal(broken.downloads,0);assert(!broken.nodes().some(n=>n.type==='a'&&n.props.children==='Rate your experience (optional)'));
 const cancel=setup();await cancel.begin();await cancel.click(n=>n.props.children==='Back to editing');
 assert.equal(cancel.downloads,0);assert.equal(cancel.writes.length,0);
 const full=setup({quota:true});await full.begin();assert.equal(full.downloads,0);
 const boundary=setup({signed:true});boundary.blocked=true;await boundary.begin();assert.equal(boundary.downloads,0);
 console.log('PASS: no rating before auth/download; optional feedback only after delivery; review failures do not block; guest/quota/session boundaries retained.');
})().catch(e=>{console.error(e);process.exitCode=1});
