// Execute the generated TSX with synthetic hooks and deferred network results.
// No browser, real account, token, database or new dependency is required.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(process.argv[2] || 'site-src/sirati-cv-source');
const ts = require(path.join(root, 'node_modules/typescript'));
const source = fs.readFileSync(process.argv[3] || path.join(root, 'components/SiratiFeedbackRating.tsx'), 'utf8');
const code = ts.transpileModule(source, {compilerOptions: {
  module: ts.ModuleKind.CommonJS, jsx: ts.JsxEmit.ReactJSX,
  target: ts.ScriptTarget.ES2020,
}}).outputText;
const deferred = () => { let resolve, reject; const promise = new Promise((a,b) => {resolve=a;reject=b;}); return {promise,resolve,reject}; };
const tick = async () => { for(let i=0;i<12;i++) await Promise.resolve(); };
function harness() {
  let slots=[], cursor=0, mounted=false, effect, cleanup, listener, tree;
  let user={id:'synthetic-A'}, authNext=null;
  const writes=[], timers=[];
  const client={auth:{
    getUser:()=> { if(authNext) {const p=authNext;authNext=null;return p;} return Promise.resolve({data:{user},error:null}); },
    onAuthStateChange:fn=> {listener=fn;return {data:{subscription:{unsubscribe(){}}}};},
  },from:()=>({
    select:()=>({eq:()=>({maybeSingle:async()=>({data:null,error:null})})}),
    upsert:payload=>{const pending=deferred();writes.push({payload,pending});return pending.promise;},
  })};
  const react={
    useState:initial=> {const i=cursor++;if(!(i in slots))slots[i]=initial;return [slots[i],value=>{slots[i]=typeof value==='function'?value(slots[i]):value;}];},
    useRef:initial=> {const i=cursor++;return slots[i]??=( {current:initial} );},
    useEffect:fn=>{if(!mounted)effect=fn;},
  };
  const module={exports:{}};
  vm.runInNewContext(code,{exports:module.exports,require:name=>{
    if(name==='react')return react;
    if(name==='react/jsx-runtime')return {jsx:(type,props)=>({type,props}),jsxs:(type,props)=>({type,props})};
    if(name==='@/lib/supabase/client')return {createClient:()=>client};
    if(name==='@/lib/basePath')return {withBasePath:value=>value};
    throw Error(name);
  },window:{setTimeout:fn=>timers.push(fn)}});
  function render(){cursor=0;tree=module.exports.default();if(!mounted){mounted=true;cleanup=effect();}return tree;}
  function nodes(node){if(!node||typeof node!=='object')return [];if(Array.isArray(node))return node.flatMap(nodes);return [node,...nodes(node.props?.children)];}
  const find=predicate=>nodes(tree).find(predicate);
  return {
    writes, render,
    async ready(){render();await tick();render();},
    rating(value=5){find(n=>n.type==='button'&&n.props['aria-label']?.startsWith(value+' of')).props.onClick();render();},
    comment(value){find(n=>n.type==='textarea').props.onChange({target:{value}});render();},
    submit(){return find(n=>n.type==='form').props.onSubmit({preventDefault(){}});},
    button(){return find(n=>n.props?.type==='submit').props;},
    status(){return find(n=>n.props?.className?.startsWith('sirati-feedback-v2__status is-'))?.props.className;},
    value(){return find(n=>n.type==='textarea').props.value;},
    deferAuth(){const d=deferred();authNext=d.promise;return d;},
    async switchUser(id){user=id?{id}:null;listener(id?'SIGNED_IN':'SIGNED_OUT',{user});for(const fn of timers.splice(0))fn();await tick();render();},
    unmount(){cleanup();},
  };
}
const tests={
  async 'edits cannot reopen an in-flight submit or report unsaved text as saved'(){
    const h=harness();await h.ready();h.rating();h.comment('sent');
    const p=h.submit();await tick();h.render();h.comment('unsaved edit');
    assert.equal(h.button().disabled,true,'submit reopened while request pending');
    await h.submit();assert.equal(h.writes.length,1,'duplicate request');
    h.writes[0].pending.resolve({error:null});await p;h.render();
    assert.equal(h.value(),'unsaved edit');assert.equal(h.status(),undefined,'false saved notice');
    const retry=h.submit();await tick();assert.equal(h.writes[1].payload.comment,'unsaved edit');
    h.writes[1].pending.resolve({error:null});await retry;h.render();
    assert.match(h.status(),/is-saved$/);
  },
  async 'same-render duplicate submit is blocked'(){
    const h=harness();await h.ready();h.rating();const a=h.submit(),b=h.submit();await tick();
    assert.equal(h.writes.length,1);h.writes[0].pending.resolve({error:null});await Promise.all([a,b]);
  },
  async 'old rejection cannot replace the next account status'(){
    const h=harness();await h.ready();h.rating();const p=h.submit();await tick();
    await h.switchUser('synthetic-B');h.writes[0].pending.reject(Error('offline'));await p;h.render();
    assert.equal(h.status(),undefined);
  },
  async 'A-B-A switch invalidates the original A response'(){
    const h=harness();await h.ready();h.rating();const p=h.submit();await tick();
    await h.switchUser('synthetic-B');await h.switchUser('synthetic-A');
    h.writes[0].pending.resolve({error:null});await p;h.render();assert.equal(h.status(),undefined);
  },
  async 'late auth response cannot set sign-in on a new account'(){
    const h=harness();await h.ready();h.rating();const auth=h.deferAuth(),p=h.submit();
    await h.switchUser('synthetic-B');auth.resolve({data:{user:null},error:{name:'AuthSessionMissingError'}});
    await p;h.render();assert.equal(h.status(),undefined);assert.equal(h.writes.length,0);
  },
  async 'normal write failure preserves draft and permits retry'(){
    const h=harness();await h.ready();h.rating();h.comment('retry me');
    const p=h.submit();await tick();h.writes[0].pending.resolve({error:{message:'synthetic'}});await p;h.render();
    assert.match(h.status(),/is-error$/);assert.equal(h.value(),'retry me');assert.equal(h.button().disabled,false);
  },
};
(async()=>{let failed=0;for(const [name,test]of Object.entries(tests)){try{await test();console.log('PASS:',name);}catch(e){failed++;console.error('FAIL:',name,'—',e.message);}}process.exitCode=failed?1:0;})();
