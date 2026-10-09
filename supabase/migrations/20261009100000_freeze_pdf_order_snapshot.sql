-- Issue #41 — DRAFT ONLY. NOT APPLIED TO STAGING OR PRODUCTION.
-- Product rule: EGP 50 buys ONE fixed CV revision, repeat downloads permitted.
-- Deleting the parent CV deletes the order and its frozen snapshot via CASCADE.
-- A visible UI warning before CV deletion must be implemented separately.
--
-- IMPORTANT: historical PDF orders deliberately receive NO snapshot.
-- Never backfill a legacy order from a potentially edited current CV.
-- Apply only after owner authorization, code review, backups, and staging preflight.
BEGIN;

-- Fail closed if the P0 pending/EGP 50 guard is absent; do not weaken #26.
DO $preflight$
BEGIN
  IF NOT (SELECT relrowsecurity FROM pg_class
          WHERE oid = 'public.pdf_orders'::regclass) THEN
    RAISE EXCEPTION 'Issue 41: PDF order RLS must already be enabled';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies
    WHERE schemaname = 'public' AND tablename = 'pdf_orders'
      AND policyname = 'Customer PDF orders require pending status and fixed price'
      AND permissive = 'RESTRICTIVE' AND cmd = 'INSERT'
  ) THEN
    RAISE EXCEPTION 'Issue 41: pending/EGP 50 RESTRICTIVE guard is required';
  END IF;
END;
$preflight$;

-- Server-issued opaque revision, changed even by stale writes or forged tokens.
ALTER TABLE public.cv_documents ADD COLUMN revision uuid NOT NULL
  DEFAULT gen_random_uuid();
ALTER TABLE public.pdf_orders ADD COLUMN expected_revision uuid;
-- Legacy orders deliberately remain NULL/unbound. One active entitlement per revision.
CREATE UNIQUE INDEX sirati_pdf_order_active_revision
  ON public.pdf_orders (document_id, expected_revision)
  WHERE expected_revision IS NOT NULL AND status IN ('pending', 'approved');

-- Separate non-exposed schema: do NOT expose this schema in Supabase Data API.
-- CREATE (without IF NOT EXISTS) intentionally aborts on a conflicting schema.
CREATE SCHEMA sirati_private;
REVOKE ALL ON SCHEMA sirati_private FROM PUBLIC, anon, authenticated;
GRANT USAGE ON SCHEMA sirati_private TO service_role;

-- Snapshot is NOT another client-writable cv_versions row.
-- ON DELETE CASCADE: deleting cv_documents deletes pdf_orders and then snapshot.
CREATE TABLE sirati_private.pdf_order_snapshots (
  order_id uuid PRIMARY KEY
    REFERENCES public.pdf_orders (id) ON DELETE CASCADE,
  owner_user_id uuid NOT NULL,
  source_document_id uuid NOT NULL,
  source_revision uuid NOT NULL,
  snapshot_data jsonb NOT NULL,
  snapshot_template text NOT NULL,
  snapshot_language text NOT NULL,
  source_updated_at timestamptz NOT NULL,
  frozen_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
  snapshot_schema_version integer NOT NULL DEFAULT 1
    CHECK (snapshot_schema_version = 1)
);

ALTER TABLE sirati_private.pdf_order_snapshots ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON TABLE sirati_private.pdf_order_snapshots
  FROM PUBLIC, anon, authenticated, service_role;
-- Trusted server may only read snapshots after independently verifying user/order.
GRANT SELECT ON TABLE sirati_private.pdf_order_snapshots TO service_role;
-- No PUBLIC/authenticated RLS policy: customers cannot read or modify snapshots.

-- Invoker trigger always overwrites any client-supplied revision.
CREATE FUNCTION sirati_private.advance_cv_revision()
RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path = ''
AS $revision$
BEGIN
  NEW.revision := pg_catalog.gen_random_uuid();
  RETURN NEW;
END;
$revision$;
REVOKE ALL ON FUNCTION sirati_private.advance_cv_revision()
  FROM PUBLIC, anon, authenticated, service_role;
CREATE TRIGGER sirati_cv_revision_before_write
BEFORE INSERT OR UPDATE ON public.cv_documents
FOR EACH ROW EXECUTE FUNCTION sirati_private.advance_cv_revision();

-- Trusted reviewers may change status, never move an order to another revision/owner.
CREATE FUNCTION sirati_private.protect_pdf_order_binding()
RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path = ''
AS $binding$
BEGIN
  IF ROW(NEW.id, NEW.user_id, NEW.document_id, NEW.expected_revision)
     IS DISTINCT FROM ROW(OLD.id, OLD.user_id, OLD.document_id, OLD.expected_revision) THEN
    RAISE EXCEPTION 'Paid PDF order revision binding is immutable' USING ERRCODE = '23514';
  END IF;
  RETURN NEW;
