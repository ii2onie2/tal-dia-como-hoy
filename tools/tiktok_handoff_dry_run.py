"""Deterministic, strictly offline TikTok transfer rehearsal.

This is a contract simulation, not OAuth or a TikTok API call.
"""
import hashlib
import json
from pathlib import Path

def simulate(video, manifest, published_ids=(), scenario="ok", max_attempts=3):
    video=Path(video)
    manifest=Path(manifest)
    if not video.is_file() or video.stat().st_size==0:
        return {"status":"BLOCKED","reason":"VIDEO_MISSING","sent":False}
    if not manifest.is_file():
        return {"status":"BLOCKED","reason":"APPROVAL_MANIFEST_MISSING","sent":False}
    try:
        meta=json.loads(manifest.read_text(encoding="utf-8"))
    except (ValueError,OSError):
        return {"status":"BLOCKED","reason":"INVALID_MANIFEST","sent":False}
    if not isinstance(meta,dict):
        return {"status":"BLOCKED","reason":"INVALID_MANIFEST","sent":False}
    digest=hashlib.sha256(video.read_bytes()).hexdigest()
    if digest in published_ids:
        return {"status":"BLOCKED","reason":"DUPLICATE_VIDEO","sent":False}
    if "video_sha256" in meta and meta["video_sha256"]!=digest:
        return {"status":"BLOCKED","reason":"VIDEO_HASH_MISMATCH","sent":False}
    if not isinstance(max_attempts,int) or isinstance(max_attempts,bool) or not 1<=max_attempts<=5:
        return {"status":"BLOCKED","reason":"INVALID_RETRY_LIMIT","sent":False}
    # Never trust a self-declared approval in content or manifest.
    if scenario not in ("ok","oauth_expired","rate_limited","server_error","timeout","permanent_rejection"):
        return {"status":"BLOCKED","reason":"UNKNOWN_SCENARIO","sent":False}
    retryable={"rate_limited","server_error","timeout"}
    attempts=min(max_attempts,3) if scenario in retryable else 1
    outcome={
        "ok":"OFFLINE_FLOW_COMPLETED",
        "oauth_expired":"OAUTH_REAUTH_REQUIRED",
        "rate_limited":"RATE_LIMIT_RETRY_EXHAUSTED",
        "server_error":"SERVER_RETRY_EXHAUSTED",
        "timeout":"TIMEOUT_RETRY_EXHAUSTED",
        "permanent_rejection":"NON_RETRYABLE_REJECTION"
    }[scenario]
    return {"status":"SIMULATED_ONLY","reason":"NO_TRUSTED_APPROVAL_OR_TIKTOK_ACCESS",
            "scenario":scenario,"simulated_outcome":outcome,"attempts":attempts,
            "retryable":scenario in retryable,"video_sha256":digest,
            "sent":False,"published":False}
