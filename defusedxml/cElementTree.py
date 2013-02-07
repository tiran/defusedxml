# defusedxml
#
# Copyright (c) 2013 by Christian Heimes <christian@python.org>
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license for licensing details.
from __future__ import print_function, absolute_import, division

from xml.etree.cElementTree import TreeBuilder as _TreeBuilder
from xml.etree.cElementTree import parse as _parse
from xml.etree.cElementTree import iterparse as _iterparse

from .ElementTree import DefusedXMLParser

__origin__ = "xml.etree.cElementTree"

XMLTreeBuilder = XMLParse = DefusedXMLParser

def parse(source, parser=None, forbid_dtd=False, forbid_entities=True):
    if parser is None:
        parser = DefusedXMLParser(target=_TreeBuilder(),
                                  forbid_dtd=forbid_dtd,
                                  forbid_entities=forbid_entities)
    return _parse(source, parser)


def iterparse(source, events=None, parser=None, forbid_dtd=False,
              forbid_entities=True):
    if parser is None:
        parser = DefusedXMLParser(target=_TreeBuilder())
    return _iterparse(source, events, parser)


def fromstring(text, forbid_dtd=False, forbid_entities=True):
    parser = DefusedXMLParser(target=_TreeBuilder(),
                              forbid_dtd=forbid_dtd,
                              forbid_entities=forbid_entities)
    parser.feed(text)
    return parser.close()

XML = fromstring
