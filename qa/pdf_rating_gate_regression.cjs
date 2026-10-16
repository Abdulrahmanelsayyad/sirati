// Actual generated component; synthetic accounts, database and PDF sink only.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(process.argv[2]);
const ts=require(require.resolve('typescript',{paths:[root]}));
const code=ts.transpileModule(fs.readFileSync(path.join(root,'components/SiratiBuilderPdfButton.tsx'),'utf8'),{compilerOptions:{jsx:ts.JsxEmit.ReactJSX,module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText;
function setup({signed=false,previous=false,quota=false}={}) {
 let slots=[],idx=0,tree,user=signed?{id:'A',email:'a@example.invalid'}:null,review=previous?{rating:2}:null,writes=[],downloads=0,failed=false,writeFailed=false,blocked=false,changeOnWrite=false;
 const storage=new Map(),hooks={useState(v){let i=idx++;if(!(i in slots))slots[i]=v;return[slots[i],x=>slots[i]=typeof x==='function'?x(slots[i]):x]},useRef(v){let i=idx++;return slots[i]||=( {current:v})},useId(){idx++;return'test'},useEffect(){idx++}};
 const auth={async getUser(){return{data:{user},error:null}},async signInWithPassword({email}){user={id:'A',email};return{error:null}},async signUp(){return{data:{session:null},error:null}}};
 const client={auth,from(table){assert.equal(table,'sirati_site_feedback');return{select(){return{eq(key,id){assert.equal(key,'user_id');assert.equal(id,user.id);return{async maybeSingle(){return{data:review,error:failed?Error('offline'):null}}}}}},async upsert(payload,options){assert.equal(options.ignoreDuplicates,true);writes.push(payload);if(writeFailed)return{error:Error('offline')};review={rating:payload.rating};if(changeOnWrite)user={id:'B',email:'b@example.invalid'};return{error:null}}}}};
 const mod={exports:{}},jsx=(type,props)=>({type,props});
 vm.runInNewContext(code,{module:mod,exports:mod.exports,require(n){if(n==='react')return hooks;if(n==='react/jsx-runtime')return{jsx,jsxs:jsx};if(n.includes('supabase'))return{createClient:()=>client};if(n.includes('sessionBoundary'))return{isSessionBoundaryBlocked:()=>blocked};if(n.includes('basePath'))return{withBasePath:x=>x};if(n.includes('siratiPdfExport'))return{downloadCvSheet:async()=>{downloads++}};throw Error(n)},window:{location:{origin:'https://example.invalid'},sessionStorage:{getItem:k=>storage.get(k)||null,setItem(k,v){if(quota)throw Error('full');storage.set(k,v)},removeItem:k=>storage.delete(k)}},document:{activeElement:null,querySelector:()=>({querySelector:()=>({textContent:'Synthetic CV'})})},requestAnimationFrame:fn=>fn(),Date,JSON,Error});
 const props={language:'en',data:{fullName:'Synthetic CV'},template:'modern',hydrated:true,userId:user?.id||null,onAuthenticated(){}};
 function render(){idx=0;tree=mod.exports.default(props)}
 function nodes(n=tree){if(!n||typeof n!=='object')return[];if(Array.isArray(n))return n.flatMap(nodes);return[n,...nodes(n.props?.children ?? null)]}
 async function click(find){const n=nodes().find(find);assert(n,'control exists');assert(!n.props.disabled,'control enabled');await n.props.onClick();await new Promise(r=>setImmediate(r));render()}
 function field(type,value,index=0){nodes().filter(n=>n.type==='input'&&n.props.type===type)[index].props.onChange({target:{value}});render()}
 render();return{nodes,storage,props,render,field,click,async begin(){await click(n=>n.type==='button'&&n.props.className==='btn btn-secondary btn-lg')},async rate(v){await click(n=>n.props['aria-label']===v+' of 5 stars')},async next(){await click(n=>n.type==='button'&&n.props.children==='Save rating and continue')},async submit(){await nodes().find(n=>n.type==='form').props.onSubmit({preventDefault(){}});render()},async signin(){await click(n=>n.type==='button'&&n.props.children==='Sign in')},set writeFailed(v){writeFailed=v},set failed(v){failed=v},set blocked(v){blocked=v},set changeOnWrite(v){changeOnWrite=v},get writes(){return writes},get downloads(){return downloads}};
}
(async()=>{
 const s=setup();await s.begin();assert(s.nodes().some(n=>n.props['data-rating']!==undefined));assert(!s.nodes().some(n=>n.type==='input'));
 await s.rate(1);await s.next();const draft=JSON.parse([...s.storage.values()][0]);assert.equal(draft.rating,1);assert.equal(draft.data.fullName,'Synthetic CV');assert.equal(s.downloads,0);
 await s.signin();s.field('email','a@example.invalid');s.field('password','synthetic-password');await s.submit();assert.equal(s.downloads,1);assert.equal(s.writes[0].rating,1);assert.deepEqual(Object.keys(s.writes[0]).sort(),['category','comment','rating','user_id']);assert.equal(s.storage.size,0);
 await s.begin();assert.equal(s.downloads,2);assert.equal(s.writes.length,1,'existing review is not overwritten');
 for(const stars of [2,3,4,5]){const t=setup({signed:true});await t.begin();await t.rate(stars);await t.next();assert.equal(t.downloads,1);assert.equal(t.writes[0].rating,stars)}
 const existing=setup({signed:true,previous:true});await existing.begin();assert.equal(existing.downloads,1);assert.equal(existing.writes.length,0);
 const retry=setup({signed:true});await retry.begin();await retry.rate(3);retry.failed=true;await retry.next();assert.equal(retry.downloads,0);assert(retry.nodes().some(n=>n.props.role==='alert'));retry.failed=false;await retry.next();assert.equal(retry.downloads,1);
 const writeRetry=setup({signed:true});await writeRetry.begin();await writeRetry.rate(2);writeRetry.writeFailed=true;await writeRetry.next();assert.equal(writeRetry.downloads,0);writeRetry.writeFailed=false;await writeRetry.next();assert.equal(writeRetry.downloads,1);
 const signup=setup();await signup.begin();await signup.rate(3);await signup.next();signup.field('email','a@example.invalid');signup.field('password','synthetic-password');signup.field('password','synthetic-password',1);await signup.submit();assert.equal(signup.downloads,0);assert.equal(JSON.parse([...signup.storage.values()][0]).rating,3);await signup.submit();assert.equal(signup.downloads,1);assert.equal(signup.writes[0].rating,3);
 const cancel=setup();await cancel.begin();await cancel.rate(4);await cancel.click(n=>n.props.children==='Back to editing');assert.equal(cancel.downloads,0);assert.equal(cancel.writes.length,0);
 const full=setup({quota:true});await full.begin();await full.rate(4);await full.next();assert.equal(full.downloads,0);assert(!full.nodes().some(n=>n.type==='input'));
 const boundary=setup({signed:true});await boundary.begin();await boundary.rate(4);boundary.blocked=true;await boundary.next();assert.equal(boundary.writes.length,0);
 const switched=setup({signed:true});await switched.begin();await switched.rate(4);switched.changeOnWrite=true;await switched.next();assert.equal(switched.downloads,0,'account switch blocks export');
 console.log('PASS: rating before auth; all five ratings accepted; save precedes PDF; previous review preserved; retry/cancel/quota/session/account boundaries.');
})().catch(e=>{console.error(e);process.exitCode=1});
