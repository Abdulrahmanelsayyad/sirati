-- Synthetic PostgreSQL 17 staging schema for GitHub issue #26.
-- No Supabase production connection, accounts, tokens, or customer data.
-- Reproduces only the production metadata relevant to public.pdf_orders.
create role authenticated nologin;
create role anon nologin;
create role service_role nologin bypassrls;

create schema auth;
create function auth.uid() returns uuid
language sql stable as $fn$
  select nullif(current_setting('request.jwt.claim.sub', true), '')::uuid;
$fn$;

grant usage on schema auth to authenticated;
grant execute on function auth.uid() to authenticated;

create table public.cv_documents (
  id uuid primary key,
  user_id uuid not null
);
create table public.pdf_orders (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  document_id uuid not null references public.cv_documents(id),
  amount_egp integer not null default 50 check (amount_egp > 0),
  payment_method text not null check (payment_method in ('instapay','vodafone_cash','other')),
  payment_reference text not null,
  status text not null default 'pending' check (status in ('pending','approved','rejected')),
  note text,
  requested_at timestamptz not null default now(),
  reviewed_at timestamptz
);

alter table public.cv_documents enable row level security;
alter table public.pdf_orders enable row level security;

create policy "Users view own CV documents"
on public.cv_documents for select to authenticated
using ((select auth.uid()) = user_id);

create policy "Users request PDF for own document"
on public.pdf_orders for insert to authenticated
with check (
  ((select auth.uid()) = user_id)
  and exists (
    select 1 from public.cv_documents d
    where d.id = pdf_orders.document_id
    and d.user_id = (select auth.uid())
  )
);
create policy "Users view own PDF orders"
on public.pdf_orders for select to authenticated
using ((select auth.uid()) = user_id);

grant select on public.cv_documents to authenticated;
grant select, insert on public.pdf_orders to authenticated;
grant select, insert, update on public.pdf_orders to service_role;

insert into public.cv_documents(id,user_id) values
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','11111111-1111-4111-8111-111111111111'),
  ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb','22222222-2222-4222-8222-222222222222');
