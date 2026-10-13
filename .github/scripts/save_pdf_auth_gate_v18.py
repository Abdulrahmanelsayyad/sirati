"""Issue #98: finish the CV as a guest and ask for a free account only at Save PDF.
Applied after all other site generators; never changes Supabase, export engine,
payment logic, templates, or authenticated document access.
"""
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve()
builder_path=root/'app/builder/page.tsx'
button_path=root/'components/SiratiBuilderPdfButton.tsx'
css_path=root/'app/globals.css'
source=builder_path.read_text(encoding='utf-8')

# Synchronize an existing short-lived guest CV snapshot only after account
# resolution and CV hydration, preventing an empty first render from wiping it.
ready_ref='  const cloudReadyRef = useRef(false);'
if source.count(ready_ref)!=1:
    raise SystemExit('Builder cloud readiness anchor missing')
source=source.replace(ready_ref, ready_ref + '\n  const [emailReturnMissing, setEmailReturnMissing] = useState(false);\n  const [guestRestoreReady, setGuestRestoreReady] = useState(false);', 1)
configured_anchor='''    if (!isSupabaseConfigured()) {
      cloudReadyRef.current = true;
      return;
    }'''
if source.count(configured_anchor)!=1:
    raise SystemExit('Builder nonconfigured guest readiness anchor missing')
source=source.replace(configured_anchor,'''    if (!isSupabaseConfigured()) {
      cloudReadyRef.current = true;
      // The public Builder also works in local QA/offline configuration.
      // Restore a short-lived guest snapshot before enabling auto-updates.
      if (!newCvRequestedRef.current &&
          !new URLSearchParams(window.location.search).has('doc')) {
        try {
          const raw = window.sessionStorage.getItem('sirati.guest.pdf.pending.v1');
          const pending = raw ? JSON.parse(raw) : null;
          if (pending?.version === 1 && Number.isFinite(pending.createdAt) &&
              Date.now() - pending.createdAt >= 0 &&
              Date.now() - pending.createdAt < 30 * 60 * 1000 &&
              pending.data && typeof pending.data === 'object') {
            setData(normalizeCv(pending.data));
            if (typeof pending.template === 'string') {
              setTemplate(pending.template as TemplateName);
            }
            setLanguage(pending.language === 'ar' ? 'ar' : 'en');
          }
        } catch { /* Storage access must not prevent offline editing. */ }
      }
      setGuestRestoreReady(true);
      return;
    }''',1)

# Only direct account-owned ?doc links require early authentication.
start=source.find("      if (!user) {\n        cloudReadyRef.current = true;\n")
end=source.find("\n      const requestedDocumentId = ",start)
if start < 0 or end < 0:
    raise SystemExit('Guest-only Builder auth redirect source changed')
source=source[:start]+"""      if (!user) {
        cloudReadyRef.current = true;
        if (new URLSearchParams(window.location.search).has('doc')) {
          window.location.href = withBasePath('/auth?next=' +
            encodeURIComponent(window.location.pathname + window.location.search));
          return;
        }
        setCloudStatus('Guest mode · Create a free account only at Save PDF');
        setGuestRestoreReady(true);
        return;
      }
""" + source[end:]

# Restore an expiring tab-only guest snapshot only for the same guest, or for
# the confirmed email used to create it. Never open it on someone else's account,
# never overwrite a saved ?doc=, and never write guest CV to a server automatically.
anchor="      setUserId(user?.id ?? null);\n      setUserEmail(user?.email ?? null);\n"
if source.count(anchor)!=1:
    raise SystemExit('Builder account identity anchor changed')
