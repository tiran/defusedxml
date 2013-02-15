===================================================
defusedxml -- defusing XML bombs and other exploits
===================================================

    "It's just XML, what could probably go wrong?"


.. contents:: Table of Contents
   :depth: 2

Synopsis
========

The results of an attack on a vulnerable XML library can be fairly dramatic.
With just a few hundred bytes of XML data an attacker can occupy several
**gigabytes** of memory within **seconds**. An attacker can also keep
CPUs busy for a long time with a small to medium size request. Under some
circumstances it is even possible to access local files on your
server, to circumvent a firewall, or to abuse services to rebound attacks to
third parties.

The attacks use and abuse less common features of XML and its parsers. The
majority of developers are unacquainted with features such as processing
instructions and entity expansions that XML inherited from SGML. At best
they know about ``<!DOCTYPE>`` from experience with HTML but they are not
aware that a document type definition (DTD) can generate an HTTP request
or load a file from the file system.

None of the issues is new. They have been known for a long time. Billion
laughs was first reported in 2003. Nevertheless some XML libraries and
applications are still vulnerable and even heavy users of XML are
surprised by these features. It's hard to say whom to blame for the
situation. It's too short sighted to shift all blame on XML parsers and
XML libraries for using insecure default settings. After all they
properly implement XML specifications. Application developers must not rely
that a library is always configured for security and potential harmful data
by default.


Attack vectors
==============

billion laughs / exponential entity expansion
---------------------------------------------

The `Billion Laughs`_ attack -- also known as exponential entity expansion --
uses multiple levels of nested entities. The original example uses 9 levels
of 10 expansions in each level to expand the string ``lol`` to a string of
3 * 10 :sup:`9` bytes, hence the name "billion laughs". The resulting string
occupies 3 GB (2.79 GiB) of memory; intermediate strings require additional
memory. Because most parsers don't cache the intermediate step for every
expansion it is repeated over and over again. It increases the CPU load even
more.

An XML document of just a few hundred bytes can disrupt all services on a
machine within seconds.

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

A quadratic blowup attack is similar to a `Billion Laughs`_ attack; it abuses
entity expansion, too. Instead of nested entities it repeats one large entity
with a couple of ten thousand chars over and over again. The attack isn't as
efficient as the exponential case but it avoids triggering countermeasures of
parsers against heavily nested entities. Some parsers limit the depth and
breadth of a single entity but not the total amount of expanded text
throughout an entire XML document.

A medium-sized XML document with a couple of hundred kilobytes can require a
couple of hundred MB to several GB of memory. When the attack is combined
with some level of nested expansion an attacker is able to achieve a higher
ratio of success.

::

    <!DOCTYPE bomb [
    <!ENTITY a "xxxxxxx... a couple of ten thousand chars">
    ]>
    <bomb>&a;&a;&a;... repeat</bomb>


external entity expansion (remote)
----------------------------------

Entity declarations can contain more than just text for replacement. They can
also point to external resources by public identifiers or system identifiers.
System identifiers are standard URIs. When the URI is a URL (e.g. a
``http://`` locator) some parsers download the resource from the remote
location and embed them into the XML document verbatim.

Simple example of a parsed external entity::

    <!DOCTYPE external [
    <!ENTITY ee SYSTEM "http://www.python.org/some.xml">
    ]>
    <root>&ee;</root>

The case of parsed external entities works only for valid XML content. The
XML standard also supports unparsed external entities with a
``NData declaration``.

External entity expansion opens the door to plenty of exploits. An attacker
can abuse a vulnerable XML library and application to rebound and forward
network requests with the IP address of the server. It highly depends
on the parser and the application what kind of exploit is possible. For
example:

* An attacker can circumvent firewalls and gain access to restricted
  resources as all the requests are made from an internal and trustworthy
  IP address, not from the outside.
* An attacker can abuse a service to attack, spy on or DoS your servers but
  also third party services. The attack is disguised with the IP address of
  the server and the attacker is able to utilize the high bandwidth of a big
  machine.
* An attacker can exhaust additional resources on the machine, e.g. with
  requests to a service that doesn't respond or responds with very large
  files.
* An attacker may gain knowledge, when, how often and from which IP address
  a XML document is accessed.
* An attacker could send mail from inside your network if the URL handler
  supports ``smtp://`` URIs.


external entity expansion (local file)
--------------------------------------

External entities with references to local files are a sub-case of external
entity expansion. It's listed as an extra attack because it deserves extra
attention. Some XML libraries such as lxml disable network access by default
but still allow entity expansion with local file access by default. Local
files are either referenced with a ``file://`` URL or by a file path (either
relative or absolute).

