#!/usr/bin/env python3
import argparse, json, os, pathlib, subprocess, textwrap, wave

W,H=1080,1920

def run(cmd):
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)

def probe_duration(path):
    p=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",path],capture_output=True,text=True,check=True)
    return float(p.stdout.strip())

def srt_time(t):
    ms=int(round(t*1000)); h=ms//3600000; ms%=3600000; m=ms//60000; ms%=60000; s=ms//1000; ms%=1000
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def make_srt(text,duration,out):
    chunks=textwrap.wrap(text,width=42,break_long_words=False,break_on_hyphens=False) or [text]
    step=max(duration/len(chunks),1.0)
    with open(out,"w",encoding="utf-8") as f:
        for i,c in enumerate(chunks,1):
            start=(i-1)*step; end=min(i*step,duration)
            f.write(f"{i}\n{srt_time(start)} --> {srt_time(end)}\n{c}\n\n")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--content",required=True)
    ap.add_argument("--voice-model",default=os.environ.get("PIPER_VOICE_MODEL",""))
    ap.add_argument("--voice-config",default=os.environ.get("PIPER_VOICE_CONFIG",""))
    ap.add_argument("--out",default="out")
    args=ap.parse_args()
    out=pathlib.Path(args.out); out.mkdir(parents=True,exist_ok=True)
    data=json.loads(pathlib.Path(args.content).read_text(encoding="utf-8"))
    narration=(data.get("narration") or "").strip()
    if not narration: raise SystemExit("narration vide")

    wav=str(out/"voice.wav")
    if not args.voice_model:
        raise SystemExit("PIPER_VOICE_MODEL absent")
    cmd=["piper","--model",args.voice_model,"--output_file",wav]
    if args.voice_config:
        cmd += ["--config",args.voice_config]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,text=True)
    p.communicate(narration)
    if p.returncode: raise SystemExit(p.returncode)

    duration=probe_duration(wav)
    srt=str(out/"subtitles.srt"); make_srt(narration,duration,srt)

    media=data.get("media") or []
    bg=None
    for item in media:
        pth=item.get("path") if isinstance(item,dict) else None
        if pth and pathlib.Path(pth).exists():
            bg=pth; break

    video=str(out/"video.mp4")
    vf=f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},subtitles={srt}:force_style='FontName=DejaVu Sans,FontSize=18,Outline=2,Shadow=0,Alignment=2,MarginV=140'"
    if bg:
        run(["ffmpeg","-y","-loop","1","-i",bg,"-i",wav,"-t",f"{duration:.3f}","-vf",vf,"-c:v","libx264","-preset","medium","-crf","21","-c:a","aac","-b:a","192k","-pix_fmt","yuv420p","-movflags","+faststart",video])
    else:
        run(["ffmpeg","-y","-f","lavfi","-i",f"color=c=0x111111:s={W}x{H}:r=30","-i",wav,"-t",f"{duration:.3f}","-vf",f"subtitles={srt}:force_style='FontName=DejaVu Sans,FontSize=18,Outline=2,Shadow=0,Alignment=2,MarginV=140'","-c:v","libx264","-preset","medium","-crf","21","-c:a","aac","-b:a","192k","-pix_fmt","yuv420p","-movflags","+faststart",video])

    pathlib.Path(out/"caption.txt").write_text((data.get("caption","") + "\n\n" + " ".join(data.get("hashtags",[]))).strip()+"\n",encoding="utf-8")
    pathlib.Path(out/"sources.json").write_text(json.dumps(data.get("sources",[]),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(video)

if __name__=="__main__": main()
