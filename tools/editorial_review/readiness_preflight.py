"""P3.32R23 observable input-only readiness; never render or publish."""
from pathlib import Path
import json
import datetime

def inspect_content(root, date):
    datetime.date.fromisoformat(date)
    names=[f"{date}.json",f"{date}-detalle.json",f"{date}-sabias.json"]
    result={"date":date,"ready":False,"publishing_authorized":False,"files":[]}
    for name in names:
        p=Path(root)/name
        entry={"name":name,"exists":p.is_file(),"valid_json":False,"date_matches":False}
        if entry["exists"]:
            try:
                data=json.loads(p.read_text(encoding="utf-8"))
                entry["valid_json"]=isinstance(data,dict)
                entry["date_matches"]=entry["valid_json"] and data.get("date")==date
            except (ValueError,OSError):pass
        result["files"].append(entry)
    result["ready"]=all(x["exists"] and x["valid_json"] and x["date_matches"] for x in result["files"])
    return result