An attacker may be able to access and download all files that can be read by
the application process. This may include critical configuration files, too.

::

    <!DOCTYPE external [
    <!ENTITY ee SYSTEM "file:///PATH/TO/simple.xml">
    ]>
    <root>&ee;</root>


DTD retrieval
-------------

This case is similar to external entity expansion, too. Some XML libraries
like Python's xml.dom.pulldown retrieve document type definitions from remote
or local locations. Several attack scenarios from the external entity case
apply to this issue as well.

::

    <?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html>
        <head/>
        <body>text</body>
    </html>


Python XML Libraries
====================

.. csv-table::
   :header: "kind", "sax", "etree", "minidom", "pulldom", "lxml", "genshi"
   :widths: 24, 8, 8, 8, 8, 8, 8

   "billion laughs", "True", "True", "True", "True", "False (1)", "False (5)"
   "quadratic blowup", "True", "True", "True", "True", "True", "False (5)"
   "external entity expansion (remote)", "True", "False (3)", "False (4)", "True", "False (1)", "False (5)"
   "external entity expansion (local file)", "True", "False (3)", "False (4)", "True", "True", "False (5)"
   "DTD retrieval", "True", "False", "False", "True", "False (1)", "False"
   "gzip bomb", "False", "False", "False", "False", "partly (2)", "False"
   "xpath support", "False", "False", "False", "False", "True", "False"
   "xsl(t) support", "False", "False", "False", "False", "True", "False"
   "xinclude support", "False", "True (6)", "False", "False", "True (6)", "True"
   "C library", "expat", "expat", "expat", "expat", "libxml2", "expat"

1. Lxml is protected against billion laughs attacks and doesn't do network
   lookups by default.
2. libxml2 and lxml are not directly vulnerable to gzip decompression bombs
   but they don't protect you against them either.
3. xml.etree doesn't expand entities and raises a ParserError when an entity
   occurs.
4. minidom doesn't expand entities and simply returns the unexpanded entity
   verbatim.
5. genshi.input of genshi 0.6 doesn't support entity expansion and raises a
   ParserError when an entity occurs.
6. Library has (limited) XInclude support but requires an additional step to
   process inclusion.


CVE
===

CVE-2013-1664:
  Unrestricted entity expansion induces DoS vulnerabilities in Python XML
  libraries (XML bomb)

CVE-2013-1665:
  External entity expansion in Python XML libraries inflicts potential
  security flaws and DoS vulnerabilities


defusedxml
==========

The `defusedxml package`_ contains several Python-only workarounds and fixes
for denial of service and other vulnerabilities in Python's XML libraries.

All functions and parser classes accept two additional keyword arguments.

forbid_dtd (default: False)
  disallow XML with a ``<!DOCTYPE>`` processing instruction and raise a
  DTDForbidden exception

forbid_entities (default: True)
  disallow XML with ``<!ENTITY>`` declarations inside the DTD and raise a
  EntitiesForbidden exception

All parsers also enforce a hard ban of external entities and retrieval of
external DTDs by raising an ExternalReferenceForbidden exception.


defused.cElementTree
--------------------

