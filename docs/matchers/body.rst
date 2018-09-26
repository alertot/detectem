.. _body_matcher:

Body Matcher
============

======  ===
Format  ``extractor=string``
Type    string
Scope   All requests/responses except first one
======  ===

It operates on response body as a regular expression on raw text.
Its scope is every response body except the first one
since doing matching at it is highly prone to false positives.
To select data from first response, you should use a XPath matcher.

It's used usually to extract data from commentaries.


Example
^^^^^^^

A website ``X`` uses a library called ``yobu`` and loads it from
``https://cdn.tld/yobu.js``.
As you see, no version could be extracted using a URL matcher.
However, the response body contains some valuable information:

.. code-block:: javascript

  //! yobu v1.2.3
  [...]


Then, it's the perfect fit for a body matcher.
Let's create a plugin to detect ``yobu``.


.. code-block:: python

  from detectem.plugin import Plugin

  class YobuPlugin(Plugin):
      name = 'yobu'
      matchers = [
        {'body': r'//! yobu v(?P<version>[0-9\.]+)'},
      ]

Then, when you run detectem on ``X``,
it will detect the presence of ``yobu`` and its version ``1.2.3``.
