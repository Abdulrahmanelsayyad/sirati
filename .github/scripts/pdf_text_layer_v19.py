"""Issue #97: experimental image-faithful PDF + native searchable Unicode text layer.
The screenshot remains the original CV template; do not advertise this as certified
ATS/PDF-UA. Fail instead of silently sending an image-only file if fonts or
searchable text generation are unavailable. Intended for isolated Staging QA.
"""
from pathlib import Path
import json
import sys
root=Path(sys.argv[1]).resolve()
src=root/'lib/siratiPdfExport.ts'
if not src.is_file():
    raise SystemExit('FAIL #97: original shared PDF exporter was not generated')
previous=src.read_text(encoding='utf-8')
if "Capture the existing CV preview" not in previous or "html2canvas" not in previous:
    raise SystemExit('FAIL #97: expected V16 exporter drift')
src.write_text(r"""'use client';

import html2canvas from 'html2canvas';
import { PDFDocument } from 'pdf-lib';
import fontkit from '@pdf-lib/fontkit';
import { withBasePath } from '@/lib/basePath';

type Word = { value: string; x: number; top: number; bottom: number;
              width: number; size: number; rtl: boolean };
const PDF_WIDTH_PT = 595.2756;
const PDF_HEIGHT_PT = 841.8898;

// Use OFL fonts installed with npm and copied into /public at build time.
// No third-party requests, CV uploads, browser print, or server-side PDF API.
async function fontBytes(url: string): Promise<Uint8Array> {
  const response = await fetch(withBasePath(url), { credentials: 'same-origin' });
  if (!response.ok) throw new Error('A required offline PDF font is unavailable.');
  return new Uint8Array(await response.arrayBuffer());
}

function wordsFromSheet(sheet: HTMLElement, bounds: DOMRect): Word[] {
  const result: Word[] = [];
  const walker = document.createTreeWalker(sheet, NodeFilter.SHOW_TEXT);
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    const parent = node.parentElement;
    if (!parent || !node.textContent) continue;
    if (parent.closest('script,style,noscript,svg,[aria-hidden="true"],[hidden]')) continue;
    const style = window.getComputedStyle(parent);
    if (style.display === 'none' || style.visibility !== 'visible' ||
        Number(style.opacity) === 0) continue;
    const fontSize = Number.parseFloat(style.fontSize) || 12;
    const rtl = style.direction === 'rtl' || parent.closest('[dir="rtl"]') !== null;
    const text = node.textContent;
    const rex = /\S+/gu;
    let match: RegExpExecArray | null;
    while ((match = rex.exec(text))) {
      const range = document.createRange();
      range.setStart(node, match.index);
      range.setEnd(node, match.index + match[0].length);
      const rect = range.getBoundingClientRect();
      range.detach();
      if (!rect.width || !rect.height) continue;
      const top = rect.top - bounds.top;
      const bottom = rect.bottom - bounds.top;
      if (top < -3 || bottom < 0 || top > sheet.scrollHeight + 15) continue;
      result.push({
        value: match[0].normalize('NFC'),
        x: rect.left - bounds.left,
        width: rect.width, top, bottom, size: fontSize, rtl,
      });
    }
  }
  return result;
}

// Find a gap in the actual rendered word line boxes near an A4 boundary.
// A fixed pixel crop can cut through Arabic glyphs, Latin lines or headings.
// If both columns leave no line-safe boundary, fail rather than cut text.
function chooseBreak(start: number, ideal: number, items: Word[]): number {
  const floor = start + (ideal - start) * 0.70;
  for (let offset = 0; offset <= ideal - floor; offset += 2) {
    const candidate = ideal - offset;
    const cutsText = items.some(w => w.top + 1 < candidate && w.bottom - 1 > candidate);
    if (!cutsText) return candidate;
  }
  throw new Error('Cannot split this CV safely across A4 pages. Shorten a long block.');
}

function downloadBlob(blob: Blob, name: string) {
  const safe = (name || 'Sirati-CV')
    .replace(/[^\p{L}\p{N}_. -]/gu, '').trim().slice(0, 80) || 'Sirati-CV';
  const href = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = href;
  a.download = safe + '.pdf';
  a.style.display = 'none';
  document.body.appendChild(a);
  try { a.click(); }
  finally { a.remove(); setTimeout(() => URL.revokeObjectURL(href), 20000); }
}

/** Captures the existing, chosen CV template as image while embedding a
 * searchable, selectable (visually transparent) Unicode text layer.
 *
 * LIMITATION: Hybrid/image-backed PDF, not tagged PDF/UA and not a guarantee
 * of ATS parser reading order. Text extraction and Arabic QA required.
 */
export async function downloadCvSheet(sheet: HTMLElement, name: string): Promise<void> {
  await document.fonts.ready;
  const bounds = sheet.getBoundingClientRect();
  if (bounds.width < 200 || sheet.scrollHeight < 100)
    throw new Error('CV preview is not ready yet.');
  const words = wordsFromSheet(sheet, bounds);
  if (!words.length) throw new Error('CV has no searchable text to export.');
  // Fail before capture if the local Arabic/Latin fonts are missing.
  const [arabicBytes, latinBytes] = await Promise.all([
    fontBytes('/fonts/pdf-naskh-arabic.woff'),
    fontBytes('/fonts/pdf-naskh-latin.woff'),
  ]);
  const doc = await PDFDocument.create();
  doc.registerFontkit(fontkit);
  const [arabicFont, latinFont] = await Promise.all([
    doc.embedFont(arabicBytes, { subset: true }),
    doc.embedFont(latinBytes, { subset: true }),
  ]);
  const arabicChars = new Set(arabicFont.getCharacterSet());
  const latinChars = new Set(latinFont.getCharacterSet());
  const canvas = await html2canvas(sheet, {
    backgroundColor: '#ffffff', scale: 2, useCORS: true,
    allowTaint: false, logging: false, scrollX: 0, scrollY: -window.scrollY,
    windowWidth: Math.max(window.innerWidth, Math.ceil(bounds.width)),
  });
  if (!canvas.width || !canvas.height) throw new Error('Could not render the CV.');
  const pxPerCss = canvas.width / bounds.width;
  const cssHeight = canvas.height / pxPerCss;
  const a4HeightCss = bounds.width * PDF_HEIGHT_PT / PDF_WIDTH_PT;
  const pageCuts: number[] = [0];
  // Keep original 1-page templates fully A4. For longer CVs, trim *only*
  // obvious trailing blank space, never any visible text.
  const lastInk = Math.max(...words.map(w => w.bottom));
  const effectiveHeight = Math.min(cssHeight,
    Math.max(Math.min(a4HeightCss, cssHeight), lastInk + 20));
  let top = 0;
  while (top + a4HeightCss < effectiveHeight - 2) {
    const next = chooseBreak(top, top + a4HeightCss, words);
    if (next - top < a4HeightCss * 0.69)
      throw new Error('Invalid PDF page boundary.');
    pageCuts.push(next);
    top = next;
    if (pageCuts.length > 15) throw new Error('CV is too long for safe PDF export.');
  }
  pageCuts.push(effectiveHeight);

  let embedded = 0;
  for (let pageIndex = 0; pageIndex < pageCuts.length - 1; pageIndex++) {
    const topCss = pageCuts[pageIndex], bottomCss = pageCuts[pageIndex + 1];
    const topPx = Math.max(0, Math.floor(topCss * pxPerCss));
    const bottomPx = Math.min(canvas.height, Math.ceil(bottomCss * pxPerCss));
    if (bottomPx <= topPx) continue;
    const pageCanvas = document.createElement('canvas');
    pageCanvas.width = canvas.width;
    pageCanvas.height = bottomPx - topPx;
    const ctx = pageCanvas.getContext('2d');
    if (!ctx) throw new Error('Cannot render A4 page image.');
    ctx.fillStyle = '#fff';
    ctx.fillRect(0, 0, pageCanvas.width, pageCanvas.height);
    ctx.drawImage(canvas, 0, topPx, canvas.width, pageCanvas.height,
      0, 0, canvas.width, pageCanvas.height);
    const page = doc.addPage([PDF_WIDTH_PT, PDF_HEIGHT_PT]);
    const image = await doc.embedPng(pageCanvas.toDataURL('image/png'));
    const imageHeight = pageCanvas.height / pageCanvas.width * PDF_WIDTH_PT;
    page.drawImage(image, { x: 0, y: PDF_HEIGHT_PT - imageHeight,
      width: PDF_WIDTH_PT, height: imageHeight });
    pageCanvas.width = 0; pageCanvas.height = 0;

    const scalePt = PDF_WIDTH_PT / bounds.width;
    for (const w of words) {
      if (w.top + 0.5 < topCss || w.bottom - 0.5 > bottomCss) continue;
      // Keep each visual word contiguous; mixing left/right scripts inside
      // one token is rare, but unsupported symbols are skipped explicitly.
      const hasArabic = /[\u0600-\u08FF]/u.test(w.value);
      const font = hasArabic ? arabicFont : latinFont;
      const supported = hasArabic ? arabicChars : latinChars;
      const token = [...w.value].filter(ch => supported.has(ch.codePointAt(0)!)).join('');
      if (!token) continue;
      const size = Math.max(5, Math.min(20, w.size * scalePt));
      const x = w.rtl
        ? (w.x + w.width) * scalePt - font.widthOfTextAtSize(token, size)
        : w.x * scalePt;
      const y = PDF_HEIGHT_PT - (w.top - topCss + w.size * 0.84) * scalePt;
      if (y < 0 || y > PDF_HEIGHT_PT || !Number.isFinite(x)) continue;
      page.drawText(token, { x: Math.max(0, x), y, size, font, opacity: 0 });
      embedded++;
    }
  }
  if (embedded < Math.max(3, words.length * 0.55))
    throw new Error('Unicode PDF text coverage was insufficient; export aborted.');
  const bytes = await doc.save({ useObjectStreams: true });
  const blob = new Blob([new Uint8Array(bytes)], { type: 'application/pdf' });
  if (blob.size < 800) throw new Error('Generated PDF is invalid.');
  downloadBlob(blob, name);
}
""", encoding='utf-8')

