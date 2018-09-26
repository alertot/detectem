.. _xpath_matcher:

XPath Matcher
=============

======  ===
Format  ``(xpath=string:required, extractor=string:optional)``
Type    tuple
Scope   First response
======  ===

It operates on the first response.
Since regular expressions are unproper
to use on first response body
it's better to use XPaths that are context-aware.

This matcher is useful to extract version information
from meta tags, tag attributes or HTML comments.
Javascript embedded scripts or inline declarations
aren't available to XPath matcher because of embedded inline split.


Example
^^^^^^^

A website ``X`` uses a software called ``yobu``.
It doesn't load any resource that could lead
to identify the version of ``yobu``
but it adds a meta tag to the page
that contains its version.
It looks like:

..
  [...]
  <meta name="generator" content="yobu 1.2.3" />
  [...]

We will use a XPath matcher to extract that data.
The first element of the tuple is an XPath.
What should be able to give us this XPath?
A string where we could apply our version extractor string.
In this case, our goal is to get ``yobu 1.2.3``.

A XPath capable of doing this is:
``//meta[@name='generator']/@content``.
That is enough but as this case is so common,
we've added a helper named ``meta_generator``
that works very well in this scenario.
In this case, it should be called ``meta_generator('yobu')``.

The second element is our well-known version extractor string.
Finally, we are ready with our new matcher:


.. code-block:: python

  from detectem.plugin import Plugin
  from detectem.plugins.helpers import meta_generator


  class YobuPlugin(Plugin):
      name = 'yobu'
      matchers = [
          {'xpath': (meta_generator('yobu'), r'(?P<version>[0-9\.]+)')},
      ]

Then, when you run detectem on ``X``,
it will detect the presence of ``yobu`` and its version ``1.2.3``.
