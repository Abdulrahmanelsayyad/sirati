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
        return;
      }
""" + source[end:]

# Restore an expiring tab-only guest snapshot only for the same guest, or for
# the confirmed email used to create it. Never open it on someone else's account,
# never overwrite a saved ?doc=, and never write guest CV to a server automatically.
anchor="      setUserId(user?.id ?? null);\n      setUserEmail(user?.email ?? null);\n"
if source.count(anchor)!=1:
    raise SystemExit('Builder account identity anchor changed')
source=source.replace(anchor,anchor+"""      const guestDocRequested = new URLSearchParams(window.location.search).has('doc');
      if (!guestDocRequested && !newCvRequestedRef.current) {
        try {
          const raw = window.sessionStorage.getItem('sirati.guest.pdf.pending.v1');
          const pending = raw ? JSON.parse(raw) : null;
          const emailOK = !user || (typeof pending?.email === 'string' &&
            pending.email.toLowerCase() === user.email?.toLowerCase());
          if (pending?.version === 1 && typeof pending.createdAt === 'number' &&
              Date.now() - pending.createdAt >= 0 &&
              Date.now() - pending.createdAt < 30 * 60 * 1000 && emailOK &&
              pending.data && typeof pending.data === 'object') {
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
builder_path.write_text(source,encoding='utf-8')

# Keep the original PDF generator unchanged. Password auth stays on the page;
# the CV remains mounted during sign-in. For email confirmation, the same-tab
# session snapshot can resume after redirect; never transmit CV content in URLs.
button_path.write_text(r"""'use client';

import { useEffect, useRef, useState, type FormEvent } from 'react';
import { createClient } from '@/lib/supabase/client';
import { withBasePath } from '@/lib/basePath';
import { downloadCvSheet } from '@/lib/siratiPdfExport';
import type { CvData, TemplateName } from '@/lib/types';

const PENDING_KEY = 'sirati.guest.pdf.pending.v1';
const MAX_AGE = 30 * 60 * 1000;
type Transfer = {
  version: 1; createdAt: number; email: string | null; requested: boolean;
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
type Props = {
  language: string; data: CvData; template: TemplateName; hydrated: boolean;
  userId: string | null; onAuthenticated: (id: string, email: string | null) => void;
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
  const arabic = language === 'ar';

  useEffect(() => {
    if (!open) return;
    firstField.current?.focus();
    const escape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !busy) { setOpen(false); trigger.current?.focus(); }
    };
    window.addEventListener('keydown', escape);
    return () => window.removeEventListener('keydown', escape);
  }, [open,busy]);

  async function exportCurrentSheet() {
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

  async function begin() {
    if (active.current) return;
    active.current = true;
    setBusy(true); setError(''); setNotice('');
    try {
      if (!hydrated) throw new Error('CV is still loading. Try again.');
      const client = createClient();
      const result = client ? await client.auth.getUser() : null;
      if (result && !result.error && result.data.user) {
        onAuthenticated(result.data.user.id, result.data.user.email || null);
        await exportCurrentSheet();
        return;
      }
      // Preserve exact editable CV, language, template and photo data in this tab.
      storeTransfer({version:1,createdAt:Date.now(),email:null,requested:true,
        data,template,language});
      setOpen(true);
    } catch(e: unknown) {
      setError(e instanceof Error ? e.message : 'Cannot prepare your PDF.');
    } finally { setBusy(false); active.current=false; }
  }

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (active.current) return;
    active.current=true; setBusy(true); setError(''); setNotice('');
    try {
      if (password.length < 8) throw new Error('Use a password of at least 8 characters.');
      const client=createClient();
      if (!client) throw new Error('Account service unavailable.');
      const transfer=readTransfer();
      if (!transfer) throw new Error('Guest draft expired. Your CV is still in the editor; click Save PDF again.');
      const expectedEmail=email.trim().toLowerCase();
      if (!expectedEmail) throw new Error('Enter your email.');
      storeTransfer({...transfer,email:expectedEmail,requested:true});
      if (mode==='signin') {
        const {error:signinError}=await client.auth.signInWithPassword({
          email:expectedEmail,password
        });
        if (signinError) throw signinError;
        const {data:auth,error:userError}=await client.auth.getUser();
        if (userError || !auth.user || auth.user.email?.toLowerCase()!==expectedEmail)
          throw new Error('Account verification failed. Try signing in again.');
        onAuthenticated(auth.user.id,auth.user.email||null);
        await exportCurrentSheet();
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
          if (checkError || !confirmed.user || confirmed.user.email?.toLowerCase()!==expectedEmail)
            throw new Error('Account verification failed. Please sign in again.');
          onAuthenticated(confirmed.user.id,confirmed.user.email||null);
          await exportCurrentSheet();
          setOpen(false); setPassword('');
        } else {
          setNotice(arabic
            ? 'راجع بريدك لتأكيد الحساب. اترك هذا التبويب مفتوحًا، ثم ارجع له وسجّل الدخول بنفس البريد لإكمال تنزيل PDF.'
            : 'Check your email to confirm your account. Keep this tab open, then sign in here with the same email to finish your PDF.');
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
    if (!hydrated || !userId || autoResumed.current) return;
    const transfer=readTransfer();
    if (!transfer?.requested || !transfer.email) return;
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
      if (active.current) return;
      active.current=true; setBusy(true);
      try { await exportCurrentSheet(); }
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
    trigger.current?.focus();
  }

  return <span className="sirati-builder-pdf-action">
    <button ref={trigger} type="button" className="btn btn-secondary btn-lg"
      disabled={busy} onClick={begin}>
      {busy ? (arabic?'جارٍ إعداد PDF…':'Preparing PDF…')
        : (arabic?'حفظ PDF':'Save PDF')}
    </button>
    {error && <small role="alert" className="sirati-pdf-error">{error}</small>}
    {open && <div className="sirati-pdf-auth-overlay">
      <section role="dialog" aria-modal="true" aria-labelledby="sirati-pdf-auth-heading"
        className="sirati-pdf-auth-dialog" dir={arabic?'rtl':'ltr'}>
        <button type="button" className="sirati-pdf-auth-close" aria-label="Close"
          disabled={busy} onClick={cancel}>×</button>
        <h2 id="sirati-pdf-auth-heading">
          {arabic?'أنشئ حسابًا مجانيًا لحفظ سيرتك PDF':'Create a free account to save your CV as PDF'}
        </h2>
        <p>{arabic?'سيرتك وقالبك سيظلان كما هما. لا توجد رسوم.':'Your CV and selected template stay intact. No payment required.'}</p>
        <div className="sirati-pdf-auth-modes">
          <button type="button" aria-pressed={mode==='signup'} disabled={busy}
            onClick={()=>{setMode('signup');setError('')}}>{arabic?'حساب جديد':'Sign up'}</button>
          <button type="button" aria-pressed={mode==='signin'} disabled={busy}
            onClick={()=>{setMode('signin');setError('')}}>{arabic?'تسجيل الدخول':'Sign in'}</button>
        </div>
        <form onSubmit={submit}>
          <label htmlFor="sirati-pdf-email">{arabic?'البريد الإلكتروني':'Email'}</label>
          <input ref={firstField} id="sirati-pdf-email" type="email" required
            autoComplete="email" value={email} onChange={e=>setEmail(e.target.value)}
            disabled={busy}/>
          <label htmlFor="sirati-pdf-password">{arabic?'كلمة المرور':'Password'}</label>
          <input id="sirati-pdf-password" type="password" minLength={8} required
            autoComplete={mode==='signup'?'new-password':'current-password'}
            value={password} onChange={e=>setPassword(e.target.value)} disabled={busy}/>
          <button className="btn btn-primary" type="submit" disabled={busy}>
            {busy?(arabic?'جارٍ المعالجة…':'Please wait…')
              :(mode==='signup'?(arabic?'إنشاء حساب ومتابعة':'Create account and continue')
                :(arabic?'دخول وتنزيل PDF':'Sign in and download PDF'))}
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
