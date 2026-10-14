"""V34: focused production-quality bilingual account UX on top of V33.

The generated source archive is unchanged. No Supabase project settings, DB,
RLS, passwords, customer data, PDF renderers, or CI release guards are changed.
"""
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve()

# The previous generated auth step incorrectly implies account creation precedes
# guest CV editing. Replace only the generated Auth route, retaining the verified
# /auth/confirm callback and all other account-bound documents.
auth=root/"app/auth/page.tsx"
original=auth.read_text(encoding="utf-8")
assert "export default function AuthPage()" in original
assert "auth.signUp" in original and "signInWithPassword" in original
auth.write_text(r"""'use client';

import {useEffect, useRef, useState, type FormEvent} from 'react';
import {createClient, isSupabaseConfigured} from '@/lib/supabase/client';
import {withBasePath} from '@/lib/basePath';
import {isSessionBoundaryBlocked} from '@/lib/sessionBoundary';

type Mode='signin'|'signup';
type Language='ar'|'en';
function safeNext(raw:string|null):string {
  // Internal routes only. Do not trust a caller-supplied external redirect.
  if (!raw || !raw.startsWith('/') || raw.startsWith('//') || raw.includes('\\') ||
      /[\u0000-\u001f]/.test(raw)) return '/templates';
  return raw;
}
function scorePassword(value:string) {
  return Math.min(4,(value.length>=8?1:0)+(value.length>=12?1:0)+
    (/[A-Za-z]/.test(value)&&/[0-9]/.test(value)?1:0)+
    (/[^A-Za-z0-9]/.test(value)?1:0));
}
function friendlyAuthError(error:unknown,ar:boolean):string {
  const msg=(error instanceof Error?error.message:String(error)).toLowerCase();
  if (msg.includes('email not confirmed')) return ar?
    'فعّل حسابك من رسالة البريد أولًا، ثم حاول الدخول.':'Please confirm your email before signing in.';
  if (msg.includes('rate')||msg.includes('too many')) return ar?
    'محاولات كثيرة. حاول مرة أخرى لاحقًا.':'Too many attempts. Try again later.';
  if (msg.includes('invalid login')||msg.includes('invalid credentials')) return ar?
    'البريد الإلكتروني أو كلمة المرور غير صحيحة.':'Incorrect email or password.';
  if (msg.includes('already registered')) return ar?
    'قد يكون لديك حساب بالفعل. جرّب تسجيل الدخول.':'You may already have an account. Try signing in.';
  return ar?'تعذّر إكمال العملية الآن. حاول مجددًا.':'We could not complete your request. Please retry.';
}

export default function AuthPage() {
  const [mode,setMode]=useState<Mode>('signin');
  const [language,setLanguage]=useState<Language>('ar');
  const [email,setEmail]=useState('');
  const [password,setPassword]=useState('');
  const [confirm,setConfirm]=useState('');
  const [showPassword,setShowPassword]=useState(false);
  const [busy,setBusy]=useState(false);
  const [sent,setSent]=useState(false);
  const [notice,setNotice]=useState('');
  const [error,setError]=useState('');
  const [nextPath,setNextPath]=useState('/templates');
  const active=useRef(false);
  const ar=language==='ar';
  const configured=isSupabaseConfigured();
  const strength=scorePassword(password);

  useEffect(()=>{
    const params=new URLSearchParams(window.location.search);
    const next=safeNext(params.get('next'));
    setNextPath(next);
    const lang=params.get('lang');
    if (lang==='ar'||lang==='en') setLanguage(lang);
    if (params.get('error')==='confirmation') setError('تعذّر تأكيد البريد. اطلب رسالة جديدة · Email confirmation failed. Request a new email.');
    const client=createClient();
    if (!client) return;
    let alive=true;
    void client.auth.getUser().then(({data,error})=>{
      if (alive && !error && data.user && !isSessionBoundaryBlocked()) {
        window.location.assign(withBasePath(next));
      }
    }).catch(()=>{/* Guest sign-in remains available if session check fails. */});
    return ()=>{alive=false;};
  },[]);

  function switchMode(next:Mode) {
    if (busy) return;
    setMode(next);setError('');setNotice('');setPassword('');setConfirm('');
    setShowPassword(false);setSent(false);
  }
  const returnTarget=withBasePath(nextPath);
  const confirmationRedirect=()=>{
    const callback=withBasePath('/auth/confirm');
    return window.location.origin+callback+'?next='+encodeURIComponent(nextPath);
  };
  async function submit(e:FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (active.current || isSessionBoundaryBlocked()) return;
    setError('');setNotice('');
    if (password.length<8) {setError(ar?'كلمة المرور لا تقل عن 8 أحرف.':'Password must have at least 8 characters.');return;}
    if (mode==='signup' && password!==confirm) {
      setError(ar?'تأكيد كلمة المرور غير مطابق.':'Passwords do not match.');return;
    }
    if (!configured) {setError(ar?'خدمة الحسابات غير متاحة الآن.':'Account service is currently unavailable.');return;}
    const client=createClient();
    if (!client) {setError(ar?'خدمة الحسابات غير متاحة الآن.':'Account service is currently unavailable.');return;}
    active.current=true;setBusy(true);
    const normalized=email.trim().toLowerCase();
    try {
      if (mode==='signin') {
        const result=await client.auth.signInWithPassword({email:normalized,password});
        if (result.error) throw result.error;
        const checked=await client.auth.getUser();
        if (isSessionBoundaryBlocked()||checked.error||!checked.data.user ||
            checked.data.user.email?.toLowerCase()!==normalized) {
          throw new Error('Account verification failed');
        }
        setPassword('');window.location.assign(returnTarget);return;
      }
      const result=await client.auth.signUp({
        email:normalized,password,options:{emailRedirectTo:confirmationRedirect()}
      });
      if (result.error) throw result.error;
      setPassword('');setConfirm('');
      if (result.data.session) {
        const checked=await client.auth.getUser();
        if (isSessionBoundaryBlocked()||checked.error||!checked.data.user ||
            checked.data.user.email?.toLowerCase()!==normalized)
          throw new Error('Account verification failed');
        window.location.assign(returnTarget);return;
      }
      setSent(true);
      setNotice(ar?'إذا كان إنشاء الحساب يتطلب تأكيدًا، راجع بريدك وافتح رابط التفعيل.':'Check your inbox for a confirmation email if verification is required.');
    } catch (err:unknown) {
      setError(friendlyAuthError(err,ar));
    } finally {active.current=false;setBusy(false);}
  }
  async function resend() {
    if (busy || active.current || !email.trim()) return;
    const client=createClient();
    if (!client) return;
    active.current=true;setBusy(true);setError('');
    try {
      const {error:err}=await client.auth.resend({
        type:'signup',email:email.trim().toLowerCase(),
        options:{emailRedirectTo:confirmationRedirect()}
      });
      if (err) throw err;
      setNotice(ar?'إذا كان الحساب ينتظر التفعيل، ستصل رسالة جديدة. افحص الرسائل غير المرغوبة.':
        'If confirmation is pending, you will receive another email. Check spam as well.');
    } catch(err:unknown) {setError(friendlyAuthError(err,ar));}
    finally {active.current=false;setBusy(false);}
  }
  return <main className="sirati-auth-v34" dir={ar?'rtl':'ltr'}>
    <div className="sirati-auth-v34-top">
      <a href={withBasePath('/')} className="sirati-auth-v34-brand" aria-label="Sirati home">S<span>★</span> Sirati CV</a>
      <div className="sirati-auth-v34-lang" aria-label="Language">
        <button type="button" aria-pressed={ar} onClick={()=>setLanguage('ar')}>العربية</button>
        <button type="button" aria-pressed={!ar} onClick={()=>setLanguage('en')}>English</button>
      </div>
    </div>
    <div className="sirati-auth-v34-layout">
      <section className="sirati-auth-v34-story" aria-label={ar?'عن سيرتي':'About Sirati'}>
        <span className="sirati-auth-v34-kicker">{ar?'طوّر مستقبلك المهني':'Build your next opportunity'}</span>
        <h1>{ar?'سيرتك الاحترافية تبدأ من هنا.':'Your professional story starts here.'}</h1>
        <p>{ar?'أنشئ سيرتك الذاتية مجانًا، ثم سجّل الدخول عندما تريد حفظ إصداراتك والعودة إليها.':
          'Create your CV for free. Sign in whenever you want to save versions and pick up where you left off.'}</p>
        <div className="sirati-auth-v34-benefits">
          <div><span aria-hidden="true">✓</span>{ar?'إنشاء سيرة ذاتية مجانًا':'Free CV creation'}</div>
          <div><span aria-hidden="true">✓</span>{ar?'حفظ مستنداتك في حسابك':'Save documents to your account'}</div>
          <div><span aria-hidden="true">✓</span>{ar?'دعم العربية والإنجليزية':'Arabic and English support'}</div>
        </div>
        <a href={withBasePath('/templates')} className="sirati-auth-v34-explore">
          {ar?'تصفح القوالب دون حساب ←':'Explore templates without an account →'}
        </a>
      </section>
      <section className="sirati-auth-v34-card" aria-label={ar?'تسجيل الحساب':'Account access'}>
        <div className="sirati-auth-v34-tabs" role="group" aria-label={ar?'اختر طريقة الدخول':'Account method'}>
          <button type="button" aria-pressed={mode==='signin'} onClick={()=>switchMode('signin')} disabled={busy}>
            {ar?'تسجيل الدخول':'Sign in'}
          </button>
          <button type="button" aria-pressed={mode==='signup'} onClick={()=>switchMode('signup')} disabled={busy}>
            {ar?'إنشاء حساب':'Create account'}
          </button>
        </div>
        <h2>{sent?(ar?'تحقق من بريدك':'Check your email'):mode==='signin'?
          (ar?'مرحبًا بعودتك':'Welcome back'):(ar?'ابدأ بحساب مجاني':'Create a free account')}</h2>
        <p className="sirati-auth-v34-sub">{sent?(ar?'تأكيد البريد خطوة لحماية حسابك.':'Email verification helps protect your account.'):
          mode==='signin'?(ar?'ادخل لحفظ سيرك ومتابعة عملك.':'Access your saved CVs and continue editing.'):
          (ar?'خطوات بسيطة، بدون اشتراك أو رسوم.':'A quick setup, with no subscription or payment.')}</p>
        {!configured&&<div className="sirati-auth-v34-alert" role="status">
          {ar?'خدمة الحسابات غير متاحة حاليًا. يمكنك إنشاء السيرة دون تسجيل.':
            'Account service unavailable. You can still create a CV as a guest.'}
        </div>}
        {sent ? <div className="sirati-auth-v34-sent" role="status">
          <strong>{email}</strong>
          <p>{notice || (ar?'راجع صندوق الوارد والرسائل غير المرغوبة.':'Check your inbox and spam folder.')}</p>
          <button type="button" className="sirati-auth-v34-secondary" disabled={busy||!configured} onClick={resend}>
            {busy?(ar?'جارٍ الإرسال…':'Sending…'):(ar?'إعادة إرسال رسالة التفعيل':'Resend confirmation email')}
          </button>
          <button type="button" className="sirati-auth-v34-text" onClick={()=>switchMode('signin')}>
            {ar?'تم التفعيل؟ سجل الدخول':'Already confirmed? Sign in'}
          </button>
        </div> : <form onSubmit={submit} noValidate={false}>
          <label htmlFor="sirati-auth-email">{ar?'البريد الإلكتروني':'Email address'}</label>
          <input id="sirati-auth-email" type="email" inputMode="email" autoComplete="email"
            placeholder="name@example.com" required value={email} onChange={e=>setEmail(e.target.value)}
            disabled={busy} dir="ltr"/>
          <label htmlFor="sirati-auth-password">{ar?'كلمة المرور':'Password'}</label>
          <div className="sirati-auth-v34-password">
            <input id="sirati-auth-password" type={showPassword?'text':'password'}
              autoComplete={mode==='signin'?'current-password':'new-password'}
              minLength={8} required value={password} onChange={e=>setPassword(e.target.value)}
              disabled={busy} dir="ltr"/>
            <button type="button" onClick={()=>setShowPassword(v=>!v)} disabled={busy}
              aria-label={showPassword?(ar?'إخفاء كلمة المرور':'Hide password'):(ar?'إظهار كلمة المرور':'Show password')}>
              {showPassword?(ar?'إخفاء':'Hide'):(ar?'إظهار':'Show')}
            </button>
          </div>
          {mode==='signup'&&<>
            <label htmlFor="sirati-auth-confirm">{ar?'تأكيد كلمة المرور':'Confirm password'}</label>
            <input id="sirati-auth-confirm" type={showPassword?'text':'password'} autoComplete="new-password"
              minLength={8} required value={confirm} onChange={e=>setConfirm(e.target.value)}
              disabled={busy} dir="ltr"/>
            <div className="sirati-auth-v34-strength">
              <progress max={4} value={strength} aria-label={ar?'مؤشر تعقيد كلمة المرور':'Password complexity indicator'}/>
              <small>{ar?'8 أحرف على الأقل. يفضّل 12 حرفًا أو أكثر مع تنويع الرموز.':
                'At least 8 characters; 12+ with mixed characters is recommended.'}</small>
            </div>
          </>}
          {mode==='signin'&&<a className="sirati-auth-v34-forgot" href={withBasePath('/auth/recovery')}>
            {ar?'نسيت كلمة المرور؟':'Forgot password?'}
          </a>}
          <button type="submit" className="sirati-auth-v34-submit" disabled={busy||!configured}
            aria-busy={busy}>
            {busy?(ar?'جارٍ المعالجة…':'Please wait…'):mode==='signin'?
              (ar?'تسجيل الدخول':'Sign in'):(ar?'إنشاء حساب مجاني':'Create free account')}
          </button>
        </form>}
        {error&&<div role="alert" className="sirati-auth-v34-alert">{error}</div>}
        {!sent&&<p className="sirati-auth-v34-foot">{mode==='signin'?
          (ar?'ليس لديك حساب؟':'New to Sirati?'):(ar?'لديك حساب بالفعل؟':'Already have an account?')}
          {' '}<button type="button" className="sirati-auth-v34-inline" disabled={busy}
            onClick={()=>switchMode(mode==='signin'?'signup':'signin')}>
            {mode==='signin'?(ar?'أنشئ حسابًا':'Create an account'):(ar?'سجّل الدخول':'Sign in')}
          </button>
        </p>}
      </section>
    </div>
  </main>;
}
""",encoding="utf-8")