pkg=root/'package.json'
data=json.loads(pkg.read_text(encoding='utf-8'))
deps=data.setdefault('dependencies',{})
deps['pdf-lib']='1.17.1'
deps['@pdf-lib/fontkit']='1.1.1'
deps['@fontsource/noto-naskh-arabic']='5.3.0'
# Font assets are copied from pinned OFL package LOCALLY before build.
# No network requests are made when exporting a CV in the browser.
copy_script=root/'scripts/prepare_pdf_fonts.cjs'
copy_script.parent.mkdir(parents=True, exist_ok=True)
copy_script.write_text(r"""const { mkdirSync, copyFileSync, existsSync } = require('node:fs');
const { join } = require('node:path');
const root = process.cwd();
const source = join(root, 'node_modules', '@fontsource', 'noto-naskh-arabic', 'files');
const destination = join(root, 'public', 'fonts');
mkdirSync(destination, { recursive: true });
for (const region of ['arabic','latin']) {
  const original = join(source, 'noto-naskh-arabic-' + region + '-400-normal.woff');
  if (!existsSync(original)) throw new Error('Required OFL Arabic PDF font not installed: ' + region);
  copyFileSync(original, join(destination, 'pdf-naskh-' + region + '.woff'));
}
console.log('PASS: self-hosted OFL Arabic and Latin PDF fonts copied');
""",encoding='utf-8')
scripts=data.setdefault('scripts',{})
if scripts.get('prebuild') and scripts.get('prebuild') != 'node scripts/prepare_pdf_fonts.cjs':
    raise SystemExit('FAIL #97: existing prebuild script must be composed manually')
scripts['prebuild']='node scripts/prepare_pdf_fonts.cjs'
pkg.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('PASS: experimental hybrid Unicode PDF exporter generated (issue #97)')
