"""Sirati Template Library v1: 24 new live-rendered style variants + existing 8.
Original designs based on vetted one-column, profile and timeline CV structures.
No copied Zety code/designs or changes to auth, customer data, or payment.
"""
from pathlib import Path
import json, re, sys
root = Path(sys.argv[1]).resolve()
specs = json.loads(r'''[{"id":"aurora-ats","name":"Aurora ATS","bg":"#237b80","accent":"#e7f5f1","family":"ats"},{"id":"graphite-ats","name":"Graphite ATS","bg":"#303744","accent":"#e9eaec","family":"ats"},{"id":"navy-precision","name":"Navy Precision","bg":"#203c70","accent":"#e8eef9","family":"ats"},{"id":"emerald-clean","name":"Emerald Clean","bg":"#247252","accent":"#e7f2ea","family":"ats"},{"id":"ivory-classic","name":"Ivory Classic","bg":"#76583c","accent":"#f5efe6","family":"ats"},{"id":"berry-minimal","name":"Berry Minimal","bg":"#923d65","accent":"#f5e9f0","family":"ats"},{"id":"glacier-ats","name":"Glacier ATS","bg":"#3176a3","accent":"#e5f2fa","family":"ats"},{"id":"cobalt-pro","name":"Cobalt Pro","bg":"#264fc4","accent":"#eaf0ff","family":"ats"},{"id":"sandstone-ats","name":"Sandstone ATS","bg":"#80634b","accent":"#f4efe8","family":"ats"},{"id":"terra-resume","name":"Terra Resume","bg":"#a34f38","accent":"#f8ede9","family":"ats"},{"id":"academic-slate","name":"Academic Slate","bg":"#49596e","accent":"#eef1f5","family":"ats"},{"id":"teal-outline","name":"Teal Outline","bg":"#176e7e","accent":"#e5f4f4","family":"ats"},{"id":"ocean-profile","name":"Ocean Profile","bg":"#174d63","accent":"#75d3e5","family":"photo"},{"id":"sage-profile","name":"Sage Profile","bg":"#355b4d","accent":"#a7dfbc","family":"photo"},{"id":"lilac-profile","name":"Lilac Profile","bg":"#503d72","accent":"#b8a2eb","family":"photo"},{"id":"coral-profile","name":"Coral Profile","bg":"#7f3e43","accent":"#f5b1a2","family":"photo"},{"id":"midnight-profile","name":"Midnight Profile","bg":"#232f49","accent":"#95b6ff","family":"photo"},{"id":"olive-profile","name":"Olive Profile","bg":"#4d5834","accent":"#e0d28a","family":"photo"},{"id":"copper-timeline","name":"Copper Timeline","bg":"#38332f","accent":"#e6a66b","family":"timeline"},{"id":"forest-timeline","name":"Forest Timeline","bg":"#223e36","accent":"#b6d598","family":"timeline"},{"id":"plum-timeline","name":"Plum Timeline","bg":"#423044","accent":"#deb3db","family":"timeline"},{"id":"azure-timeline","name":"Azure Timeline","bg":"#1c3b58","accent":"#71c8e2","family":"timeline"},{"id":"rose-timeline","name":"Rose Timeline","bg":"#513941","accent":"#edb6ae","family":"timeline"},{"id":"slate-timeline","name":"Slate Timeline","bg":"#303b49","accent":"#a6bece","family":"timeline"}]''')
assert len(specs) == 24 and len({v['id'] for v in specs}) == 24
by_family = {family: [s['id'] for s in specs if s['family'] == family]
             for family in ('ats', 'photo', 'timeline')}
quote = lambda values: ', '.join("'" + v + "'" for v in values)
def get(name):
    file = root / name
    return file, file.read_text(encoding='utf-8')
def replace_once(source, old, new):
    if source.count(old) != 1: raise RuntimeError('Template library anchor missing/ambiguous: ' + old[:90])
    return source.replace(old, new, 1)

file, source = get('lib/types.ts')
source = replace_once(source, "'gold-sidebar'",
    "'gold-sidebar' | " + ' | '.join("'" + s['id'] + "'" for s in specs))
