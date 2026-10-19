"""Offline candidate discovery queue, not factual approval or publication.

Produces dated research requests with explicit evidence and media-rights gates.
Does not invent events or create publishable content.
"""
import argparse,json
from datetime import date,timedelta
from pathlib import Path
SLOTS=("principal","detalle","sabias")
def build(day):
    date.fromisoformat(day)
    return {"date":day,"status":"RESEARCH_REQUIRED","publishable":False,
      "candidates":[{"slot":slot,"topic":None,"verified_facts":[],"independent_sources":[],
                      "media_rights":[],"editorial_status":"PENDING"} for slot in SLOTS]}
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--date",required=True);ap.add_argument("--out",required=True);args=ap.parse_args()
    p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(build(args.date),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("RESEARCH_QUEUE_CREATED=YES APPROVED=NO")
if __name__=="__main__":main()