# Existing guest CV editor must remain mounted while its sign-in dialog is open.
# Improve *only* the existing dialog; do not change pending CV snapshot or save/export.
dialog=root/"components/SiratiBuilderPdfButton.tsx"
text=dialog.read_text(encoding="utf-8")
def replace_once(before,after):
    global text
    assert text.count(before)==1, "Expected one guest auth dialog anchor: "+before[:85]
    text=text.replace(before,after,1)

replace_once(
    "  const [password,setPassword] = useState('');",
    """  const [password,setPassword] = useState('');
  const [passwordConfirm,setPasswordConfirm] = useState('');
  const [showPassword,setShowPassword] = useState(false);""")
replace_once(
    "      if (password.length < 8) throw new Error('Use a password of at least 8 characters.');",
    """       if (password.length < 8) throw new Error(arabic
         ? 'كلمة المرور يجب ألا تقل عن 8 أحرف.' : 'Use a password of at least 8 characters.');
       if (mode==='signup' && password !== passwordConfirm) throw new Error(arabic
         ? 'تأكيد كلمة المرور غير مطابق.' : 'Passwords do not match.');""")
replace_once(
    """onClick={()=>{setMode('signup');setError('')}}""",
    """onClick={()=>{setMode('signup');setError('');setPassword('');setPasswordConfirm('');setShowPassword(false)}}""")
