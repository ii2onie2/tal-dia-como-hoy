import io
import unittest
from email.message import Message
from fetch_public_evidence import fetch,validate_url
class FakeResponse:
    status=200
    def __init__(self,data=b"<html>Test</html>",kind="text/html"):
        self.buf=io.BytesIO(data);self.headers=Message();self.headers.add_header("Content-Type",kind)
    def __enter__(self):return self
    def __exit__(self,*a):pass
    def read(self,n):return self.buf.read(n)
class FakeOpen:
    def __init__(self,r):self.r=r
    def open(self,req,timeout):return self.r
def dns(host,port,type):
    return [(2,1,6,"",("8.8.8.8",443))]
class Tests(unittest.TestCase):
    def test_valid(self):
        m,data=fetch("https://www.boe.es/a",dns,FakeOpen(FakeResponse()))
        self.assertFalse(m["approved"]);self.assertEqual(len(m["sha256"]),64)
    def test_unsafe_domain(self):
        with self.assertRaises(ValueError):validate_url("https://evil.example/a")
    def test_http(self):
        with self.assertRaises(ValueError):validate_url("http://www.boe.es/a")
    def test_credentials(self):
        with self.assertRaises(ValueError):validate_url("https://x@www.boe.es/a")
    def test_private_dns(self):
        with self.assertRaises(ValueError):
            fetch("https://www.boe.es/a",lambda *a,**kw:[(2,1,6,"",("127.0.0.1",443))],FakeOpen(FakeResponse()))
    def test_wrong_type(self):
        with self.assertRaises(ValueError):fetch("https://www.boe.es/a",dns,FakeOpen(FakeResponse(kind="application/pdf")))
    def test_too_big(self):
        with self.assertRaises(ValueError):fetch("https://www.boe.es/a",dns,FakeOpen(FakeResponse(data=b"x"*262145)))
if __name__=="__main__":unittest.main()
