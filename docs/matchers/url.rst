.. _url_matcher:

URL matcher
===========

======  ===
Format  ``extractor=string``
Type    string
Scope   All requests/responses except first one
======  ===

It operates on request/response URLs made by the browser when loading a website.
The *scope* for this matcher is every request/response URL
except the first one,
since they are usually the website's URL to analyze.


Example
^^^^^^^

A website ``X`` uses a library called ``yobu`` and loads it from
``https://cdn.tld/yobu-1.2.3.js``.
As you see, the version is present in the URL
and we can extract it using a URL matcher.
Let's create a plugin to detect ``yobu``.


.. code-block:: python

  from detectem.plugin import Plugin

  class YobuPlugin(Plugin):
      name = 'yobu'
      matchers = [
        {'url': r'/yobu-(?P<version>[0-9\.]+)\.js'},
      ]

Then, when you run detectem on ``X``,
it will detect the presence of ``yobu`` and its version ``1.2.3``.