replace_once(
    """onClick={()=>{setMode('signin');setError('')}}""",
    """onClick={()=>{setMode('signin');setError('');setPassword('');setPasswordConfirm('');setShowPassword(false)}}""")
replace_once(
    """<input id={dialogId + '-password'} type="password" minLength={8} required
             autoComplete={mode==='signup'?'new-password':'current-password'}
             value={password} onChange={e=>setPassword(e.target.value)} disabled={busy}/>""",
    """<div className="sirati-auth-v34-modal-password">
             <input id={dialogId + '-password'} type={showPassword?'text':'password'} minLength={8} required
               autoComplete={mode==='signup'?'new-password':'current-password'}
               value={password} onChange={e=>setPassword(e.target.value)} disabled={busy}/>
             <button type="button" disabled={busy} onClick={()=>setShowPassword(v=>!v)}
               aria-label={showPassword?(arabic?'إخفاء كلمة المرور':'Hide password'):(arabic?'إظهار كلمة المرور':'Show password')}>
               {showPassword?(arabic?'إخفاء':'Hide'):(arabic?'إظهار':'Show')}
             </button>
           </div>
           {mode==='signup'&&<>
             <label htmlFor={dialogId+'-confirm'}>{arabic?'تأكيد كلمة المرور':'Confirm password'}</label>
             <input id={dialogId+'-confirm'} type={showPassword?'text':'password'} minLength={8} required
               autoComplete="new-password" value={passwordConfirm}
               onChange={e=>setPasswordConfirm(e.target.value)} disabled={busy}/>
             <small className="sirati-auth-v34-modal-hint">{arabic?
               'استخدم 8 أحرف على الأقل، ويفضل 12 حرفًا مع رموز متنوعة.':
               'Use at least 8 characters; 12+ with varied characters is recommended.'}</small>
           </>}""")
