# defusedxml
#
# Copyright (c) 2013 by Christian Heimes <christian@python.org>
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license for licensing details.
"""Defused xml.dom.expatbuilder
"""
from __future__ import print_function, absolute_import, division

from xml.dom.expatbuilder import ExpatBuilder as _ExpatBuilder
from xml.dom.expatbuilder import Namespaces as _Namespaces

from .common import DTDForbidden, EntityForbidden, PY3

__origin__ = "xml.dom.expatbuilder"


class DefusedExpatBuilder(_ExpatBuilder):
    def __init__(self, options=None, forbid_dtd=False, forbid_entities=True):
        if PY3:
            super().__init__(options)
        else:
            # Python 2.x old style class
            _ExpatBuilder.__init__(self, options)
        self.forbid_dtd = forbid_dtd
        self.forbid_entities = forbid_entities

    def start_doctype_decl(self, name, sysid, pubid, has_internal_subset):
        raise DTDForbidden(name, sysid, pubid)

    def entity_decl(self, entityName, is_parameter_entity, value, base,
                    systemId, publicId, notationName):
        raise EntityForbidden(entityName)

    def unparsed_entity_decl(self, name, base, sysid, pubid, notation_name):
        # expat 1.2
        raise EntityForbidden(name)

    def external_entity_ref_handler(self, context, base, systemId, publicId):
        raise EntityForbidden(systemId, publicId)

    def install(self, parser):
        if PY3:
            super().install(parser)
        else:
            # Python 2.x old style class
            _ExpatBuilder.install(self, parser)

        if self.forbid_dtd:
            parser.StartDoctypeDeclHandler = self.start_doctype_decl
        if self.forbid_entities:
            #if self._options.entities:
            parser.EntityDeclHandler = self.entity_decl
            parser.UnparsedEntityDeclHandler = self.unparsed_entity_decl
            parser.ExternalEntityRefHandler = self.external_entity_ref_handler


class DefusedExpatBuilderNS(_Namespaces, DefusedExpatBuilder):
    """Document builder that supports namespaces."""

    def install(self, parser):
        if PY3:
            super().install(parser)
        else:
            # Python 2.x
            DefusedExpatBuilder.install(self, parser)
            if self._options.namespace_declarations:
                parser.StartNamespaceDeclHandler = (
                    self.start_namespace_decl_handler)

    def reset(self):
        if PY3:
            super().reset()
        else:
            DefusedExpatBuilder.reset(self)
        self._initNamespaces()


def parse(file, namespaces=True, forbid_dtd=False, forbid_entities=True):
    """Parse a document, returning the resulting Document node.

    'file' may be either a file name or an open file object.
    """
    if namespaces:
        builder = DefusedExpatBuilderNS(forbid_dtd=forbid_dtd,
                                        forbid_entities=forbid_entities)
    else:
        builder = DefusedExpatBuilder(forbid_dtd=forbid_dtd,
                                      forbid_entities=forbid_entities)

    if isinstance(file, str):
        fp = open(file, 'rb')
        try:
            result = builder.parseFile(fp)
        finally:
            fp.close()
    else:
        result = builder.parseFile(file)
    return result


def parseString(string, namespaces=True, forbid_dtd=False,
                forbid_entities=True):
    """Parse a document from a string, returning the resulting
    Document node.
    """
    if namespaces:
        builder = DefusedExpatBuilderNS(forbid_dtd=forbid_dtd,
                                        forbid_entities=forbid_entities)
    else:
        builder = DefusedExpatBuilder(forbid_dtd=forbid_dtd,
                                      forbid_entities=forbid_entities)
    return builder.parseString(string)
