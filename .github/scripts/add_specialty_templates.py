"""Add two ATS-friendly Sirati designs without changing saved CV data.

This runs after the existing template, UX and account-isolation patches.
Both variants intentionally reuse the vetted single-column Compact ATS document
structure; they differ in typography and presentation, not in the data model.
"""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1]).resolve()
new_ids = ("healthcare-pro", "executive-ats")

# Keep the same persisted CV schema, extending only the type discriminators.
for rel in ("lib/types.ts", "app/builder/page.tsx", "app/templates/page.tsx", "components/CvPreview.tsx"):
    path = root / rel
    source = path.read_text(encoding="utf-8")
    for quote in ("'", '"'):
        old = f"{quote}modern{quote} | {quote}classic{quote} | {quote}compact{quote} | {quote}compact-ats{quote}"
        extra = "".join(f" | {quote}{value}{quote}" for value in new_ids)
        source = source.replace(old, old + extra) if new_ids[0] not in source else source
    path.write_text(source, encoding="utf-8")

# The selection page keeps a single click-through workflow, adding two choices.
cards_path = root / "app/templates/page.tsx"
cards = cards_path.read_text(encoding="utf-8")
if "id: 'healthcare-pro'" not in cards:
    anchor = re.search(r"(?m)^(?P<indent>\s*)\{ id: 'compact-ats',[^\n]+\n", cards)
    if not anchor:
        raise RuntimeError("Missing Compact ATS card anchor")
    indent = anchor.group("indent")
    additions = (
        indent + "{ id: 'healthcare-pro', name: 'Healthcare Pro', description: 'Clean clinical resume with calm teal headings and clear licensure, experience and training sections.', badge: 'Healthcare' },\n"
        + indent + "{ id: 'executive-ats', name: 'Executive ATS', description: 'Refined navy, centered header and a one-column layout for leadership and business roles.', badge: 'Leadership' },\n"
    )
    cards = cards[:anchor.end()] + additions + cards[anchor.end():]
cards_path.write_text(cards, encoding="utf-8")

# Extend the builder selector and every recognized Compact ATS guard. The latter
# includes both onboarding query parameters and account-scoped draft restore.
builder_path = root / "app/builder/page.tsx"
builder = builder_path.read_text(encoding="utf-8")
if 'value="healthcare-pro"' not in builder:
    anchor = '<option value="compact-ats">Compact ATS</option>'
    if anchor not in builder:
        raise RuntimeError("Missing Compact ATS builder option")
    builder = builder.replace(
        anchor,
        anchor + '\n                <option value="healthcare-pro">Healthcare Pro</option>'
        + '\n                <option value="executive-ats">Executive ATS</option>',
        1,
    )
# Match the precise lhs, preventing changes to unrelated conditionals or text.
guard = re.compile(r"(?P<lhs>[A-Za-z_$][\w.$]*)\s*===\s*'compact-ats'")
def append_new_ids(match):
    lhs = match.group("lhs")
    following = builder[match.end():match.end()+130]
    if f"{lhs} === 'healthcare-pro'" in following:
        return match.group(0)
    return (match.group(0)
        + f" || {lhs} === 'healthcare-pro'"
        + f" || {lhs} === 'executive-ats'")
builder, guards = guard.subn(append_new_ids, builder)
if guards < 1:
    raise RuntimeError("No Compact ATS validation guards found in builder")
builder_path.write_text(builder, encoding="utf-8")

# Share the stable semantic markup: no icons, columns or fabricated CV claims.
# A different class provides a distinct layout and print treatment for each.
preview_path = root / "components/CvPreview.tsx"
preview = preview_path.read_text(encoding="utf-8")
old_if = "if (template === 'compact-ats') {"
new_if = "if (template === 'compact-ats' || template === 'healthcare-pro' || template === 'executive-ats') {"
if old_if in preview:
    preview = preview.replace(old_if, new_if, 1)
elif new_if not in preview:
    raise RuntimeError("Missing Compact ATS preview branch")
