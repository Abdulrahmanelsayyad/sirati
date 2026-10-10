#!/usr/bin/env python3
"""Staging-only, user-triggered cross-account HTTP UPDATE/DELETE RLS QA.

Installs a Next.js route using the existing Supabase browser client and two
disposable records created solely for this test on Sirati-Staging. No Production
endpoints, service_role keys, payments, or actual user CVs are involved.
"""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("Usage: staging_api_write_probe.py SOURCE_ROOT")

root = Path(sys.argv[1]).resolve()
target = root / "app" / "qa-write" / "page.tsx"
if target.exists():
    raise SystemExit("FAIL: refusing to replace existing QA write test page")
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(r"""'use client';

import { useState } from 'react';
import { createClient } from '@/lib/supabase/client';

type Status = 'PASS' | 'FAIL' | 'NOT RUN';
type TestResult = { label: string; status: Status; detail: string };
const STAGING_API = 'https://ykfxcxhozqqsvhtdyxho.supabase.co';
const STAGING_HOST = 'sirati-staging-elsayyad.netlify.app';
const OWN_TITLE = 'SIRATI-QA-OWN-API-UPDATE-20261010';
const FOREIGN_TITLE = 'SIRATI-QA-CROSS-ACCOUNT-UNAUTHORIZED-UPDATE-20261010';

// Two *disposable*, empty staging-only CV rows. Not actual saved customer CVs.
// If an RLS regression allows a forbidden write, ONLY these records are targeted.
const qaFixtures: Record<string, { ownId: string; foreignId: string }> = {
  'd69a2a76-0d1f-4b58-9998-2f4473082bf6': {
    ownId: 'fa6e8ae8-edd3-472d-9f50-2c921cb87487',
    foreignId: 'b2b93a8a-2f10-4cd9-8971-ef95e15dc671',
  },
  'e589f2a0-2123-4fe8-8704-a3fd18ab7ec3': {
    ownId: 'b2b93a8a-2f10-4cd9-8971-ef95e15dc671',
    foreignId: 'fa6e8ae8-edd3-472d-9f50-2c921cb87487',
  },
};

export default function StagingApiWriteQa() {
  const [busy, setBusy] = useState(false);
  const [items, setItems] = useState<TestResult[]>([]);
  const [summary, setSummary] = useState('Not run. Only start this test while signed in as test account A or B.');

  async function run() {
    if (busy) return;
    setBusy(true);
    setItems([]);
    setSummary('Verifying Staging identity, then testing disposable QA rows…');
    const results: TestResult[] = [];
    const add = (label: string, status: Status, detail: string) =>
      results.push({ label, status, detail });
    try {
      if (window.location.hostname !== STAGING_HOST) {
        add('Environment', 'NOT RUN', 'Open the canonical Netlify Staging domain.');
        return;
      }
      const client = createClient();
      if (!client || process.env.NEXT_PUBLIC_SUPABASE_URL !== STAGING_API) {
        add('Environment', 'NOT RUN', 'Supabase client is not configured for Sirati-Staging.');
        return;
      }
      const { data: verified, error: authError } = await client.auth.getUser();
      if (authError || !verified.user) {
        add('Verified session', 'NOT RUN', 'Sign in to a dedicated Staging test account.');
        return;
      }
      const fixture = qaFixtures[verified.user.id];
      if (!fixture) {
        add('Verified session', 'NOT RUN', 'This account is not an approved QA fixture owner.');
        return;
      }
      add('Staging environment and account', 'PASS', 'Verified synthetic account and isolated Staging API.');

      // Require positive and negative read controls before issuing writes.
      const own = await client.from('cv_documents').select('id').eq('id', fixture.ownId).maybeSingle();
      const foreign = await client.from('cv_documents').select('id').eq('id', fixture.foreignId).maybeSingle();
      if (own.error || foreign.error || own.data?.id !== fixture.ownId || foreign.data !== null) {
        add('Disposable fixture preflight', 'NOT RUN',
          'Expected own/foreign read isolation not confirmed; NO write calls were sent.');
        return;
      }
      add('Disposable fixture preflight', 'PASS', 'Own test record accessible, other record hidden.');

      // Positive control: a test account can update its *own disposable* row.
      const ownUpdate = await client.from('cv_documents')
        .update({ title: OWN_TITLE }).eq('id', fixture.ownId).select('id');
      if (ownUpdate.error || (ownUpdate.data || []).length !== 1 ||
          ownUpdate.data?.[0]?.id !== fixture.ownId) {
        add('Live API: own UPDATE', 'NOT RUN',
          'Own disposable update was not confirmed; stopping before cross-account tests.');
        return;
      }
      add('Live API: own UPDATE', 'PASS', 'Owner updated exactly one disposable QA row.');

      // Negative UPDATE: if it unexpectedly modifies a row, mark FAIL and stop.
      const forbiddenUpdate = await client.from('cv_documents')
        .update({ title: FOREIGN_TITLE }).eq('id', fixture.foreignId).select('id');
      if ((forbiddenUpdate.data || []).length > 0) {
        add('Live API: forbidden UPDATE', 'FAIL',
          'RLS regression: another account’s disposable row was modified. Stop testing.');
        return;
      }
      if (forbiddenUpdate.error) {
        add('Live API: forbidden UPDATE', 'NOT RUN',
          'API returned an error; investigate the error class without exposing tokens.');
        return;
      }
      add('Live API: forbidden UPDATE', 'PASS', 'API updated zero foreign-owned rows.');

      // Negative DELETE: only an independently disposable test row is targeted.
      const forbiddenDelete = await client.from('cv_documents')
        .delete().eq('id', fixture.foreignId).select('id');
      if ((forbiddenDelete.data || []).length > 0) {
        add('Live API: forbidden DELETE', 'FAIL',
          'RLS regression: another account’s disposable row was deleted. Stop testing.');
        return;
      }
      if (forbiddenDelete.error) {
        add('Live API: forbidden DELETE', 'NOT RUN',
          'API returned an error; investigate without logging credentials or CV data.');
        return;
      }
      add('Live API: forbidden DELETE', 'PASS', 'API deleted zero foreign-owned rows.');

      const afterOwn = await client.from('cv_documents')
        .select('id').eq('id', fixture.ownId).maybeSingle();
      const afterForeign = await client.from('cv_documents')
        .select('id').eq('id', fixture.foreignId).maybeSingle();
      add('Live API: post-test read isolation',
        !afterOwn.error && !afterForeign.error &&
        afterOwn.data?.id === fixture.ownId && afterForeign.data === null ? 'PASS' : 'NOT RUN',
        'Rechecked own disposable record and foreign-row invisibility.');
    } catch {
      add('Test execution', 'NOT RUN', 'Unexpected test error; verify staging fixtures and logs.');
    } finally {
      setItems(results);
      setSummary(results.some(x => x.status === 'FAIL') ?
        'FAIL — Security defect suspected. Do not use Production.' :
        results.some(x => x.status === 'NOT RUN') ?
          'INCOMPLETE — Some checks need investigation.' :
          'PASS — Authenticated staging API checks passed for this account.');
      setBusy(false);
    }
  }

  return <main style={{ maxWidth: 720, margin: '24px auto 72px', padding: '18px', fontFamily: 'system-ui, sans-serif', color: '#173a2e' }}>
    <meta name="robots" content="noindex,nofollow" />
    <h1 style={{ fontSize: 28, lineHeight: 1.2 }}>Sirati Staging — API Write Security QA</h1>
    <p>Checks actual authenticated UPDATE and DELETE requests against <strong>two disposable, synthetic Staging records</strong>. Only fixture records can be targeted. No customer CVs, secrets or Production database are involved.</p>
    <p><strong>Note:</strong> The positive control updates the current test account’s empty disposable record. Failed RLS may cause a write to another empty disposable record; never to a saved user CV.</p>
    <button type="button" onClick={run} disabled={busy}
      style={{ minHeight: 50, width: '100%', padding: 14, border: 0, borderRadius: 10, color: '#fff', background: '#194d3e', fontSize: 16, fontWeight: 700 }}>
      {busy ? 'Running Staging-only API security check…' : 'Run API UPDATE / DELETE security check'}
    </button>
    <p role="status" aria-live="polite">{summary}</p>
    {items.map((result, index) => <section key={index} style={{ border: '1px solid #d9e2da', borderRadius: 10, background: '#fff', padding: 14, margin: '10px 0' }}>
      <strong>{result.status} — {result.label}</strong>
      <p style={{ margin: '6px 0 0' }}>{result.detail}</p>
    </section>)}
    <p style={{ fontSize: 13, color: '#557165' }}>
      Complete for this account only. Repeat once with the other synthetic account. Independent security and QA sign-off remain separate.
    </p>
    <a href="/qa-privacy/">Return to read-only privacy QA</a>
  </main>;
}
""", encoding="utf-8")
print("PASS: disposable-fixture, account-gated HTTP write RLS probe installed only on Staging.")
