from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
path = root / "components" / "DuplicateCvAction.tsx"
text = path.read_text(encoding="utf-8")

required = [
    "from('cv_documents')",
    ".eq('user_id', auth.user.id)",
    "user_id: auth.user.id",
    "crypto.randomUUID()",
    "title: newTitle",
    "data: source.data",
    "template: source.template",
    "language: source.language",
    "Payment orders and order history are not copied.",
]
for item in required:
    if item not in text:
        raise SystemExit(f"Duplicate CV safety check missing: {item}")

for forbidden in [".update(", ".delete(", "from('pdf_orders')", "from('cv_versions')"]:
    if forbidden in text:
        raise SystemExit(f"Duplicate CV action must not mutate unrelated/original records: {forbidden}")

if text.count(".from('cv_documents')") != 2:
    raise SystemExit("Duplicate CV action should only read the source document and insert one copy.")

print("PASS: duplicate CV action is owner-scoped and copies only CV document data.")
