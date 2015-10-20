#!/usr/bin/env python
"""
deploytool is a small Python script which uses the Marathon API to
verify that a given Docker image is deployed to the target Marathon cluster
and that no outstanding deployments are in progress.

This script requires two command line arguments:
    1) The Marathon App ID of the app to check
    2) The Docker image (repotag) that is expected to be running currently
"""
# stdlib imports
import datetime
import os
import sys
import time

# third-party imports
import requests


class DeploymentInProgress(Exception):
    pass


class DeploymentTimedOut(Exception):
    pass


class RepoTagDoesntMatch(Exception):
    pass


def _fetch_app_definition(marathon_url, app_id):
    """Use requests to fetch the app definition from Marathon
    """
    url = marathon_url + app_id
    response = requests.get(url)
    return response.json()


def _deployment_in_progress(app_definition):
    """Given an app definition from marathon, check that no deployments are
    currently running
    """
    return len(app_definition.get("app", {}).get("deployments", [])) != 0


def _has_correct_repotag(app_definition, repotag):
    """Checks that the marathon app definition contains the correct docker
    image/repotag
    """
    docker_config = app_definition.get("app", {}).get("container", {}).get("docker", {})
    running_image = docker_config.get("image", "").split("/")[-1]
    return repotag == running_image


def check_deployment(marathon_url, app_id, repotag):
    """Check that the expected app ID and repotag are correctly deployed to Marathon
    """
    app_definition = _fetch_app_definition(marathon_url, app_id)
    if _deployment_in_progress(app_definition):
        raise DeploymentInProgress(app_id)
    if not _has_correct_repotag(app_definition, repotag):
        raise RepoTagDoesntMatch(repotag)


def wait_for_deployment(marathon_url, app_id, repotag, timeout=900):
    """Waits (up to `timeout` seconds) for the deploy of a given repotag to complete
    """
    start_ts = datetime.datetime.utcnow()
    while datetime.datetime.utcnow() - datetime.timedelta(seconds=timeout) < start_ts:
        # run deployment check
        try:
            check_deployment(marathon_url, app_id, repotag)
        except DeploymentInProgress:
            print "Deployment in progress: waiting"
        except RepoTagDoesntMatch:
            print "RepoTag does not match on Marathon: waiting"
        else:
            return
        time.sleep(10)
    raise DeploymentTimedOut(app_id)


if __name__ == "__main__":

    # Load configuration from the environment
    _default_marathon_url = "http://cfn-marathon-serenity-mesos-stage-us-east-1.posrip.com:8080/v2/apps/"
    MARATHON_API_ENDPOINT = os.getenv("MARATHON_API_ENDPOINT", _default_marathon_url)

    # Grab required arguments from the command line
    try:
        APP_ID = sys.argv[1]
        REPOTAG = sys.argv[2].split("/")[-1]
    except IndexError:
        print "Both APP_ID and REPOTAG are required arguments"
        sys.exit(1)

    # wait for the given deployment to succeed or fail
    try:
        wait_for_deployment(MARATHON_API_ENDPOINT, APP_ID, REPOTAG)
    except DeploymentTimedOut:
        print "Deployment timed out: exiting"
        sys.exit(1)
    else:
        print "Deploy succeeded: exiting"
