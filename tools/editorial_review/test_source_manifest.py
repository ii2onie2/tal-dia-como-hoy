import unittest
from validate_source_manifest import check_manifest

def fixture():
 return {"schema":"p332r13_source_manifest_v1","approved":False,"publishable":False,"sources":[{"id":"s1","url":"https://www.boe.es/buscar/act.php?id=BOE-A-1977-24937","organization":"BOE","claim_id":"A1","locator":"disposicion final","accessed_utc":"2026-10-18","source_type":"official","verified_by_human":False}]}
class Tests(unittest.TestCase):
 def test_manifest_nonapproval(self):self.assertIn("APPROVAL_NO",check_manifest(fixture()))
 def denied(self, f):
  d=fixture();f(d)
  with self.assertRaises(ValueError):check_manifest(d)
 def test_private_host(self):self.denied(lambda d:d["sources"][0].update(url="https://localhost/"))
 def test_ip_host(self):self.denied(lambda d:d["sources"][0].update(url="https://127.0.0.1/"))
 def test_http(self):self.denied(lambda d:d["sources"][0].update(url="http://www.boe.es/"))
 def test_approved(self):self.denied(lambda d:d.update(approved=True))
 def test_human_claim(self):self.denied(lambda d:d["sources"][0].update(verified_by_human=True))
 def test_empty(self):self.denied(lambda d:d.update(sources=[]))
 def test_duplicate(self):self.denied(lambda d:d["sources"].append(dict(d["sources"][0])))
if __name__=="__main__":unittest.main()
