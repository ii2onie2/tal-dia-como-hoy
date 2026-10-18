"""P3.32R11 claim-to-source audit gate; structural corroboration, never factual approval."""
import json
from pathlib import Path

def audit(matrix):
    if not isinstance(matrix, dict) or matrix.get("schema") != "p332r11_claim_matrix_v1":
        raise ValueError("BAD_MATRIX_SCHEMA")
    if matrix.get("approved") is not False or matrix.get("publishable") is not False:
        raise ValueError("APPROVAL_MUST_BE_FALSE")
    dossiers = matrix.get("dossiers")
    if not isinstance(dossiers, list) or len(dossiers) != 3:
        raise ValueError("EXACTLY_THREE_DOSSIERS")
    seen = set()
    for d in dossiers:
        if not isinstance(d, dict) or d.get("status") != "UNAPPROVED":
            raise ValueError("DOSSIER_UNAPPROVED_REQUIRED")
        key = d.get("id")
        if not isinstance(key, str) or not key or key in seen:
            raise ValueError("DUPLICATE_DOSSIER")
        seen.add(key)
        claims = d.get("claims")
        if not isinstance(claims, list) or not claims:
            raise ValueError("CLAIMS_REQUIRED")
        for claim in claims:
            if not isinstance(claim, dict) or not str(claim.get("text", "")).strip():
                raise ValueError("CLAIM_TEXT_REQUIRED")
            if claim.get("review_status") != "PENDING_HUMAN_REVIEW":
                raise ValueError("CLAIM_NOT_APPROVABLE")
            citations = claim.get("citations")
            if not isinstance(citations, list) or len(citations) < 2:
                raise ValueError("TWO_CITATIONS_REQUIRED")
            orgs = set()
            for cite in citations:
                if not isinstance(cite, dict):
                    raise ValueError("CITATION_OBJECT_REQUIRED")
                if any(not str(cite.get(field, "")).strip() for field in ("organization","url","locator","support_excerpt")):
                    raise ValueError("INCOMPLETE_CITATION")
                if not str(cite["url"]).startswith("https://"):
                    raise ValueError("HTTPS_CITATION_REQUIRED")
                orgs.add(cite["organization"].strip().casefold())
            if len(orgs) < 2:
                raise ValueError("INDEPENDENCE_NOT_ESTABLISHED")
    return "CLAIM_CITATION_STRUCTURE_PASS_FACTUAL_APPROVAL_NO"

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        raise SystemExit("usage: validate_claim_matrix.py path.json")
    try:
        result=audit(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
        print(result)
    except (OSError, ValueError, TypeError) as e:
        print("BLOCKED:", e)
        raise SystemExit(2)
