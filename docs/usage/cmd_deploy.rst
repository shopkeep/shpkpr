==================================
Deploying a new application config
==================================

``shpkpr deploy`` allows you to deploy a new (or changes to an existing) application configuration by rendering and POSTing a JSON template to Marathon::

    $ shpkpr deploy --help
    Usage: shpkpr deploy [OPTIONS] [ENV_PAIRS]...

      Deploy application from template.

    Options:
      --force                Force update even if a deployment is in progress.
      --dry-run              Enables dry-run mode. Shpkpr will not attempt to
                             contact Marathon when this is enabled.
      -t, --template TEXT    Name of the template to use for deployment.
                             [required]
      --template_dir TEXT    Base directory in which your templates are stored (default: `pwd`).
      -e, --env_prefix TEXT  Prefix used to restrict environment vars used for
                             templating.
      --marathon_url TEXT    URL of the Marathon API to use.  [required]
      --help                 Show this message and exit.

Additional template values can be passed on the command line in a KEY=VALUE format. Any number of key/value pairs can be passed. See below for a few examples.

Required Configuration
^^^^^^^^^^^^^^^^^^^^^^

**Marathon URL:**

    URL of the Marathon API to use, e.g. ``http://marathon.mydomain.com:8080``

    * Environment variable: ``SHPKPR_MARATHON_URL``
    * Command-line flag: ``--marathon_url``

**JSON Template Name:**

    Name of the JSON template to use for deployment, e.g. ``a/template.json.tmpl`` or ``my-template.json.tmpl``. This path should always be relative to the template base directory defined by ``--template-dir`` (``pwd`` by default).

    * Environment variable: ``SHPKPR_TEMPLATE``
    * Command-line flag: ``--template``

    **NOTE:** When running Marathon >0.13.0 it is possible to deploy multiple applications at the same time either by specifying the ``--template`` option multiple times, or by using a single template which contains a list of individual applications.

Optional Configuration
^^^^^^^^^^^^^^^^^^^^^^

**Force:**

    Using the force flag allows the user to initiate a deployment even if another deployment is currently in progress. This option should only be used in the case of a previous failed deployment as it *may* leave the app in an inconsistent state if anything goes wrong.

    * Command-line flag: ``--force``

**Dry Run:**

    Using the dry-run flag allows the user to test a deployment before performing it against a live Marathon instance. When enabled, shpkpr will not attempt to contact the configured Marathon server.

    * Command-line flag: ``--dry-run``

**Environment Variable Prefix:**

    When reading variables from the environment to inject into the template at render time, only those variables which begin with the specified prefix are considered. The prefix is stripped from the variable names before injecting into the template context.

    **Note:** The ``env_prefix`` in this case controls only the prefix used for collecting environment variables for templating purposes. The ``SHPKPR_`` prefix is **always** used for regular configuration as documented elsewhere.

    * Environment variable: ``SHPKPR_ENV_PREFIX``
    * Command-line flag: ``--env_prefix``
    * Default: ``SHPKPR_``

**Base Template Directory:**

    Absolute path to the base directory in which templates are stored. By default this is ``pwd`` but can be overridden to allow reading templates from any location on the filesystem. This setting is useful when using templates not found in ``pwd`` or controlling exactly how template inheritance should work. The specified directory is passed to a ``jinja2.FilesystemLoader`` within ``shpkpr``.

    * Command-line flag: ``--template_dir``

Examples
^^^^^^^^

::

    $ cat deploy.json.tmpl
    {
      "id": "{{APPLICATION}}",
      "cmd": "{{CMD}}",
      "cpus": {{CPUS|require_float(min=0.0, max=2.0)}},
      "mem": 512,
      "instances": {{INSTANCES|require_int(min=1, max=16)}},
      "labels": {
        "DOMAIN": "{{LABEL_DOMAIN}}",
        "RANDOM_LABEL": "{{RANDOM_LABEL}}"
      }
    }

    $ export SHPKPR_APPLICATION=my-app
    $ export SHPKPR_CPUS=0.1
    $ export SHPKPR_INSTANCES=2
    $ export SHPKPR_CMD="sleep 60"
    $ export SHPKPR_LABEL_DOMAIN=mydomain.com

    $ shpkpr deploy -t deploy.json.tmpl RANDOM_LABEL=my_value

    # Would result in the following output sent to Marathon
    # {
    #   "id": "my-app",
    #   "cmd": "sleep 60",
    #   "cpus": 0.1,
    #   "mem": 512,
    #   "instances": 2,
    #   "labels": {
    #     "DOMAIN": "mydomain.com",
    #     "RANDOM_LABEL": "my_value"
    #   }
    # }
::

    $ cat deploy.json.tmpl
    {
      "id": "my-application",
      "cmd": "sleep 60",
      "cpus": 0.1,
      "mem": 512,
      "instances": 1,
      "labels": {
        {% for k, v in _all_env|filter_items("LABEL_", True) %}
        "{{ k }}": "{{ v }}"{% if loop.last == False %},{% endif %}
        {% endfor %}
      }
    }

    $ export LABEL_DOMAIN=mydomain.com
    $ export LABEL_NODE_TYPE=webserver
    $ export LABEL_FAVORITE_ICECREAM_FLAVOR=vanilla

    $ shpkpr deploy -t deploy.json.tmpl -e ""

    # Would result in the following output sent to Marathon
    # {
    #   "id": "my-application",
    #   "cmd": "sleep 60",
    #   "cpus": 0.1,
    #   "mem": 512,
    #   "instances": 1,
    #   "labels": {
    #     "DOMAIN": "mydomain.com",
    #     "NODE_TYPE": "webserver",
    #     "FAVORITE_ICECREAM_FLAVOR": "vanilla"
    #   }
    # }
