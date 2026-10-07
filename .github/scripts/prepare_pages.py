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
subprocess.run([sys.executable, str(Path(__file__).with_name('support_section.py')), str(root)], check=True)
subprocess.run([sys.executable, str(Path(__file__).with_name('guided_builder.py')), str(root)], check=True)

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
