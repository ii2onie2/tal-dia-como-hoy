#!/usr/bin/env python3
import json, pathlib, sys
HISTORY=pathlib.Path("content/published_history.json")
def main():
    files=sys.argv[1:]
    history=json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else []
    for name in files:
        d=json.loads(pathlib.Path(name).read_text(encoding="utf-8"))
        history=[x for x in history if x.get("date") != d.get("date") or x.get("series") != d.get("series")]
        history.append({
            "date":d.get("date"),"series":d.get("series"),"title":d.get("title"),
            "subject":d.get("subject"),"principal_person":d.get("principal_person"),
            "topic_family":d.get("topic_family"),"format":d.get("format"),
            "hook_pattern":d.get("hook_pattern"),"duration_target":d.get("duration_target")
        })
    HISTORY.write_text(json.dumps(history[-365:],ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
if __name__=="__main__": main()
