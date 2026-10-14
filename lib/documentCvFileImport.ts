import { extractDocumentCvFacts, type ExtractedCvFact } from './documentCvExtraction';

export type DocumentImportResult = {
  fileName: string;
  facts: ExtractedCvFact[];
  warning?: string;
};

/**
 * Zero-cost local text-file adapter. PDF and image adapters must be wired to
 * installed PDF.js / OCR packages after checking the reconstructed app.
 * No network requests or persistent storage.
 */
export async function importTextDocuments(
  files: readonly File[],
): Promise<DocumentImportResult[]> {
  const results: DocumentImportResult[] = [];
  for (const file of files) {
    const name = file.name || 'unnamed';
    if (file.size > 5 * 1024 * 1024) {
      results.push({ fileName: name, facts: [], warning: 'File exceeds 5 MB limit.' });
      continue;
    }
    if (!/\.(txt|md)$/i.test(name) || !['text/plain', 'text/markdown', ''].includes(file.type)) {
      results.push({
        fileName: name,
        facts: [],
        warning: 'This adapter supports TXT and Markdown only. PDF and image support is not yet connected.',
      });
      continue;
    }
    try {
      const text = await file.text();
      results.push({
        fileName: name,
        facts: extractDocumentCvFacts(text.slice(0, 200_000), name),
        warning: text.length > 200_000 ? 'Only the first 200,000 characters were analyzed.' : undefined,
      });
    } catch {
      results.push({ fileName: name, facts: [], warning: 'Could not read this file locally.' });
    }
  }
  return results;
}
