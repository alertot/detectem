.. _header_matcher:

Header Matcher
==============

======  ===
Format  ``(header=string:required, extractor=string:optional)``
Type    tuple
Scope   First response
======  ===

It operates on response headers.
As you could expect, it works only on first response
since it contains the headers sent by website's server.

It's used to extract data exposed by the web server software
and its stack.
You could also dive into ``Set-Cookie`` headers
to extract cookie information.


Example
^^^^^^^

A website ``X`` uses ``Apache HTTPd Server``.
The response contains the following headers:

.. code-block:: bash

  [...]
  Server: Apache/2.4.25
  [...]

We will use a header matcher to extract Apache's version.
First, we need to decide which header to look for.
In this case, it's the header ``Server``.


.. code-block:: python

  from detectem.plugin import Plugin


  class ApachePlugin(Plugin):
      name = 'apache'
      matchers = [
          {'header': ('Server', r'Apache/(?P<version>[0-9\.]+)')},
      ]

Then, when you run detectem on ``X``,
it will detect the presence of ``Apache`` and its version ``2.4.25``.
