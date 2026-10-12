"""Verify actual PDF raster markers, not only computed RTL browser styles."""
from pathlib import Path
import fitz
import re

root = Path('/tmp/sirati-pdf-template-long-candidate')
for width in (360, 390, 1440):
    with fitz.open(root / f'compact-ats-ar-{width}-target5.pdf') as doc:
        page = doc[0]
        rects = page.search_for('BoundaryToken000')
        assert rects, 'Missing first searchable paragraph'
        token = rects[0]
        # Native token height locates the first experience line in the image.
        # The original defect drew native bullets in the leftmost 20pt strip.
        def dark_pixels(rect):
            pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), clip=rect, alpha=False)
            data = pix.samples
            return sum(max(data[i:i+3]) < 130 for i in range(0, len(data), pix.n))
        # Desktop Documents rendering intentionally uses wider sheet margins.
        # Locate the Arabic paragraph's measured right edge, not the page edge.
        spans = [span for block in page.get_text('dict')['blocks']
                 for line in block.get('lines', []) for span in line['spans']
                 if abs(span['bbox'][1] - token.y0) < 1
                 and re.search(r'[\u0600-\u06ff]', span['text'])]
        assert spans, 'Missing first Arabic paragraph bounds'
        text_right = max(span['bbox'][2] for span in spans)
        margin = page.rect.width - text_right
        left = fitz.Rect(0, token.y0, margin, token.y1)
        right = fitz.Rect(text_right + 3, token.y0, text_right + 16, token.y1)
        assert dark_pixels(left) == 0, f'{width}: actual PDF retains far-left RTL bullet'
        assert dark_pixels(right) > 5, f'{width}: right-side raster bullet missing'
        print(f'PASS: actual A4 Arabic Experience raster bullet at right, no far-left marker ({width}px source)')
