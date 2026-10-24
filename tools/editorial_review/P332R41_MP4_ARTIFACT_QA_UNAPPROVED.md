# P3.32R41 — MP4 audiovisual artifact check (2026-10-18)

STATUS: TECHNICAL_OUTPUTS_VERIFIED / EDITORIAL_APPROVED=NO / PUBLICATION=NO

Inspected GitHub Actions artifacts from runs R25=39148658116 (artifact 12144726069), R27=39148658148 (artifact 12144646207). ZIP manifests inspected, MP4s probed locally, and representative frames viewed. This is a sampled visual review, **not** full playback, listening evaluation or editorial sign-off.

| MP4 | duration | video | audio | source manifest |
| --- | ---: | --- | --- | --- |
| R25 historical draft | 70.589 s | H.264 1080x1920 | AAC | BOE and Congreso |
| R27 principal | 39.633 s | H.264 1080x1920 | AAC | [] |
| R27 detalle | 38.510 s | H.264 1080x1920 | AAC | [] |
| R27 sabias | 38.940 s | H.264 1080x1920 | AAC | [] |

Representative sampled frames show 'BORRADOR / NO PUBLICAR' on all four videos. R25 shows a timeline of Ley 46/1977 (15 October signing / 17 October publication). All three R27 samples have black backgrounds, visibly showing only draft overlay and subtitle. These are synthetic fixtures, not final creative output. A sampled frame does not demonstrate the full video is visually correct or that audio has been listened to.

RELEASE BLOCKERS:
- R25 two URLs are not per-claim verified, media use and editorial approval remain unset.
- R27 source manifests are empty; this is acceptable only because these are synthetic, never publishable fixtures.
- Human/full-duration playback and speech intelligibility review not completed; do not assert media-QA PASS.
- Nothing was posted, no production or secrets modified. No reuse by Tu Perro Feliz until domain-specific review.

NEXT: automate **nonpublishing** checks on actual artifact outputs (durations, streams, safe labels, required provenance when using factual content); subsequently review real editorial claims and production assets without any auto-approval.
