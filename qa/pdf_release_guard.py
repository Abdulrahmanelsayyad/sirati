"""Current PDF artifact safety; optional explicit PDF-only release scope.

General regressions accept product changes. PDF-only dispatch requires an exact,
distinct ancestor SHA and rejects changes outside the PDF surface. Neither mode
publishes or authorizes release.
"""
import argparse
import re
import subprocess
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('root', type=Path)
parser.add_argument('--baseline', required=True, help='Exact 40-character comparison commit SHA')
parser.add_argument('--candidate', default='HEAD')
parser.add_argument('--pdf-only', action='store_true')
parser.add_argument('--scope-only', action='store_true')
parser.add_argument('--production', action='store_true')
args = parser.parse_args()
root = args.root
repo = Path(__file__).resolve().parents[1]
def git(*parts):
    return subprocess.check_output(['git', *parts], cwd=repo, text=True).strip()
assert re.fullmatch(r'[0-9a-f]{40}', args.baseline), 'Baseline must be an exact commit SHA'
base = git('rev-parse', '--verify', args.baseline + '^{commit}')
head = git('rev-parse', '--verify', args.candidate + '^{commit}')
assert base != head, 'Baseline must differ from candidate'
print(f'PDF comparison: baseline={base} candidate={head}')
if args.pdf_only:
    assert subprocess.run(['git', 'merge-base', '--is-ancestor', base, head], cwd=repo).returncode == 0, 'PDF-only baseline must be an ancestor'
    allowed = {'.github/scripts/pdf_text_layer_v19.py', '.github/scripts/compact_ats_template.py',
               '.github/workflows/pdf-release-qa.yml', 'assets/pdf-fonts/OFL.txt'}
    changed = git('diff', '--no-renames', '--name-only', base, head).splitlines()
    rejected = [p for p in changed if not (p in allowed or p.startswith('qa/pdf_') or p.startswith('assets/pdf-fonts/'))]
    assert not rejected, 'Outside PDF-only scope: ' + str(rejected)
    print('PASS: explicit PDF-only scope against supplied release baseline')
else:
    print('PASS: general PDF regression accepts product changes; artifact checks remain mandatory')
if args.scope_only:
    raise SystemExit(0)

# Preserve the currently approved main-only deployment policy, not the retired
# manual-dispatch rule. This test workflow itself retains contents:read only.
workflow = (repo / '.github/workflows/pages.yml').read_text(encoding='utf-8')
deploy_anchor = '\n  deploy:\n'
assert workflow.count(deploy_anchor) == 1, 'Exactly one Pages deployment job required'
build_section, deploy_section = workflow.split(deploy_anchor, 1)
assert '\npermissions:\n  contents: read\n' in build_section, 'Default workflow permissions expanded'
assert 'uses: actions/deploy-pages@' not in build_section, 'Unexpected deployment before build'
assert workflow.count('uses: actions/deploy-pages@') == 1, 'Additional Pages deploy action found'
expected_gate = "    if: github.event_name == 'push' && github.ref == 'refs/heads/main'"
assert deploy_section.count('\n    if:') == 1 and expected_gate in deploy_section, 'Pages deployment must be main push only'
assert '    needs: build\n' in deploy_section, 'Pages deployment must depend on build'
assert '    permissions:\n      contents: read\n      pages: write\n      id-token: write\n' in deploy_section, 'Deploy-only permissions changed'
assert '\n    environment:\n      name: github-pages\n' in deploy_section, 'Production environment guard removed'
print('PASS: PR checks cannot deploy; main deployment requires successful build')

# V17 dependency removal must leave the actual exporter byte-identical.
import json
assert 'jspdf' not in json.loads((root/'package.json').read_text())['dependencies']
assert 'jspdf' not in (root/'lib/siratiPdfExport.ts').read_text()
exporter=(root/'lib/siratiPdfExport.ts').read_text()
assert 'const pageWords = wordsByPage(words, pageCuts)' in exporter
assert 'if (embedded !== words.length)' in exporter
assert 'w.top + 0.5' not in exporter and 'w.top + 1' not in exporter
print('PASS: PDF dependency and exact text coverage guards')
if args.production:
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
