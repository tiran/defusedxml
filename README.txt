==========
defusedxml
==========


Attacks
=======

billion laughs / exponential entity expansion
---------------------------------------------

.. include:: xmltestdata/xmlbomb.xml
   :literal:


quadratic blowup entity expansion
---------------------------------

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


.. csv-table::
   :header: "kind",             "sax",  "etree",  "minidom", "pulldom", "lxml"
   :widths: 15, 10, 10, 13, 10, 10

   "billion laughs",            "True", "True",   "True",    "True",    "False *"
   "quadratic blowup",          "True", "True",   "True",    "True",    "True"
   "external entity expansion", "True", "False",  "True",    "True",    "False *"
   "DTD external fetch",        "True", "False",  "False",   "True",    "False *"
   "C library",                 "expat", "expat", "expat",   "expat",   "libxml2"
   "handler",                   "expatreader", "XMLParser", "expatbuilder / pulldom", "sax", ""

\*) By default lxml is protected against billion laughs attacks and doesn't
do network lookups.

TODO
====

 * DOM: Use xml.dom.xmlbuilder options for entity handling
 * SAX: take feature_external_ges and feature_external_pes (?) into account
 * implement monkey patching of stdlib modules
 * test lxml default element class overwrite
 * document which module / library is vulnerable to which kind of attack
