-- P0-SEC-PDF-01 / GitHub issue #26
-- Defense in depth: authenticated customers may request a PDF, not approve it.
-- This migration deliberately retains the existing ownership INSERT policy and
-- current client payload (which may explicitly include pending / EGP 50).
-- Apply to staging and run qa/supabase_rls.sql before requesting production approval.
--
-- Current product price: EGP 50, per owner-approved manual PDF order flow.
-- If pricing changes, update this database rule in a reviewed migration FIRST.

begin;

alter table public.pdf_orders enable row level security;

-- Customers must never mutate an existing order or its review outcome.
revoke update, delete on table public.pdf_orders from anon, authenticated;

-- A RESTRICTIVE policy is AND-ed with every permissive INSERT policy.
-- Thus adding another permissive policy later cannot bypass this guard.
-- The existing "Users request PDF for own document" policy still enforces
-- auth.uid() = user_id and ownership of document_id.
drop policy if exists "Customer PDF orders require pending status and fixed price"
  on public.pdf_orders;

create policy "Customer PDF orders require pending status and fixed price"
  on public.pdf_orders
  as restrictive
  for insert
  to authenticated
  with check (
    status = 'pending'
    and amount_egp = 50
    and reviewed_at is null
  );

commit;
