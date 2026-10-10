-- Sirati Account Save/Restore + Data Isolation regression test.
-- Safe to run against a test/staging or controlled project.
-- All test data is rolled back.
--
-- Covers:
-- 1) own CV insert/update
-- 2) cross-user read/update/delete isolation
-- 3) cross-owner CV insert rejection
-- 4) version insert ownership enforcement
-- 5) PDF-order ownership enforcement
-- 6) version numbering + retention of latest 30 versions

begin;

insert into auth.users (id, email) values
  ('11111111-1111-4111-8111-111111111111', 'sirati-qa-a@example.invalid'),
  ('22222222-2222-4222-8222-222222222222', 'sirati-qa-b@example.invalid');

insert into public.cv_documents
  (id, user_id, title, language, template, data)
values
  ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',
   '22222222-2222-4222-8222-222222222222',
   'B private CV',
   'en',
   'modern',
   '{"fullName":"RLS B"}'::jsonb);

create temp table qa_results (
  name text primary key,
  passed boolean not null,
  detail text
) on commit drop;

grant insert, select on qa_results to authenticated;

set local role authenticated;
set local request.jwt.claim.sub = '11111111-1111-4111-8111-111111111111';

with ins as (
  insert into public.cv_documents
    (id, user_id, title, language, template, data)
  values
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
     '11111111-1111-4111-8111-111111111111',
     'A private CV',
     'en',
     'compact-ats',
     '{"fullName":"QA A"}'::jsonb)
  returning 1
)
insert into qa_results
select 'own_document_insert', count(*) = 1, 'inserted rows=' || count(*) from ins;

with upd as (
  update public.cv_documents
  set title='A updated CV', data='{"fullName":"QA A Updated"}'::jsonb
  where id='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
  returning 1
)
insert into qa_results
select 'own_document_update', count(*) = 1, 'updated rows=' || count(*) from upd;

insert into qa_results
select 'other_document_hidden',
       count(*) = 0,
       'visible rows=' || count(*)
from public.cv_documents
where id='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';

with upd as (
  update public.cv_documents
  set title='SHOULD NOT CHANGE'
  where id='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'
  returning 1
)
insert into qa_results
select 'cross_document_update_blocked', count(*) = 0, 'updated rows=' || count(*) from upd;

with del as (
  delete from public.cv_documents
  where id='bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb'
  returning 1
)
insert into qa_results
select 'cross_document_delete_blocked', count(*) = 0, 'deleted rows=' || count(*) from del;

do $$
begin
  begin
    insert into public.cv_documents
      (id, user_id, title, language, template, data)
    values
      ('cccccccc-cccc-4ccc-8ccc-cccccccccccc',
       '22222222-2222-4222-8222-222222222222',
       'malicious',
       'en',
       'modern',
       '{}'::jsonb);

    insert into qa_results values
      ('cross_owner_insert_blocked', false, 'unexpected insert success');
  exception when insufficient_privilege then
    insert into qa_results values
      ('cross_owner_insert_blocked', true, 'RLS rejected insert');
  end;
end $$;

with ins as (
  insert into public.cv_versions
    (document_id, user_id, data, template, language)
  values
    ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
     '11111111-1111-4111-8111-111111111111',
     '{"fullName":"QA A Updated"}'::jsonb,
     'compact-ats',
     'en')
  returning 1
)
insert into qa_results
select 'own_version_insert', count(*) = 1, 'inserted rows=' || count(*) from ins;

do $$
begin
  begin
    insert into public.cv_versions
      (document_id, user_id, data, template, language)
    values
      ('bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',
       '11111111-1111-4111-8111-111111111111',
       '{}'::jsonb,
       'modern',
       'en');

    insert into qa_results values
      ('cross_document_version_blocked', false, 'unexpected version insert success');
  exception when insufficient_privilege then
    insert into qa_results values
      ('cross_document_version_blocked', true, 'RLS rejected version insert');
  end;
end $$;

with ins as (
  insert into public.pdf_orders
    (user_id, document_id, amount_egp, payment_method, payment_reference, status)
  values
    ('11111111-1111-4111-8111-111111111111',
     'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
     50,
     'instapay',
     'QA-A',
     'pending')
  returning 1
)
insert into qa_results
select 'own_pdf_order_insert', count(*) = 1, 'inserted rows=' || count(*) from ins;

