#!/usr/bin/env python3
"""Fail-closed private-preview preflight. No publication authorization."""
import hashlib
import json
import sys
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: preview_media_preflight.py CONTENT_JSON")

    root = Path.cwd()
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))

    for key, expected in (
        ("editorial_status", "APPROVED"),
        ("media_rights_status", "VERIFIED"),
    ):
        if data.get(key) != expected:
            raise SystemExit(f"PREVIEW_BLOCKED: {key} must be {expected}")

    credits = json.loads(
        (root / "media/credits.json").read_text(encoding="utf-8")
    )

    media = data.get("media", [])

    if len(media) != 4 or len(credits) != 4:
        raise SystemExit("PREVIEW_BLOCKED: expected four images")

    for index, (item, credit) in enumerate(zip(media, credits), 1):
        if item.get("path") != credit.get("path"):
            raise SystemExit(f"PREVIEW_BLOCKED: image {index} path mismatch")

        if item.get("commons_title") != credit.get("commons_title"):
            raise SystemExit(f"PREVIEW_BLOCKED: image {index} source mismatch")

        path = (root / credit["path"]).resolve()

        if not path.is_relative_to((root / "media").resolve()):
            raise SystemExit(f"PREVIEW_BLOCKED: image {index} escapes media")

        if not path.is_file():
            raise SystemExit(f"PREVIEW_BLOCKED: image {index} missing")

        actual = hashlib.sha256(path.read_bytes()).hexdigest()

        if actual != credit["sha256"].lower():
            raise SystemExit(f"PREVIEW_BLOCKED: image {index} checksum mismatch")

    print("PREVIEW_PREFLIGHT=PASS")
    print("PUBLICATION_AUTHORIZED=NO")

if __name__ == "__main__":
    main()