file.write_text(source, encoding='utf-8')

file, source = get('app/builder/page.tsx')
anchor = '<option value="gold-sidebar">Gold Sidebar (Photo)</option>'
options = '\n'.join('                <option value="' + s['id'] + '">' + s['name'] + '</option>' for s in specs)
source = replace_once(source, anchor, anchor + '\n' + options)
guard = re.compile(r"(?P<lhs>[A-Za-z_$][\w.$]*)\s*===\s*'gold-sidebar'")
source, matches = guard.subn(lambda m: m.group(0) +
    ''.join(" || " + m.group('lhs') + " === '" + s['id'] + "'" for s in specs), source)
if not matches: raise RuntimeError('Builder template allowlist guard missing')
file.write_text(source, encoding='utf-8')

file, source = get('components/CvPreview.tsx')
old = "if (template === 'compact-ats' || template === 'healthcare-pro' || template === 'executive-ats') {"
new = "if (template === 'compact-ats' || template === 'healthcare-pro' || template === 'executive-ats'" + \
      ''.join(" || template === '" + s + "'" for s in by_family['ats']) + ") {"
source = replace_once(source, old, new)
for family, base in [('photo','profile-sidebar'), ('timeline','gold-sidebar')]:
    old = "if (template === '" + base + "') {"
    new = "if (template === '" + base + "'" + \
        ''.join(" || template === '" + s + "'" for s in by_family[family]) + ") {"
    source = replace_once(source, old, new)
    old = '<article className="cv-sheet template-' + base + '" dir={dir}>'
    new = "<article className={'cv-sheet template-" + base + " template-' + template} dir={dir}>"
    source = replace_once(source, old, new)
file.write_text(source, encoding='utf-8')

file, source = get('app/templates/page.tsx')
card = re.search(r"(?m)^(?P<indent>\s*)\{ id: 'gold-sidebar',[^\n]+\n", source)
if not card: raise RuntimeError('Base Gold Sidebar catalog anchor missing')
rows = ''.join(card.group('indent')+"{ id: '"+s['id']+"', name: '"+s['name']+
    "', description: '"+('Original compact single-column CV' if s['family']=='ats'
        else 'Original photo/sidebar CV')+" with its own heading and color style.', badge: '"+
    ('ATS' if s['family']=='ats' else 'Photo + Sidebar')+"' },\n" for s in specs)
source = source[:card.end()] + rows + source[card.end():]
benefit = re.search(r"(?m)^\s*'gold-sidebar': \{[^\n]+\}", source)
if not benefit: raise RuntimeError('Live CvPreview benefits map missing')
rows = ''.join(",\n  '"+s['id']+"': { en: ['"+
    ('Single column' if s['family']=='ats' else 'Genuine sidebar')+
    "', 'Custom typography'], ar: ['"+
    ('عمود واحد' if s['family']=='ats' else 'شريط جانبي حقيقي')+
    "', 'تنسيق مميز'] }" for s in specs)
