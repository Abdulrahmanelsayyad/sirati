"""PDF V14 scope and production-path checks; no remote account operations."""
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1])
repo = Path(__file__).resolve().parents[1]
base = '54461f950554c18d64690331020596dcf79e43cb'
staging = '78ab9519599bf3436fce4418b3fe7bdfdd8e56b7'
runtime = {'.github/scripts/prepare_pages.py', '.github/scripts/compact_ats_template.py',
           '.github/scripts/pdf_text_layer_v19.py'}
changed = subprocess.check_output(['git', 'diff', '--name-only', base], cwd=repo, text=True).splitlines()
for path in changed:
    assert path in runtime or path.startswith('qa/pdf_') or path in {
        '.github/workflows/pdf-release-qa.yml', 'docs/PDF_RELEASE_V14.md'}, path
original = subprocess.check_output(['git', 'show', base + ':.github/scripts/prepare_pages.py'], cwd=repo, text=True)
candidate = (repo / '.github/scripts/prepare_pages.py').read_text()
assert candidate.startswith(original), 'Original reconstruction/auth ordering changed'
assert candidate[len(original):].count('subprocess.run(') == 2
staged = subprocess.check_output(['git', 'show', staging + ':.github/scripts/pdf_text_layer_v19.py'], cwd=repo, text=True)
current = (repo / '.github/scripts/pdf_text_layer_v19.py').read_text()
assert staged.replace('Intended for isolated Staging QA.',
    'Production candidate; release remains gated by isolated QA and owner review.') == current
print('PASS: unchanged staged PDF algorithm; main reconstruction preserved; scoped tracked diff')
if '--production' in sys.argv:
    out = root / 'out'
    assert out.is_dir(), 'No production artifact'
    assert not list((root / 'app').glob('qa-pdf-*/page.tsx')), 'Synthetic route in production source'
    assert not list(out.glob('qa-pdf-*')), 'Synthetic route in production output'
    assert '/sirati/_next/' in (out / 'builder/index.html').read_text(), 'Wrong base path'
    for font in ['arabic', 'latin']:
        assert (out / f'fonts/pdf-naskh-{font}.woff').stat().st_size > 1000
    for path in out.rglob('*'):
        if path.is_file() and path.suffix in {'.js', '.html', '.json'}:
            text = path.read_text(errors='replace')
            assert 'ykfxcxhozqqsvhtdyxho.supabase.co' not in text, 'Staging Supabase shipped'
            assert 'sb_publishable_WJRNf7gnhrggw8r-XB85gw_MmRvwkVt' not in text, 'Staging key shipped'
    print('PASS: /sirati production artifact, local fonts, no synthetic routes or Staging Supabase')
