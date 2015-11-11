shpkpr
======

shpkpr is a tool for controlling and observing applications running on ShopKeep's Mesos/Marathon platform. shpkpr is designed to provide a simple command-line interface to the platform (similiar to the `deis` command-line tool) for use both manually and with CI tools like jenkins.


## Features

- List all deployed applications
- Show detailed application info
- Scale application resources
- View/Modify application configuration
- Deploy applications (using Jinja2 templates)
- View/Tail application logs
- **TODO:** Run one-off commands inside the deployed environment (like `heroku run`)


## Installation

To install a release version of shpkpr from [PyPI](https://pypi.python.org), simply:

```bash
$ pip install shpkpr # NOTE: This won't actually work until our first release
```

If you prefer to use shpkpr from git (**WARNING:** May be unstable), then:

```bash
$ pip install -e git+https://github.com/shopkeep/shpkpr.git#egg=shpkpr
```


## Configuration

All configuration options and arguments are fully documented in the `--help` screen for each command, however, `shpkpr` additionally allows all options to be specified in environment variables with the prefix `SHPKPR_`.

For example, to avoid having to specify the Marathon API URL with each command, you could do:

```bash
$ export SHPKPR_MARATHON_URL=http://my.marathon.install.mydomain.com:8080
$ shpkpr list
myapp1
my-other-app
yet-another-app
```

Which is functionally equivalent to:

```bash
$ shpkpr --marathon_url=http://my.marathon.install.mydomain.com:8080 list
myapp1
my-other-app
yet-another-app
```

Options specified on the command line will always take precedence over those in the environment.


## Usage

`shpkpr` is fully self-documenting, and documentation for any command can be viewed by passing the `--help` parameter, e.g.:

```bash
$ shpkpr --help
Usage: shpkpr [OPTIONS] COMMAND [ARGS]...

  A tool to manage applications running on Marathon.

Options:
  --marathon_url TEXT      URL of the Marathon API to use.  [required]
  --mesos_master_url TEXT  URL of the Mesos master to use.  [required]
  -v, --verbose            Enables verbose mode.
  --help                   Show this message and exit.

Commands:
  config  Manage application configuration
  deploy  Deploy application from template.
  list    Lists all deployed applications
  logs    View/tail application logs.
  scale   Scale application resources.
  show    Show application details.
```

Or:

```bash
$ shpkpr config --help
Usage: shpkpr config [OPTIONS] COMMAND [ARGS]...

  Manage application configuration

Options:
  --help  Show this message and exit.

Commands:
  list   List application configuration.
  set    Set application configuration.
  unset  Unset application configuration.
```


## Development Setup

### Local environment setup

The easiest way to setup `shpkpr` for development purposes is to use `pip` and install the application in "editable" mode:

```bash
$ git clone git@github.com:shopkeep/shpkpr.git

# Assumes you have virtualenvwrapper installed
$ mkvirtualenv shpkpr
New python executable in shpkpr/bin/python2.7
Also creating executable in shpkpr/bin/python
Installing setuptools, pip, wheel...done.

(shpkpr)$ pip install --editable .
```

Changes in your working tree should then be available (from within the virtual environment) when you run `shpkpr`.

### Testing

`shpkpr` runs its tests using [tox](https://tox.readthedocs.org/en/latest/). To run the tests locally, simply:

```bash
$ tox
```

Or to run the tests against a specific version of Python, you can:

```bash
$ tox -e py27
$ tox -e py34
```

**NOTE:** In future, the tests will make use of [Docker](http://docker.com) to provide a consistent environment for testing and build purposes.


## Examples

All examples below assume that the `SHPKPR_MARATHON_URL` environment variable has been set appropriately.

#### Listing deployed applications

```bash
$ shpkpr list
my-app-1
my-other-app
yet-another-app
```

#### Showing application information

```bash
$ shpkpr list -a my-app-1
ID:           my-app-1
CPUs:         0.5
RAM:          512.0
Instances:    2
Docker Image: myuser/myservice:master-a7c01d9b
Domain:       somedomain.com
Version:      2015-11-09T13:57:20.827Z
Status:       HEALTHY
```

#### Listing application configuration

```bash
$ shpkpr config list -a my-app-1
SOMEKEY=SOMEVALUE
SOME_OTHER_KEY=SOME_OTHER_VALUE
YET_ANOTHER_KEY=YET_another_VALUE
```

#### Setting application configuration

```bash
$ shpkpr config set -a my-app-1 MYKEY=MYVALUE MYOTHERKEY=myothervalue
```

#### Unsetting application configuration

```bash
$ shpkpr config unset -a my-app-1 MYKEY MYOTHERKEY
```

#### Scaling application resources

```bash
$ shpkpr scale -a my-app-1 --instances=4
$ shpkpr scale -a my-app-1 --instances=2 --cpus=0.5
$ shpkpr scale -a my-app-1 --cpus=0.25 --mem=1024
```

#### Viewing application logs

```bash
$ shpkpr logs -a my-app-1 -n 100
$ shpkpr logs -a my-app-1 -n 100 --completed
$ shpkpr logs -a my-app-1 --follow
```
