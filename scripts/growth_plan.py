#!/usr/bin/env python3
import json, pathlib, re, sys

HISTORY=pathlib.Path("content/published_history.json")
OUT=pathlib.Path("content/growth_queue.json")

HOOKS=[
"surprising_fact","unanswered_question","consequence_first",
"this_happened_here","before_after","three_facts","overlooked_detail"
]
TOPICS=[
"reyes_y_coronas","batallas_y_conflictos","personajes","lugares",
"ciencia_y_inventos","cultura_y_gastronomia","palabras_y_costumbres",
"historias_olvidadas","arquitectura_y_patrimonio","vida_cotidiana"
]

def main():
    history=json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else []
    recent=history[-14:]
    used_formats={x.get("format") for x in recent}
    used_hooks={x.get("hook_pattern") for x in recent}
    used_people={x.get("principal_person") for x in recent if x.get("principal_person")}
    queue=[]
    for topic in TOPICS:
        if topic not in {x.get("topic_family") for x in recent}:
            queue.append({
                "topic_family":topic,
                "format":next((x for x in ["chronological_event","historical_person","battle_or_conflict","place_with_history","before_after","three_facts","invention_science_culture","forgotten_story","historical_object_word_custom"] if x not in used_formats),"chronological_event"),
                "hook_pattern":next((x for x in HOOKS if x not in used_hooks),"surprising_fact"),
                "avoid_principal_people":sorted(used_people)
            })
    OUT.write_text(json.dumps(queue[:10],ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"GROWTH_QUEUE={len(queue[:10])}")

if __name__=="__main__": main()
