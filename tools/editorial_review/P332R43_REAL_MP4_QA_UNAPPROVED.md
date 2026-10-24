# P3.32R43 — Actual MP4 artifact preflight (2026-10-18)

STATUS=TECHNICAL_PREFLIGHT_PASS / EDITORIAL_APPROVAL=NO / PUBLISHABLE=NO

CI: R42 offline unit tests SUCCESS, run https://github.com/ii2onie2/tal-dia-como-hoy/actions/runs/39149122477 . Note: the unit tests mock ffprobe and do NOT independently validate media files.

The GitHub R25 and R27 artifact ZIPs downloaded in prior step were extracted and their actual MP4 video/audio streams, durations and source JSON were inspected with local ffprobe.

| Artifact | Path | Duration seconds | Video | Audio | Sources |
| --- | --- | ---: | --- | --- | ---: |
| R25 12144726069 | video.mp4 | 70.588980 | H.264 1080x1920 | AAC | 2 |
| R27 12144646207 | principal/video.mp4 | 39.633333 | H.264 1080x1920 | AAC | 0 |
| R27 12144646207 | detalle/video.mp4 | 38.510023 | H.264 1080x1920 | AAC | 0 |
| R27 12144646207 | sabias/video.mp4 | 38.940000 | H.264 1080x1920 | AAC | 0 |

All four have nonempty subtitle/caption/source sidecars. R25 sources name BOE and Congreso. **The existence and number of sources do not prove each claim.** R27 fixtures are explicitly synthetic and must never be relabelled as factual/approved.

QA limitation: audio presence is proven, intelligibility is not; representative frames were sampled in R41 but full-length visual playback and rights review remain incomplete. The validator checks stream structure but not full content consistency, provenance authenticity, evidence sufficiency or rights.

NEXT: extend the offline validator with strict URL/domain and claim-level provenance semantics without promotion to approval. Keep any subsequent CI and production workflow integration separate.

No deployment, secrets, production data changes, TikTok posts or REA changes.
