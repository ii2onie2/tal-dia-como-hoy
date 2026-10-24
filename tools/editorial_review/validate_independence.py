"""P3.32R22 nonpublishing source-independence assessment."""
import json
from pathlib import Path
from urllib.parse import urlsplit

def assess(q):
    if q.get("schema")!="p332r20_evidence_queue_v1" or q.get("approved") is not False or q.get("publishable") is not False:
        raise ValueError("FAIL_CLOSED_APPROVAL")
    ds=q.get("dossiers")
    if not isinstance(ds,list) or len(ds)!=3 or len({d.get("id") for d in ds})!=3: raise ValueError("DOSSIER_COUNT")
    result=[]
    for d in ds:
        if d.get("status")!="UNAPPROVED":raise ValueError("DOSSIER_STATUS")
        for claim in d.get("claims",[]):
            if claim.get("review")!="PENDING" or not claim.get("blockers"):raise ValueError("CLAIM_STATUS")
            sources=claim.get("sources",[])
            groups=set()
            for source in sources:
                if source.get("independent_verified") is not False:raise ValueError("UNJUSTIFIED_INDEPENDENCE_FLAG")
                url=source.get("url","")
                parsed=urlsplit(url)
                if parsed.scheme!="https" or not parsed.hostname:raise ValueError("INVALID_SOURCE")
                # Domain, hosting platform, or multiple URLs are NOT sufficient evidence of independence.
                group=source.get("editorial_control_group")
                if not isinstance(group,str) or not group.strip():continue
                if source.get("control_group_reviewed") is True:
                    groups.add(group.strip().casefold())
            result.append({"dossier":d["id"],"claim":claim.get("id"),"independent_groups_reviewed":len(groups),
                           "status":"PENDING_EDITORIAL_REVIEW","publishable":False})
    if len(result)!=3:raise ValueError("THREE_CLAIMS_REQUIRED")
    return {"schema":"p332r22_independence_report_v1","approved":False,"publishable":False,"claims":result}

def main():
    source=Path(__file__).parent/"P332R20_EVIDENCE_QUEUE_UNAPPROVED.json"
    report=assess(json.loads(source.read_text(encoding="utf-8")))
    print(json.dumps(report,sort_keys=True))
if __name__=="__main__":main()