source = source[:benefit.end()] + rows + source[benefit.end():]
state_anchor = '  const [canScrollNext, setCanScrollNext] = useState(false);'
gallery_state = r"""
  const [libraryView, setLibraryView] = useState(false);
  const [librarySearch, setLibrarySearch] = useState('');
  const [libraryCategory, setLibraryCategory] = useState('all');
  const [libraryLimit, setLibraryLimit] = useState(8);
  const libraryGroup = (id: TemplateName) => {
    if (['profile-sidebar', 'gold-sidebar', __PHOTO__].includes(id)) return 'photo';
    if (['modern', 'classic', 'executive-ats'].includes(id)) return 'professional';
    return 'ats';
  };
  const libraryMatches = templateOptions.filter(option =>
    (libraryCategory === 'all' || libraryGroup(option.id) === libraryCategory) &&
    (option.name + ' ' + option.description + ' ' + option.badge)
      .toLocaleLowerCase().includes(librarySearch.trim().toLocaleLowerCase())
  );
  const visibleLibrary = libraryView ? libraryMatches.slice(0, libraryLimit) : templateOptions.slice(0, 8);
""".replace('__PHOTO__', quote(by_family['photo']+by_family['timeline']))
source = replace_once(source, state_anchor, state_anchor + gallery_state)
toolbar = r"""        <div className="template-library-entrance">
          <span>{language === 'ar' ? '8 مميزة • 32 قالبًا في المكتبة' : '8 featured · 32 templates available'}</span>
          <button className="template-library-toggle" type="button" aria-pressed={libraryView}
            onClick={() => {setLibraryView(v => !v);setLibraryLimit(8);setLibraryCategory('all');setLibrarySearch('');}}>
            {libraryView ? (language === 'ar' ? 'العودة إلى المميزة' : 'Back to featured') :
              (language === 'ar' ? 'استعرض الـ32 قالبًا' : 'Browse all 32 templates')}
          </button>
        </div>
        {libraryView && <div className="template-library-filters">
          <label>
            <span>{language === 'ar' ? 'البحث عن قالب' : 'Find a template'}</span>
            <input type="search" aria-label="Search templates" value={librarySearch}
              placeholder={language === 'ar' ? 'اكتب اسم القالب' : 'Search by name or style'}
              onChange={e => {setLibrarySearch(e.target.value);setLibraryLimit(8);}} />
          </label>
          <div role="group" aria-label="Template categories" className="template-library-categories">
            {([
              ['all',language === 'ar' ? 'الكل' : 'All'],
              ['ats','ATS'],
              ['professional',language === 'ar' ? 'احترافي' : 'Professional'],
              ['photo',language === 'ar' ? 'صورة وشريط جانبي' : 'Photo + Sidebar'],
            ] as const).map(([id,title]) =>
              <button type="button" key={id} aria-pressed={libraryCategory===id}
                onClick={() => {setLibraryCategory(id);setLibraryLimit(8);}}>{title}</button>)}
          </div>
          <div className="template-library-count" role="status">
            {language === 'ar' ? ('عرض '+Math.min(libraryLimit,libraryMatches.length)+' من '+libraryMatches.length)
              : ('Showing '+Math.min(libraryLimit,libraryMatches.length)+' of '+libraryMatches.length+' templates')}
          </div>
          {libraryMatches.length > libraryLimit && <button type="button"
            className="template-library-more" onClick={() => setLibraryLimit(v => v + 8)}>
            {language === 'ar' ? 'عرض 8 قوالب إضافية ↓' : 'Show 8 more templates ↓'}
          </button>}
          {libraryMatches.length === 0 && <p>{language === 'ar' ? 'لا توجد نتائج' : 'No matching templates'}</p>}
        </div>}
"""
source = replace_once(source,'        <div className="template-carousel-toolbar">',
    toolbar+'        <div className="template-carousel-toolbar">')
source = replace_once(source,'Swipe or use arrows to browse 6 designs',
    "{libraryView ? (language === 'ar' ? 'تصفح النتائج بالتمرير لأسفل' : 'Scroll down through the gallery') : (language === 'ar' ? 'اسحب أو استخدم الأسهم' : 'Swipe or use arrows to browse featured templates')}")
source = replace_once(source,'className="template-carousel-toolbar"',
    'className={libraryView ? "template-carousel-toolbar template-library-active" : "template-carousel-toolbar"}')
source = replace_once(source,'className="template-flow-grid template-carousel-track"',
    'className={libraryView ? "template-flow-grid template-carousel-track template-library-grid" : "template-flow-grid template-carousel-track"}')
source = replace_once(source,'templateOptions.map((option) => (','visibleLibrary.map((option) => (')
file.write_text(source, encoding='utf-8')

