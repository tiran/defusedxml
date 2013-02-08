from __future__ import print_function
import os
import sys
import unittest
import io

from xml.sax.saxutils import XMLGenerator

from defusedxml import cElementTree, ElementTree, minidom, pulldom, sax
from defusedxml import (DefusedXmlException, DTDForbidden, EntitiesForbidden,
                        ExternalEntitiesForbidden, NotSupportedError)
from defusedxml.common import PY3, PY26


try:
    from defusedxml import lxml
    LXML3 = lxml.LXML3
except ImportError:
    lxml = None
    LXML3 = False


HERE = os.path.dirname(os.path.abspath(__file__))

# prevent web access
# based on Debian's rules, Port 9 is discard
os.environ["http_proxy"] = "http://127.0.9.1:9"
os.environ["https_proxy"] = os.environ["http_proxy"]
os.environ["ftp_proxy"] = os.environ["http_proxy"]


class BaseTests(unittest.TestCase):

    module = None

    if PY3:
        content_binary = False
    else:
        content_binary = True

    dtd_external_ref = False

    xml_dtd = os.path.join(HERE, "xmltestdata", "dtd.xml")
    xml_external = os.path.join(HERE, "xmltestdata", "external.xml")
    xml_quadratic = os.path.join(HERE, "xmltestdata", "quadratic.xml")
    xml_simple = os.path.join(HERE, "xmltestdata", "simple.xml")
    xml_simple_ns = os.path.join(HERE, "xmltestdata", "simple-ns.xml")
    xml_bomb = os.path.join(HERE, "xmltestdata", "xmlbomb.xml")
    xml_bomb2 = os.path.join(HERE, "xmltestdata", "xmlbomb2.xml")

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
        mode = "rb" if self.content_binary else "r"
        with io.open(xmlfile, mode) as f:
            data = f.read()
        return data

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
        self.assertRaises(EntitiesForbidden, self.parse, self.xml_bomb)
        self.assertRaises(EntitiesForbidden, self.parse, self.xml_quadratic)
        self.assertRaises(EntitiesForbidden, self.parse, self.xml_external)

        self.assertRaises(EntitiesForbidden, self.parseString,
                          self.get_content(self.xml_bomb))
        self.assertRaises(EntitiesForbidden, self.parseString,
                          self.get_content(self.xml_quadratic))
        self.assertRaises(EntitiesForbidden, self.parseString,
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

    def test_dtd_with_external_ref(self):
        if self.dtd_external_ref:
            self.assertRaises(ExternalEntitiesForbidden, self.parse,
                              self.xml_dtd)
        else:
            self.parse(self.xml_dtd)

    def test_external_ref(self):
        self.assertRaises(ExternalEntitiesForbidden, self.parse,
                          self.xml_external, forbid_entities=False)


class TestDefusedcElementTree(BaseTests):
    module = cElementTree

    def test_external_ref(self):
        # etree doesn't do external ref lookup
        self.assertRaises(ElementTree.ParseError, self.parse,
                          self.xml_external, forbid_entities=False)


class TestDefusedElementTree(BaseTests):
    module = ElementTree

    def test_external_ref(self):
        # etree doesn't do external ref lookup
        self.assertRaises(ElementTree.ParseError, self.parse,
                          self.xml_external, forbid_entities=False)


class TestDefusedMinidom(BaseTests):
    module = minidom

    iterparse = None


class TestDefusedPulldom(BaseTests):
    module = pulldom

    dtd_external_ref = True
    iterparse = None

    def parse(self, xmlfile, **kwargs):
        dom = self.module.parse(xmlfile, **kwargs)
        list(dom)

    def parseString(self, xmlstring, **kwargs):
        dom = self.module.parseString(xmlstring, **kwargs)
        list(dom)


class TestDefusedSax(BaseTests):
    module = sax

    content_binary = True
    dtd_external_ref = True

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

    content_binary = True
    iterparse = None

    if not LXML3:
        def test_entities_forbidden(self):
            self.assertRaises(NotSupportedError, self.parse, self.xml_bomb)

        def test_dtd_with_external_ref(self):
            self.assertRaises(NotSupportedError, self.parse, self.xml_dtd)

    def test_external_ref(self):
        pass

    def test_restricted_element1(self):
        tree = self.module.parse(self.xml_bomb, forbid_dtd=False,
                                 forbid_entities=False)
        root = tree.getroot()
        self.assertEqual(root.text, None)

        self.assertEqual(list(root), [])
        self.assertEqual(root.getchildren(), [])
        self.assertEqual(list(root.iter()), [root])
        self.assertEqual(list(root.iterchildren()), [])
        self.assertEqual(list(root.iterdescendants()), [])
        self.assertEqual(list(root.itersiblings()), [])
        self.assertEqual(list(root.getiterator()), [root])
        self.assertEqual(root.getnext(), None)


    def test_restricted_element2(self):
        tree = self.module.parse(self.xml_bomb2, forbid_dtd=False,
                                 forbid_entities=False)
        root = tree.getroot()
        bomb, tag = root
        self.assertEqual(root.text, "text")

        self.assertEqual(list(root), [bomb, tag])
        self.assertEqual(root.getchildren(), [bomb, tag])
        self.assertEqual(list(root.iter()), [root, bomb, tag])
        self.assertEqual(list(root.iterchildren()), [bomb, tag])
        self.assertEqual(list(root.iterdescendants()), [bomb, tag])
        self.assertEqual(list(root.itersiblings()), [])
        self.assertEqual(list(root.getiterator()), [root, bomb, tag])
        self.assertEqual(root.getnext(), None)
        self.assertEqual(root.getprevious(), None)

        self.assertEqual(list(bomb.itersiblings()), [tag])
        self.assertEqual(bomb.getnext(), tag)
        self.assertEqual(bomb.getprevious(), None)
        self.assertEqual(tag.getnext(), None)
        self.assertEqual(tag.getprevious(), bomb)



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
