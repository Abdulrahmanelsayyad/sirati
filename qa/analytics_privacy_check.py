"""Behavior test for analytics privacy exclusion (synthetic inputs only)."""
from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1]).resolve()
tracker = root / "components" / "SiratiAnalyticsTracker.tsx"
dashboard = root / "app" / "analytics" / "page.tsx"
if not tracker.is_file() or not dashboard.is_file():
    raise SystemExit("Analytics generated components missing")

# Executes only the pure privacy predicate with synthetic browser inputs.
# No network, no real customer accounts and no analytics events are used.
js = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const dashboard = fs.readFileSync(process.argv[2], 'utf8');
const start = src.indexOf('function trackingBlocked() {');
const end = src.indexOf('\n}\n\nexport default function', start);
assert(start >= 0 && end > start, 'privacy predicate missing');
const fn = src.slice(start, end + 2)
  .replace('navigator as Navigator & { globalPrivacyControl?: boolean }', 'navigator');
const check = new Function('navigator', 'localStorage',
  fn + '\nreturn trackingBlocked();');
const normal = {doNotTrack:'0',globalPrivacyControl:false};
const storage = answer => ({getItem:()=>answer});
assert.equal(check(normal, storage(null)), false, 'ordinary consented browsing must be eligible');
assert.equal(check(normal, storage('yes')), true, 'owner QA opt-out must always block');
assert.equal(check({doNotTrack:'1'}, storage(null)), true, 'DNT must block');
assert.equal(check({globalPrivacyControl:true}, storage(null)), true, 'GPC must block');
assert.equal(check(normal, {getItem:()=>{throw Error('blocked');}}), true,
  'storage exceptions must fail closed');
assert(src.includes("const ENABLED = process.env.NEXT_PUBLIC_ANALYTICS_ENABLED === 'true';"),
  'collection must be feature-flagged off by default');
assert(src.includes("if (trackingBlocked()) {"),
  'initial choice must honor exclusions');
assert(src.includes("choice !== 'yes' || trackingBlocked() || sentFor.current"),
  'pageview requests must recheck exclusions');
assert(src.includes("choice === 'loading' || trackingBlocked()) return null"),
  'privacy controls must not reactivate excluded test traffic');
assert(src.includes("sessionStorage.setItem(SID_KEY, sid)"),
  'analytics identifier must be tab-session scoped');
assert(src.includes("p_type: 'page_view', p_route: safeRoute(pathname)"),
  'only a normalized route may be sent');
assert(dashboard.includes("client.rpc('sirati_analytics_summary'"),
  'dashboard must fetch protected aggregate RPC');
assert(!dashboard.includes(".from('cv_documents')"),
  'owner aggregate dashboard must not query customer documents directly');
console.log('PASS: analytics QA exclusion, DNT, GPC, storage failure, consent + server-gated aggregate source');
"""
subprocess.run(
    ["node", "-e", js, str(tracker), str(dashboard)],
    check=True
)
