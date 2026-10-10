from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
path = root / "app" / "builder" / "page.tsx"
text = path.read_text(encoding="utf-8")

required = {
    "account key helper": "function accountDraftStorageKey(userId: string)",
    "scoped key format": "return `${STORAGE_KEY}.${userId}`;",
    "cloud mode avoids shared draft": "} else if (!isSupabaseConfigured()) {",
    "scoped save": "window.sessionStorage.setItem(accountDraftStorageKey(userId), payload);",
    "save waits for identity": "if (!userId) return;",
    "scoped restore": "window.sessionStorage.getItem(accountDraftStorageKey(user.id))",
    "legacy shared key preserved": "const STORAGE_KEY = 'sirati.cv.v2';",
}

missing = [name for name, needle in required.items() if needle not in text]
if missing:
    raise SystemExit("Account draft isolation source check failed: " + ", ".join(missing))


if "window.localStorage.getItem(draftKey)" in text:
    raise SystemExit("Persistent plaintext CV migration must be disabled for prelaunch reset")

# Run the actual sitewide cleanup effect on synthetic browser storage, not
# any connected customer session. Purge is ONE TIME to preserve later CV edits.
cleanup = (root / "components" / "LegacyJobMatchCleanup.tsx").read_text(encoding="utf-8")
for token in ("QA_CV_PURGE_MARKER", "sirati.cv.v1", "sirati.cv.v2.",
              "isOldCvDraftKey", "window.localStorage.setItem(QA_CV_PURGE_MARKER, '1')"):
    if token not in cleanup:
        raise SystemExit("Missing prelaunch CV cleanup token: " + token)
import subprocess
test_js = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const src = fs.readFileSync(process.argv[1], 'utf8');
const defsStart = src.indexOf("const LEGACY_PREFIX");
const defsEnd = src.indexOf("export default function", defsStart);
const bodyStart = src.indexOf("  useEffect(() => {", defsEnd) + "  useEffect(() => {".length;
const bodyEnd = src.indexOf("  }, []);", bodyStart);
assert(defsStart >= 0 && defsEnd > defsStart && bodyStart > defsEnd && bodyEnd > bodyStart);
const defs = src.slice(defsStart, defsEnd).replace("key: string", "key");
const run = new Function('window', defs + '\n' + src.slice(bodyStart, bodyEnd));
function store(entries) {
  const m = new Map(entries);
  return {get length(){return m.size;},key:i=>[...m.keys()][i]||null,
    getItem:k=>m.get(k)||null,setItem:(k,v)=>m.set(k,v),
    removeItem:k=>m.delete(k),has:k=>m.has(k)};
}
const local = store([
  ['sirati.cv.v1','old1'],['sirati.cv.v2','old2'],
  ['sirati.cv.v2.A','oldA'],['sirati.cv.v2.B','oldB'],
  ['sirati.onboarding.template','compact'],
  ['sb-example-auth-token','leave-auth-alone'],
  ['sirati.analytics.consent.v1','yes']
]);
const session = store([['sirati.cv.v2.A','oldTabA'],['sirati.jobTailor.v2.A','oldTailor']]);
const window = {localStorage:local,sessionStorage:session};
run(window);
for (const k of ['sirati.cv.v1','sirati.cv.v2','sirati.cv.v2.A','sirati.cv.v2.B'])
  assert(!local.has(k), k);
