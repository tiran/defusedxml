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


class EntityForbidden(DefusedXmlException):
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