old_article = '<article className="cv-sheet template-compact-ats" dir={dir}>'
new_article = "<article className={'cv-sheet template-compact-ats template-' + template} dir={dir}>"
if old_article in preview:
    preview = preview.replace(old_article, new_article, 1)
elif new_article not in preview:
    raise RuntimeError("Missing Compact ATS preview root")
preview_path.write_text(preview, encoding="utf-8")

css_path = root / "app/globals.css"
css = css_path.read_text(encoding="utf-8")
marker = "/* Sirati specialty ATS template variants */"
if marker not in css:
    css += """
/* Sirati specialty ATS template variants: text-first, single-column CVs. */
.template-healthcare-pro {
  padding:35px 42px 38px;
  font-family:Arial, Helvetica, sans-serif;
}
.template-healthcare-pro .compact-ats-head {
  padding-bottom:13px;
  border-bottom:3px solid #0b7285;
}
.template-healthcare-pro .compact-ats-head h1 {
  color:#173b4a;
  font-size:27px;
  letter-spacing:0;
}
.template-healthcare-pro .compact-ats-title { color:#176b79; }
.template-healthcare-pro .compact-ats-section { margin-bottom:14px; }
.template-healthcare-pro .compact-ats-section h2 {
  color:#135d70;
  font-size:11.7px;
  padding-bottom:4px;
  border-bottom:1px solid #b3cbd0;
  letter-spacing:.3px;
}
.template-healthcare-pro .compact-ats-entry-head strong { color:#173b4a; }
.template-healthcare-pro .compact-ats-keywords span:not(:last-child)::after { color:#176b79; }

.template-executive-ats {
  padding:38px 43px 40px;
  font-family:Georgia, 'Times New Roman', serif;
  color:#202938;
}
.template-executive-ats .compact-ats-head {
  text-align:center;
  margin-bottom:19px;
  padding:15px 8px 16px;
  border-top:4px solid #233958;
  border-bottom:1px solid #a8b4c5;
}
.template-executive-ats .compact-ats-head h1 {
  font-size:29px;
  letter-spacing:.4px;
  color:#233958;
}
.template-executive-ats .compact-ats-title {
  font-size:13.3px;
  font-weight:600;
  color:#3c526d;
}
.template-executive-ats .compact-ats-contact { justify-content:center; }
.template-executive-ats .compact-ats-section { margin-bottom:15px; }
.template-executive-ats .compact-ats-section h2 {
  padding-bottom:4px;
  border-bottom:1.5px solid #233958;
  color:#233958;
  font-family:Arial, Helvetica, sans-serif;
  font-size:11.3px;
  letter-spacing:1px;
}
.template-executive-ats .compact-ats-entry-head strong {
  font-size:12.5px;
  color:#233958;
}
@media (max-width: 920px) {
  .template-healthcare-pro, .template-executive-ats { width:100%; min-height:auto; padding:27px 27px 30px; }
}
@media (max-width: 560px) {
  .template-healthcare-pro, .template-executive-ats { padding:20px 16px 24px; }
  .template-executive-ats .compact-ats-head h1 { font-size:23px; }
  .template-healthcare-pro .compact-ats-head h1 { font-size:23px; }
}
@media print {
  .template-healthcare-pro, .template-executive-ats {
    width:210mm; min-height:297mm; padding:11mm 13mm 12mm;
    background:white; border:0; box-shadow:none;
  }
  .template-healthcare-pro .compact-ats-head,
  .template-executive-ats .compact-ats-head {
    margin-bottom:3.4mm; padding-top:0; padding-bottom:2.5mm;
  }
  .template-healthcare-pro .compact-ats-head h1,
  .template-executive-ats .compact-ats-head h1 { font-size:19pt; }
  .template-healthcare-pro .compact-ats-section,
  .template-executive-ats .compact-ats-section { margin-bottom:3.1mm; }
}
"""
    css_path.write_text(css, encoding="utf-8")

print("Applied Healthcare Pro and Executive ATS template variants.")
