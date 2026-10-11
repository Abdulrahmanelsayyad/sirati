"""Adversarial boundary and failure-contract regressions; no real credentials."""
import base64
import json
from pathlib import Path
import sys
import tempfile
import unittest

from verification import findings, run_check, scan, fingerprint


def jwt(role):
    payload = base64.urlsafe_b64encode(json.dumps({'role': role}).encode()).decode().rstrip('=')
    return 'eyJhbGciOiJIUzI1NiJ9.' + payload + '.synthetic'


class VerificationTests(unittest.TestCase):
    def test_privileged_credentials_detected_without_echo(self):
        samples = [
            'sb_' + 'secret_' + 'synthetic' * 3,
            '-----BEGIN ' + 'PRIVATE KEY-----',
            'process.env.' + 'NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY',
            'sk-' + 'proj-' + 'synthetic' * 4,
            'sk-' + 'ant-' + 'synthetic' * 4,
            'gh' + 'p_' + 'synthetic' * 4,
            'github_' + 'pat_' + 'synthetic' * 4,
            jwt('service_role'),
        ]
        for sample in samples:
            with self.subTest(kind=sample[:5]):
                result = findings('\n' + sample)
                self.assertTrue(result)
                self.assertEqual(result[0]['line'], 2)
                self.assertNotIn(sample, json.dumps(result))

    def test_publishable_and_anon_are_not_secrets(self):
        for text in ['sb_publishable_synthetic', jwt('anon'), 'process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY']:
            self.assertEqual(findings(text), [])

    def test_malformed_and_non_object_jwt_do_not_crash(self):
        for payload in ['e30', 'W10', 'bnVsbA', 'notjson']:
            self.assertEqual(findings('eyJhbGciOiJIUzI1NiJ9.' + payload + '.fake'), [])

    def test_missing_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(scan(Path(tmp))['status'], 'FAIL')

    def test_public_assets_and_symlinks_cannot_hide_credentials(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ('app', 'components', 'lib', 'public'):
                (root / name).mkdir()
                (root / name / 'safe.ts').write_text('export {}')
            self.assertEqual(scan(root)['status'], 'PASS')
            (root / 'public/asset.bin').write_bytes(b'\xff' + jwt('service_role').encode())
            self.assertEqual(scan(root)['findings'][0]['rule'], 'privileged-jwt')
            (root / 'public/asset.bin').unlink()
            (root / 'public/link').symlink_to(root / 'app/safe.ts')
            self.assertEqual(scan(root)['status'], 'FAIL')

    def test_exit_failure_blocked_timeout_and_no_output_leak(self):
        for name, argv, expected in [
            ('pass', [sys.executable, '-c', 'print("synthetic-private-output")'], 'PASS'),
            ('fail', [sys.executable, '-c', 'raise SystemExit(7)'], 'FAIL'),
            ('missing', ['/nonexistent/sirati-test-command'], 'BLOCKED'),
            ('timeout', [sys.executable, '-c', 'import time; time.sleep(5)'], 'TIMEOUT'),
        ]:
            with self.subTest(name=name):
                result = run_check(name, argv, Path.cwd(), timeout=.2)
                self.assertEqual(result['status'], expected)
                self.assertNotIn('stdout', result)
                self.assertNotIn('stderr', result)

    def test_failure_diagnostics_do_not_echo_assertion_message(self):
        result = run_check('assertion', [sys.executable, '-c',
            'assert False, "synthetic-private-message"'], Path.cwd())
        self.assertEqual(result['diagnostic_types'], ['AssertionError'])
        self.assertEqual(result['status'], 'FAIL')

    def test_cli_removes_stale_success_for_invalid_input(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'report.json'
            output.write_text('{"status":"PASS"}')
            result = subprocess.run([sys.executable, str(Path(__file__).with_name('verification.py')),
                tmp, '--output', str(output)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())

    def test_report_rejects_input_changes_and_keeps_explicit_gaps(self):
        from unittest.mock import patch
        import verification
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'package.json').write_text('{}')
            output = root / 'report.json'
            with patch.object(sys, 'argv', ['verification', tmp, '--output', str(output)]), \
                 patch.object(verification, 'fingerprint', side_effect=['before', 'after']), \
                 patch.object(verification, 'scan', return_value={'status':'PASS'}), \
                 patch.object(verification, 'checks', return_value=[]), \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(verification.main(), 1)
            report = json.loads(output.read_text())
            self.assertFalse(report['inputs_unchanged'])
            self.assertFalse(report['release_approved'])
            self.assertIn('live-RLS', report['not_run'])

    def test_credentials_not_inherited(self):
        from unittest.mock import patch
        with patch.dict('os.environ', {'SIRATI_TEST_SECRET': 'synthetic'}):
            result = run_check('env', [sys.executable, '-c',
                'import os; assert "SIRATI_TEST_SECRET" not in os.environ'], Path.cwd())
        self.assertEqual(result['status'], 'PASS')


if __name__ == '__main__':
    unittest.main()
