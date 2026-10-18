"""R48 offline approval attestation contract. Not connected to rendering or publishing."""
import hashlib
import hmac
import json

def canonical(payload):
    return json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")

def verify(record, key, trusted_digest):
    if not isinstance(record,dict) or not isinstance(key,bytes) or len(key)<32:
        return False
    if set(record)!={"payload","signature"} or not isinstance(record["payload"],dict):
        return False
    p=record["payload"]
    if set(p)!={"dossier_id","content_sha256","editor_id","decision","timestamp","source_review","media_rights"}:
        return False
    if p["decision"]!="APPROVED" or p["source_review"] is not True or p["media_rights"] is not True:
        return False
    if not isinstance(p["content_sha256"],str) or len(p["content_sha256"])!=64 or any(c not in "0123456789abcdef" for c in p["content_sha256"]):
        return False
    if not hmac.compare_digest(p["content_sha256"],trusted_digest):
        return False
    if any(not isinstance(p[k],str) or not p[k].strip() for k in ("dossier_id","editor_id","timestamp")):
        return False
    sig=record["signature"]
    if not isinstance(sig,str) or len(sig)!=64:
        return False
    expected=hmac.new(key,canonical(p),hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected,sig)

def gate(record,key,digest):
    # The trust/key custody and verified editor identity registry do not exist yet.
    # Verification of a syntactically valid signature cannot grant release.
    return {"cryptographic_contract_valid":verify(record,key,digest),
            "release_authorized":False,"publish_authorized":False,
            "reason":"TRUSTED_EDITOR_REGISTRY_NOT_CONFIGURED"}
