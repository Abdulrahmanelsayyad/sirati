"""Owner-requested Builder flow: rating -> existing auth -> saved review -> PDF.
No auth configuration, database schema, PDF renderer or Save CV changes.
"""
from pathlib import Path
import sys
p = Path(sys.argv[1]) / 'components/SiratiBuilderPdfButton.tsx'
s = p.read_text()
def replace(old, new):
    global s
    if s.count(old) != 1:
        raise RuntimeError('PDF rating gate anchor changed: ' + old[:80])
    s = s.replace(old, new, 1)
replace("  data: CvData; template: TemplateName; language: string;", "  data: CvData; template: TemplateName; language: string; rating?: number;")
replace("  const [open,setOpen] = useState(false);", """  const [open,setOpen] = useState(false);
  const [reviewStep,setReviewStep] = useState(false);
  const [rating,setRating] = useState(0);
  const ratingRef = useRef(0);""")
replace('    firstField.current?.focus();', """    if (reviewStep) dialogRef.current?.querySelector<HTMLButtonElement>('[data-rating]')?.focus();
    else firstField.current?.focus();""")
replace('  }, [open,busy]);', '  }, [open,busy,reviewStep]);')
replace('  async function exportWithFeedback() {', """  async function hasReview(client: NonNullable<ReturnType<typeof createClient>>, id: string) {
    const {data: review, error: reviewError} = await client.from('sirati_site_feedback')
      .select('rating').eq('user_id', id).maybeSingle();
    if (reviewError) throw new Error('Could not check your rating. Please retry; your CV is unchanged.');
    return Boolean(review && Number.isInteger(review.rating) && review.rating >= 1 && review.rating <= 5);
  }

  async function saveRatingBeforePdf() {
    const client = createClient();
    if (!client) throw new Error('Account service unavailable.');
    const {data: auth, error: authError} = await client.auth.getUser();
    if (authError || !auth.user || isSessionBoundaryBlocked()) throw new Error('Please sign in again.');
    if (!await hasReview(client, auth.user.id)) {
      const pending = readTransfer();
      const value = ratingRef.current || (pending?.requested && pending.action !== 'save' &&
        pending.email === auth.user.email?.toLowerCase() ? pending.rating : 0);
      if (!Number.isInteger(value) || !value || value < 1 || value > 5) {
        setReviewStep(true); setOpen(true);
        return false;
      }
      // Ignore conflicts: never replace an existing review/comment from another tab.
      const {error: writeError} = await client.from('sirati_site_feedback').upsert({
        user_id: auth.user.id, rating: value, category: 'overall', comment: ''
      }, {onConflict: 'user_id', ignoreDuplicates: true});
      if (writeError || !await hasReview(client, auth.user.id))
        throw new Error('Your rating was not saved. Please retry; your CV is unchanged.');
    }
    const {data: current, error: currentError} = await client.auth.getUser();
    if (currentError || current.user?.id !== auth.user.id || isSessionBoundaryBlocked())
      throw new Error('Account changed. Reopen your CV before downloading.');
    return true;
  }

  async function exportWithFeedback() {""")
# Keep review failures distinct from PDF render failures and reopen a retryable review step.
replace('''    try {
      if (!saving) {
        const warning = pdfJoinedScriptWarning(data, arabic);''', '''    if (!saving) {
      try { if (!await saveRatingBeforePdf()) return; }
      catch (e) { setReviewStep(true); setOpen(true); throw e; }
    }
    try {
      if (!saving) {
        const warning = pdfJoinedScriptWarning(data, arabic);''')
replace('      await exportCurrentSheet();', '      await exportCurrentSheet();\n      if (!saving) setOpen(false);')
replace('  async function begin() {', '  async function begin(reviewSubmitted = false) {')
replace('''        onAuthenticated(result.data.user.id, result.data.user.email || null);
        await exportWithFeedback();''', '''        onAuthenticated(result.data.user.id, result.data.user.email || null);
        if (!saving && !reviewSubmitted && !await hasReview(client!, result.data.user.id)) {
          setReviewStep(true); setOpen(true); return;
        }
        await exportWithFeedback();''')
replace('''      // Preserve exact editable CV, language, template and photo data in this tab.
      storeTransfer''', '''      if (!saving && !reviewSubmitted) {
        setReviewStep(true); setOpen(true); return;
      }
      if (!saving && (!Number.isInteger(ratingRef.current) || ratingRef.current < 1 || ratingRef.current > 5)) return;
      // Preserve exact editable CV, language, template and photo data in this tab.
      storeTransfer''')
replace('''        data,template,language});''', '''        data,template,language,...(!saving ? {rating:ratingRef.current} : {})});
      setReviewStep(false);''')
replace('aria-busy={busy} onClick={begin}', 'aria-busy={busy} onClick={()=>void begin()}')
replace('''        <h2 id={dialogId}>''', '''        {reviewStep && !saving ? <>
          <h2 id={dialogId}>{arabic?'قيّم تجربتك قبل تنزيل PDF':'Rate your experience before downloading'}</h2>
          <p>{arabic?'اختر تقييمك الصادق من نجمة إلى خمس نجوم، ثم سجّل الدخول لحفظه وتنزيل سيرتك مجانًا.':'Choose an honest rating from 1 to 5 stars, then sign in to save it and download your free PDF.'}</p>
          <div className="sirati-feedback-v2__stars" role="group" aria-label="Rating">
            {[1,2,3,4,5].map(value=><button key={value} data-rating type="button"
              disabled={busy} aria-label={value+' of 5 stars'} aria-pressed={rating===value}
              className={value<=rating?'selected':''}
              onClick={()=>{ratingRef.current=value;setRating(value);setError('');}}><span aria-hidden="true">★</span></button>)}
          </div>
          <p aria-live="polite">{rating ? `${rating} / 5` : (arabic?'اختر تقييمًا للمتابعة':'Choose a rating to continue')}</p>
          <button type="button" className="btn btn-primary" disabled={busy || !rating}
            onClick={()=>void begin(true)}>{busy?'Please wait…':(arabic?'حفظ التقييم ومتابعة':'Save rating and continue')}</button>
          {error&&<p role="alert" className="sirati-pdf-error">{error}</p>}
          <button type="button" className="sirati-pdf-auth-cancel" disabled={busy} onClick={cancel}>
            {arabic?'العودة للتعديل':'Back to editing'}</button>
        </> : <>
        <h2 id={dialogId}>''')
replace('''      </section>
    </div>}''', '''        </>}
      </section>
    </div>}''')
p.write_text(s)
print('Applied rating-before-auth Builder PDF flow; existing reviews and Save CV preserved.')