source=source.replace(anchor,anchor+"""      let guestTransferRestored = false;
      const guestDocRequested = new URLSearchParams(window.location.search).has('doc');
      if (!guestDocRequested && !newCvRequestedRef.current) {
        try {
          const raw = window.sessionStorage.getItem('sirati.guest.pdf.pending.v1');
          const pending = raw ? JSON.parse(raw) : null;
          const emailOK = !user || (pending?.requested === true &&
            typeof pending?.email === 'string' &&
            pending.email.toLowerCase() === user.email?.toLowerCase());
          if (pending?.version === 1 && typeof pending.createdAt === 'number' &&
              Date.now() - pending.createdAt >= 0 &&
              Date.now() - pending.createdAt < 30 * 60 * 1000 && emailOK &&
              pending.data && typeof pending.data === 'object') {
            guestTransferRestored = Boolean(user);
            setData(normalizeCv(pending.data));
            if (typeof pending.template === 'string') {
              setTemplate(pending.template as TemplateName);
            }
            setLanguage(pending.language === 'ar' ? 'ar' : 'en');
          } else if (pending && Date.now() - pending.createdAt >= 30 * 60 * 1000) {
            window.sessionStorage.removeItem('sirati.guest.pdf.pending.v1');
          }
        } catch { /* The existing editor remains usable without device storage. */ }
      }
      setEmailReturnMissing(Boolean(user) && !guestTransferRestored &&
        new URLSearchParams(window.location.search).has('resume_pdf'));
""",1)

# Existing Builder PDF button must receive the current editable data and
# hydration/verified-session state without reading or overwriting cloud data.
old="<SiratiBuilderPdfButton language={language} />"
new="""<SiratiBuilderPdfButton language={language} data={data} template={template}
      hydrated={hydrated} userId={userId}
      onAuthenticated={(id, email) => { setUserId(id); setUserEmail(email); }} />"""
if source.count(old)!=1:
    raise SystemExit('Builder PDF CTA anchor changed')
source=source.replace(old,new,1)
# An authenticated user may already have a separate tab draft. The verified
# just-confirmed guest transfer must win only for this explicit Save PDF action,
# without overwriting their cloud documents.
draft_anchor="""        if (!newCvRequestedRef.current) {
          try { raw = window.sessionStorage.getItem(accountDraftStorageKey(user.id)); }"""
draft_replacement="""        if (!newCvRequestedRef.current && !guestTransferRestored) {
          try { raw = window.sessionStorage.getItem(accountDraftStorageKey(user.id)); }"""
if source.count(draft_anchor)!=1:
    raise SystemExit('Signed-in tab draft precedence anchor changed')
source=source.replace(draft_anchor,draft_replacement,1)
# The Builder stays mounted on every CV step, unlike the final-step PDF button.
# Synchronize the existing snapshot after user input, but only AFTER guest
# restoration is complete. Do not create new persistent/localStorage guest data.
effect_anchor="""  const [guestRestoreReady, setGuestRestoreReady] = useState(false);"""
if source.count(effect_anchor)!=1:
    raise SystemExit('Builder guest-ready state not found')
effect=r'''
  useEffect(() => {
    if (!hydrated || !guestRestoreReady || userId) return;
    try {
      const key = 'sirati.guest.pdf.pending.v1';
      const raw = window.sessionStorage.getItem(key);
      if (!raw) return;
      const pending = JSON.parse(raw);
      if (pending?.version !== 1 || !Number.isFinite(pending.createdAt) ||
          Date.now() - pending.createdAt < 0 ||
          Date.now() - pending.createdAt >= 30 * 60 * 1000) return;
      const updated = JSON.stringify({...pending, data, template, language});
      if (updated.length > 1800000) throw new Error('Guest CV snapshot is too large.');
      window.sessionStorage.setItem(key, updated);
    } catch {
      setCloudStatus(language === 'ar'
        ? 'لا يمكن حفظ آخر تعديل مؤقتًا. اترك هذا التبويب مفتوحًا.'
        : 'Latest guest edit could not be kept temporarily. Keep this tab open.');
    }
  }, [hydrated, guestRestoreReady, userId, data, template, language]);
'''
source=source.replace(effect_anchor, effect_anchor+'\n'+effect,1)
# Keep every Save CV entry point in the mounted editor, reusing the auth dialog.
source=source.replace(ready_ref, ready_ref + "\n  const [saveAuthRequest, setSaveAuthRequest] = useState(0);\n  const saveVersionRequested = useRef(true);", 1)
old_save="""    if (!activeUserId) {
      window.location.href = withBasePath('/auth');
      return null;
    }"""
if source.count(old_save)!=1:
    raise SystemExit('Guest Save CV redirect anchor changed')
source=source.replace(old_save,"""    if (!activeUserId) {
      saveVersionRequested.current = createVersion;
      setSaveAuthRequest(request => request + 1);
      return null;
    }""",1)
