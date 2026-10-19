"""Create the three daily draft slots only from three pre-reviewed inputs.

Inputs are date-specific and must retain their own independent source review.
This utility NEVER invents history, auto-approves, renders or publishes.
"""
import argparse,json,shutil
from pathlib import Path

SLOTS=("", "-detalle", "-sabias")
def prepare(source_dir,out_dir,date):
    source_dir=Path(source_dir);out_dir=Path(out_dir)
    result={"date":date,"created":[],"blocked":[],"publish_authorized":False}
    for suffix in SLOTS:
        name=f"{date}{suffix}.json"
        src=source_dir/name
        dst=out_dir/name
        if not src.is_file():
            result["blocked"].append(f"MISSING_REVIEWED_DRAFT:{name}")
            continue
        try:
            obj=json.loads(src.read_text(encoding="utf-8"))
        except (ValueError,OSError):
            result["blocked"].append(f"INVALID_DRAFT:{name}")
            continue
        if not isinstance(obj,dict) or obj.get("date")!=date or not obj.get("narration") or not obj.get("sources"):
            result["blocked"].append(f"INCOMPLETE_DRAFT:{name}")
            continue
        # Source of truth stays in review directory; create a draft only.
        out_dir.mkdir(parents=True,exist_ok=True)
        dst.write_text(json.dumps({**obj,"editorial_approved":False,"publishable":False},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        result["created"].append(name)
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--source",required=True);p.add_argument("--out",default="staging_content");p.add_argument("--date",required=True);a=p.parse_args()
    result=prepare(a.source,a.out,a.date)
    print(json.dumps(result,ensure_ascii=False))
    raise SystemExit(0 if not result["blocked"] else 2)
