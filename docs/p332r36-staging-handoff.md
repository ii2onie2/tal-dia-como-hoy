# P3.32R36 – Isolated Cloudflare staging handoff (NOT DEPLOYED)
Target: **new Worker**, never overwrite `tiktok-auto-publisher`.
Source: `tools/p332r34_worker_dry_run.mjs`.
Route: `POST /internal/v1/transport-dry-run`.
Required encrypted Worker secret: `R34_HMAC_SECRET`, unique random >=32 chars, **not** the existing `PUBLISH_ADMIN_PASSWORD`.
GitHub would need the same secret supplied as a repository secret after an explicit staging setup; do not place it in workflow source or logs.
Requests: `Content-Type: application/json`, `X-R34-Timestamp` (13-digit Unix milliseconds), `X-R34-Signature: sha256=<HMAC_SHA256(timestamp + "." + raw_body)>`.
Strict accepted envelope: `account,approved,content_sha256,date,dry_run,publishable,slot`; only `taldiacomohoy09`; both editorial flags true; `dry_run` true.
Responses must only indicate simulation; source has no real TikTok endpoint or MP4 upload.
**Limitations**: this is not deployed, sender integration to real staging URL not configured, and replay within a 5-minute window is possible without persistent nonce storage. No real transfer of MP4 is implemented.
**Before any real staging call**: verify staging Worker name/URL distinct from production; isolate credentials and bindings; stage-only deployment approval; run negative tests. Do not reuse the production OAuth client or TikTok KV.
