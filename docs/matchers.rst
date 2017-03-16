.. _matchers:

Matchers
========

Matchers are in charge of extract software version.
There are two big groups: static and javascript matchers.


Static matchers
^^^^^^^^^^^^^^^

There are three types of static matchers:

* URL (``url``): operate on request/response URLs made by the website.
* Body (``body``): operate on response body.
* Header (``header``): operate on request/response headers.
  Useful to analyze cookie content too.

Matchers are usually regular expressions (functions are also supported)
and they **must** have a named parameter ``version``.
In example, *MomentJS* plugin has the following URL matcher:


.. code-block:: python

  matchers = [
    {'url': '/moment\.js/(?P<version>[0-9\.]+)/moment(\.min)?\.js'},
  ]


Javascript matchers
^^^^^^^^^^^^^^^^^^^

Javascript matchers are evaluated on the page DOM_.
It makes easy the cases where it's hard to write reliable static matchers
due to page measures.
In example, this D3.js_ `example <https://bl.ocks.org/mbostock/4061502>`_
uses a minified version of `D3.js library <https://d3js.org/d3.v3.min.js>`_.
If you see, it's hard to extract version in a reliable and generic way
since it's hold in a not meaningful variable
and recompiling the library could change the variable name.

However, this minified script create the ``D3`` object in the DOM_,
then using ``D3.version`` we could get the version reliably.
Taking the example from the D3.js_ plugin:

.. code-block:: python

  js_matchers = [
    {'check': 'window.d3', 'version': 'window.d3.version'},
  ]

It has two fields:

* ``check``: Javascript code to verify if the target object exists.
  Usually you use ``window.object`` since it doesn't raise an error.
* ``version``: Javascript code to get software version.
  It has ``window`` as prefix to make easier the testing
  (it's valid in the browser and testing environment)

Both fields are evaluated in the Javascript context of the page.
For sanity purposes,
it's a good idea to keep the ``window`` object
since without it could lead to unexpected results in presence of iframes.


Modular matchers
^^^^^^^^^^^^^^^^

Some projects like AngularJS_ have modules that could be included
to add functionality.
The issue is that both core library and module
have the same signature for the version,
then it's needed to determine the software module too.
Here comes *modular matchers* to detect the module name.
They use the static matchers but with ``name``
as the named parameter for the regular expression.

In example, *AngularJS* plugin has the following modular matcher:

.. code-block:: python

  modular_matchers = [
    {'url': '/(?:angular-)(?P<name>\w+)\.min\.js'},
  ]


.. _DOM: https://en.wikipedia.org/wiki/Document_Object_Model
.. _D3.js: https://d3js.org/
.. _AngularJS: https://angularjs.org/
