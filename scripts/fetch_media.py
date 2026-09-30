#!/usr/bin/env python3
import argparse,json,pathlib,requests,urllib.parse

API="https://commons.wikimedia.org/w/api.php"

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--content",required=True); ap.add_argument("--out",default="media"); args=ap.parse_args()
    data=json.loads(pathlib.Path(args.content).read_text(encoding="utf-8"))
    out=pathlib.Path(args.out); out.mkdir(parents=True,exist_ok=True)
    downloaded=[]
    for i,item in enumerate(data.get("media") or [],1):
        if not isinstance(item,dict): continue
        title=item.get("commons_title")
        if not title: continue
        params={"action":"query","format":"json","prop":"imageinfo","iiprop":"url|extmetadata","titles":title}
        j=requests.get(API,params=params,timeout=30).json()
        page=next(iter(j.get("query",{}).get("pages",{}).values()),{})
        info=(page.get("imageinfo") or [{}])[0]
        url=info.get("url")
        if not url: continue
        ext=pathlib.Path(urllib.parse.urlparse(url).path).suffix or ".jpg"
        dest=out/f"{i:02d}{ext}"
        r=requests.get(url,timeout=60); r.raise_for_status(); dest.write_bytes(r.content)
        downloaded.append({"path":str(dest),"source":url,"metadata":info.get("extmetadata",{})})
        item["path"]=str(dest)
    pathlib.Path(args.content).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    pathlib.Path(out/"credits.json").write_text(json.dumps(downloaded,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__": main()
