"""R49 offline review registry verifier. Always non-releasing."""
from approval_contract_r48 import verify

def assess(record, key, digest, registry, seen):
    if not verify(record, key, digest):
        return {"valid":False,"reason":"INVALID_SIGNATURE_OR_PAYLOAD","release":False}
    p=record["payload"]
    reviewer=p["editor_id"]
    if reviewer not in registry or registry[reviewer] != "ACTIVE_REVIEWER":
        return {"valid":False,"reason":"UNTRUSTED_REVIEWER","release":False}
    if p["dossier_id"] in seen:
        return {"valid":False,"reason":"REPLAY_OR_DUPLICATE_DOSSIER","release":False}
    return {"valid":True,"reason":"OFFLINE_CONTRACT_ONLY","release":False}
