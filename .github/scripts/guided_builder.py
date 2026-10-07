from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()

component_path = root / "components" / "BuilderNavigator.tsx"
component_path.parent.mkdir(parents=True, exist_ok=True)
component_path.write_text("'use client';\n\nimport { useEffect, useMemo, useState } from 'react';\n\ntype Step = {\n  title: string;\n  el: HTMLElement;\n};\n\nconst IGNORED = new Set(['preview', 'cv preview', 'معاينة', 'معاينة السيرة الذاتية']);\n\nfunction cleanTitle(value: string) {\n  return value.replace(/\\s+/g, ' ').trim();\n}\n\nexport default function BuilderNavigator() {\n  const [enabled, setEnabled] = useState(false);\n  const [steps, setSteps] = useState<Step[]>([]);\n  const [index, setIndex] = useState(0);\n\n  useEffect(() => {\n    if (typeof window === 'undefined') return;\n    const onBuilder = window.location.pathname.includes('/builder');\n    setEnabled(onBuilder);\n    if (!onBuilder) return;\n\n    const collect = () => {\n      const headings = Array.from(\n        document.querySelectorAll<HTMLElement>('main h2, main h3, .builder h2, .builder h3, form h2, form h3')\n      );\n\n      const seen = new Set<string>();\n      const found: Step[] = [];\n\n      for (const el of headings) {\n        const title = cleanTitle(el.innerText || el.textContent || '');\n        if (!title || title.length > 70) continue;\n        const key = title.toLowerCase();\n        if (IGNORED.has(key) || seen.has(key)) continue;\n\n        const rect = el.getBoundingClientRect();\n        if (rect.width === 0 && rect.height === 0) continue;\n\n        seen.add(key);\n        found.push({ title, el });\n      }\n\n      if (found.length > 1) setSteps(found.slice(0, 14));\n    };\n\n    const timer = window.setTimeout(collect, 700);\n    const observer = new MutationObserver(() => {\n      window.clearTimeout(timer);\n      window.setTimeout(collect, 250);\n    });\n    observer.observe(document.body, { childList: true, subtree: true });\n\n    return () => {\n      window.clearTimeout(timer);\n      observer.disconnect();\n    };\n  }, []);\n\n  useEffect(() => {\n    if (!enabled || steps.length < 2) return;\n\n    const onScroll = () => {\n      let best = 0;\n      let bestDistance = Number.POSITIVE_INFINITY;\n      steps.forEach((step, i) => {\n        const distance = Math.abs(step.el.getBoundingClientRect().top - 150);\n        if (distance < bestDistance) {\n          bestDistance = distance;\n          best = i;\n        }\n      });\n      setIndex(best);\n    };\n\n    onScroll();\n    window.addEventListener('scroll', onScroll, { passive: true });\n    return () => window.removeEventListener('scroll', onScroll);\n  }, [enabled, steps]);\n\n  const progress = useMemo(\n    () => (steps.length ? Math.round(((index + 1) / steps.length) * 100) : 0),\n    [index, steps.length]\n  );\n\n  const go = (nextIndex: number) => {\n    if (!steps.length) return;\n    const bounded = Math.max(0, Math.min(nextIndex, steps.length - 1));\n    setIndex(bounded);\n    steps[bounded].el.scrollIntoView({ behavior: 'smooth', block: 'start' });\n  };\n\n  if (!enabled || steps.length < 2) return null;\n\n  return (\n    <aside className=\"builder-guide\" aria-label=\"CV section navigation\">\n      <div className=\"builder-guide__progress\" aria-hidden=\"true\">\n        <span style={{ width: `${progress}%` }} />\n      </div>\n\n      <div className=\"builder-guide__content\">\n        <button\n          type=\"button\"\n          className=\"builder-guide__nav\"\n          onClick={() => go(index - 1)}\n          disabled={index === 0}\n          aria-label=\"Previous CV section\"\n        >\n          ←\n        </button>\n\n        <label className=\"builder-guide__step\">\n          <small>Step {index + 1} of {steps.length}</small>\n          <select\n            value={index}\n            onChange={(event) => go(Number(event.target.value))}\n            aria-label=\"Choose CV section\"\n          >\n            {steps.map((step, i) => (\n              <option value={i} key={`${step.title}-${i}`}>\n                {step.title}\n              </option>\n            ))}\n          </select>\n        </label>\n\n        <button\n          type=\"button\"\n          className=\"builder-guide__nav builder-guide__next\"\n          onClick={() => go(index + 1)}\n          disabled={index === steps.length - 1}\n          aria-label=\"Next CV section\"\n        >\n          →\n        </button>\n      </div>\n    </aside>\n  );\n}\n", encoding="utf-8")

