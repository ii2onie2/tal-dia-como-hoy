"""Pre-TikTok operational readiness: inventory, rights, editorial gates and alerts.
No generation, authentication, network I/O, rendering or publication.
"""
import argparse
import datetime
import json
from pathlib import Path

SLOTS=("", "-detalle", "-sabias")

def audit(root, day):
    datetime.date.fromisoformat(day)
    root=Path(root)
    results=[]
    for suffix in SLOTS:
        name=f"{day}{suffix}.json"
        path=root/name
        entry={"file":name,"present":path.is_file(),"content_valid":False,
               "sources_present":False,"media_rights_verified":False,
               "editorial_approved":False,"ready_for_render":False}
        if path.is_file():
            try:
                obj=json.loads(path.read_text(encoding="utf-8"))
                entry["content_valid"]=isinstance(obj,dict) and obj.get("date")==day and bool(obj.get("narration"))
                from urllib.parse import urlsplit
                sources=obj.get("sources",[])
                hosts=set()
                if isinstance(sources,list):
                    for source in sources:
                        if isinstance(source,dict) and isinstance(source.get("url"),str):
                            url=urlsplit(source["url"])
                            if url.scheme=="https" and url.hostname and "." in url.hostname and not url.username and not url.password:
                                hosts.add(url.hostname.lower())
                # Two distinct domains are leads for review, not proof of editorial independence.
                entry["sources_present"]=len(hosts)>=2
                media=obj.get("media")
                # Never infer rights from Commons URL or descriptive text.
                entry["media_rights_verified"]=bool(media) and isinstance(media,list) and all(
                    isinstance(m,dict) and m.get("rights_review")=="VERIFIED"
                    and bool(m.get("license")) and bool(m.get("attribution"))
                    for m in media)
                # No trusted review registry is configured. Fail closed.
            except (OSError,ValueError,TypeError):
                pass
        results.append(entry)
    blockers=[]
    if any(not x["present"] for x in results):blockers.append("DAILY_CONTENT_MISSING")
    if any(x["present"] and not x["content_valid"] for x in results):blockers.append("CONTENT_INVALID")
    if any(x["present"] and not x["sources_present"] for x in results):blockers.append("FACT_SOURCES_INCOMPLETE")
    if any(x["present"] and not x["media_rights_verified"] for x in results):blockers.append("MEDIA_RIGHTS_UNVERIFIED")
    blockers.extend(["TRUSTED_EDITORIAL_APPROVAL_UNAVAILABLE","TIKTOK_DIRECT_POST_NOT_APPROVED","PUBLISHER_NOT_CONNECTED"])
    content_ready=all(x["content_valid"] and x["sources_present"] and x["media_rights_verified"] for x in results)
    # Media markers and distinct hosts are only preliminary checks; neither is trusted approval.
    stage="READY_FOR_INDEPENDENT_REVIEW" if content_ready else "CONTENT_INCOMPLETE"
    return {"day":day,"slots":results,"blockers":sorted(set(blockers)),
            "content_preflight_complete":content_ready,"preparation_stage":stage,
            "render_authorized":False,"publish_authorized":False,
            "tiktok_request_sent":False,"status":"BLOCKED"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root",default="content")
    p.add_argument("--date",required=True)
    p.add_argument("--out",default="pre_tiktok_readiness.json")
    a=p.parse_args()
    result=audit(a.root,a.date)
    Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("READINESS="+result["status"]+" BLOCKERS="+",".join(result["blockers"]))

if __name__=="__main__":main()
