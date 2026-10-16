#!/usr/bin/env python3
"""Offline staging render. No publication, DB or GitHub operations."""
import argparse, json, re, subprocess, wave
from pathlib import Path

def run(cmd):
    subprocess.run(cmd, check=True)

def duration(path):
    return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(path)],text=True).strip())

def stamp(t):
    ms=round(t*1000); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--voice-model',required=True); ap.add_argument('--voice-config',required=True); a=ap.parse_args()
    root=Path(__file__).resolve().parent; out=root/'p36_output'; out.mkdir(exist_ok=True)
    narration=(root/'narration_es_v2_draft.txt').read_text(encoding='utf-8').strip()
    audio=out/'narration.wav'
    run(['piper','--model',a.voice_model,'--config',a.voice_config,'--output_file',str(audio)],) if False else None
    subprocess.run(['piper','--model',a.voice_model,'--config',a.voice_config,'--output_file',str(audio)],input=narration,text=True,check=True)
    d=duration(audio)
    if not 65<=d<=80: raise SystemExit(f'DURATION_GATE=BLOCKED audio={d:.2f}s; revise script/voice before rendering')
    paras=[p.strip() for p in narration.split('\n\n') if p.strip()]
    chunks=[]
    for p in paras:
        sentences=re.split(r'(?<=[.!?])\s+',p)
        chunks.extend(sentences)
    weights=[max(1,len(x.split())) for x in chunks]; total=sum(weights); t=0
    with (out/'subtitles.srt').open('w',encoding='utf-8') as f:
        for i,(s,w) in enumerate(zip(chunks,weights),1):
            end=d if i==len(chunks) else t+d*w/total
            f.write(f'{i}\n{stamp(t)} --> {stamp(end)}\n{s}\n\n'); t=end
    # Equal thirds, slow zoom with looped stills. No image edits.
    clips=[]
    for i in range(1,4):
        src=root/f'{i:02}.jpg'; clip=out/f'clip{i}.mp4'; seg=d/3
        run(['ffmpeg','-y','-hide_banner','-loglevel','error','-loop','1','-framerate','25','-i',str(src),'-t',f'{seg:.3f}', '-vf',"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p",'-an','-c:v','libx264','-preset','veryfast','-crf','24',str(clip)])
        clips.append(clip)
    concat=out/'concat.txt'; concat.write_text(''.join(f"file '{p.name}'\n" for p in clips))
    joined=out/'joined.mp4'
    run(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(joined)])
    result=out/'tal_dia_p36_review_only.mp4'
    run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(joined),'-i',str(audio),'-vf',"drawtext=text='Recreacion visual generada con IA':fontcolor=white:fontsize=28:box=1:boxcolor=black@0.65:x=(w-text_w)/2:y=h-90",'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','veryfast','-crf','24','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(result)])
    meta={'audio_duration_seconds':d,'video_duration_seconds':duration(result),'subtitle_timing':'ESTIMATED_NOT_FORCED_ALIGNED','publication_approved':False,'source_rights_verified':False,'editorial_approved':False}
    (out/'P36_REPORT.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('P36_RENDER=PASS_REVIEW_ONLY',result)
if __name__=='__main__': main()
