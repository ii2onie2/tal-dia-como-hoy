import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from validate_mp4_artifact import inspect

class ArtifactTests(unittest.TestCase):
    def fixture(self):
        td=tempfile.TemporaryDirectory()
        p=Path(td.name)
        for name in ("video.mp4","subtitles.srt","caption.txt"):
            (p/name).write_text("sample",encoding="utf-8")
        (p/"sources.json").write_text("[]",encoding="utf-8")
        return td,p
    def probe(self,audio=True,width=1080,duration=40):
        streams=[{"codec_type":"video","codec_name":"h264","width":width,"height":1920}]
        if audio:streams.append({"codec_type":"audio","codec_name":"aac"})
        return subprocess.CompletedProcess([],0,json.dumps({"streams":streams,"format":{"duration":duration}}),"")
    def test_synthetic_pass_without_approval(self):
        with self.fixture()[0] as path,patch("validate_mp4_artifact.subprocess.run",return_value=self.probe()):
            self.assertEqual(inspect(path)["result"],"TECHNICAL_STRUCTURE_PASS_APPROVAL_NO")
    def test_factual_empty_sources_blocked(self):
        with self.fixture()[0] as path,patch("validate_mp4_artifact.subprocess.run",return_value=self.probe()):
            with self.assertRaisesRegex(ValueError,"INSUFFICIENT"):inspect(path,factual=True)
    def test_missing_audio_blocked(self):
        with self.fixture()[0] as path,patch("validate_mp4_artifact.subprocess.run",return_value=self.probe(audio=False)):
            with self.assertRaisesRegex(ValueError,"INVALID_AUDIO"):inspect(path)
    def test_wrong_resolution_blocked(self):
        with self.fixture()[0] as path,patch("validate_mp4_artifact.subprocess.run",return_value=self.probe(width=720)):
            with self.assertRaisesRegex(ValueError,"INVALID_VIDEO"):inspect(path)
    def test_missing_sidecar_blocked(self):
        with self.fixture()[0] as path,patch("validate_mp4_artifact.subprocess.run",return_value=self.probe()):
            (Path(path)/"caption.txt").unlink()
            with self.assertRaisesRegex(ValueError,"MISSING"):inspect(path)
    def test_duration_blocked(self):
        with self.fixture()[0] as path,patch("validate_mp4_artifact.subprocess.run",return_value=self.probe(duration=0)):
            with self.assertRaisesRegex(ValueError,"INVALID_DURATION"):inspect(path)
if __name__=="__main__":unittest.main()
