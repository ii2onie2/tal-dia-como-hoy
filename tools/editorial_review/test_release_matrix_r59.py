import unittest
from synthetic_positive_r58 import synthetic_walkthrough
from e2e_rehearsal_r57 import rehearse
from pathlib import Path
import tempfile

class R59ReleaseMatrix(unittest.TestCase):
 def test_synthetic_signed_contract_never_releases(self):
  result=synthetic_walkthrough()
  self.assertEqual(result["contract_result"],"SIMULATED_VALIDITY_ONLY_RELEASE_DENIED")
  self.assertFalse(result["publish_authorized"])
  self.assertFalse(result["render_authorized"])
 def test_unapproved_historical_queue_blocks_every_downstream_step(self):
  with tempfile.TemporaryDirectory() as directory:
   queue=Path(__file__).with_name("P332R20_EVIDENCE_QUEUE_UNAPPROVED.json")
   r=rehearse(directory,queue,"2026-10-17")
   self.assertFalse(r["editorial_gate"]["render_allowed"])
   for key in ("render_attempted","video_created","transfer_attempted","publish_attempted"):
    self.assertFalse(r[key])
 def test_date_mismatch_never_releases(self):
  with tempfile.TemporaryDirectory() as directory:
   queue=Path(__file__).with_name("P332R20_EVIDENCE_QUEUE_UNAPPROVED.json")
   r=rehearse(directory,queue,"2026-10-18")
   self.assertIn("EVIDENCE_DATE_MISMATCH",r["editorial_gate"]["reasons"])
   self.assertFalse(r["publish_attempted"])
if __name__=="__main__":unittest.main()