file, css = get('app/globals.css')
css += r"""
/* Template Library gallery. Keep existing swipe carousel as the default. */
.flow-shell .template-library-entrance {max-width:960px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;margin:12px 0;}
.flow-shell .template-library-entrance span,.flow-shell .template-library-count {font-size:12px;color:#526375;}
.flow-shell .template-library-toggle,.flow-shell .template-library-more {
  border:1px solid #185244;background:#185244;color:white;border-radius:11px;
  min-height:44px;padding:9px 14px;font-size:13px;font-weight:700;cursor:pointer;
}
.flow-shell .template-library-filters {display:grid;gap:10px;max-width:960px;margin:8px 0 16px;}
.flow-shell .template-library-filters label {display:grid;gap:5px;max-width:460px;font-size:12px;}
.flow-shell .template-library-filters input {width:100%;min-height:44px;border-radius:10px;border:1px solid #b9c8cc;background:white;color:#23354a;padding:9px 12px;font:inherit;}
.flow-shell .template-library-categories {display:flex;flex-wrap:wrap;gap:7px;}
.flow-shell .template-library-categories button {background:white;color:#334155;border:1px solid #cbd5e1;border-radius:99px;min-height:40px;padding:7px 13px;cursor:pointer;}
.flow-shell .template-library-categories button[aria-pressed="true"] {background:#e6f2eb;border-color:#306c54;color:#185244;font-weight:700;}
.flow-shell .template-carousel-toolbar.template-library-active .template-carousel-actions {display:none;}
.flow-shell .template-carousel-track.template-library-grid {
  display:grid;grid-template-columns:repeat(auto-fill,minmax(205px,1fr));
  gap:16px;overflow:visible;max-width:960px;width:100%;padding:0 0 10px;
  scroll-snap-type:none;scroll-behavior:auto;
}
.flow-shell .template-carousel-track.template-library-grid .template-choice {min-width:0;max-width:none;width:100%;flex:auto;scroll-snap-align:none;}
.flow-shell .template-library-toggle:focus-visible,.flow-shell .template-library-more:focus-visible,
.flow-shell .template-library-categories button:focus-visible,.flow-shell .template-library-filters input:focus-visible {outline:2px solid #247d78;outline-offset:2px;}
@media(max-width:600px){
  .flow-shell .template-library-toggle {width:100%;}
  .flow-shell .template-carousel-track.template-library-grid {grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;}
  .flow-shell .template-carousel-track.template-library-grid .template-choice {min-width:0;width:100%;}
  .flow-shell .template-carousel-track.template-library-grid .template-choice-preview.template-real-preview {height:150px;min-height:150px;max-height:150px;}
}
@media(max-width:350px){.flow-shell .template-carousel-track.template-library-grid {grid-template-columns:1fr;}}
@media print {.template-library-entrance,.template-library-filters {display:none!important;}}
"""
for index,s in enumerate(specs):
    tag = '.cv-sheet.template-'+s['id']
    bg,accent = s['bg'],s['accent']
    if s['family']=='ats':
        css += '\n'+tag+' {font-family:'+('Georgia,serif' if index%3==0 else 'Arial,Helvetica,sans-serif')+';}\n'
        css += tag+' .compact-ats-head {border-bottom:'+str(1+index%3)+'px solid '+bg+';'+('text-align:center;' if index%4==0 else '')+'}\n'
        css += tag+' .compact-ats-head h1,'+tag+' .compact-ats-section h2 {color:'+bg+';}\n'
        css += tag+' .compact-ats-section h2 {border-bottom:1px solid '+accent+';'+('background:'+accent+';padding:3px 6px;' if index%4==1 else '')+'}\n'
    elif s['family']=='photo':
        css += '\n'+tag+' .profile-sidebar-rail {background:'+bg+';}\n'
        css += tag+' .profile-sidebar-rail h2 {color:'+accent+';border-color:'+accent+';}\n'
        css += tag+' .profile-sidebar-main h2 {color:'+bg+';border-bottom-color:'+accent+';}\n'
    else:
        css += '\n'+tag+' .gold-sidebar-rail {background:'+bg+';}\n'
        css += tag+' .gold-sidebar-rail::before {background:'+accent+';}\n'
        css += tag+' .gold-sidebar-main h2 {color:'+bg+';border-color:'+accent+';}\n'
file.write_text(css, encoding='utf-8')
print('Template Library v1: 32 real renderers; searchable progressive gallery.')
