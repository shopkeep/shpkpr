=============================
Scaling Application Resources
=============================

``shpkpr scale`` allows you to change an application's resource allocation (CPU, memory, and number of instances)::

    $ shpkpr scale --help
    Usage: shpkpr scale [OPTIONS]

      Scale application resources to specified levels.

    Options:
      -a, --application TEXT   ID/name of the application to scale.  [required]
      -c, --cpus FLOAT         Number of CPUs to assign to each instance of the
                               application.
      -m, --mem INTEGER        Amount of RAM (in MB) to assign to each instance of
                               the application.
      -i, --instances INTEGER  Number of instances of the application to run.
      --help                   Show this message and exit.

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

Optional Configuration
^^^^^^^^^^^^^^^^^^^^^^

**CPU share:**

    The number of CPU`s this application needs per instance. This number does not have to be integer, but can be a fraction. e.g. ``0.5``

    * Evironment variable: ``SHPKPR_CPUS``
    * Command-line flag: ``--cpus``

**Memory/RAM:**

    The amount of memory in MB that is needed for the application per instance. e.g. ``1024``

    * Environment variable: ``SHPKPR_MEM``
    * Command-line flag: ``--mem``

**Number of instances:**

    The number of instances of this application to start. Please note: this number can be changed everytime as needed to scale the application. e.g. ``8``

    * Environment variable: ``SHPKPR_INSTANCES``
    * Command-line flag: ``--instances``

Examples
^^^^^^^^

::

    $ shpkpr scale -a my-app-1 --instances=4

::

    $ shpkpr scale -a my-app-1 --instances=2 --cpus=0.5

::

    $ shpkpr scale -a my-app-1 --cpus=0.25 --mem=1024
