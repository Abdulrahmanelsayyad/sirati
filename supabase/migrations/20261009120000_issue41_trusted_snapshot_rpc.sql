-- Issue #41: BRANCH-ONLY DRAFT. NOT APPLIED TO ANY DATABASE.
-- Needs an explicit staging-only authorization, schema/history preflight,
-- independent security review, and backup before execution.
-- Uses the existing private snapshot table from #42. NEVER expose that schema
-- in the Supabase Data API. Legacy/unbound orders fail closed.
BEGIN;

DO $preflight$
BEGIN
  IF to_regclass('sirati_private.pdf_order_snapshots') IS NULL
     OR to_regclass('public.pdf_orders') IS NULL
     OR to_regclass('public.cv_documents') IS NULL THEN
    RAISE EXCEPTION 'Issue #42 atomic snapshot schema required';
  END IF;
  IF NOT EXISTS (
    SELECT 1 FROM pg_attribute
    WHERE attrelid = 'public.pdf_orders'::regclass
      AND attname = 'expected_revision' AND NOT attisdropped
  ) THEN
    RAISE EXCEPTION 'Issue #42 expected_revision required';
  END IF;
END;
$preflight$;

-- Callable only with a trusted server-side service_role key.
-- The caller must first verify the end-user JWT with Supabase Auth.
-- An account ID sent directly by a browser is NEVER sufficient.
-- SECURITY DEFINER has a fixed empty search path and no dynamic SQL.
CREATE FUNCTION public.sirati_pdf_snapshot_for_server(
  p_order_id uuid,
  p_user_id uuid
) RETURNS jsonb
LANGUAGE plpgsql VOLATILE SECURITY DEFINER
SET search_path = ''
AS $fn$
DECLARE
  v_result jsonb;
BEGIN
  IF p_order_id IS NULL OR p_user_id IS NULL THEN
    RETURN NULL;
  END IF;

  SELECT pg_catalog.jsonb_build_object(
    'order_id', o.id,
    'owner_user_id', o.user_id,
    'source_document_id', s.source_document_id,
    'source_revision', s.source_revision,
    'expected_revision', o.expected_revision,
    'snapshot_schema_version', s.snapshot_schema_version,
    'snapshot_data', s.snapshot_data,
    'snapshot_template', s.snapshot_template,
    'snapshot_language', s.snapshot_language
  ) INTO v_result
  FROM public.pdf_orders AS o
  INNER JOIN public.cv_documents AS d
    ON d.id = o.document_id AND d.user_id = o.user_id
  INNER JOIN sirati_private.pdf_order_snapshots AS s
    ON s.order_id = o.id
  WHERE o.id = p_order_id
    AND o.user_id = p_user_id
    AND o.status = 'approved'
    AND o.amount_egp = 50
    AND o.reviewed_at IS NOT NULL
    AND o.expected_revision IS NOT NULL
    AND s.owner_user_id = o.user_id
    AND s.source_document_id = o.document_id
    AND s.source_revision = o.expected_revision
    AND s.snapshot_schema_version = 1
    AND pg_catalog.octet_length(s.snapshot_data::text) <= 131072
  FOR SHARE OF o, d, s;

  -- Returning NULL denies absent, deleted, cross-user, pending, rejected,
  -- legacy, revoked, or inconsistent orders. Nothing is synthesized.
  RETURN v_result;
END;
$fn$;

-- No browser/authenticated/anonymous role can call the public RPC.
-- Entire DDL is transactional: no committed window of PUBLIC EXECUTE.
REVOKE ALL ON FUNCTION public.sirati_pdf_snapshot_for_server(uuid, uuid)
  FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION public.sirati_pdf_snapshot_for_server(uuid, uuid)
  TO service_role;

COMMIT;
