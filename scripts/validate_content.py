#!/usr/bin/env python3
import json, pathlib, sys

ACTIVATION_DATE="2026-10-04"

def fail(msg):
    print("CONTENT_CHECK=FAIL:", msg)
    raise SystemExit(1)

files=sys.argv[1:]
if not files:
    fail("no content files")
for name in files:
    p=pathlib.Path(name)
    d=json.loads(p.read_text(encoding="utf-8"))
    for key in ["series","title","date","hook","narration","caption","hashtags","sources","media"]:
        if key not in d: fail(f"{name}: missing {key}")
    if d["series"] not in {"Tal Día Como Hoy","¿Sabías esto de España?","El detalle que casi nadie ve"}:
        fail(f"{name}: unknown series")
    if d["date"] >= ACTIVATION_DATE:
        min_words=180
        target=d.get("duration_target","")
        if target not in {"65-80s","65-75s"}:
            fail(f"{name}: duration_target must be 65-80s or 65-75s from {ACTIVATION_DATE}")
    else:
        min_words=45 if d["series"]=="El detalle que casi nadie ve" else 70
    if len(d["narration"].split()) < min_words:
        fail(f"{name}: narration too short")
    if len(d["narration"]) > 3800:
        fail(f"{name}: narration too long")
    if not d["hook"].strip(): fail(f"{name}: empty hook")
    if not d["hashtags"]: fail(f"{name}: no hashtags")
    if not d["sources"]: fail(f"{name}: no sources")
    if not d["media"]: fail(f"{name}: no media declared")
    cta=d.get("cta","").strip()
    if not cta:
        fail(f"{name}: missing CTA")
    if "Síguenos" not in cta and "Sigue" not in cta:
        fail(f"{name}: CTA does not contain follow request")
    print(f"CONTENT_CHECK=PASS {name}")
