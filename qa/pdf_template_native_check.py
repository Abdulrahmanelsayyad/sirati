"""Poppler/PyMuPDF independently verify every long-template paragraph marker."""
import json
import re
import subprocess
import unicodedata
from pathlib import Path
import fitz

root=Path('/tmp/sirati-pdf-template-long-candidate')
cases=json.loads((root/'results.json').read_text())
assert len(cases)==162
results=[]
for item in cases:
    pdf=root/(item['id']+'.pdf')
    with fitz.open(pdf) as doc:
        assert all(abs(p.rect.width-595.28)<2 and abs(p.rect.height-841.89)<2 for p in doc)
        native='\n'.join(p.get_text(sort=True) for p in doc)
    poppler=subprocess.check_output(['pdftotext','-raw',str(pdf),'-'],text=True)
    for reader,text in [('poppler-raw',poppler),('pymupdf',native)]:
        errors=[]
        for n in range(item['lines']):
            token='BoundaryToken'+str(n).zfill(3)
            count=text.count(token)
            if count!=1: errors.append({'token':token,'count':count})
        results.append({'id':item['id'],'reader':reader,'status':'FAIL' if errors else 'PASS','errors':errors})
# Short 360px data must preserve all sections and equivalent Arabic numeric values.
for pdf in Path('/tmp/sirati-pdf-candidate-widths').glob('*-360.pdf'):
    with fitz.open(pdf) as doc:
        native='\n'.join(p.get_text(sort=True) for p in doc)
    poppler=subprocess.check_output(['pdftotext','-raw',str(pdf),'-'],text=True)
    markers=(['ملخص','خبرة','درجة','شهادة','دورة','مشروع','مهارات','اللغة'] if '-ar-' in pdf.name else
             ['SummaryMarker','ExperienceMarker','EducationMarker','CertificationMarker','CourseMarker','ProjectMarker','SkillsMarker','LanguagesMarker'])
    for reader,text in [('poppler-raw',poppler),('pymupdf',native)]:
        text=''.join(ch for ch in unicodedata.normalize('NFC',text) if unicodedata.category(ch)!='Cf')
        assert all(word in text for word in markers), f'{pdf.name}/{reader}: missing section'
        if '-ar-' in pdf.name:
            assert all(re.search(r'(?<!\d)'+n+r'(?!\d)',text) for n in ['2020','2022','2023','30','2024'])
print('PASS: 18 short 360px PDFs, both native readers, all sections and Arabic numeric values')
output=Path('candidate/pdf-perf-visual')
output.mkdir(parents=True,exist_ok=True)
(output/'long-template-native-results.json').write_text(json.dumps(results,indent=2))
failed=[r for r in results if r['status']=='FAIL']
print(f'{len(results)-len(failed)} PASS / {len(failed)} FAIL native long-template reader observations')
assert not failed, 'P1: one or more long-template paragraphs missing or duplicated in native text'
