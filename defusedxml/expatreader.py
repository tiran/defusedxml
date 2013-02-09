# defusedxml
#
# Copyright (c) 2013 by Christian Heimes <christian@python.org>
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license for licensing details.
"""Defused xml.sax.expatreader
"""
from __future__ import print_function, absolute_import, division

from xml.sax.expatreader import ExpatParser as _ExpatParser

from .common import (DTDForbidden, EntitiesForbidden,
                     ExternalReferenceForbidden)

__origin__ = "xml.sax.expatreader"


class DefusedExpatParser(_ExpatParser):

    def __init__(self, forbid_dtd=False, forbid_entities=True,
                 *args, **kwargs):
        _ExpatParser.__init__(self, *args, **kwargs)
        self.forbid_dtd = forbid_dtd
        self.forbid_entities = forbid_entities

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

    def reset(self):
        _ExpatParser.reset(self)
        parser = self._parser
        if self.forbid_dtd:
            parser.StartDoctypeDeclHandler = self.start_doctype_decl
        if self.forbid_entities:
            parser.EntityDeclHandler = self.entity_decl
            parser.UnparsedEntityDeclHandler = self.unparsed_entity_decl
        if hasattr(parser.ExternalEntityRefHandler, "__call__"):
            parser.ExternalEntityRefHandler = self.external_entity_ref_handler


def create_parser(*args, **kwargs):
    return DefusedExpatParser(*args, **kwargs)
