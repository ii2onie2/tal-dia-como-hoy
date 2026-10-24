#!/usr/bin/env python3
"""P3.32R33: offline transport contract. No network, TikTok, or production calls."""
import hashlib
import hmac
import json
import os
import sys

ACCOUNT = "taldiacomohoy09"
SLOTS = frozenset(("principal", "detalle", "sabias"))

def prepare(envelope, key):
    if not isinstance(envelope, dict):
        raise ValueError("envelope must be object")
    if set(envelope) != {"account", "slot", "date", "content_sha256", "approved", "publishable", "dry_run"}:
        raise ValueError("unexpected or missing fields")
    if envelope["account"] != ACCOUNT:
        raise ValueError("account denied")
    if envelope["slot"] not in SLOTS:
        raise ValueError("slot denied")
    import re
    if not isinstance(envelope["date"], str) or not re.fullmatch(r"20[0-9]{2}-[0-9]{2}-[0-9]{2}", envelope["date"]):
        raise ValueError("invalid date")
    if not isinstance(envelope["content_sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", envelope["content_sha256"]):
        raise ValueError("invalid digest")
    if envelope["approved"] is not True or envelope["publishable"] is not True:
        raise ValueError("editorial gate denied")
    if envelope["dry_run"] is not True:
        raise ValueError("R33 permits simulation only")
    if not isinstance(key, bytes) or len(key) < 32:
        raise ValueError("test signing key invalid")
    payload = json.dumps(envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    signature = hmac.new(key, payload, hashlib.sha256).hexdigest()
    return {"transport": "SIMULATED_ONLY", "payload_sha256": hashlib.sha256(payload).hexdigest(),
            "signature": signature, "account": ACCOUNT, "slot": envelope["slot"], "network_calls": 0}

def selftest():
    key = b"R33-synthetic-test-key-NOT-FOR-PRODUCTION-2026"
    sample = {"account": ACCOUNT, "slot": "principal", "date": "2026-10-18",
              "content_sha256": "a" * 64, "approved": True, "publishable": True, "dry_run": True}
    assert prepare(sample, key)["network_calls"] == 0
    for changes in (
        {"account": "tuperrofelizofficial"},
        {"account": "taldiacomohoy"},
        {"approved": False},
        {"publishable": False},
        {"dry_run": False},
        {"slot": "unknown"},
        {"date": "not-a-date"},
        {"content_sha256": "bad"},
        {"extra": "unexpected"},
    ):
        candidate = dict(sample, **changes)
        try:
            prepare(candidate, key)
        except ValueError:
            pass
        else:
            raise AssertionError("unsafe payload accepted: " + str(changes))
    assert prepare(sample, key)["signature"] == prepare(sample, key)["signature"]
    try:
        prepare(sample, b"weak")
    except ValueError:
        pass
    else:
        raise AssertionError("weak key accepted")
    print("P3.32R33=PASS; NEGATIVE_CASES=10; HTTP_CALLS=0; PRODUCTION_WRITE=NO; PUBLISH=NO")

if __name__ == "__main__":
    selftest()
