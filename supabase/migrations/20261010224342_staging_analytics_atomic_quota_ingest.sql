-- Sirati Analytics Issue #87/#99: safer quota ordering and atomic admission.
-- Applied to Sirati-Staging only as migration 20261010224342.
-- DO NOT apply to Production or merge without release approval.
-- Sitewide cap checked before creating per-session quota allocations.
-- Nested EXCEPTION rolls back all increments when a request is rejected.
-- Duplicate-event races do not consume extra quota.
CREATE OR REPLACE FUNCTION public.sirati_track_event(p_session uuid, p_event uuid, p_type text, p_route text)
 RETURNS boolean
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO ''
AS $function$
DECLARE
  v_day date := (now() AT TIME ZONE 'UTC')::date;
  v_count integer;
  v_inserted integer;
BEGIN
  IF p_session IS NULL OR p_event IS NULL
     OR p_type IS NULL OR p_route IS NULL
     OR p_type NOT IN ('page_view','signup_completed','builder_started',
                       'cv_created','cv_saved','pdf_export_succeeded')
     OR p_route NOT IN ('/','/auth','/templates','/builder',
                        '/documents','/career-tools','/profile','/other')
  THEN RETURN false; END IF;

  IF p_type <> 'page_view' AND auth.uid() IS NULL THEN
    RETURN false;
  END IF;

  IF EXISTS(SELECT 1 FROM sirati_metrics.events WHERE event_id=p_event) THEN
    RETURN true;
  END IF;

  BEGIN
    -- A reject at the site-wide limit must not create a session quota row.
    INSERT INTO sirati_metrics.day_quota(event_day,calls)
      VALUES(v_day,1)
    ON CONFLICT (event_day) DO UPDATE
      SET calls = sirati_metrics.day_quota.calls + 1
      WHERE sirati_metrics.day_quota.calls < 15000
    RETURNING calls INTO v_count;
    IF v_count IS NULL THEN
      RAISE EXCEPTION 'analytics event quota exhausted'
        USING ERRCODE='A9001';
    END IF;

    v_count := NULL;
    INSERT INTO sirati_metrics.session_quota(session_id,event_day,calls)
      VALUES(p_session,v_day,1)
    ON CONFLICT(session_id,event_day) DO UPDATE
      SET calls=sirati_metrics.session_quota.calls+1
      WHERE sirati_metrics.session_quota.calls<80
    RETURNING calls INTO v_count;
    IF v_count IS NULL THEN
      RAISE EXCEPTION 'analytics session quota exhausted'
        USING ERRCODE='A9001';
    END IF;

    INSERT INTO sirati_metrics.events(event_id,session_id,event_type,route)
      VALUES(p_event,p_session,p_type,p_route)
      ON CONFLICT(event_id) DO NOTHING;
    GET DIAGNOSTICS v_inserted = ROW_COUNT;
    IF v_inserted=0 THEN
      RAISE EXCEPTION 'analytics duplicate event retry'
        USING ERRCODE='A9002';
    END IF;
  EXCEPTION
    WHEN SQLSTATE 'A9001' THEN RETURN false;
    WHEN SQLSTATE 'A9002' THEN RETURN true;
  END;
  RETURN true;
END;
$function$


REVOKE ALL ON FUNCTION public.sirati_track_event(uuid,uuid,text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.sirati_track_event(uuid,uuid,text,text)
 TO anon, authenticated;
