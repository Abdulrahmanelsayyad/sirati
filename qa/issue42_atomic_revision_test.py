#!/usr/bin/env python3
"""Exact draft trigger tests in CI's disposable PostgreSQL, never a live project.

No Supabase connection or migration runner. The fixture supplies only relevant
schema and grants, then extracts the actual proposed DDL/trigger definitions.
Requires local psql and CI service database sirati_atomic_fixture.
"""
from pathlib import Path
import subprocess
import threading
import time
import unittest

PSQL = ["psql", "-X", "-qAt", "-v", "ON_ERROR_STOP=1", "-h", "127.0.0.1",
        "-U", "postgres", "-d", "sirati_atomic_fixture"]
A = "11111111-1111-4111-8111-111111111111"
B = "22222222-2222-4222-8222-222222222222"
D = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
F = "ffffffff-ffff-4fff-8fff-ffffffffffff"


def sql(text, check=True):
    result = subprocess.run(PSQL, input="\\set VERBOSITY verbose\n" + text,
                            text=True, capture_output=True, timeout=15)
    if check and result.returncode:
        raise AssertionError(result.stderr)
    return result


def owned(text, user=A):
    return f"SET ROLE authenticated; SET request.jwt.claim.sub='{user}';\n{text}"


def order(revision, ref="synthetic", doc=D):
    revision_sql = "NULL" if revision is None else f"'{revision}'"
    return ("INSERT INTO public.pdf_orders"
            "(user_id,document_id,expected_revision,amount_egp,status,payment_reference)"
            f" VALUES ('{A}','{doc}',{revision_sql},50,'pending','{ref}') RETURNING id;")


def fixture():
    sql("""
CREATE ROLE anon;
CREATE ROLE authenticated;
CREATE ROLE service_role BYPASSRLS;
CREATE SCHEMA auth;
CREATE FUNCTION auth.uid() RETURNS uuid LANGUAGE sql AS
  $$ SELECT nullif(current_setting('request.jwt.claim.sub',true),'')::uuid $$;
GRANT USAGE ON SCHEMA auth TO authenticated;
GRANT EXECUTE ON FUNCTION auth.uid() TO authenticated;
CREATE TABLE public.cv_documents (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), user_id uuid NOT NULL,
 title text NOT NULL DEFAULT 'Synthetic', data jsonb NOT NULL,
 template text NOT NULL DEFAULT 'compact-ats', language text NOT NULL DEFAULT 'en',
 updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE public.pdf_orders (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), user_id uuid NOT NULL,
 document_id uuid NOT NULL REFERENCES public.cv_documents(id) ON DELETE CASCADE,
 amount_egp integer NOT NULL, status text NOT NULL, reviewed_at timestamptz,
 payment_reference text NOT NULL
);
ALTER TABLE public.cv_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pdf_orders ENABLE ROW LEVEL SECURITY;
GRANT SELECT,INSERT,UPDATE,DELETE ON public.cv_documents TO authenticated;
GRANT SELECT,INSERT ON public.pdf_orders TO authenticated;
CREATE POLICY doc_owner ON public.cv_documents TO authenticated
 USING (user_id=auth.uid()) WITH CHECK (user_id=auth.uid());
CREATE POLICY order_owner ON public.pdf_orders TO authenticated
 USING (user_id=auth.uid()) WITH CHECK (user_id=auth.uid());
CREATE POLICY "Customer PDF orders require pending status and fixed price"
 ON public.pdf_orders AS RESTRICTIVE FOR INSERT TO authenticated
 WITH CHECK (status='pending' AND amount_egp=50 AND reviewed_at IS NULL);
""")
    # Deliberately NOT running migration/preflight/BEGIN/COMMIT against a project.
    proposal = Path("supabase/migrations/20261009100000_freeze_pdf_order_snapshot.sql").read_text()
    ddl = proposal[proposal.index("-- Server-issued opaque revision"):
                   proposal.index("-- No UPDATE/DELETE on historical orders")]
    sql(ddl)


