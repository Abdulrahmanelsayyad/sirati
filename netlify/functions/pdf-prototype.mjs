// Issue #41: deliberately isolated, synthetic-only server-side PDF proof of concept.
// NOT a paid export endpoint. Never accept, fetch, or render real user CV data here.
const STAGING_URL = 'https://ykfxcxhozqqsvhtdyxho.supabase.co';

const rows = [
  ['JANE SAMPLE', 20, true, 788],
  ['Emergency Nurse | SYNTHETIC DEMO CV', 11, false, 766],
  ['jane.sample@example.invalid | Cairo, Egypt', 10, false, 747],
  ['PROFESSIONAL SUMMARY', 12, true, 714],
  ['Emergency nurse with 5 years of simulated clinical experience.', 10, false, 695],
  ['EXPERIENCE', 12, true, 661],
  ['Emergency Nurse | Fictional General Hospital | 2021 - 2026', 10, true, 642],
  ['- Assisted with triage and emergency department workflows.', 10, false, 624],
  ['- Documented patient assessments and treatment updates.', 10, false, 607],
  ['EDUCATION', 12, true, 573],
  ['BSc Nursing | Sample University | 2020', 10, false, 554],
  ['SKILLS', 12, true, 520],
  ['Triage | BLS | Documentation | Emergency Response', 10, false, 501],
  ['This CV is fictional. No real customer data or payment is used.', 9, false, 64],
];

function pdfString(s) {
  if (!/^[\x20-\x7e]*$/.test(s)) throw new Error('ASCII-only demo fixture');
  return s.replaceAll('\\', '\\\\').replaceAll('(', '\\(').replaceAll(')', '\\)');
}

export function renderSyntheticCompactAtsPdf() {
  const content = rows.map(([str, fontSize, bold, y]) =>
    'BT /' + (bold ? 'F2' : 'F1') + ' ' + fontSize + ' Tf 48 ' + y + ' Td (' + pdfString(str) + ') Tj ET'
  ).join('\n') + '\n';
  const objects = [
    '<< /Type /Catalog /Pages 2 0 R >>',
    '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
    '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.28 841.89] /Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>',
    '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
    '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>',
    '<< /Length ' + Buffer.byteLength(content) + ' >>\nstream\n' + content + 'endstream',
  ];
  let pdf = '%PDF-1.4\n% Synthetic Sirati staging-only proof\n';
  const offsets = [0];
  for (let index = 0; index < objects.length; index++) {
    offsets.push(Buffer.byteLength(pdf));
    pdf += (index + 1) + ' 0 obj\n' + objects[index] + '\nendobj\n';
  }
  const xrefStart = Buffer.byteLength(pdf);
  pdf += 'xref\n0 ' + offsets.length + '\n0000000000 65535 f \n';
  for (const offset of offsets.slice(1)) pdf += String(offset).padStart(10, '0') + ' 00000 n \n';
  pdf += 'trailer\n<< /Size ' + offsets.length + ' /Root 1 0 R >>\nstartxref\n' + xrefStart + '\n%%EOF\n';
  return Buffer.from(pdf, 'ascii');
}

export default async function handler(request) {
  // Default disabled even on Netlify. A mistaken production deployment is inert.
  if (process.env.SIRATI_PDF_POC_ENABLED !== 'true' ||
      process.env.NEXT_PUBLIC_SUPABASE_URL !== STAGING_URL) {
    return new Response(null, { status: 404 });
  }
  if (request.method !== 'POST') return new Response(null, { status: 405 });
  const body = await request.text();
  if (body.length > 32 || body !== '{"synthetic":true}') {
    return new Response('Synthetic test payload only', { status: 400 });
  }
  const pdf = renderSyntheticCompactAtsPdf();
  return new Response(pdf, {
    headers: {
      'Content-Type': 'application/pdf',
      'Content-Disposition': 'attachment; filename="sirati-synthetic-compact-ats.pdf"',
      'Cache-Control': 'no-store',
      'X-Content-Type-Options': 'nosniff',
    },
  });
}
