"""TikTok handoff simulation: never sends any network request or credentials."""
import hashlib,json
from pathlib import Path

def simulate(video,manifest,published_ids=()):
    video=Path(video);manifest=Path(manifest)
    if not video.is_file() or video.stat().st_size==0:
        return {"status":"BLOCKED","reason":"VIDEO_MISSING","sent":False}
    if not manifest.is_file():
        return {"status":"BLOCKED","reason":"APPROVAL_MANIFEST_MISSING","sent":False}
    try: meta=json.loads(manifest.read_text(encoding="utf-8"))
    except (ValueError,OSError):
        return {"status":"BLOCKED","reason":"INVALID_MANIFEST","sent":False}
    digest=hashlib.sha256(video.read_bytes()).hexdigest()
    if digest in published_ids:
        return {"status":"BLOCKED","reason":"DUPLICATE_VIDEO","sent":False}
    # Never authorize based on a manifest controlled by a content generator.
    return {"status":"SIMULATED_ONLY","reason":"TIKTOK_DEVELOPERS_IN_REVIEW_AND_TRUSTED_APPROVAL_MISSING","video_sha256":digest,"sent":False,"published":False}
