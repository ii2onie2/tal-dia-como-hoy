# P3.32R24–R26: operational rehearsal gates (2026-10-18)

All work on draft PR #2, NOT production. No TikTok uploads or secret inspection.

## P3.32R23: baseline
- Main render workflow requires three dated JSON files; it renders MP4 but may write back to main. It must not be invoked for this isolated rehearsal.
- TryPost publication workflow on main is explicitly disabled.

## P3.32R24: isolated video gate
- Separate PR-only workflow uses existing `scripts/render.py` and synthetic text explicitly marked NOT FOR PUBLICATION, no historical claims, no external media.
- Only an uploaded MP4 with verified 1080x1920 resolution and sidecar artifacts proves this gate. Creation of the workflow or other CI success does not.
- No `contents: write`, no secrets, no media fetch, no TikTok.

## P3.32R25: editorial content gate
- Historical dossier inputs (17 October 1991/1977/1952) remain UNAPPROVED. Zero of three have full independent claim-source crosschecks, sign-off, and media reuse clearance.
- A synthetic test video is not a public-facing historically validated video.
- Releasing actual historical content is BLOCKED until each claim is supported, validated by editorial review, and its media rights are cleared.

## P3.32R26: TikTok readiness gate
- `.github/workflows/publish-trypost.yml` on main only prints a disable message; not a publisher.
- TikTok Developers review/approval and account connectivity CANNOT be inferred from the repository or past pipeline CI.
- No test posting, authentication inspection, token access, or switch-on is attempted.
- To declare READY, collect read-only authenticated publisher authorization evidence, permitted scopes, account status, dry-run validation, then separately authorize posting.

## Measurable dashboard
- INPUT_READY: BLOCKED (no three independently approved day-matched content inputs)
- CONTENT_VALIDATED: BLOCKED
- SYNTHETIC_MP4_RENDER: requires new run and artifact verification
- APPROVED_HISTORICAL_MP4: BLOCKED
- PUBLICATION_CHANNEL_READY: NOT VERIFIED / TryPost explicitly disabled
- TIKTOK_POSTED: NO CONFIRMATION

No single percentage is inferred.
