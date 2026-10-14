/**
 * Local, zero-cost extraction of CV facts from text obtained from documents.
 * No uploads, network requests, persistence, or invented qualifications.
 * PDF/OCR adapters and review UI are separate follow-up integrations.
 */
export type DocumentEvidence = {
  fileName: string;
  snippet: string;
};
export type ExtractedCvFact = {
  field: 'email' | 'phone' | 'education' | 'date' | 'url' | 'name' | 'title' | 'experience' | 'certification';
  value: string;
  evidence: DocumentEvidence;
  requiresReview: true;
};

const EMAIL = /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi;
const PHONE = /(?:\+?\d[\d\s().-]{7,}\d)/g;
const URL = /\bhttps?:\/\/[^\s<>]+/gi;
const DATE = /\b(?:19|20)\d{2}\b/g;
const EDUCATION = /(?:bachelor|master|doctorate|diploma|degree|university|college|بكالوريوس|ماجستير|دكتوراه|دبلوم|جامعة|كلية)/i;

function normalize(value: string): string {
  return value.replace(/\s+/g, ' ').trim();
}
function uniqueMatches(text: string, pattern: RegExp): string[] {
  return [...new Set((text.match(pattern) || []).map(normalize))];
}
export function extractDocumentCvFacts(text: string, fileName: string): ExtractedCvFact[] {
  if (!text || !fileName) return [];
  const lines = text.split(/\r?\n/).map(normalize).filter(Boolean);
  const facts: ExtractedCvFact[] = [];
  const seen = new Set<string>();
  function add(field: ExtractedCvFact['field'], value: string, snippet: string) {
    const key = field + ':' + value.toLowerCase();
    if (seen.has(key)) return;
    seen.add(key);
    facts.push({ field, value, evidence: { fileName, snippet: snippet.slice(0, 240) }, requiresReview: true });
  }
  for (const line of lines) {
    const labeled: [ExtractedCvFact['field'], RegExp][] = [
      ['name', /^(?:full name|name|الاسم|الاسم الكامل)\s*[:：]\s*(.+)$/i],
      ['title', /^(?:professional title|job title|المسمى الوظيفي)\s*[:：]\s*(.+)$/i],
      ['experience', /^(?:experience|work experience|employment|الخبرة|الخبرة العملية)\s*[:：]\s*(.+)$/i],
      ['certification', /^(?:certification|certificate|qualification|الشهادة|شهادة|المؤهل)\s*[:：]\s*(.+)$/i],
    ];
    for (const [field, pattern] of labeled) {
      const match = line.match(pattern);
      if (match) add(field, match[1].slice(0, 500), line);
    }
    for (const value of uniqueMatches(line, EMAIL)) add('email', value, line);
    for (const value of uniqueMatches(line, URL)) add('url', value, line);
    for (const value of uniqueMatches(line, PHONE)) {
      const digits = value.replace(/\D/g, '');
      if (digits.length >= 9 && digits.length <= 15 && !/^\d{4}$/.test(digits)) add('phone', value, line);
    }
    if (EDUCATION.test(line)) add('education', line.slice(0, 180), line);
    for (const value of uniqueMatches(line, DATE)) add('date', value, line);
  }
  return facts;
}
