"""A collection of marathon-related utils
"""
# future imports
from __future__ import absolute_import

# stdlib imports
import json
from collections import OrderedDict

# third-party imports
import dotmap
import requests

# local imports
from .application import MarathonApplication
from .deployment import MarathonDeployment
from shpkpr import exceptions


class DotMap(dotmap.DotMap):
    """Override DotMap constructor to match the signature of dict()
    """

    def __init__(self, *args, **kwargs):
        self._map = OrderedDict()

        if args:
            for k, v in args[0]:
                self._map[k] = v

        for k, v in self.__call_items(kwargs):
            self._map[k] = v


class ClientError(exceptions.ShpkprException):
    pass


class MarathonClient(object):
    """A thin wrapper around marathon.MarathonClient for internal use
    """

    def __init__(self, marathon_url, schema_path):
        self._marathon_url = marathon_url
        self._schema_path = schema_path

    def _build_url(self, path):
        return self._marathon_url.rstrip("/") + path

    def _make_request(self, method, path, **kwargs):
        request = getattr(requests, method.lower())
        return request(self._build_url(path), **kwargs)

    def _parse_response(self, response_json):
        """Parses a JSON response, loading into a DotMap instance
        """
        return json.loads(response_json, object_pairs_hook=DotMap)

    @property
    def embed_params(self):
        return [
            "app.tasks",
            "app.counts",
            "app.deployments",
            "app.lastTaskFailure",
            "app.taskStats",
        ]

    @property
    def application_schema(self):
        with open(self._schema_path, 'r') as f:
            schema = json.loads(f.read())
        return schema

    def get_application(self, application_id):
        """Returns detailed information for a single application.
        """
        path = "/v2/apps/" + application_id
        params = {"embed": self.embed_params}
        response = self._make_request('GET', path, params=params)

        # return a new MarathonApplication instance that wraps the returned
        # application data
        if response.status_code == 200:
            return MarathonApplication(self._parse_response(response.text).app, self.application_schema)

        # raise an appropriate error if something went wrong
        if response.status_code == 404:
            raise ClientError("Unable to retrieve application details from marathon: does not exist.")
        raise ClientError("Unknown Marathon error: %s\n\n%s" % response.status_code, response.text)

    def list_applications(self):
        """Return a list of all applications currently deployed to marathon.
        """
        path = "/v2/apps"
        params = {"embed": self.embed_params}
        response = self._make_request('GET', path, params=params)

        # return a new MarathonApplication instance that wraps the returned
        # application data
        if response.status_code == 200:
            apps = self._parse_response(response.text).apps
            return [MarathonApplication(app, self.application_schema) for app in apps]

        raise ClientError("Unknown Marathon error: %s\n\n%s" % response.status_code, response.text)

    def list_application_ids(self):
        """Returns ids of all applications currently deployed to marathon.
        """

        return sorted([app.id.lstrip('/') for app in self.list_applications()])

    def deploy_application(self, applications, force=False):
        """Deploys the given application(s) to Marathon.
        """
        if not isinstance(applications, list):
            applications = [applications]

        for app in applications:
            app.validate()

        path = "/v2/apps"
        params = {"force": force}
        data = json.dumps([app.to_json() for app in applications])
        response = self._make_request('PUT', path, params=params, data=data)

        if response.status_code == 200:
            deployment = self._parse_response(response.text)
            return MarathonDeployment(self, applications[0].id, deployment.deploymentId, deployment.version)

        raise ClientError("Unknown Marathon error: %s\n\n%s" % response.status_code, response.text)
