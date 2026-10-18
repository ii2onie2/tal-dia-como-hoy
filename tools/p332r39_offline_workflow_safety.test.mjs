// P3.32R39: assert the manual staging workflow remains offline and secret-free.
// This is a repository static safety check, not a live staging deployment test.
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
const yml=readFileSync(".github/workflows/p332r38-signed-staging.yml","utf8");
assert.match(yml,/workflow_dispatch:/);
assert.match(yml,/contents:\s*read/);
assert.match(yml,/node tools\/p332r38_signed_staging\.test\.mjs/);
assert.doesNotMatch(yml,/node\s+tools\/p332r38_signed_staging\.mjs\s*$/m);
assert.doesNotMatch(yml,/\$\{\{\s*secrets\./);
assert.doesNotMatch(yml,/R34_HMAC_SECRET/);
assert.doesNotMatch(yml,/contents:\s*write/);
assert.match(yml,/STAGING_TRANSPORT=NOT_AUTHORIZED/);
const source=readFileSync("tools/p332r38_signed_staging.mjs","utf8");
assert.match(source,/Staging endpoint allowlist mismatch/);
assert.match(source,/redirect:"error"/);
console.log("R39_OFFLINE_WORKFLOW_SAFETY=PASS SECRET_ACCESS=NO STAGING_SEND=NO");
