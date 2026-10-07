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
