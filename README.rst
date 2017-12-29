detectem
========


.. image:: https://img.shields.io/pypi/v/detectem.svg
        :target: https://pypi.python.org/pypi/detectem

.. image:: https://img.shields.io/travis/spectresearch/detectem.svg
        :target: https://travis-ci.org/spectresearch/detectem


detectem is a specialized software detector.
Let's see it in action.

.. code-block:: bash

  $ docker-compose run --rm detectem http://domain.tld
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

* Detect software in modern web technologies
* Browser support provided by Splash_
* Analysis on requests made and responses received by the browser
* Get software information from the DOM
* Great performance (less than 10 seconds to get a fingerprint)
* Plugin system to add new software easily
* Test suite to ensure plugin result integrity
* Continuous development to support new features


Installation
------------

1. Install the last `Docker CE Stable version`_

2. Add your user into the docker group (this will avoid using sudo with docker)::

    $ sudo usermod -a -G docker you

3. Install `Docker Compose`_


4. Download to your workspace the docker-compose building files
    `Dockerfile-alternate`_
    `docker-compose.yml`_

5. Build the required docker images for Detectem::
        
    $ docker-compose up -d

    # This step will build up a Docker image for 'Splash' and another one for 'Python Alpine' which are necessaries as software dependencies for the Detectem container instances, so, let them survive. 

    # Be patience, it will download 1.24GB

6. Run Detectem against some URL::

    $ docker-compose run --rm detectem url

    # This will create a temporal Detectem container instance just to be executed against the target url 

Documentation
-------------

The documentation is at `ReadTheDocs <https://detectem.readthedocs.io>`_.

.. _`Docker CE Stable version`: https://www.docker.com/community-edition
.. _`Docker compose`: https://docs.docker.com/compose/install/
.. _Dockerfile-alternate: https://github.com/alertot/detectem/tree/master/extras/docker/Dockerfile-alternate
.. _docker-compose.yml: https://github.com/alertot/detectem/tree/master/extras/docker/docker-compose.yml
.. _Splash: https://github.com/scrapinghub/splash
.. _DOM: https://en.wikipedia.org/wiki/Document_Object_Model
