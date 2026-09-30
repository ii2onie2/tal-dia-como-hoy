#!/usr/bin/env python3
import json, pathlib, sys

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
    if d["series"] not in {"Tal Día Como Hoy","¿Sabías esto de España?"}:
        fail(f"{name}: unknown series")
    if len(d["narration"].split()) < 70:
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
