=====
Usage
=====

shpkpr is mostly self-documenting, and documentation for any command can be viewed by passing the ``--help`` parameter, e.g.::

    $ shpkpr --help
    Usage: shpkpr [OPTIONS] COMMAND [ARGS]...

      A tool to manage applications running on Marathon.

    Options:
      --marathon_url TEXT      URL of the Marathon API to use.
      --mesos_master_url TEXT  URL of the Mesos master to use.
      --help                   Show this message and exit.

    Commands:
      config  Manage application configuration
      deploy  Deploy application from template.
      list    Lists all deployed applications
      logs    View/tail application logs.
      scale   Scale application resources.
      show    Show application details.

For more detailed usage instructions use the sections linked below:

.. toctree::
   :maxdepth: 1

   configuration

   cmd_list
   cmd_show
   cmd_config
   cmd_scale
   cmd_logs
