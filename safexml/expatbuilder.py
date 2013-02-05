# safexml
#
# Copyright (c) 2013 by Christian Heimes <christian@cheimes.de>
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license for licensing details.
"""Safe xml.dom.expatbuilder
"""
from __future__ import print_function, absolute_import, division

from xml.dom.expatbuilder import ExpatBuilder as _ExpatBuilder
from xml.dom.expatbuilder import Namespaces as _Namespaces

from .exceptions import DTDForbidden, EntityForbidden
from .compat import PY3


class SafeExpatBuilder(_ExpatBuilder):
    def __init__(self, options=None, forbid_dtd=False, forbid_entities=True):
        if PY3:
            super().__init__(options)
        else:
            # Python 2.x old style class
            _ExpatBuilder.__init__(options)
        self.forbid_dtd = forbid_dtd
        self.forbid_entities = forbid_entities

    def start_doctype_decl(self, name, sysid, pubid, has_internal_subset):
        raise DTDForbidden(name, sysid, pubid)

    def entity_decl(self, entityName, is_parameter_entity, value, base,
                    systemId, publicId, notationName):
        raise EntityForbidden(entityName)

    def external_entity_ref_handler(self, context, base, systemId, publicId):
        raise EntityForbidden(context)

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
            parser.ExternalEntityRefHandler = self.external_entity_ref_handler


class SafeExpatBuilderNS(_Namespaces, SafeExpatBuilder):
    """Document builder that supports namespaces."""

    def reset(self):
        if PY3:
            super().reset(self)
        else:
            SafeExpatBuilder.reset(self)
        self._initNamespaces()


def parse(file, namespaces=True):
    """Parse a document, returning the resulting Document node.

    'file' may be either a file name or an open file object.
    """
    if namespaces:
        builder = SafeExpatBuilderNS()
    else:
        builder = SafeExpatBuilder()

    if isinstance(file, str):
        fp = open(file, 'rb')
        try:
            result = builder.parseFile(fp)
        finally:
            fp.close()
    else:
        result = builder.parseFile(file)
    return result


def parseString(string, namespaces=True):
    """Parse a document from a string, returning the resulting
    Document node.
    """
    if namespaces:
        builder = SafeExpatBuilderNS()
    else:
        builder = SafeExpatBuilder()
    return builder.parseString(string)