assert(!session.has('sirati.cv.v2.A'));
assert(!session.has('sirati.jobTailor.v2.A'));
assert.equal(local.getItem('sirati.privacy.prelaunch-reset.v1'),'1');
assert.equal(local.getItem('sb-example-auth-token'),'leave-auth-alone');
assert.equal(local.getItem('sirati.onboarding.template'),'compact');
assert.equal(local.getItem('sirati.analytics.consent.v1'),'yes');
local.setItem('sirati.cv.v2','newGuestDraft');
session.setItem('sirati.cv.v2.A','newSignedInTab');
run(window);
assert.equal(local.getItem('sirati.cv.v2'),'newGuestDraft');
assert.equal(session.getItem('sirati.cv.v2.A'),'newSignedInTab');
console.log('PASS: prelaunch one-time purge removes only legacy trial CV keys and preserves future drafts');
"""
subprocess.run(["node", "-e", test_js,
                str(root / "components" / "LegacyJobMatchCleanup.tsx")], check=True)
print("PASS: account-scoped per-tab draft source + controlled prelaunch CV purge")

# Run behavior regressions against the same prepared builder used by the build.
import subprocess
# Parse the opt-in A/B privacy harness at every CI run; do NOT execute it without fixture accounts.
subprocess.run(['node', '--check', str(Path(__file__).with_name('live_account_ab_readonly.mjs'))], check=True)
print('PASS: optional real-account A/B test harness has valid JavaScript syntax (live test NOT RUN)')
subprocess.run([
    'node', str(Path(__file__).with_name('new_cv_regression.cjs')),
    str(root),
], check=True)

# Targeted sign-out privacy regression: use synthetic local keys only.
# This is not a real A/B auth/browser test; PR #73 remains that independent gate.
import json
import re

for relative in ("components/AccountNav.tsx", "app/documents/page.tsx"):
    code = (root / relative).read_text(encoding="utf-8")
    start = code.find("// SIRATI_PRIVACY_SIGNOUT_START")
    end = code.find("// SIRATI_PRIVACY_SIGNOUT_END", start)
    if start < 0 or end < 0 or code.count("// SIRATI_PRIVACY_SIGNOUT_START") != 1:
        raise SystemExit(f"Privacy sign-out guard missing or duplicated: {relative}")
    block = code[start:end]
    client_match = re.search(r"const draftAuthClient = ([A-Za-z_$][\w$]*(?:\(\))?);", block)
    if not client_match or "await draftAuthClient.auth.getSession()" not in block:
        raise SystemExit(f"Missing active session lookup: {relative}")
    client_expr = client_match.group(1)
    client_name = client_expr[:-2] if client_expr.endswith("()") else client_expr
    client_arg = "() => auth" if client_expr.endswith("()") else "auth"
    if "localStorage.clear(" in block or "sirati.cv.v1" in block:
        raise SystemExit(f"Unsafe broad/legacy draft deletion in {relative}")
    js = """
const assert = require('node:assert/strict');
const AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;
const handler = new AsyncFunction(CLIENT, 'window', SNIPPET);
async function check({allowed=true, logoutFails=false, hasDraft=true}) {
  const cache = new Map([
    ['sirati.cv.v2.A', hasDraft ? '{"data":"synthetic"}' : ''],
    ['sirati.cv.v2.B', '{"data":"keep B"}'],
    ['sirati.cv.v2', '{"data":"keep legacy"}']
  ]);
  const sessionCache = new Map([
    ['sirati.cv.v2.A', hasDraft ? '{"data":"current tab A"}' : ''],
    ['sirati.cv.v2.B', '{"data":"keep session B"}']
  ]);
  let signedOut=0, confirmed=0, alerts=0;
  const window = {
    localStorage: {getItem: k=>cache.get(k)||null, removeItem:k=>cache.delete(k)},
    sessionStorage: {getItem: k=>sessionCache.get(k)||null, removeItem:k=>sessionCache.delete(k)},
    confirm:()=>{confirmed++;return allowed;},
    alert:()=>{alerts++;}
  };
  const auth = {auth:{
    getSession:async()=>({data:{session:{user:{id:'A'}}}}),
    signOut:async()=>{signedOut++;return {error:logoutFails?Error('synthetic'):null};}
  }};
  await handler(AUTH_ARG,window);
  return {cache,sessionCache,signedOut,confirmed,alerts};
}
(async()=>{
  let s=await check({allowed:false});
  assert.equal(s.signedOut,0);assert(s.cache.has('sirati.cv.v2.A'));assert(s.sessionCache.has('sirati.cv.v2.A'));
  s=await check({});
  assert.equal(s.signedOut,1);assert(!s.cache.has('sirati.cv.v2.A'));assert(!s.sessionCache.has('sirati.cv.v2.A'));
  assert(s.cache.has('sirati.cv.v2.B'));assert(s.sessionCache.has('sirati.cv.v2.B'));assert(s.cache.has('sirati.cv.v2'));
  s=await check({logoutFails:true});
  assert.equal(s.signedOut,1);assert(s.cache.has('sirati.cv.v2.A'));assert(s.sessionCache.has('sirati.cv.v2.A'));
  assert.equal(s.alerts,1);
  s=await check({hasDraft:false});
  assert.equal(s.confirmed,0);assert.equal(s.signedOut,1);
  console.log('PASS: synthetic logout safety for local+session scoped drafts, failure retention, and other-user preservation');
})().catch(e=>{console.error(e);process.exitCode=1;});
""".replace("CLIENT", json.dumps(client_name)).replace("SNIPPET", json.dumps(block)).replace("AUTH_ARG", client_arg)
    subprocess.run(["node", "-e", js], check=True)
print("PASS: generated sign-out safety invariants (real A/B still NOT RUN)")