layout = root / "app" / "layout.tsx"
text = layout.read_text(encoding="utf-8")
imp = "import BuilderNavigator from '@/components/BuilderNavigator';\n"
if imp not in text:
    lines = text.splitlines(True)
    insert_at = 0
    while insert_at < len(lines) and (lines[insert_at].startswith("import ") or not lines[insert_at].strip()):
        insert_at += 1
    lines.insert(insert_at, imp)
    text = "".join(lines)

if "<BuilderNavigator />" not in text:
    if "</body>" not in text:
        raise SystemExit("Could not find </body> in app/layout.tsx")
    text = text.replace("</body>", "        <BuilderNavigator />\n      </body>", 1)
layout.write_text(text, encoding="utf-8")

css_path = root / "app" / "globals.css"
css = css_path.read_text(encoding="utf-8")
marker = "/* Sirati guided CV navigation */"
if marker not in css:
    css += r'''

/* Sirati guided CV navigation */
.builder-guide {
  position: fixed;
  left: 50%;
  bottom: 16px;
  z-index: 90;
  width: min(620px, calc(100vw - 24px));
  transform: translateX(-50%);
  border: 1px solid rgba(15, 23, 42, .12);
  border-radius: 18px;
  background: rgba(255, 255, 255, .97);
  box-shadow: 0 18px 50px rgba(15, 23, 42, .16);
  backdrop-filter: blur(12px);
  overflow: hidden;
}
.builder-guide__progress {
  height: 4px;
  background: rgba(15, 23, 42, .08);
}
.builder-guide__progress span {
  display: block;
  height: 100%;
  background: #111827;
  transition: width .2s ease;
}
.builder-guide__content {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr) 48px;
  gap: 10px;
  align-items: center;
  padding: 10px;
}
.builder-guide__nav {
  min-width: 48px;
  min-height: 48px;
  border: 1px solid rgba(15, 23, 42, .12);
  border-radius: 12px;
  background: #fff;
  font-size: 21px;
  cursor: pointer;
}
.builder-guide__nav:disabled {
  opacity: .35;
  cursor: default;
}
.builder-guide__next {
  background: #111827;
  color: #fff;
}
.builder-guide__step {
  min-width: 0;
}
.builder-guide__step small {
  display: block;
  margin: 0 0 3px 2px;
  font-size: 11px;
  color: #64748b;
}
.builder-guide__step select {
  width: 100%;
  min-height: 42px;
  padding: 0 34px 0 10px;
  border: 1px solid rgba(15, 23, 42, .12);
  border-radius: 11px;
  background: #f8fafc;
  color: #111827;
  font: inherit;
  font-weight: 650;
}
@media (max-width: 760px) {
  body {
    padding-bottom: 92px;
  }
  .builder-guide {
    bottom: 8px;
    width: calc(100vw - 16px);
    border-radius: 16px;
  }
  .builder-guide__content {
    grid-template-columns: 52px minmax(0, 1fr) 52px;
    gap: 8px;
    padding: 8px;
  }
  .builder-guide__nav {
    min-width: 52px;
    min-height: 52px;
  }
}
'''
    css_path.write_text(css, encoding="utf-8")

print("Applied guided CV navigation.")
