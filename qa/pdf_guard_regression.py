"""Exercise the real PDF guard in a disposable checkout, with synthetic artifacts."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
PIN = 'd909eba3ae04d5bd246ef8e06a7938cd9bf36d75'


class GuardRegression(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / 'repo'
        subprocess.run(['git', 'clone', '--quiet', '--shared', str(REPO), str(self.repo)], check=True)
        subprocess.run(['git', 'checkout', '--quiet', PIN], cwd=self.repo, check=True)
        shutil.copyfile(REPO / 'qa/pdf_release_guard.py', self.repo / 'qa/pdf_release_guard.py')
        self.root = Path(self.temp.name) / 'app'
        self.write('package.json', json.dumps({'dependencies': {}}))
        self.write('lib/siratiPdfExport.ts', 'const pageWords = wordsByPage(words, pageCuts);\nif (embedded !== words.length) throw Error();')
        self.write('out/builder/index.html', '<script src="/sirati/_next/test.js"></script>')
        for font in ('arabic', 'latin'):
            self.write('out/fonts/pdf-naskh-' + font + '.woff', 'x' * 1001)

    def write(self, path, content, repo=False):
        target = (self.repo if repo else self.root) / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    def check(self, succeeds, message=''):
        result = subprocess.run([sys.executable, str(self.repo / 'qa/pdf_release_guard.py'), str(self.root), '--production'], capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, succeeds, result.stdout + result.stderr)
        self.assertIn(message, result.stdout + result.stderr)

    def test_pinned_session_candidate_passes(self):
        self.check(True, 'V21 runtime and account tests match')

    def test_historical_pdf_release_still_passes(self):
        subprocess.run(['git', 'checkout', '--quiet', '25b29f883edfd09797bbc974c0acf2224844479e'], cwd=self.repo, check=True)
        self.check(True, 'PDF dependency and exact text coverage guards')

    def test_runtime_edit_rejected(self):
        self.write('.github/scripts/session_boundary_v21.py', '# unexpected runtime edit', repo=True)
        self.check(False, 'Unreviewed V21 source change')

    def test_deploy_gate_edit_rejected(self):
        path = self.repo / '.github/workflows/pages.yml'
        path.write_text(path.read_text().replace('default: false', 'default: true'))
        self.check(False, 'Unreviewed V21 source change')

    def test_pdf_coverage_guard_required(self):
        self.write('lib/siratiPdfExport.ts', 'const pageWords = wordsByPage(words, pageCuts);')
        self.check(False, 'AssertionError')

    def test_unsafe_word_tolerance_rejected(self):
        path = self.root / 'lib/siratiPdfExport.ts'
        path.write_text(path.read_text() + '\nw.top + 0.5;')
        self.check(False, 'AssertionError')

    def test_qa_route_rejected(self):
        self.write('app/qa-pdf-probe/page.tsx', 'synthetic')
        self.check(False, 'Synthetic route in production source')

    def test_staging_backend_rejected(self):
        self.write('out/backend.js', 'ykfxcxhozqqsvhtdyxho.supabase.co')
        self.check(False, 'Staging Supabase shipped')

    def test_missing_font_rejected(self):
        self.write('out/fonts/pdf-naskh-arabic.woff', '')
        self.check(False, 'AssertionError')

    def test_wrong_basepath_rejected(self):
        self.write('out/builder/index.html', '<script src="/_next/test.js"></script>')
        self.check(False, 'Wrong base path')


if __name__ == '__main__':
    unittest.main()
