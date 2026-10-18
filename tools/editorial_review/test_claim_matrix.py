import copy
import unittest
from validate_claim_matrix import audit

def fixture():
    return {"schema":"p332r11_claim_matrix_v1","approved":False,"publishable":False,
    "dossiers":[{"id":str(i),"status":"UNAPPROVED","claims":[{
        "text":"The primary claim","review_status":"PENDING_HUMAN_REVIEW",
        "citations":[{"organization":"Archive A","url":"https://example.org/a","locator":"paragraph 1","support_excerpt":"primary passage"},
                     {"organization":"Archive B","url":"https://example.net/b","locator":"paragraph 2","support_excerpt":"secondary passage"}]
    }]} for i in range(3)]}
class TestEvidenceMatrix(unittest.TestCase):
    def test_valid_remains_unapproved(self):
        self.assertIn("FACTUAL_APPROVAL_NO",audit(fixture()))
    def reject(self, mutate):
        f=fixture(); mutate(f)
        with self.assertRaises(ValueError):audit(f)
    def test_approval(self):self.reject(lambda f:f.update(approved=True))
    def test_publishable(self):self.reject(lambda f:f.update(publishable=True))
    def test_missing_claim(self):self.reject(lambda f:f["dossiers"][0].update(claims=[]))
    def test_unapproved_only(self):self.reject(lambda f:f["dossiers"][0].update(status="APPROVED"))
    def test_claim_review(self):self.reject(lambda f:f["dossiers"][0]["claims"][0].update(review_status="APPROVED"))
    def test_one_citation(self):self.reject(lambda f:f["dossiers"][0]["claims"][0].update(citations=f["dossiers"][0]["claims"][0]["citations"][:1]))
    def test_same_org(self):self.reject(lambda f:f["dossiers"][0]["claims"][0]["citations"][1].update(organization="Archive A"))
    def test_missing_excerpt(self):self.reject(lambda f:f["dossiers"][0]["claims"][0]["citations"][1].update(support_excerpt=""))
    def test_duplicate_id(self):self.reject(lambda f:f["dossiers"][1].update(id="0"))
    def test_bad_url(self):self.reject(lambda f:f["dossiers"][0]["claims"][0]["citations"][1].update(url="http://example.net"))
if __name__=="__main__":unittest.main()
