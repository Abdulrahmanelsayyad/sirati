-- Applied to the Sirati Supabase project as migration 20261007131224.
-- Principle of least privilege for Data API access.
-- RLS policies remain the row-level authorization boundary.

revoke all privileges on table public.cv_documents from anon;
revoke all privileges on table public.cv_versions from anon;
revoke all privileges on table public.pdf_orders from anon;

revoke all privileges on table public.cv_documents from authenticated;
revoke all privileges on table public.cv_versions from authenticated;
revoke all privileges on table public.pdf_orders from authenticated;

grant select, insert, update, delete on table public.cv_documents to authenticated;
grant select, insert, delete on table public.cv_versions to authenticated;
grant select, insert on table public.pdf_orders to authenticated;
