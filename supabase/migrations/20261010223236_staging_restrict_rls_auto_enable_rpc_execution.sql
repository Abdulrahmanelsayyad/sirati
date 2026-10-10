-- Sirati Analytics Issue #99: Stage-verified SECURITY DEFINER trigger ACL fix.
-- Applied to Supabase Sirati-Staging via migration
-- 20261010223236_staging_restrict_rls_auto_enable_rpc_execution.
-- DO NOT APPLY TO PRODUCTION without an additional explicit owner approval
-- and independent Security/QA sign-off.
-- This does not alter tracking, RLS policies, data, billing, or jobs.
DO $preflight$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_event_trigger e
    WHERE e.evtname = 'ensure_rls'
      AND e.evtfoid = 'public.rls_auto_enable()'::regprocedure
      AND e.evtenabled IN ('O', 'A')
  ) THEN
    RAISE EXCEPTION 'Expected enabled ensure_rls event trigger is absent';
  END IF;
END;
$preflight$;

REVOKE EXECUTE ON FUNCTION public.rls_auto_enable()
  FROM PUBLIC, anon, authenticated;

-- Staging verification already completed:
-- anon EXECUTE = false, authenticated EXECUTE = false;
-- active ensure_rls event trigger auto-enabled RLS on a synthetic
-- public table within a rolled-back test transaction.
-- Reversal, only with explicit approval:
-- GRANT EXECUTE ON FUNCTION public.rls_auto_enable()
--   TO PUBLIC, anon, authenticated;
