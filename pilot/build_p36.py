
#!/usr/bin/env python3
"""Offline staging render with burned-in Spanish subtitles.

No publication, database writes, or GitHub operations.
Subtitles are estimated from sentence lengths, not force-aligned.
"""

import argparse
import json
import re
import subprocess
from pathlib import Path


def run(cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, check=True)


def duration(path):
    return float(
        subprocess.check_output(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            text=True,
        ).strip()
    )


def stamp(t):
    ms = round(t * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-model", required=True)
    ap.add_argument("--voice-config", required=True)
    args = ap.parse_args()

    root = Path(__file__).resolve().parent
    out = root / "p36_output"
    out.mkdir(parents=True, exist_ok=True)

    narration = (
        (root / "narration_es_v2_draft.txt")
        .read_text(encoding="utf-8")
        .strip()
    )

    # 1. Generate Spanish narration with Piper.
    audio = out / "narration.wav"

    subprocess.run(
        [
            "piper",
            "--model", args.voice_model,
            "--config", args.voice_config,
            "--output_file", str(audio),
        ],
        input=narration,
        text=True,
        check=True,
    )

    audio_duration = duration(audio)

    if not 65 <= audio_duration <= 80:
        raise SystemExit(
            "DURATION_GATE=BLOCKED "
            f"audio={audio_duration:.2f}s; "
            "revise script/voice before rendering"
        )

    print(f"DURATION_GATE=PASS audio={audio_duration:.2f}s")

    # 2. Generate estimated Spanish SRT subtitles.
    paragraphs = [
        p.strip()
        for p in narration.split("\n\n")
        if p.strip()
    ]

    chunks = []

    for paragraph in paragraphs:
        sentences = re.split(
            r"(?<=[.!?])\s+",
            paragraph,
        )
        chunks.extend(
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        )

    weights = [
        max(1, len(sentence.split()))
        for sentence in chunks
    ]

    total_weight = sum(weights)

    if not chunks or total_weight == 0:
        raise SystemExit("SUBTITLE_GATE=BLOCKED empty narration")

    subtitles = out / "subtitles.srt"
    t = 0.0

    with subtitles.open("w", encoding="utf-8") as f:
        for i, (sentence, weight) in enumerate(
            zip(chunks, weights), 1
        ):
            end = (
                audio_duration
                if i == len(chunks)
                else t + audio_duration * weight / total_weight
            )

            f.write(
                f"{i}\n"
                f"{stamp(t)} --> {stamp(end)}\n"
                f"{sentence}\n\n"
            )

            t = end

    print(f"SUBTITLE_SRT=PASS entries={len(chunks)}")

    # 3. Create three vertical image clips.
    clips = []
    segment_duration = audio_duration / 3

    for i in range(1, 4):
        src = root / f"{i:02}.jpg"
        clip = out / f"clip{i}.mp4"

        if not src.is_file():
            raise SystemExit(
                f"IMAGE_GATE=BLOCKED missing={src.name}"
            )

        run([
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel", "error",
            "-loop", "1",
            "-framerate", "25",
            "-i", str(src),
            "-t", f"{segment_duration:.3f}",
            "-vf",
            (
                "scale=1080:1920:"
                "force_original_aspect_ratio=increase,"
                "crop=1080:1920,"
                "format=yuv420p"
            ),
            "-an",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "24",
            str(clip),
        ])

        clips.append(clip)

    # 4. Join image clips.
    concat = out / "concat.txt"

    concat.write_text(
        "".join(
            f"file '{clip.name}'\n"
            for clip in clips
        ),
        encoding="utf-8",
    )

    joined = out / "joined.mp4"

    run([
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel", "error",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat),
        "-c", "copy",
        str(joined),
    ])

    # 5. Burn Spanish subtitles and AI disclosure into MP4.
    result = out / "tal_dia_p36_review_only.mp4"

    subtitle_filter = (
        "subtitles=subtitles.srt:"
        "force_style='"
        "FontName=DejaVu Sans,"
        "FontSize=17,"
        "PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,"
        "BorderStyle=1,"
        "Outline=2,"
        "Shadow=1,"
        "Alignment=2,"
        "MarginV=145"
        "'"
    )

    disclosure_filter = (
        "drawtext="
        "text='Recreacion visual generada con IA':"
        "fontcolor=white:"
        "fontsize=28:"
        "box=1:"
        "boxcolor=black@0.65:"
        "x=(w-text_w)/2:"
        "y=h-90"
    )

    video_filter = (
        subtitle_filter + "," + disclosure_filter
    )

    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel", "error",
            "-i", str(joined),
            "-i", str(audio),
            "-vf", video_filter,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "24",
            "-c:a", "aac",
            "-b:a", "160k",
            "-shortest",
            "-movflags", "+faststart",
            str(result),
        ],
        cwd=out,
    )

    # 6. Validate generated MP4 and report results.
    video_duration = duration(result)

    if abs(video_duration - audio_duration) > 1.0:
        raise SystemExit(
            "VIDEO_DURATION_GATE=BLOCKED "
            f"audio={audio_duration:.2f}s "
            f"video={video_duration:.2f}s"
        )

    meta = {
        "audio_duration_seconds": audio_duration,
        "video_duration_seconds": video_duration,
        "subtitle_file": "subtitles.srt",
        "subtitles_burned_in": True,
        "subtitle_timing": "ESTIMATED_NOT_FORCED_ALIGNED",
        "ai_disclosure_burned_in": True,
        "publication_approved": False,
        "source_rights_verified": False,
        "editorial_approved": False,
    }

    (out / "P36_REPORT.json").write_text(
        json.dumps(
            meta,
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    print(
        "P36_RENDER=PASS_REVIEW_ONLY",
        result,
    )
    print("SUBTITLES_BURNED_IN=YES")
    print("PUBLICATION_ENABLED=NO")


if __name__ == "__main__":
    main()
