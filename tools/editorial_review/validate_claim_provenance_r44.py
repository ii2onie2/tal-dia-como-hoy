"""P3.32R44 stronger claim/source structure checks; no automatic fact approval."""
from urllib.parse import urlsplit
import ipaddress

def validate_claim_provenance(matrix):
    from validate_claim_matrix import audit
    audit(matrix)
    for dossier in matrix["dossiers"]:
        for claim in dossier["claims"]:
            if claim.get("approved") is not False or claim.get("publishable") is not False:
                raise ValueError("CLAIM_APPROVAL_FORBIDDEN")
            domains=set()
            for cite in claim["citations"]:
                url=str(cite["url"])
                try:
                    u=urlsplit(url)
                    host=(u.hostname or "").lower().rstrip(".")
                    if u.scheme!="https" or not host or u.username or u.password or u.fragment or u.port not in (None,443):
                        raise ValueError("INVALID_SOURCE_URL")
                    if host in ("localhost",) or host.endswith((".localhost",".local",".internal")):
                        raise ValueError("PRIVATE_SOURCE_HOST")
                    try:
                        ipaddress.ip_address(host)
                        raise ValueError("IP_SOURCE_HOST_NOT_ALLOWED")
                    except ValueError as e:
                        if str(e)=="IP_SOURCE_HOST_NOT_ALLOWED": raise
                    if "." not in host or not all(host.split(".")):
                        raise ValueError("INVALID_SOURCE_HOST")
                except (ValueError, TypeError) as e:
                    raise ValueError("INVALID_SOURCE_URL") from e
                domains.add(host)
                if len(str(cite["support_excerpt"]).strip())<20:
                    raise ValueError("EXCERPT_TOO_SHORT")
            if len(domains)<2:
                raise ValueError("DISTINCT_SOURCE_HOSTS_REQUIRED")
    return "CLAIM_PROVENANCE_STRUCTURE_PASS_FACTUAL_APPROVAL_NO"
