"""P3.32R14 bounded HTTPS evidence fetcher; never approval or publishing."""
import argparse
import hashlib
import json
import socket
import ipaddress
import urllib.request
from urllib.parse import urlsplit
from pathlib import Path

ALLOWED={"www.boe.es","www.rtve.es","www.unav.edu"}
MAX_BYTES=262144
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        raise ValueError("REDIRECT_FORBIDDEN")

def validate_url(url):
    if not isinstance(url,str):raise ValueError("INVALID_URL")
    p=urlsplit(url)
    if (p.scheme!="https" or p.hostname not in ALLOWED or p.port not in (None,443)
        or p.username or p.password or p.fragment):
        raise ValueError("URL_NOT_ALLOWED")
    return p.hostname

def fetch(url,resolve=socket.getaddrinfo,opener=None):
    host=validate_url(url)
    answers=resolve(host,443,type=socket.SOCK_STREAM)
    if not answers:raise ValueError("NO_DNS")
    for answer in answers:
        ip=ipaddress.ip_address(answer[4][0])
        if not ip.is_global:raise ValueError("UNSAFE_DNS_IP")
    # P3.32R15: DNS prechecking cannot pin the subsequent urllib TCP connection.\n    # Until a pinned-IP TLS transport is implemented and tested, refuse live I/O.\n    if opener is None:\n        raise ValueError("LIVE_NETWORK_DISABLED_UNTIL_PINNED_TLS")\n    client=opener
    req=urllib.request.Request(url,headers={"User-Agent":"EditorialEvidenceAudit/1.0","Accept":"text/html,text/plain"})
    with client.open(req,timeout=8) as resp:
        if resp.status!=200:raise ValueError("HTTP_STATUS")
        mime=resp.headers.get_content_type()
        if mime not in ("text/html","text/plain"):raise ValueError("UNSAFE_CONTENT_TYPE")
        size=resp.headers.get("Content-Length")
        if size is not None and int(size)>MAX_BYTES:raise ValueError("OVERSIZE")
        data=resp.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES:raise ValueError("OVERSIZE")
    return {"url":url,"sha256":hashlib.sha256(data).hexdigest(),
            "byte_count":len(data),"content_type":mime,
            "approved":False,"publishable":False},data

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--url",required=True)
    p.add_argument("--output-dir",required=True)
    a=p.parse_args()
    meta,data=fetch(a.url)
    out=Path(a.output_dir)
    out.mkdir(parents=True,exist_ok=True)
    digest=meta["sha256"]
    (out/(digest+".raw")).write_bytes(data)
    (out/(digest+".json")).write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(meta,sort_keys=True))
if __name__=="__main__":main()
