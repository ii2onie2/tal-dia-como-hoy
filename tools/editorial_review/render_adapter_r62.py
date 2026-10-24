"""R62 dry-run adapter for the real render workflow; never executes rendering."""
import json
from pathlib import Path
from prerender_gate_r47 import assess

def preflight(content_dir, evidence_queue, date):
    decision=assess(content_dir,evidence_queue,date)
    return {"allowed":False,"render_invoked":False,"publish_invoked":False,
            "reasons":decision["reasons"],"mode":"ISOLATED_DRY_RUN"}

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--content-dir",required=True)
    p.add_argument("--queue",required=True)
    p.add_argument("--date",required=True)
    a=p.parse_args()
    r=preflight(a.content_dir,a.queue,a.date)
    print(json.dumps(r,sort_keys=True))
    raise SystemExit(2 if not r["allowed"] else 0)
