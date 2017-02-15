Installation
============

1. Install Docker_ and add your user to the docker group, then you avoid to use sudo.

2. Pull the image::

    $ docker pull scrapinghub/splash

3. Create a virtual environment with Python >= 3.5 .

4. Install detectem::

    $ pip install detectem

5. Run it against some URL::

    $ det http://domain.tld


.. _Docker: http://docker.io
