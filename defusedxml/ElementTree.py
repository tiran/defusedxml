# defusedxml
#
# Copyright (c) 2013 by Christian Heimes <christian@python.org>
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license for licensing details.
"""Defused xml.etree.ElementTree facade
"""
from __future__ import print_function, absolute_import

import sys
from .common import PY3, PY26
if PY3:
    import importlib
else:
    from xml.etree.ElementTree import XMLParser as _XMLParser
    from xml.etree.ElementTree import iterparse as _iterparse
    if PY26:
        from xml.parsers.expat import ExpatError as ParseError
    else:
        from xml.etree.ElementTree import ParseError
    _IterParseIterator = None
from xml.etree.ElementTree import TreeBuilder as _TreeBuilder
from xml.etree.ElementTree import parse as _parse

from .common import (DTDForbidden, EntitiesForbidden,
                     ExternalReferenceForbidden, _generate_etree_functions)

__origin__ = "xml.etree.ElementTree"

def _get_python_classes():
    """Python 3.3 hides the pure Python code but defusedxml requires it.

    The code is based on test.support.import_fresh_module().
    """
    global _XMLParser, _iterparse, _IterParseIterator, ParseError
    pymodname = "xml.etree.ElementTree"
    cmodname = "_elementtree"

    pymod = sys.modules.pop(pymodname, None)
    cmod = sys.modules.pop(cmodname, None)

    sys.modules[cmodname] = None
    pure_pymod = importlib.import_module(pymodname)
    if cmod is not None:
        sys.modules[cmodname] = cmod
    else:
        sys.modules.pop(cmodname)
    sys.modules[pymodname] = pymod

    _XMLParser = pure_pymod.XMLParser
    _iterparse = pure_pymod.iterparse
    _IterParseIterator = pure_pymod._IterParseIterator
    ParseError = pure_pymod.ParseError

if PY3:
    _get_python_classes()


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
        if PY3:
            parser = self.parser
        else:
            parser = self._parser
        if self.forbid_dtd:
            parser.StartDoctypeDeclHandler = self.start_doctype_decl
        if self.forbid_entities:
            parser.EntityDeclHandler = self.entity_decl
            parser.UnparsedEntityDeclHandler = self.unparsed_entity_decl
        if hasattr(parser.ExternalEntityRefHandler, "__call__"):
            parser.ExternalEntityRefHandler = self.external_entity_ref_handler

    def start_doctype_decl(self, name, sysid, pubid, has_internal_subset):
        raise DTDForbidden(name, sysid, pubid)

    def entity_decl(self, name, is_parameter_entity, value, base,
                    sysid, pubid, notation_name):

        raise EntitiesForbidden(name, value, base, sysid, pubid, notation_name)

    def unparsed_entity_decl(self, name, base, sysid, pubid, notation_name):
        # expat 1.2
        raise EntitiesForbidden(name, None, base, sysid, pubid, notation_name)

    def external_entity_ref_handler(self, context, base, sysid, pubid):
        raise ExternalReferenceForbidden(context, base, sysid, pubid)


# aliases
XMLTreeBuilder = XMLParse = DefusedXMLParser

parse, iterparse, fromstring = _generate_etree_functions(DefusedXMLParser,
        _TreeBuilder, _IterParseIterator, _parse, _iterparse)
XML = fromstring
