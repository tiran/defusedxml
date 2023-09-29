# defusedxml -- defusing XML bombs and other exploits
[![Latest Version](https://img.shields.io/pypi/v/defusedxml.svg)](https://pypi.org/project/defusedxml/)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/defusedxml.svg)](https://pypi.org/project/defusedxml/)
[![Travis CI](https://travis-ci.org/tiran/defusedxml.svg?branch=master)](https://travis-ci.org/tiran/defusedxml)
[![codecov](https://codecov.io/github/tiran/defusedxml/coverage.svg?branch=master)](https://codecov.io/github/tiran/defusedxml?branch=master)
[![PyPI downloads](https://img.shields.io/pypi/dm/defusedxml.svg)](https://pypistats.org/packages/defusedxml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> "It's just XML, what could probably go wrong?"

Christian Heimes \<<christian@python.org>\>

## Synopsis

The results of an attack on a vulnerable XML library can be fairly
dramatic. With just a few hundred **Bytes** of XML data an attacker can
occupy several **Gigabytes** of memory within **seconds**. An attacker
can also keep CPUs busy for a long time with a small to medium size
request. Under some circumstances it is even possible to access local
files on your server, to circumvent a firewall, or to abuse services to
rebound attacks to third parties.

The attacks use and abuse less common features of XML and its parsers.
The majority of developers are unacquainted with features such as
processing instructions and entity expansions that XML inherited from
SGML. At best they know about `<!DOCTYPE>` from experience with HTML but
they are not aware that a document type definition (DTD) can generate an
HTTP request or load a file from the file system.

None of the issues is new. They have been known for a long time. Billion
laughs was first reported in 2003. Nevertheless some XML libraries and
applications are still vulnerable and even heavy users of XML are
surprised by these features. It's hard to say whom to blame for the
situation. It's too short sighted to shift all blame on XML parsers and
XML libraries for using insecure default settings. After all they
properly implement XML specifications. Application developers must not
rely that a library is always configured for security and potential
harmful data by default.

<div class="contents" depth="2">

Table of Contents

</div>

## Attack vectors

### billion laughs / exponential entity expansion

The [Billion Laughs](https://en.wikipedia.org/wiki/Billion_laughs)
attack -- also known as exponential entity expansion --uses multiple
levels of nested entities. The original example uses 9 levels of 10
expansions in each level to expand the string `lol` to a string of 3 \*
10 <sup>9</sup> bytes, hence the name "billion laughs". The resulting
string occupies 3 GB (2.79 GiB) of memory; intermediate strings require
additional memory. Because most parsers don't cache the intermediate
step for every expansion it is repeated over and over again. It
increases the CPU load even more.

An XML document of just a few hundred bytes can disrupt all services on
a machine within seconds.

Example XML:

    <!DOCTYPE xmlbomb [
    <!ENTITY a "1234567890" >
    <!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;">
    <!ENTITY c "&b;&b;&b;&b;&b;&b;&b;&b;">
    <!ENTITY d "&c;&c;&c;&c;&c;&c;&c;&c;">
    ]>
    <bomb>&d;</bomb>

### quadratic blowup entity expansion

A quadratic blowup attack is similar to a [Billion
Laughs](https://en.wikipedia.org/wiki/Billion_laughs) attack; it abuses
entity expansion, too. Instead of nested entities it repeats one large
entity with a couple of thousand chars over and over again. The attack
isn't as efficient as the exponential case but it avoids triggering
countermeasures of parsers against heavily nested entities. Some parsers
limit the depth and breadth of a single entity but not the total amount
of expanded text throughout an entire XML document.

A medium-sized XML document with a couple of hundred kilobytes can
require a couple of hundred MB to several GB of memory. When the attack
is combined with some level of nested expansion an attacker is able to
achieve a higher ratio of success.

    <!DOCTYPE bomb [
    <!ENTITY a "xxxxxxx... a couple of ten thousand chars">
    ]>
    <bomb>&a;&a;&a;... repeat</bomb>

### external entity expansion (remote)

Entity declarations can contain more than just text for replacement.
They can also point to external resources by public identifiers or
system identifiers. System identifiers are standard URIs. When the URI
is a URL (e.g. a `http://` locator) some parsers download the resource
from the remote location and embed them into the XML document verbatim.

Simple example of a parsed external entity:

    <!DOCTYPE external [
    <!ENTITY ee SYSTEM "http://www.python.org/some.xml">
    ]>
    <root>&ee;</root>

The case of parsed external entities works only for valid XML content.
The XML standard also supports unparsed external entities with a
`NData declaration`.

External entity expansion opens the door to plenty of exploits. An
attacker can abuse a vulnerable XML library and application to rebound
and forward network requests with the IP address of the server. It
highly depends on the parser and the application what kind of exploit is
possible. For example:

-   An attacker can circumvent firewalls and gain access to restricted
    resources as all the requests are made from an internal and
    trustworthy IP address, not from the outside.
-   An attacker can abuse a service to attack, spy on or DoS your
    servers but also third party services. The attack is disguised with
    the IP address of the server and the attacker is able to utilize the
    high bandwidth of a big machine.
-   An attacker can exhaust additional resources on the machine, e.g.
    with requests to a service that doesn't respond or responds with
    very large files.
-   An attacker may gain knowledge, when, how often and from which IP
    address an XML document is accessed.
-   An attacker could send mail from inside your network if the URL
    handler supports `smtp://` URIs.

### external entity expansion (local file)

External entities with references to local files are a sub-case of
external entity expansion. It's listed as an extra attack because it
deserves extra attention. Some XML libraries such as lxml disable
network access by default but still allow entity expansion with local
file access by default. Local files are either referenced with a
`file://` URL or by a file path (either relative or absolute).
Additionally, lxml's `libxml2` has catalog support. XML catalogs like
`/etc/xml/catalog` are XML files, which map schema URIs to local files.

An attacker may be able to access and download all files that can be
read by the application process. This may include critical configuration
files, too.

    <!DOCTYPE external [
    <!ENTITY ee SYSTEM "file:///PATH/TO/simple.xml">
    ]>
    <root>&ee;</root>

### DTD retrieval

This case is similar to external entity expansion, too. Some XML
libraries like Python's xml.dom.pulldom retrieve document type
definitions from remote or local locations. Several attack scenarios
from the external entity case apply to this issue as well.

    <?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html>
        <head/>
        <body>text</body>
    </html>

## Python XML Libraries

| kind                                   | sax           | etree         | minidom       | pulldom       | xmlrpc        |
|----------------------------------------|---------------|---------------|---------------|---------------|---------------|
| billion laughs                         | **Maybe** (1) | **Maybe** (1) | **Maybe** (1) | **Maybe** (1) | **Maybe** (1) |
| quadratic blowup                       | **Maybe** (1) | **Maybe** (1) | **Maybe** (1) | **Maybe** (1) | **Maybe** (1) |
| external entity expansion (remote)     | False (2)     | False (3)     | False (4)     | False (2)     | false         |
| external entity expansion (local file) | False (2)     | False (3)     | False (4)     | False (2)     | false         |
| DTD retrieval                          | False (2)     | False         | False         | False (2)     | false         |
| gzip bomb                              | False         | False         | False         | False         | **True**      |
| xpath support (6)                      | False         | False         | False         | False         | False         |
| xsl(t) support (6)                     | False         | False         | False         | False         | False         |
| xinclude support (6)                   | False         | **True** (5)  | False         | False         | False         |
| C library                              | expat         | expat         | expat         | expat         | expat         |

vulnerabilities and features

1.  [expat parser](https://libexpat.github.io/) >= 2.4.0 has [billion
    laughs
    protection](https://libexpat.github.io/doc/api/latest/#billion-laughs)
    against XML bombs (CVE-2013-0340). The parser has sensible defaults
    for `XML_SetBillionLaughsAttackProtectionMaximumAmplification` and
    `XML_SetBillionLaughsAttackProtectionActivationThreshold`.
2.  Python >= 3.6.8, >= 3.7.1, and >= 3.8 no longer retrieve local and
    remote resources with urllib, see
    [bpo-17239](https://github.com/python/cpython/issues/61441).
3.  xml.etree doesn't expand entities and raises a ParserError when an
    entity occurs.
4.  minidom doesn't expand entities and simply returns the unexpanded
    entity verbatim.
5.  Library has (limited) XInclude support but requires an additional
    step to process inclusion.
6.  These are features but they may introduce exploitable holes, see
    [Other things to consider](#other-things-to-consider)

### Settings in standard library

#### xml.sax.handler Features

feature_external_ges (<http://xml.org/sax/features/external-general-entities>)  
disables external entity expansion

feature_external_pes (<http://xml.org/sax/features/external-parameter-entities>)  
the option is ignored and doesn't modify any functionality

#### DOM xml.dom.xmlbuilder.Options

external_parameter_entities  
ignored

external_general_entities  
ignored

external_dtd_subset  
ignored

entities  
unsure

## defusedxml

The [defusedxml package](https://github.com/tiran/defusedxml)
([defusedxml on PyPI](https://pypi.python.org/pypi/defusedxml)) contains
several Python-only workarounds and fixes for denial of service and
other vulnerabilities in Python's XML libraries. In order to benefit
from the protection you just have to import and use the listed functions
/ classes from the right defusedxml module instead of the original
module. Merely [defusedxml.xmlrpc](#defusedxml.xmlrpc) is implemented as
monkey patch.

Instead of:

    >>> from xml.etree.ElementTree import parse
    >>> et = parse(xmlfile)

alter code to:

    >>> from defusedxml.ElementTree import parse
    >>> et = parse(xmlfile)

<div class="note">

<div class="title">

Note

</div>

The defusedxml modules are not drop-in replacements of their stdlib
counterparts. The modules only provide functions and classes related to
parsing and loading of XML. For all other features, use the classes,
functions, and constants from the stdlib modules. For example:

    >>> from defusedxml import ElementTree as DET
    >>> from xml.etree.ElementTree as ET

    >>> root = DET.fromstring("<root/>")
    >>> root.append(ET.Element("item"))
    >>> ET.tostring(root)
    b'<root><item /></root>'

</div>

Additionally the package has an **untested** function to monkey patch
all stdlib modules with `defusedxml.defuse_stdlib()`.

<div class="warning">

<div class="title">

Warning

</div>

`defuse_stdlib()` should be avoided. It can break third party package or
cause surprising side effects. Instead you should use the parsing
features of defusedxml explicitly.

</div>

All functions and parser classes accept three additional keyword
arguments. They return either the same objects as the original functions
or compatible subclasses.

forbid_dtd (default: False)  
disallow XML with a `<!DOCTYPE>` processing instruction and raise a
*DTDForbidden* exception when a DTD processing instruction is found.

forbid_entities (default: True)  
disallow XML with `<!ENTITY>` declarations inside the DTD and raise an
*EntitiesForbidden* exception when an entity is declared.

forbid_external (default: True)  
disallow any access to remote or local resources in external entities or
DTD and raising an *ExternalReferenceForbidden* exception when a DTD or
entity references an external resource.

### defusedxml (package)

DefusedXmlException, DTDForbidden, EntitiesForbidden,
ExternalReferenceForbidden, NotSupportedError

defuse_stdlib() (*experimental*)

### defusedxml.cElementTree

**NOTE** `defusedxml.cElementTree` is deprecated and will be removed in
a future release. Import from `defusedxml.ElementTree` instead.

parse(), iterparse(), fromstring(), XMLParser

### defusedxml.ElementTree

parse(), iterparse(), fromstring(), XMLParser

### defusedxml.expatreader

create_parser(), DefusedExpatParser

### defusedxml.sax

parse(), parseString(), make_parser()

### defusedxml.expatbuilder

parse(), parseString(), DefusedExpatBuilder, DefusedExpatBuilderNS

### defusedxml.minidom

parse(), parseString()

### defusedxml.pulldom

parse(), parseString()

### defusedxml.xmlrpc

The fix is implemented as monkey patch for the stdlib's xmlrpc package
(3.x) or xmlrpclib module (2.x). The function <span
class="title-ref">monkey_patch()</span> enables the fixes, <span
class="title-ref">unmonkey_patch()</span> removes the patch and puts the
code in its former state.

The monkey patch protects against XML related attacks as well as
decompression bombs and excessively large requests or responses. The
default setting is 30 MB for requests, responses and gzip decompression.
You can modify the default by changing the module variable <span
class="title-ref">MAX_DATA</span>. A value of <span
class="title-ref">-1</span> disables the limit.

### defusedxml.lxml

**DEPRECATED** The module is deprecated and will be removed in a future
release.

lxml is safe against most attack scenarios. lxml uses `libxml2` for
parsing XML. The library has builtin mitigations against billion laughs
and quadratic blowup attacks. The parser allows a limit amount of entity
expansions, then fails. lxml also disables network access by default.
libxml2 [lxml
FAQ](https://lxml.de/FAQ.html#how-do-i-use-lxml-safely-as-a-web-service-endpoint)
lists additional recommendations for safe parsing, for example counter
measures against compression bombs.

The default parser resolves entities and protects against huge trees and
deeply nested entities. To disable entities expansion, use a custom
parser object:

    from lxml import etree

    parser = etree.XMLParser(resolve_entities=False)
    root = etree.fromstring("<example/>", parser=parser)

The module acts as an *example* how you could protect code that uses
lxml.etree. It implements a custom Element class that filters out Entity
instances, a custom parser factory and a thread local storage for parser
instances. It also has a check_docinfo() function which inspects a tree
for internal or external DTDs and entity declarations. In order to check
for entities lxml \> 3.0 is required.

parse(), fromstring() RestrictedElement, GlobalParserTLS,
getDefaultParser(), check_docinfo()

## defusedexpat

The [defusedexpat package](https://github.com/tiran/defusedexpat)
([defusedexpat on PyPI](https://pypi.python.org/pypi/defusedexpat)) is
no longer supported. [expat parser](https://libexpat.github.io/) 2.4.0
and newer come with [billion laughs
protection](https://libexpat.github.io/doc/api/latest/#billion-laughs)
against XML bombs.

## How to avoid XML vulnerabilities

Update to Python 3.6.8, 3.7.1, or newer. The SAX and DOM parser do not
load external entities from files or network resources.

Update to expat to 2.4.0 or newer. It has [billion laughs
protection](https://libexpat.github.io/doc/api/latest/#billion-laughs)
with sensible default limits to mitigate billion laughs and quadratic
blowup.

Official binaries from python.org use libexpat 2.4.0 since 3.7.12,
3.8.12, 3.9.7, and 3.10.0 (August 2021). Third party vendors may use
older or newer versions of expat. `pyexpat.version_info` contains the
current runtime version of libexpat. Vendors may have backported fixes
to older versions without bumping the version number.

Example:

    import sys
    import pyexpat

    has_mitigations = (
        sys.version_info >= (3, 7, 1) and
        pyexpat.version_info >= (2, 4, 0)
    )

### Best practices

-   Don't allow DTDs
-   Don't expand entities
-   Don't resolve externals
-   Limit parse depth
-   Limit total input size
-   Limit parse time
-   Favor a SAX or iterparse-like parser for potential large data
-   Validate and properly quote arguments to XSL transformations and
    XPath queries
-   Don't use XPath expression from untrusted sources
-   Don't apply XSL transformations that come untrusted sources

(based on Brad Hill's [Attacking XML
Security](https://www.isecpartners.com/media/12976/iSEC-HILL-Attacking-XML-Security-bh07.pdf))

## Other things to consider

XML, XML parsers and processing libraries have more features and
possible issue that could lead to DoS vulnerabilities or security
exploits in applications. I have compiled an incomplete list of
theoretical issues that need further research and more attention. The
list is deliberately pessimistic and a bit paranoid, too. It contains
things that might go wrong under daffy circumstances.

### attribute blowup / hash collision attack

XML parsers may use an algorithm with quadratic runtime O(n
<sup>2</sup>) to handle attributes and namespaces. If it uses hash
tables (dictionaries) to store attributes and namespaces the
implementation may be vulnerable to hash collision attacks, thus
reducing the performance to O(n <sup>2</sup>) again. In either case an
attacker is able to forge a denial of service attack with an XML
document that contains thousands upon thousands of attributes in a
single node.

I haven't researched yet if expat, pyexpat or libxml2 are vulnerable.

### decompression bomb

The issue of decompression bombs (aka [ZIP
bomb](https://en.wikipedia.org/wiki/Zip_bomb)) apply to all XML
libraries that can parse compressed XML stream like gzipped HTTP streams
or LZMA-ed files. For an attacker it can reduce the amount of
transmitted data by three magnitudes or more. Gzip is able to compress 1
GiB zeros to roughly 1 MB, lzma is even better:

    $ dd if=/dev/zero bs=1M count=1024 | gzip > zeros.gz
    $ dd if=/dev/zero bs=1M count=1024 | lzma -z > zeros.xy
    $ ls -sh zeros.*
    1020K zeros.gz
     148K zeros.xy

None of Python's standard XML libraries decompress streams except for
`xmlrpclib`. The module is vulnerable
\<<https://bugs.python.org/issue16043>\> to decompression bombs.

lxml can load and process compressed data through libxml2 transparently.
libxml2 can handle even very large blobs of compressed data efficiently
without using too much memory. But it doesn't protect applications from
decompression bombs. A carefully written SAX or iterparse-like approach
can be safe.

### Processing Instruction

[PI](https://en.wikipedia.org/wiki/Processing_Instruction)'s like:

    <?xml-stylesheet type="text/xsl" href="style.xsl"?>

may impose more threats for XML processing. It depends if and how a
processor handles processing instructions. The issue of URL retrieval
with network or local file access apply to processing instructions, too.

### Other DTD features

[DTD](https://en.wikipedia.org/wiki/Document_Type_Definition) has more
features like `<!NOTATION>`. I haven't researched how these features may
be a security threat.

### XPath

XPath statements may introduce DoS vulnerabilities. Code should never
execute queries from untrusted sources. An attacker may also be able to
create an XML document that makes certain XPath queries costly or
resource hungry.

### XPath injection attacks

XPath injeciton attacks pretty much work like SQL injection attacks.
Arguments to XPath queries must be quoted and validated properly,
especially when they are taken from the user. The page [Avoid the
dangers of XPath
injection](http://www.ibm.com/developerworks/xml/library/x-xpathinjection/index.html)
list some ramifications of XPath injections.

Python's standard library doesn't have XPath support. Lxml supports
parameterized XPath queries which does proper quoting. You just have to
use its xpath() method correctly:

    # DON'T
    >>> tree.xpath("/tag[@id='%s']" % value)

    # instead do
    >>> tree.xpath("/tag[@id=$tagid]", tagid=name)

### XInclude

[XML Inclusion](https://www.w3.org/TR/xinclude/#include_element) is
another way to load and include external files:

    <root xmlns:xi="http://www.w3.org/2001/XInclude">
      <xi:include href="filename.txt" parse="text" />
    </root>

This feature should be disabled when XML files from an untrusted source
are processed. Some Python XML libraries and libxml2 support XInclude
but don't have an option to sandbox inclusion and limit it to allowed
directories.

### XMLSchema location

A validating XML parser may download schema files from the information
in a `xsi:schemaLocation` attribute.

    <ead xmlns="urn:isbn:1-931666-22-9"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="urn:isbn:1-931666-22-9 http://www.loc.gov/ead/ead.xsd">
    </ead>

### XSL Transformation

You should keep in mind that XSLT is a Turing complete language. Never
process XSLT code from unknown or untrusted source! XSLT processors may
allow you to interact with external resources in ways you can't even
imagine. Some processors even support extensions that allow read/write
access to file system, access to JRE objects or scripting with Jython.

Example from [Attacking XML
Security](https://www.isecpartners.com/media/12976/iSEC-HILL-Attacking-XML-Security-bh07.pdf)
for Xalan-J:

    <xsl:stylesheet version="1.0"
     xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
     xmlns:rt="http://xml.apache.org/xalan/java/java.lang.Runtime"
     xmlns:ob="http://xml.apache.org/xalan/java/java.lang.Object"
     exclude-result-prefixes= "rt ob">
     <xsl:template match="/">
       <xsl:variable name="runtimeObject" select="rt:getRuntime()"/>
       <xsl:variable name="command"
         select="rt:exec($runtimeObject, &apos;c:\Windows\system32\cmd.exe&apos;)"/>
       <xsl:variable name="commandAsString" select="ob:toString($command)"/>
       <xsl:value-of select="$commandAsString"/>
     </xsl:template>
    </xsl:stylesheet>

## Related CVEs

CVE-2013-1664  
Unrestricted entity expansion induces DoS vulnerabilities in Python XML
libraries (XML bomb)

CVE-2013-1665  
External entity expansion in Python XML libraries inflicts potential
security flaws and DoS vulnerabilities

## Other languages / frameworks

Several other programming languages and frameworks are vulnerable as
well. A couple of them are affected by the fact that libxml2 up to 2.9.0
has no protection against quadratic blowup attacks. Most of them have
potential dangerous default settings for entity expansion and external
entities, too.

### Perl

Perl's XML::Simple is vulnerable to quadratic entity expansion and
external entity expansion (both local and remote).

### Ruby

Ruby's REXML document parser is vulnerable to entity expansion attacks
(both quadratic and exponential) but it doesn't do external entity
expansion by default. In order to counteract entity expansion you have
to disable the feature:

    REXML::Document.entity_expansion_limit = 0

libxml-ruby and hpricot don't expand entities in their default
configuration.

### PHP

PHP's SimpleXML API is vulnerable to quadratic entity expansion and
loads entities from local and remote resources. The option
`LIBXML_NONET` disables network access but still allows local file
access. `LIBXML_NOENT` seems to have no effect on entity expansion in
PHP 5.4.6.

### C# / .NET / Mono

Information in [XML DoS and Defenses
(MSDN)](https://msdn.microsoft.com/en-us/magazine/ee335713.aspx) suggest
that .NET is vulnerable with its default settings. The article contains
code snippets how to create a secure XML reader:

    XmlReaderSettings settings = new XmlReaderSettings();
    settings.ProhibitDtd = false;
    settings.MaxCharactersFromEntities = 1024;
    settings.XmlResolver = null;
    XmlReader reader = XmlReader.Create(stream, settings);

### Java

Untested. The documentation of Xerces and its [Xerces
SecurityMananger](https://xerces.apache.org/xerces2-j/javadocs/xerces2/org/apache/xerces/util/SecurityManager.html)
sounds like Xerces is also vulnerable to billion laugh attacks with its
default settings. It also does entity resolving when an
`org.xml.sax.EntityResolver` is configured. I'm not yet sure about the
default setting here.

Java specialists suggest to have a custom builder factory:

    DocumentBuilderFactory builderFactory = DocumentBuilderFactory.newInstance();
    builderFactory.setXIncludeAware(False);
    builderFactory.setExpandEntityReferences(False);
    builderFactory.setFeature(XMLConstants.FEATURE_SECURE_PROCESSING, True);
    # either
    builderFactory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", True);
    # or if you need DTDs
    builderFactory.setFeature("http://xml.org/sax/features/external-general-entities", False);
    builderFactory.setFeature("http://xml.org/sax/features/external-parameter-entities", False);
    builderFactory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", False);
    builderFactory.setFeature("http://apache.org/xml/features/nonvalidating/load-dtd-grammar", False);

## TODO

-   DOM: Use xml.dom.xmlbuilder options for entity handling
-   SAX: take feature_external_ges and feature_external_pes (?) into
    account
-   test experimental monkey patching of stdlib modules
-   improve documentation

## License

Copyright (c) 2013-2023 by Christian Heimes \<<christian@python.org>\>

Licensed to PSF under a Contributor Agreement.

See <https://www.python.org/psf/license> for licensing details.

## Acknowledgements

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
Many thanks to Carl for his report to PSRT on behalf of the Django
security team.

Daniel Veillard (libxml2)  
Many thanks to Daniel for his insight and assistance with libxml2.

semantics GmbH (<https://www.semantics.de/>)  
Many thanks to my employer semantics for letting me work on the issue
during working hours as part of semantics's open source initiative.

## References

-   [XML DoS and Defenses
    (MSDN)](https://msdn.microsoft.com/en-us/magazine/ee335713.aspx)
-   [Billion Laughs](https://en.wikipedia.org/wiki/Billion_laughs) on
    Wikipedia
-   [ZIP bomb](https://en.wikipedia.org/wiki/Zip_bomb) on Wikipedia
-   [Configure SAX parsers for secure
    processing](http://www.ibm.com/developerworks/xml/library/x-tipcfsx/index.html)
-   [Testing for XML
    Injection](https://www.owasp.org/index.php/Testing_for_XML_Injection_(OWASP-DV-008))
# Changelog

## defusedxml 0.8.0rc2

-   Silence deprecation warning in <span
    class="title-ref">defuse_stdlib</span>.
-   Update lxml safety information

## defusedxml 0.8.0rc1

*Release date: 26-Sep-2023*

-   Drop support for Python 2.7, 3.4, and 3.5.
-   Test on 3.10, 3.11, and 3.12.
-   Add `defusedxml.ElementTree.fromstringlist()`
-   Update *vulnerabilities and features* table in README.
-   **Pending removal** The `defusedxml.lxml` module has been
    unmaintained and deprecated since 2019. The module will be removed
    in the next version.
-   **Pending removal** The `defusedxml.cElementTree` will be removed in
    the next version. Please use `defusedxml.ElementTree` instead.

## defusedxml 0.7.1

*Release date: 08-Mar-2021*

-   Fix regression `defusedxml.ElementTree.ParseError` (#63) The
    `ParseError` exception is now the same class object as
    `xml.etree.ElementTree.ParseError` again.

## defusedxml 0.7.0

*Release date: 4-Mar-2021*

-   No changes

## defusedxml 0.7.0rc2

*Release date: 12-Jan-2021*

-   Re-add and deprecate `defusedxml.cElementTree`
-   Use GitHub Actions instead of TravisCI
-   Restore `ElementTree` attribute of `xml.etree` module after patching

## defusedxml 0.7.0rc1

*Release date: 04-May-2020*

-   Add support for Python 3.9
-   `defusedxml.cElementTree` is not available with Python 3.9.
-   Python 2 is deprecate. Support for Python 2 will be removed in
    0.8.0.

## defusedxml 0.6.0

*Release date: 17-Apr-2019*

-   Increase test coverage.
-   Add badges to README.

## defusedxml 0.6.0rc1

*Release date: 14-Apr-2019*

-   Test on Python 3.7 stable and 3.8-dev
-   Drop support for Python 3.4
-   No longer pass *html* argument to XMLParse. It has been deprecated
    and ignored for a long time. The DefusedXMLParser still takes a html
    argument. A deprecation warning is issued when the argument is False
    and a TypeError when it's True.
-   defusedxml now fails early when pyexpat stdlib module is not
    available or broken.
-   defusedxml.ElementTree.\_\_all\_\_ now lists ParseError as public
    attribute.
-   The defusedxml.ElementTree and defusedxml.cElementTree modules had a
    typo and used XMLParse instead of XMLParser as an alias for
    DefusedXMLParser. Both the old and fixed name are now available.

## defusedxml 0.5.0

*Release date: 07-Feb-2017*

-   No changes

## defusedxml 0.5.0.rc1

*Release date: 28-Jan-2017*

-   Add compatibility with Python 3.6
-   Drop support for Python 2.6, 3.1, 3.2, 3.3
-   Fix lxml tests (XMLSyntaxError: Detected an entity reference loop)

## defusedxml 0.4.1

*Release date: 28-Mar-2013*

-   Add more demo exploits, e.g. python_external.py and Xalan XSLT
    demos.
-   Improved documentation.

## defusedxml 0.4

*Release date: 25-Feb-2013*

-   As per <http://seclists.org/oss-sec/2013/q1/340> please REJECT
    CVE-2013-0278, CVE-2013-0279 and CVE-2013-0280 and use
    CVE-2013-1664, CVE-2013-1665 for OpenStack/etc.
-   Add missing parser_list argument to sax.make_parser(). The argument
    is ignored, though. (thanks to Florian Apolloner)
-   Add demo exploit for external entity attack on Python's SAX parser,
    XML-RPC and WebDAV.

## defusedxml 0.3

*Release date: 19-Feb-2013*

-   Improve documentation

## defusedxml 0.2

*Release date: 15-Feb-2013*

-   Rename ExternalEntitiesForbidden to ExternalReferenceForbidden
-   Rename defusedxml.lxml.check_dtd() to check_docinfo()
-   Unify argument names in callbacks
-   Add arguments and formatted representation to exceptions
-   Add forbid_external argument to all functions and classes
-   More tests
-   LOTS of documentation
-   Add example code for other languages (Ruby, Perl, PHP) and parsers
    (Genshi)
-   Add protection against XML and gzip attacks to xmlrpclib

## defusedxml 0.1

*Release date: 08-Feb-2013*

-   Initial and internal release for PSRT review
