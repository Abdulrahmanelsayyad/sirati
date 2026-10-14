"""Sirati V33: self-service password recovery and authenticated password change.

Applied to generated app after existing authentication/session-boundary scripts.
No Auth provider configuration, policies, database, credentials or exports change.
Fail closed if expected signup/dialog/menu hooks are absent.
"""
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve()

def add_page(relative, body):
    path=root/relative
    if path.exists():
        raise RuntimeError("Password UX route already exists: "+relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body,encoding="utf-8")

add_page("app/auth/recovery/page.tsx", r"""'use client';

import {useEffect, useRef, useState, type FormEvent} from 'react';
import {createClient} from '@/lib/supabase/client';
import {withBasePath} from '@/lib/basePath';
import {isSessionBoundaryBlocked} from '@/lib/sessionBoundary';

export default function RecoverPasswordPage() {
  const [email, setEmail] = useState('');
  const [verifiedEmail, setVerifiedEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [visible, setVisible] = useState(false);
  const [busy, setBusy] = useState(false);
  const [stage, setStage] = useState<'request'|'change'|'sent'|'complete'>('request');
  const [message, setMessage] = useState('');
  // Only Supabase's verified recovery event authorizes a password change.
  const recoveryAuthorized = useRef(false);
  useEffect(() => {
    const client=createClient();
    if (!client) {setMessage('خدمة الحسابات غير متاحة حاليًا · Account service unavailable.');return;}
    let alive=true;
    async function verifyRecoverySession() {
      const {data,error}=await client!.auth.getUser();
      if (!alive || isSessionBoundaryBlocked()) return;
      if (!error && data.user?.email) {
        recoveryAuthorized.current=true;
        setVerifiedEmail(data.user.email);
        setStage('change');setMessage('');
      } else {
        recoveryAuthorized.current=false;
        setMessage('رابط الاستعادة غير صالح أو انتهت صلاحيته. اطلب رابطًا جديدًا. · Request a fresh reset link.');
      }
    }
    const {data:{subscription}}=client.auth.onAuthStateChange((event)=>{
      // Supabase auth callbacks must not await another Supabase call inline.
      if (event==='PASSWORD_RECOVERY') window.setTimeout(()=>{void verifyRecoverySession();},0);
    });
    // The ?flow=password marker is ONLY navigation, never proof of recovery.
    // Requiring PASSWORD_RECOVERY prevents an existing session from using
    // a hand-crafted recovery URL to bypass current-password verification.
    if (new URLSearchParams(window.location.search).get('flow')==='password') {
      setMessage('تحقق من رابط البريد. إذا لم تظهر خانات كلمة المرور، اطلب رابطًا جديدًا. · If reset fields do not appear, request a fresh email link.');
    }
    return ()=>{alive=false;subscription.unsubscribe();};
  },[]);
  async function sendReset(e:FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (busy) return;
    const client=createClient();
    if (!client) {setMessage('خدمة الحسابات غير متاحة · Account service unavailable.');return;}
    setBusy(true);setMessage('');
    try {
      const url=window.location.origin+withBasePath('/auth/recovery?flow=password');
      const {error}=await client.auth.resetPasswordForEmail(email.trim().toLowerCase(),{redirectTo:url});
      if (error) throw error;
      // The same response is shown whether an account exists, to avoid user enumeration.
      setStage('sent');
    } catch {
      setMessage('تعذّر إرسال الرابط. حاول لاحقًا. · Could not send reset link. Please retry.');
    } finally {setBusy(false);}
  }
  async function changePassword(e:FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (busy) return;
    if (newPassword.length<8 || newPassword!==confirm) {
      setMessage('استخدم 8 أحرف على الأقل، وتأكد من تطابق كلمتَي المرور. · Passwords must match and have at least 8 characters.');
      return;
    }
    const client=createClient();
    if (!recoveryAuthorized.current || !client || isSessionBoundaryBlocked()) {
      setMessage('هذه العملية تتطلب رابط استعادة صالحًا من البريد. · Open a valid password recovery link.');return;
    }
    setBusy(true);setMessage('');
    try {
      const {data:verified,error:verificationError}=await client.auth.getUser();
      if (verificationError || !verified.user || verified.user.email?.toLowerCase()!==verifiedEmail.toLowerCase()) {
        throw new Error('Session verification failed');
      }
      const {error}=await client.auth.updateUser({password:newPassword});
      if (error) throw error;
      recoveryAuthorized.current=false;
      setNewPassword('');setConfirm('');setStage('complete');
      window.history.replaceState(null,'',withBasePath('/auth/recovery'));
    } catch {
      setMessage('تعذّر تعديل كلمة المرور. قد تحتاج لرابط جديد أو إعادة التحقق. · Password change failed; retry the recovery link.');
    } finally {setBusy(false);}
  }
  return <main className="container" style={{maxWidth:520,paddingBlock:48}} dir="auto">
    <h1>استعادة كلمة المرور · Reset password</h1>
    {stage==='request' && <>
      <p>أدخل بريدك لإرسال رابط الاستعادة. · Enter your email to receive a reset link.</p>
      <form onSubmit={sendReset} style={{display:'grid',gap:12}}>
        <label htmlFor="recovery-email">البريد الإلكتروني · Email</label>
        <input id="recovery-email" type="email" autoComplete="email" required
          value={email} onChange={e=>setEmail(e.target.value)} disabled={busy}
          style={{padding:12,minHeight:44,width:'100%'}}/>
        <button className="btn btn-primary" disabled={busy} type="submit">{busy?'جارٍ الإرسال… · Sending…':'إرسال رابط الاستعادة · Send reset link'}</button>
      </form>
    </>}
    {stage==='sent' && <p role="status">إذا كان البريد مسجلًا، ستصلك رسالة برابط الاستعادة. افحص البريد غير المرغوب أيضًا. · If the account exists, a reset email will arrive. Check spam as well.</p>}
    {stage==='change' && <>
      <p>تغيير كلمة المرور للحساب: <strong>{verifiedEmail}</strong></p>
      <form onSubmit={changePassword} style={{display:'grid',gap:12}}>
        <label htmlFor="recovery-new">كلمة مرور جديدة · New password</label>
        <input id="recovery-new" type={visible?'text':'password'} minLength={8} required
          autoComplete="new-password" value={newPassword} onChange={e=>setNewPassword(e.target.value)}
          disabled={busy} style={{padding:12,minHeight:44,width:'100%'}}/>
        <label htmlFor="recovery-confirm">تأكيد كلمة المرور · Confirm password</label>
        <input id="recovery-confirm" type={visible?'text':'password'} minLength={8} required
          autoComplete="new-password" value={confirm} onChange={e=>setConfirm(e.target.value)}
          disabled={busy} style={{padding:12,minHeight:44,width:'100%'}}/>
        <label><input type="checkbox" checked={visible} onChange={e=>setVisible(e.target.checked)}/> إظهار كلمات المرور · Show passwords</label>
        <button className="btn btn-primary" type="submit" disabled={busy}>{busy?'جارٍ الحفظ… · Saving…':'تحديث كلمة المرور · Update password'}</button>
      </form>
    </>}
    {stage==='complete' && <p role="status">تم تحديث كلمة المرور بنجاح. · Password updated successfully.</p>}
    {message && <p role="alert">{message}</p>}
    <p style={{marginTop:24}}><a href={withBasePath('/auth')}>العودة لتسجيل الدخول · Return to sign in</a></p>
  </main>;
}
""")

