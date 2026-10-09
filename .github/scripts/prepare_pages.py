from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()

(root / ".env.local").unlink(missing_ok=True)

(root / "next.config.ts").write_text("""import type { NextConfig } from 'next';

const basePath = process.env.NEXT_PUBLIC_BASE_PATH || '';

const nextConfig: NextConfig = {
  output: 'export',
  trailingSlash: true,
  basePath,
};

export default nextConfig;
""", encoding="utf-8")

(root / "lib" / "basePath.ts").write_text("""export const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH || '';

export function withBasePath(path: string): string {
  if (!path || !path.startsWith('/')) return path;
  if (!BASE_PATH) return path;
  if (path === BASE_PATH || path.startsWith(`${BASE_PATH}/`)) return path;
  return `${BASE_PATH}${path}`;
}
""", encoding="utf-8")

def inject_import(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    imp = "import { withBasePath } from '@/lib/basePath';\n"
    if imp in text:
        return text
    lines = text.splitlines(True)
    idx = 0
    if lines and lines[0].strip() in {"'use client';", '"use client";'}:
        idx = 1
        while idx < len(lines) and lines[idx].strip() == "":
            idx += 1
    first_import = next((i for i in range(idx, len(lines)) if lines[i].startswith("import ")), idx)
    lines.insert(first_import, imp)
    return "".join(lines)

def patch(rel: str, replacements):
    path = root / rel
    text = inject_import(path)
    for old, new in replacements:
        if old not in text:
            print(f"WARN: pattern not found in {rel}: {old}")
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")

patch("app/documents/page.tsx", [
    ("window.location.href = '/auth';", "window.location.href = withBasePath('/auth');"),
    ("window.location.href = '/';", "window.location.href = withBasePath('/');"),
])

patch("app/templates/page.tsx", [
    ("window.location.href = '/auth?next=/templates';", "window.location.href = withBasePath('/auth?next=/templates');"),
    ("window.location.href = `/builder?template=${template}&language=${language}`;", "window.location.href = withBasePath(`/builder?template=${template}&language=${language}`);"),
])

patch("components/AccountNav.tsx", [
    ("window.location.href = '/';", "window.location.href = withBasePath('/');"),
])

patch("app/auth/page.tsx", [
    ("if (data.user) window.location.href = next;", "if (data.user) window.location.href = withBasePath(next);"),
    ("window.location.href = nextPath;", "window.location.href = withBasePath(nextPath);"),
    ("const redirectTo = `${window.location.origin}/auth/confirm?next=${encodeURIComponent(nextPath)}`;", "const redirectTo = `${window.location.origin}${withBasePath('/auth/confirm')}?next=${encodeURIComponent(nextPath)}`;"),
])

patch("app/auth/confirm/page.tsx", [
    ("window.location.href = next;", "window.location.href = withBasePath(next);"),
])

patch("app/builder/page.tsx", [
    ("window.location.href = `/auth?next=${encodeURIComponent(window.location.pathname + window.location.search)}`;", "window.location.href = withBasePath(`/auth?next=${encodeURIComponent(window.location.pathname + window.location.search)}`);"),
    ("window.location.href = '/auth';", "window.location.href = withBasePath('/auth');"),
    ("window.history.replaceState({}, '', `/builder?doc=${id}`);", "window.history.replaceState({}, '', withBasePath(`/builder?doc=${id}`));"),
    ("window.history.replaceState({}, '', '/builder');", "window.history.replaceState({}, '', withBasePath('/builder'));"),
    ("onClick={() => window.location.href = '/templates'}", "onClick={() => window.location.href = withBasePath('/templates')}"),
])

(root / "public" / ".nojekyll").write_text("", encoding="utf-8")

import subprocess
subprocess.run([sys.executable, str(Path(__file__).with_name('professional_template.py')), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name('professional_template_v2.py')), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name('compact_ats_template.py')), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name('smart_nursing_library.py')), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name('experience_description_picker.py')), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name('support_section.py')), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name('guided_builder.py')), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name('cv_readiness_check.py')), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name('multi_cv_duplicate.py')), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name('pdf_order_clarity.py')), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name('home_polish.py')), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name('sirati_studio.py')), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name('mobile_builder_fix.py')), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name('account_storage_isolation.py')), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name('add_specialty_templates.py')), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name('compact_template_carousel.py')), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name("real_template_previews.py")), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name("profile_sidebar_template.py")), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name("profile_sidebar_polish.py")), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name("gold_sidebar_template.py")), str(root)], check=True)

