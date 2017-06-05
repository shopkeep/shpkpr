=============
Configuration
=============

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

All configuration options and arguments are fully documented in the ``--help`` screen for each command, however, ``shpkpr`` additionally allows most options to be specified as environment variables with the prefix ``SHPKPR_``.

For example, to avoid having to specify the Marathon API URL with each command, you could do::

    $ export SHPKPR_MARATHON_URL=http://my.marathon.install.mydomain.com:8080
    $ shpkpr show myapp

Which is functionally equivalent to::

    $ shpkpr --marathon_url=http://my.marathon.install.mydomain.com:8080 show myapp

Options specified on the command line will always take precedence over those in the environment.

See documentation for individual commands for exact option/environment variable names.
