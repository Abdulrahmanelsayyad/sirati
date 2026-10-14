"""Static regression checks for the generated local import page."""
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest

REPO = Path(__file__).resolve().parents[1]
GENERATOR = REPO / ".github/scripts/document_import_v1.py"

class DocumentImportTests(unittest.TestCase):
    def test_generated_page_is_local_and_review_gated(self):
        with tempfile.TemporaryDirectory() as temp:
            subprocess.run([sys.executable, str(GENERATOR), temp], check=True)
            page = (Path(temp) / "app/import-documents/page.tsx").read_text(encoding="utf-8")
            self.assertIn("accept=\".txt,.md", page)
            self.assertIn("accepted:false", page)
            self.assertIn("disabled={!accepted.length}", page)
            self.assertNotIn("fetch(", page)
            self.assertNotIn("localStorage", page)
            self.assertNotIn("supabase", page)
            self.assertIn("PDF/image extraction is not available yet", page)

if __name__ == "__main__":
    unittest.main()
