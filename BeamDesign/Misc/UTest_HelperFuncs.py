"""Unit tests for the HelperFunc module"""

import unittest
import HelperFuncs

class Test_HelperFuncs(unittest.TestCase):
    """this class provides unit tests for the helper functions file."""

    def test_AlmostEqual(self):
        """Tests the "AlmostEqual function"""
        #first test a couple of cases we know should be true
        self.assertEqual(HelperFuncs.almostEqual(2.0,2.1,0.2),True)
        self.assertEqual(HelperFuncs.almostEqual(-2.0,-1.9,0.2),True)
        
        #next test a couple of cases we know should be false
        self.assertFalse(HelperFuncs.almostEqual(2.0,2.1,0.1),True)
        self.assertFalse(HelperFuncs.almostEqual(-2.0,-1.9,0.1),True)

if __name__ == '__main__':
    unittest.main()
