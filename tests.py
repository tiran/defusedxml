from __future__ import print_function
import os
import sys
import unittest

from safexml import cElementTree, ElementTree, expatreader, minidom, pulldom, sax

class TestSafeElementTree(unittest.TestCase):
    pass

def test_main():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestSafeElementTree))
    return suite

if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(test_main())
    sys.exit(not result.wasSuccessful())
