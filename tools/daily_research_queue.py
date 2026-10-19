"""Build a dated research queue from explicitly documented, unapproved evidence.

No live facts, editorial approvals, rendering or publishing are inferred.
"""
import argparse,json
from datetime import date
from pathlib import Path
SLOTS=("principal","detalle","sabias")
def build(day,evidence_path=None):
    date.fromisoformat(day)
    candidates=[]
    evidence={}
    if evidence_path is not None and Path(evidence_path).is_file():
        try:
            evidence=json.loads(Path(evidence_path).read_text(encoding="utf-8"))
        except (ValueError,OSError):
            evidence={}
    dossiers=evidence.get("dossiers",[]) if evidence.get("date")==day else []
    for index,slot in enumerate(SLOTS):
        dossier=dossiers[index] if isinstance(dossiers,list) and len(dossiers)>index else None
        claims=dossier.get("claims",[]) if isinstance(dossier,dict) else []
        sources=[{"publisher":s.get("publisher"),"url":s.get("url"),"verified":False}
                 for claim in claims if isinstance(claim,dict)
                 for s in claim.get("sources",[]) if isinstance(s,dict)]
        candidates.append({"slot":slot,"topic":dossier.get("id") if isinstance(dossier,dict) else None,
                           "claims_to_check":[c.get("text") for c in claims if isinstance(c,dict)],
                           "source_leads":sources,"verified_facts":[],
                           "independent_sources":[],"media_rights":[],
                           "editorial_status":"PENDING"})
    return {"date":day,"status":"RESEARCH_REQUIRED","publishable":False,"candidates":candidates}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--date",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--evidence",default="tools/editorial_review/P332R20_EVIDENCE_QUEUE_UNAPPROVED.json")
    a=p.parse_args()
    path=Path(a.out)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(build(a.date,a.evidence),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("RESEARCH_QUEUE_CREATED=YES APPROVED=NO")
if __name__=="__main__":main()
