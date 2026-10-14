"""Regression checks for the generated local-first CV document review page."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
GENERATOR = REPO / ".github/scripts/document_import_v1.py"


class DocumentImportTests(unittest.TestCase):
    def test_generated_review_uses_shared_facts_without_uploading(self):
        with tempfile.TemporaryDirectory() as temp:
            subprocess.run([sys.executable, str(GENERATOR), temp], check=True)
            root = Path(temp)
            page = (root / "app/import-documents/page.tsx").read_text(encoding="utf-8")
            extractor = (root / "lib/documentCvExtraction.ts").read_text(encoding="utf-8")
            adapter = (root / "lib/documentCvFileImport.ts").read_text(encoding="utf-8")

            # The same extractor drives the UI and standalone adapter.
            self.assertIn("importTextDocuments(selected)", page)
            self.assertIn("extractDocumentCvFacts(text", adapter)
            for field in ("email", "phone", "education", "date", "url"):
                self.assertIn(field + ":", page)

            # Every fact needs explicit review, and its evidence remains visible.
            self.assertIn("accepted: false", page)
            self.assertIn("disabled={!approved.length || busy}", page)
            self.assertIn("fact.evidence.fileName", page)
            self.assertIn("fact.evidence.snippet", page)
            self.assertIn("aria-label=\"Approved CV facts\"", page)
            self.assertIn("files.length > 10", page)
            self.assertIn("5 * 1024 * 1024", adapter)

            # No server upload, automatic CV write, database, or storage access.
            for file_text in (page, extractor, adapter):
                self.assertNotIn("fetch(", file_text)
                self.assertNotIn("localStorage", file_text)
                self.assertNotIn("sessionStorage", file_text)
                self.assertNotIn("supabase", file_text.lower().replace("no supabase", ""))

            self.assertIn("PDF/DOCX/image import", page)
            self.assertIn('accept=".txt,.md', page)

    def test_generator_does_not_overwrite_existing_library(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / "lib/documentCvExtraction.ts"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text("other existing implementation", encoding="utf-8")
            proc = subprocess.run([sys.executable, str(GENERATOR), temp], capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertEqual(dest.read_text(encoding="utf-8"), "other existing implementation")


if __name__ == "__main__":
    unittest.main()
