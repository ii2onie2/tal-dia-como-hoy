"""R46 negative integration: structurally ready JSON never grants publication."""
import json
import tempfile
import unittest
from pathlib import Path
from readiness_preflight import inspect_content

class ReleaseSeparationTests(unittest.TestCase):
    def test_three_date_matched_files_are_not_publication_authorization(self):
        with tempfile.TemporaryDirectory() as directory:
            date="2026-10-17"
            for suffix in ("","-detalle","-sabias"):
                (Path(directory)/f"{date}{suffix}.json").write_text(json.dumps({"date":date,"approved":False,"publishable":False}),encoding="utf-8")
            result=inspect_content(directory,date)
            self.assertTrue(result["ready"])
            self.assertIs(result["publishing_authorized"],False)
    def test_missing_file_is_not_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            result=inspect_content(directory,"2026-10-17")
            self.assertFalse(result["ready"])
            self.assertIs(result["publishing_authorized"],False)
    def test_wrong_day_is_not_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            date="2026-10-17"
            for suffix in ("","-detalle","-sabias"):
                (Path(directory)/f"{date}{suffix}.json").write_text(json.dumps({"date":"2026-10-18"}),encoding="utf-8")
            result=inspect_content(directory,date)
            self.assertFalse(result["ready"])
            self.assertIs(result["publishing_authorized"],False)

if __name__=="__main__":
    unittest.main()
