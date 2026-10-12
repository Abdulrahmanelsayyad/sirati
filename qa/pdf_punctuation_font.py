"""Rebuild the OFL PDF Arabic font with selected ASCII punctuation (FontTools 4.61.1).
Run after reconstruction/npm install; this is an offline maintainer tool.
Latin letters/digits remain in the existing Latin font; no bidi policy changes.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from fontTools.ttLib import TTFont
from fontTools.subset import Options, Subsetter
from fontTools.merge import Merger
repo = Path(__file__).resolve().parents[1]
source = repo / 'site-src/sirati-cv-source/node_modules/@fontsource/noto-naskh-arabic/files'
with TemporaryDirectory() as tmp:
    latin = TTFont(source / 'noto-naskh-arabic-latin-400-normal.woff')
    options = Options()
    subset = Subsetter(options=options)
    punctuation = {32} | {ord(c) for c in ':;,!?()'}
    subset.populate(unicodes=punctuation)
    subset.subset(latin)
    latin.save(Path(tmp)/'punctuation.woff')
    combined = Merger().merge([str(source/'noto-naskh-arabic-arabic-400-normal.woff'),str(Path(tmp)/'punctuation.woff')])
    for record in combined['name'].names:
        if record.nameID in (1, 3, 4, 6, 16):
            record.string = 'Sirati PDF Naskh'.replace(' ', '') if record.nameID == 6 else 'Sirati PDF Naskh'
    assert punctuation <= set(combined.getBestCmap())
    assert ord('A') not in combined.getBestCmap()
    assert ord('-') not in combined.getBestCmap() and ord('/') not in combined.getBestCmap()
    combined['head'].created = 2082844800
    combined['head'].modified = 2082844800
    combined.recalcTimestamp = False
    combined.flavor = 'woff'
    combined.save(repo/'assets/pdf-fonts/sirati-pdf-naskh-punctuation.woff')
print('PASS: punctuation supported without adding mixed Latin letters')
