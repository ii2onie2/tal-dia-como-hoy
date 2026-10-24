import unittest,copy,json
from pathlib import Path
from validate_independence import assess
def fixture():
 return json.loads((Path(__file__).parent/"P332R20_EVIDENCE_QUEUE_UNAPPROVED.json").read_text(encoding="utf-8"))
class IndependenceTests(unittest.TestCase):
 def test_pending_queue(self):
  r=assess(fixture());self.assertEqual(len(r["claims"]),3);self.assertFalse(r["approved"])
 def test_same_editorial_group_count_once(self):
  q=fixture();ss=q["dossiers"][0]["claims"][0]["sources"]
  ss[0]["editorial_control_group"]="BOE";ss[0]["control_group_reviewed"]=True
  s=copy.deepcopy(ss[0]);s["url"]="https://www.boe.es/buscar/doc.php?id=BOE-A-1977-24937";ss.append(s)
  self.assertEqual(assess(q)["claims"][0]["independent_groups_reviewed"],1)
 def test_two_websites_not_independence_without_review(self):
  q=fixture();ss=q["dossiers"][2]["claims"][0]["sources"]
  ss.append({"publisher":"External Mirror","url":"https://example.org/mirror","locator":"section","independent_verified":False,"editorial_control_group":"Unreviewed","control_group_reviewed":False})
  self.assertEqual(assess(q)["claims"][2]["independent_groups_reviewed"],0)
 def test_forbid_approval(self):
  q=fixture();q["approved"]=True
  with self.assertRaises(ValueError):assess(q)
 def test_forbid_fake_independent(self):
  q=fixture();q["dossiers"][0]["claims"][0]["sources"][0]["independent_verified"]=True
  with self.assertRaises(ValueError):assess(q)
if __name__=="__main__":unittest.main()