source=source.replace('<main className="builder-page wizard-builder-page">',
    '''<main className="builder-page wizard-builder-page">
      {emailReturnMissing && <aside className="container" role="alert">
        <p dir="rtl">لو سيرتك مش ظاهرة بعد تأكيد البريد، ارجع لتبويب المحرر الأصلي وسجّل الدخول هناك لإكمال الحفظ. المسودة المؤقتة لا تنتقل بين التبويبات.</p>
        <p>If your CV is missing after email confirmation, return to the original editor tab and sign in there to finish saving. Temporary drafts do not transfer between tabs.</p>
      </aside>}
      <SiratiBuilderPdfButton language={language} data={data} template={template}
        hydrated={hydrated} userId={userId} saveRequest={saveAuthRequest}
        onSave={() => saveToAccount(saveVersionRequested.current)}
        onAuthenticated={(id, email) => { setUserId(id); setUserEmail(email); }} />''',1)
# Serialize all explicit save entry points before any asynchronous auth/network work.
source=source.replace(ready_ref, ready_ref + '\n  const saveInFlight = useRef(false);', 1)
save_start='  async function saveToAccount(createVersion = true) {'
save_end='    return id;\n  }\n\n  function restoreVersion('
if source.count(save_start)!=1 or source.count(save_end)!=1:
    raise SystemExit('Save concurrency anchors changed')
source=source.replace(save_start, save_start + """
    if (saveInFlight.current) return null;
    saveInFlight.current = true;
    try {""",1)
source=source.replace(save_end,"""    return id;
    } catch {
      if (!isSessionBoundaryBlocked()) setCloudStatus(language === 'ar'
        ? 'تعذّر الحفظ. بياناتك ما زالت في المحرر؛ حاول مجددًا.'
        : 'Save failed. Your CV is still in the editor; retry Save.');
      return null;
    } finally {
      saveInFlight.current = false;
    }
  }

  function restoreVersion(""",1)
builder_path.write_text(source,encoding='utf-8')

