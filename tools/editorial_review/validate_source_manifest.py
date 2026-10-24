"""P3.32R13: verify a manually collected source manifest, no network or approval."""
from urllib.parse import urlsplit
import ipaddress

def check_manifest(doc):
    if not isinstance(doc,dict) or doc.get("schema")!="p332r13_source_manifest_v1":
        raise ValueError("INVALID_SCHEMA")
    if doc.get("approved") is not False or doc.get("publishable") is not False:
        raise ValueError("APPROVAL_FORBIDDEN")
    records=doc.get("sources")
    if not isinstance(records,list) or not records:
        raise ValueError("MISSING_SOURCES")
    ids=set()
    for r in records:
        if not isinstance(r,dict):raise ValueError("INVALID_RECORD")
        key=r.get("id")
        if not isinstance(key,str) or not key.strip() or key in ids:raise ValueError("DUPLICATE_ID")
        ids.add(key)
        url=r.get("url")
        if not isinstance(url,str):raise ValueError("INVALID_URL")
        p=urlsplit(url)
        if p.scheme!="https" or not p.hostname or p.username or p.password or p.fragment:
            raise ValueError("UNSAFE_URL")
        host=p.hostname.strip(".")
        if host in ("localhost",) or host.endswith((".localhost",".local",".internal")):
            raise ValueError("PRIVATE_HOST")
        try:
            ipaddress.ip_address(host)
            raise ValueError("IP_HOST_NOT_ALLOWED")
        except ValueError as e:
            if str(e)=="IP_HOST_NOT_ALLOWED":raise
        for field in ("organization","claim_id","locator","accessed_utc","source_type"):
            if not isinstance(r.get(field),str) or not r[field].strip():
                raise ValueError("MISSING_"+field.upper())
        if r.get("verified_by_human") is not False:raise ValueError("REVIEW_MUST_BE_FALSE")
    return "MANIFEST_STRUCTURE_PASS_SOURCES_NOT_RETRIEVED_APPROVAL_NO"
