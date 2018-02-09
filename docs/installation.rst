============
Installation
============

Using Pip
~~~~~~~~~

At the command line::

    $ pip install shpkpr

Or, if you have virtualenvwrapper installed::

    $ mkvirtualenv shpkpr
    $ pip install shpkpr

If you prefer to use shpkpr from git (**WARNING:** May be unstable), then::

    $ pip install -e git+https://github.com/shopkeep/shpkpr.git#egg=shpkpr

Once installed, shpkpr should be available on your ``$PATH``::

    $ shpkpr --marathon_url=http://marathon.mydomain.com:8080 show

Using Docker
~~~~~~~~~~~~

shpkpr is also available in a prebuilt Docker image if you'd prefer to run it in a container. A list of the available tags can be found on the `Docker hub <https://hub.docker.com/r/shopkeep/shpkpr/tags/>`_::

    $ docker pull shopkeep/shpkpr:v3.1.3
    $ docker pull shopkeep/shpkpr:master

Once the image is downloaded, you can use shpkpr with ``docker run``::

    $ docker run -ti shopkeep/shpkpr:master shpkpr --marathon_url=http://marathon.mydomain.com:8080 show

A simple way to avoid having to repeat the long ``docker run`` command is to use a bash alias::

    $ alias shpkpr="docker run -ti -e SHPKPR_MARATHON_URL=http://marathon.mydomain.com:8080 shopkeep/shpkpr:master shpkpr"
    $ shpkpr show
