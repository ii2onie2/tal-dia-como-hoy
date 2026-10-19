#!/usr/bin/env python3
"""Conservative Wikimedia Commons rights review. Metadata never equals legal approval."""
import argparse,datetime,html,json,re,urllib.parse,urllib.request
from pathlib import Path
UA="TalDiaComoHoyRights/0.1 (attribution audit)"
def plain(value):
    return re.sub(r"<[^>]+>"," ",html.unescape(value or "")).strip()
def check(title):
    url="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode({
        "action":"query","prop":"imageinfo","iiprop":"extmetadata|url",
        "titles":"File:"+title.removeprefix("File:"),"format":"json"})
    request=urllib.request.Request(url,headers={"User-Agent":UA})
    with urllib.request.urlopen(request,timeout=18) as response:
        data=json.load(response)
    pages=data.get("query",{}).get("pages",{})
    page=next(iter(pages.values()),{})
    info=(page.get("imageinfo") or [{}])[0]
    meta=info.get("extmetadata",{})
    def get(key):return plain(meta.get(key,{}).get("value",""))
    license_name=get("LicenseShortName")
    restriction=" ".join((get("Restrictions"),get("UsageTerms")))
    allowed=bool(re.match(r"^(CC0|CC BY(?:-SA)?(?: |-|$)|Public domain|PD-)",license_name,re.I))
    prohibited=bool(re.search(r"(non.?commercial|no.?derivatives|fair use|personality rights|trademark|model release|restricted)",restriction+" "+license_name,re.I))
    author=get("Artist");credit=get("Credit")
    compliant=bool(info.get("url") and allowed and not prohibited and (author or credit))
    return {"file":title,"status":"METADATA_PRECHECK_PASS" if compliant else "REJECTED_FOR_AUTOMATION",
            "manual_rights_approval_required":True,"license":license_name,
            "license_full":get("License"),"artist":author,"credit":credit,
            "attribution_required":get("AttributionRequired"),"usage_terms":get("UsageTerms"),
            "restrictions":get("Restrictions"),"file_url":info.get("descriptionurl"),
            "download_url":info.get("url"),"metadata_api":url,
            "credit_line":f"{author or credit} — {license_name} — {info.get('descriptionurl','')}" if compliant else None,
            "checked_at":datetime.datetime.now(datetime.timezone.utc).isoformat()}
def main():
    p=argparse.ArgumentParser();p.add_argument("--file",action="append",required=True);p.add_argument("--out",required=True);a=p.parse_args()
    records=[]
    for title in a.file:
        try:records.append(check(title))
        except (OSError,ValueError,KeyError,TimeoutError) as e:
            records.append({"file":title,"status":"ERROR","error":type(e).__name__,
                            "manual_rights_approval_required":True})
    out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps({"images":records,"approved":False},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"images":len(records),"metadata_pass":sum(x["status"]=="METADATA_PRECHECK_PASS" for x in records),"approved":False}))
if __name__=="__main__":main()
