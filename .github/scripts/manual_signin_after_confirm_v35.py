"""V35: email verification and password recovery require explicit sign-in.

Keep identity verification and existing CV drafts; do not auto-enter the site.
Generated-site patch runs only after V34; fail closed on missing anchors.
No changes to Supabase configuration, database, secrets or PDF logic.
"""
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve()
auth=root/"app/auth/page.tsx"
confirm=root/"app/auth/confirm/page.tsx"
recovery=root/"app/auth/recovery/page.tsx"

def replace_exact(text,before,after,label):
    if text.count(before)!=1:
        raise RuntimeError("V35 expected exactly one "+label+" anchor")
    return text.replace(before,after,1)

auth_text=auth.read_text(encoding="utf-8")
assert "sirati-auth-v34-card" in auth_text and "export default function AuthPage()" in auth_text
auth_text=replace_exact(auth_text,
    "  const [notice,setNotice]=useState('');",
    """  const [notice,setNotice]=useState('');
  const [postVerification,setPostVerification]=useState<'confirmed'|'password_changed'|null>(null);""",
    "auth outcome state")
auth_text=replace_exact(auth_text,
    """    if (params.get('error')==='confirmation') setError('تعذّر تأكيد البريد. اطلب رسالة جديدة · Email confirmation failed. Request a new email.');
    const client=createClient();""",
    """    if (params.get('error')==='confirmation') setError('تعذّر تأكيد البريد. اطلب رسالة جديدة · Email confirmation failed. Request a new email.');
    // Verification/reset callbacks must NOT auto-enter the app after email proof.
    // The user types their email and password on this screen themselves.
    const outcome=params.get('confirmed')==='1'?'confirmed':
      params.get('password_changed')==='1'?'password_changed':null;
    if (outcome) {
      setPostVerification(outcome);
      setMode('signin');
      return;
    }
    const client=createClient();""",
    "prevent auto-entry after email")
auth_text=replace_exact(auth_text,
    "    setMode(next);setError('');setNotice('');setPassword('');setConfirm('');",
    "    setMode(next);setError('');setNotice('');setPostVerification(null);setPassword('');setConfirm('');",
    "clear signup mode notice")
auth_text=replace_exact(auth_text,
    """        <p className="sirati-auth-v34-sub">{sent?(ar?'تأكيد البريد خطوة لحماية حسابك.':'Email verification helps protect your account.'):
          mode==='signin'?(ar?'ادخل لحفظ سيرك ومتابعة عملك.':'Access your saved CVs and continue editing.'):
          (ar?'خطوات بسيطة، بدون اشتراك أو رسوم.':'A quick setup, with no subscription or payment.')}</p>""",
    """        <p className="sirati-auth-v34-sub">{sent?(ar?'تأكيد البريد خطوة لحماية حسابك.':'Email verification helps protect your account.'):
          mode==='signin'?(ar?'ادخل لحفظ سيرك ومتابعة عملك.':'Access your saved CVs and continue editing.'):
          (ar?'خطوات بسيطة، بدون اشتراك أو رسوم.':'A quick setup, with no subscription or payment.')}</p>
        {postVerification&&<div className="sirati-auth-v35-confirmed" role="status" aria-live="polite">
          <strong>{postVerification==='confirmed'?
            (ar?'تم تأكيد بريدك الإلكتروني بنجاح ✓':'Email confirmed successfully ✓'):
            (ar?'تم تغيير كلمة المرور بنجاح ✓':'Password updated successfully ✓')}</strong>
          <p>{postVerification==='confirmed'?
            (ar?'سجّل الدخول الآن بالبريد الإلكتروني وكلمة المرور التي أنشأتها.':
              'Now enter your email and the password you created to sign in.'):
            (ar?'سجّل الدخول بالبريد الإلكتروني وكلمة المرور الجديدة.':
              'Sign in using your email and your new password.')}</p>
        </div>}""",
    "bilingual confirmation success notice")
auth.write_text(auth_text,encoding="utf-8")

