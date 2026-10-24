#!/usr/bin/env python3
"""P3.32R12 nonpublishing daily audit: inputs are evidence files, never fabricated."""
import argparse
import datetime
import json
from pathlib import Path
from validate_claim_matrix import audit

def run(date, evidence_dir, output_dir):
    day=datetime.date.fromisoformat(date)
    if day.isoformat()!=date: raise ValueError("NONCANONICAL_DATE")
    if not output_dir.is_relative_to(Path(".")) and not output_dir.is_absolute():
        raise ValueError("INVALID_PATH")
    input_path=evidence_dir / (date+".json")
    report={"schema":"p332r12_audit_v1","date":date,"status":"BLOCKED",
            "approved":False,"publishable":False,"tiktok_publication":False,
            "evidence_input":input_path.name,"reason":"EVIDENCE_NOT_PROVIDED"}
    try:
        matrix=json.loads(input_path.read_text(encoding="utf-8"))
        audit(matrix)
        report["reason"]="STRUCTURE_VALID_HUMAN_FACT_CHECK_REQUIRED"
    except (OSError,ValueError,TypeError,KeyError) as e:
        report["reason"]="GATE_BLOCKED_"+type(e).__name__
    output_dir.mkdir(parents=True,exist_ok=True)
    dest=output_dir / (date+".json")
    dest.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--date",required=True)
    p.add_argument("--evidence-dir",type=Path,default=Path("tools/editorial_review/evidence"))
    p.add_argument("--output-dir",type=Path,default=Path("audit-output"))
    a=p.parse_args()
    result=run(a.date,a.evidence_dir,a.output_dir)
    print(json.dumps(result,sort_keys=True))
    if result["reason"]!="STRUCTURE_VALID_HUMAN_FACT_CHECK_REQUIRED":raise SystemExit(2)

if __name__=="__main__":main()
