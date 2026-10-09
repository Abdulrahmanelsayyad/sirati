from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
path = root / "app" / "builder" / "page.tsx"
text = path.read_text(encoding="utf-8")

required = {
    "account key helper": "function accountDraftStorageKey(userId: string)",
    "scoped key format": "return `${STORAGE_KEY}.${userId}`;",
    "cloud mode avoids shared draft": "} else if (!isSupabaseConfigured()) {",
    "scoped save": "localStorage.setItem(accountDraftStorageKey(userId), payload);",
    "save waits for identity": "if (!userId) return;",
    "scoped restore": "localStorage.getItem(accountDraftStorageKey(user.id))",
    "legacy shared key preserved": "const STORAGE_KEY = 'sirati.cv.v2';",
}

missing = [name for name, needle in required.items() if needle not in text]
if missing:
    raise SystemExit("Account draft isolation source check failed: " + ", ".join(missing))


print("PASS: account-scoped local draft source invariants")

# Run behavior regressions against the same prepared builder used by the build.
import subprocess
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
    client_match = re.search(r"await ([A-Za-z_$][\w$]*)\.auth\.getSession\(\)", block)
    if not client_match:
        raise SystemExit(f"Missing active session lookup: {relative}")
    client_name = client_match.group(1)
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
  let signedOut=0, confirmed=0, alerts=0;
  const window = {
    localStorage: {getItem: k=>cache.get(k)||null, removeItem:k=>cache.delete(k)},
    confirm:()=>{confirmed++;return allowed;},
    alert:()=>{alerts++;}
  };
  const auth = {auth:{
    getSession:async()=>({data:{session:{user:{id:'A'}}}}),
    signOut:async()=>{signedOut++;return {error:logoutFails?Error('synthetic'):null};}
  }};
  await handler(auth,window);
  return {cache,signedOut,confirmed,alerts};
}
(async()=>{
  let s=await check({allowed:false});
  assert.equal(s.signedOut,0);assert(s.cache.has('sirati.cv.v2.A'));
  s=await check({});
  assert.equal(s.signedOut,1);assert(!s.cache.has('sirati.cv.v2.A'));
  assert(s.cache.has('sirati.cv.v2.B'));assert(s.cache.has('sirati.cv.v2'));
  s=await check({logoutFails:true});
  assert.equal(s.signedOut,1);assert(s.cache.has('sirati.cv.v2.A'));
  assert.equal(s.alerts,1);
  s=await check({hasDraft:false});
  assert.equal(s.confirmed,0);assert.equal(s.signedOut,1);
  console.log('PASS: synthetic sign-out cancellation, scoped purge, failure retention, legacy preservation');
})().catch(e=>{console.error(e);process.exitCode=1;});
""".replace("CLIENT", json.dumps(client_name)).replace("SNIPPET", json.dumps(block))
    subprocess.run(["node", "-e", js], check=True)
print("PASS: generated sign-out safety invariants (real A/B still NOT RUN)")
