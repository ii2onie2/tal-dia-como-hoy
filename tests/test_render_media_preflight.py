"""Offline regression tests for fail-closed rendering preflight."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.render_media_preflight import check


class RenderMediaPreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "content").mkdir()
        (self.root / "media").mkdir()
        self.path = self.root / "content" / "2026-10-29.json"
        self.doc = {"media": [{"commons_title": "File:Example_licensed_image.jpg"}]}

    def run_check(self):
        self.path.write_text(json.dumps(self.doc), encoding="utf-8")
        return check("content/2026-10-29.json", root=self.root)

    def assert_blocked(self, reason):
        with self.assertRaisesRegex(ValueError, reason):
            self.run_check()

    def test_commons_candidate_passes_only_input_preflight(self):
        self.run_check()

    def test_research_draft_cannot_render(self):
        self.doc["editorial_status"] = "RESEARCH_DRAFT_UNAPPROVED"
        self.assert_blocked("unresolved editorial_status")

    def test_global_rights_unverified_cannot_render(self):
        self.doc["media_rights_status"] = "NOT_VERIFIED"
        self.assert_blocked("unresolved media_rights_status")

    def test_forbidden_publication_status_cannot_render(self):
        self.doc["publishing_status"] = "FORBIDDEN_UNTIL_RIGHTS_AND_EDITORIAL_GATES"
        self.assert_blocked("unresolved publishing_status")

    def test_undetermined_media_cannot_render(self):
        self.doc["media"] = [{"asset_status": "NOT_SELECTED", "license_note": "RIGHTS_UNVERIFIED_NO_RENDER"}]
        self.assert_blocked("unresolved asset_status")

    def test_pending_license_note_cannot_render(self):
        self.doc["media"][0]["license_note"] = "PENDING_LICENSE_REVIEW"
        self.assert_blocked("unresolved license_note")

    def test_empty_media_cannot_render(self):
        self.doc["media"] = []
        self.assert_blocked("no declared visual asset")

    def test_non_commons_asset_without_review_cannot_render(self):
        self.doc["media"] = [{"role": "no visual selected"}]
        self.assert_blocked("unresolved non-Commons")

    def test_invalid_commons_title_cannot_render(self):
        self.doc["media"] = [{"commons_title": "not-a-file"}]
        self.assert_blocked("invalid Commons title")

    def test_local_media_requires_verified_rights(self):
        self.doc["media"] = [{"path": "media/checked.jpg"}]
        self.assert_blocked("local asset reviews not approved")

    def test_valid_local_media_with_checksum(self):
        asset = self.root / "media" / "checked.jpg"
        asset.write_bytes(b"test image bytes")
        self.doc["media"] = [{
            "path": "media/checked.jpg",
            "rights_review": "PASS", "visual_review": "PASS",
            "sha256": hashlib.sha256(asset.read_bytes()).hexdigest(),
        }]
        self.run_check()

    def test_local_media_rejects_tampered_checksum(self):
        asset = self.root / "media" / "checked.jpg"
        asset.write_bytes(b"test image bytes")
        self.doc["media"] = [{
            "path": "media/checked.jpg",
            "rights_review": "PASS", "visual_review": "PASS",
            "sha256": "0" * 64,
        }]
        self.assert_blocked("SHA256 mismatch")

    def test_local_media_rejects_directory_escape(self):
        self.doc["media"] = [{
            "path": "media/../content/2026-10-29.json",
            "rights_review": "PASS", "visual_review": "PASS",
            "sha256": "0" * 64,
        }]
        self.assert_blocked("missing or escapes")

    def test_workflow_preflight_occurs_before_installations(self):
        flow = Path(".github/workflows/render.yml").read_text(encoding="utf-8")
        resolve = flow.index("- name: Resolve content files")
        media = flow.index("- name: Enforce media and editorial render preflight")
        quality = flow.index("- name: Validate content quality")
        ffmpeg = flow.index("- name: Install FFmpeg and fonts")
        pip = flow.index("- name: Install Python dependencies and Piper")
        self.assertLess(resolve, media)
        self.assertLess(media, quality)
        self.assertLess(quality, ffmpeg)
        self.assertLess(ffmpeg, pip)
        self.assertIn("python3 scripts/render_media_preflight.py", flow)
        self.assertIn('INPUT_CONTENT_FILE: ${{ inputs.content_file }}', flow)
        self.assertNotIn('FILE="${{ inputs.content_file }}"', flow)


if __name__ == "__main__":
    unittest.main()
