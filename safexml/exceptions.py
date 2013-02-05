# safexml
#
# Copyright (c) 2013 by Christian Heimes <christian@cheimes.de>
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license for licensing details.

class SafeXmlException(ValueError):
    pass


class DTDForbidden(SafeXmlException):
    pass


class EntityForbidden(SafeXmlException):
    pass
