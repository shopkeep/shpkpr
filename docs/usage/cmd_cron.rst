=====================
Managing Chronos Jobs
=====================

``shpkpr cron`` Allows one to list, add, delete, update, run and terminate running tasks for Chronos Jobs.

    $ shpkpr cron --help
    Usage: shpkpr cron [OPTIONS] COMMAND [ARGS]...

      Manage Chronos Jobs.

    Options:
      --help  Show this message and exit.
      --chronos_url  URL of the Chronos API to use.

Required Configuration
^^^^^^^^^^^^^^^^^^^^^^

**Chronos URL:**

    URL of the Chronos API to use, e.g. ``http://chronos.mydomain.com:4400``

    * Environment variable: ``SHPKPR_CHRONOS_URL``
    * Command-line flag: ``--chronos_url``

Examples
^^^^^^^^

::

    $ shpkpr cron show --chronos_url chronos.mydomain.com:4400
    [
        {
            "name": "job1",
            ...
        },
        {
            "name": "job2",
            ...
        }
    ]

::

    $ shpkpr cron show --job-name job1 --chronos_url chronos.mydomain.com:4400
    [
        {
            "name": "job1",
            ...
        }
    ]

::

    $ shpkpr cron set --chronos_url chronos.mydomain.com:4400 \
      --template_dir /path/to/template/base/path \
      --template job_1_template.json.tmpl

::

    $ shpkpr cron set --chronos_url chronos.mydomain.com:4400 \
      --template_dir /path/to/template/base/path \
      --template job_1_template.json.tmpl \
      --template job_2_template.json.tmpl

::

    $ shpkpr cron delete-tasks --chronos_url chronos.mydomain.com:4400 job2

::

    $ shpkpr cron delete --chronos_url chronos.mydomain.com:4400 job2

::

    $ shpkpr cron run --chronos_url chronos.mydomain.com:4400 job2
