#!/usr/bin/env python3
"""Nonpublishing MP4 and source-sidecar structural QA (not fact or media approval)."""
import argparse
import json
import subprocess
from pathlib import Path

def inspect(directory, *, factual=False):
    p=Path(directory)
    video=p/"video.mp4"
    if not video.is_file() or video.stat().st_size==0:
        raise ValueError("MISSING_MP4")
    result=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_type,codec_name,width,height","-of","json",str(video)],capture_output=True,text=True,timeout=30,check=True)
    meta=json.loads(result.stdout)
    streams=meta.get("streams",[])
    if not any(s.get("codec_type")=="video" and s.get("codec_name")=="h264" and s.get("width")==1080 and s.get("height")==1920 for s in streams):
        raise ValueError("INVALID_VIDEO_STREAM")
    if not any(s.get("codec_type")=="audio" and s.get("codec_name")=="aac" for s in streams):
        raise ValueError("INVALID_AUDIO_STREAM")
    duration=float(meta.get("format",{}).get("duration",0))
    if not 5<=duration<=180:
        raise ValueError("INVALID_DURATION")
    for name in ("subtitles.srt","caption.txt","sources.json"):
        if not (p/name).is_file() or not (p/name).stat().st_size:
            raise ValueError("MISSING_"+name)
    sources=json.loads((p/"sources.json").read_text(encoding="utf-8"))
    if not isinstance(sources,list):
        raise ValueError("INVALID_SOURCE_MANIFEST")
    if factual:
        if len(sources)<2:
            raise ValueError("INSUFFICIENT_FACTUAL_SOURCES")
        for source in sources:
            if not isinstance(source,(str,dict)):
                raise ValueError("MALFORMED_SOURCE_ENTRY")
        # Do not infer factual truth, licensing, permission or editorial approval.
    return {"result":"TECHNICAL_STRUCTURE_PASS_APPROVAL_NO","seconds":round(duration,3),"source_count":len(sources)}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--directory",required=True)
    parser.add_argument("--factual",action="store_true")
    args=parser.parse_args()
    try:
        print(json.dumps(inspect(args.directory,factual=args.factual),sort_keys=True))
    except (ValueError,OSError,subprocess.SubprocessError,json.JSONDecodeError) as exc:
        print("QA_BLOCKED:"+str(exc))
        raise SystemExit(2)

if __name__=="__main__":
    main()
