# defusedxml
#
# Copyright (c) 2013 by Christian Heimes <christian@python.org>
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license for licensing details.
"""Defused xml.sax
"""

from xml.sax.xmlreader import InputSource
from xml.sax.handler import ContentHandler, ErrorHandler
from xml.sax._exceptions import SAXException, SAXNotRecognizedException, \
                                SAXParseException, SAXNotSupportedException, \
                                SAXReaderNotAvailable
from . import expatreader

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
