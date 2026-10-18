// P3.32R34 isolated Cloudflare Worker endpoint: NEVER deploy to production.
// No TikTok calls. No uploads. No account KV reads. No publishing branch.
const ACCOUNT = "taldiacomohoy09";
const SLOTS = new Set(["principal", "detalle", "sabias"]);
const path = "/internal/v1/transport-dry-run";
const json = (obj, status = 200) => new Response(JSON.stringify(obj), {
  status, headers: {"Content-Type": "application/json", "Cache-Control": "no-store"}
});
const bytes = text => new TextEncoder().encode(text);
const hex = arr => [...new Uint8Array(arr)].map(n => n.toString(16).padStart(2,"0")).join("");
async function sign(secret, message) {
  const key = await crypto.subtle.importKey("raw", bytes(secret), {name:"HMAC", hash:"SHA-256"}, false, ["sign"]);
  return hex(await crypto.subtle.sign("HMAC", key, bytes(message)));
}
function equalHex(a,b) {
  if (!/^[a-f0-9]{64}$/.test(a) || !/^[a-f0-9]{64}$/.test(b)) return false;
  let diff=0;
  for(let i=0;i<64;i++) diff |= a.charCodeAt(i)^b.charCodeAt(i);
  return diff===0;
}
export async function handleDryRun(request, env, now = Date.now()) {
  const url = new URL(request.url);
  if(url.pathname!==path) return json({error:"not_found"},404);
  if(request.method!=="POST") return json({error:"method_not_allowed"},405);
  if(typeof env?.R34_HMAC_SECRET!=="string" || env.R34_HMAC_SECRET.length<32) return json({error:"unavailable"},503);
  if(!request.headers.get("Content-Type")?.toLowerCase().startsWith("application/json")) return json({error:"bad_type"},415);
  const ts = request.headers.get("X-R34-Timestamp") || "";
  if(!/^\d{13}$/.test(ts) || Math.abs(now-Number(ts))>300000) return json({error:"stale"},401);
  const claimed = request.headers.get("X-R34-Signature") || "";
  if(!/^sha256=[a-f0-9]{64}$/.test(claimed)) return json({error:"unauthorized"},401);
  // Limit untrusted bytes BEFORE parsing, no file or binary accepted.
  const body = await request.text();
  if(bytes(body).length>2048) return json({error:"too_large"},413);
  const expected = await sign(env.R34_HMAC_SECRET, ts+"."+body);
  if(!equalHex(claimed.slice(7),expected)) return json({error:"unauthorized"},401);
  let value;
  try {value=JSON.parse(body);} catch {return json({error:"bad_json"},400);}
  if(!value || Array.isArray(value) || typeof value!=="object") return json({error:"bad_payload"},400);
  const keys=Object.keys(value).sort().join(",");
  if(keys!=="account,approved,content_sha256,date,dry_run,publishable,slot") return json({error:"bad_fields"},400);
  if(value.account!==ACCOUNT || !SLOTS.has(value.slot) || value.dry_run!==true ||
     value.approved!==true || value.publishable!==true ||
     typeof value.date!=="string" || !/^20\d{2}-\d{2}-\d{2}$/.test(value.date) ||
     typeof value.content_sha256!=="string" || !/^[a-f0-9]{64}$/.test(value.content_sha256))
    return json({error:"denied"},403);
  return json({status:"SIMULATED_ONLY", account:ACCOUNT, slot:value.slot,
    publish:false, uploaded:false, forwarded:false});
}
export default {fetch: handleDryRun};
export {sign};
