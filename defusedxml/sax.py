# defusedxml
#
# Copyright (c) 2013 by Christian Heimes <christian@python.org>
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license for licensing details.
"""Defused xml.sax
"""

from xml import sax
from xml.sax.xmlreader import InputSource
from xml.sax.handler import ErrorHandler

from . import expatreader
from .common import _wire_module

def parse(source, handler, errorHandler=ErrorHandler()):
    parser = make_parser()
    parser.setContentHandler(handler)
    parser.setErrorHandler(errorHandler)
    parser.parse(source)


def parseString(string, handler, errorHandler=ErrorHandler()):
    from io import BytesIO

    if errorHandler is None:
        errorHandler = ErrorHandler()
    parser = make_parser()
    parser.setContentHandler(handler)
    parser.setErrorHandler(errorHandler)

    inpsrc = InputSource()
    inpsrc.setByteStream(BytesIO(string))
    parser.parse(inpsrc)

def make_parser():
    return expatreader.create_parser()


_wire_module(sax, __name__)
