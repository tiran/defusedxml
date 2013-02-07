# defusedxml
#
# Copyright (c) 2013 by Christian Heimes <christian@python.org>
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license for licensing details.

from xml.dom import minidom
from .common import _wire_module

def parse(file, bufsize=None):
    pass

def parseString(string, parser=None):
    pass


_wire_module(minidom, __name__)