add_page("app/account/password/page.tsx", r"""'use client';

import {useEffect, useState, type FormEvent} from 'react';
import {createClient} from '@/lib/supabase/client';
import {withBasePath} from '@/lib/basePath';
import {isSessionBoundaryBlocked} from '@/lib/sessionBoundary';

export default function AccountPasswordPage() {
  const [email,setEmail]=useState('');
  const [loading,setLoading]=useState(true);
  const [busy,setBusy]=useState(false);
  const [password,setPassword]=useState('');
  const [confirm,setConfirm]=useState('');
  const [visible,setVisible]=useState(false);
  const [message,setMessage]=useState('');
  const [success,setSuccess]=useState(false);
  useEffect(()=>{
    let alive=true;
    const client=createClient();
    if (!client) {setLoading(false);return;}
    void client.auth.getUser().then(({data,error})=>{
      if (!alive) return;
      if (!error && data.user && !isSessionBoundaryBlocked()) setEmail(data.user.email||'');
      setLoading(false);
    });
    return ()=>{alive=false;};
  },[]);
  async function submit(e:FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (busy || isSessionBoundaryBlocked()) return;
    if (password.length<8 || password!==confirm) {
      setMessage('كلمة المرور يجب ألا تقل عن 8 أحرف وأن تتطابق مع التأكيد. · Use 8+ matching characters.');return;
    }
    const client=createClient();
    if (!client) {setMessage('خدمة الحسابات غير متاحة · Account service unavailable.');return;}
    setBusy(true);setMessage('');
    try {
      const {data,error}=await client.auth.getUser();
      if (error || !data.user || data.user.email?.toLowerCase()!==email.toLowerCase()) throw new Error('Session mismatch');
      const updated=await client.auth.updateUser({password});
      if (updated.error) throw updated.error;
      setPassword('');setConfirm('');setSuccess(true);
    } catch {
      setMessage('لم نتمكن من التحديث. أعد التحقق أو استخدم استعادة كلمة المرور. · Update failed; please reverify or use recovery.');
    } finally {setBusy(false);}
  }
  return <main className="container" style={{maxWidth:520,paddingBlock:48}} dir="auto">
    <h1>أمان الحساب · Account security</h1>
    {loading?<p role="status">جارٍ التحقق… · Verifying session…</p>
      : !email ? <p>يلزم تسجيل الدخول لتغيير كلمة المرور. · Sign in to change your password.
        {' '}<a href={withBasePath('/auth?next=/account/password')}>تسجيل الدخول · Sign in</a></p>
      : <>
        <p>الحساب: <strong>{email}</strong></p>
        <form onSubmit={submit} style={{display:'grid',gap:12}}>
          <label htmlFor="account-new">كلمة المرور الجديدة · New password</label>
          <input id="account-new" type={visible?'text':'password'} minLength={8} required
            autoComplete="new-password" value={password} onChange={e=>setPassword(e.target.value)}
            disabled={busy} style={{padding:12,minHeight:44,width:'100%'}}/>
          <label htmlFor="account-confirm">تأكيد كلمة المرور · Confirm password</label>
          <input id="account-confirm" type={visible?'text':'password'} minLength={8} required
            autoComplete="new-password" value={confirm} onChange={e=>setConfirm(e.target.value)}
            disabled={busy} style={{padding:12,minHeight:44,width:'100%'}}/>
          <label><input type="checkbox" checked={visible} onChange={e=>setVisible(e.target.checked)}/> إظهار كلمات المرور · Show passwords</label>
          <button className="btn btn-primary" disabled={busy} type="submit">{busy?'جارٍ الحفظ… · Saving…':'حفظ كلمة المرور الجديدة · Save new password'}</button>
        </form>
        <p><a href={withBasePath('/auth/recovery')}>نسيت كلمة المرور؟ · Forgot password?</a></p>
      </>}
    {success && <p role="status">تم تغيير كلمة المرور بنجاح. · Password changed successfully.</p>}
    {message && <p role="alert">{message}</p>}
  </main>;
}
""")

button=root/"components/SiratiBuilderPdfButton.tsx"
source=button.read_text(encoding="utf-8")
anchor='''        {notice&&<p role="status">{notice}</p>}'''
assert source.count(anchor)==1,"Expected one PDF auth dialog notice anchor"
source=source.replace(anchor,'''        {mode==='signin' && <p><a href={withBasePath('/auth/recovery')}>
          {arabic?'نسيت كلمة المرور؟':'Forgot password?'}
        </a></p>}
'''+anchor,1)
button.write_text(source,encoding="utf-8")

menu=root/"components/SiratiSiteMenu.tsx"
source=menu.read_text(encoding="utf-8")
anchor='''                <button type="button" className="sirati-menu-signout"'''
assert source.count(anchor)==1,"Expected one signed-in menu signout anchor"
source=source.replace(anchor,'''                <a href={withBasePath('/account/password')} onClick={close}>
                  تغيير كلمة المرور · Change password
                </a>
'''+anchor,1)
menu.write_text(source,encoding="utf-8")
print("PASS: recovery and change-password pages + PDF sign-in and account menu links")