# Keep the original PDF generator unchanged. Password auth stays on the page;
# the CV remains mounted during sign-in. For email confirmation, the same-tab
# session snapshot can resume after redirect; never transmit CV content in URLs.
button_path.write_text(r"""'use client';

import { useEffect, useId, useRef, useState, type FormEvent } from 'react';
import { isSessionBoundaryBlocked } from '@/lib/sessionBoundary';
import { createClient } from '@/lib/supabase/client';
import { withBasePath } from '@/lib/basePath';
import { downloadCvSheet } from '@/lib/siratiPdfExport';
import type { CvData, TemplateName } from '@/lib/types';

const PENDING_KEY = 'sirati.guest.pdf.pending.v1';
const MAX_AGE = 30 * 60 * 1000;
type Transfer = {
  version: 1; createdAt: number; email: string | null; requested: boolean; action?: 'pdf' | 'save';
  data: CvData; template: TemplateName; language: string;
};
function readTransfer(): Transfer | null {
  try {
    const raw = window.sessionStorage.getItem(PENDING_KEY);
    if (!raw) return null;
    const item = JSON.parse(raw) as Transfer;
    if (item.version !== 1 || !item.data || typeof item.data !== 'object' ||
        !Number.isFinite(item.createdAt) ||
        Date.now() - item.createdAt < 0 || Date.now() - item.createdAt > MAX_AGE) {
      window.sessionStorage.removeItem(PENDING_KEY);
      return null;
    }
    return item;
  } catch { return null; }
}
function storeTransfer(value: Transfer) {
  // Explicitly bounded session-only storage, never URL/localStorage/analytics.
  const serialized = JSON.stringify(value);
  if (serialized.length > 1800000) {
    throw new Error('This CV is too large to keep during email confirmation. Remove large images or save the CV to your account first.');
  }
  window.sessionStorage.setItem(PENDING_KEY, serialized);
}
// Show owners actionable bilingual PDF feedback without leaking browser
// exceptions or changing Supabase authentication and cloud save behavior.
function pdfExportFeedback(error: unknown, arabic: boolean): string {
  const detail = error instanceof Error ? error.message : '';
  if (detail.includes('Mixed-script PDF text cannot be exported safely'))
    return arabic
      ? 'تعذّر تصدير نص مختلط بالعربية والإنجليزية داخل كلمة واحدة. افصل الاختصارات والرموز إلى كلمات مستقلة ثم أعد التنزيل.'
      : 'Some joined Arabic/English text cannot be exported safely. Separate abbreviations and punctuation into distinct words, then retry.';
  if (detail === 'CV preview is not available.')
    return arabic
      ? 'معاينة السيرة غير متاحة حاليًا. افتح المعاينة وأعد المحاولة.'
      : 'CV preview is unavailable. Open the preview and retry.';
  return arabic
    ? 'تعذّر إعداد ملف PDF. راجع المعاينة وحاول مجددًا. بيانات سيرتك ما زالت في المحرر.'
    : 'Could not prepare the PDF. Check the preview and retry. Your CV remains in the editor.';
}
// Detect only a joined Arabic/Latin token before requesting an account or PDF.
// All checks stay in the local editor; never mutate, upload, or log CV values.
function pdfJoinedScriptWarning(data: CvData, arabic: boolean): string | null {
  const joined = /[\u0600-\u08FF]+[A-Za-z]+(?:[/-][A-Za-z]+)*|[A-Za-z]+[\u0600-\u08FF]+/u;
  function firstToken(value: unknown, depth = 0): string | null {
    if (depth > 5) return null;
    if (typeof value === 'string') return value.match(joined)?.[0] || null;
    if (Array.isArray(value)) {
      for (const item of value) {
        const found = firstToken(item, depth + 1);
        if (found) return found;
      }
    } else if (value && typeof value === 'object') {
      for (const [key, item] of Object.entries(value)) {
        // Photo/base64 and URLs are not human CV prose.
        if (/photo|image|url|href/i.test(key)) continue;
        const found = firstToken(item, depth + 1);
        if (found) return found;
      }
    }
    return null;
  }
  const token = firstToken(data);
  if (!token) return null;
  const example = token
    .replace(/([\u0600-\u08FF])([A-Za-z])/u, '$1 $2')
    .replace(/([A-Za-z])([\u0600-\u08FF])/u, '$1 $2');
  return arabic
    ? 'قبل تنزيل PDF، افصل الحروف العربية والإنجليزية في «' + token +
      '». مثال: «' + example + '». بيانات سيرتك لم تتغير.'
    : 'Before downloading PDF, separate Arabic and English in "' + token +
      '". Try "' + example + '". Your CV is unchanged.';
}

class PdfRenderFailure extends Error {}

type Props = {
  language: string; data: CvData; template: TemplateName; hydrated: boolean;
  userId: string | null;
  saveRequest?: number;
  onSave?: () => Promise<string | null>;
  onAuthenticated: (id: string, email: string | null) => void;
};
export default function SiratiBuilderPdfButton(props: Props) {
  const {language, data, template, hydrated, userId, onAuthenticated} = props;
  const [busy,setBusy] = useState(false);
  const [open,setOpen] = useState(false);
  const [mode,setMode] = useState<'signin'|'signup'>('signup');
  const [email,setEmail] = useState('');
  const [password,setPassword] = useState('');
  const [error,setError] = useState('');
  const [notice,setNotice] = useState('');
  const active = useRef(false);
  const autoResumed = useRef(false);
  const trigger = useRef<HTMLButtonElement>(null);
  const firstField = useRef<HTMLInputElement>(null);
  const dialogRef = useRef<HTMLElement>(null);
  const saving = props.saveRequest !== undefined;
  const action = saving ? 'save' : 'pdf';
  const dialogId = useId();
  const returnFocus = useRef<HTMLElement | null>(null);
  const arabic = language === 'ar';

  useEffect(() => {
    if (!open) return;
    firstField.current?.focus();
    const escape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !busy) { e.preventDefault(); cancel(); }
      if (e.key === 'Tab') {
        const choices = dialogRef.current?.querySelectorAll<HTMLElement>(
          'button:not([disabled]), input:not([disabled])');
        if (!choices?.length) return;
        const first = choices[0], last = choices[choices.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault(); last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault(); first.focus();
        }
      }
    };
    window.addEventListener('keydown', escape);
    return () => window.removeEventListener('keydown', escape);
  }, [open,busy]);

  // Open the shared gate only in response to an explicit Save CV request.
  useEffect(() => {
    if (props.saveRequest) void begin();
  }, [props.saveRequest]);

  async function exportCurrentSheet() {
    if (isSessionBoundaryBlocked()) throw new Error('Session changed. Reopen your CV.');
    if (saving) {
      const id = await props.onSave?.();
      if (!id) throw new Error(arabic ? 'تعذّر الحفظ. بياناتك ما زالت في المحرر؛ حاول مجددًا.' : 'Save failed. Your CV is still in the editor; please retry.');
      try { window.sessionStorage.removeItem(PENDING_KEY); } catch {}
      return;
    }
    const sheet = document.querySelector<HTMLElement>(
      '.wizard-preview-wrap .preview-stage > .cv-sheet'
    );
    if (!sheet) throw new Error('CV preview is not available.');
    await new Promise<void>(resolve => requestAnimationFrame(() =>
      requestAnimationFrame(() => resolve())));
    const name = sheet.querySelector('h1')?.textContent?.trim() || 'Sirati-CV';
    await downloadCvSheet(sheet,name);
    try { window.sessionStorage.removeItem(PENDING_KEY); } catch {}
  }

  async function exportWithFeedback() {
    try {
      if (!saving) {
        const warning = pdfJoinedScriptWarning(data, arabic);
        if (warning) throw new PdfRenderFailure(warning);
      }
      await exportCurrentSheet();
    }
    catch (e: unknown) {
      // Saving a cloud CV and authenticating retain their existing error paths.
      if (saving || e instanceof PdfRenderFailure) throw e;
      throw new PdfRenderFailure(pdfExportFeedback(e, arabic));
    }
  }

  async function begin() {
    if (active.current || isSessionBoundaryBlocked()) return;
    // Guest users should see the actionable fix before signing up or
    // sharing an email address, while Save CV stays fully available.
    if (!saving) {
      const warning = pdfJoinedScriptWarning(data, arabic);
      if (warning) { setError(warning); return; }
    }
    active.current = true;
    returnFocus.current = document.activeElement as HTMLElement;
    setBusy(true); setError(''); setNotice('');
    try {
      if (!hydrated) throw new Error('CV is still loading. Try again.');
      const client = createClient();
      const result = client ? await client.auth.getUser() : null;
      if (isSessionBoundaryBlocked()) return;
      if (result && !result.error && result.data.user) {
        onAuthenticated(result.data.user.id, result.data.user.email || null);
        await exportWithFeedback();
        return;
      }
      // Preserve exact editable CV, language, template and photo data in this tab.
      storeTransfer({version:1,createdAt:Date.now(),email:null,requested:true,action,
        data,template,language});
      setOpen(true);
    } catch(e: unknown) {
      setError(e instanceof Error ? e.message : 'Cannot prepare your PDF.');
    } finally { setBusy(false); active.current=false; }
  }

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (active.current || isSessionBoundaryBlocked()) return;
    active.current=true; setBusy(true); setError(''); setNotice('');
    try {
      if (password.length < 8) throw new Error('Use a password of at least 8 characters.');
      const client=createClient();
      if (!client) throw new Error('Account service unavailable.');
      const transfer=readTransfer();
      if (!transfer) throw new Error('Guest draft expired. Your CV is still in the editor; click Save again.');
      const expectedEmail=email.trim().toLowerCase();
      if (!expectedEmail) throw new Error('Enter your email.');
      storeTransfer({...transfer,email:expectedEmail,requested:true,action});
      if (mode==='signin') {
        const {error:signinError}=await client.auth.signInWithPassword({
          email:expectedEmail,password
        });
        if (signinError) throw signinError;
        const {data:auth,error:userError}=await client.auth.getUser();
        if (isSessionBoundaryBlocked() || userError || !auth.user || auth.user.email?.toLowerCase()!==expectedEmail)
          throw new Error('Account verification failed. Try signing in again.');
        onAuthenticated(auth.user.id,auth.user.email||null);
        await exportWithFeedback();
        setOpen(false); setPassword('');
      } else {
        const next=withBasePath('/builder?resume_pdf=1');
        const redirectTo=window.location.origin +
          withBasePath('/auth/confirm') + '?next=' + encodeURIComponent(next);
        const {data:created,error:signupError}=await client.auth.signUp({
          email:expectedEmail,password,
          options:{emailRedirectTo:redirectTo}
        });
        if (signupError) throw signupError;
        if (created.session) {
          const {data:confirmed,error:checkError}=await client.auth.getUser();
          if (isSessionBoundaryBlocked() || checkError || !confirmed.user || confirmed.user.email?.toLowerCase()!==expectedEmail)
            throw new Error('Account verification failed. Please sign in again.');
          onAuthenticated(confirmed.user.id,confirmed.user.email||null);
          await exportWithFeedback();
          setOpen(false); setPassword('');
        } else {
          setNotice(arabic
            ? 'راجع بريدك لتأكيد الحساب. اترك هذا التبويب مفتوحًا، ثم ارجع له وسجّل الدخول بنفس البريد لإكمال الحفظ.'
            : 'Check your email to confirm your account. Keep this tab open, then sign in here with the same email to finish saving your CV.');
          setMode('signin');
        }
      }
    } catch(e: unknown) {
      setError(e instanceof Error ? e.message : 'Authentication failed.');
    } finally {setBusy(false);active.current=false;}
  }

  // Only resume an expressly requested PDF after a verified account sign-in
  // matching the signup email; never attach a guest draft to another user.
  useEffect(() => {
    if (saving || !hydrated || !userId || autoResumed.current || isSessionBoundaryBlocked()) return;
    const transfer=readTransfer();
    if (!transfer?.requested || !transfer.email || transfer.action === 'save') return;
    autoResumed.current=true;
    let disposed=false;
    (async()=>{
      const client=createClient();
      if (!client) return;
      const {data:verified,error:authError}=await client.auth.getUser();
      if (disposed || authError || !verified.user ||
          verified.user.id!==userId ||
          verified.user.email?.toLowerCase()!==transfer.email?.toLowerCase()) {
        if (!disposed) setError(arabic
          ? 'يجب تسجيل الدخول بنفس البريد الذي بدأت به إنشاء السيرة.'
          : 'Please sign in using the same email you used to start the CV.');
        return;
      }
      if (active.current || isSessionBoundaryBlocked()) return;
      active.current=true; setBusy(true);
      try { await exportWithFeedback(); }
      catch(e:unknown) { if (!disposed) setError(e instanceof Error ? e.message : 'PDF export failed.'); }
      finally {active.current=false;if(!disposed)setBusy(false);}
    })();
    return()=>{disposed=true;};
  },[hydrated,userId,arabic]);

  function cancel() {
    if (busy) return;
    // Cancel pending export, retain guest draft briefly for safe editing reload.
    const transfer=readTransfer();
    if (transfer) try {storeTransfer({...transfer,requested:false});} catch {}
    setOpen(false);setPassword('');setNotice('');
    (saving ? returnFocus.current : trigger.current)?.focus();
  }

  return <span className="sirati-builder-pdf-action">
    {!saving && <button ref={trigger} type="button" className="btn btn-secondary btn-lg"
      disabled={busy} aria-busy={busy} onClick={begin}>
      {busy ? (arabic?'جارٍ إعداد PDF…':'Preparing PDF…')
        : (arabic?'حفظ PDF':'Save PDF')}
    </button>}
    {error && <small role="alert" className="sirati-pdf-error">{error}</small>}
    {open && <div className="sirati-pdf-auth-overlay">
      <section ref={dialogRef} role="dialog" aria-modal="true" aria-labelledby={dialogId}
        className="sirati-pdf-auth-dialog" dir={arabic?'rtl':'ltr'}>
        <button type="button" className="sirati-pdf-auth-close" aria-label="Close"
          disabled={busy} onClick={cancel}>×</button>
        <h2 id={dialogId}>
          {saving ? (arabic?'سجّل الدخول لحفظ سيرتك':'Sign in to save your CV')
            : (arabic?'أنشئ حسابًا مجانيًا لحفظ سيرتك PDF':'Create a free account to save your CV as PDF')}
        </h2>
        <p>{arabic?'سيرتك وقالبك سيظلان كما هما. لا توجد رسوم.':'Your CV and selected template stay intact. No payment required.'}</p>
        <div className="sirati-pdf-auth-modes">
          <button type="button" aria-pressed={mode==='signup'} disabled={busy}
            onClick={()=>{setMode('signup');setError('')}}>{arabic?'حساب جديد':'Sign up'}</button>
          <button type="button" aria-pressed={mode==='signin'} disabled={busy}
            onClick={()=>{setMode('signin');setError('')}}>{arabic?'تسجيل الدخول':'Sign in'}</button>
        </div>
        <form onSubmit={submit}>
          <label htmlFor={dialogId + '-email'}>{arabic?'البريد الإلكتروني':'Email'}</label>
          <input ref={firstField} id={dialogId + '-email'} type="email" required
            autoComplete="email" value={email} onChange={e=>setEmail(e.target.value)}
            disabled={busy}/>
          <label htmlFor={dialogId + '-password'}>{arabic?'كلمة المرور':'Password'}</label>
          <input id={dialogId + '-password'} type="password" minLength={8} required
            autoComplete={mode==='signup'?'new-password':'current-password'}
            value={password} onChange={e=>setPassword(e.target.value)} disabled={busy}/>
          <button className="btn btn-primary" type="submit" disabled={busy}>
            {busy?(arabic?'جارٍ المعالجة…':'Please wait…')
              :(mode==='signup'?(arabic?'إنشاء حساب ومتابعة':'Create account and continue')
                :(saving ? (arabic?'دخول وحفظ السيرة':'Sign in and save CV') : (arabic?'دخول وتنزيل PDF':'Sign in and download PDF')))}
          </button>
        </form>
        {notice&&<p role="status">{notice}</p>}
        {error&&<p role="alert" className="sirati-pdf-error">{error}</p>}
        <button type="button" onClick={cancel} disabled={busy}
          className="sirati-pdf-auth-cancel">{arabic?'العودة لتعديل السيرة':'Back to editing'}</button>
      </section>
    </div>}
  </span>;
}
""",encoding="utf-8")

