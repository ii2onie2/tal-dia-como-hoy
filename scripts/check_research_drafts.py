#!/usr/bin/env python3
"""Structural check for unapproved research only. Never signals render readiness."""
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

SLOTS = {"": ("Tal Día Como Hoy", "10:00"), "-detalle": ("El detalle que casi nadie ve", "16:00"), "-sabias": ("¿Sabías esto de España?", "19:00")}
PATH_RE = re.compile(r"^(20[0-9]{2}-[0-9]{2}-[0-9]{2})(-detalle|-sabias)?\.research\.json$")
ALLOWED_SOURCE_HOSTS = {"www.consilium.europa.eu", "www.europarl.europa.eu", "whc.unesco.org", "ich.unesco.org"}


def check(paths):
    history = json.loads(Path("content/published_history.json").read_text(encoding="utf-8"))
    used = {str(x.get("topic_family", "")).casefold() for x in history if isinstance(x, dict)}
    dates = set()
    for path in paths:
        path = Path(path)
        m = PATH_RE.fullmatch(path.name)
        if path.parent.as_posix() != "content/research" or not m:
            raise ValueError(f"Research-only path required: {path}")
        date, suffix = m.groups()
        suffix = suffix or ""
        dates.add(date)
        d = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(d, dict):
            raise ValueError(f"{path}: expected JSON object")
        if (d.get("date"), d.get("series"), d.get("slot")) != (date, *SLOTS[suffix]):
            raise ValueError(f"{path}: date, series or slot mismatch")
        if any(not d.get(k) for k in ("title", "hook", "narration", "caption", "hashtags", "sources", "media", "cta", "topic_family")):
            raise ValueError(f"{path}: required field empty")
        words = len(d["narration"].split())
        if not 180 <= words <= 250:
            raise ValueError(f"{path}: narration word count {words}")
        if d.get("duration_target") != "65-80s":
            raise ValueError(f"{path}: unexpected duration target")
        if d.get("editorial_status") != "RESEARCH_DRAFT_UNAPPROVED" or d.get("media_rights_status") != "NOT_VERIFIED":
            raise ValueError(f"{path}: drafts must remain unapproved and rights unresolved")
        if d.get("publishing_status") != "FORBIDDEN_UNTIL_RIGHTS_AND_EDITORIAL_GATES":
            raise ValueError(f"{path}: publication guard missing")
        family = d["topic_family"].strip().casefold()
        if not family or family in used:
            raise ValueError(f"{path}: duplicate or missing topic_family")
        used.add(family)
        if not isinstance(d["sources"], list):
            raise ValueError(f"{path}: invalid source list")
        for source in d["sources"]:
            if not isinstance(source, dict) or not source.get("name"):
                raise ValueError(f"{path}: missing named source")
            url = urlsplit(source.get("url", ""))
            if url.scheme != "https" or url.hostname not in ALLOWED_SOURCE_HOSTS or url.username or url.password:
                raise ValueError(f"{path}: unverified source host")
        if not isinstance(d["media"], list):
            raise ValueError(f"{path}: invalid media")
        for media in d["media"]:
            if (not isinstance(media, dict)
                    or media.get("asset_status") != "NOT_SELECTED"
                    or media.get("license_note") != "RIGHTS_UNVERIFIED_NO_RENDER"
                    or any(x in media for x in ("path", "commons_title", "flow_asset", "sha256"))):
                raise ValueError(f"{path}: unapproved media must not be renderable")
        if (Path("content") / f"{date}{suffix}.json").exists():
            raise ValueError(f"{path}: live content file already exists; reconcile manually")
        print(f"RESEARCH_SCHEMA_PASS={path} WORDS={words} MEDIA_RIGHTS=BLOCKED RENDER=NO")
    if len(paths) != 3 or len(dates) != 1:
        raise ValueError("Expect one day's three separate research drafts")
    print("STRUCTURE_ONLY_PASS FACT_SOURCE_REVIEW=MANUAL CONTENT_READINESS=BLOCKED")


if __name__ == "__main__":
    check(sys.argv[1:])
