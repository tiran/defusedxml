# defusedxml
#
# Copyright (c) 2013 by Christian Heimes <christian@python.org>
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license for licensing details.
"""Defused xmlrpclib

Also defuses gzip bomb
"""
from __future__ import print_function, absolute_import
from .common import PY3

if PY3:
    __origin__ = "xmlrpc.client"
    from xmlrpc import client as xmlrpc
    from xmlrpc import server as xmlrpc_server
else:
    __origin__ = "xmlrpclib"
    import xmlrpclib as xmlrpc
    xmlrpc_server = None

