#!/usr/bin/env python3
"""Offline research structure gate. NOT an independent fact check or publication approval."""
import argparse
import datetime
import json
from pathlib import Path
from urllib.parse import urlparse

SLOTS = ("10:00", "16:00", "19:00")
SCHEMA = "p332r8_research_v1"
FLAGS = ("evidence_review_approved", "publication_approved", "media_license_approved")

def check(packet, brand, date):
    if not isinstance(packet, dict) or packet.get("schema") != SCHEMA:
        raise ValueError("SCHEMA_MISMATCH")
    datetime.date.fromisoformat(date)
    if packet.get("brand") != brand or packet.get("date") != date:
        raise ValueError("DATE_OR_BRAND_MISMATCH")
    if any(packet.get(k) is not False for k in FLAGS):
        raise ValueError("UNSAFE_ROOT_APPROVAL")
    dossiers = packet.get("dossiers")
    if not isinstance(dossiers, list) or len(dossiers) != 3:
        raise ValueError("THREE_DOSSIERS_REQUIRED")
    topics = set()
    for index, d in enumerate(dossiers):
        if not isinstance(d, dict) or d.get("slot") != SLOTS[index] or d.get("date") != date:
            raise ValueError("SLOT_DATE_MISMATCH")
        topic = str(d.get("topic", "")).strip().casefold()
        if not topic or topic in topics:
            raise ValueError("DUPLICATE_OR_EMPTY_TOPIC")
        topics.add(topic)
        if any(d.get(k) is not False for k in FLAGS):
            raise ValueError("UNSAFE_DOSSIER_APPROVAL")
        if d.get("fact_check_status") != "SOURCE_TEXT_CROSSCHECKED_NOT_FORMALLY_APPROVED":
            raise ValueError("MISSING_REVIEW_STATUS")
        event_date = d.get("event_date")
        if brand == "history" or event_date is not None:
            try:
                datetime.date.fromisoformat(str(event_date))
            except (ValueError, TypeError):
                raise ValueError("INVALID_EVENT_DATE")
        if brand == "history" and str(event_date)[5:] != date[5:]:
            raise ValueError("NOT_SAME_DAY_ANNIVERSARY")
        sources = d.get("sources")
        if not isinstance(sources, list) or len(sources) < 2:
            raise ValueError("SECOND_SOURCE_REQUIRED")
        orgs = set()
        for source in sources:
            if not isinstance(source, dict):
                raise ValueError("MALFORMED_SOURCE")
            org = str(source.get("organization", "")).strip().casefold()
            if not org:
                raise ValueError("MISSING_SOURCE_ORGANIZATION")
            orgs.add(org)
            parsed = urlparse(str(source.get("url", "")))
            if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
                raise ValueError("UNSAFE_SOURCE_URL")
            if not str(source.get("locator", "")).strip():
                raise ValueError("MISSING_FACT_LOCATOR")
            facts = source.get("facts")
            if not isinstance(facts, list) or not facts or any(
                not isinstance(f, str) or len(f.strip()) < 12 for f in facts
            ):
                raise ValueError("MISSING_ATOMIC_FACTS")
        if len(orgs) < 2:
            raise ValueError("NOT_INDEPENDENT_ORGANIZATIONS")
    return "RESEARCH_STRUCTURE_PASS_APPROVAL_NO"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--brand", choices=("history", "dogs"), required=True)
    p.add_argument("--date", required=True)
    args = p.parse_args()
    try:
        packet = json.loads(Path(args.input).read_text(encoding="utf-8"))
        print(check(packet, args.brand, args.date))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print("BLOCKED_" + str(exc).replace(" ", "_"))
        raise SystemExit(2)
    print("FACTUAL_APPROVAL=NO PUBLICATION=NO MEDIA_RIGHTS_APPROVED=NO")

if __name__ == "__main__":
    main()
