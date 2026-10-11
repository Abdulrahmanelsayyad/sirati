"""Verify actual PDF raster markers, not only computed RTL browser styles."""
from pathlib import Path
import fitz

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
        left = fitz.Rect(0, token.y0, 20, token.y1)
        right = fitz.Rect(page.rect.width - 24, token.y0, page.rect.width - 8, token.y1)
        assert dark_pixels(left) == 0, f'{width}: actual PDF retains far-left RTL bullet'
        assert dark_pixels(right) > 5, f'{width}: right-side raster bullet missing'
        print(f'PASS: actual A4 Arabic Experience raster bullet at right, no far-left marker ({width}px source)')
