detectem
========


.. image:: https://img.shields.io/pypi/v/detectem.svg
        :target: https://pypi.python.org/pypi/detectem

.. image:: https://img.shields.io/travis/spectresearch/detectem.svg
        :target: https://travis-ci.org/spectresearch/detectem


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


Installation
------------

1. Install Docker_ and add your user to the docker group, then you avoid to use sudo.

2. Pull the image::

    $ docker pull scrapinghub/splash

3. Create a virtual environment with Python >= 3.5 .

4. Install detectem::

    $ pip install detectem

5. Run it against some URL::

    $ det http://domain.tld


Documentation
-------------

The documentation is at `ReadTheDocs <https://detectem.readthedocs.io>`_.

.. _Docker: http://docker.io
.. _Splash: https://github.com/scrapinghub/splash
.. _DOM: https://en.wikipedia.org/wiki/Document_Object_Model

