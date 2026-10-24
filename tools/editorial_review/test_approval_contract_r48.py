import hashlib
import hmac
import unittest
from approval_contract_r48 import canonical,verify,gate

KEY=b"synthetic-only-offline-fixture-key-00000000"
DIGEST="a"*64

def fixture():
 p={"dossier_id":"test-1","content_sha256":DIGEST,"editor_id":"synthetic-reviewer","decision":"APPROVED","timestamp":"2026-10-18T10:00:00Z","source_review":True,"media_rights":True}
 return {"payload":p,"signature":hmac.new(KEY,canonical(p),hashlib.sha256).hexdigest()}

class R48Tests(unittest.TestCase):
 def test_valid_signature_never_releases(self):
  r=gate(fixture(),KEY,DIGEST)
  self.assertTrue(r["cryptographic_contract_valid"])
  self.assertFalse(r["release_authorized"])
  self.assertFalse(r["publish_authorized"])
 def test_tamper_blocked(self):
  r=fixture();r["payload"]["media_rights"]=False
  self.assertFalse(verify(r,KEY,DIGEST))
 def test_wrong_key_blocked(self):
  self.assertFalse(verify(fixture(),b"another-synthetic-key-000000000000000",DIGEST))
 def test_wrong_hash_blocked(self):
  self.assertFalse(verify(fixture(),KEY,"b"*64))
 def test_short_key_blocked(self):
  self.assertFalse(verify(fixture(),b"too-short",DIGEST))
 def test_unapproved_blocked(self):
  r=fixture();r["payload"]["decision"]="PENDING"
  r["signature"]=hmac.new(KEY,canonical(r["payload"]),hashlib.sha256).hexdigest()
  self.assertFalse(verify(r,KEY,DIGEST))
if __name__=="__main__":unittest.main()
