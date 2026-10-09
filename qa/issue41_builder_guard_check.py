#!/usr/bin/env python3
"""Static regression gate on the ACTUAL reconstructed/prepared Sirati source.

This does not replace browser E2E, live Supabase QA or independent review.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
builder = (root / "app/builder/page.tsx").read_text(encoding="utf-8")
docs = (root / "app/documents/page.tsx").read_text(encoding="utf-8")


def require(expression: bool, label: str) -> None:
    if not expression:
        raise SystemExit(f"FAIL Issue #41: {label}")
    print(f"PASS Issue #41: {label}")


start = builder.index("  async function requestCleanPdf() {")
end = builder.index("  async function saveToAccount(createVersion = true, captureRevision?: (revision: string) => void) {", start)
request = builder[start:end]

require(request.count("await saveToAccount(false, revision => { expectedRevision = revision; })") == 1,
        "EVERY order requires awaited persisted CV save")
require("if (!id || !expectedRevision)" in request and request.index("await saveToAccount(false, revision => { expectedRevision = revision; })") <
        request.index("if (!id || !expectedRevision)") < request.index(".from('pdf_orders')"),
        "payment order blocked on save failure")
require("if (!documentId)" not in request,
        "existing CV is saved before order too")
require(request.index("latestDraftFingerprintRef.current !== draftAtStart") <
        request.index(".from('pdf_orders')"),
        "edit-during-save rejected before order INSERT")
require("paymentSubmittingRef.current = true" in request and
        "paymentSubmittingRef.current = false" in request,
        "payment guard set and released in finally")
require(request.index(".from('pdf_orders')") > request.index("await saveToAccount(false, revision => { expectedRevision = revision; })"),
        "pending order inserted after save only")
require("queueCloudSave(async () =>" in builder and
        "const { data: saved, error } = await queueCloudSave" in builder,
        "autosave and explicit save share a serialization queue")
require(".select('id,revision')\n          .single()" in builder,
        "existing CV save confirms a row was really persisted")

require(".select('id,status,requested_at,amount_egp')" in builder and
        "pdfOrders.map(order =>" in builder,
        "order history is tracked by distinct order IDs")
require("watermarked={true}" in builder and
        "watermarked={pdfOrderStatus !== 'approved'}" not in builder,
        "old approved payment cannot remove current-preview watermark")
require("Secure repeat downloading is not enabled yet." in builder and
        "onClick={() => window.print()}>{'Print watermarked preview'}</button>" in builder,
        "UI does not promise insecure browser-side paid PDF")
require("disabled={paymentSubmitting}" in builder,
        "duplicate payment submission disabled during save/order")

require("النسخ المدفوعة" in docs and "لن تستطيع تحميل النسخ المدفوعة" in docs,
        "Arabic delete warning clearly describes purchased-copy loss")
require("if (!window.confirm(warning)) return;" in docs and
        ".from('cv_documents')\n        .delete()" in docs,
        "destructive deletion requires warning before actual delete")
require("disabled={deletingId !== null}" in docs,
        "document Delete button disabled during deletion")
print("PASS Issue #41: prepared Builder and Documents source guard checks")


require("expected_revision: expectedRevision" in request and "error.code === 'PT409'" in request,
        "order carries exact save revision and shows conflict without retry")
require("captureRevision?.(created.revision as string)" in builder and
        "captureRevision?.(saved.revision as string)" in builder,
        "new and existing saves capture returned server revision")