css=css_path.read_text(encoding='utf-8')
if '/* Sirati #98 Save PDF auth gate */' in css:
    raise SystemExit('Duplicate guest PDF auth CSS')
css+=r"""
/* Sirati #98 Save PDF auth gate */
@media screen {
  .sirati-pdf-auth-overlay { position:fixed;inset:0;z-index:2147482000;
    display:flex;align-items:center;justify-content:center;padding:16px;
    background:rgba(8,24,18,.63); }
  .sirati-pdf-auth-dialog { position:relative;background:#fff;color:#19352a;
    border-radius:16px;box-shadow:0 22px 65px #0004;padding:24px;
    width:min(100%,440px);max-height:92vh;overflow-y:auto; }
  .sirati-pdf-auth-dialog h2 {font-size:1.25rem;margin:0 24px 8px 0}
  .sirati-pdf-auth-dialog p {font-size:.9rem;line-height:1.6}
  .sirati-pdf-auth-dialog form {display:grid;gap:8px;margin-top:12px}
  .sirati-pdf-auth-dialog input {width:100%;box-sizing:border-box;min-height:44px;
    border:1px solid #9daea3;border-radius:8px;padding:10px;font:inherit}
  .sirati-pdf-auth-dialog form button {min-height:44px;margin-top:8px}
  .sirati-pdf-auth-modes {display:flex;gap:8px;flex-wrap:wrap}
  .sirati-pdf-auth-modes button {min-height:42px;padding:7px 13px;border-radius:8px;
    border:1px solid #a8beb1;background:#f6faf7;color:#29473a}
  .sirati-pdf-auth-modes [aria-pressed=true] {background:#1d523d;color:#fff}
  .sirati-pdf-auth-close {position:absolute;top:10px;right:10px;
    background:transparent;border:0;font-size:24px;min-width:36px;min-height:36px}
  .sirati-pdf-auth-cancel {margin-top:12px;padding:10px;border:0;
    text-decoration:underline;background:transparent;color:#284b3c}
}
@media print {.sirati-pdf-auth-overlay {display:none!important}}
"""
css_path.write_text(css,encoding='utf-8')
print('PASS: guest builder enabled; verified auth gate only at Save PDF; no DB changes.')
