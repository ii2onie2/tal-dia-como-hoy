# Neon reservation ledger V1 — permanent migration preparation (NOT AUTHORIZED)

## Verified evidence (2026-10-16)
- Both GitHub repos point at the same PostgreSQL 18 target (matching read-only connection fingerprint).
- Transactional SQL rehearsals PASS and ended ROLLBACK.
- Independent read-only table absence checks PASS on both repositories.
- Existing PlanVortex list pagination with nonempty data UNVERIFIED.
- Publication approval and media rights NOT GRANTED.

## Pre-commit requirements
1. Revalidate the same Neon database and schema/table absence in a new read-only session immediately before commit.
2. Save immutable DDL content hash and verify it matches the reviewed SQL.
3. Confirm the dedicated writer role and its least-privilege grants; current owner URL must not be used by routine publisher jobs.
4. Capture read-only pre-migration schema inventory, then approve one narrowly scoped migration.
5. Commit within one PostgreSQL transaction, verify indexes/constraints and capture post-migration inventory.
6. On migration failure, ROLLBACK. For later reversal, first inspect occupancy and dependencies, back up any state, and require separate authorization; never drop a live table automatically.

## Status
PERMANENT_MIGRATION_AUTHORIZED=NO
SCHEMA_CREATED=NO
UPLOAD_ENABLED=NO
PUBLICATION_ENABLED=NO
VERITAS_VPS_ACCESSED=NO
