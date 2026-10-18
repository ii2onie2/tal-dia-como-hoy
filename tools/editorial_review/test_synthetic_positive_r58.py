import unittest
from synthetic_positive_r58 import synthetic_walkthrough

class SyntheticPositiveTests(unittest.TestCase):
 def test_positive_crypto_without_release(self):
  r=synthetic_walkthrough()
  self.assertEqual(r["contract_result"],"SIMULATED_VALIDITY_ONLY_RELEASE_DENIED")
  self.assertTrue(r["synthetic"])
  for field in ("editorial_approved","render_authorized","transfer_authorized","publish_authorized"):
   self.assertFalse(r[field])
if __name__=="__main__":unittest.main()
