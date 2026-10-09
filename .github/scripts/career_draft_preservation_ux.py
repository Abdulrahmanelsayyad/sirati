"""Preserve per-tool/per-language Career Studio drafts while page is open.

Source-confirmed accidental erasure on mode/language switching. In-memory only.
No localStorage, network, auth, storage, payment, or PDF behavior changes.
"""
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve()
path=root/"app/career-tools/page.tsx"
css_path=root/"app/globals.css"
source=path.read_text(encoding="utf-8")

def swap(old,new,label):
    global source
    matches=source.count(old)
    if matches != 1:
        raise RuntimeError("Career draft UX "+label+": expected one anchor, found "+str(matches))
    source=source.replace(old,new,1)

swap(
"""  const [draft, setDraft] = useState('');
  const [notice, setNotice] = useState('');""",
"""  // Retain edits for each tool and language in React state only (not device storage).
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const draftKey = mode + ':' + lang;
  const draft = drafts[draftKey] ?? '';
  function setDraft(next: string) {
    setDrafts(previous => ({ ...previous, [draftKey]: next }));
  }
  const [notice, setNotice] = useState('');""",
"per-tab state")

swap(
"  function changeMode(next: Mode) { setMode(next); setDraft(''); setNotice(''); }",
"  function changeMode(next: Mode) { setMode(next); setNotice(''); }",
"switching modes")

swap(
"onClick={() => { setLang(ar ? 'en' : 'ar'); setDraft(''); }} aria-label=\"Switch language\"",
"onClick={() => { setLang(ar ? 'en' : 'ar'); setNotice(''); }} aria-label=\"Switch language\"",
"switching language")

swap(
"""          <p>{t('Review the wording and accuracy before using it. This is structured drafting, not a hiring guarantee.', 'راجع الصياغة والدقة قبل الاستخدام. هذه مسودة منظمة وليست ضمانًا للتوظيف.')}</p>""",
"""          <p>{t('Review the wording and accuracy before using it. This is structured drafting, not a hiring guarantee.', 'راجع الصياغة والدقة قبل الاستخدام. هذه مسودة منظمة وليست ضمانًا للتوظيف.')}</p>
          <p className="career-draft-memory-notice">{t(
            'Your English and Arabic drafts remain available while this page is open. Copy or download before refreshing or leaving.',
            'تظل مسوداتك بالعربية والإنجليزية متاحة ما دامت الصفحة مفتوحة. انسخها أو نزّلها قبل تحديث الصفحة أو مغادرتها.'
          )}</p>""",
"temporary retention guidance")

path.write_text(source,encoding="utf-8")
css=css_path.read_text(encoding="utf-8")
if "/* Career draft preservation UX */" in css:
    raise RuntimeError("Already applied")
css += r"""
/* Career draft preservation UX */
@media screen {
  .career-result .career-draft-memory-notice {
    margin-block:12px; padding:10px 12px;
    border-inline-start:3px solid #6d9c7e; border-radius:8px;
    background:#eff7f0; color:#254f36; font-size:12px;
    line-height:1.6; overflow-wrap:anywhere;
  }
}
@media print {
  .career-result .career-draft-memory-notice {display:none!important}
}
"""
css_path.write_text(css,encoding="utf-8")
print("PASS: in-memory per-tool/per-language drafts; clear refresh limitation.")
