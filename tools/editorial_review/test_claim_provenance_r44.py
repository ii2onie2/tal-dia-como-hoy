import unittest
from validate_claim_provenance_r44 import validate_claim_provenance

def make():
 c=lambda org,url:{"organization":org,"url":url,"locator":"archive p. 3","support_excerpt":"This excerpt is an unverified synthetic test fixture."}
 return {"schema":"p332r11_claim_matrix_v1","approved":False,"publishable":False,"dossiers":[{"id":str(i),"status":"UNAPPROVED","claims":[{"text":"Test claim","review_status":"PENDING_HUMAN_REVIEW","approved":False,"publishable":False,"citations":[c("Official","https://official.example.org/a"),c("Archive","https://archive.example.net/b")]}]} for i in range(3)]}

class TestR44(unittest.TestCase):
 def test_valid_structure_never_approves(self):
  self.assertIn("APPROVAL_NO",validate_claim_provenance(make()))
 def reject(self,mut):
  m=make();mut(m)
  with self.assertRaises(ValueError): validate_claim_provenance(m)
 def test_approval(self):self.reject(lambda m:m["dossiers"][0]["claims"][0].update(approved=True))
 def test_same_hostname(self):self.reject(lambda m:m["dossiers"][0]["claims"][0]["citations"][1].update(url="https://official.example.org/b"))
 def test_private_host(self):self.reject(lambda m:m["dossiers"][0]["claims"][0]["citations"][0].update(url="https://localhost/a"))
 def test_url_credentials(self):self.reject(lambda m:m["dossiers"][0]["claims"][0]["citations"][0].update(url="https://user:pass@official.example.org"))
 def test_ip_literal(self):self.reject(lambda m:m["dossiers"][0]["claims"][0]["citations"][0].update(url="https://127.0.0.1"))
 def test_short_excerpt(self):self.reject(lambda m:m["dossiers"][0]["claims"][0]["citations"][0].update(support_excerpt="short"))
if __name__=="__main__":unittest.main()
