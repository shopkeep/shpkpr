=====
Usage
=====

shpkpr is mostly self-documenting, and documentation for any command can be viewed by passing the ``--help`` parameter, e.g.::

    $ shpkpr --help
    Usage: shpkpr [OPTIONS] COMMAND [ARGS]...

      A tool to manage applications running on Marathon.

    Options:
      --marathon_url TEXT      URL of the Marathon API to use.
      --help                   Show this message and exit.

    Commands:
      deploy  Deploy application from template.
      show    Show application details.

For more detailed usage instructions use the sections linked below:

.. toctree::
   :maxdepth: 1

   configuration

   cmd_show
   cmd_deploy
   cmd_cron
