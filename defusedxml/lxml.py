# defusedxml
#
# Copyright (c) 2013 by Christian Heimes <christian@python.org>
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license for licensing details.
from __future__ import print_function, absolute_import, division

import threading
from lxml import etree

from .common import DTDForbidden, EntityForbidden, NotSupportedError

LXML3 = etree.LXML_VERSION[0] >= 3


class RestrictedElement(etree.ElementBase):
    """A restricted Element class that filters out instances of some classes
    """
    __slots__ = ()
    # blacklist = (etree._Entity, etree._ProcessingInstruction, etree._Comment)
    blacklist = etree._Entity

    def _filter(self, iterator):
        blacklist = self.blacklist
        for child in iterator:
            if isinstance(child, blacklist):
                continue
            yield child

    def __iter__(self):
        iterator = super(RestrictedElement, self).__iter__()
        return self._filter(iterator)

    def iterchildren(self, tag=None, reversed=False):
        iterator = super(RestrictedElement, self).iterchildren(tag=tag, reversed=reversed)
        return self._filter(iterator)

    def iter(self, tag=None, *tags):
        iterator = super(RestrictedElement, self).iter(tag=tag, *tags)
        return self._filter(iterator)

    def iterdescendants(self, tag=None, *tags):
        iterator = super(RestrictedElement, self).iterdescendants(tag=tag, *tags)
        return self._filter(iterator)

    def getchildren(self):
        iterator = super(RestrictedElement, self).__iter__()
        return list(self._filter(iterator))


class GlobalParserTLS(threading.local):
    """Thread local context for custom parser instances
    """
    parser_config = {
        'resolve_entities': False,
        #'remove_comments': True,
        #'remove_pis': True,

    }

    element_class = RestrictedElement

    def createDefaultParser(self):
        parser = etree.XMLParser(**self.parser_config)
        if self.element_class is not None:
            lookup = etree.ElementDefaultClassLookup(element=RestrictedElement)
            parser.set_element_class_lookup(lookup)
        return parser

    def setDefaultParser(self, parser):
        self._default_parser = parser

    def getDefaultParser(self):
        parser = getattr(self, "_default_parser", None)
        if parser is None:
            parser = self.createDefaultParser()
            self.setDefaultParser(parser)
        return parser


_parser_tls = GlobalParserTLS()
getDefaultParser = _parser_tls.getDefaultParser


def check_dtd(elementtree, forbid_dtd=False, forbid_entities=True):
    docinfo = elementtree.docinfo
    if docinfo.doctype:
        if forbid_dtd:
            raise DTDForbidden(docinfo.doctype,
                               docinfo.system_url,
                               docinfo.public_id)
        if forbid_entities and not LXML3:
            # lxml < 3 has no iterentities()
            raise NotSupportedError("Unable to check for entites in lxml 2.x")

    if forbid_entities:
        for dtd in docinfo.internalDTD, docinfo.externalDTD:
            if dtd is None:
                continue
            for entity in dtd.iterentities():
                raise EntityForbidden(entity.name)


def parse(source, base_url=None, forbid_dtd=False, forbid_entities=True):
    parser = getDefaultParser()
    elementtree = etree.parse(source, parser, base_url)
    check_dtd(elementtree, forbid_dtd, forbid_entities)
    return elementtree


def fromstring(text, base_url=None, forbid_dtd=False, forbid_entities=True):
    parser = getDefaultParser()
    elementtree = etree.fromstring(text, parser, base_url)
    check_dtd(elementtree, forbid_dtd, forbid_entities)
    return elementtree

XML = fromstring


def iterparse(*args, **kwargs):
    raise NotSupportedError("defused interparse not available")
