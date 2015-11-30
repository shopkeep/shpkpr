==================================
Deploying a new application config
==================================

``shpkpr deploy`` allows you to deploy a new (or changes to an existing) application configuration by rendering and POSTing a JSON template to Marathon::

    $ shpkpr deploy --help
    Usage: shpkpr deploy [OPTIONS]

      Deploy application from template.

    Options:
      -t, --template FILENAME  Path of the template to use for deployment.
                               [required]
      -e, --env_prefix TEXT    Prefix used to restrict environment vars used
                               for templating.
      --help                   Show this message and exit.


Required Configuration
^^^^^^^^^^^^^^^^^^^^^^

**Marathon URL:**

    URL of the Marathon API to use, e.g. ``http://marathon.mydomain.com:8080``

    * Evironment variable: ``SHPKPR_MARATHON_URL``
    * Command-line flag: ``--marathon_url``

**JSON Template Path:**

    Path of the JSON template to use for deployment, e.g. ``/some/path/to/a/template.json.tmpl`` or ``./my-template.json.tmpl``

    * Environment variable: ``SHPKPR_TEMPLATE``
    * Command-line flag: ``--template``

Optional Configuration
^^^^^^^^^^^^^^^^^^^^^^

**Environment Variable Prefix:**

    When reading variables from the environment to inject into the template at render time, only those variables which begin with the specified prefix are considered. The prefix is stripped from the variable names before injecting into the template context.

    **Note:** The ``env_prefix`` in this case controls only the prefix used for collecting environment variables for templating purposes. The ``SHPKPR_`` prefix is **always** used for regular configuration as documented elsewhere.

    * Environment variable: ``SHPKPR_ENV_PREFIX``
    * Command-line flag: ``--env_prefix``
    * Default: ``SHPKPR_``


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
        "DOMAIN": "{{LABEL_DOMAIN}}"
      }
    }

    $ export SHPKPR_APPLICATION=my-app
    $ export SHPKPR_CPUS=0.1
    $ export SHPKPR_INSTANCES=2
    $ export SHPKPR_CMD="sleep 60"
    $ export SHPKPR_LABEL_DOMAIN=mydomain.com

    $ shpkpr deploy -t deploy.json.tmpl

    # Would result in the following output sent to Marathon
    # {
    #   "id": "my-app",
    #   "cmd": "sleep 60",
    #   "cpus": 0.1,
    #   "mem": 512,
    #   "instances": 2,
    #   "labels": {
    #     "DOMAIN": "mydomain.com"
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