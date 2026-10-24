import tempfile
import unittest
from pathlib import Path
from render_adapter_r62 import preflight

QUEUE=Path(__file__).with_name("P332R20_EVIDENCE_QUEUE_UNAPPROVED.json")
class R62Tests(unittest.TestCase):
 def test_unapproved_is_denied(self):
  with tempfile.TemporaryDirectory() as root:
   r=preflight(root,QUEUE,"2026-10-17")
   self.assertFalse(r["allowed"])
   self.assertFalse(r["render_invoked"])
   self.assertFalse(r["publish_invoked"])
 def test_wrong_date_is_denied(self):
  with tempfile.TemporaryDirectory() as root:
   r=preflight(root,QUEUE,"2026-10-18")
   self.assertFalse(r["allowed"])
   self.assertIn("EVIDENCE_DATE_MISMATCH",r["reasons"])
if __name__=="__main__":unittest.main()
