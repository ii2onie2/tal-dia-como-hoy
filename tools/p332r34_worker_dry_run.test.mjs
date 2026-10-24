import assert from "node:assert/strict";
import {handleDryRun,sign} from "./p332r34_worker_dry_run.mjs";
const now = Date.parse("2026-10-18T12:00:00Z");
const secret="R34-SYNTHETIC-TEST-KEY-NEVER-DEPLOY-OR-REUSE";
const payload={account:"taldiacomohoy09",approved:true,content_sha256:"a".repeat(64),date:"2026-10-18",dry_run:true,publishable:true,slot:"principal"};
const base="https://isolated.test/internal/v1/transport-dry-run";
async function run(obj=payload, opts={}) {
 const body=opts.body??JSON.stringify(obj); const ts=String(opts.ts??now);
 const signature=opts.signature??"sha256="+await sign(secret,ts+"."+body);
 const req=new Request(opts.url??base,{method:"POST",headers:{"Content-Type":opts.type??"application/json","X-R34-Timestamp":ts,"X-R34-Signature":signature},body});
 const resp=await handleDryRun(req,{R34_HMAC_SECRET:opts.secret??secret},now);
 return {status:resp.status,data:await resp.json()};
}
let tests=0;
function check(got,expected){assert.equal(got.status,expected);tests++;}
check(await run(),200);
for (const change of [
 {account:"tuperrofelizofficial"},{account:"taldiacomohoy"},{approved:false},
 {publishable:false},{dry_run:false},{slot:"bad"},{content_sha256:"x"},
 {extra:true}
]) check(await run({...payload,...change}),change.extra?400:403);
check(await run(payload,{signature:"sha256"+"0".repeat(64)}),401);
check(await run(payload,{ts:now-400000}),401);
check(await run(payload,{secret:"short"}),503);
check(await run(payload,{type:"text/plain"}),415);
check(await run(payload,{body:"not-json"}),400);
check(await run(payload,{url:"https://isolated.test/publish"}),404);
assert.equal((await handleDryRun(new Request(base),{R34_HMAC_SECRET:secret},now)).status,405);tests++;
console.log("P3.32R34=PASS TESTS="+tests+"; DRY_RUN_ONLY=YES; TIKTOK_CALLS=0; CLOUDFLARE_DEPLOY=NO");
