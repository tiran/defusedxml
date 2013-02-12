==========
defusedxml
==========

The `defusedxml package`_ contains several Python-only workarounds and fixes
for denial of service vulnerabilities in Python's XML libraries. The
`defusedexpat package`_ comes with binary extensions and a `modified expat`_
libary instead of the standard `expat parser`_.


.. contents:: Table of Contents
   :depth: 2


Attack vectors
==============

The results of an attack on vulnerable XML library can be fairly dramatic.
With just a few hundred Bytes of XML data an attacker can occupy several
**Gigabyte** of memory within **seconds**. An attacker can also keep
CPUs busy for a long time with small to medium size request. Under some
conditions circumstances it is even possible to access local files on your
server, to circumvent firewall or to abuse services to rebound attacks to
third parties.

The attacks use and abuse less common features of XML and XML parsers. The
majority of developers are unacquainted with features such as processing
instructions and entity expansions that XML inherited from SGML. At best
they know about ``<!DOCTYPE>`` from experience with HTML but they are not
aware that a document type definition (DTD) can generate a HTTP request
or load a file from the file system.


billion laughs / exponential entity expansion
---------------------------------------------

`Billion Laughs`_

::

    <!DOCTYPE xmlbomb [
    <!ENTITY a "1234567890" >
    <!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;">
    <!ENTITY c "&b;&b;&b;&b;&b;&b;&b;&b;">
    <!ENTITY d "&c;&c;&c;&c;&c;&c;&c;&c;">
    ]>
    <bomb>&c;</bomb>


quadratic blowup entity expansion
---------------------------------

`XML DoS and Defenses (MSDN)`_

::

    <!DOCTYPE bomb [
    <!ENTITY a "xxxxxxx... repeat">
    ]>
    <bomb>&a;&a;&a;... repeat</bomb>


external entity expansion (remote)
----------------------------------

::

    <!DOCTYPE external [
    <!ENTITY ee SYSTEM "http://www.python.org/">
    ]>
    <root>&ee;</root>


external entity expansion (local file)
--------------------------------------

::

    <!DOCTYPE external [
    <!ENTITY ee SYSTEM "file:///PATH/TO/simple.xml">
    ]>
    <root>&ee;</root>

DTD external fetch
------------------

::

    <?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html>
        <head/>
        <body>text</body>
    </html>


decompression bomb
------------------

`ZIP bomb`_


Library overview
================

.. csv-table::
   :header: "kind", "sax", "etree", "minidom", "pulldom", "lxml", "libxml2 python"
   :widths: 20, 10, 10, 15, 10, 10, 13

   "billion laughs", "True", "True", "True", "True", "False (1)", "untested"
   "quadratic blowup", "True", "True", "True", "True", "True", "untested"
   "external entity expansion (remote)", "True", "False (error)", "False (ignore)", "True", "False (1)", "untested"
   "external entity expansion (local file)", "True", "False (error)", "False (ignore)", "True", "True", "untested"
   "DTD external fetch", "True", "False", "False", "True", "False (1)", "untested"
   "gzip bomb", "False", "False", "False", "False", "partly (2)", "untested"
   "xpath", "False", "False", "False", "False", "True", "untested"
   "xslt", "False", "False", "False", "False", "True", "unknown"
   "C library", "expat", "expat", "expat", "expat", "libxml2", "libxml2"
   "handler", "expatreader", "XMLParser", "expatbuilder / pulldom", "sax", "", ""

1. Lxml is protected against billion laughs attacks and doesn't do network
   lookups by default.
2. libxml2 and lxml are not directly vulnerable to gzip decompression bombs
   but they don't protect you against them either.


Other things to consider
========================

Best practices
--------------

* Don't allow DTDs
* Don't expand entities
* Don't resolve externals
* Limit parse depth
* Limit total input size
* Don't use XPath expression from untrusted sources
* Don't use XSLT code from untrusted sources

(based on Brad Hill's `Attacking XML Security`_)


Processing Instruction
----------------------

`PI`_'s like::

  <?xml-stylesheet type="text/xsl" href="style.xsl"?>

may impose more threats for XML processing.


Other DTD features
------------------

`DTD`_ has more features like ``<!NOTATION>``. I haven't researched how
these features may be a security threat.


XPath
-----

XPath statements may introduce DoS vulnerabilities.


XSL Transformation
------------------

You should keep in mind that XSLT is a Turing complete language. Never
process XSLT code from unknown or untrusted source. XSLT processors may
allow you to interact with external resources in ways you can't even imagine.

Example from `Attacking XML Security`_ for Xalan-J::

    <xsl:stylesheet version="1.0"
     xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
     xmlns:rt="http://xml.apache.org/xalan/java/java.lang.Runtime"
     xmlns:ob="http://xml.apache.org/xalan/java/java.lang.Object"
     exclude-result-prefixes= "rt,ob">
     <xsl:template match="/">
       <xsl:variable name="runtimeObject" select="rt:getRuntime()"/>
       <xsl:variable name="command"
         select="rt:exec($runtimeObject, &apos;c:\Windows\system32\cmd.exe&apos;)"/>
       <xsl:variable name="commandAsString" select="ob:toString($command)"/>
       <xsl:value-of select="$commandAsString"/>
     </xsl:template>
    </xsl:stylesheet>



TODO
====

 * DOM: Use xml.dom.xmlbuilder options for entity handling
 * SAX: take feature_external_ges and feature_external_pes (?) into account
 * implement monkey patching of stdlib modules
 * test lxml default element class overwrite
 * document which module / library is vulnerable to which kind of attack
 * handle iterparse on Python 2.6
 * documentation, documentation, documentation ...


License
=======

Copyright (c) 2013 by Christian Heimes <christian@python.org>

Licensed to PSF under a Contributor Agreement.

See http://www.python.org/psf/license for licensing details.


Contributors
============

Brett Cannon <brett@python.org>
  review and code cleanup


.. _defusedxml package: https://bitbucket.org/tiran/defusedxml
.. _defusedexpat package: https://bitbucket.org/tiran/defusedexpat
.. _modified expat: https://bitbucket.org/tiran/expat
.. _expat parser: http://expat.sourceforge.net/
.. _Attacking XML Security: https://www.isecpartners.com/media/12976/iSEC-HILL-Attacking-XML-Security-bh07.pdf
.. _Billion Laughs: http://en.wikipedia.org/wiki/Billion_laughs
.. _XML DoS and Defenses (MSDN): http://msdn.microsoft.com/en-us/magazine/ee335713.aspx
.. _ZIP bomb: http://en.wikipedia.org/wiki/Zip_bomb
.. _DTD: http://en.wikipedia.org/wiki/Document_Type_Definition
.. _PI: https://en.wikipedia.org/wiki/Processing_Instruction

