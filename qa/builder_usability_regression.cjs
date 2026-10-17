// Run against reconstructed source; completion must depend on data, never navigation.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),vm=require('node:vm');
const root=path.resolve(process.argv[2]),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const source=read('app/builder/page.tsx');
const logic=source.slice(source.indexOf('  const sectionComplete ='),source.indexOf('  const progressPercent ='));
function check(data,currentSection){return vm.runInNewContext(logic+'; ({complete:sectionComplete, checks:essentialChecks})',{data,currentSection});}
const empty={fullName:'',title:'',email:'',phone:'',profile:'',skills:'',languages:'',experience:[],education:[],certifications:[],courses:[],projects:[]};
for(let section=0;section<9;section++)assert(check(empty,section).complete.every(x=>!x));
const partial={...empty,experience:[{role:'Engineer',company:'',period:''}]};assert(!check(partial,8).complete[2]);
const full={...empty,fullName:'Test',title:'Engineer',email:'test@example.invalid',profile:'Profile',skills:'Testing',languages:'Arabic',education:[{degree:'BSc',school:'University',period:'2020'}]};
assert(check(full,0).checks.every(Boolean));assert(!check(full,8).complete[8]);
// Every explicit text/select field label must resolve to the same stable field ID.
const labels=[...source.matchAll(/<label htmlFor=(\{`[^`]+`\})>[^<]*<\/label>\s*<(input|textarea|select) id=(\{`[^`]+`\})/g)];
assert(labels.length>=29);for(const m of labels)assert.equal(m[1],m[3]);
assert(!/<label>[^<]+<\/label>\s*<(input|textarea|select)/.test(source));
assert(source.includes('uiLanguage={uiLanguage} language={language} data={data}'));
assert(source.includes('<CvPreview data={data} template={template} language={language}'));
assert(source.includes('TEMPLATE_NAMES[template]'));assert(source.includes('"modern": "Professional ATS"'));
assert(!read('app/layout.tsx').includes('<BuilderNavigator />'));
assert(source.includes("sessionStorage.setItem('sirati.builder.uiLanguage',value)"));
assert(read('components/SiratiBuilderPdfButton.tsx').includes('data,template,language}'));
assert(source.includes('<ExperienceDates'));
console.log('PASS: empty/partial/full completion, Review navigation, 30 accessible labels, independent CV/UI language, template name and single navigator.');
