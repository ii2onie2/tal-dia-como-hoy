import json
import tempfile
import unittest
from pathlib import Path
from readiness_preflight import inspect_content

class ReadinessTests(unittest.TestCase):
 def test_missing_blocks(self):
  with tempfile.TemporaryDirectory() as d:
   a=inspect_content(d,"2026-10-18")
   self.assertFalse(a["ready"])
   self.assertFalse(a["publishing_authorized"])
 def test_three_structures_only(self):
  with tempfile.TemporaryDirectory() as d:
   for n in ("2026-10-18.json","2026-10-18-detalle.json","2026-10-18-sabias.json"):
    (Path(d)/n).write_text(json.dumps({"date":"2026-10-18"}),encoding="utf-8")
   a=inspect_content(d,"2026-10-18")
   self.assertTrue(a["ready"])
   self.assertFalse(a["publishing_authorized"])
 def test_mismatch_blocks(self):
  with tempfile.TemporaryDirectory() as d:
   for n in ("2026-10-18.json","2026-10-18-detalle.json","2026-10-18-sabias.json"):
    (Path(d)/n).write_text(json.dumps({"date":"2026-10-17"}),encoding="utf-8")
   self.assertFalse(inspect_content(d,"2026-10-18")["ready"])
