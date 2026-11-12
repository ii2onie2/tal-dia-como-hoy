# Tal Día Como Hoy — recovery plan (2026-10-27)

Status: APPROVED SCOPE, IMPLEMENTATION NOT YET APPROVED FOR MAIN. No TikTok publishing through GitHub or Metricool.

## Existing components (main)
- render.yml: manual render, Piper voice, FFmpeg, source/credit files, MP4 and caption outputs; scheduled trigger removed in PR #8.
- daily-content-readiness.yml: scheduled read-only verification of three dated JSON inputs.
- tiktok-studio-pack.yml: manual ZIP export requiring three rendered MP4s, captions and sources.
- validate_content.py: structural checks only, not historical verification or media licensing proof.
- Research/editorial PRs #2, #4, #5: not approved for production.

## A — safety gate (first)
- Make an isolated PR and tests for an explicit, reviewable editorial approval manifest covering each date/series, independent factual sources, licensed media and provenance.
- Refuse unapproved or missing daily JSON; no fallback to older dates; prevent duplicate output for a date/series.
- Preserve manual render. No TikTok posting, no automatic production changes until gate passes review.

## B — editorial preparation
- Audit and reuse isolated research work from PRs #2/#4/#5; do not merge wholesale.
- Generate three candidate daily JSONs (main, detalle, sabias), verify historical claims and image rights; queue unresolved claims for review.
- Produce only approved inputs for rendering; no fabricated source or approval status.

## C — automated video + manual TikTok Studio
- After A and B pass, automate the approved daily rendering to 1080x1920 H.264/AAC MP4, captions, source and media-credit files.
- Validate duration, audio/video, output uniqueness and provenance.
- Extend the existing TikTok Studio pack to bundle all three videos and texts; never publish or schedule to TikTok automatically.
- Human downloads ZIP, reviews video and manually publishes in TikTok Studio.

## Release gates
A: isolated tests PASS + editorial approval rules reviewed.
B: three valid date-specific JSONs with evidence and media-rights review.
C: three rendered MP4s and downloadable pack QA PASS; TikTok publication remains manual.

No deployment, no merge to main, no TikTok publication authorized by this planning document.
