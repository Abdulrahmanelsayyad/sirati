"""Bounded local verification, not an AI agent or a production release approval."""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
import tempfile

REPO = Path(__file__).resolve().parents[1]
PUBLIC_DIRS = ('app', 'components', 'lib', 'public')
PATTERNS = {
    'server-secret': re.compile(r'(?<![A-Za-z0-9_])sb_secret_[A-Za-z0-9_-]{12,}'),
    'private-key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'public-privileged-env': re.compile(r'(?<![A-Za-z0-9_])NEXT_PUBLIC_[A-Z0-9_]*(?:SERVICE_ROLE|SECRET|PRIVATE_KEY)[A-Z0-9_]*\b'),
    'provider-secret': re.compile(r'(?<![A-Za-z0-9_])(?:sk-proj-|sk-ant-|ghp_|github_pat_)[A-Za-z0-9_-]{20,}'),
}
JWT = re.compile(r'(?<![A-Za-z0-9_])eyJ[A-Za-z0-9_-]+\.([A-Za-z0-9_-]+)\.[A-Za-z0-9_-]+')


def findings(text: str) -> list[dict]:
    """Return locations/rule IDs only; never include matched credential values."""
    result = []
    for rule, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            result.append({'rule': rule, 'line': text.count('\n', 0, match.start()) + 1})
    for match in JWT.finditer(text):
        try:
            payload = json.loads(base64.urlsafe_b64decode(match[1] + '=' * (-len(match[1]) % 4)))
        except (ValueError, UnicodeError):
            continue
        if isinstance(payload, dict) and payload.get('role') == 'service_role':
            result.append({'rule': 'privileged-jwt', 'line': text.count('\n', 0, match.start()) + 1})
    return result


def scan(root: Path) -> dict:
    """Supplemental client boundary check, not a general secret scanner or RLS proof."""
    errors, hits, paths = [], [], []
    for name in PUBLIC_DIRS:
        directory = root / name
        if not directory.is_dir() or directory.is_symlink():
            errors.append({'path': name, 'rule': 'missing-or-symlink-directory'})
            continue
        for path in sorted(directory.rglob('*')):
            if path.is_symlink():
                errors.append({'path': str(path.relative_to(root)), 'rule': 'symlink-not-scanned'})
                continue
            if not path.is_file():
                continue
            paths.append(path)
            # latin1 preserves ASCII credential patterns inside otherwise binary assets.
            for hit in findings(path.read_bytes().decode('latin1')):
                hits.append({'path': str(path.relative_to(root)), **hit})
    if not paths:
        errors.append({'rule': 'empty-source'})
    return {'status': 'FAIL' if hits or errors else 'PASS', 'files': len(paths),
            'findings': hits, 'errors': errors}


def run_check(name: str, argv: list[str], cwd: Path, timeout: float = 90) -> dict:
    start = time.perf_counter()
    status, code, diagnostics = 'BLOCKED', None, []
    # Explicit environment allowlist: checks need no credentials or customer backend.
    env = {key: os.environ[key] for key in ('PATH', 'SYSTEMROOT', 'TMPDIR') if key in os.environ}
    env.update({'CI': 'true', 'NEXT_TELEMETRY_DISABLED': '1', 'PYTHONIOENCODING': 'utf-8'})
    try:
        with tempfile.TemporaryFile() as log, subprocess.Popen(argv, cwd=cwd, env=env, stdout=log,
                              stderr=log, start_new_session=True) as process:
            try:
                code = process.wait(timeout=timeout)
                status = 'PASS' if code == 0 else 'FAIL'
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
                status = 'TIMEOUT'
            if status != 'PASS':
                log.seek(0)
                output = log.read(65536).decode('utf-8', errors='replace')
                # Only fixed exception class names; assertion messages may contain CVs/secrets.
                diagnostics = sorted(set(re.findall(r'\b(?:AssertionError|SyntaxError|TypeError|ReferenceError|ValueError|FileNotFoundError|ERR_ASSERTION|TimeoutError)\b', output)))
    except OSError:
        pass
    return {'id': name, 'status': status, 'exit_code': code,
            'elapsed_ms': round((time.perf_counter() - start) * 1000, 3),
            'reproduce': argv, 'diagnostic_types': diagnostics}


def checks(root: Path) -> list[tuple[str, list[str]]]:
    return [
        ('account-draft-synthetic', [sys.executable, 'qa/account_storage_check.py', str(root)]),
        ('duplicate-cv-source', [sys.executable, 'qa/multi_cv_duplicate_check.py', str(root)]),
        ('pdf-order-sql-static', [sys.executable, 'qa/pdf_order_policy_static_check.py']),
        ('pdf-boundary-behavior', ['node', 'qa/pdf_boundary_check.mjs', str(root / 'lib/siratiPdfExport.ts')]),
    ]


def fingerprint(root: Path) -> str:
    # Hash relevant source and verifier inputs so dirty work is not represented by SHA alone.
    inputs = sorted(set(p for n in PUBLIC_DIRS for p in (root / n).rglob('*') if p.is_file() and not p.is_symlink()) |
                    {root / 'package.json', Path(__file__)} |
                    set((REPO / 'qa').glob('*.py')) | set((REPO / 'qa').glob('*.cjs')) |
                    set((REPO / 'qa').glob('*.mjs')) | set((REPO / 'qa').glob('*.sql')) |
                    set((REPO / 'supabase/migrations').glob('*.sql')))
    digest = hashlib.sha256()
    for path in inputs:
        label = 'source/' + str(path.relative_to(root)) if path.is_relative_to(root) else str(path.relative_to(REPO))
        digest.update(label.encode() + b'\0' + path.read_bytes() + b'\0')
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.unlink(missing_ok=True)  # Never leave stale PASS evidence on failure.
    root = args.source.resolve()
    if not (root / 'package.json').is_file():
        parser.error('Reconstruct the application first; package.json is missing')
    started = time.perf_counter()
    before = fingerprint(root)
    boundary = scan(root)
    results = [run_check(name, argv, REPO) for name, argv in checks(root)]
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()
    after = fingerprint(root)
    unchanged = before == after
    report = {'schema_version': 1, 'commit': sha, 'input_sha256': before, 'inputs_unchanged': unchanged,
              'status': 'PASS' if unchanged and boundary['status'] == 'PASS' and all(r['status'] == 'PASS' for r in results) else 'FAIL',
              'client_boundary': boundary, 'checks': results,
              'not_run': ['live-account-isolation', 'live-RLS', 'browser-E2E', 'PDF-native-reader-matrix',
                          'dependency-audit', 'independent-human-review'],
              'release_approved': False, 'elapsed_ms': round((time.perf_counter()-started)*1000, 3)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
