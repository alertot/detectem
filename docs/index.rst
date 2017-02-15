.. _detectem:

Welcome to detectem's documentation!
====================================

This documentation contains everything you need to know about detectem.

detectem is a specialized software detector.
Let's see it in action.

.. code-block:: bash

  $ det http://domain.tld
  [{'name': 'phusion-passenger', 'version': '4.0.10'},
   {'name': 'apache-mod_bwlimited', 'version': '1.4'},
   {'name': 'apache-mod_fcgid', 'version': '2.3.9'},
   {'name': 'jquery', 'version': '1.11.3'},
   {'name': 'crayon-syntax-highlighter', 'version': '_2.7.2_beta'}]


Using a serie of indicators, it's able to detect software running on a site
and extract accurately its version information.
It uses Splash_ API
to render the website and start the detection routine.
It does full analysis on requests, responses and even on the DOM_!

There are two important articles to read:

* `Reasons to create detectem <http://www.spect.cl/blog/2016/11/challenges-in-web-software-detection/>`_
* `Introduction to detectem <http://www.spect.cl/blog/2016/11/introducing-detectem/>`_


Features
--------

* Detect software in modern web technologies.
* Browser support provided by Splash_.
* Analysis on requests made and responses received by the browser.
* Get software information from the DOM.
* Great performance (less than 10 seconds to get a fingerprint).
* Plugin system to add new software easily.
* Test suite to ensure plugin result integrity.
* Continuous development to support new features.


Contribuiting
-------------

It's easy to contribute.
If you want to add a new plugin follow the guide of :ref:`plugin_dev`
and make your pull request at the official repository.


Documentation
-------------

.. toctree::
   :maxdepth: 2

   installation
   matchers
   plugin_development


.. _DOM: https://en.wikipedia.org/wiki/Document_Object_Model
.. _Splash: https://github.com/scrapinghub/splash
