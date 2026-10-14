import { extractDocumentCvFacts, type ExtractedCvFact } from './documentCvExtraction';
import { withBasePath } from './basePath';

export type DocumentImportResult = { fileName: string; facts: ExtractedCvFact[]; warning?: string };
const MAX_TEXT = 200_000;

/** Local PDF text extraction: no document upload, remote worker or paid service. */
async function readPdf(file: File): Promise<{ text: string; warning?: string }> {
  const pdfjs = await import('pdfjs-dist');
  pdfjs.GlobalWorkerOptions.workerSrc = withBasePath('/pdf-import/pdf.worker.min.mjs');
  const task = pdfjs.getDocument({ data: new Uint8Array(await file.arrayBuffer()),
    isEvalSupported: false, useSystemFonts: true, disableFontFace: true });
  let timer: ReturnType<typeof setTimeout> | undefined;
  try {
    return await Promise.race([
      (async () => {
        const pdf = await task.promise;
        if (pdf.numPages > 30) throw new Error('PDF exceeds the 30-page limit. Split the file and try again.');
        let text = '';
        let emptyPages = 0;
        for (let i = 1; i <= pdf.numPages; i++) {
          const page = await pdf.getPage(i);
          const content = await page.getTextContent();
          const line = content.items.map(item => 'str' in item ? item.str + (item.hasEOL ? '\n' : ' ') : '').join('');
          if (!line.trim()) emptyPages++;
          text += line + '\n';
          page.cleanup();
          if (text.length > MAX_TEXT) return { text: text.slice(0, MAX_TEXT), warning: 'Only the first 200,000 characters were analyzed.' };
        }
        return { text, warning: emptyPages ? 'Some pages have no readable text. Scanned pages and images need OCR, which is not supported here. Enter missing facts manually.' : undefined };
      })(),
      new Promise<never>((_, reject) => { timer = setTimeout(() => reject(new Error('PDF reading timed out. Try a smaller file.')), 20000); }),
    ]);
  } finally {
    clearTimeout(timer);
    await task.destroy();
  }
}

export async function importTextDocuments(files: readonly File[]): Promise<DocumentImportResult[]> {
  const results: DocumentImportResult[] = [];
  for (const file of files.slice(0, 10)) {
    const name = file.name || 'unnamed';
    if (file.size > 5 * 1024 * 1024) {
      results.push({ fileName: name, facts: [], warning: 'File exceeds 5 MB limit.' });
      continue;
    }
    const pdf = /\.pdf$/i.test(name) && ['application/pdf', ''].includes(file.type);
    const plain = /\.(txt|md)$/i.test(name) && ['text/plain', 'text/markdown', ''].includes(file.type);
    if (!pdf && !plain) {
      results.push({ fileName: name, facts: [], warning: 'Use a text PDF, TXT or Markdown file. Images and scanned documents need OCR, which is not supported here.' });
      continue;
    }
    try {
      const read = pdf ? await readPdf(file) : { text: await file.text(), warning: undefined };
      results.push({ fileName: name, facts: extractDocumentCvFacts(read.text.slice(0, MAX_TEXT), name),
        warning: read.warning || (read.text.length > MAX_TEXT ? 'Only the first 200,000 characters were analyzed.' : undefined) });
    } catch (error) {
      const message = error instanceof Error ? error.message : '';
      results.push({ fileName: name, facts: [], warning: /^(PDF exceeds|PDF reading timed out)/.test(message) ? message :
        'Could not read this file locally. It may be damaged, password-protected or unsupported. Try an unlocked text PDF or TXT file.' });
    }
  }
  return results;
}
