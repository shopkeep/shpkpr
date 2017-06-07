======================
Working With Templates
======================

When deploying a new application or scheduled task, shpkpr renders the application or task definition (typically a JSON document) using Jinja2_. This allows the user to interpolate values into the template prior to deployment if required. This is particularly useful for keeping configuration or secret data out of your codebase and injecting it just in time prior to the deployment.


Passing values to a template
----------------------------

For the following sections we'll use the ``shpkpr apps deploy`` command as an example (the documentation that follows applies equally to other commands that render templates too), assuming the following environment variables have been set (so we don't have to repeat them in the examples below)::

    $ export SHPKPR_MARATHON_URL=http://my.marathon.install.mydomain.com

And that we're using the :ref:`default-template-standard`. The only required values for this template are ``MARATHON_APP_ID`` (the id of the application to be deployed) and ``DOCKER_REPOTAG`` (the image and tag for the docker container to be deployed).

shpkpr offers two methods of passing values to a template at deploy time, both are described below:

On the command line
~~~~~~~~~~~~~~~~~~~

The most straightforward way to provide values for a template in shpkpr is on the command line. Each one of the commands which renders a template (currently ``shpkpr apps deploy`` and ``shpkpr cron set``) accepts an arbitrary list of ``key=value`` pairs which are passed directly to the template being rendered::

    $ shpkpr apps deploy MARATHON_APP_ID=my-app DOCKER_REPOTAG=my.docker.registry/my-image:latest

.. note::

   When passing template values on the command line, they must always be passed after any options (those parameters starting with ``-`` or ``--``).

In the environment
~~~~~~~~~~~~~~~~~~

It may be more convenient to use environment variables to pass values to a template, so shpkpr supports this method too. When reading values from the environment, shpkpr respects the value of the ``-e/--env-prefix`` option (defaults to ``SHPKPR_``). This means that if you wanted to set the values for the required variables in the standard template you would set them like so::

    $ export SHPKPR_MARATHON_APP_ID=my-app
    $ export SHPKPR_DOCKER_REPOTAG=my.docker.registry/my-image:latest

You can then deploy with a simple::

    $ shpkpr apps deploy

If you prefer not to prefix your environment variables and just slurp up all of them, you can do::

    $ export MARATHON_APP_ID=my-app
    $ export DOCKER_REPOTAG=my.docker.registry/my-image:latest
    $ shpkpr apps deploy -e ""


Handling Missing Values
-----------------------

When rendering a template, if a value does not have a default and is not provided by the user, then shpkpr will exit with a non-zero exit code and display a helpful error message.

.. command-output:: shpkpr apps deploy --marathon-url http://marathon MARATHON_APP_ID=my-app
   :returncode: 2


Writing Templates
-----------------

The Jinja2_ documentation is the best place to go to find general advice on syntax, features and how the language works, so we'll only cover shpkpr specific bits in this section.

Formatting
~~~~~~~~~~

Currently, shpkpr only supports JSON templates. That is, *after rendering* the template must be valid JSON or shpkpr will exit with a non-zero exit code.

Given the following template:

.. literalinclude:: ../resources/usage/templates/broken.json.tmpl
   :language: yaml+jinja

shpkpr will raise an error here due to the lack of quote-marks around ``{{CMD}}`` which would result in invalid JSON (as shpkpr escapes quote-marks in interpolated values).

Currently shpkpr doesn't produce particularly helpful error messages here, but that will be fixed in a future release.

.. command-output:: shpkpr apps deploy --marathon-url http://marathon MARATHON_APP_ID=my-app -t resources/usage/templates/broken.json.tmpl CMD="echo Hello!"
   :returncode: 2

Using Filters
~~~~~~~~~~~~~

From the `Jinja docs`_:

    Variables can be modified by **filters**.  Filters are separated from the variable by a pipe symbol (``|``) and may have optional arguments in parentheses.  Multiple filters can be chained.  The output of one filter is applied to the next.

    For example, ``{{ name|striptags|title }}`` will remove all HTML Tags from variable ```name`` and title-case the output (``title(striptags(name))``).

    Filters that accept arguments have parentheses around the arguments, just like a function call.  For example: ``{{ listx|join(', ') }}`` will join a list with commas (``str.join(', ', listx)``).

In addition to the `built-in filters`_ shipped by Jinja, shpkpr provides a number of additional filters to assist with writing your templates, from validation/typing to text transformation.

.. autofunction:: shpkpr.template_filters.filter_items
.. autofunction:: shpkpr.template_filters.require_int
.. autofunction:: shpkpr.template_filters.require_float
.. autofunction:: shpkpr.template_filters.slugify

.. _all_env:

Dictionary access to all variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes it's useful to be able to access all template variables in a single dictionary object. This allows for iteration over the variables, or indirect access (using the value of another variable as the key).

shpkpr provides the special ``_all_env`` variable for this purpose. It can be used as follows:

.. code-block:: jinja

    {# Iterate over all template variables beginning with "LABEL_" #}
    {% for k, v in _all_env|filter_items("LABEL_") %}
        "{{k}}": "{{v}}",
    {% endfor %}

    {# Regular dictionary-style access is available if necessary #}
    {{ _all_env[SOME_VARIABLE] }}


.. _Jinja2: http://jinja.pocoo.org/docs/
.. _`Jinja docs`: http://jinja.pocoo.org/docs/2.9/templates/#filters
.. _`built-in filters`: http://jinja.pocoo.org/docs/2.9/templates/#list-of-builtin-filters