do $$
begin
  begin
    insert into public.pdf_orders
      (user_id, document_id, amount_egp, payment_method, payment_reference, status)
    values
      ('11111111-1111-4111-8111-111111111111',
       'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',
       50,
       'instapay',
       'QA-X',
       'pending');

    insert into qa_results values
      ('cross_document_pdf_order_blocked', false, 'unexpected order insert success');
  exception when insufficient_privilege then
    insert into qa_results values
      ('cross_document_pdf_order_blocked', true, 'RLS rejected PDF order');
  end;
end $$;

-- P0-SEC-PDF-01 (#26): the customer role must not approve or discount
-- a PDF order or provide a fabricated review timestamp on INSERT.
-- The positive pending/EGP 50 order is tested above.
insert into qa_results
select 'pdf_order_restrictive_guard_present',
       count(*) = 1,
       'restrictive policies=' || count(*)
from pg_policies
where schemaname = 'public'
  and tablename = 'pdf_orders'
  and policyname = 'Customer PDF orders require pending status and fixed price'
  and permissive = 'RESTRICTIVE'
  and cmd = 'INSERT';

do $$
begin
  begin
    insert into public.pdf_orders
      (user_id, document_id, amount_egp, payment_method, payment_reference, status)
    values
      ('11111111-1111-4111-8111-111111111111',
       'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
       50, 'instapay', 'QA-APPROVED', 'approved');

    insert into qa_results values
      ('pdf_order_self_approval_blocked', false, 'approved INSERT unexpectedly succeeded');
  exception when insufficient_privilege then
    insert into qa_results values
      ('pdf_order_self_approval_blocked', true, 'RLS denied approved INSERT');
  end;

  begin
    insert into public.pdf_orders
      (user_id, document_id, amount_egp, payment_method, payment_reference, status)
    values
      ('11111111-1111-4111-8111-111111111111',
       'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
       1, 'instapay', 'QA-DISCOUNT', 'pending');

    insert into qa_results values
      ('pdf_order_price_tampering_blocked', false, 'altered-price INSERT unexpectedly succeeded');
  exception when insufficient_privilege then
    insert into qa_results values
      ('pdf_order_price_tampering_blocked', true, 'RLS denied altered-price INSERT');
  end;

  begin
    insert into public.pdf_orders
      (user_id, document_id, amount_egp, payment_method, payment_reference, status, reviewed_at)
    values
      ('11111111-1111-4111-8111-111111111111',
       'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
       50, 'instapay', 'QA-REVIEWED', 'pending', now());

    insert into qa_results values
      ('pdf_order_fake_review_blocked', false, 'reviewed_at INSERT unexpectedly succeeded');
  exception when insufficient_privilege then
    insert into qa_results values
      ('pdf_order_fake_review_blocked', true, 'RLS denied reviewed_at INSERT');
  end;

  begin
    insert into public.pdf_orders
      (user_id, document_id, amount_egp, payment_method, payment_reference, status)
    values
      ('11111111-1111-4111-8111-111111111111',
       'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
       50, 'instapay', 'QA-REJECTED', 'rejected');

    insert into qa_results values
      ('pdf_order_self_rejection_blocked', false, 'rejected INSERT unexpectedly succeeded');
  exception when insufficient_privilege then
    insert into qa_results values
      ('pdf_order_self_rejection_blocked', true, 'RLS denied rejected INSERT');
  end;
end $$;

insert into public.cv_versions (document_id,user_id,data,template,language)
select
  'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'::uuid,
  '11111111-1111-4111-8111-111111111111'::uuid,
  jsonb_build_object('save', g),
  'modern',
  'en'
from generate_series(1,30) as g;

insert into qa_results
select
  'version_retention_latest_30',
  count(*) = 30 and min(version_number) = 2 and max(version_number) = 31,
  'count=' || count(*) || ', min=' || min(version_number) || ', max=' || max(version_number)
from public.cv_versions
where document_id='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';

set local request.jwt.claim.sub = '22222222-2222-4222-8222-222222222222';

insert into qa_results
select 'user_b_cannot_see_user_a',
       count(*) = 0,
       'visible rows=' || count(*)
from public.cv_documents
where id='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';

reset role;

do $$
begin
  if exists (select 1 from qa_results where not passed) then
    raise exception 'Sirati RLS QA failed: %',
      (select string_agg(name || ': ' || coalesce(detail,''), '; ')
       from qa_results where not passed);
  end if;
end $$;

select name, passed, detail
from qa_results
order by name;

rollback;
