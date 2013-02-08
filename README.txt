==========
defusedxml
==========

defuxedxml contains various workarounds and fixes for denial of service
attacks on Python's XML parsers.


Attack vectors
==============

billion laughs / exponential entity expansion
---------------------------------------------

`Billion Laughs`_

.. include:: xmltestdata/xmlbomb.xml
   :literal:


quadratic blowup entity expansion
---------------------------------

`XML DoS and Defenses (MSDN)`_

::

    <!DOCTYPE bomb [
    <!ENTITY a "xxxxxxx... repeat">
    ]>
    <bomb>&a;&a;&a;... repeat</bomb>


external entity expansion
-------------------------

.. include:: xmltestdata/external.xml
   :literal:


DTD external fetch
------------------

.. include:: xmltestdata/dtd.xml
   :literal:


decompression bomb
------------------

`ZIP bomb`_


Overview
--------

.. csv-table::
   :header: "kind", "sax", "etree", "minidom", "pulldom", "lxml", "libxml2 python"
   :widths: 15, 10, 10, 15, 10, 10, 13

   "billion laughs", "True", "True", "True", "True", "False ¹", "untested"
   "quadratic blowup", "True", "True", "True", "True", "True", "untested"
   "external entity expansion", "True", "False", "True", "True", "False ¹", "untested"
   "DTD external fetch", "True", "False", "False", "True", "False ¹", "untested"
   "gzip bomb", "False", "False", "False", "False", "partly ²", "untested"
   "xpath", "False", "False", "False", "False", "True", "untested"
   "xslt", "False", "False", "False", "False", "True", "unknown"
   "C library", "expat", "expat", "expat", "expat", "libxml2", "libxml2"
   "handler", "expatreader", "XMLParser", "expatbuilder / pulldom", "sax", "", ""

1) Lxml is protected against billion laughs attacks and doesn't do network
lookups by default.
2) libxml2 and lxml are not directly vulnerable to gzip decompression bombs
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


.. _Attacking XML Security: https://www.isecpartners.com/media/12976/iSEC-HILL-Attacking-XML-Security-bh07.pdf
.. _Billion Laughs: http://en.wikipedia.org/wiki/Billion_laughs
.. _XML DoS and Defenses (MSDN): http://msdn.microsoft.com/en-us/magazine/ee335713.aspx
.. _ZIP bomb: http://en.wikipedia.org/wiki/Zip_bomb
.. _DTD: http://en.wikipedia.org/wiki/Document_Type_Definition
.. _PI: https://en.wikipedia.org/wiki/Processing_Instruction


Author
======

Christian Heimes <christian@python.org>

