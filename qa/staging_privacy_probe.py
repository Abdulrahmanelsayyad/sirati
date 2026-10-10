#!/usr/bin/env python3
"""Install an opt-in, read-only privacy probe into the isolated Netlify Staging build.

Never installed in main/GitHub Pages. Uses the current browser's signed-in
Staging session, existing synthetic fixtures and no credentials or CV fields.
"""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("Usage: staging_privacy_probe.py SOURCE_ROOT")

root = Path(sys.argv[1]).resolve()
target = root / "app" / "qa-privacy" / "page.tsx"
if target.exists():
    raise SystemExit("FAIL: refusing to overwrite an existing privacy-check page")
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(r"""'use client';

import { useState } from 'react';
import { createClient } from '@/lib/supabase/client';

type Status = 'PASS' | 'FAIL' | 'NOT RUN';
type Check = { label: string; status: Status; detail: string };

// Disposable test-only fixtures from Sirati-Staging, never Production.
// Only IDs are queried. No names, CV content or credentials are read.
const fixtures: Record<string, { own: string; other: string }> = {
  'd69a2a76-0d1f-4b58-9998-2f4473082bf6': {
    own: 'f67cc81d-467d-4fc2-8341-31ca9de9f338',
    other: 'c7134c69-bfd2-4b74-8846-a5fd9d55099a',
  },
  'e589f2a0-2123-4fe8-8704-a3fd18ab7ec3': {
    own: 'c7134c69-bfd2-4b74-8846-a5fd9d55099a',
    other: 'f67cc81d-467d-4fc2-8341-31ca9de9f338',
  },
};

export default function StagingPrivacyCheckPage() {
  const [busy, setBusy] = useState(false);
  const [checks, setChecks] = useState<Check[]>([]);
  const [message, setMessage] = useState('Ready. The check only runs when you press the button.');

  async function run() {
    if (busy) return;
    setBusy(true);
    setChecks([]);
    setMessage('Checking this browser and the live Staging API...');
    const next: Check[] = [];
    const add = (label: string, status: Status, detail: string) => next.push({ label, status, detail });
    try {
      if (window.location.hostname !== 'sirati-staging-elsayyad.netlify.app') {
        add('Environment isolation', 'NOT RUN', 'Open the canonical Sirati-Staging Netlify URL.');
        setChecks(next);
        return;
      }
      const client = createClient();
      if (!client) {
        add('Staging client available', 'NOT RUN', 'Supabase client configuration is missing.');
        setChecks(next);
        return;
      }
      const { data: authData, error: authError } = await client.auth.getUser();
      const user = authData.user;
      if (authError || !user) {
        add('Verified test session', 'NOT RUN', 'Log in to a dedicated Staging QA account first.');
        setChecks(next);
        return;
      }
      const fixture = fixtures[user.id];
      if (!fixture) {
        add('Verified test session', 'NOT RUN', 'The signed-in account is not one of the two QA fixtures.');
        setChecks(next);
        return;
      }
      add('Verified test session', 'PASS', 'Known synthetic test account is authenticated.');

      // Only inspect draft key names; do not read, log, render or delete CV values.
      // The account-scoped key is removed on successful sign-out.
      try {
        let foreign = 0;
        let legacy = 0;
        const scoped = /^sirati\.cv\.v2\.([0-9a-f-]{36})$/i;
        for (let i = 0; i < window.localStorage.length; i++) {
          const key = window.localStorage.key(i) || '';
          const match = scoped.exec(key);
          if (match && match[1].toLowerCase() !== user.id.toLowerCase()) foreign++;
          if (key === 'sirati.cv.v1' || key === 'sirati.cv.v2') legacy++;
        }
        add('Other-account device drafts', foreign === 0 ? 'PASS' : 'FAIL',
          foreign === 0 ? 'No other-account scoped drafts found in this browser.' :
            'Other-account draft keys still exist in shared browser storage.');
        add('Legacy device drafts', legacy === 0 ? 'PASS' : 'FAIL',
          legacy === 0 ? 'No legacy shared CV drafts found.' :
            'Legacy shared CV draft exists. Treat as a local confidentiality risk.');
      } catch {
        add('Browser local drafts', 'NOT RUN', 'Browser denied access to localStorage.');
      }

      // Requests below use the real signed-in user session and the real
      // PostgREST Data API, NOT an admin connection or a simulated SQL role.
      // Deliberately query only row IDs and perform no writes.
      const ownDoc = await client.from('cv_documents').select('id')
        .eq('id', fixture.own).maybeSingle();
      const otherDoc = await client.from('cv_documents').select('id')
        .eq('id', fixture.other).maybeSingle();
      if (ownDoc.error || otherDoc.error) {
        add('Live API: cross-account document read', 'NOT RUN',
          'API returned an error; this requires investigation before passing.');
      } else {
        add('Live API: own document readable', ownDoc.data?.id === fixture.own ? 'PASS' : 'FAIL',
          ownDoc.data?.id === fixture.own ? 'Owner can read the own test record.' : 'Own test record was not available.');
        add('Live API: other document denied', otherDoc.data === null ? 'PASS' : 'FAIL',
          otherDoc.data === null ? 'Other account document was not disclosed.' : 'Cross-account read returned a record.');
      }
      const ownVersions = await client.from('cv_versions').select('id')
        .eq('document_id', fixture.own).limit(1);
      const otherVersions = await client.from('cv_versions').select('id')
        .eq('document_id', fixture.other).limit(1);
      if (ownVersions.error || otherVersions.error) {
        add('Live API: cross-account CV versions', 'NOT RUN',
          'API returned an error; this requires investigation before passing.');
      } else {
        add('Live API: own CV version readable',
          (ownVersions.data?.length || 0) > 0 ? 'PASS' : 'FAIL',
          (ownVersions.data?.length || 0) > 0 ? 'Own version exists and is accessible.' : 'Own fixture version was not found.');
        add('Live API: other CV versions denied',
          (otherVersions.data?.length || 0) === 0 ? 'PASS' : 'FAIL',
          (otherVersions.data?.length || 0) === 0 ? 'Other account versions were not disclosed.' : 'Foreign CV version was visible.');
      }
    } catch {
      add('Probe completed', 'NOT RUN', 'Unexpected failure; no CVs were changed.');
    } finally {
      setChecks(next);
      setMessage(next.some(x => x.status === 'FAIL') ? 'FAIL: a privacy concern needs review.' :
        next.some(x => x.status === 'NOT RUN') ? 'INCOMPLETE: inspect unrun checks.' :
          'PASS: inspected browser drafts and live API reads for this account.');
      setBusy(false);
    }
  }

  return <main style={{ maxWidth: 710, margin: '25px auto 70px', padding: '16px 20px', fontFamily: 'system-ui, sans-serif', color: '#15372b' }}>
    <meta name="robots" content="noindex,nofollow" />
    <h1 style={{ fontSize: 28 }}>Sirati Staging — Privacy QA</h1>
    <p>Read-only test of existing synthetic accounts A/B. Uses your current Staging login. Does not display passwords, tokens, customer details, CV fields or document IDs.</p>
    <p><strong>No data modifications, payment requests or Production access.</strong></p>
    <button type="button" onClick={run} disabled={busy}
      style={{ minHeight: 48, width: '100%', border: 0, borderRadius: 10, background: '#174b3b', color: '#fff', fontWeight: 700, padding: '12px 20px' }}>
      {busy ? 'Checking…' : 'Run Staging privacy check'}
    </button>
    <p role="status" aria-live="polite">{message}</p>
    {checks.map((x, i) => <section key={i}
      style={{ border: '1px solid #d8e4dd', background: '#fff', borderRadius: 9, padding: 13, margin: '10px 0' }}>
      <strong>{x.status} — {x.label}</strong>
      <p style={{ margin: '7px 0 0' }}>{x.detail}</p>
    </section>)}
    <p style={{ fontSize: 13, color: '#52665f' }}>
      This check tests real authenticated READ operations only. Direct authenticated UPDATE and DELETE requests and independent Security/QA sign-off are separate release gates.
    </p>
    <a href="/documents/" style={{ color: '#174b3b' }}>Back to My Documents</a>
  </main>;
}
""", encoding="utf-8")
print("PASS: Staging-only opt-in, read-only privacy QA page installed.")
