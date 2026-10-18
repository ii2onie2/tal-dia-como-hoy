import json
import tempfile
import unittest
from pathlib import Path
from e2e_rehearsal_r57 import rehearse

QUEUE=Path(__file__).with_name("P332R20_EVIDENCE_QUEUE_UNAPPROVED.json")

class R57Tests(unittest.TestCase):
 def test_real_unapproved_queue_does_not_render_or_transfer(self):
  with tempfile.TemporaryDirectory() as root:
   date="2026-10-17"
   for suffix in ("","-detalle","-sabias"):
    (Path(root)/f"{date}{suffix}.json").write_text(json.dumps({"date":date}),encoding="utf-8")
   result=rehearse(root,QUEUE,date)
   self.assertIn("TRUSTED_APPROVAL_REGISTRY_UNAVAILABLE",result["editorial_gate"]["reasons"])
   self.assertFalse(result["editorial_gate"]["render_allowed"])
   self.assertFalse(result["render_attempted"])
   self.assertFalse(result["video_created"])
   self.assertFalse(result["transfer_attempted"])
   self.assertFalse(result["publish_attempted"])
 def test_wrong_date_rejected(self):
  with tempfile.TemporaryDirectory() as root:
   result=rehearse(root,QUEUE,"2026-10-18")
   self.assertIn("EVIDENCE_DATE_MISMATCH",result["editorial_gate"]["reasons"])
   self.assertFalse(result["render_attempted"])
 def test_missing_queue_rejected(self):
  with tempfile.TemporaryDirectory() as root:
   result=rehearse(root,Path(root)/"missing.json","2026-10-17")
   self.assertIn("EVIDENCE_QUEUE_UNREADABLE",result["editorial_gate"]["reasons"])
   self.assertFalse(result["transfer_attempted"])

if __name__=="__main__":unittest.main()