END;
$binding$;
REVOKE ALL ON FUNCTION sirati_private.protect_pdf_order_binding()
  FROM PUBLIC, anon, authenticated, service_role;
CREATE TRIGGER sirati_pdf_order_binding_before_update
BEFORE UPDATE ON public.pdf_orders
FOR EACH ROW EXECUTE FUNCTION sirati_private.protect_pdf_order_binding();

-- Defense in depth: approval cannot rewrite even a privileged server's snapshot.
CREATE FUNCTION sirati_private.reject_snapshot_update()
RETURNS trigger LANGUAGE plpgsql SECURITY INVOKER SET search_path = ''
AS $immutable$
BEGIN
  RAISE EXCEPTION 'Paid PDF snapshot is immutable' USING ERRCODE = '23514';
END;
$immutable$;
REVOKE ALL ON FUNCTION sirati_private.reject_snapshot_update()
  FROM PUBLIC, anon, authenticated, service_role;
CREATE TRIGGER sirati_snapshot_no_update
BEFORE UPDATE ON sirati_private.pdf_order_snapshots
FOR EACH ROW EXECUTE FUNCTION sirati_private.reject_snapshot_update();

-- Trigger runs inside the original order INSERT transaction.
-- Caller cannot supply snapshot content, approved status, or a version ID.
-- Invoker cannot execute this function directly through Data API.
CREATE FUNCTION sirati_private.capture_pdf_order_snapshot()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $capture$
DECLARE
  v_document public.cv_documents%ROWTYPE;
  v_claim_user_id uuid;
BEGIN
  IF TG_OP <> 'INSERT' OR TG_TABLE_SCHEMA <> 'public'
     OR TG_TABLE_NAME <> 'pdf_orders' THEN
    RAISE EXCEPTION 'Unexpected snapshot trigger context';
  END IF;

  IF NEW.status IS DISTINCT FROM 'pending'
     OR NEW.amount_egp IS DISTINCT FROM 50
     OR NEW.reviewed_at IS NOT NULL THEN
    RAISE EXCEPTION 'Only pending PDF orders at EGP 50 may be snapshotted'
      USING ERRCODE = '23514';
  END IF;

  -- JWT owner check when invoked as an authenticated end-user.
  -- RLS ownership policy remains the primary authorization on pdf_orders.
  v_claim_user_id := auth.uid();
  IF v_claim_user_id IS NOT NULL AND
     NEW.user_id IS DISTINCT FROM v_claim_user_id THEN
    RAISE EXCEPTION 'PDF order owner does not match authenticated user'
      USING ERRCODE = '42501';
  END IF;

  -- Lock the persisted revision through transaction COMMIT: no concurrent edit
  -- or deletion can change the captured values halfway through INSERT.
  SELECT d.* INTO v_document
    FROM public.cv_documents AS d
    WHERE d.id = NEW.document_id
    FOR SHARE;
  IF NOT FOUND OR v_document.user_id IS DISTINCT FROM NEW.user_id THEN
    RAISE EXCEPTION 'PDF order document is missing or belongs to another owner'
      USING ERRCODE = '42501';
  END IF;

  -- PT409 is PostgREST's explicit HTTP 409 custom SQLSTATE. Raising aborts
  -- the INSERT and all its effects, including the AFTER trigger snapshot.
  IF NEW.expected_revision IS NULL OR
     NEW.expected_revision IS DISTINCT FROM v_document.revision THEN
    RAISE EXCEPTION 'CV revision conflict: review and save the current CV before retrying'
      USING ERRCODE = 'PT409';
  END IF;

  INSERT INTO sirati_private.pdf_order_snapshots (
    order_id, owner_user_id, source_document_id, source_revision,
    snapshot_data, snapshot_template, snapshot_language,
    source_updated_at
  ) VALUES (
    NEW.id, NEW.user_id, NEW.document_id, v_document.revision,
    v_document.data, v_document.template, v_document.language,
    v_document.updated_at
  );

  RETURN NEW;
END;
$capture$;

REVOKE ALL ON FUNCTION sirati_private.capture_pdf_order_snapshot()
  FROM PUBLIC, anon, authenticated, service_role;

CREATE TRIGGER sirati_pdf_order_snapshot_after_insert
AFTER INSERT ON public.pdf_orders
FOR EACH ROW
EXECUTE FUNCTION sirati_private.capture_pdf_order_snapshot();

-- No UPDATE/DELETE on historical orders, no data backfill, no UI deployment.
COMMIT;

