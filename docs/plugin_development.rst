.. _plugin_dev:

Plugin development
==================

A plugin is the component in charge of detect one software and its version.
Since a software could have many different signatures,
every plugin has test files associated to assure version integrity
and add new signatures without breaking the working ones.

Let's see how to write your own plugin.

Requirements
^^^^^^^^^^^^

The plugin has to:

* Be compliant with :class:`IPlugin <detectem.plugin.IPlugin>` interface.
* Be a subclass of :class:`Plugin <detectem.plugin.Plugin>`.
* Have a test file at ``tests/plugins/fixtures/<plugin_name>.yml``.

To make it faster, there's a script called ``add_new_plugin.py``
which creates both plugin and test file.


.. code-block:: bash

  $ python scripts/add_new_plugin.py example --matcher url --category infraestructure

  Created plugin file at detectem/detectem/plugins/infraestructure/example.py
  Created test file at detectem/tests/plugins/fixtures/example.yml


Plugin file
^^^^^^^^^^^

We're creating an example plugin
for a ficticious software called ``examplelib``.
We can detect it easily since it's included as an external library
and in its ``URL`` it contains the version.
Then we will use the ``URL`` matcher for this case.


.. code-block:: python

  from detectem.plugin import Plugin


  class ExamplePlugin(Plugin):
      name = 'example'
      homepage = 'http://example.org'
      matchers = [
          {'url': '/examplelib\.v(?P<version>[0-9\.]+)-min\.js$'},
      ]
      """
      js_matchers = [
          {{'check': '', 'version': ''}},
      ]
      """

It contains the attributes enforced by the interface.
There also Javascript matchers (``js_matchers``)
which works on the page DOM_ to get dynamic information.

Review :ref:`matchers <matchers>` page to meet the available options.


Test file
^^^^^^^^^

This is the test file for our example plugin:

.. code-block:: yaml

  - plugin: example
    matches:
      - url: http://domain.tld/examplelib.v1.1.3-min.js
        version: 1.1.3


Then running the test is simple:


.. code-block:: bash

  $ py.test tests/plugins/test_generic.py --plugin example
  ===== test session starts ==============================
  platform linux -- Python 3.5.2, pytest-3.0.6, py-1.4.32, pluggy-0.4.0
  plugins: mock-1.5.0, cov-2.4.0
  collected 2 items

  tests/plugins/test_generic.py .s

  ===== 1 passed, 1 skipped in 0.20 seconds ==============


When you need to support a new signature
and it's not supported by current signatures,
you must modify your plugin file
and add a new test to the list to see
that your changes didn't break previous detected versions.


References
^^^^^^^^^^

.. autointerface:: detectem.plugin.IPlugin

.. autoclass:: detectem.plugin.Plugin



.. _DOM: https://en.wikipedia.org/wiki/Document_Object_Model
