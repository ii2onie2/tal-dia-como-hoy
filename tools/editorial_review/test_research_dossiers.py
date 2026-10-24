"""Fail-closed structural checks only: tests do not establish historical truth."""
import copy
import unittest
from validate_research_dossiers import check

def fixture():
    sources=[
        {"organization":"Archive A","url":"https://example.org/a","locator":"Section 2","facts":["A claim with adequate length"]},
        {"organization":"Archive B","url":"https://example.net/b","locator":"Section 4","facts":["Another independently cited claim"]}
    ]
    return {"schema":"p332r8_research_v1","brand":"history","date":"2026-10-17",
        "evidence_review_approved":False,"publication_approved":False,"media_license_approved":False,
        "dossiers":[{"slot":slot,"date":"2026-10-17","topic":"Topic "+str(i),
        "event_date":"1991-10-17","fact_check_status":"SOURCE_TEXT_CROSSCHECKED_NOT_FORMALLY_APPROVED",
        "evidence_review_approved":False,"publication_approved":False,"media_license_approved":False,
        "sources":copy.deepcopy(sources)} for i,slot in enumerate(("10:00","16:00","19:00"))]}

class GateTests(unittest.TestCase):
    def test_valid_structure_not_approval(self):
        self.assertEqual(check(fixture(),"history","2026-10-17"),"RESEARCH_STRUCTURE_PASS_APPROVAL_NO")
    def blocked(self,change):
        packet=fixture(); change(packet)
        with self.assertRaises(ValueError):check(packet,"history","2026-10-17")
    def test_wrong_date(self): self.blocked(lambda p:p.update(date="2026-10-18"))
    def test_root_approval(self): self.blocked(lambda p:p.update(publication_approved=True))
    def test_dossier_approval(self):self.blocked(lambda p:p["dossiers"][0].update(evidence_review_approved=True))
    def test_one_source(self):self.blocked(lambda p:p["dossiers"][0].update(sources=p["dossiers"][0]["sources"][:1]))
    def test_same_organization(self):self.blocked(lambda p:p["dossiers"][0]["sources"][1].update(organization="Archive A"))
    def test_missing_locator(self):self.blocked(lambda p:p["dossiers"][0]["sources"][0].update(locator=""))
    def test_anniversary_mismatch(self):self.blocked(lambda p:p["dossiers"][0].update(event_date="1991-10-18"))
    def test_duplicate(self):self.blocked(lambda p:p["dossiers"][1].update(topic="Topic 0"))
    def test_unsafe_url(self):self.blocked(lambda p:p["dossiers"][0]["sources"][0].update(url="http://example.net"))
    def test_dogs_fixture(self):
        p=fixture();p["brand"]="dogs"
        for d in p["dossiers"]:d.pop("event_date",None)
        self.assertEqual(check(p,"dogs","2026-10-17"),"RESEARCH_STRUCTURE_PASS_APPROVAL_NO")
    def test_missing_flag(self):
        self.blocked(lambda p:p["dossiers"][0].pop("media_license_approved"))

if __name__=="__main__":unittest.main()
