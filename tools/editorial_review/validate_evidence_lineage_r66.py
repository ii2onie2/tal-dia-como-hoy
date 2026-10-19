"""R66 research structure gate: never approves content or permits publication."""
import datetime
import json
from pathlib import Path
from urllib.parse import urlsplit

def audit(p, brand="history", date="2026-10-17"):
    if not isinstance(p, dict) or p.get("schema") != "p332r66_evidence_v1":
        raise ValueError("SCHEMA")
    if p.get("brand") != brand or p.get("content_date") != date:
        raise ValueError("BRAND_OR_DATE")
    datetime.date.fromisoformat(date)
    datetime.date.fromisoformat(p["checked_on"])
    if p.get("status") != "UNAPPROVED" or any(
        p.get(k) is not False for k in ("approved", "publishable", "human_signoff", "media_rights_verified")
    ):
        raise ValueError("ROOT_RELEASE_DENIED")
    dossiers = p.get("dossiers")
    if not isinstance(dossiers, list) or len(dossiers) != 3:
        raise ValueError("THREE_DOSSIERS")
    origins = {}
    for d in dossiers:
        if d.get("status") != "UNAPPROVED" or any(
            d.get(k) is not False for k in ("approved", "publishable", "media_rights_verified")
        ):
            raise ValueError("DOSSIER_RELEASE_DENIED")
        if brand == "history":
            datetime.date.fromisoformat(d["event_date"])
            if d["event_date"][5:] != date[5:]:
                raise ValueError("ANNIVERSARY_MISMATCH")
        if not d.get("blockers") or d["id"] in origins:
            raise ValueError("BLOCKERS_OR_DUPLICATE")
        claim = d["claim"]
        if claim.get("review_status") != "PENDING_HUMAN_REVIEW" or any(
            claim.get(k, False) is not False for k in ("approved", "publishable")
        ):
            raise ValueError("CLAIM_RELEASE_DENIED")
        sources = claim.get("sources")
        if not isinstance(sources, list) or len(sources) < 2:
            raise ValueError("TWO_SOURCES")
        direct = set()
        for s in sources:
            u = urlsplit(s["url"])
            if u.scheme != "https" or not u.hostname or u.username or u.password:
                raise ValueError("UNSAFE_URL")
            if not all(isinstance(s.get(k), str) and s[k].strip()
                       for k in ("publisher", "lineage", "locator")):
                raise ValueError("INCOMPLETE_SOURCE")
            if s.get("scope") not in ("DIRECT", "PARTIAL", "REPRINT", "CONTEXT_ONLY"):
                raise ValueError("SOURCE_SCOPE")
            if s["scope"] == "DIRECT":
                direct.add(s["lineage"].casefold())
        origins[d["id"]] = len(direct)
    return {"result": "STRUCTURE_PASS_NO_APPROVAL", "candidate_lineages_not_verified": origins,
            "render_authorized": False, "publish_authorized": False}

if __name__ == "__main__":
    import argparse
    a = argparse.ArgumentParser()
    a.add_argument("--input", required=True)
    a.add_argument("--brand", choices=("history", "dogs"), required=True)
    a.add_argument("--date", required=True)
    v = a.parse_args()
    try:
        print(json.dumps(audit(json.loads(Path(v.input).read_text()), v.brand, v.date)))
    except (OSError, ValueError, TypeError, KeyError) as error:
        print("BLOCKED:", error)
        raise SystemExit(2)