parse(), iterparse(), fromstring(), XMLParser


defused.ElementTree
--------------------

parse(), iterparse(), fromstring(), XMLParser


defused.expatreader
-------------------

create_parser(), DefusedExpatParser


defused.sax
-----------

parse(), parseString(), create_parser()


defused.expatbuilder
--------------------

parse(), parseString(), DefusedExpatBuilder, DefusedExpatBuilderNS

defused.minidom
---------------

parse(), parseString()

defused.pulldom
---------------

parse(), parseString()

defused.lxml
------------

parse(), fromstring()

RestrictedElement, GlobalParserTLS, getDefaultParser, check_docinfo()


defusedexpat
============

The `defusedexpat package`_ comes with binary extensions and a `modified expat`_
libary instead of the standard `expat parser`_. It's basically a stand-alone
version of the patches for Python's standard library C extensions.


How to avoid XML vulnerabilities
================================

Best practices
--------------

* Don't allow DTDs
* Don't expand entities
* Don't resolve externals
* Limit parse depth
* Limit total input size
* Don't use XPath expression from untrusted sources
* Don't apply XSL transformations that come untrusted sources
* Always validate and properly quote arguments to XSL transformations and
  XPath queries

(based on Brad Hill's `Attacking XML Security`_)


Other things to consider
========================

XML, XML parsers and processing libraries have more features and possible
issue that can lead to DoS vulnerabilities or security exploits in
applications. I have compiled an incomplete list of possible issues that
need further research and more attention.


attribute blowup
----------------

XML parsers may use an algorithm with quadratic runtime O(n :sup:`2`) to
handle attributes and namespaces. If it uses hash tables (dictionaries) to
store attributes and namespaces the implementation may be vulnerable to
hash collision attacks, thus reducing the performance to O(n :sup:`2`) again.
In either case an attacker is able to forge a denial of service attack with
an XML document that contains thousands upon thousands of attributes in
a single node.

I haven't researched yet if expat, pyexpat or libxml2 are vulnerable.


decompression bomb
------------------

The issue of decompression bombs (aka `ZIP bomb`_) apply to all XML libraries
that can parse compressed XML stream like gzipped HTTP streams or LZMA-ed
files. For an attacker it can reduce the amount of transmitted data by three
magnitudes or more. Gzip is able to compress 1 GiB zeros to roughly 1 MB,
lzma is even better::

    $ dd if=/dev/zero bs=1M count=1024 | gzip > zeros.gz
    $ dd if=/dev/zero bs=1M count=1024 | lzma -z > zeros.xy
    $ ls -sh zeros.*
    1020K zeros.gz
     148K zeros.xy

None of Python's standard XML libraries decompresses streams except of
``xmlrpclib`` and that is vulnerable <http://bugs.python.org/issue16043>
to decompression bombs.

lxml can load and process compressed data through libxml2 transparently.
libxml2 can handle even very large blobs of compressed data efficiently
without using too much memory. But it doesn't protect applications from
decompression bombs. A carefully written SAX or iterparse-like approach can
be safe.


Processing Instruction
----------------------

`PI`_'s like::

  <?xml-stylesheet type="text/xsl" href="style.xsl"?>

may impose more threats for XML processing. It depends if and how a
processor handles processing instructions. The issue of URL retrieval with
network or local file access apply to processing instructions, too.


Other DTD features
------------------

`DTD`_ has more features like ``<!NOTATION>``. I haven't researched how
these features may be a security threat.


XPath
-----

XPath statements may introduce DoS vulnerabilities. Code should never execute
queries from untrusted sources. An attacker may also be able to create a XML
document that makes certain XPath queries costly or resource hungry.


XPath injection attacks
-----------------------

XPath injeciton attacks pretty much work like SQL injection attacks.
Arguments to XPath queries must be quoted and validated properly, especially
when they are taken from the user. The page `Avoid the dangers of XPath injection`_
list some ramifications of XPath injections.

Python's standard library doesn't have XPath support. Lxml supports
parameterized XPath queries which does proper quoting. You just have to use
its xpath() method correctly::

   # DON'T
   >>> tree.xpath("/tag[@id='%s']" % value)

   # instead do
   >>> tree.xpath("/tag[@id=$tagid]", tagid=name)


XInclude
--------

`XML Inclusion`_ is another way to load and include external files::

   <root xmlns:xi="http://www.w3.org/2001/XInclude">
     <xi:include href="filename.txt" parse="text" />
   </root>

This feature should be disabled when XML files from an untrusted source are
processed. Some Python XML libraries and libxml2 support XInclude but don't
have an option to sandbox inclusion and limit it to allowed directories.


XSL Transformation
------------------

You should keep in mind that XSLT is a Turing complete language. Never
process XSLT code from unknown or untrusted source! XSLT processors may
allow you to interact with external resources in ways you can't even imagine.
Some processors even support extensions that allow read/write access to file
system, access to JRE objects or scripting with Jython.

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


Other languages / frameworks
=============================

Several other programming languages and frameworks are vulnerable as well. A
couple of them are affected by the fact that libxml2 up to 2.9.0 has no
protection against quadratic blowup attacks. Most of them have potential
dangerous default settings for entity expansion and external entities, too.

Perl
----

Perl's XML::Simple is vulnerable to quadratic entity expansion and external
entity expansion (both local and remote).


Ruby
----

Ruby's REXML document parser is vulnerable to entity expansion attacks
(both quadratic and exponential) but it doesn't do external entity
expansion by default. In order to counteract entity expansion you have to
disable the feature::

  REXML::Document.entity_expansion_limit = 0

libxml-ruby and hpricot don't expand entities in their default configuration.


PHP
---

PHP's SimpleXML API is vulnerable to quadratic entity expansion and loads
entites from local and remote resources. The option ``LIBXML_NONET`` disables
network access but still allows local file access. ``LIBXML_NOENT`` seems to
have no effect on entity expansion in PHP 5.4.6.


C# / .NET / Mono
----------------

Untested. Information in `XML DoS and Defenses (MSDN)`_ suggest that .NET is
vulnerable with its default settings.


Java
----

Untested. The documentation of Xerces and its `Xerces SecurityMananger`_
sounds like Xerces is also vulnerable to billion laugh attacks with its
default settings. It also does entity resolving when an
``org.xml.sax.EntityResolver`` is configured. I'm not yet sure about the
default setting here.


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


Acknowledgements
================

Brett Cannon (Python Core developer)
  review and code cleanup

Antoine Pitrou (Python Core developer)
  code review

Aaron Patterson, Ben Murphy and Michael Koziarski (Ruby community)
  Many thanks to Aaron, Ben and Michael from the Ruby community for their
  report and assistance.

Thierry Carrez (OpenStack)
  Many thanks to Thierry for his report to the Python Security Response
  Team on behalf of the OpenStack security team.

Carl Meyer (Django)
  Many thanks to Carl for his report to PSRT on behalf of the Django security
  team.

Daniel Veillard (libxml2)
  Many thanks to Daniel for his insight and assistance with libxml2.

semantics GmbH (http://www.semantics.de/)
  Many thanks to my employer semantics for letting me work on the issue
  during working hours as part of semantics's open source initiative.


References
==========

* `XML DoS and Defenses (MSDN)`_
* `Billion Laughs`_ on Wikipedia
* `ZIP bomb`_ on Wikipedia

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
.. _Avoid the dangers of XPath injection: http://www.ibm.com/developerworks/xml/library/x-xpathinjection/index.html
.. _Xerces SecurityMananger: http://xerces.apache.org/xerces2-j/javadocs/xerces2/org/apache/xerces/util/SecurityManager.html
.. _XML Inclusion: http://www.w3.org/TR/xinclude/#include_element
