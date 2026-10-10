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
# The independent Experience helper is untouched. The site has not launched:
# all existing browser CV drafts are owner-created QA data, and the owner
# approved their one-time removal before the first real customer.
(root / "components" / "TargetJobTailor.tsx").unlink(missing_ok=True)
cleanup_path = root / "components" / "LegacyJobMatchCleanup.tsx"
cleanup_path.parent.mkdir(parents=True, exist_ok=True)
cleanup_path.write_text("""'use client';

import { useEffect } from 'react';

const LEGACY_PREFIX = 'sirati.jobTailor.v2.';
const QA_CV_PURGE_MARKER = 'sirati.privacy.prelaunch-reset.v1';
function isOldCvDraftKey(key: string) {
  return key === 'sirati.cv.v1' || key === 'sirati.cv.v2' ||
    key.startsWith('sirati.cv.v2.');
}

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
    // One-time prelaunch cleanup; never blanket-clear browser auth/session,
    // onboarding, analytics or other application keys.
    // Do not repeat on later visits: real guests may be editing an unsaved CV.
    try {
      if (window.localStorage.getItem(QA_CV_PURGE_MARKER) !== '1') {
        for (const storage of [window.localStorage, window.sessionStorage]) {
          for (let index = storage.length - 1; index >= 0; index--) {
            const key = storage.key(index);
            if (key && isOldCvDraftKey(key)) storage.removeItem(key);
          }
        }
        window.localStorage.setItem(QA_CV_PURGE_MARKER, '1');
      }
    } catch {
      // If either storage area fails, retry at the next site visit.
      // Never block auth or cloud-saved CVs.
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

# Zero-cost public career tools, separated from the existing CV Builder.
subprocess.run([sys.executable, str(Path(__file__).with_name("free_career_toolkit.py")), str(root)], check=True)

# Discovery UX: show these shipped tools in the signed-in My Documents view.
subprocess.run([sys.executable, str(Path(__file__).with_name("account_career_shortcut.py")), str(root)], check=True)

# Last-mile visual identity applied AFTER the homepage, Career Tools and account dashboard.
subprocess.run([sys.executable, str(Path(__file__).with_name("signature_ui_v3.py")), str(root)], check=True)

# Career Studio brand replaces CV-only visual identity after the existing UI layers.
subprocess.run([sys.executable, str(Path(__file__).with_name("career_studio_brand.py")), str(root)], check=True)

# Full career platform navigation and self-service customer profile after all UI hooks.
subprocess.run([sys.executable, str(Path(__file__).with_name("career_platform_navigation.py")), str(root)], check=True)

# Discoverability improvement for the existing sidebar; no data model changes.
subprocess.run([sys.executable, str(Path(__file__).with_name("sidebar_feature_finder_v2.py")), str(root)], check=True)

# Role-specific, opt-in Smart CV Pro V4: UI-only and facts-first.
subprocess.run([sys.executable, str(Path(__file__).with_name('smart_cv_pro_v4.py')), str(root)], check=True)

# V5 enriches only the generated V4 Summary picker, no auth/backend changes.
subprocess.run([sys.executable, str(Path(__file__).with_name('smart_cv_pro_v5.py')), str(root)], check=True)

# V6 Pro Max: local job fit and pre-insertion editor; never touches persistence.
subprocess.run([sys.executable, str(Path(__file__).with_name('smart_cv_pro_v6.py')), str(root)], check=True)

# Cross-site navigation UX: visible shortcuts, route context and overlay-free mobile menu.
subprocess.run([sys.executable, str(Path(__file__).with_name('sitewide_navigation_ux.py')), str(root)], check=True)

# UX phase 2: manual Builder form/preview navigation and responsive input usability.
subprocess.run([sys.executable, str(Path(__file__).with_name('ux_cv_editor_forms_v2.py')), str(root)], check=True)

# Keep Career Tools text per tab/language during this open session (in memory only).
subprocess.run([sys.executable, str(Path(__file__).with_name('career_draft_preservation_ux.py')), str(root)], check=True)

# Bilingual account menu sign-out: local session only, saved documents untouched.
subprocess.run([sys.executable, str(Path(__file__).with_name('menu_signout.py')), str(root)], check=True)

# V11: remove redundant template header, keep Documents/Tools in existing navigation.
subprocess.run([sys.executable, str(Path(__file__).with_name('compact_template_header_v11.py')), str(root)], check=True)

# V12: remove duplicated Home header; put saved CV workspace ahead of tools.
subprocess.run([sys.executable, str(Path(__file__).with_name('home_documents_v12.py')), str(root)], check=True)

# V13: keep five useful landing sections; reuse templates, free tools and FAQ.
subprocess.run([sys.executable, str(Path(__file__).with_name('minimal_home_v13.py')), str(root)], check=True)

# V14: feature search stays fixed under the sidebar brand while tools scroll.
subprocess.run([sys.executable, str(Path(__file__).with_name('fixed_menu_search_v14.py')), str(root)], check=True)

# Optional privacy-first analytics UI; GitHub Pages does not set NEXT_PUBLIC_ANALYTICS_ENABLED.
# Keep event collection off until owner approves Production migration, privacy notice and QA.
subprocess.run([sys.executable, str(Path(__file__).with_name('analytics_client_dashboard.py')), str(root)], check=True)

# V15: dedicated saved-document routes to existing Smart CV and CV Quality.
subprocess.run([sys.executable, str(Path(__file__).with_name('menu_document_intents_v15.py')), str(root)], check=True)

# V16: direct saved CV and Builder PDF download (no browser print dialog).
subprocess.run([sys.executable, str(Path(__file__).with_name('direct_pdf_download_v16.py')), str(root)], check=True)

# V17: public template previews must never await a remote account lookup.
subprocess.run([sys.executable, str(Path(__file__).with_name('templates_guest_first_v17.py')), str(root)], check=True)

# V18 (#98): guest Builder; sign in/up only when requesting Save PDF.
# Protected Auth/Browse paths stay untouched; PDF engine stays the same.
subprocess.run([sys.executable, str(Path(__file__).with_name('save_pdf_auth_gate_v18.py')), str(root)], check=True)

# V19 (#97): image-faithful PDF with extractable Unicode and line-aware A4 cuts.
# Synthetic QA fixture is available only in CI; no auth or DB changes.
subprocess.run([sys.executable, str(Path(__file__).with_name('pdf_text_layer_v19.py')), str(root)], check=True)
