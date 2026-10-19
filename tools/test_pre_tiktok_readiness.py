import json
import tempfile
import unittest
from pathlib import Path
from pre_tiktok_readiness import audit

class ReadinessTests(unittest.TestCase):
 def test_missing_all_slots_blocks(self):
  with tempfile.TemporaryDirectory() as d:
   r=audit(d,"2026-10-19")
   self.assertEqual(len(r["slots"]),3)
   self.assertIn("DAILY_CONTENT_MISSING",r["blockers"])
   self.assertFalse(r["publish_authorized"])
 def test_self_declared_approval_cannot_release(self):
  with tempfile.TemporaryDirectory() as d:
   day="2026-10-19"
   for suffix in ("","-detalle","-sabias"):
    Path(d,f"{day}{suffix}.json").write_text(json.dumps({"date":day,"narration":"synthetic", "approved":True,"sources":["x","y"],"media":[{"license":"CC0","attribution":"x","rights_review":"VERIFIED"}]}),encoding="utf-8")
   r=audit(d,day)
   self.assertFalse(r["render_authorized"])
   self.assertFalse(r["publish_authorized"])
   self.assertIn("TRUSTED_EDITORIAL_APPROVAL_UNAVAILABLE",r["blockers"])
 def test_rights_not_inferred_from_url(self):
  with tempfile.TemporaryDirectory() as d:
   day="2026-10-19"
   Path(d,f"{day}.json").write_text(json.dumps({"date":day,"narration":"x","sources":["one","two"],"media":[{"commons_title":"File:Public.jpg"}]}),encoding="utf-8")
   r=audit(d,day)
   self.assertIn("MEDIA_RIGHTS_UNVERIFIED",r["blockers"])
 def test_wrong_day_not_valid(self):
  with tempfile.TemporaryDirectory() as d:
   Path(d,"2026-10-19.json").write_text(json.dumps({"date":"2026-10-18","narration":"x"}))
   self.assertIn("CONTENT_INVALID",audit(d,"2026-10-19")["blockers"])
if __name__=="__main__":unittest.main()
