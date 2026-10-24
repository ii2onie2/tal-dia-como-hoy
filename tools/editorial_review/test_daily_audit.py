import json
import tempfile
import unittest
from pathlib import Path
from daily_audit import run

class DailyAuditTests(unittest.TestCase):
    def test_missing_evidence_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            report=run("2026-10-18",root/"missing",root/"out")
            self.assertEqual(report["status"],"BLOCKED")
            self.assertFalse(report["publishable"])
            self.assertTrue((root/"out"/"2026-10-18.json").exists())
    def test_invalid_json_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);e=root/"e";e.mkdir()
            (e/"2026-10-18.json").write_text("{",encoding="utf-8")
            report=run("2026-10-18",e,root/"out")
            self.assertIn("GATE_BLOCKED",report["reason"])
    def test_wrong_schema_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);e=root/"e";e.mkdir()
            (e/"2026-10-18.json").write_text('{"schema":"wrong"}',encoding="utf-8")
            report=run("2026-10-18",e,root/"out")
            self.assertEqual(report["status"],"BLOCKED")
    def test_unsafe_date_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):run("../../2026-10-18",Path(td),Path(td)/"out")
    def test_valid_structure_still_blocked(self):
        from test_claim_matrix import fixture
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);e=root/"e";e.mkdir()
            (e/"2026-10-18.json").write_text(json.dumps(fixture()),encoding="utf-8")
            report=run("2026-10-18",e,root/"out")
            self.assertEqual(report["reason"],"STRUCTURE_VALID_HUMAN_FACT_CHECK_REQUIRED")
            self.assertFalse(report["approved"])
            self.assertFalse(report["publishable"])
if __name__=="__main__":unittest.main()
