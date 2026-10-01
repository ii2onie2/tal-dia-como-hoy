#!/usr/bin/env python3
import json, pathlib, re, sys

HISTORY=pathlib.Path("content/published_history.json")
formats=[
"chronological_event","historical_person","battle_or_conflict","place_with_history",
"before_after","three_facts","mystery","invention_science_culture","forgotten_story","historical_object_word_custom"
]

def main():
    content_path=pathlib.Path(sys.argv[1])
    d=json.loads(content_path.read_text(encoding="utf-8"))
    history=[]
    if HISTORY.exists():
        history=json.loads(HISTORY.read_text(encoding="utf-8"))
    recent=history[-7:]
    used_formats={x.get("format") for x in recent}
    title=(d.get("title") or "").lower()
    explicit_format=d.get("format")
    if explicit_format in formats:
        fmt=explicit_format
    elif any(k in title for k in ["batalla","guerra","conflicto"]): fmt="battle_or_conflict"
    elif any(k in title for k in ["nace","nació","invent","descubr","cient"]): fmt="invention_science_culture"
    elif "¿por qué" in title or "por que" in title: fmt="mystery"
    elif "3 " in title or "tres " in title: fmt="three_facts"
    elif any(k in title for k in ["madrid","barcelona","sevilla","valencia","puerta","castillo","palacio"]): fmt="place_with_history"
    else: fmt="chronological_event"
    if not explicit_format and fmt in used_formats:
        fmt=next((x for x in formats if x not in used_formats),fmt)
    d["format"]=fmt
    d["hook_pattern"]=d.get("hook_pattern","surprising_fact")
    content_path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"FORMAT={fmt}")

if __name__=="__main__": main()
