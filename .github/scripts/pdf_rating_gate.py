"""Owner-requested optional feedback AFTER successful PDF delivery.
Reuse the existing homepage feedback form; never gate auth/export on a review.
"""
from pathlib import Path
import sys
p = Path(sys.argv[1]) / 'components/SiratiBuilderPdfButton.tsx'
s = p.read_text()
def replace(old, new):
    global s
    if s.count(old) != 1:
        raise RuntimeError('Optional PDF feedback anchor changed: ' + old[:80])
    s = s.replace(old, new, 1)
replace('  const [open,setOpen] = useState(false);', '''  const [open,setOpen] = useState(false);
  const [downloaded,setDownloaded] = useState(false);''')
replace('  async function begin() {', '  async function begin() {\n    setDownloaded(false);')
replace('    await downloadCvSheet(sheet,name);', '''    await downloadCvSheet(sheet,name);
    setDownloaded(true);''')
replace('    {error && <small role="alert"', '''    {downloaded && !saving && <span role="status" className="sirati-pdf-feedback-optional">
      {arabic ? 'تم تجهيز تنزيل PDF. ' : 'PDF download prepared. '}
      <a href={withBasePath('/#feedback')} target="_blank" rel="noopener noreferrer">
        {arabic ? 'قيّم تجربتك (اختياري)' : 'Rate your experience (optional)'}
      </a>
    </span>}
    {error && <small role="alert"''')
p.write_text(s)
print('Applied optional post-download feedback; no rating gate or feedback API dependency.')
