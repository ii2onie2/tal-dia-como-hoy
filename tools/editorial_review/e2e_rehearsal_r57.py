"""P3.32R57 end-to-end nonpublishing rehearsal: evidence -> release -> render -> transfer."""
import json
from pathlib import Path
from prerender_gate_r47 import assess as assess_release

def rehearse(content_dir, evidence_queue, date):
    release=assess_release(content_dir,evidence_queue,date)
    result={"date":date,"editorial_gate":release,"render_attempted":False,
            "video_created":False,"transfer_attempted":False,"publish_attempted":False}
    if release["render_allowed"] or release["publish_allowed"]:
        raise AssertionError("UNAUTHORIZED_RELEASE_IN_REHEARSAL")
    return result

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--content-dir",required=True)
    p.add_argument("--evidence-queue",required=True)
    p.add_argument("--date",required=True)
    args=p.parse_args()
    result=rehearse(args.content_dir,args.evidence_queue,args.date)
    print(json.dumps(result,sort_keys=True))
