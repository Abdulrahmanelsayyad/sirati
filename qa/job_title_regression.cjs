// Synthetic component events and generated-builder integration; no accounts or network.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(process.argv[2]);
const ts = require(path.join(root, 'node_modules/typescript'));
const source = fs.readFileSync(path.join(root, 'components/JobTitleInput.tsx'), 'utf8');
let slots = [], index = 0, effects = [], tree, value = '', calls = [];
const jsx = (type, props) => ({type, props});
const moduleObject = {exports:{}};
vm.runInNewContext(ts.transpileModule(source, {compilerOptions:{jsx:ts.JsxEmit.ReactJSX,module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText, {
  module:moduleObject, exports:moduleObject.exports, require(name) {
    if (name === 'react/jsx-runtime') return {jsx,jsxs:jsx};
    if (name === 'react') return {
      useId:()=> 'job-test', useRef:()=>({current:null}), useMemo:fn=>fn(),
      useState(initial) { const i=index++; if (!(i in slots)) slots[i]=initial; return [slots[i],v=>slots[i]=typeof v==='function'?v(slots[i]):v]; },
      useEffect(fn,deps) { const i=index++; if (!slots[i] || deps.some((v,j)=>v!==slots[i][j])) { slots[i]=deps; effects.push(fn); } },
    };
    throw Error(name);
  },
});
const {suggestJobTitles: suggest, JOB_TITLES: titles, default: Component} = moduleObject.exports;
assert(titles.length >= 350); assert.equal(new Set(titles).size, titles.length);
for (const query of ['', 'd', 'de', '  de  ', '<script>']) assert.equal(suggest(query).length, 0);
for (const [query,title] of [['DEV','Developer'],['registered','Registered Nurse'],['educator','Educator'],['soft dev','Software Developer'],['nurse','Registered Nurse'],['account','Accountant'],['مهندس','مهندس مدني']]) assert(suggest(query).includes(title), query);
assert.equal(suggest('Developer')[0],'Developer'); assert(suggest('engineer').length <= 12);
assert.equal(suggest('Unlisted Custom Specialist').length, 0);
function render() { index=0; tree=Component({value,label:'Role',onChange:v=>{value=v;calls.push(v)}}); effects.splice(0).forEach(fn=>fn()); }
function nodes(n=tree) { if(!n||typeof n!=='object')return []; if(Array.isArray(n))return n.flatMap(nodes);return [n,...nodes(n.props?.children ?? null)]; }
const input=()=>nodes().find(n=>n.type==='input');
const options=()=>nodes().filter(n=>n.props?.role==='option');
function type(v) {input().props.onChange({target:{value:v}});render();}
function key(k,composing=false) {let prevented=false;input().props.onKeyDown({key:k,nativeEvent:{isComposing:composing},preventDefault(){prevented=true}});render();return prevented;}
render();type('de');assert.equal(options().length,0);type('dev');assert(options().length>0);assert.equal(value,'dev');
key('Enter');assert.equal(value,'dev'); // No implicit selection.
key('ArrowDown');assert(input().props['aria-activedescendant']);key('Enter');assert.equal(value,'Developer');assert.equal(options().length,0);
type('registered');options()[0].props.onClick();render();assert.equal(value,'Registered Nurse');
type('dev');key('ArrowDown');key('Escape');assert.equal(value,'dev');assert.equal(options().length,0);
input().props.onFocus();render();assert(options().length);key('Tab');assert.equal(options().length,0);
type('Custom specialist');input().props.onBlur();render();assert.equal(value,'Custom specialist');
type('dev');assert.equal(key('ArrowDown',true),false);input().props.onCompositionStart();render();assert.equal(options().length,0);input().props.onCompositionEnd();render();assert(options().length);
key('ArrowUp');assert(input().props['aria-activedescendant'].endsWith(`-${options().length-1}`));
type('Registered');key('Enter');assert.equal(value,'Registered'); // Typing resets active item.
const builder=fs.readFileSync(path.join(root,'app/builder/page.tsx'),'utf8');
assert.equal((builder.match(/<JobTitleInput /g)||[]).length,2);
assert(builder.includes("onChange={value => update('title', value)}"));
assert(builder.includes('onChange={value => updateExperience(item.id, { role: value })}'));
assert(builder.includes('key={item.id}'));
assert(!/fetch\(|supabase|https?:\/\//.test(source));
console.log(`PASS: ${titles.length} unique titles; prefix/token/case/Arabic search; 3-letter threshold; custom values; explicit keyboard/click selection; Escape/Tab/blur/IME; stable row-ID integration; no network dependency.`);
console.log('NOT RUN: real browser/mobile interaction, saved-account reload and PDF regression.');
