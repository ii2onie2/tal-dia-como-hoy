import json
import tempfile
import unittest
from pathlib import Path
from prerender_gate_r47 import assess

class PrerenderTests(unittest.TestCase):
    def test_unapproved_real_queue_is_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            result=assess(d,Path(__file__).with_name("P332R20_EVIDENCE_QUEUE_UNAPPROVED.json"),"2026-10-17")
            self.assertFalse(result["render_allowed"])
            self.assertFalse(result["publish_allowed"])
            self.assertIn("DOSSIER_NOT_APPROVED",result["reasons"])
    def test_json_self_approval_still_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            date="2026-10-17"
            for suffix in ("","-detalle","-sabias"):
                (Path(d)/f"{date}{suffix}.json").write_text(json.dumps({"date":date}),encoding="utf-8")
            data={"date":date,"approved":True,"publishable":True,"dossiers":[
                {"status":"APPROVED","claims":[{"review":"APPROVED","sources":[
                    {"independent_verified":True},{"independent_verified":True}]}]} for _ in range(3)]}
            p=Path(d)/"queue.json"
            p.write_text(json.dumps(data),encoding="utf-8")
            result=assess(d,p,date)
            self.assertFalse(result["render_allowed"])
            self.assertIn("TRUSTED_APPROVAL_REGISTRY_UNAVAILABLE",result["reasons"])
    def test_unreadable_queue_stays_blocked(self):
        with tempfile.TemporaryDirectory() as d:
            r=assess(d,Path(d)/"missing.json","2026-10-17")
            self.assertFalse(r["render_allowed"])
            self.assertIn("EVIDENCE_QUEUE_UNREADABLE",r["reasons"])

if __name__=="__main__":
    unittest.main()
