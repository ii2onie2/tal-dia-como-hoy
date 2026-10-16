#!/usr/bin/env python3
"""Explicitly authorized Neon V1 bounded migration, one transaction."""
import hashlib,os,pathlib,sys
import psycopg
from psycopg.conninfo import conninfo_to_dict
expected={
"sql/neon_reservation_schema_v1.sql":"f2b0e3c90589cce1df622ce7f70b3c02aae12c665950342a3ec7cb06c24c1f90",
"sql/neon_role_grants_v1_proposal.sql":"918f465f9832db00957499a9a114a5e5d76cae79dfbe92ac651f0ea27cfb46eb"}
def ddl(path):
 raw=pathlib.Path(path).read_bytes()
 actual=hashlib.sha256(raw).hexdigest()
 if actual!=expected[path]:raise RuntimeError("SQL_HASH_MISMATCH")
 text=raw.decode()
 start=text.find("\nBEGIN;\n")
 end=text.rfind("\nCOMMIT;")
 if start<0 or end<start or text[end:].strip()!="COMMIT;":raise RuntimeError("SQL_TRANSACTION_WRAPPERS")
 return text[:start]+text[start+len("\nBEGIN;\n"):end]
def state(cur):
 cur.execute("""SELECT to_regnamespace('tiktok_autopilot') IS NOT NULL,
 to_regclass('tiktok_autopilot.publication_reservations') IS NOT NULL,
 EXISTS(SELECT 1 FROM pg_roles WHERE rolname='tiktok_reservation_rw')""")
 return cur.fetchone()
url=os.environ.get("NEON_DATABASE_URL","")
if not url:raise SystemExit("BLOCKED_DSN_MISSING")
if conninfo_to_dict(url).get("sslmode") not in ("require","verify-ca","verify-full"):raise SystemExit("BLOCKED_SSL")
try:
 scripts=[ddl(p) for p in expected]
 print("SQL_HASHES=PASS")
 with psycopg.connect(url,connect_timeout=15,autocommit=False) as db:
  with db.cursor() as cur:
   cur.execute("SET LOCAL lock_timeout='8s'")
   cur.execute("SET LOCAL statement_timeout='25s'")
   before=state(cur)
   print("PRE_SCHEMA_TABLE_ROLE="+str(before))
   if before!=(False,False,False):raise RuntimeError("PRECHECK_OBJECTS_NOT_ABSENT")
   cur.execute(scripts[0])
   cur.execute(scripts[1])
   if state(cur)!=(True,True,True):raise RuntimeError("IN_TRANSACTION_OBJECTS_MISSING")
   cur.execute("""SELECT rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,
     has_schema_privilege('tiktok_reservation_rw','tiktok_autopilot','USAGE'),
     has_table_privilege('tiktok_reservation_rw','tiktok_autopilot.publication_reservations','SELECT'),
     has_table_privilege('tiktok_reservation_rw','tiktok_autopilot.publication_reservations','INSERT'),
     has_table_privilege('tiktok_reservation_rw','tiktok_autopilot.publication_reservations','UPDATE'),
     has_table_privilege('tiktok_reservation_rw','tiktok_autopilot.publication_reservations','DELETE')
     FROM pg_roles WHERE rolname='tiktok_reservation_rw'""")
   role=cur.fetchone()
   if role!=(False,False,False,False,True,True,True,True,False):raise RuntimeError("ROLE_POLICY_MISMATCH")
   cur.execute("""SELECT COUNT(*) FROM pg_constraint WHERE conrelid='tiktok_autopilot.publication_reservations'::regclass AND contype IN ('p','u')""")
   if cur.fetchone()[0]<3:raise RuntimeError("UNIQUE_CONSTRAINTS_MISSING")
  db.commit()
 print("COMMIT=YES")
 with psycopg.connect(url,connect_timeout=15,options="-c default_transaction_read_only=on") as chk:
  chk.read_only=True
  with chk.cursor() as cur:
   if state(cur)!=(True,True,True):raise RuntimeError("POSTCHECK_OBJECTS_MISSING")
   cur.execute("SELECT COUNT(*) FROM tiktok_autopilot.publication_reservations")
   if cur.fetchone()[0]!=0:raise RuntimeError("NONEMPTY_NEW_LEDGER")
 print("POSTCOMMIT_READ_ONLY_VERIFICATION=PASS")
 print("PUBLICATION=NO")
 print("RESULT=PASS_NEON_V1_BOUNDED_COMMIT")
except Exception as exc:
 print("RESULT=FAIL_NEON_V1_BOUNDED_MIGRATION")
 print("ERROR_CLASS="+type(exc).__name__)
 sys.exit(1)
