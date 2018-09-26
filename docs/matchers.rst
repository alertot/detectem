.. _matchers:

Matchers
========

Matchers are in charge of extract software information.
*detectem* has different matchers according to its target.

.. toctree::
  :glob:
  :maxdepth: 1

  matchers/*


Most matchers use an argument called ``extractor``.
Depending on its value, it could extract:

Presence
~~~~~~~~

If ``extractor`` doesn't have a named parameter or doesn't exist,
the matcher only checks plugin presence.


Version extraction
~~~~~~~~~~~~~~~~~~

For these cases the ``extractor`` has ``version``
as the named parameter for the regular expression.


Name extraction
~~~~~~~~~~~~~~~

Some projects like AngularJS_ have modules that could be included
to add functionality.
The issue is that both core library and module
have the same signature for the version,
then it's needed to determine the software module too.

For these cases ``extractor`` has ``name``
as the named parameter for the regular expression.


.. _AngularJS: https://angularjs.org/
