# P3.8 - Tal Dia review-only GitHub Actions pilot

Target branch ONLY: integration/indiepost-premium-audit-20261015.

Upload files from this archive preserving `.github/workflows/` and `pilot/` paths to the integration branch only. Do not merge to main. Then manually run workflow `P3.8 Piper review-only (manual)` from Actions, selecting the integration branch. The workflow does not publish or write repository content, but uploading these files creates a staging commit.

This is a prepared package, not an executed workflow. It installs Piper, downloads the voice, runs the 65-80s gate, and uploads any outputs as an artifact. If duration is outside range, workflow fails closed; the WAV may still be uploaded. Subtitles are estimated SRT and are NOT burned into MP4. Visual, factual, licensing and timing review required.
