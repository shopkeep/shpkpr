============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/shopkeep/shpkpr/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Did you install with ``pip`` or ``docker``?
* Are you using a released version or a ``git`` checkout?
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "feature" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

shpkpr could always use more documentation, whether as part of the official shpkpr docs, in docstrings, or even on the web in blog posts, articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/shopkeep/shpkpr/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that contributions are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up ``shpkpr`` for local development.

1. Fork the ``shpkpr`` repo on GitHub.

2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/shpkpr.git

3. Install your local copy into a virtualenv. Assuming you have `virtualenvwrapper <https://virtualenvwrapper.readthedocs.org/en/latest/>`_ installed, this is how you set up your fork for local development::

    $ mkvirtualenv shpkpr
    $ cd shpkpr/
    $ pip install --editable .

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass the tests, including testing other Python versions with `tox <https://pypi.python.org/pypi/tox>`_::

    $ tox

   To get tox, just pip install it into your virtualenv.

   If you prefer, and have docker installed, you can also run the tests against all supported Python versions::

    $ make test

   You should also run the integration tests against a live marathon instance to manually verify that the tool still works as expected. Set the necessary environment variables as appropriate::

    # URL of the Marathon API to use
    export SHPKPR_MARATHON_URL=http://marathon.somedomain.com:8080

    # An application ID to use for testing, this should not exist on
    # Marathon prior to running the tests
    export SHPKPR_APPLICATION=my-dummy-application-for-testing

    # Docker repotag of the container that should be deployed to Marathon.
    # This container must be pullable by the mesos cluster; for testing
    # purposes it's probably easiest to use a container from the public
    # Docker hub.
    export SHPKPR_DOCKER_REPOTAG=goexample/outyet:latest

    # Port that should be exposed from the Docker container
    export SHPKPR_DOCKER_EXPOSED_PORT=8080

    # An arbitrary label to be injected into the deploy template. This can
    # be any non-empty string for testing.
    export SHPKPR_DEPLOY_DOMAIN=somedomain.com

   Then::

    $ tox -e integration

   Or::

    $ make test.integration

6. If your changes are user-facing, you should update the documentation to reflect the changes you've made. shpkpr's documentation is built with `Sphinx <http://sphinx-doc.org/>`_ and can be built using the ``make``::

    $ pip install -r requirements-docs.txt
    $ make docs

   While developing, you can watch the documentation for changes and rebuild as required by installing `watchdog <https://pypi.python.org/pypi/watchdog>`_::

    $ pip install watchdog
    $ make docs.watch

   The built documentation is output to the ``_build/html/`` folder. The simplest way to view these docs is with Python's built-in static webserver ``python -m SimpleHTTPServer``.

7. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

8. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. If applicable, add the feature to the list in README.rst.
3. The pull request should work for Python 2.7, 3.3, 3.4, and 3.5, and for PyPy. Check https://travis-ci.org/shopkeep/shpkpr/pull_requests and make sure that the tests pass for all supported Python versions.
