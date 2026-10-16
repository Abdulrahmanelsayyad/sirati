"""Mutation tests for current PDF safety and opt-in scope, without remote data."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]

class GuardRegression(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / 'repo'
        self.repo.mkdir()
        self.git('init', '-q')
        self.git('config', 'user.email', 'synthetic@example.invalid')
        self.git('config', 'user.name', 'Synthetic QA')
        for name in ('qa/pdf_release_guard.py', '.github/workflows/pages.yml'):
            self.write(name, (REPO / name).read_text(), repo=True)
        self.commit()
        self.base = self.git('rev-parse', 'HEAD')
        self.write('qa/pdf_probe.py', '# synthetic PDF test', repo=True)
        self.commit()
        self.root = Path(self.temp.name) / 'app'
        self.write('package.json', json.dumps({'dependencies': {}}))
        self.write('lib/siratiPdfExport.ts', 'const pageWords = wordsByPage(words, pageCuts);\nif (embedded !== words.length) throw Error();')
        self.write('out/builder/index.html', '<script src="/sirati/_next/test.js"></script>')
        for font in ('arabic', 'latin'):
            self.write('out/fonts/pdf-naskh-' + font + '.woff', 'x' * 1001)

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.repo, text=True).strip()

    def commit(self):
        self.git('add', '.')
        self.git('commit', '-qm', 'synthetic fixture')

    def write(self, path, content, repo=False):
        target = (self.repo if repo else self.root) / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    def check(self, succeeds, message='', pdf_only=False, baseline=None):
        cmd = [sys.executable, str(self.repo / 'qa/pdf_release_guard.py'), str(self.root),
               '--production', '--baseline', baseline or self.base]
        if pdf_only:
            cmd.append('--pdf-only')
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode == 0, succeeds, result.stdout + result.stderr)
        self.assertIn(message, result.stdout + result.stderr)

    def test_general_product_change_passes(self):
        self.write('components/JobTitleInput.tsx', 'UI change', repo=True)
        self.commit()
        self.check(True, 'general PDF regression accepts product changes')

    def test_pdf_only_change_passes(self):
        self.check(True, 'explicit PDF-only scope', pdf_only=True)

    def test_pdf_only_rejects_product_change(self):
        self.write('components/JobTitleInput.tsx', 'UI change', repo=True)
        self.commit()
        self.check(False, 'Outside PDF-only scope', pdf_only=True)

    def test_pdf_only_rejects_removed_non_pdf_file(self):
        self.git('rm', '.github/workflows/pages.yml')
        self.commit()
        self.check(False, 'Outside PDF-only scope', pdf_only=True)

    def test_branch_name_not_immutable_baseline(self):
        self.check(False, 'exact commit SHA', baseline='main')

    def test_unknown_baseline_fails(self):
        self.check(False, baseline='f' * 40)

    def test_same_commit_fails(self):
        self.check(False, 'must differ', baseline=self.git('rev-parse', 'HEAD'))

    def test_pdf_only_nonancestor_fails(self):
        candidate = self.git('rev-parse', 'HEAD')
        self.git('checkout', '-qb', 'other', self.base)
        self.write('qa/pdf_other.py', '# other branch', repo=True)
        self.commit()
        other = self.git('rev-parse', 'HEAD')
        self.git('checkout', '-q', candidate)
        self.check(False, 'must be an ancestor', pdf_only=True, baseline=other)

    def test_deploy_gate_edit_rejected(self):
        path = self.repo / '.github/workflows/pages.yml'
        path.write_text(path.read_text().replace("github.event_name == 'push'", "github.event_name == 'pull_request'"))
        self.check(False, 'main push only')

    def test_deploy_build_dependency_required(self):
        path = self.repo / '.github/workflows/pages.yml'
        path.write_text(path.read_text().replace('    needs: build\n', ''))
        self.check(False, 'depend on build')

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

    def test_general_still_checks_artifacts(self):
        self.write('components/NewFeature.tsx', 'UI change', repo=True)
        self.commit()
        self.write('out/backend.js', 'ykfxcxhozqqsvhtdyxho.supabase.co')
        self.check(False, 'Staging Supabase shipped')

if __name__ == '__main__':
    unittest.main()
