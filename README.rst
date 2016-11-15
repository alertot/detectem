detectem
========


.. image:: https://img.shields.io/pypi/v/detectem.svg
        :target: https://pypi.python.org/pypi/detectem

.. image:: https://img.shields.io/travis/spectresearch/detectem.svg
        :target: https://travis-ci.org/spectresearch/detectem


detectem detects software and its version in websites.
For a great introduction about it, please check
`this blog post <http://www.spect.cl/blog/2016/11/introducing-detectem/>`_.


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


Features
--------

* Detect software in modern web technologies.
* Browser support provided by Splash_.
* Plugin system to add new software easily.
* Test suite to ensure plugin functionality.


.. _Docker: http://docker.io
.. _Splash: https://github.com/scrapinghub/splash
