"""PDF V14 scope and production-path checks; no remote account operations."""
import subprocess
import sys
from pathlib import Path

root = Path(sys.argv[1])
repo = Path(__file__).resolve().parents[1]
base = '54461f950554c18d64690331020596dcf79e43cb'
staging = '78ab9519599bf3436fce4418b3fe7bdfdd8e56b7'
runtime = {'.github/scripts/prepare_pages.py', '.github/scripts/compact_ats_template.py',
           '.github/scripts/pdf_text_layer_v19.py', '.github/scripts/minimal_home_v13.py'}
changed = subprocess.check_output(['git', 'diff', '--name-only', base], cwd=repo, text=True).splitlines()
for path in changed:
    assert path in runtime or path.startswith('qa/pdf_') or path in {
        '.github/workflows/pdf-release-qa.yml', '.github/workflows/pages.yml', 'docs/PDF_RELEASE_V14.md', 'AGENT_BOARD.md'}, path
# Regression gate: PR/build checks must never restore automatic
# Production deployment. Only an approved manual dispatch on main can publish.
workflow = (repo / '.github/workflows/pages.yml').read_text(encoding='utf-8')
deploy_anchor = '\n  deploy:\n'
assert workflow.count(deploy_anchor) == 1, 'Exactly one Pages deployment job required'
build_section, deploy_section = workflow.split(deploy_anchor, 1)
assert '\npermissions:\n  contents: read\n' in build_section, 'Default workflow permissions expanded'
assert 'uses: actions/deploy-pages@' not in build_section, 'Unexpected deployment before approval'
assert workflow.count('uses: actions/deploy-pages@') == 1, 'Additional Pages deploy action found'
assert "workflow_dispatch:\n    inputs:\n      approve_production_deploy:" in build_section, 'Approval input removed'
assert all(x in build_section for x in ('required: true', 'type: boolean', 'default: false')), 'Approval must be required, boolean and default denied'
expected_gate = "    if: github.event_name == 'workflow_dispatch' && github.ref == 'refs/heads/main' && inputs.approve_production_deploy == true"
assert deploy_section.count('\n    if:') == 1 and expected_gate in deploy_section, 'Pages deployment no longer requires manual approval on main'
assert '    permissions:\n      contents: read\n      pages: write\n      id-token: write\n' in deploy_section, 'Deploy-only permissions changed'
assert '\n    environment:\n      name: github-pages\n' in deploy_section, 'Production environment guard removed'
print('PASS: PR/main builds cannot automatically publish; explicit main dispatch is required')

original = subprocess.check_output(['git', 'show', base + ':.github/scripts/prepare_pages.py'], cwd=repo, text=True)
candidate = (repo / '.github/scripts/prepare_pages.py').read_text()
assert candidate.startswith(original), 'Original reconstruction/auth ordering changed'
assert candidate[len(original):].count('subprocess.run(') == 2
# V15 is an intentional remediation of the staged algorithm. Protect all
# non-exporter generated application sources against the verified V14 head.
v14 = 'c18427445bd521e0acba5ee6f6c34ae30168037b'
followup = subprocess.check_output(['git', 'diff', '--name-only', v14], cwd=repo, text=True).splitlines()
for path in followup:
    assert path in {'.github/scripts/pdf_text_layer_v19.py', '.github/scripts/compact_ats_template.py', '.github/scripts/minimal_home_v13.py'} or path.startswith('qa/pdf_') or path in {
        '.github/workflows/pdf-release-qa.yml', '.github/workflows/pages.yml', 'docs/PDF_RELEASE_V14.md', 'AGENT_BOARD.md'}, path
for path in ['.github/scripts/prepare_pages.py', '.github/scripts/compact_ats_template.py']:
    expected = subprocess.check_output(['git','show',v14+':'+path],cwd=repo,text=True)
    actual = (repo/path).read_text()
    if path.endswith('compact_ats_template.py'):
        # V16 is strictly additive to V14; never rewrite the validated template.
        assert actual.startswith(expected), 'V14 Compact ATS template was rewritten'
        tail = actual[len(expected):]
        assert tail.startswith('\n# V16: narrowly scope the Arabic Experience bullet alignment')
        assert tail.count('/* V16 Compact ATS Arabic Experience bullets */') == 2  # Sentinel string + CSS comment
        assert '.template-compact-ats[dir="rtl"] .cv-bullets' in tail
        assert '.template-compact-ats[dir="rtl"] .cv-bullets > li' in tail
        assert 'css_path.write_text(css, encoding="utf-8")' in tail
    else:
        assert actual == expected, 'Protected V14 generator changed: '+path
# V18 permits exactly two homepage FAQ copy substitutions, no other generator edits.
home_path = '.github/scripts/minimal_home_v13.py'
expected_home = subprocess.check_output(['git', 'show', base + ':' + home_path], cwd=repo, text=True)
for old, new in [
    ('Yes. CV templates, smart writing tools and browser PDF export are free.',
     'Yes. CV templates, smart writing tools and PDF downloads are free. No payment is required.'),
    ('Yes. Choose Print / Save free PDF, then Save as PDF in your browser.',
     'Yes. Create and edit as a guest, then choose Save PDF. Sign in or create a free account at that step to download your PDF directly.'),
]:
    assert expected_home.count(old) == 1
    expected_home = expected_home.replace(old, new)
assert (repo / home_path).read_text() == expected_home, 'Unapproved homepage generator change'
board_before = subprocess.check_output(['git', 'show', base + ':AGENT_BOARD.md'], cwd=repo, text=True)
assert (repo / 'AGENT_BOARD.md').read_text().startswith(board_before), 'Existing task ownership changed'
# V17 dependency removal must leave the actual exporter byte-identical.
import json
assert 'jspdf' not in json.loads((root/'package.json').read_text())['dependencies']
assert 'jspdf' not in (root/'lib/siratiPdfExport.ts').read_text()
exporter=(root/'lib/siratiPdfExport.ts').read_text()
assert 'const pageWords = wordsByPage(words, pageCuts)' in exporter
assert 'if (embedded !== words.length)' in exporter
assert 'w.top + 0.5' not in exporter and 'w.top + 1' not in exporter
print('PASS: scoped V15 remediation; V14 auth/reconstruction/templates preserved; exact text coverage guard')
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
