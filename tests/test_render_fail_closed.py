"""Offline regression tests for rendering without usable visual media."""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import render


class RenderFailClosedTests(unittest.TestCase):
    def test_empty_media_blocks_render_without_mp4(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = root / "content.json"
            output = root / "out"

            content.write_text(
                json.dumps({
                    "editorial_status": "APPROVED",
                    "media_rights_status": "VERIFIED",
                    "publishing_status": "READY",
                    "narration": "Esta es una prueba de seguridad.",
                    "media": [],
                }),
                encoding="utf-8",
            )

            class FakePiper:
                returncode = 0

                def communicate(self, text):
                    return (None, None)

            argv = [
                "render.py",
                "--content", str(content),
                "--out", str(output),
                "--voice-model", "mock-voice.onnx",
            ]

            with (
                mock.patch.object(sys, "argv", argv),
                mock.patch.object(
                    render.subprocess, "Popen", return_value=FakePiper()
                ) as piper,
                mock.patch.object(
                    render, "probe_duration", return_value=65.0
                ),
                mock.patch.object(render, "run") as ffmpeg,
            ):
                with self.assertRaises(SystemExit) as ctx:
                    render.main()

            self.assertIn(
                "RENDER_BLOCKED_NO_MEDIA",
                str(ctx.exception.code),
            )
            self.assertFalse(list(output.rglob("*.mp4")))
            self.assertFalse((output / "caption.txt").exists())
            self.assertFalse((output / "sources.json").exists())
            piper.assert_called_once()
            ffmpeg.assert_not_called()


if __name__ == "__main__":
    unittest.main()
