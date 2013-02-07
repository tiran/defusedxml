# defusedxml
#
# Copyright (c) 2013 by Christian Heimes <christian@python.org>
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license for licensing details.
"""Defused xml.sax
"""

from xml.sax import InputSource as _InputSource
from xml.sax import ErrorHandler as _ErrorHandler

from . import expatreader

__origin__ = "xml.sax"

def parse(source, handler, errorHandler=_ErrorHandler()):
    parser = make_parser()
    parser.setContentHandler(handler)
    parser.setErrorHandler(errorHandler)
    parser.parse(source)


def parseString(string, handler, errorHandler=_ErrorHandler()):
    from io import BytesIO

    if errorHandler is None:
        errorHandler = _ErrorHandler()
    parser = make_parser()
    parser.setContentHandler(handler)
    parser.setErrorHandler(errorHandler)

    inpsrc = _InputSource()
    inpsrc.setByteStream(BytesIO(string))
    parser.parse(inpsrc)

def make_parser():
    return expatreader.create_parser()
