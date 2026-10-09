-- Real PostgreSQL RLS DML checks, run ONLY on synthetic CI database.
-- Applies the exact proposed migration before executing these tests.
begin;

set local role authenticated;
set local request.jwt.claim.sub = '11111111-1111-4111-8111-111111111111';

insert into public.pdf_orders
  (user_id,document_id,payment_method,payment_reference,status,amount_egp)
values
  ('11111111-1111-4111-8111-111111111111',
   'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
   'instapay','CI-LEGIT','pending',50);

do $qa$
declare
  v_count integer;
begin
  select count(*) into v_count from public.pdf_orders where payment_reference='CI-LEGIT';
  if v_count <> 1 then
    raise exception 'FAIL: legitimate pending 50 EGP request was not visible to its owner';
  end if;
  raise notice 'PASS: legitimate pending 50 EGP customer INSERT';

  begin
    insert into public.pdf_orders
      (user_id,document_id,payment_method,payment_reference,status,amount_egp)
    values
      ('11111111-1111-4111-8111-111111111111',
       'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
       'instapay','CI-APPROVED','approved',50);
    raise exception 'FAIL: user self-approved PDF order';
  exception when insufficient_privilege then
    raise notice 'PASS: self approval blocked by RLS';
  end;

  begin
    insert into public.pdf_orders
      (user_id,document_id,payment_method,payment_reference,status,amount_egp)
    values
      ('11111111-1111-4111-8111-111111111111',
       'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
       'instapay','CI-DISCOUNT','pending',1);
    raise exception 'FAIL: user discounted PDF order';
  exception when insufficient_privilege then
    raise notice 'PASS: altered price blocked by RLS';
  end;

  begin
    insert into public.pdf_orders
      (user_id,document_id,payment_method,payment_reference,status,amount_egp)
    values
      ('11111111-1111-4111-8111-111111111111',
       'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
       'instapay','CI-UPCHARGE','pending',100);
    raise exception 'FAIL: user upcharged PDF order';
  exception when insufficient_privilege then
    raise notice 'PASS: altered higher price blocked';
  end;

  begin
    insert into public.pdf_orders
      (user_id,document_id,payment_method,payment_reference,status,amount_egp,reviewed_at)
    values
      ('11111111-1111-4111-8111-111111111111',
       'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
       'instapay','CI-REVIEW','pending',50,now());
    raise exception 'FAIL: user supplied reviewed_at';
  exception when insufficient_privilege then
    raise notice 'PASS: forged review timestamp blocked';
  end;

  begin
    insert into public.pdf_orders
      (user_id,document_id,payment_method,payment_reference,status,amount_egp)
    values
      ('11111111-1111-4111-8111-111111111111',
       'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
       'instapay','CI-REJECTED','rejected',50);
    raise exception 'FAIL: user supplied rejected status';
  exception when insufficient_privilege then
    raise notice 'PASS: customer cannot choose review status';
  end;

  begin
    insert into public.pdf_orders
      (user_id,document_id,payment_method,payment_reference,status,amount_egp)
    values
      ('11111111-1111-4111-8111-111111111111',
       'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb',
       'instapay','CI-FOREIGN','pending',50);
    raise exception 'FAIL: user inserted order for a foreign document';
  exception when insufficient_privilege then
    raise notice 'PASS: foreign document order blocked by ownership RLS';
  end;

  begin
    insert into public.pdf_orders
      (user_id,document_id,payment_method,payment_reference,status,amount_egp)
    values
      ('22222222-2222-4222-8222-222222222222',
       'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
       'instapay','CI-SPOOFED','pending',50);
    raise exception 'FAIL: user spoofed owner id';
  exception when insufficient_privilege then
    raise notice 'PASS: owner spoofing blocked by ownership RLS';
  end;
end
$qa$;

reset role;

do $qa$
begin
  if has_table_privilege('authenticated','public.pdf_orders','UPDATE')
  or has_table_privilege('authenticated','public.pdf_orders','DELETE') then
    raise exception 'FAIL: customer has UPDATE or DELETE privilege on PDF orders';
  end if;
  if has_table_privilege('anon','public.pdf_orders','INSERT') then
    raise exception 'FAIL: anonymous role can insert PDF orders';
  end if;
  raise notice 'PASS: customer UPDATE/DELETE and anonymous INSERT unavailable';
end $qa$;

set local role authenticated;
set local request.jwt.claim.sub = '22222222-2222-4222-8222-222222222222';
do $qa$
begin
  if exists (select 1 from public.pdf_orders where payment_reference='CI-LEGIT') then
    raise exception 'FAIL: user B can see user A order';
  end if;
  raise notice 'PASS: cross-account PDF order SELECT remains isolated';
end $qa$;

reset role;
set local role service_role;
update public.pdf_orders
set status='approved',reviewed_at=now()
where payment_reference='CI-LEGIT';

do $qa$
begin
  if not exists (
    select 1 from public.pdf_orders
    where payment_reference='CI-LEGIT'
      and status='approved'
      and reviewed_at is not null
  ) then
    raise exception 'FAIL: trusted reviewer could not approve pending order';
  end if;
  raise notice 'PASS: trusted service_role can approve order';
end $qa$;

reset role;
rollback;
