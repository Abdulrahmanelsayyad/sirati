#!/usr/bin/env python3
"""Issue #41 branch-only Builder/Library compatibility patch for frozen paid CVs.

No live customer operations, SQL writes, payment approvals, or deployment.
Applied to reconstructed source AFTER the normal Sirati presentation patches.
Fail closed on unexpected source changes.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
builder_path = root / "app/builder/page.tsx"
documents_path = root / "app/documents/page.tsx"
builder = builder_path.read_text(encoding="utf-8")
documents = documents_path.read_text(encoding="utf-8")


def replace_once(value: str, before: str, after: str, label: str) -> str:
    if value.count(before) != 1:
        raise SystemExit(f"FAIL Issue #41 {label}: expected one anchor; found {value.count(before)}")
    return value.replace(before, after, 1)


def replace_between(value: str, first: str, last: str, update: str, label: str) -> str:
    if value.count(first) != 1 or value.count(last) != 1:
        raise SystemExit(f"FAIL Issue #41 {label}: unexpected function anchors")
    begin, end = value.index(first), value.index(last)
    if begin >= end:
        raise SystemExit(f"FAIL Issue #41 {label}: out-of-order anchors")
    return value[:begin] + update + value[end:]


builder = replace_once(
    builder,
    "  const cloudReadyRef = useRef(false);",
    """  const cloudReadyRef = useRef(false);
  const autosaveTimerRef = useRef<number | null>(null);
  const cloudSaveQueueRef = useRef<Promise<void>>(Promise.resolve());
  const paymentSubmittingRef = useRef(false);
  const [paymentSubmitting, setPaymentSubmitting] = useState(false);
  const [pdfOrders, setPdfOrders] = useState<Array<{
    id: string;
    status: 'pending' | 'approved' | 'rejected';
    requested_at: string;
    amount_egp: number;
  }>>([]);
  const draftFingerprint = JSON.stringify({ data, template, language });
  const latestDraftFingerprintRef = useRef(draftFingerprint);
  latestDraftFingerprintRef.current = draftFingerprint;

  function queueCloudSave<T>(work: () => Promise<T>): Promise<T> {
    const queued = cloudSaveQueueRef.current.then(work, work);
    cloudSaveQueueRef.current = queued.then(() => undefined, () => undefined);
    return queued;
  }""",
    "state and save queue",
)

builder = replace_between(
    builder,
    "  useEffect(() => {\n    if (!hydrated || !cloudReadyRef.current || !documentId || !userId || cloudLoading) return;",
    "  async function refreshVersions(id: string) {",
    """  useEffect(() => {
    if (!hydrated || !cloudReadyRef.current || !documentId || !userId || cloudLoading ||
        paymentSubmittingRef.current) return;
    const supabase = createClient();
    if (!supabase) return;

    const timer = window.setTimeout(() => {
      autosaveTimerRef.current = null;
      void queueCloudSave(async () => {
        // A pending payment snapshots only the awaited explicit save, never a stale debounce.
        if (paymentSubmittingRef.current) return;
        setCloudStatus('Saving...');
        const { error } = await supabase!
          .from('cv_documents')
          .update({ title: documentTitle(data), data, template, language })
          .eq('id', documentId);
        setCloudStatus(error ? `Cloud save failed: ${error.message}` : 'Saved to account');
      });
    }, 1200);
    autosaveTimerRef.current = timer;
    return () => {
      window.clearTimeout(timer);
      if (autosaveTimerRef.current === timer) autosaveTimerRef.current = null;
    };
  }, [data, template, language, hydrated, documentId, userId, cloudLoading]);

