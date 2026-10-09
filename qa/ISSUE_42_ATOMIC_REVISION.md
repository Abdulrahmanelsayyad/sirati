# Issue #42 — branch-only atomic revision correction

Parent #41; supersedes the earlier save/order race assessment at bf1cd513.
Nothing in this document authorizes SQL activation, Staging/Production deployment,
merge, payment approval, or spending.

## Invariant and integration

Every CV INSERT/UPDATE receives a new server-generated UUID revision, even if a
caller submits a forged/old value. Builder captures id and revision directly from
its own save's RETURNING response. It sends that revision as expected_revision
when inserting a pending EGP 50 order; it never obtains it from a later SELECT.

The order's AFTER INSERT trigger reads the owned CV under FOR SHARE and compares
its revision to expected_revision. Missing/stale revision raises PT409, mapped by
PostgREST to HTTP 409. The entire statement rolls back: no order/snapshot remains.
The row lock lasts through transaction completion; an in-flight concurrent CV
write must finish first and its resulting revision is rechecked.

Snapshot is keyed by order_id and records source_revision, document and owner.
An order cannot subsequently change those binding fields, even during trusted
approval. Clients cannot access snapshots; the server has SELECT only; a snapshot
UPDATE is rejected by a separate trigger. Approved status/review fields remain
reviewer-controlled under the existing grants and RLS.

A partial unique index permits one pending/approved order per document/revision.
Concurrent creation attempts produce one order/snapshot, with the other rejected
by 23505 (PostgREST HTTP 409). A rejected order permits a new attempt; its original
snapshot remains attached to its original order. Later saves get new revisions.
Legacy orders stay NULL/unbound and receive no snapshot or invented entitlement.

## Verification boundaries

The targeted CI job uses only a disposable localhost PostgreSQL 17 fixture,
synthetic owners and exact proposed trigger definitions. It does not connect to
Supabase, use secrets, run a migration command, or apply the migration to a project.
Run: python3 qa/issue42_atomic_revision_test.py with the CI PostgreSQL fixture.
Cases: current revision/binding; tab B edit before tab A order; missing/foreign
revision/document; concurrent orders; uncommitted concurrent CV update; immutable
snapshot/order binding and forged revision; client snapshot denial; approval,
rejection retry and deletion cascade. The fixture models relevant grants/RLS,
not the actual project's full schema or Data API configuration.

The existing targeted Builder build must run because generated TS and its save
response shape changed. Existing unchanged PDF auth mock/print/RLS evidence is
reused; unrelated tests must not rerun. Live HTTP status, browser two-tab E2E,
real project privileges and inherited triggers remain NOT RUN until explicitly
authorized isolated Staging testing.

## Outstanding parent gates

The real snapshot-reading official PDF backend/renderer is still absent, and
asset/template version pinning and full Arabic/ATS fidelity remain unproved.
Passing this correction does not authorize paid-customer launch or prove #41
complete. Migration remains a draft and must be reviewed against actual schema,
trigger ordering, grants and migration history before separate owner-approved
Staging activation. Never bulk db push older unaligned migration history.

Official status-code contract:
https://docs.postgrest.org/en/v14/references/errors.html