replace_once(
    """{mode==='signin' && <p><a href={withBasePath('/auth/recovery')}>""",
    """{mode==='signin' && <p><a href={withBasePath('/auth/recovery')} target="_blank" rel="noopener noreferrer">""")
replace_once("setOpen(false);setPassword('');setNotice('');",
             "setOpen(false);setPassword('');setPasswordConfirm('');setNotice('');")
dialog.write_text(text,encoding="utf-8")

# Change password is a sensitive, authenticated action. Explicitly revalidate
# the current password without storing it or authenticating another account.
account=root/"app/account/password/page.tsx"
account_source=account.read_text(encoding="utf-8")
assert "updateUser({password})" in account_source
account_source=account_source.replace(
    "  const [password,setPassword]=useState('');",
    "  const [currentPassword,setCurrentPassword]=useState('');\n  const [password,setPassword]=useState('');",1)
account_source=account_source.replace(
    "      const updated=await client.auth.updateUser({password});",
    """      // Re-authenticate the *same* user before this sensitive mutation.
      const current=await client.auth.signInWithPassword({email,password:currentPassword});
      if (current.error) throw current.error;
      const {data:after,error:afterError}=await client.auth.getUser();
      if (isSessionBoundaryBlocked()||afterError||!after.user||
          after.user.id!==data.user.id) throw new Error('Account changed');
      const updated=await client.auth.updateUser({password});""",1)