""",
    "serialized autosave",
)

builder = replace_between(
    builder,
    "  async function refreshPdfOrder(id: string) {",
    "  async function saveToAccount(createVersion = true) {",
    """  async function refreshPdfOrder(id: string) {
    const supabase = createClient();
    if (!supabase) return;
    // Status listing only. NEVER use document-level approval to authorize current preview.
    const { data: rows, error } = await supabase
      .from('pdf_orders')
      .select('id,status,requested_at,amount_egp')
      .eq('document_id', id)
      .order('requested_at', { ascending: false })
      .limit(30);
    if (error) {
      setOrderMessage('Could not refresh order history. Try again.');
      return;
    }
    const orders = (rows ?? []) as Array<{
      id: string; status: 'pending' | 'approved' | 'rejected';
      requested_at: string; amount_egp: number;
    }>;
    setPdfOrders(orders);
    setPdfOrderStatus(orders[0]?.status ?? 'none');
  }

  async function requestCleanPdf() {
    // A fast second tap cannot create a second paid order.
    if (paymentSubmittingRef.current) return;
    setOrderMessage('');
    if (!paymentReference.trim()) {
      setOrderMessage('Enter your payment transaction reference before submitting.');
      return;
    }

    paymentSubmittingRef.current = true;
    setPaymentSubmitting(true);
    const draftAtStart = latestDraftFingerprintRef.current;
    try {
      if (autosaveTimerRef.current !== null) {
        window.clearTimeout(autosaveTimerRef.current);
        autosaveTimerRef.current = null;
      }

      // CRITICAL: save both NEW and EXISTING CVs before a pending paid order.
      // queueCloudSave serializes with any autosave already in flight.
      const id = await saveToAccount(false);
      if (!id) {
        setOrderMessage('Could not save the CV. No payment order was created.');
        return;
      }
      if (latestDraftFingerprintRef.current !== draftAtStart) {
        setOrderMessage('Your CV changed during saving. Review your edits and try again; no payment order was created.');
        return;
      }

      const supabase = createClient();
      if (!supabase) {
        setOrderMessage('Account storage is unavailable. No order was created.');
        return;
      }
      let activeUserId = userId;
      if (!activeUserId) {
        const { data: userData } = await supabase!.auth.getUser();
        activeUserId = userData.user?.id ?? null;
      }
      if (!activeUserId) {
        setOrderMessage('Sign in to submit a payment reference.');
        return;
      }

      // Staging migration, when separately approved, will freeze the persisted CV
      // inside this INSERT transaction. Legacy orders remain unbound.
      const { error } = await supabase
        .from('pdf_orders')
        .insert({
          user_id: activeUserId, document_id: id, amount_egp: 50,
          payment_method: paymentMethod, payment_reference: paymentReference.trim(),
          status: 'pending'
        });
      if (error) {
        setOrderMessage(error.message);
        return;
      }
      setPdfOrderStatus('pending');
      setOrderMessage('Payment reference submitted for one saved CV revision. Approval does not unlock later edits.');
      await refreshPdfOrder(id);
    } catch {
      setOrderMessage('Save or order submission was interrupted. Check your orders before trying again.');
    } finally {
      paymentSubmittingRef.current = false;
      setPaymentSubmitting(false);
    }
  }

""",
    "payment request and per-order history",
)

builder = replace_once(
    builder,
    """      const { error } = await supabase
        .from('cv_documents')
        .update({ title: documentTitle(data), data, template, language })
        .eq('id', id);
      if (error) {
        setCloudStatus(`Cloud save failed: ${error.message}`);
        return null;
      }""",
    """      const { data: saved, error } = await queueCloudSave(async () =>
        await supabase!
          .from('cv_documents')
          .update({ title: documentTitle(data), data, template, language })
          .eq('id', id)
          .select('id')
          .single()
      );
      if (error || !saved) {
        setCloudStatus(`Cloud save failed: ${error?.message || 'Document not found'}`);
        return null;
      }""",
    "awaited existing CV update",
)

# Hide no payment history: old approved payments NEVER unlock mutable preview.
builder = replace_once(
    builder,
    "{pdfOrderStatus !== 'approved' && (",
    "{(",
    "allow requests for new revisions after older approved orders",
)

builder = replace_once(
    builder,
    """<div className={`notice review-notice ${pdfOrderStatus === 'approved' ? 'success-notice' : ''}`}>""",
    """<div className="notice review-notice">""",
    "payment status banner",
)

start = builder.index("                {pdfOrderStatus === 'approved'", builder.index('<div className="notice review-notice">'))
stop = builder.index("\n              </div>", start)
builder = builder[:start] + """                {pdfOrderStatus === 'approved'
                  ? 'A previous PDF order was approved for a fixed revision. Your current editable preview remains watermarked; official frozen PDF delivery is not live yet.'
                  : pdfOrderStatus === 'pending'
                    ? 'Your latest payment request is pending review. Only its saved revision can later be issued as a clean PDF.'
                    : pdfOrderStatus === 'rejected'
                      ? 'Your latest payment request was not approved. You may submit another reference for this saved revision.'
                      : 'Watermarked preview is free. Each clean PDF order (EGP 50) is for one fixed saved revision.'}""" + builder[stop:]

builder = replace_once(
    builder,
    '<button type="button" className="btn btn-primary" onClick={requestCleanPdf}>',
    '<button type="button" className="btn btn-primary" onClick={requestCleanPdf} disabled={paymentSubmitting}>',
    "disable duplicate payment tap",
)
builder = replace_once(
    builder,
    'onClick={requestCleanPdf} disabled={paymentSubmitting}>Submit payment reference</button>',
    "onClick={requestCleanPdf} disabled={paymentSubmitting}>{paymentSubmitting ? 'Saving CV before order...' : 'Submit payment reference'}</button>",
    "payment in progress label",
)

# Record status of each order; no false download button until trusted renderer exists.
anchor = """              <div className="review-actions">
                <button type="button" className="btn btn-primary btn-lg" onClick={() => saveToAccount(true)}>"""
if builder.count(anchor) != 1:
    raise SystemExit("FAIL Issue #41: review actions anchor changed")
builder = builder.replace(
    anchor,
    """              <section className="manual-payment-card" aria-label="Saved PDF order history">
                <strong>Paid PDF copies — one fixed revision per EGP 50</strong>
                <p className="small">Approval is specific to its saved revision, never to all edits of this CV. Secure repeat downloading is not enabled yet.</p>
                {pdfOrders.length === 0 ? (
                  <p className="small">No payment orders found for this CV.</p>
                ) : (
                  <ul className="small">
                    {pdfOrders.map(order => (
                      <li key={order.id}>
                        {order.status === 'approved'
                          ? 'Approved order (fixed revision) — secure PDF download pending launch'
                          : order.status === 'pending'
                            ? 'Payment request pending review'
                            : 'Payment request rejected'}
                        {' — EGP '}{order.amount_egp}
                        {' — order '}{order.id.slice(0, 8)}
                      </li>
                    ))}
                  </ul>
                )}
              </section>

