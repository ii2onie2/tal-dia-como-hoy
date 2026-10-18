import tempfile
import unittest
from pathlib import Path
from controlled_render_r61 import controlled_render

QUEUE=Path(__file__).with_name("P332R20_EVIDENCE_QUEUE_UNAPPROVED.json")
class R61Tests(unittest.TestCase):
 def test_unapproved_queue_never_calls_renderer(self):
  with tempfile.TemporaryDirectory() as d:
   calls=[]
   def renderer():calls.append("CALLED")
   result=controlled_render(d,QUEUE,"2026-10-17",renderer)
   self.assertTrue(result["blocked"])
   self.assertFalse(result["renderer_invoked"])
   self.assertEqual(calls,[])
 def test_wrong_date_never_calls_renderer(self):
  with tempfile.TemporaryDirectory() as d:
   calls=[]
   result=controlled_render(d,QUEUE,"2026-10-18",lambda:calls.append(1))
   self.assertIn("EVIDENCE_DATE_MISMATCH",result["reasons"])
   self.assertEqual(calls,[])
 def test_absent_evidence_never_calls_renderer(self):
  with tempfile.TemporaryDirectory() as d:
   calls=[]
   result=controlled_render(d,Path(d)/"missing.json","2026-10-17",lambda:calls.append(1))
   self.assertIn("EVIDENCE_QUEUE_UNREADABLE",result["reasons"])
   self.assertEqual(calls,[])
if __name__=="__main__":unittest.main()
