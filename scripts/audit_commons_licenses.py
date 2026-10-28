#!/usr/bin/env python3
"""Offline fail-closed audit of declared Commons image metadata. No network calls."""
import argparse
import html
import json
from pathlib import Path

ALLOWED = {"cc0", "public domain", "cc-by-4.0", "cc-by-3.0", "cc-by-sa-4.0", "cc-by-sa-3.0"}

def plain(value):
    if isinstance(value, dict):
        value = value.get("value", "")
    return html.unescape(str(value or "")).strip()

def check(entry):
    title = entry.get("commons_title", "")
    metadata = entry.get("metadata", {})
    license_name = plain(metadata.get("LicenseShortName", "")).lower().replace(" ", "")
    normalized = license_name.replace("creativecommons", "cc").replace("attribution-sharealike", "by-sa").replace("attribution", "by")
    allowed = normalized in {x.replace(" ", "") for x in ALLOWED}
    author = plain(metadata.get("Artist", ""))
    credit = plain(metadata.get("Credit", ""))
    url = entry.get("source", "")
    if not title.startswith("File:") or not url.startswith("https://upload.wikimedia.org/"):
        return False, "INVALID_COMMONS_SOURCE"
    if not allowed:
        return False, "LICENSE_NOT_ALLOWLISTED"
    if not author and not credit:
        return False, "ATTRIBUTION_MISSING"
    return True, "LICENSE_METADATA_OK"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("credits", type=Path)
    args = ap.parse_args()
    data = json.loads(args.credits.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise SystemExit("FAIL_EMPTY_CREDITS")
    for entry in data:
        ok, reason = check(entry)
        print(f"{reason}: {entry.get('commons_title', '')}")
        if not ok:
            raise SystemExit(1)
    print("PASS_OFFLINE_LICENSE_METADATA_GATE")

if __name__ == "__main__":
    main()
