// Execute the actual generated TypeScript geometry functions, not a test copy.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { stripTypeScriptTypes } from 'node:module';
const source=fs.readFileSync(process.argv[2] || 'site-src/sirati-cv-source/lib/siratiPdfExport.ts','utf8');
const functions=source.slice(source.indexOf('function chooseBreak('),source.indexOf('function downloadBlob('));
const {chooseBreak,wordsByPage}=new Function(stripTypeScriptTypes(functions)+'; return {chooseBreak,wordsByPage};')();
const word=(top,bottom,value='BoundaryToken108')=>({top,bottom,value});
const recorded=word(2228.421875,2241.421875);
assert( recorded.top+1 >= 2229.001846665645, 'recorded old break permitted overlap');
assert(recorded.bottom-.5>2229.001846665645 && recorded.top+.5<2229.001846665645,
  'recorded old inclusion excludes word from both pages');
let count=0;
for(const scale of [1,1.25,1.5,2,2.00000001,3]) {
  for(const delta of [-1,-.5,-.001,0,.001,.5,1]) {
    const w=word(recorded.top+delta,recorded.bottom+delta);
    const cut=chooseBreak(1110,2229.001846665645,[w],scale);
    assert(!(w.top<cut && cut<w.bottom));
    assert(Math.abs(cut*scale-Math.round(cut*scale))<1e-8);
    const pages=wordsByPage([w],[0,cut,3300]);
    assert.equal(pages.flat().length,1);
    assert.equal(pages[1][0],w);
    count++;
  }
}
const touching=[word(0,100,'before'),word(100,113,'after')];
assert.deepEqual(wordsByPage(touching,[0,100,200]).map(p=>p.map(w=>w.value)),[['before'],['after']]);
const cascade=[word(95,110),word(90,96)];
assert.equal(chooseBreak(0,100,cascade,2),90);
assert.throws(()=>wordsByPage([recorded],[0,2229.001846665645,3300]),/boundary/);
assert.throws(()=>wordsByPage([word(-1,5)],[0,100]),/boundary/);
assert.throws(()=>wordsByPage([word(99,101)],[0,100]),/boundary/);
assert.throws(()=>chooseBreak(0,100,[word(0,101)],2),/safely/);
console.log('PASS:',count,'fractional regressions, touching edges, column cascade and fail-closed unsafe bounds');
