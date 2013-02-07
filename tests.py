from __future__ import print_function
import os
import sys
import unittest
import io
from StringIO import StringIO

from xml.sax.saxutils import XMLGenerator

from defusedxml import cElementTree, ElementTree, minidom, pulldom, sax

try:
    from defusedxml import lxml
except ImportError:
    lxml = None


HERE = os.path.dirname(os.path.abspath(__file__))

class BaseTests(unittest.TestCase):
    module = None
    parse = None
    parseString = None

    xml_dtd = os.path.join(HERE, "xmltestdata", "dtd.xml")
    xml_external = os.path.join(HERE, "xmltestdata", "external.xml")
    xml_quadratic = os.path.join(HERE, "xmltestdata", "quadratic.xml")
    xml_simple = os.path.join(HERE, "xmltestdata", "simple.xml")
    xml_simple_ns = os.path.join(HERE, "xmltestdata", "simple-ns.xml")
    xml_bomb = os.path.join(HERE, "xmltestdata", "xmlbomb.xml")

    def setUp(self):
        self.parse = self.module.parse
        if hasattr(self.module, "fromstring"):
            self.parseString = self.module.fromstring
        else:
            self.parseString = self.module.parseString

    def get_content(self, xmlfile):
        with io.open(xmlfile, "rb") as f:
            return f.read()

    def test_simple_parse(self):
        self.parse(self.xml_simple)
        self.parseString(self.get_content(self.xml_simple))


class TestDefusedcElementTree(BaseTests):
    module = cElementTree


class TestDefusedElementTree(BaseTests):
    module = ElementTree


class TestDefusedMinidom(BaseTests):
    module = minidom


class TestDefusedPulldom(BaseTests):
    module = pulldom


class TestDefusedSax(BaseTests):
    module = sax

    def test_simple_parse(self):
        result = StringIO()
        gen = XMLGenerator(result)
        self.module.parse(self.xml_simple, gen)


class TestDefusedLxml(BaseTests):
    module = lxml


def test_main():
    suite = unittest.TestSuite()
    for cls in (TestDefusedcElementTree, TestDefusedElementTree,
                TestDefusedMinidom, TestDefusedPulldom,
                TestDefusedSax):
        suite.addTests(unittest.makeSuite(cls))
    if lxml is not None:
        suite.addTests(unittest.makeSuite(TestDefusedLxml))
    return suite

if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(test_main())
    sys.exit(not result.wasSuccessful())
