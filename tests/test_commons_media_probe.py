"""Offline, no-network tests for the Commons media preflight."""
import importlib.util
import io
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts/probe_commons_media_20261030.py"
spec = importlib.util.spec_from_file_location("commons_probe", SCRIPT)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

class Response(io.BytesIO):
    def __init__(self, data, url, content_type="image/jpeg"):
        super().__init__(data)
        self.url = url
        self.headers = self
        self.content_type = content_type
    def geturl(self):
        return self.url
    def get_content_type(self):
        return self.content_type

class Tests(unittest.TestCase):
    def run_probe(self, api, media=None):
        with tempfile.TemporaryDirectory() as temp:
            base = pathlib.Path(temp)
            inventory = base / "inventory.json"
            report = base / "report.json"
            inventory.write_text(json.dumps({"slots": [{"slot": "test", "exact_file_url": "https://commons.wikimedia.org/wiki/File:Test.jpg"}]}))
            def open_url(req, timeout=None):
                url = req.full_url
                if "/w/api.php?" in url:
                    return Response(json.dumps(api).encode(), url, "application/json")
                return Response(media or b"", url)
            with patch.object(probe, "INVENTORY", inventory), patch.object(probe, "OUT", report), patch.object(probe.OPENER, "open", side_effect=open_url):
                result = probe.main()
            return result, json.loads(report.read_text())
    def test_hash_success_does_not_approve_rights(self):
        data = b"abc"
        api = {"query": {"pages": {"1": {"imageinfo": [{"url": "https://upload.wikimedia.org/test.jpg", "size": len(data), "mime": "image/jpeg"}]}}}}
        result, report = self.run_probe(api, data)
        self.assertEqual(result, 0)
        self.assertEqual(report["status"], "PASS_HASH_ONLY")
        self.assertFalse(report["rights_approved"])
        self.assertFalse(report["publication_authorized"])
        self.assertEqual(report["results"][0]["sha256"], "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
    def test_reject_untrusted_original_host(self):
        api = {"query": {"pages": {"1": {"imageinfo": [{"url": "https://example.com/test.jpg", "size": 3, "mime": "image/jpeg"}]}}}}
        result, report = self.run_probe(api, b"abc")
        self.assertEqual(result, 1)
        self.assertEqual(report["status"], "BLOCKED")
    def test_reject_size_mismatch(self):
        api = {"query": {"pages": {"1": {"imageinfo": [{"url": "https://upload.wikimedia.org/test.jpg", "size": 4, "mime": "image/jpeg"}]}}}}
        result, report = self.run_probe(api, b"abc")
        self.assertEqual(result, 1)
        self.assertEqual(report["status"], "BLOCKED")
    def test_redirect_handler_blocks(self):
        with self.assertRaises(ValueError):
            probe.NoRedirect().redirect_request(None, None, 302, "Found", {}, "https://example.com")
if __name__ == "__main__":
    unittest.main()
