-- Sirati #87: minimal first-party interaction events (STAGING first).
-- No visitor IP, user-agent, email, job title, CV body, or browser fingerprint.
-- Anonymous sessions are NOT unique people; events are client-reported.
create schema if not exists sirati_metrics;
revoke all on schema sirati_metrics from public, anon, authenticated;

create table if not exists sirati_metrics.events (
  event_id uuid primary key,
  session_id uuid not null,
  event_type text not null check (event_type in (
    'page_view','signup_completed','builder_started','cv_created',
    'cv_saved','pdf_export_succeeded')),
  route text not null check (route in (
    '/','/auth','/templates','/builder','/documents',
    '/career-tools','/profile','/other')),
  occurred_at timestamptz not null default now()
);
create index if not exists sirati_events_time_idx
  on sirati_metrics.events (occurred_at desc);
create index if not exists sirati_events_session_idx
  on sirati_metrics.events (session_id, occurred_at desc);
alter table sirati_metrics.events enable row level security;

create table if not exists sirati_metrics.session_quota (
  session_id uuid not null, event_day date not null,
  calls integer not null check (calls between 1 and 80),
  primary key (session_id, event_day)
);
create table if not exists sirati_metrics.day_quota (
  event_day date primary key,
  calls integer not null check (calls between 1 and 15000)
);
create table if not exists sirati_metrics.admin_users (
  user_id uuid primary key
);
alter table sirati_metrics.session_quota enable row level security;
alter table sirati_metrics.day_quota enable row level security;
alter table sirati_metrics.admin_users enable row level security;
revoke all on all tables in schema sirati_metrics from public, anon, authenticated;

-- Public *ingest* only. Row data and admin aggregate access remain private.
-- Per-session/day and global/day budgets guard accidental event storms.
-- Abuse-resistant identity proof for truly anonymous visitors is impossible.
create or replace function public.sirati_track_event(
  p_session uuid, p_event uuid, p_type text, p_route text
) returns boolean language plpgsql security definer
set search_path = ''
as $$
declare
  v_day date := (now() at time zone 'UTC')::date;
  v_count integer;
begin
  if p_session is null or p_event is null
     or p_type is null or p_route is null
     or p_type not in ('page_view','signup_completed','builder_started',
                      'cv_created','cv_saved','pdf_export_succeeded')
     or p_route not in ('/','/auth','/templates','/builder',
                       '/documents','/career-tools','/profile','/other')
  then return false; end if;
  if p_type <> 'page_view' and auth.uid() is null then
    return false;
  end if;
  if exists (select 1 from sirati_metrics.events where event_id=p_event) then
    return true; -- retry is idempotent
  end if;

  insert into sirati_metrics.session_quota(session_id,event_day,calls)
    values (p_session,v_day,1)
    on conflict (session_id,event_day) do update
      set calls=sirati_metrics.session_quota.calls+1
      where sirati_metrics.session_quota.calls<80
    returning calls into v_count;
  if v_count is null then return false; end if;

  v_count := null;
  insert into sirati_metrics.day_quota(event_day,calls)
    values (v_day,1)
    on conflict (event_day) do update
      set calls=sirati_metrics.day_quota.calls+1
      where sirati_metrics.day_quota.calls<15000
    returning calls into v_count;
  if v_count is null then return false; end if;

  insert into sirati_metrics.events(event_id,session_id,event_type,route)
    values (p_event,p_session,p_type,p_route)
    on conflict (event_id) do nothing;
  return true;
end;
$$;
revoke all on function public.sirati_track_event(uuid,uuid,text,text) from public;
grant execute on function public.sirati_track_event(uuid,uuid,text,text)
  to anon, authenticated;

-- Dashboard aggregate: access is checked INSIDE privileged code.
-- Provision authorized admin UUID via protected server-side operation,
-- never in public source / client metadata.
create or replace function public.sirati_analytics_summary(p_days integer default 7)
returns jsonb language plpgsql security definer
set search_path = ''
as $$
declare
  v_since timestamptz;
  v_result jsonb;
begin
  if auth.uid() is null or not exists (
    select 1 from sirati_metrics.admin_users where user_id=auth.uid()
  ) then
    raise exception 'analytics access denied' using errcode='42501';
  end if;
  if p_days not in (1,7,30) then
    raise exception 'unsupported reporting window' using errcode='22023';
  end if;
  v_since := now() - make_interval(days=>p_days);

  select jsonb_build_object(
    'days', p_days,
    'registered_accounts', (select count(*) from auth.users
      where deleted_at is null and coalesce(is_anonymous,false)=false),
    'cv_creators', (select count(distinct user_id) from public.cv_documents),
    'saved_cvs', (select count(*) from public.cv_documents),
    'page_views', (select count(*) from sirati_metrics.events
      where event_type='page_view' and occurred_at>=v_since),
    'estimated_sessions', (select count(distinct session_id)
      from sirati_metrics.events where occurred_at>=v_since),
    'builder_starts', (select count(*) from sirati_metrics.events
      where event_type='builder_started' and occurred_at>=v_since),
    'cv_creation_events', (select count(*) from sirati_metrics.events
      where event_type='cv_created' and occurred_at>=v_since),
    'cv_save_events', (select count(*) from sirati_metrics.events
      where event_type='cv_saved' and occurred_at>=v_since),
    'pdf_export_events', (select count(*) from sirati_metrics.events
      where event_type='pdf_export_succeeded' and occurred_at>=v_since),
    'daily', coalesce((
      select jsonb_agg(jsonb_build_object(
        'date', day, 'views', views, 'sessions', sessions) order by day)
      from (
        select (occurred_at at time zone 'UTC')::date as day,
          count(*) filter (where event_type='page_view') as views,
          count(distinct session_id) as sessions
        from sirati_metrics.events where occurred_at>=v_since
        group by 1
      ) d
    ), '[]'::jsonb)
  ) into v_result;
  return v_result;
end;
$$;
revoke all on function public.sirati_analytics_summary(integer) from public, anon;
grant execute on function public.sirati_analytics_summary(integer) to authenticated;
