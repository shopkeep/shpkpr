==================================
Managing Application Configuration
==================================

``shpkpr config`` allows you to manage an application's configuration, listing, setting and unsetting configuration values::

    $ shpkpr config --help
    Usage: shpkpr config [OPTIONS] COMMAND [ARGS]...

      Manage application configuration.

    Options:
      --help  Show this message and exit.

    Commands:
      list   List application configuration.
      set    Set application configuration.
      unset  Unset application configuration.

Applications on Marathon are configured using environment variables which are passed into the application container at startup. A change in the application configuration (when using ``shpkpr config set`` or ``shpkpr config unset``) will trigger a deployment and restart all running instances with the new configuration.

Listing application configuration
---------------------------------

``shpkpr config list`` allows you to list an application's configuration::

    $ shpkpr config list --help
    Usage: shpkpr config list [OPTIONS]

      List application configuration.

    Options:
      -a, --application TEXT  ID/name of the application to scale.  [required]
      --help                  Show this message and exit.

Required Configuration
^^^^^^^^^^^^^^^^^^^^^^

**Marathon URL:**

    URL of the Marathon API to use, e.g. ``http://marathon.mydomain.com:8080``

    * Evironment variable: ``SHPKPR_MARATHON_URL``
    * Command-line flag: ``--marathon_url``

**Application ID:**

    ID of the application to show, e.g. ``my-app``

    * Environment variable: ``SHPKPR_APPLICATION``
    * Command-line flag: ``--application``

Examples
^^^^^^^^

::

    $ shpkpr config list -a my-app
    MY_KEY=MY_VALUE
    SOME_OTHER_KEY=SOME_OTHER_VALUE
    MAGIC_NUMBER=12

::

    $ shpkpr config list -a my-app
    SOME_KEY=this-is-a-value
    YET_ANOTHER_KEY=42

Setting application configuration
---------------------------------

``shpkpr config set`` allows you to set configuration values (key/value pairs) for a Marathon application::

    $ shpkpr config set --help
    Usage: shpkpr config set [OPTIONS] [ENV_VARS]...

      Set application configuration.

    Options:
      -a, --application TEXT  ID/name of the application to scale.  [required]
      --help                  Show this message and exit.

New (or changed) configuration values are passed on the command line in a KEY=VALUE format. Any number of key/value pairs can be passed. See below for a few examples.

Required Configuration
^^^^^^^^^^^^^^^^^^^^^^

**Marathon URL:**

    URL of the Marathon API to use, e.g. ``http://marathon.mydomain.com:8080``

    * Evironment variable: ``SHPKPR_MARATHON_URL``
    * Command-line flag: ``--marathon_url``

**Application ID:**

    ID of the application to show, e.g. ``my-app``

    * Environment variable: ``SHPKPR_APPLICATION``
    * Command-line flag: ``--application``

Examples
^^^^^^^^

::

    $ shpkpr config set -a my-app SOME_KEY=SOME_VALUE

::

    $ shpkpr config set -a my-app SOME_KEY=SOME_VALUE SOME_OTHER_KEY=0123456789

Unsetting application configuration
---------------------------------

``shpkpr config unset`` allows you to unset configuration values and remove them from an application::

    $ shpkpr config unset --help
    Usage: shpkpr config unset [OPTIONS] [KEYS]...

      Unset application configuration.

    Options:
      -a, --application TEXT  ID/name of the application to scale.  [required]
      --help                  Show this message and exit.

Existing configuration keys are passed on the command line. Any number of keys can be passed. See below for a few examples.

Required Configuration
^^^^^^^^^^^^^^^^^^^^^^

**Marathon URL:**

    URL of the Marathon API to use, e.g. ``http://marathon.mydomain.com:8080``

    * Evironment variable: ``SHPKPR_MARATHON_URL``
    * Command-line flag: ``--marathon_url``

**Application ID:**

    ID of the application to show, e.g. ``my-app``

    * Environment variable: ``SHPKPR_APPLICATION``
    * Command-line flag: ``--application``

Examples
^^^^^^^^

::

    $ shpkpr config unset -a my-app SOME_KEY

::

    $ shpkpr config unset -a my-app SOME_KEY SOME_OTHER_KEY
