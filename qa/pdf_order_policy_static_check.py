#!/usr/bin/env python3
"""Zero-dependency static checks for issue #26's proposed PDF order RLS migration.

This is NOT a substitute for applying the SQL to an isolated PostgreSQL instance
and proving the role-based INSERT cases. Its purpose is to catch malformed
regression fixtures and accidental removal of authorization requirements in CI.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "supabase/migrations/20261008144500_guard_customer_pdf_order_insert.sql"
QA = ROOT / "qa/supabase_rls.sql"

migration = MIGRATION.read_text(encoding="utf-8")
qa = QA.read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"PASS: {message}")


policy = re.search(
    r'create\\s+policy\\s+"Customer PDF orders require pending status and fixed price"'
    r'\\s+on\\s+public\\.pdf_orders\\s+as\\s+restrictive\\s+for\\s+insert'
    r'\\s+to\\s+authenticated\\s+with\\s+check\\s*\\((.*?)\\)\\s*;',
    migration, re.IGNORECASE | re.DOTALL,
)
require(policy is not None, "restrictive customer INSERT policy exists")
body = policy.group(1).lower()
for fragment in ("status = 'pending'", "amount_egp = 50", "reviewed_at is null"):
    require(fragment in body, f"INSERT policy requires {fragment}")
require(
    'drop policy if exists "Users request PDF for own document"' not in migration,
    "existing document ownership policy remains",
)
require(
    re.search(r"revoke\\s+update\\s*,\\s*delete\\s+on\\s+table\\s+public\\.pdf_orders"
              r"\\s+from\\s+anon\\s*,\\s*authenticated", migration, re.I) is not None,
    "customers cannot update or delete PDF orders",
)

opens = re.findall(r"(?mi)^\\s*do\\s+(\\$[A-Za-z0-9_]*\\$)\\s*$", qa)
closes = re.findall(r"(?mi)^\\s*end\\s+(\\$[A-Za-z0-9_]*\\$)\\s*;", qa)
require(bool(opens) and opens == closes,
        "SQL test DO blocks have matching dollar quotes (not single $)")
require(re.search(r"(?mi)^\\s*(?:do|end)\\s+\\$(?!\\$)", qa) is None,
        "SQL test has no malformed single-dollar block delimiter")
require("begin;" in qa.lower() and qa.lower().rstrip().endswith("rollback;"),
        "SQL test rolls back all synthetic records")

for name in (
    "own_pdf_order_insert",
    "cross_document_pdf_order_blocked",
    "pdf_order_restrictive_guard_present",
    "pdf_order_self_approval_blocked",
    "pdf_order_price_tampering_blocked",
    "pdf_order_fake_review_blocked",
    "pdf_order_self_rejection_blocked",
):
    require(f"'{name}'" in qa, f"SQL regression includes {name}")

print("Static SQL policy contract checks passed. PostgreSQL role testing still required.")
