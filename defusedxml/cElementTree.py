# defusedxml
#
# Copyright (c) 2013 by Christian Heimes <christian@python.org>
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license for licensing details.
from __future__ import print_function, absolute_import, division

from xml.etree import cElementTree as ET
from .ElementTree import DefusedXMLParser
from .common import _wire_module


XMLTreeBuilder = XMLParse = DefusedXMLParser

def parse(source, forbid_dtd=False, forbid_entities=True):
    parser = DefusedXMLParser(target=ET.TreeBuilder(),
                              forbid_dtd=forbid_dtd,
                              forbid_entities=forbid_entities)
    return ET.parse(source, parser)


def iterparse(source, events=None, forbid_dtd=False, forbid_entities=True):
    parser = DefusedXMLParser(target=ET.TreeBuilder())
    return ET.iterparse(source, events, parser)


def XML(text, forbid_dtd=False, forbid_entities=True):
    parser = DefusedXMLParser(target=ET.TreeBuilder(),
                              forbid_dtd=forbid_dtd,
                              forbid_entities=forbid_entities)
    parser.feed(text)
    return parser.close()


fromstring = XML


_wire_module(ET, __name__)
