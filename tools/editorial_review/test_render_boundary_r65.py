import unittest
from render_boundary_r65 import guarded_invoke

class BoundaryTests(unittest.TestCase):
 def test_denial_never_calls_renderer(self):
  calls=[]
  result=guarded_invoke(lambda:{"render_allowed":False},lambda:calls.append(1))
  self.assertEqual(calls,[])
  self.assertEqual(result["status"],"DENIED_BY_EDITORIAL_GATE")
 def test_malformed_gate_never_calls_renderer(self):
  calls=[]
  with self.assertRaises(RuntimeError):guarded_invoke(lambda:None,lambda:calls.append(1))
  self.assertEqual(calls,[])
 def test_forged_allow_never_calls_renderer(self):
  calls=[]
  with self.assertRaises(RuntimeError):guarded_invoke(lambda:{"render_allowed":True},lambda:calls.append(1))
  self.assertEqual(calls,[])
if __name__=="__main__":unittest.main()