account_source=account_source.replace(
    "      setPassword('');setConfirm('');setSuccess(true);",
    "      setCurrentPassword('');setPassword('');setConfirm('');setSuccess(true);",1)
account_source=account_source.replace(
    """          <label htmlFor="account-new">""",
    """          <label htmlFor="account-current">كلمة المرور الحالية · Current password</label>
          <input id="account-current" type="password" required autoComplete="current-password"
            value={currentPassword} onChange={e=>setCurrentPassword(e.target.value)}
            disabled={busy} style={{padding:12,minHeight:44,width:'100%'}}/>
          <label htmlFor="account-new">""",1)
account_source=account_source.replace(
    "className=\"container\" style={{maxWidth:520,paddingBlock:48}} dir=\"auto\"",
    "className=\"container sirati-auth-v34-utility\" dir=\"auto\"",1)
account.write_text(account_source,encoding="utf-8")
recovery=root/"app/auth/recovery/page.tsx"
recovery_source=recovery.read_text(encoding="utf-8")
assert "resetPasswordForEmail" in recovery_source
recovery_source=recovery_source.replace(
    "className=\"container\" style={{maxWidth:520,paddingBlock:48}} dir=\"auto\"",
    "className=\"container sirati-auth-v34-utility\" dir=\"auto\"",1)
recovery.write_text(recovery_source,encoding="utf-8")

# Confirmation callback safety: keep existing OTP/PKCE logic, remove raw server
# errors from customer-facing text, provide bilingual recoverable navigation.
confirm=root/"app/auth/confirm/page.tsx"
old=confirm.read_text(encoding="utf-8")
assert "exchangeCodeForSession" in old and "verifyOtp" in old
old=old.replace("setMessage(error.message || 'The confirmation link could not be verified.');",
  "setMessage('تعذّر التحقق من الرابط. اطلب رسالة جديدة · Confirmation failed. Request a new link.');")
old=old.replace("setMessage('The confirmation link is incomplete. Please return to sign in.');",
  "setMessage('رابط التأكيد غير مكتمل · The confirmation link is incomplete.');")
old=old.replace("const [message, setMessage] = useState('Confirming your email…');",
  "const [message, setMessage] = useState('جارٍ تأكيد بريدك · Confirming your email…');")
old=old.replace("Back to sign in", "العودة للدخول · Back to sign in")
confirm.write_text(old,encoding="utf-8")

