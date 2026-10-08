"""Keep Sirati's template picker compact and horizontally browsable.

Applied after existing source preparation and all template additions.
No persisted CV fields, auth, payments or PDF rules are changed.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
page = root / "app/templates/page.tsx"
source = page.read_text(encoding="utf-8")

old_import = "import { useEffect, useState } from 'react';"
new_import = "import { useCallback, useEffect, useRef, useState } from 'react';"
if old_import in source:
    source = source.replace(old_import, new_import, 1)
elif new_import not in source:
    raise RuntimeError("Template page React import changed")

old_state = "  const [checking, setChecking] = useState(true);"
new_state = old_state + """
  const carouselRef = useRef<HTMLDivElement>(null);
  const [canScrollPrevious, setCanScrollPrevious] = useState(false);
  const [canScrollNext, setCanScrollNext] = useState(false);

  const syncCarouselNavigation = useCallback(() => {
    const track = carouselRef.current;
    if (!track) return;
    const end = Math.max(0, track.scrollWidth - track.clientWidth);
    setCanScrollPrevious(track.scrollLeft > 3);
    setCanScrollNext(track.scrollLeft < end - 3);
  }, []);

  useEffect(() => {
    if (checking || !carouselRef.current) return;
    const track = carouselRef.current;
    syncCarouselNavigation();
    window.addEventListener('resize', syncCarouselNavigation);
    const observer = typeof ResizeObserver !== 'undefined'
      ? new ResizeObserver(syncCarouselNavigation) : null;
    observer?.observe(track);
    return () => {
      window.removeEventListener('resize', syncCarouselNavigation);
      observer?.disconnect();
    };
  }, [checking, syncCarouselNavigation]);

  function scrollTemplates(direction: -1 | 1) {
    const track = carouselRef.current;
    if (!track) return;
    track.scrollBy({
      left: direction * Math.max(160, Math.round(track.clientWidth * 0.72)),
      behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
    });
  }
"""
if "const carouselRef = useRef" not in source:
    if old_state not in source:
        raise RuntimeError("Template page state anchor not found")
    source = source.replace(old_state, new_state, 1)

old_track = '        <div className="template-flow-grid">'
new_track = """        <div className="template-carousel-toolbar">
          <span className="template-carousel-hint">Swipe or use arrows to browse 6 designs</span>
          <div className="template-carousel-actions" role="group" aria-label="Browse CV templates">
            <button type="button" onClick={() => scrollTemplates(-1)} disabled={!canScrollPrevious} aria-label="Previous templates">←</button>
            <button type="button" onClick={() => scrollTemplates(1)} disabled={!canScrollNext} aria-label="Next templates">→</button>
          </div>
        </div>
        <div
          className="template-flow-grid template-carousel-track"
          ref={carouselRef}
          role="region"
          aria-label="CV template choices"
          tabIndex={0}
          onScroll={syncCarouselNavigation}
        >"""
if 'className="template-flow-grid template-carousel-track"' not in source:
    if old_track not in source:
        raise RuntimeError("Template grid anchor not found")
    source = source.replace(old_track, new_track, 1)
page.write_text(source, encoding="utf-8")

# Override only the selection page, not the resume preview or PDF styles.
css_path = root / "app/globals.css"
css = css_path.read_text(encoding="utf-8")
marker = "/* Compact horizontal template picker */"
if marker not in css:
    css += """
/* Compact horizontal template picker */
.flow-shell .template-carousel-toolbar {
  max-width: 900px; display: flex; align-items: center;
  justify-content: space-between; gap: 12px; margin: 0 0 7px;
}
.flow-shell .template-carousel-hint {
  color: #64748b; font-size: 12px; line-height: 1.4;
}
.flow-shell .template-carousel-actions { display: flex; gap: 7px; flex: none; }
.flow-shell .template-carousel-actions button {
  width: 34px; height: 34px; border: 1px solid #cbd5e1;
  border-radius: 10px; background: #fff; color: #0f172a;
  cursor: pointer; font-size: 18px; line-height: 1;
}
.flow-shell .template-carousel-actions button:hover:not(:disabled) {
  background: #f1f5f9; border-color: #64748b;
}
.flow-shell .template-carousel-actions button:disabled { opacity: .35; cursor: default; }
.flow-shell .template-carousel-actions button:focus-visible,
.flow-shell .template-carousel-track:focus-visible {
  outline: 2px solid #2563eb; outline-offset: 2px;
}
.flow-shell .template-carousel-track {
  display: flex; flex-wrap: nowrap; gap: 12px;
  width: 100%; max-width: 900px; min-width: 0;
  overflow-x: auto; overflow-y: hidden;
  padding: 4px 4px 12px; margin: 0 0 17px;
  scroll-snap-type: x mandatory; scroll-padding-inline: 4px;
  overscroll-behavior-x: contain;
  -webkit-overflow-scrolling: touch; scrollbar-width: thin;
  scrollbar-color: #cbd5e1 transparent;
}
.flow-shell .template-carousel-track .template-choice {
  flex: 0 0 192px; width: 192px; min-width: 192px; max-width: 192px;
  min-height: 0; height: auto; align-self: stretch;
  padding: 10px; display: flex; flex-direction: column;
  text-align: start; scroll-snap-align: start;
}
.flow-shell .template-carousel-track .template-choice-preview {
  width: 100%; height: 112px; min-height: 0; max-height: 112px;
  aspect-ratio: auto; margin: 0 0 9px; padding: 11px 13px;
  box-sizing: border-box; overflow: hidden;
}
.flow-shell .template-carousel-track .template-choice-copy { padding: 0; flex: 1; }
.flow-shell .template-carousel-track .template-choice-copy strong {
  font-size: 13px; line-height: 1.3;
}
.flow-shell .template-carousel-track .template-choice-copy p {
  display: -webkit-box; -webkit-box-orient: vertical;
  -webkit-line-clamp: 2; overflow: hidden;
  font-size: 11px; line-height: 1.4;
  margin: 5px 0 7px;
}
.flow-shell .template-carousel-track .choice-badge { font-size: 9px; }
.flow-shell .template-carousel-track .choice-select { font-size: 11px; }
@media (max-width: 640px) {
  .flow-shell .template-carousel-toolbar { margin-bottom: 5px; }
  .flow-shell .template-carousel-hint { font-size: 11px; }
  .flow-shell .template-carousel-actions button { width: 32px; height: 32px; }
  .flow-shell .template-carousel-track { gap: 9px; margin-bottom: 13px; }
  .flow-shell .template-carousel-track .template-choice {
    flex-basis: 150px; width: 150px; min-width: 150px; max-width: 150px;
    padding: 8px;
  }
  .flow-shell .template-carousel-track .template-choice-preview {
    height: 86px; max-height: 86px; padding: 8px 10px; margin-bottom: 7px;
  }
  .flow-shell .template-carousel-track .template-choice-copy strong { font-size: 12px; }
  .flow-shell .template-carousel-track .template-choice-copy p { font-size: 10px; }
}
@media (prefers-reduced-motion: reduce) {
  .flow-shell .template-carousel-track { scroll-behavior: auto; }
}
"""
    css_path.write_text(css, encoding="utf-8")
print("Applied compact horizontal template carousel.")
