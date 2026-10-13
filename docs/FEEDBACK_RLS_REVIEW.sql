-- Sirati feedback V2 — proposed database change, REVIEW/STAGING FIRST.
-- NOT APPLIED by this PR. Do not run on Production without owner consent,
-- staging A/B tests, independent security acceptance and backup.
-- Use Supabase CLI migration new sirati_site_feedback_rls when available,
-- copy this reviewed SQL into that CLI-generated migration.

begin;
create table if not exists public.sirati_site_feedback (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null unique references auth.users(id) on delete cascade,
  rating smallint not null check (rating between 1 and 5),
  category text not null default 'overall' check
    (category in ('overall', 'templates', 'editing', 'pdf', 'mobile')),
  comment text not null default '' check (char_length(comment) <= 400),
  created_at timestamptz not null default now()
);
create index if not exists sirati_site_feedback_recent_idx
  on public.sirati_site_feedback (created_at desc);
alter table public.sirati_site_feedback enable row level security;

-- No public reads or anonymous writes; user revises only their own review.
-- Owner status is trusted only in server-controlled app_metadata, not user_metadata.
revoke all on table public.sirati_site_feedback from public, anon, authenticated;
grant select on public.sirati_site_feedback to authenticated;
grant insert (user_id, rating, category, comment)
  on public.sirati_site_feedback to authenticated;
grant update (rating, category, comment)
  on public.sirati_site_feedback to authenticated;

create policy "feedback_read_own_or_owner"
  on public.sirati_site_feedback for select to authenticated
  using (
    user_id = (select auth.uid())
    or (
      (select auth.uid()) is not null
      and (select auth.jwt() -> 'app_metadata' ->> 'sirati_feedback_admin') = 'true'
    )
  );
create policy "feedback_write_own"
  on public.sirati_site_feedback for insert to authenticated
  with check (
    user_id = (select auth.uid())
    and coalesce((select auth.jwt() ->> 'is_anonymous'), 'false') = 'false'
  );
create policy "feedback_edit_own"
  on public.sirati_site_feedback for update to authenticated
  using (user_id = (select auth.uid()))
  with check (
    user_id = (select auth.uid())
    and coalesce((select auth.jwt() ->> 'is_anonymous'), 'false') = 'false'
  );
commit;

-- REQUIRED STAGING ACCEPTANCE (SYNTHETIC ACCOUNTS ONLY):
-- anon cannot insert/select; anonymous-auth cannot insert.
-- A can insert/update own unique review, cannot change user_id/created_at.
-- B cannot read/update A, cannot impersonate A via user_id.
-- Owner test user receives trusted app_metadata {"sirati_feedback_admin": true}
-- through an approved ADMIN operation and can read all rows.
-- User-editable user_metadata must not authorize dashboard access.
-- Invalid ratings/overlength comments fail; UI must not claim success.
-- Review a retention policy and one-account-per-user spam limitation.
