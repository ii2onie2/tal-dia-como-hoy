"""Bounded TLS-pinned HTTPS evidence retrieval; no automatic approvals."""
import argparse
import hashlib
import http.client
import ipaddress
import json
import socket
import ssl
from email.message import Message
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
ALLOWED={"www.boe.es","www.rtve.es","www.unav.edu"}
MAX_BYTES=262144

def validate_url(url):
    if not isinstance(url,str):raise ValueError("INVALID_URL")
    p=urlsplit(url)
    if p.scheme!="https" or p.hostname not in ALLOWED or p.port not in (None,443) or p.username or p.password or p.fragment:
        raise ValueError("URL_NOT_ALLOWED")
    return p.hostname

def public_addresses(host,resolve):
    answers=resolve(host,443,type=socket.SOCK_STREAM)
    if not answers:raise ValueError("NO_DNS")
    addresses=[]
    for answer in answers:
        ip=ipaddress.ip_address(answer[4][0])
        if not ip.is_global:raise ValueError("UNSAFE_DNS_IP")
        addresses.append(str(ip))
    return sorted(set(addresses))

class PinnedHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self,host,pinned_ip,**kw):
        super().__init__(host,port=443,context=ssl.create_default_context(),**kw)
        self.pinned_ip=pinned_ip
    def connect(self):
        sock=socket.create_connection((self.pinned_ip,443),self.timeout)
        try:
            self.sock=self._context.wrap_socket(sock,server_hostname=self.host)
        except BaseException:
            sock.close()
            raise

class ResponseAdapter:
    def __init__(self,response,connection):
        self.response=response
        self.connection=connection
        self.status=response.status
        self.headers=Message()
        for k,v in response.getheaders():self.headers[k]=v
    def read(self,n):return self.response.read(n)
    def __enter__(self):return self
    def __exit__(self,*exc):self.connection.close()

class LiveClient:
    def __init__(self,address):self.address=address
    def open(self,req,timeout):
        p=urlsplit(req.full_url)
        con=PinnedHTTPSConnection(p.hostname,self.address,timeout=timeout)
        try:
            path=urlunsplit(("","",p.path or "/",p.query,""))
            con.request("GET",path,headers={"Host":p.hostname,"Accept":"text/html,text/plain","User-Agent":"EditorialEvidenceAudit/1.0"})
            return ResponseAdapter(con.getresponse(),con)
        except BaseException:
            con.close()
            raise

def fetch(url,resolve=socket.getaddrinfo,opener=None):
    host=validate_url(url)
    ips=public_addresses(host,resolve)
    client=opener if opener is not None else LiveClient(ips[0])
    req=type("Request",(),{"full_url":url})()
    with client.open(req,timeout=8) as resp:
        if resp.status!=200:raise ValueError("HTTP_STATUS_OR_REDIRECT_FORBIDDEN")
        mime=resp.headers.get_content_type()
        if mime not in ("text/html","text/plain"):raise ValueError("UNSAFE_CONTENT_TYPE")
        size=resp.headers.get("Content-Length")
        if size is not None and int(size)>MAX_BYTES:raise ValueError("OVERSIZE")
        data=resp.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES:raise ValueError("OVERSIZE")
    return {"url":url,"sha256":hashlib.sha256(data).hexdigest(),"byte_count":len(data),
            "content_type":mime,"approved":False,"publishable":False},data

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--url",required=True)
    ap.add_argument("--output-dir",required=True)
    ap.add_argument("--enable-live-network",action="store_true")
    a=ap.parse_args()
    if not a.enable_live_network:raise SystemExit("LIVE_NETWORK_DISABLED_BY_DEFAULT")
    meta,data=fetch(a.url)
    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    digest=meta["sha256"]
    (out/(digest+".raw")).write_bytes(data)
    (out/(digest+".json")).write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(meta,sort_keys=True))
if __name__=="__main__":main()
