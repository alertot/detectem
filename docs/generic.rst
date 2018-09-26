.. _generic_plugin:

.. |wgp| replace:: :class:`WordpressGenericPlugin <detectem.plugins.generic.WordpressGenericPlugin>`

Generic plugin
==============

A generic plugin is a plugin that detects the presence of multiple softwares.
It's ideal for software that uses plugins and its detection could be automatic.
For this walkthrough we will take as example |wgp|.

Please verify the code for an exact working example
since here we put it by pieces just highlighting important parts.


Basics
^^^^^^

What defines a generic plugin?
The first difference, it subclasses :class:`GenericPlugin <detectem.plugin.GenericPlugin>`
to set the plugin type (``ptype`` attribute) to ``'generic'``,
which let us know that it's a generic plugin.
For organization purposes, they lie in ``detectem.plugins.generic`` module.


.. code:: python

    from detectem.plugin import GenericPlugin

    class WordpressGenericPlugin(GenericPlugin):
        [...]


In this class of plugins, as far as we've seen during development until now,
there's no way to extract the version reliably,
then we're going to use ``indicators``.

What's a proper indicator for a generic plugin?
In Wordpress, every Wordpress plugin is located at the following path:
``/wp-content/plugins/<plugin_name>/``.
The mission of our generic plugin is to discover
as many Wordpress plugins as possible,
then we are going to use an URL matcher that matches Wordpress plugin directory.

.. code:: python

    from detectem.plugin import GenericPlugin

    class WordpressGenericPlugin(GenericPlugin):
        indicators = [
            {'url': '/wp-content/plugins/'}
        ]


Then, if a website loads a resource from the directory ``/wp-content/plugins/``,
our |wgp| will match.


Data extraction
^^^^^^^^^^^^^^^

After matching,
detectem will call a method named ``get_information(entry)`` on the plugin.
This method extracts information from the matching _HAR_ ``entry``
and returns a dictionary with at least ``name`` and ``homepage`` keys
to be displayed in detectem results.

In the case of |wgp|,
we extract the plugin name from ``entry``'s url
and build homepage plugin URL dinamycally.

.. code:: python

    def get_information(self, entry):
        name = re.findall('/wp-content/plugins/([^/]+)/', get_url(entry))[0]
        homepage = self.homepage % name

        return {
            'name': name,
            'homepage': homepage,
        }


Despite of using an ``indicator``,
the generic spider could return version data from ``get_information(entry)``
since the ``indicator`` is just a signal to execute the generic plugin logic.

Actual implementation of WordpressGenericPlugin returns more data
and verifies plugin name against the public repository of Wordpress plugins.
Please check out the source code to see the working implementation.


Priority
^^^^^^^^

As seen with |wgp|,
it returns the same data as an ``indicator`` would do,
then they share the same priority.

That makes possible that we can create plugins to detect Wordpress plugins
where we can extract the version and they will prevail over generic results
because they have higher priority.
A good example is the plugin ``crayon-syntax-highlighter``,
which correct detection will return the plugin version
and that information will be returned instead of generic information.
