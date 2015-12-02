=====================
View Application Logs
=====================

``shpkpr logs`` allows you to view/tail an applications logs::

    $ shpkpr logs --help
    Usage: shpkpr logs [OPTIONS]

      Tail a file in a mesos task's sandbox.

    Options:
      -a, --application TEXT  ID/name of the application to scale.  [required]
      --file TEXT             Which sandbox file to read from.
      -n, --lines INTEGER     Number of lines to show in tail output.
      -c, --completed         Show logs for completed tasks.
      -f, --follow            Enables follow mode.
      --help                  Show this message and exit.

Required Configuration
^^^^^^^^^^^^^^^^^^^^^^

**Mesos Master URL:**

    URL of the Mesos master to connect to to retrieve logs, e.g. ``http://mesos-master.mydomain.com:5050``

    * Environment variable: ``SHPKPR_MESOS_MASTER_URL``
    * Command-line flag: ``--mesos_master_url``

**Application ID:**

    ID of the application to show, e.g. ``my-app``

    * Environment variable: ``SHPKPR_APPLICATION``
    * Command-line flag: ``--application``

Optional Configuration
^^^^^^^^^^^^^^^^^^^^^^

**Number of lines to show:**

    The number of log lines to show in the output (per instance), e.g. ``5``

    * Environment variable: ``SHPKPR_LINES``
    * Command-line flag: ``--lines``
    * Default: ``10``

**File to view/tail:**

    Which output file to read from. shpkpr can read from any file in the mesos sandbox e.g. ``stderr``

    * Environment variable: ``SHPKPR_FILE``
    * Command-line flag: ``--file``
    * Default: ``stdout``

**View logs for completed tasks:**

    Show logs for tasks that have finished or been killed.

    * Environment variable: ``SHPKPR_COMPLETED``
    * Command-line flag: ``--completed``
    * Default: ``false``

**Follow log file:**

    Follow the log file as it's being written to, similar to ``tail -f`` on unix.

    * Environment variable: ``SHPKPR_FOLLOW``
    * Command-line flag: ``--follow``
    * Default: ``false``

Examples
^^^^^^^^

::

    $ shpkpr logs -a my-app-1 -n 5
    [3c44088c] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:47Z"}
    [3c44088c] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:49Z"}
    [3c44088c] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:49Z"}
    [3c44088c] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:51Z"}
    [3c44088c] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:51Z"}
    [5eea6ce0] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:47Z"}
    [5eea6ce0] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:49Z"}
    [5eea6ce0] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:49Z"}
    [5eea6ce0] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:51Z"}
    [5eea6ce0] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:51Z"}

::

    $ shpkpr logs -a my-app-1 -n 2 --completed
    [3c44088c] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:47Z"}
    [3c44088c] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:49Z"}
    [234dwa23] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:49Z"}
    [234dwa23] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:51Z"}
    [5eea6ce0] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:47Z"}
    [5eea6ce0] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:49Z"}

::

    $ shpkpr logs -a my-app-1 --follow
    [3c44088c] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:47Z"}
    [3c44088c] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:49Z"}
    [234dwa23] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:49Z"}
    [234dwa23] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:51Z"}
    [5eea6ce0] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:47Z"}
    [5eea6ce0] {"level":"info","msg":"Hello log!","time":"2015-11-19T03:29:49Z"}
    ...
    ...
    # continues until ^C