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


// Issue #41 incremental SERVER-side renderer: exact frozen snapshot input, not the
// mutable browser CV. NOT wired to any HTTP endpoint or approved for customers.
// Safe fail-closed subset: English, Compact ATS, Latin ASCII, text only.
// Arabic RTL, photos and seven other templates require a vetted parity renderer.
export function renderCompactAtsSnapshotPdf(snapshot) {
  if (!snapshot || typeof snapshot !== 'object' ||
      snapshot.snapshot_template !== 'compact-ats' ||
      snapshot.snapshot_language !== 'en' ||
      !snapshot.snapshot_data || Array.isArray(snapshot.snapshot_data) ||
      typeof snapshot.snapshot_data !== 'object') {
    throw new Error('Unsupported or missing immutable PDF snapshot');
  }
  const data = snapshot.snapshot_data;
  if (data.avatar || data.photo || data.photoUrl || data.profileImage ||
      data.image || data.avatarUrl) {
    throw new Error('Cannot silently drop a snapshot portrait');
  }
  function safe(value) {
    if (value == null) return '';
    if (typeof value !== 'string' || value.length > 10000 ||
        /[^\x09\x0a\x0d\x20-\x7e]/.test(value)) {
      throw new Error('Unsupported snapshot text/encoding');
    }
    return value.replace(/\r\n?/g, '\n').replace(/\t/g, ' ').trim();
  }
  const logical = [];
  const add = (value, size = 10, bold = false) => {
    const text = safe(value);
    if (!text) return;
    for (const paragraph of text.split('\n')) {
      let remaining = paragraph.trim();
      if (!remaining) { logical.push({ text: '', size, bold }); continue; }
      while (remaining.length > 0) {
        if (logical.length > 400) throw new Error('Snapshot exceeds renderer limits');
        let cut = Math.min(remaining.length, size >= 17 ? 48 : 93);
        if (cut < remaining.length) {
          const space = remaining.lastIndexOf(' ', cut);
          if (space > 25) cut = space;
        }
        logical.push({ text: remaining.slice(0, cut).trimEnd(), size, bold });
        remaining = remaining.slice(cut).trimStart();
      }
    }
  };
  const heading = text => { logical.push({ text: '', size: 6 }); add(text, 11, true); };
  const fields = (...values) => values.map(safe).filter(Boolean).join(' | ');

  add(data.fullName || '', 19, true);
  add(data.title || '', 12, true);
  add(fields(data.phone, data.email, data.location, data.linkedin), 9);
  if (safe(data.profile)) { heading('PROFESSIONAL SUMMARY'); add(data.profile); }
  const sections = [
    ['PROFESSIONAL EXPERIENCE', 'experience',
      e => [fields(e.role, e.company, e.location, e.period), e.details]],
    ['EDUCATION', 'education',
      e => [fields(e.degree, e.school, e.location, e.period), e.details]],
    ['LICENSURE & CERTIFICATIONS', 'certifications',
      e => [fields(e.name, e.issuer, e.date)]],
    ['ADDITIONAL TRAINING', 'courses',
      e => [fields(e.name, e.provider, e.date)]],
    ['PROJECTS', 'projects',
      e => [fields(e.name, e.organization, e.period), e.details]],
  ];
  for (const [label, key, describe] of sections) {
    const entries = data[key];
    if (entries == null) continue;
    if (!Array.isArray(entries) || entries.length > 100) {
      throw new Error('Unsupported snapshot section');
    }
    if (!entries.length) continue;
    heading(label);
    for (const entry of entries) {
      if (!entry || typeof entry !== 'object' || Array.isArray(entry)) {
        throw new Error('Invalid snapshot entry');
      }
      for (const item of describe(entry)) add(item);
      logical.push({ text: '', size: 5 });
    }
  }
  for (const [label, key] of [['CORE SKILLS', 'skills'], ['LANGUAGES', 'languages']]) {
    if (safe(data[key])) { heading(label); add(data[key]); }
  }
  if (!safe(data.fullName) || logical.length > 400) {
    throw new Error('Incomplete or excessive snapshot');
  }

  const pages = [[]];
  let y = 792;
  for (const line of logical) {
    const step = Math.max(line.size + 4, 12);
    if (y - step < 55) {
      if (pages.length >= 8) throw new Error('PDF exceeds page budget');
      pages.push([]);
      y = 792;
    }
    y -= step;
    if (line.text) {
      const escaped = line.text.replaceAll('\\', '\\\\')
        .replaceAll('(', '\\(').replaceAll(')', '\\)');
      pages.at(-1).push('BT /' + (line.bold ? 'F2' : 'F1') + ' ' +
        line.size + ' Tf 45 ' + y + ' Td (' + escaped + ') Tj ET');
    }
  }
  const objects = [
    '<< /Type /Catalog /Pages 2 0 R >>',
    '<< /Type /Pages /Count ' + pages.length + ' /Kids [' +
      pages.map((_, i) => 5 + i * 2 + ' 0 R').join(' ') + '] >>',
    '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
    '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>',
  ];
  for (let i = 0; i < pages.length; i++) {
    const content = pages[i].join('\n') + '\n';
    objects.push('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595.28 841.89] ' +
      '/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents ' +
      (6 + i * 2) + ' 0 R >>');
    objects.push('<< /Length ' + Buffer.byteLength(content) +
      ' >>\nstream\n' + content + 'endstream');
  }
  let pdf = '%PDF-1.4\n% Sirati Snapshot Compact ATS - branch prototype\n';
  const offsets = [0];
  for (const obj of objects) {
    offsets.push(Buffer.byteLength(pdf));
    pdf += offsets.length - 1 + ' 0 obj\n' + obj + '\nendobj\n';
  }
  const xref = Buffer.byteLength(pdf);
  pdf += 'xref\n0 ' + offsets.length + '\n0000000000 65535 f \n';
  for (const offset of offsets.slice(1)) {
    pdf += String(offset).padStart(10, '0') + ' 00000 n \n';
  }
  pdf += 'trailer\n<< /Size ' + offsets.length +
    ' /Root 1 0 R >>\nstartxref\n' + xref + '\n%%EOF\n';
  return Buffer.from(pdf, 'ascii');
}
