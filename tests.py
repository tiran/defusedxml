from __future__ import print_function
import os
import sys
import unittest
import io
#from StringIO import StringIO

from xml.sax.saxutils import XMLGenerator

from defusedxml import cElementTree, ElementTree, minidom, pulldom, sax
from defusedxml import DTDForbidden, EntityForbidden, NotSupportedError
from defusedxml.common import PY3, PY26


try:
    from defusedxml import lxml
    LXML3 = lxml.LXML3
except ImportError:
    lxml = None
    LXML3 = False


HERE = os.path.dirname(os.path.abspath(__file__))

class BaseTests(unittest.TestCase):
    module = None

    xml_dtd = os.path.join(HERE, "xmltestdata", "dtd.xml")
    xml_external = os.path.join(HERE, "xmltestdata", "external.xml")
    xml_quadratic = os.path.join(HERE, "xmltestdata", "quadratic.xml")
    xml_simple = os.path.join(HERE, "xmltestdata", "simple.xml")
    xml_simple_ns = os.path.join(HERE, "xmltestdata", "simple-ns.xml")
    xml_bomb = os.path.join(HERE, "xmltestdata", "xmlbomb.xml")

    def setUp(self):
        if not hasattr(self, "parse"):
            self.parse = self.module.parse
        if not hasattr(self, "parseString"):
            if hasattr(self.module, "fromstring"):
                self.parseString = self.module.fromstring
            else:
                self.parseString = self.module.parseString
        if PY26:
            # TODO
            self.iterparse = None
        if not hasattr(self, "iterparse"):
            if hasattr(self.module, "iterparse"):
                self.iterparse = self.module.iterparse

    def get_content(self, xmlfile):
        if PY3:
            mode = "r"
        else:
            mode = "rb"
        with io.open(xmlfile, mode) as f:
            return f.read()

    def test_simple_parse(self):
        self.parse(self.xml_simple)
        self.parseString(self.get_content(self.xml_simple))
        if self.iterparse:
            self.iterparse(self.xml_simple)

    def test_simple_parse_ns(self):
        self.parse(self.xml_simple_ns)
        self.parseString(self.get_content(self.xml_simple_ns))
        if self.iterparse:
            self.iterparse(self.xml_simple_ns)

    def test_entities_forbidden(self):
        self.assertRaises(EntityForbidden, self.parse, self.xml_bomb)
        self.assertRaises(EntityForbidden, self.parse, self.xml_quadratic)
        self.assertRaises(EntityForbidden, self.parse, self.xml_external)

        #self.parse(self.xml_dtd)
        self.assertRaises(EntityForbidden, self.parseString,
                          self.get_content(self.xml_bomb))
        self.assertRaises(EntityForbidden, self.parseString,
                          self.get_content(self.xml_quadratic))
        self.assertRaises(EntityForbidden, self.parseString,
                          self.get_content(self.xml_external))

    def test_dtd_forbidden(self):
        self.assertRaises(DTDForbidden, self.parse, self.xml_bomb,
                          forbid_dtd=True)
        self.assertRaises(DTDForbidden, self.parse, self.xml_quadratic,
                          forbid_dtd=True)
        self.assertRaises(DTDForbidden, self.parse, self.xml_external,
                          forbid_dtd=True)
        self.assertRaises(DTDForbidden, self.parse, self.xml_dtd,
                          forbid_dtd=True)

        self.assertRaises(DTDForbidden, self.parseString,
                          self.get_content(self.xml_bomb),
                          forbid_dtd=True)
        self.assertRaises(DTDForbidden, self.parseString,
                          self.get_content(self.xml_quadratic),
                          forbid_dtd=True)
        self.assertRaises(DTDForbidden, self.parseString,
                          self.get_content(self.xml_external),
                          forbid_dtd=True)
        self.assertRaises(DTDForbidden, self.parseString,
                          self.get_content(self.xml_dtd),
                          forbid_dtd=True)


class TestDefusedcElementTree(BaseTests):
    module = cElementTree


class TestDefusedElementTree(BaseTests):
    module = ElementTree


class TestDefusedMinidom(BaseTests):
    module = minidom

    iterparse = None


class TestDefusedPulldom(BaseTests):
    module = pulldom

    iterparse = None

    def parse(self, xmlfile, **kwargs):
        dom = self.module.parse(xmlfile, **kwargs)
        list(dom)

    def parseString(self, xmlstring, **kwargs):
        dom = self.module.parseString(xmlstring, **kwargs)
        list(dom)

class TestDefusedSax(BaseTests):
    module = sax

    iterparse = None

    def parse(self, xmlfile, **kwargs):
        if PY3:
            result = io.StringIO()
        else:
            result = io.BytesIO()
        handler = XMLGenerator(result)
        self.module.parse(xmlfile, handler, **kwargs)

    def parseString(self, xmlstring, **kwargs):
        if PY3:
            result = io.StringIO()
        else:
            result = io.BytesIO()
        handler = XMLGenerator(result)
        self.module.parseString(xmlstring, handler, **kwargs)


class TestDefusedLxml(BaseTests):
    module = lxml

    iterparse = None

    if not LXML3:
        def test_entities_forbidden(self):
            self.assertRaises(NotSupportedError, self.parse, self.xml_bomb)


def test_main():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestDefusedcElementTree))
    suite.addTests(unittest.makeSuite(TestDefusedElementTree))
    suite.addTests(unittest.makeSuite(TestDefusedMinidom))
    suite.addTests(unittest.makeSuite(TestDefusedPulldom))
    suite.addTests(unittest.makeSuite(TestDefusedSax))
    if lxml is not None:
        suite.addTests(unittest.makeSuite(TestDefusedLxml))
    return suite

if __name__ == "__main__":
    suite = test_main()
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