subprocess.run([sys.executable, str(Path(__file__).with_name("cv_quality_preview_anchor.py")), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name("manual_navigation_scroll.py")), str(root)], check=True)

print("Prepared Sirati for GitHub Pages.")


# createClient() is nullable by design, but every Builder call is guarded first.
# Non-null assertions keep that runtime guard while satisfying strict TypeScript
# across async callbacks where control-flow narrowing is not retained.
builder_path = root / "app/builder/page.tsx"
builder_text = builder_path.read_text(encoding="utf-8")
builder_text = builder_text.replace("await supabase.auth", "await supabase!.auth")
builder_text = builder_text.replace("await supabase\n        .from", "await supabase!\n        .from")
builder_text = builder_text.replace("await supabase\n      .from", "await supabase!\n      .from")
builder_path.write_text(builder_text, encoding="utf-8")

# Job Match Center has been retired. Remove any inherited generated artifact,
# and clear only its legacy browser-local storage after the new site loads.
# CV drafts, account data, and the independent Experience helper are untouched.
(root / "components" / "TargetJobTailor.tsx").unlink(missing_ok=True)
cleanup_path = root / "components" / "LegacyJobMatchCleanup.tsx"
cleanup_path.parent.mkdir(parents=True, exist_ok=True)
cleanup_path.write_text("""'use client';

import { useEffect } from 'react';

const LEGACY_PREFIX = 'sirati.jobTailor.v2.';

export default function LegacyJobMatchCleanup() {
  useEffect(() => {
    // Storage may be disabled; the rest of the Builder must continue working.
    for (const storage of [window.localStorage, window.sessionStorage]) {
      try {
        for (let index = storage.length - 1; index >= 0; index--) {
          const key = storage.key(index);
          if (key?.startsWith(LEGACY_PREFIX)) storage.removeItem(key);
        }
      } catch {
        // Storage is unavailable in this browser context.
      }
    }
  }, []);
  return null;
}
""", encoding="utf-8")

layout_path = root / "app" / "layout.tsx"
layout_text = layout_path.read_text(encoding="utf-8")
layout_text = layout_text.replace("import TargetJobTailor from '@/components/TargetJobTailor';\n", "")
layout_text = layout_text.replace("        <TargetJobTailor />\n", "")
cleanup_import = "import LegacyJobMatchCleanup from '@/components/LegacyJobMatchCleanup';\n"
if cleanup_import not in layout_text:
    layout_text = cleanup_import + layout_text
if "<LegacyJobMatchCleanup />" not in layout_text:
    if "</body>" not in layout_text:
        raise RuntimeError("Could not install legacy Job Match storage cleanup")
    layout_text = layout_text.replace("</body>", "        <LegacyJobMatchCleanup />\n      </body>", 1)
layout_path.write_text(layout_text, encoding="utf-8")

# Apply contextual descriptions after the existing Builder/Experience generators.
subprocess.run([sys.executable, str(Path(__file__).with_name("career_description_upgrade.py")), str(root)], check=True)

# Add opt-in role-based Personal Summary templates after the description helper.
subprocess.run([sys.executable, str(Path(__file__).with_name("personal_summary_picker.py")), str(root)], check=True)

# Polish the builder navigation without changing save/auth/payment behavior.
subprocess.run([sys.executable, str(Path(__file__).with_name("builder_toolbar_upgrade.py")), str(root)], check=True)

# Keep visual upgrades last: override inherited design styles, never business logic.
subprocess.run([sys.executable, str(Path(__file__).with_name("premium_minimal_v1.py")), str(root)], check=True)

# Opt-in template gallery after all base builders, previews and visual overrides.
subprocess.run([sys.executable, str(Path(__file__).with_name("template_library_v1.py")), str(root)], check=True)
# One genuinely new document structure, built after the 32-style template library.
subprocess.run([sys.executable, str(Path(__file__).with_name("executive_letterhead_template.py")), str(root)], check=True)

# Add opt-in role-based skill and achievement prompts; reuse existing Experience Pro for duties.
subprocess.run([sys.executable, str(Path(__file__).with_name("smart_content_suggestions.py")), str(root)], check=True)

# Owner-approved all-free offering: applied after every Builder and homepage patch.
# Does not alter legacy payment data, RLS, auth, or historic entitlement records.
subprocess.run([sys.executable, str(Path(__file__).with_name("free_access_v1.py")), str(root)], check=True)
