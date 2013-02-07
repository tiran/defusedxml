# defusedxml
#
# Copyright (c) 2013 by Christian Heimes <christian@python.org>
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license for licensing details.

class DefusedXmlException(ValueError):
    pass


class DTDForbidden(DefusedXmlException):
    pass


class EntityForbidden(DefusedXmlException):
    pass

class NotSupportedError(DefusedXmlException):
    pass
