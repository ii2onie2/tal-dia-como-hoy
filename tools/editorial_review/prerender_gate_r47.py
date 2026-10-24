"""R47 isolated pre-render gate. Never an editorial approval engine."""
import json
from pathlib import Path
from readiness_preflight import inspect_content

def assess(content_dir, queue_file, date):
    readiness=inspect_content(content_dir,date)
    reasons=[]
    if not readiness["ready"]:
        reasons.append("CONTENT_NOT_READY")
    try:
        queue=json.loads(Path(queue_file).read_text(encoding="utf-8"))
    except (OSError,ValueError):
        queue={}
        reasons.append("EVIDENCE_QUEUE_UNREADABLE")
    if queue.get("date")!=date:
        reasons.append("EVIDENCE_DATE_MISMATCH")
    dossiers=queue.get("dossiers")
    if not isinstance(dossiers,list) or len(dossiers)!=3:
        reasons.append("THREE_DOSSIERS_REQUIRED")
    else:
        for dossier in dossiers:
            if not isinstance(dossier,dict) or dossier.get("status")!="APPROVED":
                reasons.append("DOSSIER_NOT_APPROVED")
                continue
            claims=dossier.get("claims")
            if not isinstance(claims,list) or not claims:
                reasons.append("CLAIMS_MISSING")
                continue
            for claim in claims:
                if not isinstance(claim,dict) or claim.get("review")!="APPROVED":
                    reasons.append("CLAIM_REVIEW_MISSING")
                    break
                src=claim.get("sources",[])
                if not isinstance(src,list) or len(src)<2 or any(not isinstance(s,dict) or s.get("independent_verified") is not True for s in src):
                    reasons.append("INDEPENDENT_EVIDENCE_MISSING")
                    break
    if queue.get("approved") is not True or queue.get("publishable") is not True:
        reasons.append("EDITORIAL_RELEASE_MISSING")
    # Intentional hard block: no authoritative, independently verified sign-off
    # registry is connected. A self-authored JSON must NEVER unlock rendering.
    reasons.append("TRUSTED_APPROVAL_REGISTRY_UNAVAILABLE")
    return {"render_allowed":False,"publish_allowed":False,"reasons":sorted(set(reasons))}
