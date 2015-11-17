#!/usr/bin/env bash
# smoke_tests.sh
#
# To run these tests, you'll need to set 6 environment variables:
# 
#     # URL of the Marathon API to use
#     export SHPKPR_MARATHON_URL=http://marathon.somedomain.com:8080
# 
#     # URL of the Mesos master to use
#     export SHPKPR_MESOS_MASTER_URL=http://mesos.somedomain.com:5050
# 
#     # An application ID to use for testing, this should not exist on
#     # Marathon prior to running the tests
#     export SHPKPR_APPLICATION=my-dummy-application-for-testing
# 
#     # Docker repotag of the container that should be deployed to Marathon.
#     # This container must be pullable by the mesos cluster; for testing
#     # purposes it's probably easiest to use a container from the public
#     # Docker hub.
#     export SHPKPR_DOCKER_REPOTAG=goexample/outyet:latest
#
#     # Port that should be exposed from the Docker container
#     export SHPKPR_DOCKER_EXPOSED_PORT=8080
#
#     # An arbitrary label to be injected into the deploy template. This can
#     # be any non-empty string for testing.
#     export SHPKPR_DEPLOY_DOMAIN=somedomain.com
#
# Once set, just run the script:
# 
#     ./smoke_tests.sh
# 
# In the absence of better tests for now, this script simply runs through a
# couple of variations of every supported command, using `set -e` to ensure
# that if anything fails the script will stop executing.
#
# You should manually verify that the system is behaving as expected during
# the test, by checking the command-line output and the Marathon UI for an
# overview on what the application is doing.
#
#
set -e

function invoke {
    echo "========================================================="
    echo " $1"
    echo "========================================================="
    eval $1
    echo
    echo
} 

invoke "shpkpr --help"
invoke "shpkpr list"
invoke "shpkpr deploy -t tests/test.json.tmpl"
invoke "shpkpr list"
invoke "shpkpr show"
invoke "shpkpr scale --instances=3 --cpus=0.1 --mem=512"
invoke "shpkpr show"
invoke "shpkpr scale --instances=2 --cpus=0.1 --mem=256"
invoke "shpkpr show"
invoke "shpkpr config list"
invoke "shpkpr config set SOMEVALUE=some-key SOMEOTHERVALUE=some-other-key"
invoke "shpkpr config list"
invoke "shpkpr config unset SOMEVALUE SOMEOTHERVALUE"
invoke "shpkpr config list"
invoke "shpkpr logs -n 10"
