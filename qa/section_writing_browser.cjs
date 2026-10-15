// Synthetic local UI regression. No accounts, paid services or real CVs.
const {chromium} = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(process.argv[2]);
const ts = require(path.join(root, 'node_modules/typescript'));
const source = fs.readFileSync(path.join(root, 'components/SectionWritingAssistant.tsx'), 'utf8');
const prefix = source.slice(source.indexOf('export function'), source.indexOf('type Props'));
const improve = vm.runInNewContext(ts.transpile(prefix.replace('export ', '') + '\nimproveSection'));
assert.equal(improve('  I manage  12 cases\n• I support colleagues  ', true), 'Manage 12 cases\nSupport colleagues');
for (const text of ['I do not manage staff', 'Not certified in ACLS', 'I was responsible for 5 cases', 'مراجعة ١٢ ملفاً', 'iOS development']) {
  assert.equal(improve(text, true), text.replace(/^I was/, 'Was'));
}
// Run the real component's event handlers even when Chromium is unavailable.
let slots=[], index=0, tree, value='  I manage 12 accounts  ';
const jsx=(type,props)=>({type,props}); const mod={exports:{}};
vm.runInNewContext(ts.transpileModule(source,{compilerOptions:{jsx:ts.JsxEmit.ReactJSX,module:ts.ModuleKind.CommonJS}}).outputText,
  {module:mod,exports:mod.exports,require(name){
    if(name==='react') return {useState(initial){const i=index++;if(!(i in slots))slots[i]=initial;return [slots[i],v=>slots[i]=v]}};
    if(name==='react/jsx-runtime') return {jsx,jsxs:jsx};throw Error(name);
  }});
function render(){index=0;tree=mod.exports.default({value,language:'en',experience:true,onApply(expected,next){if(value===expected)value=next}})}
function nodes(n=tree){if(!n||typeof n!=='object')return [];if(Array.isArray(n))return n.flatMap(nodes);return [n,...nodes(n.props?.children ?? null)]}
function button(name){return nodes().find(n=>n.type==='button'&&n.props.children===name)}
function click(name){const n=button(name);assert(n&&!n.props.disabled,name);n.props.onClick();render()}
function check(){nodes().find(n=>n.type==='input').props.onChange({target:{checked:true}});render()}
render();click('Improve this section');assert(button('Apply').props.disabled);check();click('Cancel');assert.equal(value,'  I manage 12 accounts  ');
click('Improve this section');check();value='Manual edit';render();assert(button('Apply').props.disabled);
value='  I manage 12 accounts  ';render();click('Improve this section');check();click('Apply');assert.equal(value,'Manage 12 accounts');
click('Undo improvement');assert.equal(value,'  I manage 12 accounts  ');
click('Improve this section');check();click('Apply');value='Later edit';render();assert(button('Undo improvement').props.disabled);
click('Improve this section');check();nodes().find(n=>n.type==='textarea').props.onChange({target:{value:'Edited suggestion'}});render();assert(button('Apply').props.disabled);
console.log('PASS component handlers: review, cancel, confirmation reset, stale apply, exact undo and later-edit protection; wording preserves facts and negation.');
if(process.argv.includes('--unit-only')) process.exit(0);
(async () => {
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage({viewport:{width:390,height:844}});
  const errors=[]; page.on('pageerror', error => errors.push(error.message));
  try {
    await page.goto((process.env.SIRATI_SMART_BASE_URL || 'http://127.0.0.1:8765/sirati') + '/builder/');
    await page.getByRole('button', {name:/Continue/}).last().click();
    const original = page.locator('.wizard-section-card textarea').first();
    const improveButton = page.getByRole('button', {name:'Improve this section', exact:true});
    const helper = improveButton.locator('..');
    const apply = helper.getByRole('button', {name:'Apply', exact:true});
    const confirm = helper.getByRole('checkbox');
    const before = '  I have experience in ER care and 5 years of practice.  ';
    await original.fill(before); await improveButton.click();
    assert(await apply.isDisabled()); assert.equal(await original.inputValue(), before);
    await confirm.check(); await helper.getByRole('button',{name:'Cancel',exact:true}).click();
    assert.equal(await original.inputValue(), before);
    await improveButton.click(); await confirm.check();
    await original.fill('Later manual text'); assert(await apply.isDisabled());
    await original.fill(before); await improveButton.click(); await confirm.check(); await apply.click();
    assert.equal(await original.inputValue(), 'Experience in ER care and 5 years of practice.');
    await helper.getByRole('button',{name:'Undo improvement',exact:true}).click();
    assert.equal(await original.inputValue(), before);
    await improveButton.click(); await confirm.check(); await apply.click();
    await original.fill('New manual wording');
    assert(await helper.getByRole('button',{name:'Undo improvement',exact:true}).isDisabled());
    await improveButton.click(); await helper.getByRole('textbox').fill('Reviewed custom wording');
    await confirm.check(); await helper.getByRole('textbox').fill('Changed again');
    assert(await apply.isDisabled());
    const box = await helper.boundingBox(); assert(box.x >= 0 && box.x + box.width <= 391);
    await page.setViewportSize({width:1440,height:1000});
    await page.getByRole('button',{name:/Continue/}).last().click();
    await page.getByRole('button',{name:'+ Add experience',exact:true}).click();
    const card=page.locator('.editor-card').first();
    const details=card.locator('textarea').first();
    await details.fill('I manage 12 accounts');
    await card.getByRole('button',{name:'Improve this section',exact:true}).click();
    await card.getByRole('checkbox').check(); await card.getByRole('button',{name:'Apply',exact:true}).click();
    assert.equal(await details.inputValue(),'Manage 12 accounts');
    await card.getByRole('button',{name:'Undo improvement',exact:true}).click();
    assert.equal(await details.inputValue(),'I manage 12 accounts');
    await card.getByRole('button',{name:'Improve this section',exact:true}).click();
    await card.locator('input').first().fill('Changed role');
    assert.equal(await card.getByRole('button',{name:'Apply',exact:true}).count(),0);
    assert.deepEqual(errors, []);
    console.log('PASS: facts/negation preserved, preview/cancel/confirm, stale apply, exact undo, later-edit protection, role reset, mobile containment and desktop experience flow.');
  } finally { await browser.close(); }
})().catch(error => {console.error(error); process.exit(1);});