confirm_text=confirm.read_text(encoding="utf-8")
assert "exchangeCodeForSession" in confirm_text and "verifyOtp" in confirm_text
assert "window.location.href = withBasePath(next)" in confirm_text
assert "Back to sign in" in confirm_text
confirm.write_text(r"""'use client';

import {useEffect, useState} from 'react';
import type {EmailOtpType} from '@supabase/supabase-js';
import {createClient} from '@/lib/supabase/client';
import {withBasePath} from '@/lib/basePath';
import {isSessionBoundaryBlocked} from '@/lib/sessionBoundary';

function safeNext(raw:string|null) {
  if (!raw || !raw.startsWith('/') || raw.startsWith('//') || raw.includes('\\') ||
      /[\u0000-\u001f]/.test(raw)) return '/templates';
  return raw;
}

export default function ConfirmPage() {
  const [message,setMessage]=useState('جارٍ تأكيد البريد الإلكتروني… · Verifying your email…');
  const [retry,setRetry]=useState(false);
  const [nextPath,setNextPath]=useState('/templates');
  const loginUrl=()=>withBasePath('/auth?confirmed=1&next='+encodeURIComponent(nextPath));

  async function endConfirmationSession(next:string) {
    const client=createClient();
    if (!client) throw new Error('Account service unavailable');
    // A confirmed link may create an auth session. Remove only this device's
    // session; never clear or modify CV drafts or sessions on other devices.
    const {error}=await client.auth.signOut({scope:'local'});
    if (error) throw error;
    window.location.replace(withBasePath('/auth?confirmed=1&next='+encodeURIComponent(next)));
  }
  useEffect(()=>{
    let alive=true;
    async function confirmEmail() {
      const params=new URLSearchParams(window.location.search);
      const hash=new URLSearchParams(window.location.hash.slice(1));
      const next=safeNext(params.get('next'));
      setNextPath(next);
      const code=params.get('code');
      const tokenHash=params.get('token_hash');
      const type=params.get('type') as EmailOtpType|null;
      const implicitSignup=hash.get('type')==='signup' &&
        Boolean(hash.get('access_token')) && Boolean(hash.get('refresh_token'));
      const client=createClient();
      if (!client) {
        if (alive) setMessage('خدمة الحسابات غير متاحة. · Account service unavailable.');
        return;
      }
      // A plain visit to /auth/confirm is never evidence of email ownership,
      // even when there is an unrelated existing sign-in session.
      if (!code && !(tokenHash && type) && !implicitSignup) {
        if (alive) setMessage('الرابط غير مكتمل أو مستخدم سابقًا. · The confirmation link is missing or already used.');
        return;
      }
      try {
        if (code) {
          const {error}=await client.auth.exchangeCodeForSession(code);
          if (error) throw error;
        } else if (tokenHash && type) {
          const {error}=await client.auth.verifyOtp({token_hash:tokenHash,type});
          if (error) throw error;
        } else {
          // For the Supabase implicit flow, getSession waits for URL detection.
          const {data,error}=await client.auth.getSession();
          if (error || !data.session) throw new Error('No confirmation session');
        }
        const {data,error}=await client.auth.getUser();
        if (error || !data.user?.email_confirmed_at || isSessionBoundaryBlocked())
          throw new Error('No verified confirmation');
        // Remove one-time token/code (and any implicit tokens) from browser history.
        window.history.replaceState(null,'',withBasePath('/auth/confirm'));
        if (!alive) return;
        setMessage('تم تأكيد البريد. جارٍ تجهيز تسجيل الدخول… · Email confirmed. Preparing sign in…');
        try {
          await endConfirmationSession(next);
        } catch {
          if (!alive) return;
          setRetry(true);
          setMessage('تم تأكيد البريد، لكن تعذّر إغلاق جلسة التفعيل بأمان. أعد المحاولة. · Email confirmed, but the temporary session could not be closed. Please retry.');
        }
      } catch {
        if (alive) setMessage('تعذّر تأكيد البريد. اطلب رسالة تفعيل جديدة. · We could not confirm your email. Request a new link.');
      }
    }
    void confirmEmail();
    return ()=>{alive=false;};
  },[]);
  return <main className="container sirati-auth-v34-utility" dir="auto">
    <h1>تأكيد البريد الإلكتروني · Confirm email</h1>
    <p role="status" aria-live="polite">{message}</p>
    {retry ? <button className="btn btn-primary" onClick={()=>{
      setRetry(false);
      void endConfirmationSession(nextPath).catch(()=>{
        setRetry(true);
        setMessage('تعذّر إغلاق جلسة التفعيل. أعد المحاولة. · Please retry closing the confirmation session.');
      });
    }}>متابعة لتسجيل الدخول · Continue to sign in</button>:
    <a href={withBasePath('/auth?error=confirmation')} className="btn btn-secondary">
      العودة لتسجيل الدخول · Back to sign in
    </a>}
  </main>;
}
""",encoding="utf-8")

