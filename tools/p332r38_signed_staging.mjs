// R38 staging-only signed transport client. Must never target production.
import {createHmac} from "node:crypto";
const URL_ALLOWED="https://taldiacomohoy-staging.ii2onie.workers.dev/internal/v1/transport-dry-run";
export async function sendStaging({secret, url=URL_ALLOWED, request=globalThis.fetch, now=Date.now()}={}) {
 if(url!==URL_ALLOWED) throw new Error("Staging endpoint allowlist mismatch");
 if(typeof secret!=="string" || secret.length<32) throw new Error("Missing/short staging secret");
 const body=JSON.stringify({account:"taldiacomohoy09",approved:true,content_sha256:"a".repeat(64),
    date:"2026-10-18",dry_run:true,publishable:true,slot:"principal"});
 const timestamp=String(now);
 const signature=createHmac("sha256",secret).update(timestamp+"."+body).digest("hex");
 const response=await request(url,{method:"POST",redirect:"error",headers:{"Content-Type":"application/json",
    "X-R34-Timestamp":timestamp,"X-R34-Signature":"sha256="+signature},body});
 const raw=await response.text();
 let parsed;
 try {parsed=JSON.parse(raw);} catch {throw new Error("Invalid JSON response HTTP "+response.status);}
 if(response.status!==200 || parsed.status!=="SIMULATED_ONLY" || parsed.account!=="taldiacomohoy09" ||
   parsed.publish!==false || parsed.uploaded!==false || parsed.forwarded!==false)
   throw new Error("Staging response denied HTTP "+response.status+" error="+String(parsed.error||"unexpected"));
 return {http:response.status,status:parsed.status,account:parsed.account,posted:parsed.publish};
}
if(process.argv[1] && import.meta.url===new URL("file://"+process.argv[1]).href){
 sendStaging({secret:process.env.R34_HMAC_SECRET})
 .then(v=>{console.log("R38_SIGNED_STAGING=PASS HTTP="+v.http+" STATUS="+v.status+" PUBLISH=NO");})
 .catch(e=>{console.error("R38_SIGNED_STAGING=FAIL "+e.message);process.exitCode=1;});
}
