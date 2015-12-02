===========================
Showing Application Details
===========================

``shpkpr show`` allows you to view details of a single application that is currently deployed to Marathon::

    $ shpkpr show --help
    Usage: shpkpr show [OPTIONS]

      Shows detailed information for a single application.

    Options:
      -a, --application TEXT  ID/name of the application to scale.  [required]
      --help                  Show this message and exit.

Required Configuration
~~~~~~~~~~~~~~~~~~~~~~

**Marathon URL:**

    URL of the Marathon API to use, e.g. ``http://marathon.mydomain.com:8080``

    * Environment variable: ``SHPKPR_MARATHON_URL``
    * Command-line flag: ``--marathon_url``

**Application ID:**

    ID of the application to show, e.g. ``my-app``

    * Environment variable: ``SHPKPR_APPLICATION``
    * Command-line flag: ``--application``

Examples
~~~~~~~~

::

    $ shpkpr show -a my-app
    ID:           my-app
    CPUs:         0.1
    RAM:          256.0
    Instances:    2
    Docker Image: myname/myimage:sometag
    Domain:       somedomain.com
    Version:      2015-11-18T10:59:58.428Z
    Status:       HEALTHY

::

    $ shpkpr show -a my-other-app
    ID:           my-other-app
    CPUs:         4
    RAM:          2048.0
    Instances:    8
    Docker Image: myname/myimage:sometag
    Domain:       somedomain.com
    Version:      2015-11-17T09:42:34.129Z
    Status:       DEPLOYING
