import copy,json,unittest
from pathlib import Path
from validate_review_queue import check_queue
class ReviewQueueTests(unittest.TestCase):
 def sample(self):
  return json.loads((Path(__file__).parent/"P332R20_EVIDENCE_QUEUE_UNAPPROVED.json").read_text(encoding="utf-8"))
 def test_current_queue_remains_pending(self):self.assertEqual(check_queue(self.sample()),"QUEUE_REVIEW_REQUIRED_PUBLISH_NO")
 def reject(self,fn):
  q=self.sample();fn(q)
  with self.assertRaises(ValueError):check_queue(q)
 def test_approval_refused(self):self.reject(lambda q:q.update(approved=True))
 def test_publish_refused(self):self.reject(lambda q:q.update(publishable=True))
 def test_dossier_approval_refused(self):self.reject(lambda q:q["dossiers"][0].update(status="APPROVED"))
 def test_claim_review_refused(self):self.reject(lambda q:q["dossiers"][0]["claims"][0].update(review="APPROVED"))
 def test_missing_blocker_refused(self):self.reject(lambda q:q["dossiers"][0]["claims"][0].update(blockers=[]))
 def test_false_independence_refused(self):self.reject(lambda q:q["dossiers"][2]["claims"][0]["sources"][0].update(independent_verified=True))
if __name__=="__main__":unittest.main()
