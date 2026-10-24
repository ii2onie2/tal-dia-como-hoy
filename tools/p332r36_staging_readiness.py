#!/usr/bin/env python3
"""R36 staging readiness: inspect isolated handler and workflow; no external calls."""
from pathlib import Path
s=Path("tools/p332r34_worker_dry_run.mjs").read_text()
assert '"/internal/v1/transport-dry-run"' in s
assert 'R34_HMAC_SECRET' in s
assert 'value.account!==ACCOUNT' in s and 'value.dry_run!==true' in s
assert 'value.approved!==true' in s and 'value.publishable!==true' in s
assert 'Math.abs(now-Number(ts))>300000' in s
for forbidden in ('open.tiktokapis.com','TIKTOK_KV','video/init','upload_url','fetch('):
    assert forbidden not in s, f"Unexpected external capability: {forbidden}"
workflow=Path(".github/workflows/p332r36-staging-readiness.yml").read_text()
for forbidden in ('wrangler deploy','CLOUDFLARE_API_TOKEN','curl ','secrets.','api.workers.dev'):
    assert forbidden not in workflow, forbidden
print("R36_STAGING_READINESS=PASS; REMOTE_CALLS=0; PROD_DEPLOY=NO; PUBLISH=NO")