recovery_text=recovery.read_text(encoding="utf-8")
assert "recoveryAuthorized.current=false" in recovery_text
recovery_text=replace_exact(recovery_text,
    "  const [stage, setStage] = useState<'request'|'change'|'sent'|'complete'>('request');",
    "  const [stage, setStage] = useState<'request'|'change'|'sent'|'complete'|'signout_pending'>('request');",
    "recovery stage")
recovery_text=replace_exact(recovery_text,
    """      recoveryAuthorized.current=false;
      setNewPassword('');setConfirm('');setStage('complete');
      window.history.replaceState(null,'',withBasePath('/auth/recovery'));""",
    """      recoveryAuthorized.current=false;
      setNewPassword('');setConfirm('');
      window.history.replaceState(null,'',withBasePath('/auth/recovery'));
      // Password recovery itself creates a logged-in session. An explicit
      // email+NEW-password sign-in is required after the change.
      const {error:signOutError}=await client.auth.signOut({scope:'local'});
      if (signOutError) {
        setStage('signout_pending');
        setMessage('تم تغيير كلمة المرور، لكن تعذّر إغلاق جلسة الاستعادة. أعد المحاولة. · Password updated; please retry ending the temporary session.');
        return;
      }
      setStage('complete');
      window.location.replace(withBasePath('/auth?password_changed=1'));""",
    "manual login after reset")
recovery_text=replace_exact(recovery_text,
    """    {stage==='complete' && <p role="status">تم تحديث كلمة المرور بنجاح. · Password updated successfully.</p>}""",
    """    {stage==='complete' && <p role="status">تم تحديث كلمة المرور بنجاح. يرجى تسجيل الدخول بالبريد وكلمة المرور الجديدة. · Password updated. Sign in with your email and new password.</p>}
    {stage==='signout_pending' && <button type="button" className="btn btn-primary"
      onClick={async()=>{
        if (busy) return;
        const client=createClient();
        if (!client) return;
        setBusy(true);
        try {
          const {error}=await client.auth.signOut({scope:'local'});
          if (error) throw error;
          window.location.replace(withBasePath('/auth?password_changed=1'));
        } catch {
          setMessage('حاول مرة أخرى لإغلاق جلسة الاستعادة. · Retry ending the temporary recovery session.');
        } finally {setBusy(false);}
      }} disabled={busy}>متابعة لتسجيل الدخول · Continue to sign in</button>""",
    "retry local logout after reset")
recovery.write_text(recovery_text,encoding="utf-8")

css=root/"app/globals.css"
style=css.read_text(encoding="utf-8")
if "/* Sirati Auth V34 — scoped" not in style or "sirati-auth-v35-confirmed" in style:
    raise RuntimeError("V35 expected generated V34 stylesheet")
style += """
/* V35: positive, readable confirmation notice on mobile and desktop */
.sirati-auth-v35-confirmed {border:1px solid #a4d5b7;background:#edf8f0;
  color:#165338;border-radius:12px;padding:14px 16px;margin:2px 0 18px;
  line-height:1.65;font-size:14px}
.sirati-auth-v35-confirmed strong {font-size:15px;display:block;margin-bottom:4px}
.sirati-auth-v35-confirmed p {margin:0;color:#275b41}
"""
css.write_text(style,encoding="utf-8")
print("PASS: confirmation session ends before sign-in; recovery session ends before new-password login")
