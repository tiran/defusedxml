# defusedxml
#
# Copyright (c) 2013 by Christian Heimes <christian@cheimes.de>
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license for licensing details.
"""Defused xml.sax.expatreader
"""
from __future__ import print_function, absolute_import, division

from xml.sax.expatreader import ExpatParser as _ExpatParser

from .exceptions import DTDForbidden, EntityForbidden
from .compat import PY3


class DefusedExpatParser(_ExpatParser):
    def __init__(self, forbid_dtd=False, forbid_entities=True,
                 *args, **kwargs):
        if PY3:
            super().__init__(*args, **kwargs)
        else:
            # Python 2.x old style class
            _ExpatParser.__init__(self, *args, **kwargs)
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

    def reset(self):
        if PY3:
            super().reset()
        else:
            # Python 2.x old style class
            _ExpatParser.reset(self)
        if self.forbid_dtd:
            self._parser.StartDoctypeDeclHandler = self.start_doctype_decl
        if self.forbid_entities:
            self._parser.EntityDeclHandler = self.entity_decl
            self._parser.UnparsedEntityDeclHandler = self.unparsed_entity_decl


def create_parser(*args, **kwargs):
    return DefusedExpatParser(*args, **kwargs)
