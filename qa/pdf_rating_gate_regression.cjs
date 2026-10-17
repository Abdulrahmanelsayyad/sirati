// Actual generated component; synthetic accounts, database and PDF sink only.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(process.argv[2]);
const ts=require(require.resolve('typescript',{paths:[root]}));
const code=ts.transpileModule(fs.readFileSync(path.join(root,'components/SiratiBuilderPdfButton.tsx'),'utf8'),{compilerOptions:{jsx:ts.JsxEmit.ReactJSX,module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText;
function setup({signed=false,previous=false,quota=false}={}) {
 let slots=[],idx=0,tree,user=signed?{id:'A',email:'a@example.invalid'}:null,review=previous?{rating:2}:null,writes=[],downloads=0,failed=false,writeFailed=false,blocked=false,changeOnWrite=false,downloadFailed=false;
 const storage=new Map(),hooks={useState(v){let i=idx++;if(!(i in slots))slots[i]=v;return[slots[i],x=>slots[i]=typeof x==='function'?x(slots[i]):x]},useRef(v){let i=idx++;return slots[i]||=( {current:v})},useId(){idx++;return'test'},useEffect(){idx++}};
 const auth={async getUser(){return{data:{user},error:null}},async signInWithPassword({email}){user={id:'A',email};return{error:null}},async signUp(){return{data:{session:null},error:null}}};
 const client={auth,from(table){assert.equal(table,'sirati_site_feedback');return{select(){return{eq(key,id){assert.equal(key,'user_id');assert.equal(id,user.id);return{async maybeSingle(){return{data:review,error:failed?Error('offline'):null}}}}}},upsert(payload,options){return{abortSignal(){return (async()=>{assert.equal(options.ignoreDuplicates,true);writes.push(payload);if(writeFailed)return{error:Error('offline')};if(!review)review={rating:payload.rating};if(changeOnWrite)user={id:'B',email:'b@example.invalid'};return{error:null}})()}}}}}};
 const mod={exports:{}},jsx=(type,props)=>({type,props});
 vm.runInNewContext(code,{module:mod,exports:mod.exports,require(n){if(n==='react')return hooks;if(n==='react/jsx-runtime')return{jsx,jsxs:jsx};if(n.includes('supabase'))return{createClient:()=>client};if(n.includes('sessionBoundary'))return{isSessionBoundaryBlocked:()=>blocked};if(n.includes('basePath'))return{withBasePath:x=>x};if(n.includes('siratiPdfExport'))return{downloadCvSheet:async()=>{if(downloadFailed)throw Error('render failed');downloads++}};throw Error(n)},window:{location:{origin:'https://example.invalid'},sessionStorage:{getItem:k=>storage.get(k)||null,setItem(k,v){if(quota)throw Error('full');storage.set(k,v)},removeItem:k=>storage.delete(k)}},document:{activeElement:null,querySelector:()=>({querySelector:()=>({textContent:'Synthetic CV'})})},requestAnimationFrame:fn=>fn(),AbortSignal,Date,JSON,Error});
 const props={language:'en',data:{fullName:'Synthetic CV'},template:'modern',hydrated:true,userId:user?.id||null,onAuthenticated(){}};
 function render(){idx=0;tree=mod.exports.default(props)}
 function nodes(n=tree){if(!n||typeof n!=='object')return[];if(Array.isArray(n))return n.flatMap(nodes);return[n,...nodes(n.props?.children ?? null)]}
 async function click(find){const n=nodes().find(find);assert(n,'control exists');assert(!n.props.disabled,'control enabled');await n.props.onClick();await new Promise(r=>setImmediate(r));render()}
 function field(type,value,index=0){nodes().filter(n=>n.type==='input'&&n.props.type===type)[index].props.onChange({target:{value}});render()}
 render();return{nodes,storage,props,render,field,click,async begin(){await click(n=>n.type==='button'&&n.props.className==='btn btn-secondary btn-lg')},async rate(v){await click(n=>n.props['aria-label']===v+' of 5 stars')},async next(){await click(n=>n.type==='button'&&n.props.children==='Save rating and continue')},async submit(){await nodes().find(n=>n.type==='form').props.onSubmit({preventDefault(){}});render()},async signin(){await click(n=>n.type==='button'&&n.props.children==='Sign in')},set downloadFailed(v){downloadFailed=v},set writeFailed(v){writeFailed=v},set failed(v){failed=v},set blocked(v){blocked=v},set changeOnWrite(v){changeOnWrite=v},get review(){return review},get writes(){return writes},get downloads(){return downloads}};
}
(async()=>{
 const skip=async s=>s.click(n=>n.props.children==='Skip and continue');
 const s=setup();await s.begin();assert(!s.nodes().some(n=>n.type==='input'),'rating shown before auth');
 await s.rate(4);await s.next();assert(s.nodes().some(n=>n.type==='input'));
 assert.equal(s.downloads,0);assert.equal(s.writes.length,0,'no anonymous rating write');
 await s.signin();s.field('email','a@example.invalid');s.field('password','synthetic-password');await s.submit();
 assert.equal(s.downloads,1);assert.equal(s.writes.length,1);assert.equal(s.writes[0].rating,4);
 assert.deepEqual(Object.keys(s.writes[0]).sort(),['category','comment','rating','user_id']);
 const guest=setup();await guest.begin();await skip(guest);await guest.signin();guest.field('email','a@example.invalid');guest.field('password','synthetic-password');await guest.submit();assert.equal(guest.downloads,1);assert.equal(guest.writes.length,0);
 for(const previous of [false,true]) {
   const t=setup({signed:true,previous});await t.begin();await t.rate(5);await t.next();
   assert.equal(t.downloads,1);assert.equal(t.review.rating,previous?2:5,'existing review retained');
 }
 const fail=setup({signed:true});fail.writeFailed=true;await fail.begin();await fail.rate(2);await fail.next();assert.equal(fail.downloads,1,'review failure cannot block PDF');
 const changed=setup({signed:true});changed.changeOnWrite=true;await changed.begin();await changed.rate(3);await changed.next();assert.equal(changed.downloads,0,'account change during rating must stop export');
 const broken=setup({signed:true});broken.downloadFailed=true;await broken.begin();await skip(broken);assert.equal(broken.downloads,0);
 const cancel=setup();await cancel.begin();await cancel.rate(1);await cancel.click(n=>n.props.children==='Back to editing');assert.equal(cancel.writes.length,0);assert.equal(cancel.downloads,0);
 const full=setup({quota:true});await full.begin();await skip(full);assert.equal(full.downloads,0);
 const boundary=setup({signed:true});boundary.blocked=true;await boundary.begin();assert.equal(boundary.downloads,0);
 console.log('PASS: optional rating before auth, skip, verified identity, no CV payload, existing review preserved, nonblocking failure, cancel/quota/account boundaries.');
})().catch(e=>{console.error(e);process.exitCode=1});
