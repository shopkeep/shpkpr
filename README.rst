===============================
shpkpr
===============================

.. image:: https://img.shields.io/travis/shopkeep/shpkpr.svg
        :target: https://travis-ci.org/shopkeep/shpkpr

.. image:: https://readthedocs.org/projects/shpkpr/badge/?version=latest
        :target: https://readthedocs.org/projects/shpkpr/?badge=latest
        :alt: Documentation Status


shpkpr is a tool for controlling and observing applications/tasks running on Marathon and Chronos. shpkpr is designed to provide a simple command-line interface to Marathon and Chronos (similiar to the ``heroku`` command-line tool) for use both manually and with CI tools like jenkins.

* Free software: MIT license
* Documentation: https://shpkpr.readthedocs.org.
* Quick start guide: https://shpkpr.readthedocs.io/en/latest/contributing.html#get-started

Features
--------

* List/show detailed application info
* Deploy applications (using `Jinja2 <http://jinja.pocoo.org/docs/2.9/>`_ templates)
* Zero-downtime application deploys when used with `Marathon-LB <https://github.com/mesosphere/marathon-lb>`_
* List/show detailed cron task info
* Deploy cron tasks (using `Jinja2 <http://jinja.pocoo.org/docs/2.9/>`_ templates)

Publishing the Docker image
---------------------------

The Jenkins pipeline builds an amd64 image and checks Docker API negotiation on
the agent. To publish, run the multibranch job on ``master`` with
``PUBLISH_IMAGE`` enabled and a versioned ``IMAGE_TAG`` (for example,
``v4.1.3-lsr41151``). It uses the ``dockerhub_roboshopkeep`` Jenkins credential,
which must have push access to ``lightspeedcommerceinc/shpkpr``. Publishing is
disabled by default and the pipeline does not update the shared-pipelines image
reference; update that reference separately after validating the published image.