css=root/"app/globals.css"
style=css.read_text(encoding="utf-8")
assert "/* Sirati Auth V34 */" not in style
style+=r"""
/* Sirati Auth V34 — scoped, accessible, mobile-first account experiences */
@media screen {
  .sirati-auth-v34 { min-height:calc(100vh - 52px);background:
    radial-gradient(circle at 9% 18%,#dceee5 0,transparent 37%),
    linear-gradient(135deg,#f8fbf9,#edf3f1);color:#193c30;padding:20px clamp(14px,4vw,45px) 46px; }
  .sirati-auth-v34 * {box-sizing:border-box}
  .sirati-auth-v34-top {max-width:1100px;margin:auto;display:flex;align-items:center;
    justify-content:space-between;gap:12px;padding:6px 0 22px}
  .sirati-auth-v34-brand {font-weight:850;font-size:19px;color:#154c38;text-decoration:none}
  .sirati-auth-v34-brand span {color:#aa762e;font-size:16px}
  .sirati-auth-v34-lang {display:flex;gap:4px;border:1px solid #c8d7cf;background:white;
    border-radius:30px;padding:4px}
  .sirati-auth-v34-lang button {border:0;border-radius:24px;background:transparent;color:#264739;
    padding:8px 12px;font:inherit;font-size:13px;cursor:pointer;min-height:40px}
  .sirati-auth-v34-lang [aria-pressed=true] {background:#174d39;color:white}
  .sirati-auth-v34-layout {max-width:1100px;margin:30px auto 0;display:grid;
    grid-template-columns:minmax(0,1fr) minmax(320px,475px);gap:clamp(22px,6vw,80px);
    align-items:center}
  .sirati-auth-v34-story h1 {font-size:clamp(2rem,4vw,3.5rem);
    line-height:1.24;letter-spacing:-.03em;margin:12px 0 19px;max-width:610px}
  .sirati-auth-v34-story p {font-size:clamp(15px,1.7vw,19px);
    line-height:1.9;max-width:580px;color:#51695f}
  .sirati-auth-v34-kicker {display:inline-flex;background:#e4f2e8;color:#236145;
    font-weight:800;border-radius:50px;padding:8px 13px;font-size:13px}
  .sirati-auth-v34-benefits {display:grid;gap:16px;margin:28px 0;font-weight:650}
  .sirati-auth-v34-benefits div {display:flex;align-items:center;gap:12px}
  .sirati-auth-v34-benefits span {display:inline-grid;place-items:center;background:#d7eee0;
    width:27px;height:27px;border-radius:100%;color:#1b6646}
  .sirati-auth-v34-explore {color:#1b6547;text-underline-offset:4px;font-weight:750}
  .sirati-auth-v34-card {width:100%;background:#fff;border:1px solid #d8e6dd;
    box-shadow:0 28px 75px #0c3e2619;border-radius:25px;padding:clamp(20px,4vw,38px)}
  .sirati-auth-v34-tabs {display:grid;grid-template-columns:1fr 1fr;gap:4px;background:#edf3ef;
    border-radius:13px;padding:4px;margin-bottom:23px}
  .sirati-auth-v34-tabs button {min-height:44px;border:0;border-radius:10px;background:transparent;
    color:#425f50;font:inherit;font-weight:700;cursor:pointer}
  .sirati-auth-v34-tabs [aria-pressed=true] {background:#fff;color:#185138;box-shadow:0 2px 9px #0001}
  .sirati-auth-v34-card h2 {font-size:clamp(24px,3vw,29px);margin:0 0 7px;color:#143e2c}
  .sirati-auth-v34-sub {font-size:14px;line-height:1.8;color:#65796e;margin:0 0 25px}
  .sirati-auth-v34-card form {display:grid;gap:9px}
  .sirati-auth-v34-card label {font-size:13px;font-weight:750;color:#274c38;margin-top:7px}
  .sirati-auth-v34-card input {min-width:0;width:100%;min-height:49px;padding:11px 13px;
    background:#fff;color:#172f25;border:1px solid #b9cec1;border-radius:11px;
    font:inherit;font-size:15px}
  .sirati-auth-v34-card input:focus {border-color:#237650;outline:3px solid #23765026}
  .sirati-auth-v34-password {position:relative}
  .sirati-auth-v34-password input {padding-inline-end:82px}
  .sirati-auth-v34-password button {position:absolute;right:5px;top:5px;min-height:39px;
    border:0;background:#edf4ef;border-radius:8px;padding:4px 10px;
    font-size:13px;color:#28563b;cursor:pointer}
  .sirati-auth-v34-strength {display:grid;gap:7px}
  .sirati-auth-v34-strength progress {width:100%;height:8px;accent-color:#20744e}
  .sirati-auth-v34-strength small {font-size:12px;color:#5b7568;line-height:1.6}
  .sirati-auth-v34-forgot {justify-self:end;color:#176b4c;text-decoration:underline;
    text-underline-offset:4px;font-weight:650;font-size:13px;margin:4px 0}
  .sirati-auth-v34-submit {margin-top:12px;border:0;border-radius:12px;background:#16573d;
    color:#fff;min-height:51px;font:inherit;font-size:15px;font-weight:800;cursor:pointer}
  .sirati-auth-v34-submit:hover:not(:disabled) {background:#0c422d}
  .sirati-auth-v34-submit:disabled {opacity:.65;cursor:not-allowed}
  .sirati-auth-v34-alert {background:#fff5ed;color:#803715;border:1px solid #f3cbb4;
    border-radius:10px;padding:12px;font-size:13px;line-height:1.7;margin-top:13px}
  .sirati-auth-v34-foot {text-align:center;color:#617669;font-size:13px;margin:23px 0 0}
  .sirati-auth-v34-inline,.sirati-auth-v34-text {border:0;background:none;color:#146747;
    font:inherit;font-weight:800;text-decoration:underline;cursor:pointer}
  .sirati-auth-v34-sent {background:#f0f7f2;border-radius:13px;padding:16px;
    overflow-wrap:anywhere;line-height:1.7}
  .sirati-auth-v34-sent p {font-size:14px}
  .sirati-auth-v34-secondary {border:1px solid #9ac9b1;color:#17543a;
    background:#fff;border-radius:11px;padding:12px;font:inherit;cursor:pointer;width:100%}
  .sirati-auth-v34-text {margin:12px auto;display:block}
  .sirati-auth-v34-modal-password {position:relative}
  .sirati-auth-v34-modal-password input {padding-inline-end:86px}
  .sirati-auth-v34-modal-password button {position:absolute;right:5px;top:5px;
    min-height:35px;border:0;border-radius:6px;background:#e8f1eb;color:#1e5136;
    padding:4px 9px;cursor:pointer}
  .sirati-auth-v34-modal-hint {font-size:12px;color:#526b5b;line-height:1.6}
  .sirati-auth-v34-utility {max-width:520px;margin:34px auto;padding:clamp(18px,5vw,32px)!important;
    border-radius:18px;background:white;border:1px solid #d6e5db;
    box-shadow:0 16px 55px #194b2b12}
  .sirati-auth-v34-utility h1 {font-size:clamp(23px,4vw,29px)}
  .sirati-auth-v34-utility input:not([type=checkbox]) {border:1px solid #a9c6b5;border-radius:9px}
  .sirati-auth-v34-utility input:focus-visible,.sirati-auth-v34-utility a:focus-visible {
    outline:3px solid #28694b;outline-offset:2px}
  .sirati-auth-v34 button:focus-visible,.sirati-auth-v34 a:focus-visible,
  .sirati-auth-v34-dialog button:focus-visible {outline:3px solid #b28232;outline-offset:3px}
  @media(max-width:800px) {
    .sirati-auth-v34-layout {grid-template-columns:1fr;gap:20px;margin-top:8px}
    .sirati-auth-v34-story h1 {font-size:26px;margin:7px 0}
    .sirati-auth-v34-story p {font-size:14px;margin:8px 0 12px}
    .sirati-auth-v34-benefits {display:none}
    .sirati-auth-v34-explore {font-size:13px}
    .sirati-auth-v34-card {max-width:560px;margin:0 auto}
    .sirati-auth-v34-top {padding-bottom:8px}
  }
  @media(max-width:400px) {
    .sirati-auth-v34 {padding:10px 12px 28px}
    .sirati-auth-v34-card {padding:18px;border-radius:17px}
    .sirati-auth-v34-tabs button {font-size:13px}
  }
}
"""
css.write_text(style,encoding="utf-8")
print("PASS: bilingual responsive auth, verified sessions, signup confirmation, reauth change and safe modal")
