# defusedxml
#
# Copyright (c) 2013 by Christian Heimes <christian@python.org>
# Licensed to PSF under a Contributor Agreement.
# See https://www.python.org/psf/license for licensing details.
"""Defused xml.etree.cElementTree
"""
import warnings

# This module is an alias for ElementTree just like xml.etree.cElementTree
from .ElementTree import (
    XML,
    XMLParse,
    XMLParser,
    XMLTreeBuilder,
    fromstring,
    iterparse,
    parse,
    tostring,
    DefusedXMLParser,
)

__origin__ = "xml.etree.cElementTree"


warnings.warn(
    "defusedxml.cElementTree is deprecated, import from defusedxml.ElementTree instead.",
    category=DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "XML",
    "XMLParse",
    "XMLParser",
    "XMLTreeBuilder",
    "fromstring",
    "iterparse",
    "parse",
    "tostring",
    # backwards compatibility
    "DefusedXMLParser",
]
