"""Check actual generated route normalization and exported local asset/link targets."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import subprocess
import sys

root = Path(sys.argv[1]).resolve()
base = sys.argv[2] if len(sys.argv) > 2 else '/buyer-cv'
tracker = (root / 'components/SiratiAnalyticsTracker.tsx').read_text()
start = tracker.index('function safeRoute(')
end = tracker.index('\nfunction trackingBlocked', start)
function = tracker[start:end].replace('path: string', 'path')
subprocess.run(['node', '-e', '''
const assert = require('node:assert/strict');
const source = JSON.parse(process.argv[1]);
for (const prefix of ['', '/sirati', '/buyer-cv', '/team/cv']) {
  const route = new Function('BASE_PATH', source + '; return safeRoute;')(prefix);
  for (const p of ['/', '/builder/', '/templates/', '/documents/private-id']) {
    const expected = p === '/' ? '/' : '/' + p.split('/')[1];
    assert.equal(route(prefix + p), expected);
    assert.equal(route(p), expected); // Next usePathname can omit basePath.
  }
  assert.equal(route(prefix + '/unknown/private-id'), '/other');
  assert.equal(route(prefix + 'suffix/builder'), '/other');
}
console.log('PASS: generated route normalization, exact prefix boundary and privacy allowlist');
''', json.dumps(function)], check=True)

out = root / 'out'
assert (out / 'index.html').is_file(), 'Missing exported build'
checked = set()
class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key not in ('href', 'src') or not value or not value.startswith('/'):
                continue
            url = urlsplit(value)
            if url.netloc:
                continue
            path = unquote(url.path)
            assert path == base or path.startswith(base + '/'), f'Outside base path: {path}'
            relative = path[len(base):].lstrip('/')
            target = out / relative
            assert target.is_file() or (target / 'index.html').is_file(), f'Missing export target: {path}'
            checked.add(path)

for path in out.rglob('*.html'):
    Links().feed(path.read_text())
assert len(checked) >= 5, 'Insufficient exported-link coverage'
print(f'PASS: {len(checked)} exported asset/link targets under {base or "/"}')
