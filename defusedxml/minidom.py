# defusedxml
#
# Copyright (c) 2013 by Christian Heimes <christian@python.org>
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license for licensing details.

from xml.dom.minidom import _do_pulldom_parse

__origin__ = "xml.dom.minidom"

def parse(file, parser=None, bufsize=None):
    """Parse a file into a DOM by filename or file object."""
    if parser is None and not bufsize:
        from . import expatbuilder
        return expatbuilder.parse(file)
    else:
        from . import pulldom
        return _do_pulldom_parse(pulldom.parse, (file,),
            {'parser': parser, 'bufsize': bufsize})

def parseString(string, parser=None):
    """Parse a file into a DOM from a string."""
    if parser is None:
        from xml.dom import expatbuilder
        return expatbuilder.parseString(string)
    else:
        from . import pulldom
        return _do_pulldom_parse(pulldom.parseString, (string,),
                                 {'parser': parser})
