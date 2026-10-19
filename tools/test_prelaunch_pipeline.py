import json,tempfile,unittest
from pathlib import Path
from prepare_daily_drafts import prepare
from tiktok_handoff_dry_run import simulate

class PreLaunchTests(unittest.TestCase):
 def test_missing_daily_source_fails_closed(self):
  with tempfile.TemporaryDirectory() as d:
   r=prepare(Path(d)/"sources",Path(d)/"drafts","2026-10-19")
   self.assertEqual(len(r["blocked"]),3)
   self.assertFalse(r["publish_authorized"])
 def test_draft_is_never_approved(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);source=root/"review";source.mkdir()
   for suffix in ("","-detalle","-sabias"):
    (source/f"2026-10-19{suffix}.json").write_text(json.dumps({"date":"2026-10-19","narration":"sample","sources":[{"url":"https://archive.example.org/a"},{"url":"https://museum.example.net/b"}],"media":[{"license":"CC0","attribution":"synthetic test","rights_review":"VERIFIED"}],"approved":True}))
   r=prepare(source,root/"output","2026-10-19")
   self.assertEqual(len(r["created"]),3)
   self.assertFalse(json.loads((root/"output"/"2026-10-19.json").read_text())["editorial_approved"])
 def test_one_missing_slot_produces_no_partial_package(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);source=root/"review";source.mkdir()
   for suffix in ("","-detalle"):
    (source/f"2026-10-19{suffix}.json").write_text(json.dumps({"date":"2026-10-19","narration":"sample","sources":[{"url":"https://archive.example.org/a"},{"url":"https://museum.example.net/b"}],"media":[{"license":"CC0","attribution":"synthetic test","rights_review":"VERIFIED"}]}))
   result=prepare(source,root/"out","2026-10-19")
   self.assertTrue(result["blocked"])
   self.assertFalse((root/"out").exists())
   self.assertEqual(result["created"],[])
 def test_missing_video_blocks(self):
  with tempfile.TemporaryDirectory() as d:
   self.assertEqual(simulate(Path(d)/"video.mp4",Path(d)/"manifest.json")["reason"],"VIDEO_MISSING")
 def test_duplicate_blocks(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/"video.mp4").write_bytes(b"synthetic")
   (root/"manifest.json").write_text("{}")
   import hashlib
   digest=hashlib.sha256(b"synthetic").hexdigest()
   self.assertEqual(simulate(root/"video.mp4",root/"manifest.json",{digest})["reason"],"DUPLICATE_VIDEO")
if __name__=="__main__":unittest.main()
