==========
defusedxml
==========

The `defusedxml package`_ contains several Python-only workarounds and fixes
for denial of service vulnerabilities in Python's XML libraries. The
`defusedexpat package`_ comes with binary extensions and a `modified expat`_
libary instead of the standard `expat parser`_.


.. contents:: Table of Contents
   :depth: 2

Synopsis
========

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

The issues are known for a long time -- billion laughs was first reported in
2003. Nevertheless some XML libraries are still vulnerable and even heavy
users of XML are surprised by these features.


Attack vectors
==============

billion laughs / exponential entity expansion
---------------------------------------------

A `Billion Laughs`_ attacks -- also known as exponential entity expansion --
uses multiple levels of nested entities. The original example uses 9 levels
of 10 expansions each to expand the string ``lol`` to a string of
3 * 10 :sup:`9` Bytes, hence the name billion laughs. The resulting string
occupies 3 GB (2.79 GiB) memory, intermediate strings require additional
memory. Because most parsers don't cache intermediate step every
expansion is repeated over and over again. It increases the CPU load even
more.

Example XML::

    <!DOCTYPE xmlbomb [
    <!ENTITY a "1234567890" >
    <!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;">
    <!ENTITY c "&b;&b;&b;&b;&b;&b;&b;&b;">
    <!ENTITY d "&c;&c;&c;&c;&c;&c;&c;&c;">
    ]>
    <bomb>&d;</bomb>


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


attribute blowup
----------------

A XML parsers may use a algorithm with quadratic runtime O(n :sup:`2`) to
handle attributes and namespaces. If it uses hash maps (dictionaries) to
store attributes and namespaces the implementation may be vulnerable to
hash collision attacks, thus reducing the performance to O(n :sup:`2`) again.
In either case an attacker is able to forge a denial of service attack with
a XML document that contains thousands upon thousands of attributes in
a single node.

I haven't researched yet if expat, pyexpat or libxml2 are vulnerable.


decompression bomb
------------------

`ZIP bomb`_


Library overview
================

.. csv-table::
   :header: "kind", "sax", "etree", "minidom", "pulldom", "lxml", "libxml2 python"
   :widths: 25, 10, 10, 10, 10, 10, 13

   "billion laughs", "True", "True", "True", "True", "False (1)", "untested"
   "quadratic blowup", "True", "True", "True", "True", "True", "untested"
   "external entity expansion (remote)", "True", "False (3)", "False (4)", "True", "False (1)", "untested"
   "external entity expansion (local file)", "True", "False (3)", "False (4)", "True", "True", "untested"
   "DTD external fetch", "True", "False", "False", "True", "False (1)", "untested"
   "attribute blowup", "unknown", "unknown", "unknown", "unknown", "unknown", "untested"
   "gzip bomb", "False", "False", "False", "False", "partly (2)", "untested"
   "xpath", "False", "False", "False", "False", "True", "untested"
   "xslt", "False", "False", "False", "False", "True", "untested"
   "C library", "expat", "expat", "expat", "expat", "libxml2", "libxml2"

1. Lxml is protected against billion laughs attacks and doesn't do network
   lookups by default.
2. libxml2 and lxml are not directly vulnerable to gzip decompression bombs
   but they don't protect you against them either.
3. xml.etree doesn't expand entities and raises a ParserError when an entity
   occurs.
4. minidom doesn't expand entities and simply returns the unexpanded entity
   verbatim.


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
* document which module / library is vulnerable to which kind of attack
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

s<e>mantics GmbH (http://www.semantics.de)
   I like to thank my employer s<e>mantics for
   letting me work on the issue during working hours as part of Semantics's
   open source initiative.


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

