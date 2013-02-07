# defusedxml
#
# Copyright (c) 2013 by Christian Heimes <christian@python.org>
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license for licensing details.
"""Defused xml.etree.ElementTree facade
"""
from __future__ import print_function, absolute_import, division

import sys
from xml.etree.ElementTree import XMLParser as _XMLParser
from xml.etree.ElementTree import TreeBuilder as _TreeBuilder
from xml.etree.ElementTree import parse as _parse
from xml.etree.ElementTree import iterparse as _iterparse
from xml.etree.ElementTree import __all__

from .common import DTDForbidden, EntityForbidden, PY3, PY26


__origin__ = "xml.etree.ElementTree"

class DefusedXMLParser(_XMLParser):
    def __init__(self, html=0, target=None, encoding=None,
                 forbid_dtd=False, forbid_entities=True):
        if PY3:
            super().__init__(html, target, encoding)
        elif PY26:
            # Python 2.x old style class
            _XMLParser.__init__(self, html, target)
        else:
            # Python 2.x old style class
            _XMLParser.__init__(self, html, target, encoding)
        self.forbid_dtd = forbid_dtd
        self.forbid_entities = forbid_entities
        if self.forbid_dtd:
            self._parser.StartDoctypeDeclHandler = self.start_doctype_decl
        if self.forbid_entities:
            self._parser.EntityDeclHandler = self.entity_decl
            self._parser.UnparsedEntityDeclHandler = self.unparsed_entity_decl

    def start_doctype_decl(self, name, sysid, pubid, has_internal_subset):
        raise DTDForbidden(name, sysid, pubid)

    def entity_decl(self, entityName, is_parameter_entity, value, base,
                    systemId, publicId, notationName):
        raise EntityForbidden(entityName)

    def unparsed_entity_decl(self, name, base, sysid, pubid, notation_name):
        # expat 1.2
        raise EntityForbidden(name)


# aliases
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