""" + anchor,
    1,
)
# Never authorize clean browser printing using a previously approved order.
builder = replace_once(
    builder,
    """{pdfOrderStatus === 'approved' ? 'Save clean PDF' : 'Print watermarked preview'}""",
    """{'Print watermarked preview'}""",
    "print never claims clean paid download",
)
builder = replace_once(
    builder,
    """watermarked={pdfOrderStatus !== 'approved'}""",
    """watermarked={true}""",
    "preview remains watermarked pending trusted server delivery",
)

# Clear order history if a different CV is opened or a new draft starts.
builder = replace_once(
    builder,
    """  async function refreshPdfOrder(id: string) {
    const supabase""",
    """  async function refreshPdfOrder(id: string) {
    setPdfOrders([]);
    const supabase""",
    "refresh per-document order history",
)

# Documents delete: clear Arabic warning with deliberate confirmation and no double submit.
documents = replace_once(
    documents,
    "  const [message, setMessage] = useState('');",
    """  const [message, setMessage] = useState('');
  const [deletingId, setDeletingId] = useState<string | null>(null);""",
    "deletion state",
)
documents = replace_between(
    documents,
    "  async function removeDocument(id: string) {",
    "  async function signOut() {",
    """  async function removeDocument(id: string) {
    if (deletingId !== null) return;
    const doc = documents.find(item => item.id === id);
    if (!doc) return;
    const warning = [
      'تأكيد الحذف النهائي',
      '',
      `السيرة الذاتية: ${doc.title}`,
      '',
      'حذف هذه السيرة سيحذف أيضًا طلبات الـPDF وكل النسخ المدفوعة المحفوظة معها.',
      'لن تستطيع تحميل النسخ المدفوعة مرة أخرى من Sirati بعد الحذف.',
      'الملفات التي حمّلتها سابقًا على جهازك لن تُحذف تلقائيًا.',
      '',
      'هل تريد حذف السيرة ونسخها المدفوعة نهائيًا؟'
    ].join('\\n');
    if (!window.confirm(warning)) return;

    const supabase = createClient();
    if (!supabase) return;
    setDeletingId(id);
    try {
      const { error } = await supabase
        .from('cv_documents')
        .delete()
        .eq('id', id);
      if (error) {
        setMessage(error.message);
        return;
      }
      setDocuments(prev => prev.filter(item => item.id !== id));
      setMessage('');
    } finally {
      setDeletingId(null);
    }
  }

""",
    "paid deletion confirmation",
)
documents = replace_once(
    documents,
    """<button className="btn btn-secondary danger-text" onClick={() => removeDocument(doc.id)}>Delete</button>""",
    """<button className="btn btn-secondary danger-text" disabled={deletingId !== null} onClick={() => removeDocument(doc.id)}>{deletingId === doc.id ? 'Deleting...' : 'Delete'}</button>""",
    "prevent duplicate deletion",
)

builder_path.write_text(builder, encoding="utf-8")
documents_path.write_text(documents, encoding="utf-8")
print("PASS Issue #41: serialized save-before-order, fixed-version order history, watermarked preview, explicit paid-delete warning")
