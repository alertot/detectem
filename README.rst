detectem
========


.. image:: https://img.shields.io/pypi/v/detectem.svg
        :target: https://pypi.python.org/pypi/detectem

.. image:: https://img.shields.io/travis/spectresearch/detectem.svg
        :target: https://travis-ci.org/spectresearch/detectem

.. image:: https://pyup.io/repos/github/spectresearch/detectem/shield.svg
     :target: https://pyup.io/repos/github/spectresearch/detectem/
     :alt: Updates


Detect software in websites.


Installation
------------

1. Install Docker_.
2. Pull the image::

    $ sudo docker pull scrapinghub/splash

3. Install detectem::

    $ pip install detectem

4. Run it against some URL::

    $ det http://domain.tld


Features
--------

* Detect software in modern web technologies.
* Browser support provided by Splash_.
* Plugin system to add new software easily.
* Test suite to ensure plugin functionality.


.. _Docker: http://docker.io
.. _Splash: https://github.com/scrapinghub/splash
