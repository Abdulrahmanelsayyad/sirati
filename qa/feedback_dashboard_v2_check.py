"""Feedback V2 generated-code invariants (no live users or backend access).

Does not replace browser QA or RLS verification. Keep exact checks narrow.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
dashboard = (root / "app/feedback-dashboard/page.tsx").read_text(encoding="utf-8")
form = (root / "components/SiratiFeedbackRating.tsx").read_text(encoding="utf-8")
styles = (root / "app/globals.css").read_text(encoding="utf-8")

checks = [
    ("owner access", "auth.user.app_metadata?.sirati_feedback_admin !== true" in dashboard),
    ("owner row-level security read", "from('sirati_site_feedback')" in dashboard),
    ("bound exact count", ".select('rating,category,comment,created_at', { count: 'exact' })" in dashboard),
    ("latest 200 sample", ".order('created_at', { ascending: false }).limit(200)" in dashboard),
    ("avoid false global average", "not necessarily all-time" in dashboard),
    ("distribution", "ratingSteps.map(" in dashboard),
    ("search", "const [search, setSearch]" in dashboard),
    ("category filter", "const [category, setCategory]" in dashboard),
    ("rating filter", "const [stars, setStars]" in dashboard),
    ("sorting", "const [sort, setSort]" in dashboard),
    ("no email or CV fields in dashboard select", ".select('rating,category,comment,created_at'" in dashboard),
    ("load only current member review", ".select('rating,category,comment').eq('user_id', auth.user.id).maybeSingle()" in form),
    ("prevent overwrite on read failure", "loadingPrevious || previousError" in form),
    ("save only current user", "if (currentUserId.current !== auth.user.id)" in form),
    ("one upsert per account", "onConflict: 'user_id'" in form),
    ("no private CV sent", "user_id: auth.user.id," in form and "document_id:" not in form),
    ("mobile inputs", "@media(max-width:600px)" in styles),
    ("feedback stylesheet", "/* Sirati feedback insights V2 */" in styles),
]
for name, ok in checks:
    assert ok, "Feedback V2 invariant failed: " + name

# These are UI-only generated components. No new owner grants or migration.
assert "service_role" not in dashboard and "raw_app_meta_data" not in dashboard
assert "localStorage" not in dashboard + form and "sessionStorage" not in dashboard + form
assert ".insert(" not in dashboard and ".upsert(" not in dashboard
print(f"PASS: {len(checks)} feedback insights and own-review invariants")
