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

CircleCI builds an amd64 image on ``master``, runs non-integration tests, and
checks Docker API negotiation. To publish, trigger a pipeline on ``master`` with
the boolean pipeline parameter ``publish_image`` set to true and ``image_tag``
set to a versioned tag (for example, ``v4.1.3``). The publish job uses the
``kube-system/helm/dockerhub/roboshopkeep`` CircleCI context, whose credentials
must have push access to ``lightspeedcommerceinc/shpkpr``.
Publishing is disabled by default and does not update the shared-pipelines image
reference; update that reference separately after validating the published image.
