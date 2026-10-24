import hashlib,hmac,unittest
from datetime import datetime,timezone,timedelta
from approval_contract_r48 import canonical
from approval_replay_r49 import assess
KEY=b"synthetic-only-offline-fixture-key-00000000"
NOW=datetime(2026,10,18,12,0,tzinfo=timezone.utc)
D="a"*64
def attestation(when="2026-10-18T12:00:00Z",reviewer="synthetic-reviewer"):
 p={"dossier_id":"draft-1","content_sha256":D,"editor_id":reviewer,"decision":"APPROVED","timestamp":when,"source_review":True,"media_rights":True}
 return {"payload":p,"signature":hmac.new(KEY,canonical(p),hashlib.sha256).hexdigest()}
class R49Tests(unittest.TestCase):
 def test_valid_is_not_release(self):
  self.assertEqual(assess(attestation(),KEY,D,set(),{"synthetic-reviewer"},NOW),"SIMULATED_VALIDITY_ONLY_RELEASE_DENIED")
 def test_replay(self):
  r=attestation();self.assertEqual(assess(r,KEY,D,{("draft-1",D,r["signature"])},{"synthetic-reviewer"},NOW),"DENY_REPLAY")
 def test_untrusted(self):
  self.assertEqual(assess(attestation(),KEY,D,set(),set(),NOW),"DENY_UNTRUSTED_EDITOR")
 def test_stale(self):
  self.assertEqual(assess(attestation("2026-10-18T11:00:00Z"),KEY,D,set(),{"synthetic-reviewer"},NOW),"DENY_STALE_ATTESTATION")
 def test_future(self):
  self.assertEqual(assess(attestation("2026-10-18T13:00:00Z"),KEY,D,set(),{"synthetic-reviewer"},NOW),"DENY_STALE_ATTESTATION")
 def test_tamper(self):
  r=attestation();r["payload"]["source_review"]=False
  self.assertEqual(assess(r,KEY,D,set(),{"synthetic-reviewer"},NOW),"DENY_INVALID_ATTESTATION")
if __name__=="__main__":unittest.main()
