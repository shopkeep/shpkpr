=======================
Listing Application IDs
=======================

``shpkpr list`` allows you to list the application IDs (one per line) of all applications currently deployed to Marathon::

    $ shpkpr list --help
    Usage: shpkpr list [OPTIONS]

      Lists all applications currently deployed to marathon.

    Options:
      --help  Show this message and exit.

Required Configuration
~~~~~~~~~~~~~~~~~~~~~~

**Marathon URL:**

    URL of the Marathon API to use, e.g. ``http://marathon.mydomain.com:8080``

    * Evironment variable: ``SHPKPR_MARATHON_URL``
    * Command-line flag: ``--marathon_url``

Examples
~~~~~~~~

::

    $ shpkpr list
    my-app-1
    my-other-app
    yet-another-app
