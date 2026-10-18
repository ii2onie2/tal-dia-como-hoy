# P3.32R23 — Operational baseline audit (2026-10-18)
STATUS: READ-ONLY AUDIT; PRODUCTION_UNCHANGED; TIKTOK_PUBLICATION=NO.

## Observed default-branch components
- `.github/workflows/render.yml` contains scheduled run `45 6 * * *`, push and manual triggers. Scheduled case requires three pre-existing files: `content/YYYY-MM-DD.json`, `content/YYYY-MM-DD-detalle.json`, `content/YYYY-MM-DD-sabias.json`. The workflow does not create these files.
- `scripts/render.py` invokes Piper and ffmpeg to create video.mp4, caption.txt and sources.json.
- Render workflow uploads outputs and may commit MP4s into `videos/` on default-branch runs. This is **not** evidence that videos are already posted to TikTok.
- `.github/workflows/publish-trypost.yml` is manual-only and intentionally disabled, with one echo step.
- No proven link from the newly added P3.32R9-R22 evidence checks to `render.yml` on main. Prior isolated GitHub CI success is not end-to-end rendering success.
- Existing videos in repository may reflect earlier runs only; freshness and actual MP4 playback remain to be verified.

## Release criteria — measurable, no unsupported percentage
1. INPUT_READY: three correctly dated, fact-checked, publication-approved content JSON files. Current state NOT PROVEN.
2. VALIDATION_PASS: quality checks and rights checks on exactly those inputs. Current state NOT PROVEN.
3. RENDER_PASS: actual artifact video.mp4 + ffprobe validation and readable captions/source at target run. Current state NOT PROVEN for new controlled content.
4. DISTRIBUTION_READY: proven authenticated, platform-authorized posting route. Current state BLOCKED (TryPost workflow disabled; TikTok API approval not established).
5. TIKTOK_PUBLISHED: platform confirmation and independently visible upload. Current state NOT PROVEN.

## Blocker order
A. Securely assemble and independently review valid inputs with legal media provenance.
B. Isolated render rehearsal that cannot commit to main, access posting secrets or publish. Confirm output artifact.
C. Verify approved TikTok integration separately, without posting test until authorized.
D. Reviewed integration decision and monitoring.

## Non-goals
No approval of any P3.32R20 research dossier. No main-branch edits, no production data modifications, no secret access, no TikTok posting, no REA or Tu Perro Feliz changes.
