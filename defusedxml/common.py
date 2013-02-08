# defusedxml
#
# Copyright (c) 2013 by Christian Heimes <christian@python.org>
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license for licensing details.

import sys

PY3 = sys.version_info[0] == 3
PY26 = sys.version_info[:2] == (2, 6)


class DefusedXmlException(ValueError):
    pass


class DTDForbidden(DefusedXmlException):
    pass


class EntitiesForbidden(DefusedXmlException):
    pass


class ExternalEntitiesForbidden(DefusedXmlException):
    pass


class NotSupportedError(DefusedXmlException):
    pass


def _wire_module(srcmod, dstmodname):
    assert srcmod is sys.modules[srcmod.__name__]
    dstmod = sys.modules[dstmodname]
    names = getattr(srcmod, "__all__", None)
    if not names:
        names = tuple(name for name in dir(srcmod)
                      if not name.startswith("_"))
    for name in names:
        if hasattr(dstmod, name):
            continue
        value = getattr(srcmod, name)
        setattr(dstmod, name, value)


def _generate_etree_functions(DefusedXMLParser, _TreeBuilder,
            _IterParseIterator, _parse, _iterparse):
    """Factory for functions needed by etree, dependent on whether
    cElementTree or ElementTree is used."""

    def parse(source, parser=None, forbid_dtd=False, forbid_entities=True):
        if parser is None:
            parser = DefusedXMLParser(target=_TreeBuilder(),
                                      forbid_dtd=forbid_dtd,
                                      forbid_entities=forbid_entities)
        return _parse(source, parser)

    def iterparse(source, events=None, parser=None, forbid_dtd=False,
                forbid_entities=True):
        if PY3:
            close_source = False
            if not hasattr(source, "read"):
                source = open(source, "rb")
                close_source = True
            if not parser:
                parser = DefusedXMLParser(target=_TreeBuilder())
            return _IterParseIterator(source, events, parser, close_source)
        else:
            if parser is None:
                parser = DefusedXMLParser(target=_TreeBuilder())
            return _iterparse(source, events, parser)

    def fromstring(text, forbid_dtd=False, forbid_entities=True):
        parser = DefusedXMLParser(target=_TreeBuilder(),
                                  forbid_dtd=forbid_dtd,
                                  forbid_entities=forbid_entities)
        parser.feed(text)
        return parser.close()

    return parse, iterparse, fromstring
