"""Offline-only replay and trust-policy rehearsal. No release authority."""
from datetime import datetime,timezone
from approval_contract_r48 import verify

def assess(record,key,digest,seen,allowed_editors,now):
    if not verify(record,key,digest):
        return "DENY_INVALID_ATTESTATION"
    p=record["payload"]
    if p["editor_id"] not in allowed_editors:
        return "DENY_UNTRUSTED_EDITOR"
    try:
        timestamp=datetime.fromisoformat(p["timestamp"].replace("Z","+00:00"))
        if timestamp.tzinfo is None or abs((now-timestamp).total_seconds())>300:
            return "DENY_STALE_ATTESTATION"
    except (TypeError,ValueError,OverflowError):
        return "DENY_INVALID_TIMESTAMP"
    ident=(p["dossier_id"],p["content_sha256"],p["signature"] if "signature" in p else record["signature"])
    if ident in seen:
        return "DENY_REPLAY"
    # Simulation only. Callers may record the tuple for replay rejection.
    # Positive cryptographic validation never authorizes publishing.
    return "SIMULATED_VALIDITY_ONLY_RELEASE_DENIED"
