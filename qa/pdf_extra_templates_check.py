"""Independent reader/A4/font checks for the 24 additional template variants."""
import json
import subprocess
import unicodedata
import os
from pathlib import Path
import fitz

root = Path(os.environ.get("SIRATI_QA_ARTIFACT_DIR", "qa-artifacts")).resolve().joinpath("sirati-pdf-extra-candidate")
cases = json.loads((root / 'results.json').read_text())
assert len(cases) == 144
observations = []
for case in cases:
    pdf = root / (case['id'] + '.pdf')
    with fitz.open(pdf) as doc:
        assert len(doc) == case['pages']
        assert all(abs(p.rect.width - 595.28) < 2 and abs(p.rect.height - 841.89) < 2 for p in doc)
        native = '\n'.join(p.get_text(sort=True) for p in doc)
        assert all(p.get_text().strip() for p in doc), case['id'] + ': blank page'
    fonts = subprocess.check_output(['pdffonts', str(pdf)], text=True)
    assert len(fonts.splitlines()) > 2 and all('yes' in line for line in fonts.splitlines()[2:])
    poppler = subprocess.check_output(['pdftotext', '-raw', str(pdf), '-'], text=True)
    markers = (['ملخص', 'خبرة', 'درجة', 'شهادة', 'دورة', 'مشروع', 'مهارات', 'اللغة']
               if '-ar-' in case['id'] else ['SummaryMarker', 'ExperienceMarker', 'EducationMarker',
                   'CertificationMarker', 'CourseMarker', 'ProjectMarker', 'SkillsMarker', 'LanguagesMarker'])
    for reader, text in [('poppler', poppler), ('pymupdf', native)]:
        text = ''.join(ch for ch in unicodedata.normalize('NFC', text) if unicodedata.category(ch) != 'Cf')
        assert all(marker in text for marker in markers), case['id'] + '/' + reader + ': missing section'
        observations.append({'id': case['id'], 'reader': reader, 'status': 'PASS'})
output = Path('candidate/pdf-perf-visual')
output.mkdir(parents=True, exist_ok=True)
(output / 'extra-template-native-results.json').write_text(json.dumps(observations, indent=2))
print('PASS: 144 additional variant PDFs / 288 native reader checks; A4, all sections, embedded fonts, nonblank pages')
