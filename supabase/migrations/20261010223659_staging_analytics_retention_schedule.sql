-- Sirati Analytics #87/#99: STAGING-ONLY 35d event / 2d quota retention.
-- Applied only to Sirati-Staging by migration 20261010223659.
-- DO NOT apply to Production or merge before separate owner release approval.
-- No payments, authentication records, CVs or user profiles are modified.

DO $preflight$
BEGIN
  IF to_regclass('sirati_metrics.events') IS NULL OR
     to_regclass('sirati_metrics.session_quota') IS NULL OR
     to_regclass('sirati_metrics.day_quota') IS NULL
  THEN
    RAISE EXCEPTION 'Analytics tables missing; refusing retention activation';
  END IF;
END;
$preflight$;

CREATE EXTENSION IF NOT EXISTS pg_cron WITH SCHEMA pg_catalog;
GRANT USAGE ON SCHEMA cron TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA cron TO postgres;

CREATE OR REPLACE FUNCTION sirati_metrics.cleanup_expired_events()
RETURNS void LANGUAGE plpgsql SECURITY INVOKER
SET search_path = ''
AS $function$
BEGIN
  DELETE FROM sirati_metrics.events
    WHERE occurred_at < now() - INTERVAL '35 days';
  DELETE FROM sirati_metrics.session_quota
    WHERE event_day < ((now() AT TIME ZONE 'UTC')::date - 2);
  DELETE FROM sirati_metrics.day_quota
    WHERE event_day < ((now() AT TIME ZONE 'UTC')::date - 2);
END
$function$;

REVOKE ALL ON FUNCTION sirati_metrics.cleanup_expired_events()
  FROM PUBLIC, anon, authenticated;

-- 02:12 UTC/GMT, daily. Changes to Production require independent approval.
SELECT cron.schedule(
  'sirati-analytics-retention-staging',
  '12 2 * * *',
  'SELECT sirati_metrics.cleanup_expired_events();'
);

-- Staging verified: pg_cron installed, scheduler running, exact active job
-- registered; manual function invocation on synthetic rows passed in a
-- rolled-back transaction. Automatic job execution is NOT YET OBSERVED.
