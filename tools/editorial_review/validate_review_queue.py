"""P3.32R20: safe review queue is never approval input."""
import json
from pathlib import Path

def check_queue(q):
    if not isinstance(q,dict) or q.get("schema")!="p332r20_evidence_queue_v1" or q.get("approved") is not False or q.get("publishable") is not False:
        raise ValueError("QUEUE_NOT_SAFE")
    ds=q.get("dossiers")
    if not isinstance(ds,list) or len(ds)!=3 or len({d.get("id") for d in ds})!=3:
        raise ValueError("THREE_DISTINCT_DOSSIERS")
    for d in ds:
        if d.get("status")!="UNAPPROVED":raise ValueError("APPROVED_DOSSIER_FORBIDDEN")
        claims=d.get("claims")
        if not isinstance(claims,list) or not claims:raise ValueError("MISSING_CLAIMS")
        for cl in claims:
            if cl.get("review")!="PENDING":raise ValueError("CLAIM_REVIEW_INVALID")
            if not isinstance(cl.get("blockers"),list) or not cl["blockers"]:raise ValueError("BLOCKER_REQUIRED")
            if not isinstance(cl.get("sources"),list) or not cl["sources"]:raise ValueError("SOURCE_REQUIRED")
            for s in cl["sources"]:
                if s.get("independent_verified") is not False:raise ValueError("INDEPENDENCE_UNVERIFIED")
    return "QUEUE_REVIEW_REQUIRED_PUBLISH_NO"

if __name__=="__main__":
    data=json.loads((Path(__file__).parent/"P332R20_EVIDENCE_QUEUE_UNAPPROVED.json").read_text(encoding="utf-8"))
    print(check_queue(data))
