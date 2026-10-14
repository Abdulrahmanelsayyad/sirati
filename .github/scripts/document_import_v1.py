"""Wire private browser PDF/TXT review into the route and existing Builder."""
from pathlib import Path
import shutil
import sys
import json

root = Path(sys.argv[1]).resolve()
repo = Path(__file__).resolve().parents[2]
for folder, names in (("lib", ("documentCvExtraction.ts", "documentCvFileImport.ts")),
                      ("components", ("DocumentImportReview.tsx",))):
    for name in names:
        dest = root / folder / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        source = repo / folder / name
        if dest.exists() and dest.read_bytes() != source.read_bytes():
            raise RuntimeError(f"Refusing to overwrite existing generated library: {name}")
        shutil.copyfile(source, dest)

# Reuse the already pinned PDF.js package; publish its worker from our own origin.
package = root / "package.json"
if package.exists():
    config = json.loads(package.read_text())
    command = "node scripts/prepare_document_import.cjs"
    prebuild = config.setdefault("scripts", {}).get("prebuild", "")
    if command not in prebuild:
        config["scripts"]["prebuild"] = (prebuild + " && " if prebuild else "") + command
    package.write_text(json.dumps(config, indent=2) + "\n")
    script = root / "scripts/prepare_document_import.cjs"
    script.parent.mkdir(exist_ok=True)
    script.write_text("const fs = require('node:fs'); fs.mkdirSync('public/pdf-import', {recursive:true}); fs.copyFileSync('node_modules/pdfjs-dist/build/pdf.worker.min.mjs', 'public/pdf-import/pdf.worker.min.mjs');\n")

page = root / "app/import-documents/page.tsx"
page.parent.mkdir(parents=True, exist_ok=True)
page.write_text("""'use client';
import DocumentImportReview from '@/components/DocumentImportReview';
import Link from 'next/link';
export default function DocumentImportPage() {
  return <main className="container" style={{maxWidth:800,padding:24}}>
    <DocumentImportReview />
    <p><Link href="/builder">Open CV Builder to import directly into your CV</Link></p>
  </main>;
}
""")
builder = root / "app/builder/page.tsx"
if builder.exists():
    source = builder.read_text()
    marker = '<main className="builder-page wizard-builder-page">'
    if marker not in source:
        raise RuntimeError("Builder import insertion point missing")
    source = source.replace("import CvReadinessCheck", "import DocumentImportReview, { applyReviewedFacts } from '@/components/DocumentImportReview';\nimport CvReadinessCheck", 1)
    source = source.replace(marker, marker + """
      <details className="container no-print" style={{marginTop:16}}>
        <summary style={{cursor:'pointer',padding:12}}>{language === 'ar' ? 'استيراد مستندات إلى سيرتك' : 'Import documents into your CV'}</summary>
        <DocumentImportReview key={(userId || 'guest') + ':' + (documentId || 'new')} language={language}
          onApply={facts => { if (!isSessionBoundaryBlocked()) setData(prev => applyReviewedFacts(prev, facts)); }} />
      </details>""", 1)
    builder.write_text(source)
