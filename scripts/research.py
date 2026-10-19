#!/usr/bin/env python3
"""Discover historical candidates; never invent scripts or approve claims.

Stdlib-only, free Wikimedia endpoints. A second independent publisher's
evidence MUST be collected and reviewed before narration can be prepared.
"""
import argparse,json,urllib.request,urllib.parse,datetime,re
from pathlib import Path

UA="TalDiaComoHoyResearch/0.1 (editorial review; noncommercial prototype)"
def fetch(url,method="GET",data=None):
    req=urllib.request.Request(url,data=data,headers={"User-Agent":UA,"Accept":"application/json"},method=method)
    with urllib.request.urlopen(req,timeout=18) as response:
        return json.load(response)

def wikipedia(month,day):
    url=f"https://es.wikipedia.org/api/rest_v1/feed/onthisday/events/{month:02d}/{day:02d}"
    data=fetch(url)
    return [{"year":row.get("year"),"description":row.get("text",""),
             "source":"Wikimedia", "source_url":url,
             "pages":[{"title":p.get("title"),"url":p.get("content_urls",{}).get("desktop",{}).get("page")}
                      for p in row.get("pages",[])]} for row in data.get("events",[])]

def wikidata(month,day):
    # Candidate retrieval only. Q29: Spain. Properties may be incomplete.
    sparql="""SELECT DISTINCT ?item ?itemLabel ?date ?article (COUNT(DISTINCT ?sitelink) AS ?sitelinks) WHERE {
      ?item wdt:P585|wdt:P580 ?date .
      FILTER(MONTH(?date) = %d && DAY(?date) = %d)
      { ?item wdt:P17 wd:Q29 } UNION { ?item wdt:P276/wdt:P17 wd:Q29 }
      OPTIONAL { ?article schema:about ?item; schema:isPartOf <https://es.wikipedia.org/> . }
      OPTIONAL { ?sitelink schema:about ?item; schema:isPartOf ?site . FILTER(CONTAINS(STR(?site), "wikipedia.org")) }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "es,en". }
    } GROUP BY ?item ?itemLabel ?date ?article LIMIT 100"""%(month,day)
    url="https://query.wikidata.org/sparql?"+urllib.parse.urlencode({"query":sparql,"format":"json"})
    data=fetch(url)
    return [{"id":row.get("item",{}).get("value"),"title":row.get("itemLabel",{}).get("value"),
             "event_date":row.get("date",{}).get("value"),
             "wikipedia_languages":int(row.get("sitelinks",{}).get("value",0)),
             "page":row.get("article",{}).get("value"),"source":"Wikidata","source_url":url}
            for row in data.get("results",{}).get("bindings",[])]

def build(day,history):
    date=datetime.date.fromisoformat(day)
    history_text=history.read_text(encoding="utf-8").lower() if history.is_file() else ""
    candidates=[];errors=[]
    for source,fn in (("wikipedia",wikipedia),("wikidata",wikidata)):
        try:
            rows=fn(date.month,date.day)
            for row in rows:
                label=(row.get("title") or row.get("description") or "")
                if label and label.lower() in history_text: continue
                row["origin"]=source;row["approved"]=False
                # The Spain filter is verifiable only for Wikidata, Wikipedia remains suggestions.
                row["spain_relation_verified_by_query"]=source=="wikidata"
                candidates.append(row)
        except (OSError,ValueError,KeyError,TimeoutError) as exc:errors.append({"source":source,"error":type(exc).__name__})
    candidates.sort(key=lambda c:(c["origin"]!="wikidata",-c.get("wikipedia_languages",0)))
    return {"date":day,"candidates":candidates,"fetch_errors":errors,
            "claims":[],"script":None,"editorial_status":"RESEARCH_ONLY",
            "note":"Candidates are not facts. Every script claim requires two distinct publishers and excerpts."}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--date",required=True)
    ap.add_argument("--history",default="content/published_history.json")
    ap.add_argument("--out")
    args=ap.parse_args()
    out=Path(args.out or f"content/research/{args.date}.claims.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    result=build(args.date,Path(args.history))
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"candidates":len(result["candidates"]),"errors":result["fetch_errors"],
                      "approved":False,"output":str(out)}))
if __name__=="__main__":main()