class AtomicRevision(unittest.TestCase):
    def setUp(self):
        sql("TRUNCATE public.cv_documents CASCADE;")
        sql(f"""INSERT INTO public.cv_documents(id,user_id,data)
          VALUES ('{D}','{A}','{{"fullName":"Revision A"}}'),
                 ('{F}','{B}','{{"fullName":"Foreign"}}');""")
        self.rev = sql(f"SELECT revision FROM public.cv_documents WHERE id='{D}';").stdout.strip()

    def counts(self):
        return sql("SELECT (SELECT count(*) FROM public.pdf_orders),"
                   "(SELECT count(*) FROM sirati_private.pdf_order_snapshots);").stdout.strip()

    def test_current_revision_atomic_order_and_explicit_snapshot(self):
        sql(owned(order(self.rev)))
        self.assertEqual(self.counts(), "1|1")
        actual = sql("""SELECT s.source_revision=o.expected_revision AND
          s.order_id=o.id AND s.owner_user_id=o.user_id AND
          s.source_document_id=o.document_id FROM sirati_private.pdf_order_snapshots s
          JOIN public.pdf_orders o ON s.order_id=o.id;""").stdout.strip()
        self.assertEqual(actual, "t")

    def test_two_tabs_stale_save_rejected_no_side_effects(self):
        # Tab A got revision from its write; tab B writes before A submits order.
        sql(owned(f"UPDATE public.cv_documents SET data='{{\"fullName\":\"Tab B\"}}' WHERE id='{D}';"))
        result = sql(owned(order(self.rev)), check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("PT409", result.stderr)
        self.assertEqual(self.counts(), "0|0")

    def test_missing_revision_and_foreign_document_rejected(self):
        for statement, code in [(order(None), "PT409"), (order(self.rev, doc=F), "42501")]:
            result = sql(owned(statement), check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(code, result.stderr)
            self.assertEqual(self.counts(), "0|0")

    def test_concurrent_order_creation_only_one_active_order(self):
        barrier = threading.Barrier(2)
        results = []
        def submit():
            barrier.wait()
            results.append(sql(owned(order(self.rev)), check=False))
        threads = [threading.Thread(target=submit) for _ in range(2)]
        for thread in threads: thread.start()
        for thread in threads: thread.join(timeout=15)
        self.assertEqual(len(results), 2)
        self.assertEqual(sum(result.returncode == 0 for result in results), 1)
        self.assertTrue(any("23505" in result.stderr for result in results))
        self.assertEqual(self.counts(), "1|1")

    def test_inflight_other_tab_update_rechecked_after_lock(self):
        # Hold B's uncommitted UPDATE; A must wait, then reject B's new revision.
        proc = subprocess.Popen(PSQL, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True)
        proc.stdin.write(owned(f"""BEGIN;
          UPDATE public.cv_documents SET data='{{"fullName":"In-flight B"}}' WHERE id='{D}';
          SELECT pg_sleep(3); COMMIT;"""))
        proc.stdin.close()
        for _ in range(100):
            locked = sql("""SELECT count(*) FROM pg_stat_activity
              WHERE datname='sirati_atomic_fixture' AND wait_event='PgSleep';""").stdout.strip()
            if locked != "0": break
            time.sleep(0.02)
        else:
            proc.kill()
            self.fail("Concurrent updater never acquired lock")
        result = sql(owned(order(self.rev)), check=False)
        self.assertEqual(proc.wait(timeout=10), 0)
        self.assertIn("PT409", result.stderr)
        self.assertEqual(self.counts(), "0|0")

    def test_later_edits_and_privileged_update_cannot_mutate_snapshot(self):
        sql(owned(order(self.rev)))
        before = sql("SELECT snapshot_data::text FROM sirati_private.pdf_order_snapshots;").stdout
        sql(owned(f"UPDATE public.cv_documents SET data='{{}}', revision='{self.rev}' WHERE id='{D}';"))
        self.assertNotEqual(sql(f"SELECT revision FROM public.cv_documents WHERE id='{D}';").stdout.strip(), self.rev)
        self.assertEqual(sql("SELECT snapshot_data::text FROM sirati_private.pdf_order_snapshots;").stdout, before)
        result = sql("UPDATE sirati_private.pdf_order_snapshots SET snapshot_data='{}';", check=False)
        self.assertIn("23514", result.stderr)
        result = sql("UPDATE public.pdf_orders SET expected_revision=gen_random_uuid();", check=False)
        self.assertIn("23514", result.stderr)
        self.assertEqual(self.counts(), "1|1")

    def test_client_cannot_read_or_mutate_snapshot(self):
        sql(owned(order(self.rev)))
        for statement in ["SELECT * FROM sirati_private.pdf_order_snapshots;",
                          "UPDATE sirati_private.pdf_order_snapshots SET snapshot_data='{}';"]:
            result = sql(owned(statement), check=False)
            self.assertIn("42501", result.stderr)
        self.assertEqual(self.counts(), "1|1")

    def test_approval_keeps_binding_rejection_allows_new_order_cascade(self):
        sql(owned(order(self.rev)))
        sql("UPDATE public.pdf_orders SET status='approved',reviewed_at=now();")
        self.assertIn("23505", sql(owned(order(self.rev)), check=False).stderr)
        sql("UPDATE public.pdf_orders SET status='rejected';")
        sql(owned(order(self.rev, ref="new attempt")))
        self.assertEqual(self.counts(), "2|2")
        sql(owned(f"DELETE FROM public.cv_documents WHERE id='{D}';"))
        self.assertEqual(self.counts(), "0|0")
        self.assertEqual(sql(f"SELECT count(*) FROM public.cv_documents WHERE id='{F}';").stdout.strip(), "1")


if __name__ == "__main__":
    fixture()
    unittest.main(verbosity=2)
