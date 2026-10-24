import assert from "node:assert/strict";
import {createServer} from "node:http";
import {once} from "node:events";
import {handleDryRun, sign} from "./p332r34_worker_dry_run.mjs";
const secret="R35-LOCAL-SYNTHETIC-KEY-NOT-FOR-PRODUCTION";
const payload={account:"taldiacomohoy09",approved:true,content_sha256:"a".repeat(64),date:"2026-10-18",dry_run:true,publishable:true,slot:"principal"};
const server=createServer(async(req,res)=>{
  const chunks=[];
  for await(const chunk of req)chunks.push(chunk);
  const body=Buffer.concat(chunks);
  const headers=new Headers();
  for (const [k,v] of Object.entries(req.headers)) if(typeof v==="string")headers.set(k,v);
  const incoming=new Request("https://isolated.test"+req.url,{method:req.method,headers,body:req.method==="POST"?body:undefined});
  const answer=await handleDryRun(incoming,{R34_HMAC_SECRET:secret},Date.now());
  res.writeHead(answer.status,Object.fromEntries(answer.headers.entries()));
  res.end(await answer.text());
});
server.listen(0,"127.0.0.1");
await once(server,"listening");
const url="http://127.0.0.1:"+server.address().port+"/internal/v1/transport-dry-run";
async function send(value=payload,{badSignature=false,unauthorized=false,approved=true}={}){
 const data=JSON.stringify({...value,approved});
 const ts=String(Date.now());
 const mac=await sign(secret,ts+"."+data);
 const resp=await fetch(url,{method:"POST",headers:{"Content-Type":"application/json","X-R34-Timestamp":ts,
   "X-R34-Signature":"sha256="+(badSignature?"0".repeat(64):mac)},body:data});
 const result=await resp.json();
 assert.equal(result.forwarded??false,false);
 assert.equal(result.publish??false,false);
 if(unauthorized) assert.notEqual(resp.status,200);
 return {http:resp.status,body:result};
}
try{
 const accepted=await send();
 assert.equal(accepted.http,200);
 assert.equal(accepted.body.status,"SIMULATED_ONLY");
 assert.equal(accepted.body.account,"taldiacomohoy09");
 assert.equal((await send({...payload,account:"tuperrofelizofficial"},{unauthorized:true})).http,403);
 assert.equal((await send(payload,{badSignature:true,unauthorized:true})).http,401);
 assert.equal((await send(payload,{approved:false,unauthorized:true})).http,403);
 console.log("R35=PASS; HTTP_LOOPBACK=YES; ACCEPTED=200; WRONG_ACCOUNT=403; INVALID_SIGNATURE=401; UNAPPROVED=403; TIKTOK_POSTS=0; EXTERNAL_REQUESTS=0");
}finally{server.close();}
